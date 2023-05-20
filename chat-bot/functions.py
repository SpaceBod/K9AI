import requests, re
import pyttsx3 as tts
import speech_recognition
from playsound import playsound as sound
import datetime

K9_TTS = None
weather_key = 'bf63b77834f1e14ad335ba6c23eea570'

# Initiliasing the Text to Speech engine
def initialise_tts():
    global K9_TTS
    K9_TTS = tts.init()
    K9_TTS.setProperty('rate', 200)

# Calibrates mic for 2 seconds (adjusts to ambient noise)
def calibrate_mic(recogniser):
     with speech_recognition.Microphone() as source:   
        print("Please wait. Calibrating microphone...")   
        recogniser.adjust_for_ambient_noise(source, duration=2)

# Recognises user input and converts to text
def recognise_input(recogniser):
    with speech_recognition.Microphone() as mic:
        audio = recogniser.listen(mic)
        sound("assets/prompt.mp3", False)
        message = recogniser.recognize_google(audio)
        message = message.lower()
        return message

# Text to speech
def speak(text):
    print('K9: ' + text)
    K9_TTS.say(text)
    K9_TTS.runAndWait()

# Local functions called by Watson (must take user_input even if not used)
def get_weather(user_input):
    pattern = r"(?<=\bin\s).*"
    matches = re.search(pattern, user_input)    
    if matches:
        location = matches.group(0)
    else:
        location = "London"
    weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={weather_key}")
    weather = weather_data.json()['weather'][0]['main']
    temp = round(weather_data.json()['main']['temp'])
    speak(f"In {location}, the temperature is {temp} degrees, it's {weather}.")

def get_day(user_input):
    day = datetime.datetime.now().strftime('%A')
    speak(f"Today is {day}.")