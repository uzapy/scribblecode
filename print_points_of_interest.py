import os
import argparse
import csv
import xml
import xml.etree.ElementTree as ET

counter = 0
output_file = "../VDJ/execution.log"

class Song:
    def __init__(self, file_path, file_size, tags, infos, scan, pois):
        self.file_path = file_path
        self.file_size = file_size
        self.tags = tags
        self.infos = infos
        self.scan = scan
        self.pois = pois

class Tags:
    def __init__(self, author, title, genre, album, track_number, year, bpm, flag):
        self.author = author
        self.title = title
        self.genre = genre
        self.album = album
        self.track_number = track_number
        self.year = year
        self.bpm = bpm
        self.flag = flag

class Infos:
    def __init__(self, song_length, last_modified, first_play, last_play, play_count, bitrate, cover):
        self.song_length = song_length
        self.last_modified = last_modified
        self.first_play = first_play
        self.last_play = last_play
        self.play_count = play_count
        self.bitrate = bitrate
        self.cover = cover

class Scan:
    def __init__(self, version, bpm, alt_bpm, volume, key, flag):
        self.version = version
        self.bpm = bpm
        self.alt_bpm = alt_bpm
        self.volume = volume
        self.key = key
        self.flag = flag

class Poi:
    def __init__(self, pos, poi_type, name=None, num=None, color=None, point=None):
        self.pos = pos
        self.poi_type = poi_type
        self.name = name
        self.num = num
        self.color = color
        self.point = point

def parse_song(song_element):
    tags_element = song_element.find('Tags')

    tags = Tags(
        author=tags_element.get('Author'),
        title=tags_element.get('Title'),
        genre=tags_element.get('Genre'),
        album=tags_element.get('Album'),
        track_number=tags_element.get('TrackNumber'),
        year=tags_element.get('Year'),
        bpm=tags_element.get('Bpm'),
        flag=tags_element.get('Flag')
    )
    
    infos_element = song_element.find('Infos')
    infos = Infos(
        song_length=infos_element.get('SongLength'),
        last_modified=infos_element.get('LastModified'),
        first_play=infos_element.get('FirstPlay'),
        last_play=infos_element.get('LastPlay'),
        play_count=infos_element.get('PlayCount'),
        bitrate=infos_element.get('Bitrate'),
        cover=infos_element.get('Cover')
    )
    
    scan_element = song_element.find('Scan')
    if scan_element is not None:
        scan = Scan(
            version=scan_element.get('Version'),
            bpm=scan_element.get('Bpm'),
            alt_bpm=scan_element.get('AltBpm'),
            volume=scan_element.get('Volume'),
            key=scan_element.get('Key'),
            flag=scan_element.get('Flag')
        )
    else:
        scan = None
    
    pois = []
    for poi_element in song_element.findall('Poi'):
        pois.append(Poi(
            pos=poi_element.get('Pos'),
            poi_type=poi_element.get('Type'),
            name=poi_element.get('Name'),
            num=poi_element.get('Num'),
            color=poi_element.get('Color'),
            point=poi_element.get('Point')
        ))
    
    return Song(
        file_path=song_element.get('FilePath'),
        file_size=song_element.get('FileSize'),
        tags=tags,
        infos=infos,
        scan=scan,
        pois=pois
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help = "Enter your variable")
    args = parser.parse_args()

    if args.path:
        print(f"Received variable value from command line: {args.path}")
        global counter
        xml_root = ET.parse(args.path)
        songs = []

        with open(output_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["counter","length", "bpm", "name","pos","num","color","type"])
            writer.writeheader()

            for song_element in xml_root.findall('Song'):
                songs.append(parse_song(song_element))

                for poi in songs[-1].pois:
                    writer.writerow({"counter": counter, "length": songs[-1].infos.song_length, "bpm": songs[-1].scan.bpm, "name": poi.name, "pos": poi.pos, "num": poi.num, "color": poi.color, "type": poi.poi_type})

                counter+=1
                # if counter > 1000:
                #     break

    else:
        print("No variable received from command line.")

if __name__ == "__main__":
    main()
