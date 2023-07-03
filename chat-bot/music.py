import spotipy as sp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import random
import os
import csv
import re
import time
from functions import *

global_spotify = None
global_device_id = None

class InvalidSearchError(Exception):
    pass

#-------------------------------------Setup-------------------------------------

# Creates a connection to the spotify api and connects to the particular device
def initialise_spotify(client_id, client_secret, redirect_uri, username, device_name, scope):
    auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, username=username)
    spotify = sp.Spotify(auth_manager=auth_manager)
    # Selecting device to play from
    devices = spotify.devices()
    for d in devices['devices']:
        d['name'] = d['name'].replace('’', '\'')
        if d['name'] == device_name:
            device_id = d['id']
            break
    print(f"Spotify Successfully Connected - {device_id}")
    return spotify, device_id

# Globalises the variables needed for playback
def send_variables(spotify, device_id):
    global global_spotify
    global global_device_id
    global_spotify = spotify
    global_device_id = device_id

#------------------------------------Status-------------------------------------

# Checks to see the status of the playback
def is_track_paused(spotify: Spotify) -> bool:
    current_playback = spotify.current_user_playing_track()
    if current_playback and current_playback['is_playing']:
        return True
    return False

#---------------------------------Fetching URI----------------------------------

# Searches using Spotify api for a particular song
def get_track_uri(spotify: Spotify, name: str, artist=None) -> str:
    original_name = name
    if artist == None:
        original_artist = "Unknown"
        name = name.replace(" ", "+")
        name = name.replace("'", "")
        search_title = name
    else:
        original_artist = artist
        name = name.replace(" ", "+")
        name = name.replace("'", "")
        artist = artist.replace(" ", "+")
        search_title = name + "+" + artist

    results = spotify.search(q=search_title, limit=1, type='track')
    if not results['tracks']['items']:
        raise InvalidSearchError(f'No track named "{original_name} by {original_artist}"')
    track_uri = results['tracks']['items'][0]['uri']
    return track_uri

# Searches using Spotify api for a particular playlist
def get_playlist_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='playlist')
    if not results['playlists']['items']:
        raise InvalidSearchError(f'No playlist named "{original}"')
    playlist_uri = results['playlists']['items'][0]['uri']
    print(results['playlists']['items'][0]['name'])
    return playlist_uri

# Searches using Spotify api for a particular podcast
def get_podcast_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='show')
    if not results['shows']['items']:
        raise InvalidSearchError(f'No podcast named "{original}"')
    podcast_uri = results['shows']['items'][0]['uri']
    print(results['shows']['items'][0]['name'])
    return podcast_uri

# Searches using Spotify api for a particular podcast genre
def get_podcast_genre_uri(spotify: Spotify, genre: str) -> str:
    genre = genre.lower().capitalize()
    results = spotify.search(q=genre, limit=50, type='show')
    podcasts = results['shows']['items']

    if not podcasts:
        raise InvalidSearchError(f'No podcasts found for genre "{genre}"')

    random_podcast = random.choice(podcasts)
    podcast_uri = random_podcast['uri']
    print(random_podcast['name'])
    return podcast_uri,random_podcast['name'],random_podcast['publisher']

# Searches using Spotify api for a particular artist
def get_artist_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='artist')
    if not results['artists']['items']:
        raise InvalidSearchError(f'No artist named "{original}"')
    artist_uri = results['artists']['items'][0]['uri']
    print(results['artists']['items'][0]['name'])
    return artist_uri

# Searches using Spotify api for a particular album
def get_album_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='album')
    if not results['albums']['items']:
        raise InvalidSearchError(f'No album named "{original}"')
    album_uri = results['albums']['items'][0]['uri']
    return album_uri

# Uses Spotify api function to play the liked songs of user
def get_liked_songs(spotify: Spotify):
    liked_songs = []
    offset = 0
    limit = 50  # Adjust the limit to control the number of tracks fetched per page
    # Fetch all pages of liked tracks
    while True:
        results = spotify.current_user_saved_tracks(limit=limit, offset=offset)
        tracks = results['items']
        liked_songs.extend(tracks)
        if len(tracks) < limit:
            break
        offset += limit
    # Randomly select a sample of 100 tracks
    random.shuffle(liked_songs)
    sample = liked_songs[:100]
    return sample

#-----------------------------------Playback------------------------------------

# Starts playback of a particular song
def play_track(spotify=None, device_id=None, uri=None):
    time.sleep(5)
    spotify.start_playback(device_id=device_id, uris=[uri])

