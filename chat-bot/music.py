import spotipy as sp
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

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

def get_liked_songs(spotify: Spotify):
    results = spotify.current_user_saved_tracks()
    liked_songs=results['items']
    while results['next']:
        results = spotify.next(results)
        liked_songs.extend(results['items'])
    return liked_songs

def play_artist(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, context_uri=uri)

def play_track(spotify=None, device_id=None, uri=None):
    spotify.start_playback(device_id=device_id, uris=[uri])

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