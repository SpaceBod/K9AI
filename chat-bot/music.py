import spotipy as sp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import random
import csv

class InvalidSearchError(Exception):
    pass

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

def get_artist_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='artist')
    if not results['artists']['items']:
        raise InvalidSearchError(f'No artist named "{original}"')
    artist_uri = results['artists']['items'][0]['uri']
    print(results['artists']['items'][0]['name'])
    return artist_uri

def get_album_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='album')
    if not results['albums']['items']:
        raise InvalidSearchError(f'No album named "{original}"')
    album_uri = results['albums']['items'][0]['uri']
    return album_uri

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

def get_playlist_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='playlist')
    if not results['playlists']['items']:
        raise InvalidSearchError(f'No playlist named "{original}"')
    playlist_uri = results['playlists']['items'][0]['uri']
    print(results['playlists']['items'][0]['name'])
    return playlist_uri

def get_podcast_uri(spotify: Spotify, name: str) -> str:
    original = name
    name = name.replace(' ', '+')

    results = spotify.search(q=name, limit=1, type='show')
    if not results['shows']['items']:
        raise InvalidSearchError(f'No podcast named "{original}"')
    podcast_uri = results['shows']['items'][0]['uri']
    print(results['shows']['items'][0]['name'])
    return podcast_uri

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


def is_track_paused(spotify: Spotify) -> bool:
    current_playback = spotify.current_user_playing_track()
    #print(current_playback['is_playing'])
    if current_playback and current_playback['is_playing']:
        return True
    return False


def play_liked_songs(spotify=None, device_id=None, liked_songs=None):
    track_uris = [track['track']['uri'] for track in liked_songs]
    spotify.start_playback(device_id=device_id, uris=track_uris)

def play_artist(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, context_uri=uri)

def play_track(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, uris=[uri])

def play_playlist(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, context_uri=uri)

def play_podcast(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, context_uri=uri)
    
def next_track(spotify=None, device_id=None):
    spotify.next_track(device_id=device_id)

def prev_track(spotify=None, device_id=None):
    spotify.previous_track(device_id=device_id)

def pause_track(spotify=None, device_id=None):
    spotify.pause_playback(device_id=device_id)

def resume_play(spotify=None, device_id=None):
    spotify.start_playback(device_id=device_id)

def set_volume(spotify=None, device_id=None, volume=None):
    spotify.volume(volume, device_id=device_id)

def get_current_volume(spotify=None, device_id=None):
    current_playback = spotify.current_playback()
    if current_playback and current_playback['device']:
        if current_playback['device']['id'] == device_id:
            volume_level = current_playback['device']['volume_percent']
            return volume_level
    return None

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

def init_podcast_ratings():
    # Read the topic scores from the CSV file
    topics = fetch_podcast_ratings()

    # Iterate over each topic and update its score
    for topic in topics:
        # Generate a random score between 4 and 8 (inclusive)
        new_score = random.randint(4, 8)
        change_podcast_rating(topic, new_score)

    print("Scores randomized successfully.")

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
    with open('genres.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for topic, score in topics.items():
            writer.writerow([topic, score])

    print("Score updated successfully.")

# fetch_podcast_ratings(topic)
# Reads and returns the score of a specific genre from the CSV file.

# init_podcast_ratings()
# Randomly initializes the scores between 4 and 8 (inclusive) for all genres in the CSV file.

# fav_podcast_genres()
# Finds the top two genre with the highest scores, and additional genre with the same score.

# categorize_topics()
# Categorizes the genre into three arrays based on their scores: top 30%, next 30%, and bottom 40%.

# change_podcast_rating(topic, new_score)
# Updates the score of a specific genre in the CSV file.