# Starts playback of a particular playlist
def play_playlist(spotify=None, device_id=None, uri=None):
    time.sleep(5)
    spotify.start_playback(device_id=device_id, context_uri=uri)

# Start playback of a particular podcast
def play_podcast(spotify=None, device_id=None, uri=None):
    time.sleep(5)
    spotify.start_playback(device_id=device_id, context_uri=uri)

# Starts playback of a particular artist
def play_artist(spotify=None, device_id=None, uri=None):
    time.sleep(5)
    spotify.start_playback(device_id=device_id, context_uri=uri)

# Starts playback of liked songs
def play_liked_songs(spotify=None, device_id=None, liked_songs=None):
    time.sleep(5)
    track_uris = [track['track']['uri'] for track in liked_songs]
    spotify.start_playback(device_id=device_id, uris=track_uris)
    
# Changes playback to next song on the queue
def next_track(spotify=None, device_id=None):
    spotify.next_track(device_id=device_id)

# Changes playback to previous song on the queue
def prev_track(spotify=None, device_id=None):
    spotify.previous_track(device_id=device_id)

# Pauses playback
def pause_track(spotify=None, device_id=None):
    spotify.pause_playback(device_id=device_id)

# Plays playback
def resume_play(spotify=None, device_id=None):
    spotify.start_playback(device_id=device_id)

#-----------------------------------Playback------------------------------------

# Sets volume to a percentage from 0 to 100
def set_volume(spotify=None, device_id=None, volume=None):
    spotify.volume(volume, device_id=device_id)

# Gets current volume percentage
def get_current_volume(spotify=None, device_id=None):
    current_playback = spotify.current_playback()
    if current_playback and current_playback['device']:
        if current_playback['device']['id'] == device_id:
            volume_level = current_playback['device']['volume_percent']
            return volume_level
    return None

#--------------------------------Podcast Genres---------------------------------

# Initially randomises favourite ratings
def init_podcast_ratings():
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()

    # Iterate over each topic and update its score
    for topic in topics:
        # Generate a random score between 4 and 8 (inclusive)
        new_score = random.randint(4, 8)
        change_podcast_rating(topic, new_score)

    print("Scores randomized successfully.")

# Reads genres.csv file to get users podcast ratings
def fetch_podcast_ratings():
    # Open the CSV file
    file_path = "assets/genres.csv"
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        # Create a dictionary to store the topics and their corresponding numbers
        topics = {}
        # Iterate over each row in the CSV file
        for row in reader:
            topic = row[0]
            number = int(row[1])
            # Add the topic and its number to the dictionary
            topics[topic] = number
        return topics
        
# Fetches favourite top 3 podcast genres
def fav_podcast_genres():
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()
    # Sort the topics based on their scores in descending order
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    # Retrieve the top two topics
    top_topics = sorted_topics[:2]
    highest_scores = [score for _, score in top_topics]
    # Find additional topics with the same score as the top two topics
    result = [topic for topic, score in sorted_topics if score in highest_scores]
    return result

# Sorts all genres into 3 different categories
def categorize_podcast_genres():
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()
    # Sort the topics based on their scores in descending order
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    # Calculate the number of topics for each percentile
    total_topics = len(sorted_topics)
    top30_count = int(0.3 * total_topics)
    next30_count = int(0.6 * total_topics)
    # Initialize the arrays for each percentile
    top_genres = [] #Top 30% of genres
    mid_genres = [] #40-70% of genres
    avoid_genres = [] #Bottom 40% of genres
    # Iterate over the sorted topics and distribute them into the arrays
    for i, (topic, score) in enumerate(sorted_topics):
        if score == sorted_topics[0][1]:
            top_genres.append(topic)
        elif score == sorted_topics[-1][1]:
            avoid_genres.append(topic)
        elif i < top30_count:
            top_genres.append(topic)
        elif i < next30_count:
            mid_genres.append(topic)
        else:
            avoid_genres.append(topic)

    return top_genres, mid_genres, avoid_genres

