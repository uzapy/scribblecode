import os
import time
import yt_dlp
from azure.data.tables import TableClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError

counter = 0
table_name = "playlists"
container_name = "videos"
main_playlist = "90s"
youtube_base_URL = "https://www.youtube.com/watch?v="

def main():
    global counter

    with open ("./azure_table_connection_string", 'r', encoding='utf-8') as connection_string_file :
        connection_string = connection_string_file.read()

    with open ("./music_path_from_root", 'r', encoding='utf-8') as path_file :
        path_from_root = path_file.read()

    try :
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for entity in table_client.list_entities() :

            if entity.get("playlist") == main_playlist and entity.get("video") is not None and entity.get("videoFilePath") is None:
                file_path = entity.get("path")

                # Extract blob path from file path
                blob_path = os.path.relpath(file_path, path_from_root)
                print(f"{counter} - Entity: {blob_path}")
                directories = blob_path.rsplit('/', 1)[0]
                file_name = blob_path.rsplit('/', 1)[1].rsplit('.', 1)[0]

                ydl_opts = {
                    'outtmpl': f'./videos/{file_name}.%(ext)s',  # Output filename format
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]', #best video and audio, limited to 1080p for space reasons.
                    'merge_output_format': 'mp4', #merge video and audio into mp4
                    'noplaylist': True, #do not download playlists.
                    'verbose': True, #adds verbose output
                    }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download(youtube_base_URL + entity.get("video"))
                    print(f"{counter} - Downloaded video: './videos/{file_name}.mp4'")

                    # upload to blob
                    video_file_path = directories + '/' + file_name + '.mp4'
                    blob_client = container_client.get_blob_client(video_file_path)
                    with open(f'./videos/{file_name}.mp4', "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)
                        print(f"{counter} - Uploaded: {'./' + video_file_path}/{video_file_path}")

                    # acknlowlaedge in table
                    entity["videoFilePath"] = video_file_path
                    table_client.update_entity(entity=entity)

                    # delete local file
                    os.remove(f'./videos/{file_name}.mp4')
                    print(f"{counter} - Local file deleted: ./videos/{file_name}.mp4")


                except yt_dlp.DownloadError as e:
                    print(f"Download failed: {e}")
                except Exception as e:
                    print(f"An unexpected error occured: {e}")


                counter += 1
                time.sleep(10)

    except Exception as e:
        print(f"Error updating Azure Table rows: {e}")

if __name__ == "__main__":
    main()