import time
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceNotFoundError

counter = 0
table_name = "ytvideos"

def main():
    global counter

    with open ("../VDJ/azure_table_connection_string", 'r', encoding='utf-8') as connection_string_file :
        connection_string = connection_string_file.read()

    try :
        table_client = TableClient.from_connection_string(conn_str=connection_string, table_name=table_name)

        for entity in table_client.list_entities() :

            rating = 0
            videoTitle = entity["videoTitle"].lower()
            channelName = entity["channelName"].lower()

            if "topic" in channelName :
                rating -=1
            if "pillow" in channelName :
                rating -=1
            if "lyrics" in channelName :
                rating -=1
            if "7clouds" in channelName :
                rating -=1
            if "cassiopeia" in channelName :
                rating -=1
            if "lyrixa" in channelName :
                rating -=1

            if "vevo" in channelName :
                rating +=1
            if "official" in channelName :
                rating +=1
            if "remastered" in channelName :
                rating +=1
            if "restored" in channelName :
                rating +=1

            if "live" in videoTitle :
                rating -= 1
            if "lyric" in videoTitle :
                rating -= 1
            if "audio" in videoTitle :
                rating -= 1

            if "offiziell" in videoTitle :
                rating += 1
            if "official" in videoTitle :
                rating += 1
            if "hd" in videoTitle :
                rating += 1
            if "hq" in videoTitle :
                rating += 1
            if "4k" in videoTitle :
                rating += 1
            if "remastered" in videoTitle :
                rating += 1
            if "original" in videoTitle :
                rating += 1

            entity["rating"] = rating

            print(str(counter) + ": " + str(rating) + " - " + videoTitle + " - " + channelName)
            table_client.update_entity(entity=entity)
            counter += 1
            # time.sleep(1)

    except Exception as e:
        print(f"Error updating Azure Table rows: {e}")

if __name__ == "__main__":
    main()