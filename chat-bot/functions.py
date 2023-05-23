import requests, re
import pyttsx3 as tts
import speech_recognition
from playsound import playsound as sound
import datetime
from music import *
import struct
import face_recognition
import cv2
import os
import glob
import numpy as np
import pickle

K9_TTS = None
weather_key = 'bf63b77834f1e14ad335ba6c23eea570'

local_recogniser = None
global_spotify = None
global_device_id = None


# Initiliasing the Text to Speech engine
def initialise_tts():
    global K9_TTS
    K9_TTS = tts.init()
    K9_TTS.setProperty('rate', 200)

# Calibrates mic for 2 seconds (adjusts to ambient noise)
def calibrate_mic(recogniser):
     with speech_recognition.Microphone() as source:   
        print("Please wait. Calibrating microphone...")   
        recogniser.adjust_for_ambient_noise(source, duration=3)

# Recognises user input and converts to text
def recognise_input(recogniser):
    global local_recogniser
    local_recogniser = recogniser
    with speech_recognition.Microphone() as mic:
        audio = recogniser.listen(mic)
        sound("assets/prompt.mp3")
        message = recogniser.recognize_google(audio)
        message = message.lower()
        return message

def listen_for_wake_word(porcupine, audio_stream):
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Custom Keyword Detected")
            break

# Text to speech
def speak(text):
    print('K9: ' + text)
    K9_TTS.say(text)
    K9_TTS.runAndWait()

def send_variables(spotify, device_id):
    global global_spotify
    global global_device_id

    global_spotify = spotify
    global_device_id = device_id

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


def extract_song_and_artist(text):
    # Extract the song name and artist from the user input
    match = re.search(r'(.+?)(?:\sby\s(.+))?$', text)
    song_name = match.group(1).strip() if match.group(1) is not None else ""
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name.title(), artist.title()

def extract_playlist_info(text):
    # Try to match the pattern 'playlist' followed by the playlist name
    match = re.search(r'playlist\s(.+)$', text, re.IGNORECASE)
    if match:
        playlist_name = match.group(1).strip()
    else:
        playlist_name = ""
    return playlist_name


# Local functions called by Watson (must take user_input even if not used)
def request_song(text):
    global local_recogniser
    speak("Sure, what song do you want to listen to?")
    done = False
    while not done:
        try:
            song = recognise_input(local_recogniser)
            song_name, artist = extract_song_and_artist(song)
            print("song", song_name)
            print("artist", artist)
            if artist == "":
                uri = get_track_uri(spotify=global_spotify, name=song_name)
                play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
                speak(f"Playing {song_name}.")
            # If song title + artist provided
            else:
                uri = get_track_uri(spotify=global_spotify, name=song_name, artist=artist)
                play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
                speak(f"Playing {song_name} by {artist}.")
            done = True
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            speak("Please repeat...")

def request_specific_song(text):
    song_name, artist = extract_song_info(text)
    if (artist == "" and song_name == ""):
        speak(f"Search unsuccessful, please try again.")
        return
    # If only song title provided
    if artist == "":
        uri = get_track_uri(spotify=global_spotify, name=song_name)
        play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
        speak(f"Playing {song_name}.")
    # If song title + artist provided
    else:
        uri = get_track_uri(spotify=global_spotify, name=song_name, artist=artist)
        play_track(spotify=global_spotify, device_id=global_device_id, uri=uri)
        speak(f"Playing {song_name} by {artist}.")

def request_playlist(text):
    global local_recogniser
    speak("Sure, what playlist do you want to listen to?")
    done = False
    while not done:
        try:
            playlist_name = recognise_input(local_recogniser).title()
            print("Playlist: ", playlist_name)
            uri = get_playlist_uri(spotify=global_spotify, name=playlist_name)
            play_playlist(spotify=global_spotify, device_id=global_device_id, uri=uri)
            speak(f"Playing {playlist_name}.")
            done = True
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            speak("Please repeat...")

def request_specific_playlist(text):
    playlist_name = extract_playlist_info(text).title()
    if playlist_name == "":
        speak(f"Search unsuccessful, please try again.")
        return
    else:
        uri = get_playlist_uri(spotify=global_spotify, name=playlist_name)
        play_playlist(spotify=global_spotify, device_id=global_device_id, uri=uri)
        speak(f"Playing {playlist_name}.")

