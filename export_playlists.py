import os
import argparse
import csv
import xml
import xml.etree.ElementTree as ET

counter = 0
playlist_folder = "../VDJ/playlists/"
output_file = "../VDJ/execution.log"

# <song path="/Volumes/Macintosh HD/Users/uzapy/Music/Eigene Musik/Alles/Snap - Rhythm Is a Dancer.mp3" size="9000428" songlength="224.0" bpm="124.266" key="Am" artist="Snap!" title="Rhythm Is a Dancer" idx="2" />
class Song:
    def __init__(self, path, size, songlength, bpm, key, artist, title, idx):
        self.path = path
        self.size = size
        self.songlength = songlength
        self.bpm = bpm
        self.key = key
        self.artist = artist
        self.title = title
        self.idx = idx

def parse_song(song_element):
    return Song(
        file_path=song_element.get('path'),
        file_size=song_element.get('size'),
        songlength=song_element.get('songlength'),
        bpm=song_element.get('bpm'),
        key=song_element.get('key'),
        artist=song_element.get('artist'),
        title=song_element.get('title'),
        idx=song_element.get('idx'),
    )

def main():
    global counter
    # file_list = []

    with open(output_file, mode='w', newline='', encoding='utf-8') as output:
        writer = csv.DictWriter(output, fieldnames=["counter","playlist","path","size", "songlength","bpm","key","artist","title","idx"])
        writer.writeheader()

        for file in os.listdir(playlist_folder) :
            if os.path.isfile(os.path.join(playlist_folder, file)) and file != ".DS_Store" :
                # file_list.append(file)
                with open(os.path.join(playlist_folder, file), 'r', encoding='utf-8') as xml:
                    xml_root = ET.parse(xml).getroot()
                    for song_element in xml_root.findall("song") :
                        writer.writerow({"counter" : counter, \
                                        "playlist" : file, \
                                        "path" : song_element.get('path'), \
                                        "size" : song_element.get('size'), \
                                        "songlength" : song_element.get('songlength'), \
                                        "bpm" : song_element.get('bpm'), \
                                        "key" : song_element.get('key'), \
                                        "artist" : song_element.get('artist'), \
                                        "title" : song_element.get('title'), \
                                        "idx" : song_element.get('idx'), })
                        counter+=1

if __name__ == "__main__":
    main()
