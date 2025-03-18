import os
import time
from azure.data.tables import TableClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError

counter = 0
table_name = "playlists"
container_name = "audios"

def main():
    global counter

    with open ("../VDJ/azure_table_connection_string", 'r', encoding='utf-8') as connection_string_file :
        connection_string = connection_string_file.read()

    try :
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        for entity in table_client.list_entities() :

            if entity.get("playlist") == "90s" :
                file_path = entity.get("path")

                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue

                # Extract blob path from file path
                blob_path = os.path.relpath(file_path, " add path from root to music folder here")
                blob_client = container_client.get_blob_client(blob_path)

                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                    print(f"{counter} - Uploaded: {file_path} to {container_name}/{blob_path}")

                counter += 1
                time.sleep(1)

    except Exception as e:
        print(f"Error updating Azure Table rows: {e}")

if __name__ == "__main__":
    main()