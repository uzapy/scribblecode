# This is a Python script that demonstrates how to get the currently playing
# track from the Music app on macOS and find the artist's country of origin
# by querying the Wikidata database.

import subprocess
import time
import json
import requests
import re

def get_current_track_info():
    """
    Uses AppleScript to get the name and artist of the current song in the Music app.
    
    Returns a tuple (song_name, artist_name) or (None, None) if no song is playing.
    """
    # AppleScript to get the current track and artist
    applescript = """
    tell application "Music"
        if player state is playing then
            set current_track to current track
            set track_name to name of current_track
            set artist_name to artist of current_track
            return track_name & "|" & artist_name
        else
            return "stopped"
        end if
    end tell
    """
    
    # Run the AppleScript command
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip() != "stopped":
        track_info = result.stdout.strip().split('|')
        return track_info[0], track_info[1]
    else:
        return None, None

def wikidata_query_origin(artist_name):
    """
    Queries Wikidata for the artist's place of origin and its country using a SPARQL query.
    
    Returns a string with the country/place name or a message if not found.
    """
    query_url = "https://query.wikidata.org/sparql"
    
    # SPARQL query to find the location of formation (P740), place of birth (P19),
    # or country of citizenship (P27) for an artist.
    # It also queries the country for that location by following the administrative
    # entity chain (P131) and the direct country property (P17).
    sparql_query = f"""
    SELECT ?originLabel ?countryLabel WHERE {{
      ?artist rdfs:label "{artist_name}"@en.
      
      # Find the primary origin
      {{ ?artist wdt:P740 ?origin. }}
      UNION
      {{ ?artist wdt:P19 ?origin. }}
      UNION
      {{ ?artist wdt:P27 ?origin. }}
      
      # Try to find a country, either directly or through a parent location
      OPTIONAL {{
        {{ ?origin wdt:P17 ?country. }}
        UNION
        {{ ?origin wdt:P131* ?parent_location. ?parent_location wdt:P17 ?country. }}
      }}
      
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    LIMIT 1
    """

    headers = {'Accept': 'application/json'}
    params = {'query': sparql_query}

    try:
        response = requests.get(query_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        
        data = response.json()
        bindings = data['results']['bindings']
        
        if bindings:
            origin_label = bindings[0]['originLabel']['value']
            country_label = bindings[0]['countryLabel']['value'] if 'countryLabel' in bindings[0] else None
            
            if country_label and origin_label != country_label:
                return f"{origin_label}, {country_label}"
            else:
                return origin_label
        else:
            return "Origin not found in Wikidata."

    except requests.exceptions.RequestException as e:
        print(f"Error during Wikidata API call: {e}")
        return "Query failed."

def main():
    """
    Main function to continuously check for the current song.
    """
    last_song = None
    
    print("Listening for music... Press Ctrl+C to stop.")
    
    try:
        while True:
            song, artist = get_current_track_info()
            if song and song != last_song:
                print(f"Now playing: {song} by {artist}")
                
                # Get the artist's origin from Wikidata
                origin = wikidata_query_origin(artist)
                print(f"Origin: {origin}\n")
                
                last_song = song
            elif not song:
                print("Music is stopped.")
                last_song = None
                
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()
