from neuralintents import GenericAssistant
from requests import post
from playsound import playsound
import datetime
import speech_recognition, pyttsx3 as tts, sys, re, os, random, json
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
from music import *

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
k9 = tts.init()
k9.setProperty('rate', 200)
voices = k9.getProperty('voices')
print("Available voices:")
for voice in voices:
    print(" - %s" % voice.name)
desired_voice = voices[2]
k9.setProperty('voice', desired_voice.id)

def speak(text):
    print('K9: ' + text)
    k9.say(text)
    k9.runAndWait()

def calibrate_mic(recogniser):
     with speech_recognition.Microphone() as source:   
        print("Please wait. Calibrating microphone...")   
        recogniser.adjust_for_ambient_noise(source, duration=3)

def recognise_input(recogniser):
    with speech_recognition.Microphone() as mic:
        audio = recogniser.listen(mic)
        playsound("assets/prompt.mp3", False)
        message = recogniser.recognize_google(audio)
        message = message.lower()
        return message

def extract_specific_song(text):
    # Extract the song name and artist from the user input
    match = re.search(r'play(?: me)?\s(.+?)(?:\sby\s(.+))?$', text, re.IGNORECASE)
    song_name = match.group(1).strip() if match.group(1) is not None else ""
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name, artist

def extract_song_and_artist(text):
    # Extract the song name and artist from the user input
    match = re.search(r'(.+?)(?:\sby\s(.+))?$', text)
    song_name = match.group(1).strip() if match.group(1) is not None else ""
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name, artist

def play_song():
    global recogniser
    speak("Sure, what song do you want to listen to?")

    done = False
    while not done:
        try:
            song = recognise_input(recogniser)
            song_name, artist = extract_song_and_artist(song)
            print("song", song_name)
            print("artist", artist)
            if artist == "":
                uri = get_track_uri(spotify=spotify, name=song_name)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
                speak(f"Playing {song_name}.")
            # If song title + artist provided
            else:
                uri = get_track_uri(spotify=spotify, name=song_name, artist=artist)
                play_track(spotify=spotify, device_id=deviceID, uri=uri)
                speak(f"Playing {song_name} by {artist}.")
            done = True
        except speech_recognition.UnknownValueError:
            recogniser = speech_recognition.Recognizer()
            speak("Please repeat...")

def play_specific_song():
    global message
    song_name, artist = extract_specific_song(message)
    # If only song title provided
    if artist == "":
        uri = get_track_uri(spotify=spotify, name=song_name)
        play_track(spotify=spotify, device_id=deviceID, uri=uri)
        speak(f"Playing {song_name}.")
    # If song title + artist provided
    else:
        uri = get_track_uri(spotify=spotify, name=song_name, artist=artist)
        play_track(spotify=spotify, device_id=deviceID, uri=uri)
        speak(f"Playing {song_name} by {artist}.")

def greeting():
    hour = datetime.datetime.now().hour
    if (hour >= 3 and hour < 12):
        speak("Good morning!")
    if (hour >= 12 and hour < 18):
        speak("Good afternoon!")
    if (hour >= 18 and hour < 21):
        speak("Good evening!")
    else:
        speak("Hello!")
    for intent in intents:
        if intent['tag'] == "greetings":
            speak(random.choice(intent['responses']))

def get_time():
    for intent in intents:
        if intent['tag'] == "time":
            clock = datetime.datetime.now().strftime("%I:%M %p")
            speak(random.choice(intent['responses']) + " " + clock)

def get_date():
    for intent in intents:
        if intent['tag'] == "date":
            today = datetime.datetime.now().strftime("%d %B %Y")
            speak(random.choice(intent['responses']) + " " + today)

def get_day():
    for intent in intents:
        if intent['tag'] == "day":
            day = datetime.datetime.now().strftime('%A')
            speak(random.choice(intent['responses']) + " " + day)

def quit():
    print("[K9]\tExit")
    speak("Bye")
    sys.exit(0)

mappings = {
    "greetings": greeting,
    "play_song": play_song,
    "play_specific_song": play_specific_song,
    "time": get_time,
    "date": get_date,
    "day": get_day,
    "exit": quit
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)
#assistant.train_model()
#assistant.save_model("./models/model")
assistant.load_model("./models/model")

# os.system("cls")
calibrate_mic(recogniser)
playsound("assets/startup.mp3")
speak("Hi, I'm K9. What can I help you with?")
while True:
    try:
        message = recognise_input(recogniser)
        print(f"[INPUT]\t{message}")
        assistant.request(message)
        assistant.request(message)
    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        speak("I didn't quite catch that...")
