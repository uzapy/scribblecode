import os
import csv
import time
import librosa
import soundfile as sf
import numpy as np
import tensorflow as tf
import vggish_input
import vggish_params
import vggish_slim
import vggish_postprocess
from azure.data.tables import TableClient
from azure.cosmos import CosmosClient, exceptions

table_connection_string_file = "../VDJ/azure_table_connection_string"
table_name = "playlists"
cosmosDB_connection_string_file = "../VDJ/cosmosdb_connection_string"
cosmosDB_name = "vdjdb"
cosmosDB_container = "embeddings"
output_file = "execution.log"

# Path to the VGGish model checkpoint
CHECKPOINT_PATH = 'models/research/audioset/vggish/vggish_model.ckpt'
PCA_PARAMS_PATH = 'models/research/audioset/vggish/vggish_pca_params.npz'

chunk_duration_ms = 975
sample_rate = 16000
overlap_factor = 0.2  # 20% overlap

# Initialize VGGish graph and session (you might want to do this once)
graph = tf.Graph()
with graph.as_default():
    pcm_input = tf.compat.v1.placeholder(
        tf.float32, shape=(None, vggish_params.NUM_FRAMES, vggish_params.NUM_BANDS)
    )
    embeddings = vggish_slim.define_vggish_slim(pcm_input)
    session = tf.compat.v1.Session(graph=graph)
    session.run(tf.compat.v1.global_variables_initializer())
    vggish_slim.load_vggish_slim_checkpoint(session, CHECKPOINT_PATH)
    pproc = vggish_postprocess.Postprocessor(PCA_PARAMS_PATH)

# Function to get VGGish embeddings for a single audio file
def get_vggish_embeddings(audio_path):
    try:
        input_batch = vggish_input.wavfile_to_examples(audio_path)

        if input_batch is None or input_batch.shape[0] == 0:
            print(f"Warning: No examples generated for {audio_path}")
            return None

        with graph.as_default():
            embedding_values = session.run(embeddings, feed_dict={pcm_input: input_batch})
            postprocessed_batch = pproc.postprocess(embedding_values)
            return postprocessed_batch

    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None

def main():
    counter = 0
    embeddings_dict = {}

    with open (table_connection_string_file, 'r', encoding='utf-8') as open_file :
        table_connection_string = open_file.read()
    # connect to table and get song info
    table_client = TableClient.from_connection_string(conn_str=table_connection_string, table_name=table_name)
    playlist_filter = "playlist eq '90s'"

    with open (cosmosDB_connection_string_file,  'r', encoding='utf-8') as open_file :
        cosmosDB_connection_string = open_file.read()
    # connect to cosmosDb and container
    cosmos_client = CosmosClient.from_connection_string(cosmosDB_connection_string)
    cosmos_database = cosmos_client.get_database_client(cosmosDB_name)
    cosmos_container = cosmos_database.get_container_client(cosmosDB_container)

    # create log file
    with open (output_file, mode='a', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=["counter","chunk_path"])
        writer.writeheader()

        # go through songs one by one
        for entity in table_client.query_entities(query_filter=playlist_filter):
            file_path = entity.get('path')
            chunks = entity.get('chunks')
            artist = entity.get('artist')
            title = entity.get('title')

            if file_path and chunks is None :
                
                print(f"Processing {counter}: {file_path}")
                try:
                    # Load the audio file
                    y, sr = librosa.load(file_path, sr=None, mono=False)

                    # Resample to mono and 16kHz
                    y_mono = librosa.to_mono(y)
                    y_resampled = librosa.resample(y_mono, orig_sr=sr, target_sr=sample_rate)

                    # Calculate chunk size and hop length
                    chunk_samples = int(chunk_duration_ms * sample_rate / 1000)
                    hop_samples = int(chunk_samples * (1 - overlap_factor))

                    number_of_chunks = 0
                    # Split into chunks and work on each
                    for i, start_frame in enumerate(range(0, len(y_resampled) - chunk_samples + 1, hop_samples)):
                        end_frame = start_frame + chunk_samples
                        # Create chunk and save to disk
                        chunk = y_resampled[start_frame:end_frame]
                        chunk_filename = f"chunk_{artist}_{title}_{i}.wav"
                        chunk_filename = chunk_filename.replace(" ", "_")
                        chunk_path = os.path.join("chunks", chunk_filename)
                        sf.write(chunk_path, chunk, sample_rate)

                        print(f"  Saved chunk: {chunk_path}")
                        time.sleep(0.1)

                        # VGGish magic
                        embeddings = get_vggish_embeddings(chunk_path)

                        # Save embedding vector(128)
                        if embeddings is not None:
                            embeddings_dict[chunk_path] = embeddings

                            # Save to Cosmos DB
                            embedding_document = {
                                "id": f"{entity.get('RowKey')}_chunk_{i}", # Unique ID
                                "artist": artist,
                                "title": title,
                                "original_path": file_path,
                                "playlist": "90s", # Assuming all are '90s' for now
                                "chunk": i,
                                "embedding": embeddings[0].tolist()
                            }

                            try:
                                cosmos_container.upsert_item(body=embedding_document)
                                print(f"  Saved embedding for chunk {i} to Cosmos DB")
                            except exceptions.CosmosHttpResponseError as e:
                                print(f"  Error saving to Cosmos DB: {e}")

                            writer.writerow({"counter": counter, "chunk_path": chunk_path})

                        # Delete the chunk file
                        try:
                            os.remove(chunk_path)
                            print(f"  Deleted chunk: {chunk_path}")
                        except OSError as e:
                            print(f"Error deleting chunk {chunk_path}: {e}")

                        number_of_chunks = i

                    # acknlowlaedge in table
                    entity["chunks"] = number_of_chunks
                    table_client.update_entity(entity=entity)
                    print(f"  Updated entity: {entity.get('RowKey')}. Chunks: {number_of_chunks}")

                    counter += 1

                    if counter >= 10:
                        break

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

            else:
                print(f"Warning: 'path' not found for entity.")
                
    # Optionally close the TensorFlow session if you initialized it outside the loop
    if 'session' in locals():
        session.close()

if __name__ == "__main__":
    main()