# Updates users ratings in the csv file
def change_podcast_rating(topic, new_score):
    # Check if the new score is within the range of 1-10
    if new_score < 1 or new_score > 10:
        print("Invalid score. Score must be between 1 and 10.")
        return
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()
    # Find the topic in the dictionary and update its score
    if topic in topics:
        topics[topic] = new_score
    else:
        print("Topic not found.")
        return
    # Write the updated scores back to the CSV file
    with open('assets/podcast/genres.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for topic, score in topics.items():
            writer.writerow([topic, score])
    print("Score updated successfully.")

# Users input changes the ratings of the podcasts
def update_podcast_rating(topic, rating):
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()
    # Find the topic in the dictionary and retrieve its current score
    current_score = topics.get(topic)
    if current_score is None:
        print("Topic not found.")
        return
    # Update the score based on the rating input
    if rating == "favourite":
        new_score = 9
    elif rating == "love":
        new_score = min(current_score + 2, 10)
    elif rating == "like":
        new_score = min(current_score + 1, 10)
    elif rating == "dislike":
        new_score = max(current_score - 1, 1)
    elif rating == "strongly dislike":
        new_score = max(current_score - 2, 1)
    elif rating == "hate":
        new_score = 2
        change_podcast_rating(topic, new_score)
        return
    else:
        print("Invalid rating.")
        return
    # Update the score using the change_podcast_rating function
    change_podcast_rating(topic, new_score)

# Retrieves previous listened to podcasts
def fetch_prev_podcast():
    file_path = "assets/podcast/podcast_history.csv"
    if not os.path.exists(file_path):
        return False 
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  
        for row in reader:
            podcast_genre = row[0]        
    topics = fetch_podcast_ratings()
    current_score = topics.get(podcast_genre)
    return podcast_genre, current_score

# Saving previously played podcasts 
def podcast_history(podcast_genre,podcast_name,podcast_artist):
    file_path = "assets/podcast/podcast_history.csv"
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row if the file is empty
        if not file_exists or os.stat(file_path).st_size == 0:
            writer.writerow(["Genre","Podcast Name", "Artist"])
        # Write the data to the next empty row
        writer.writerow([podcast_genre, podcast_name, podcast_artist])
    print("Podcast has been written to the CSV file.")

# Check if a podcast has been previously played
def podcast_history_check(podcast_name, podcast_artist):
    file_path = "assets/podcast/podcast_history.csv"
    if not os.path.exists(file_path):
        return False 
    with open(file_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  
        for row in reader:
            if row[1] == podcast_name and row[2] == podcast_artist:
                return True  # Exact match found
    return False  # No exact match found    

#----------------------------Information Extraction-----------------------------

# Speech to text retrieval of given song and artist with 'play'
def extract_song_info(text):
    # Try to match the pattern 'play' followed by song name and artist
    match = re.search(r'play(?: me)?\s(.+?)(?:\sby\s(.+))?$', text, re.IGNORECASE)
    if match:
        song_name = match.group(1).strip()
        artist = match.group(2).strip() if match.group(2) is not None else ""
    else:
        # If the previous pattern fails, try to match 'listen to' followed by song name and artist, or just the song name if 'by' is not present
        match = re.search(r'listen to(?:\s(.+?))(?:\sby\s(.+))?$', text, re.IGNORECASE)
        if match:
            song_name = match.group(1).strip() if match.group(1) is not None else ""
            artist = match.group(2).strip() if match.group(2) is not None else ""
        else:
            song_name = ""
            artist = ""
    return song_name.title(), artist.title()

# Speech to text retrieval of given song and artist without 'play'
def extract_song_and_artist(text):
    # Extract the song name and artist from the user input
    match = re.search(r'(.+?)(?:\sby\s(.+))?$', text)
    song_name = match.group(1).strip() if match.group(1) is not None else ""
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name.title(), artist.title()

# Speech to text retrieval of given playlist
def extract_playlist_info(text):
    # Try to match the pattern 'playlist' followed by the playlist name
    match = re.search(r'playlist\s(.+)$', text, re.IGNORECASE)
    if match:
        playlist_name = match.group(1).strip()
    else:
        playlist_name = ""
    return playlist_name

# Speech to text retrival of given podcast
def extract_podcast_info(text):
    match = re.search(r'podcast\s(.+)$', text, re.IGNORECASE)
    if match:
        podcast_name = match.group(1).strip()
    else:
        podcast_name = ""
    return podcast_name

# Speech to text retrieval of playback volume
def extract_volume_percentage(text):
    # Try to find the pattern 'to' followed by a number, with or without '%'
    match = re.search(r'to\s+(\d+)%?', text, re.IGNORECASE)
    if match:
        volume_percentage = int(match.group(1))
        return volume_percentage
    else:
        return None

#-------------------------------Watson Functions--------------------------------

# Request a song
def request_song(text):
    local_recogniser = get_recogniser()
    play_sound("sound/songRequest.mp3", 1, blocking=True)
    done = False
    while not done:
        try:
            song = recognise_input(local_recogniser)
            play_sound("sound/searching.mp3", 1, True)
            song_name, artist = extract_song_and_artist(song)
            print("Song:", song_name)
            print("Artist:", artist)
            

            if artist == "":
                uri = get_track_uri(spotify=global_spotify, name=song_name)
                play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
            # If song title + artist provided
            else:
                uri = get_track_uri(spotify=global_spotify, name=song_name, artist=artist)
                play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
            done = True
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 0.5, blocking=True)

# Request a specific pre-given song
def request_specific_song(text):
    song_name, artist = extract_song_info(text)
    play_sound("sound/searching.mp3", 1, True)
    if (artist == "" and song_name == ""):
        play_sound("sound/searchFailed.mp3", 1, True)
        return
    # If only song title provided
    if artist == "":
        uri = get_track_uri(spotify=global_spotify, name=song_name)
        play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
    # If song title + artist provided
    else:
        uri = get_track_uri(spotify=global_spotify, name=song_name, artist=artist)
        play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)

