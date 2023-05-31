import spotipy as sp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import random

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
    print(current_playback['is_playing'])
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