# This is a Python script that demonstrates how to get the currently playing
# track from the Music app on macOS using AppleScript.

import subprocess
import time

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
                last_song = song
            elif not song:
                print("Music is stopped.")
                last_song = None
                
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\nExiting.")

if __name__ == "__main__":
    main()
