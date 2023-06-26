import requests, re
import pyttsx3 as tts
import speech_recognition
import datetime
import struct
import os
from elevenlabs import generate, play, voices, save
from elevenlabs import set_api_key
from PIL import Image
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
import threading
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from beautiful_date import *
from datetime import datetime, timedelta

serial = i2c(port=1, address=0x3C)  # Set the appropriate I2C port and address
device = sh1106(serial)

# Suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

K9_TTS = None
weather_key = 'bf63b77834f1e14ad335ba6c23eea570'

local_recogniser = None
sound_effects = ["sound/ready.mp3", "sound/prompt.mp3", "sound/startup.mp3"]


def get_recogniser():
    return local_recogniser

def play_sound(file_path, volume, blocking=True):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    print(blocking)
    if file_path not in sound_effects:
        if blocking:
            play_sound_blocking(sound)
        else:
            sound_thread = threading.Thread(target=play_sound_non_blocking, args=(sound,))
            sound_thread.start()
    else:
        if blocking:
            sound.play()
            while pygame.mixer.get_busy():  # Wait for the sound to finish playing
                pygame.time.Clock().tick(10)  # Control the loop speed
            pygame.mixer.quit()
        else:
            sound.play()

def play_sound_blocking(sound):
    close_image_1 = Image.open('assets/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('assets/display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('assets/display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('assets/display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    device.display(close_image_1)
    sound.play()

    while pygame.mixer.get_busy():
        device.display(image_1)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_2)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_3)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_2)
        pygame.time.Clock().tick(20)  # Control the loop speed

    # Display the close image after the sound finishes
    device.display(close_image_1)
    pygame.mixer.quit()

def play_sound_non_blocking(sound):
    close_image_1 = Image.open('assets/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('assets/display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('assets/display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('assets/display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    device.display(close_image_1)

    animation_thread = threading.Thread(target=play_animation)
    animation_thread.start()

    sound.play()
    sound_thread = threading.Thread(target=wait_for_sound, args=(sound,))
    sound_thread.start()

def play_animation():
    close_image_1 = Image.open('assets/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('assets/display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('assets/display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('assets/display/3.png')  # Replace 'image_3_path.png' with the path to your image 3
    
    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    while pygame.mixer.get_busy():
        device.display(image_1)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_2)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_3)
        pygame.time.Clock().tick(20)  # Control the loop speed
        device.display(image_2)
        pygame.time.Clock().tick(20)  # Control the loop speed
        
    device.display(close_image_1)
    
def wait_for_sound(sound):
    while pygame.mixer.get_busy():
        pass

    # Display the close image after the sound finishes
    close_image_1 = Image.open('assets/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    close_image_1 = close_image_1.resize(device.size).convert('1')
    device.display(close_image_1)
    
# Initiliasing the Text to Speech engine
def initialise_tts():
    global K9_TTS
    K9_TTS = tts.init()
    K9_TTS.setProperty('rate', 200)

# Calibrates mic for 3 seconds (adjusts to ambient noise)
def calibrate_mic(recogniser):
     print("in calibrate mic")
     with speech_recognition.Microphone() as source:   
        print("Please wait. Calibrating microphone...")   
        recogniser.adjust_for_ambient_noise(source, duration=3)

# Recognises user input and converts to text
def recognise_input(recogniser):
    global local_recogniser
    local_recogniser = recogniser
    # Get a list of all available audio input devices
    microphone_names = speech_recognition.Microphone.list_microphone_names()
    if len(microphone_names) == 0:
        raise Exception("No audio input devices found.")
    # Select the first available audio input device
    device_index = 1
    with speech_recognition.Microphone(device_index=device_index) as mic:
        audio = recogniser.listen(mic, timeout=5)
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
    set_api_key("ecf8b902a86fab1c3ec866b9a8ed6fc3")
    available_voices = voices()
    audio = generate(
      text=text,
      voice=available_voices[9],
      model="eleven_monolingual_v1"
    )
    save(audio, "sound/tts.mp3")
    play_sound("sound/tts.mp3", 1, True)

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
    play_sound("sound/weatherFiller.mp3", 1, blocking=False)
    speak(f"In {location}, the temperature is {temp} degrees, it's {weather}.")

def get_day(user_input):
    day = datetime.datetime.now().strftime('%A')
    play_sound("sound/dayFiller.mp3", 1, blocking=False)
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

def command_sitting(user_input):
    print("not implemented")

def open_mouth():
    # Initialize OLED display
    serial = i2c(port=1, address=0x3C)  # Set the appropriate I2C port and address
    device = sh1106(serial)
    # Load the image
    image = Image.open('assets/display/open.png')
    # Resize the image to match the OLED display resolution
    image = image.resize(device.size)
    # Convert the image to grayscale
    image = image.convert('1')
    # Display the image on the OLED display
    device.display(image)

def close_mouth():
    # Initialize OLED display
    serial = i2c(port=1, address=0x3C)  # Set the appropriate I2C port and address
    device = sh1106(serial)
    # Load the image
    image = Image.open('assets/display/close.png')
    # Resize the image to match the OLED display resolution
    image = image.resize(device.size)
    # Convert the image to grayscale
    image = image.convert('1')
    # Display the image on the OLED display
    device.display(image)

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

def update_thingspeak(status):
    # ThingSpeak API endpoint URL
    url = "https://api.thingspeak.com/update.json"

    # Your ThingSpeak channel ID and write API key
    channel_id = "2201244"
    write_api_key = "M0ZNFW8ZQDW7EIZC"

    print(int(status))
    # Create the payload data
    data = {'api_key': write_api_key, 'field1': str(int(status))}

    try:
        # Send an HTTP POST request to update the field value
        response = requests.post(url, data=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Status updated successfully!")
        else:
            print("Error occurred while updating status:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
    
def light_on(text):
    update_thingspeak(1)
    
def light_off(text):
    update_thingspeak(0)