# Request a playlist
def request_playlist(text):
    local_recogniser = get_recogniser()
    play_sound("sound/playlistRequest.mp3", 1, blocking=True)
    done = False
    while not done:
        try:
            playlist_name = recognise_input(local_recogniser).title()
            print("Playlist: ", playlist_name)
            time.sleep(4)
            uri = get_playlist_uri(spotify=global_spotify, name=playlist_name)
            play_playlist(spotify=global_spotify, device_id=global_device_id, uri=uri)
            speak(f"Playing {playlist_name}.")
            done = True
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=True)

# Request a specific pre-given playlist
def request_specific_playlist(text):
    playlist_name = extract_playlist_info(text).title()
    play_sound("sound/searching.mp3", 1, True)
    if playlist_name == "":
        play_sound("sound/searchFailed.mp3", 1, blocking=True)
        return
    else:
        time.sleep(4)
        uri = get_playlist_uri(spotify=global_spotify, name=playlist_name)
        play_playlist(spotify=global_spotify, device_id=global_device_id, uri=uri)
        speak(f"Playing {playlist_name}.")

# Request a podcast
def request_podcast(text):
    local_recogniser = get_recogniser()
    play_sound("sound/podcastRequest.mp3", 1, blocking=True)
    done = False
    while not done:
        try:
            podcast_name = recognise_input(local_recogniser).title()
            print("Podcast: ", podcast_name)
            time.sleep(4)
            uri = get_podcast_uri(spotify=global_spotify, name=podcast_name)
            play_podcast(spotify=global_spotify, device_id=global_device_id, uri=uri)
            done = True
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=True)

# Request a specific pre-given podcast
def request_specific_podcast(text):
    podcast_name = extract_podcast_info(text).title()
    play_sound("sound/searching.mp3", 1, True)
    if podcast_name == "":
        play_sound("sound/searchFailed.mp3", 1, blocking=True)
        return
    else:
        time.sleep(4)
        uri = get_podcast_uri(spotify=global_spotify, name=podcast_name)
        play_podcast(spotify=global_spotify, device_id=global_device_id, uri=uri)

# Request a podcast genre
def request_genre_podcast(text):
    local_recogniser = get_recogniser()
    print("Entered request_genre_podcast")
    print("Response:", text)
    pattern1 = r"\ba\s+(.*?)\s+podcast\b|\ban\s+(.*?)\s+podcast\b"
    pattern2 = r"(?:about|on)\s+(.*?)$"
    pattern3 = r"(?:play|suggest|recommend)\s+(.*?)\s+podcast\b"
    pattern4 = r"(?i)(?<=to\s)(?!.*to\s).*?(?=\spodcast)"

    match1 = re.search(pattern1, text, re.IGNORECASE)
    match2 = re.search(pattern2, text, re.IGNORECASE)
    match3 = re.search(pattern3, text, re.IGNORECASE)
    match4 = re.search(pattern4, text, re.IGNORECASE)

    podcast_genre = None

    if match1:
        podcast_genre = match1.group(1) or match1.group(2)
    elif match2:
        podcast_genre = match2.group(1)
    elif match3:
        podcast_genre = match3.group(1)
    elif match4:
        podcast_genre = match4.group()

    
    print("genre identified:", podcast_genre)
    if podcast_genre == "":
        play_sound("sound/searchFailed.mp3", 1, blocking=False)
        return
    else:
        time.sleep(4)
        check_history = True
        while check_history == True:
            print("entered check:")
            uri,podcast_name,podcast_artist = get_podcast_genre_uri(spotify=global_spotify, genre=podcast_genre)
            check_history = podcast_history_check(podcast_name,podcast_artist)
        speak(f"Playing {podcast_genre}.")
        play_podcast(spotify=global_spotify, device_id=global_device_id, uri=uri)
        podcast_history(podcast_genre,podcast_name,podcast_artist)

