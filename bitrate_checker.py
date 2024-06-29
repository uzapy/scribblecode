import os
import argparse
import csv
from mutagen.mp3 import MP3

counter = 0
output_file = "/Users/uzapy/Desktop/export.csv"

def print_files_recursively(dir_path, writer):
    # Iterate through each file/directory in the given directory
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        global counter

        # If the item is a file, print its name
        if os.path.isfile(item_path) and (item_path.lower().endswith('.mp3') or item_path.lower().endswith('.m4a') or item_path.lower().endswith('.wma')):
            bitrate = get_bitrate(item_path)
            counter += 1
            print(f"{counter}, {bitrate}, {item_path}, {os.path.getsize(item_path)}")
            writer.writerow({"counter": counter, "bitrate": bitrate, "size": os.path.getsize(item_path), "type": os.path.splitext(item_path)[1], "path": item_path})
        else:
            counter += 1
            print(f"{counter}, 0, {item_path}, {os.path.getsize(item_path)}")
            writer.writerow({"counter": counter, "bitrate": "", "size": os.path.getsize(item_path), "type": os.path.splitext(item_path)[1], "path": item_path})

        #if(counter > 99):
            #break
        
        # If the item is a directory, recursively call this function
        if os.path.isdir(item_path):
            print_files_recursively(item_path, writer)

#def get_bitrate(audio_file):
    #audio = pydub.AudioSegment.from_file(audio_file)
    #return audio.frame_rate

def get_bitrate(filepath):
    try:
        audio = MP3(filepath)
        return audio.info.bitrate / 1000  # Convert to kbps
    except:
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help = "Enter your variable")
    args = parser.parse_args()

    if args.path:
        print(f"Received variable value from command line: {args.path}")
        if os.path.isdir(args.path):
            with open(output_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["counter","bitrate","size","type","path"])
                writer.writeheader()
                print(f"Files in the directory {args.path} are:")
                print_files_recursively(args.path, writer)
        else:
            print("The directory path you entered does not exist.")
    else:
        print("No variable received from command line.")

if __name__ == "__main__":
    main()