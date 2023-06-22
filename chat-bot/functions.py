import requests, re
import pyttsx3 as tts
import speech_recognition
import datetime
import struct
import os
from elevenlabslib.helpers import *
from elevenlabslib import *
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from beautiful_date import *
from datetime import datetime, timedelta

# Suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

K9_TTS = None
weather_key = 'bf63b77834f1e14ad335ba6c23eea570'

local_recogniser = None

def get_recogniser():
    return local_recogniser

def play_sound(file_path, volume, blocking=True):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    if blocking:
        sound.play()
        while pygame.mixer.get_busy():  # Wait for the sound to finish playing
            pygame.time.Clock().tick(10)  # Control the loop speed
    else:
        sound.play()

# Initiliasing the Text to Speech engine
def initialise_tts():
    global K9_TTS
    K9_TTS = tts.init()
    K9_TTS.setProperty('rate', 200)

# Calibrates mic for 3 seconds (adjusts to ambient noise)
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
        play_sound("sound/prompt.mp3", 0.8, blocking=False)
        message = recogniser.recognize_google(audio)
        message = message.lower()
        return message

def listen_for_wake_word(porcupine, audio_stream):
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow = False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Custom Keyword Detected")
            break

# Text to speech
def espeak(text):
    print('K9: ' + text)
    K9_TTS.say(text)
    K9_TTS.runAndWait()

def speak(text):
    print('K9: ' + text)
    api_key = "ecf8b902a86fab1c3ec866b9a8ed6fc3"
    user = ElevenLabsUser(api_key)
    premadeVoice = user.get_voices_by_name("Jarvis")[0]
    premadeVoice.generate_play_audio(text , stability=0.4, similarity_boost=0.4, playInBackground=False, latencyOptimizationLevel = 0)

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

def get_random_joke(text):
    # Yup we have to filter out a lot of bad jokes...
    url = "https://v2.jokeapi.dev/joke/Any?type=twopart&blacklistFlags=nsfw,religious,political,racist,sexist"
    response = requests.get(url)
    data = response.json()

    if data["type"] == "twopart":
        setup = data["setup"]
        punchline = data["delivery"]
        joke = f"{setup}\n{punchline}"
    else:
        joke = data["joke"]
    speak(joke)

def create_calendar_event_easy(title, day, month, year, time):
    calendar = GoogleCalendar(credentials_path='client_secret.json')
    if time == 'all day':
        start = datetime(year, month, day).strftime("%Y-%m-%d")
        end = datetime(year, month, day).strftime("%Y-%m-%d")
    else:
        start = datetime.strptime(f"{day}/{month}/{year} {time}", "%d/%m/%Y %H:%M")
        end_time = datetime.strptime(time, "%H:%M") + timedelta(hours=1)
        end_time = end_time.strftime("%H:%M")
        end = datetime.strptime(f"{day}/{month}/{year} {end_time}", "%d/%m/%Y %H:%M")
    
    event = Event(title,
                start=start,
                end=end,
                description = title,
                minutes_before_email_reminder=15)
    calendar.add_event(event)


    print("Event Created :", title)
    print("Date + Time:", start)
    print("\n")