def pause_music(text):
    pause_track(spotify=global_spotify, device_id=global_device_id)

def play_music(text):
    resume_play(spotify=global_spotify, device_id=global_device_id)

def play_liked(text):
    liked_songs = get_liked_songs(spotify=global_spotify)
    play_liked_songs(spotify=global_spotify, device_id=global_device_id, liked_songs=liked_songs)

def play_next(text):
    next_track(spotify=global_spotify, device_id=global_device_id)

def play_previous(text):
    prev_track(spotify=global_spotify, device_id=global_device_id)

def extract_volume_percentage(text):
    # Try to find the pattern 'to' followed by a number, with or without '%'
    match = re.search(r'to\s+(\d+)%?', text, re.IGNORECASE)
    if match:
        volume_percentage = int(match.group(1))
        return volume_percentage
    else:
        return None
    
def set_vol(text):
    set_vol = extract_volume_percentage(text)
    set_volume(spotify=global_spotify, device_id=global_device_id, volume=set_vol)

def increase_vol(text):
    current_volume = get_current_volume(spotify=global_spotify, device_id=global_device_id)
    if current_volume is not None:
        new_volume = min(current_volume + 10, 100)
        set_volume(spotify=global_spotify, device_id=global_device_id, volume=new_volume)
        print(f"Volume increased to {new_volume}%")
    else:
        print("No active playback or device found.")

def decrease_vol(text):
    current_volume = get_current_volume(spotify=global_spotify, device_id=global_device_id)
    if current_volume is not None:
        new_volume = max(current_volume - 10, 0)
        set_volume(spotify=global_spotify, device_id=global_device_id, volume=new_volume)
        print(f"Volume decreased to {new_volume}%")
    else:
        print("No active playback or device found.")

def get_weather(user_input):
    pattern = r"(?<=\bin\s).*"
    matches = re.search(pattern, user_input)    
    if matches:
        location = matches.group(0).title()
    else:
        location = "London"
    weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={weather_key}")
    weather = weather_data.json()['weather'][0]['main']
    temp = round(weather_data.json()['main']['temp'])
    speak(f"In {location}, the temperature is {temp} degrees, it's {weather}.")

def get_day(user_input):
    day = datetime.datetime.now().strftime('%A')
    speak(f"Today is {day}.")


class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path, save_file=None):
        if save_file and os.path.exists(save_file):
            # Load pre-encoded face encodings from file
            with open(save_file, 'rb') as f:
                data = pickle.load(f)
            self.known_face_encodings = data['encodings']
            self.known_face_names = data['names']
        else:
            # Encode faces and save the encodings
            images_path = os.path.abspath(images_path)
            for filename in os.listdir(images_path):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    image_path = os.path.join(images_path, filename)
                    img = cv2.imread(image_path)
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encoding = face_recognition.face_encodings(rgb_img)[0]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(os.path.splitext(filename)[0])

            if save_file:
                # Save the face encodings to file
                data = {'encodings': self.known_face_encodings, 'names': self.known_face_names}
                with open(save_file, 'wb') as f:
                    pickle.dump(data, f)

    def detect_known_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names

def scan_face():
    # Encode faces from a folder and save the encodings
    save_file = 'face_encodings.pkl'
    sfr = SimpleFacerec()
    sfr.load_encoding_images("faces/", save_file=save_file)

    # Load Camera
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        recognized_names = []  # Initialize the list inside the loop

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        if len(face_locations) == 0:  # No face detected
            error_message = "N"
            return error_message
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            recognized_names.append(name)  # Add recognized name to the list

            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        #cv2.imshow("Frame", frame)
        # key = cv2.waitKey(1)
        # if key == 27:
        #     break

        # Check if there are no more frames available
        if len(recognized_names) > 0:
            break

    cap.release()
    cv2.destroyAllWindows()
    return(recognized_names)


def add_face(person):
    cap = cv2.VideoCapture(0)
    _, image = cap.read()
    image_path = f"faces/{person}.jpg"
    cv2.imwrite(image_path, image)
    print(f"Face captured and saved as {image_path}")
