from neuralintents import GenericAssistant
from requests import post
from datetime import datetime
from pytz import timezone
import speech_recognition, pyttsx3 as tts, sys, re, os, glob, random, json
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
from music import *

cache_files = glob.glob('.cache*')
for file in cache_files:
    os.remove(file)

# Load the intents file
with open('intents.json') as file:
    intents = json.load(file)['intents']

client_id = "3112161c7e454bce81ee3277ac772ceb"
client_secret = "a4e72d15ac164dba8c3f1559aa1ef7c1"
redirect_uri = "http://localhost:8888/callback"
username = "lucabod8"
device_name = "Macbook"
scope = "user-read-private user-read-playback-state user-modify-playback-state"

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, username=username)
spotify = sp.Spotify(auth_manager=auth_manager)
# Selecting device to play from
devices = spotify.devices()
deviceID = None
for d in devices['devices']:
    d['name'] = d['name'].replace('’', '\'')
    if d['name'] == device_name:
        deviceID = d['id']
        break
print(f"Spotify Successfully Connected - {deviceID}")


recogniser = speech_recognition.Recognizer()
speaker = tts.init()
speaker.setProperty('rate', 200)

speaker.say("Hi, I'm K9. What can I help you with?")
speaker.runAndWait()
print("READY")

def recognise_input(recognizer):
    with speech_recognition.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.2)
        audio = recognizer.listen(mic)
        message = recognizer.recognize_google(audio)
        message = message.lower()
        return message

def extract_specific_song(text):
    # Extract the song name and artist from the user input
    match = re.search(r'play(?: me)?\s(.+?)(?:\sby\s(.+))?$', text, re.IGNORECASE)
    song_name = match.group(1).strip() if match.group(1) is not None else None
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name, artist

def extract_song_and_artist(text):
    # Extract the song name and artist from the user input
    match = re.search(r'(.+?)(?:\sby\s(.+))?$', text)
    song_name = match.group(1).strip() if match.group(1) is not None else None
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name, artist

def play_song():
    global recogniser
    print("[K9]\tSong Request")
    speaker.say("Sure, what song do you want to listen to?")
    speaker.runAndWait()

    done = False
    while not done:
        try:
            song = recognise_input(recogniser)
            song_name, artist = extract_song_and_artist(song)
            print("song", song_name)
            print("artist", artist)
            if artist == "":
                print(f"[K9] Playing {song_name}.")
                uri = get_track_uri(spotify=spotify, name=song_name)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
                speaker.say(f"Playing {song_name}.")
                speaker.runAndWait()
            # If song title + artist provided
            else:
                print(f"[K9] Playing {song_name} by {artist}.")
                uri = get_track_uri(spotify=spotify, name=song_name, artist=artist)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
                speaker.say(f"Playing {song_name} by {artist}.")
                speaker.runAndWait()
            done = True
        except speech_recognition.UnknownValueError:
            recogniser = speech_recognition.Recognizer()
            speaker.say("Please repeat...")
            speaker.runAndWait()

def play_specific_song():
    global message
    song_name, artist = extract_specific_song(message)
    # If only song title provided
    if artist == "":
        print(f"[K9] Playing {song_name}.")
        uri = get_track_uri(spotify=spotify, name=song_name)
        play_track(spotify=spotify, device_id=deviceID, uri=uri)
        speaker.say(f"Playing {song_name}.")
        speaker.runAndWait()
    # If song title + artist provided
    else:
        print(f"[K9] Playing {song_name} by {artist}.")
        uri = get_track_uri(spotify=spotify, name=song_name, artist=artist)
        play_track(spotify=spotify, device_id=deviceID, uri=uri)
        speaker.say(f"Playing {song_name} by {artist}.")
        speaker.runAndWait()

def greeting():
    print("[K9]\tGreeting")
    for intent in intents:
        if intent['tag'] == "greetings":
            speaker.say(random.choice(intent['responses']))
    speaker.runAndWait()

def get_time():
    # Set the time zone to London
    london_tz = timezone('Europe/London')
    london_time = datetime.now(london_tz)
    # Format the time as a string
    time_str = london_time.strftime('%I:%M')
    # Replace leading zeros with the word "oh"
    time_str = time_str.replace('0', '', 1)
    time_str = time_str.replace(':', ' ')
    if london_time.hour >= 12:
        time_str += ' Pee Em'
    else:
        time_str += ' Ay Em'
    
    print(f"[K9]\tTIME-{time_str}")
    for intent in intents:
        if intent['tag'] == "time":
            speaker.say(random.choice(intent['responses']))

    speaker.runAndWait()
    speaker.setProperty('rate', 150)
    speaker.say(time_str)
    speaker.runAndWait()
    speaker.setProperty('rate', 200)

def quit():
    print("[K9]\tExit")
    speaker.say("Bye")
    speaker.runAndWait()
    sys.exit(0)

mappings = {
    "greetings": greeting,
    "play_song": play_song,
    "play_specific_song": play_specific_song,
    "time": get_time,
    "exit": quit
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)
#assistant.train_model()
#assistant.save_model("./models/model")
assistant.load_model("./models/model")

while True:
    try:
        message = recognise_input(recogniser)
        print(f"[INPUT]\t{message}")
        assistant.request(message)
    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        print("unknown")