# Requests Random Podcast from pre-saved favourites
def request_random_podcast(text):
    genres = fav_podcast_genres()
    index = random.randint(0, len(genres) - 1)
    podcast_genre = genres[index]
    time.sleep(4)
    check_history = True
    while check_history == True:
        uri,podcast_name,podcast_artist = get_podcast_genre_uri(spotify=global_spotify, genre=podcast_genre)
        print(podcast_name, podcast_artist)
        check_history = podcast_history_check(podcast_name,podcast_artist)
    speak(f"Playing {podcast_genre}.")    
    play_podcast(spotify=global_spotify, device_id=global_device_id, uri=uri)
    podcast_history(podcast_genre,podcast_name,podcast_artist)

# Calls the check if podcast
def is_music_paused():
    return is_track_paused(spotify=global_spotify)

# Makes pause_track playable from Watson
def pause_music(text):
    pause_track(spotify=global_spotify, device_id=global_device_id)

# Makes resume_play playable from Watson
def play_music(text):
    resume_play(spotify=global_spotify, device_id=global_device_id)

# Overall function to play liked songs
def play_liked(text):
    liked_songs = get_liked_songs(spotify=global_spotify)
    play_liked_songs(spotify=global_spotify, device_id=global_device_id, liked_songs=liked_songs)

# Makes next_track playable from Watson
def play_next(text):
    next_track(spotify=global_spotify, device_id=global_device_id)

# Makes prev_track playable from Watson
def play_previous(text):
    prev_track(spotify=global_spotify, device_id=global_device_id)

# Setting volume on Spotify
def set_vol(text):
    set_vol = extract_volume_percentage(text)
    set_volume(spotify=global_spotify, device_id=global_device_id, volume=set_vol)

# Increases volume of Spotify
def increase_vol(text):
    current_volume = get_current_volume(spotify=global_spotify, device_id=global_device_id)
    if current_volume is not None:
        new_volume = min(current_volume + 10, 100)
        set_volume(spotify=global_spotify, device_id=global_device_id, volume=new_volume)
        print(f"Volume increased to {new_volume}%")
    else:
        print("No active playback or device found.")

# Decreases volume of Spotify
def decrease_vol(text):
    current_volume = get_current_volume(spotify=global_spotify, device_id=global_device_id)
    if current_volume is not None:
        new_volume = max(current_volume - 10, 0)
        set_volume(spotify=global_spotify, device_id=global_device_id, volume=new_volume)
        print(f"Volume decreased to {new_volume}%")
    else:
        print("No active playback or device found.")

# Changes the podcast ratings for input 'favourite'
def podcast_feedback_fav(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    change_podcast_rating(podcast_genre, 9)

# Changes the podcast ratings for input 'love'
def podcast_feedback_love(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    new_score = min(current_score + 2, 10)
    change_podcast_rating(podcast_genre, new_score)
    speak("Thanks for the feedback")

# Changes the podcast ratings for input 'like'
def podcast_feedback_like(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    new_score = min(current_score + 1, 10)
    change_podcast_rating(podcast_genre, new_score)
    speak("Thanks for the feedback")

# Changes the podcast ratings for input 'dislike'
def podcast_feedback_dis(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    new_score = max(current_score - 1, 1)
    change_podcast_rating(podcast_genre, new_score)
    speak("Thanks for the feedback")

# Changes the podcast ratings for input 'strongly dislike'
def podcast_feedback_stdis(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    new_score = max(current_score - 2, 1)
    change_podcast_rating(podcast_genre, new_score)
    speak("Thanks for the feedback")

# Changes the podcast rating for input 'hate'
def podcast_feedback_hate(text):
    podcast_genre, current_score = fetch_prev_podcast()
    if current_score is None:
        print("Topic not found.")
        return
    change_podcast_rating(podcast_genre, 2)
    speak("Thanks for the feedback")
