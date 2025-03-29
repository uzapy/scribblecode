import json
import os
import requests
import sounddevice
import soundfile
import time
from azure.data.tables import TableClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from fuzzywuzzy import fuzz

input_file_prefix = "./auddio/recorded_audio_"
recording_duration = 15
sample_rate = 44100
table_name = "playlists"
connection_string = ""

def record_audio(filename, duration, samplerate):
    """Records audio from the microphone and saves it to a WAV file."""
    print(f"Recording audio for {duration} seconds...")
    try:
        recording = sounddevice.rec(int(duration * samplerate), samplerate=samplerate, channels=1) # record in stereo
        sounddevice.wait()  # Wait until recording is finished
        soundfile.write(filename, recording, samplerate)
        print(f"Audio saved to {filename}")
        return True
    except Exception as e:
        print(f"Error during recording: {e}")
        return False

def fuzzy_search_azure_table_top_n(artist, title, top_n=3):
    """Performs a fuzzy search against an Azure Storage Table."""
    with open ("./azure_table_connection_string", 'r', encoding='utf-8') as connection_string_file :
        connection_string = connection_string_file.read()
    table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
    entities = table_client.list_entities()
    matches = []

    for entity in entities:
        if entity.get("playlist") == "90s" and entity.get("videoFilePath") is not None :
            artist_score = fuzz.token_set_ratio(artist, entity["artist"])
            title_score = fuzz.token_set_ratio(title, entity["title"])
            combined_score = (artist_score + title_score) / 2  # Average score
            matches.append((combined_score, entity))

    matches.sort(key=lambda x: x[0], reverse=True)  # Sort by score in descending order
    return matches[:top_n]  # Return the top N matches

def main():
    with open ("./auddio_API_Token", 'r', encoding='utf-8') as token_file :
        api_token = token_file.read()

    counter = 0
    while True:
        input_file = f"{input_file_prefix}{counter}.wav"
        if record_audio(input_file, recording_duration, sample_rate):
            try:
                with open(input_file, 'rb') as audio_file:
                    files = {'file': audio_file} # use the 'file' parameter as per audd.io docs
                    data = {'api_token': api_token}
                    result = requests.post('https://api.audd.io/', files=files, data=data)
                    response = json.loads(result.text)
                    print(response)

                    if response['status'] == 'success' and 'result' in response and response['result']:
                        artist = response['result']['artist']
                        title = response['result']['title']

                        top_matches = fuzzy_search_azure_table_top_n(artist, title)

                        if top_matches:
                            print("Top matches found:")
                            for score, match in top_matches:
                                print(f"  Score: {score}")
                                print(f"    Artist: {match['artist']}")
                                print(f"    Title: {match['title']}")
                                print(f"    Path: {match['path']}")
                                # Print other relevant fields from the Azure Table entity
                        else:
                            print("No matching entries found in Azure Table.")

                    counter += 1

            except FileNotFoundError:
                print(f"Error: Audio file not found at {input_file}")
            except Exception as e:
                print(f"An error occurred: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()