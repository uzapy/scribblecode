import csv
import time
from googleapiclient.discovery import build

counter = 0
yt_api_key_file = "../VDJ/yt_api_key"
input_file = "../VDJ/playlists3.csv"
output_file = "../VDJ/video_results.csv"

def main():
    global counter

    with open (yt_api_key_file, 'r', encoding='utf-8') as key_file :
        yt_api_key = key_file.readlines()

    with open (input_file, 'r', encoding='utf-8') as csv_list :
        songs = csv_list.readlines()

    try :
        youtube = build("youtube", "v3", developerKey=yt_api_key)

        with open(output_file, mode='a', newline='', encoding='utf-8') as output:
            writer = csv.DictWriter(output, fieldnames=["counter","title","id","channel","thumb","published"])
            writer.writeheader()

            for song in songs :

                request = youtube.search().list(
                    part="snippet",
                    maxResults=10,
                    q=song,
                    type="video"  # Filter to only videos
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    snippet = item["snippet"]
                    video_id = item["id"]["videoId"]
                    writer.writerow({"counter" : counter, \
                                    "title" : snippet["title"], \
                                    "id" : video_id, \
                                    "channel" : snippet["channelTitle"], \
                                    "thumb" : snippet["thumbnails"]["default"]["url"] if "thumbnails" in snippet and "default" in snippet["thumbnails"] else None, \
                                    "published" : snippet["publishedAt"]})
                    print(str(counter) + ": " + snippet["title"])

            counter += 1
            time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()