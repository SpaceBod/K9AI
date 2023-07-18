from PIL import Image
from luma.core.interface.serial import i2c
from adafruit_servokit import ServoKit
from luma.oled.device import sh1106
import pygame
from elevenlabs import generate, play, voices, save
from elevenlabs import set_api_key
import threading
import time
import requests
from quadruped import Quadruped

sound_effects = ["K9AI/demo/speech/queen.mp3"]
PAN = 14
TILT = 15

# Head Motors
def set_head():
    kit = ServoKit(channels=16)
    kit.servo[TILT].angle = 45
    kit.servo[PAN].angle = 90
    
def raise_head():
    kit = ServoKit(channels=16)
    for x in range(45, 70):
        kit.servo[TILT].angle = x
        time.sleep(0.01)
    kit.servo[PAN].angle = 90

def lower_head():
    kit = ServoKit(channels=16)
    for x in range(70, 45,  -1):
        kit.servo[TILT].angle = x
        time.sleep(0.01)
    kit.servo[PAN].angle = 90

def turn_head():
    kit = ServoKit(channels=16)
    for x in range(90, 120,  1):
        kit.servo[PAN].angle = x
        time.sleep(0.01)
    for x in range(120, 60,  -1):
        kit.servo[PAN].angle = x
        time.sleep(0.01)
    for x in range(60, 90,  1):
        kit.servo[PAN].angle = x
        time.sleep(0.01)

def thread_turn():
    thread = threading.Thread(target=turn_head)
    thread.start()

def walking_music():
    play_sound("K9AI/demo/speech/walksong.mp3", 0.1, True)
    play_sound("K9AI/demo/speech/finish.mp3", 1, True)
    
def thread_walk():
    thread = threading.Thread(target=walking_music)
    thread.start()
    
# Function to play a sound file with optional blocking (waiting for sound to finish)
def play_sound(file_path, volume, blocking=True):
    volume = 1
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    # Play sound and wait for it to finish if blocking is True
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

# Displays an animation on an OLED display while playing a sound synchronously
def play_sound_blocking(sound):
    # Load images for animation
    close_image_1 = Image.open('K9AI/demo/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('K9AI/demo/display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('K9AI/demo/display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('K9AI/demo/display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

    # Resize images to match the OLED display resolution and convert to 1-bit grayscale
    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    # Display the close image on the OLED display
    device.display(close_image_1)
    sound.play()

    # Display animation while the sound is playing
    while pygame.mixer.get_busy():
        device.display(image_1)
        pygame.time.Clock().tick(20)
        device.display(image_2)
        pygame.time.Clock().tick(20)
        device.display(image_3)
        pygame.time.Clock().tick(20)
        device.display(image_2)
        pygame.time.Clock().tick(20)

    # Display the close image after the sound finishes
    device.display(close_image_1)
    pygame.mixer.quit()

# Displays an animation on an OLED display while playing a sound asynchronously
def play_sound_non_blocking(sound):
    close_image_1 = Image.open('K9AI/demo/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('K9AI/demo/display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('K9AI/demo/display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('K9AI/demo/display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    device.display(close_image_1)

    # Start a new thread to play the animation
    animation_thread = threading.Thread(target=play_animation)
    animation_thread.start()
    sound.play()

    # Start a new thread to wait for the sound to finish
    sound_thread = threading.Thread(target=wait_for_sound, args=(sound,))
    sound_thread.start()

# Displays an animation on an OLED display by alternating between different images
def play_animation():
    close_image_1 = Image.open('K9AI/demo/display/close.png')
    image_1 = Image.open('K9AI/demo/display/1.png')
    image_2 = Image.open('K9AI/demo/display/2.png')
    image_3 = Image.open('K9AI/demo/display/3.png')
    
    close_image_1 = close_image_1.resize(device.size).convert('1')
    image_1 = image_1.resize(device.size).convert('1')
    image_2 = image_2.resize(device.size).convert('1')
    image_3 = image_3.resize(device.size).convert('1')

    while pygame.mixer.get_busy():
        device.display(image_1)
        pygame.time.Clock().tick(20)
        device.display(image_2)
        pygame.time.Clock().tick(20)
        device.display(image_3)
        pygame.time.Clock().tick(20)
        device.display(image_2)
        pygame.time.Clock().tick(20)
        
    device.display(close_image_1)
    
def wait_for_sound(sound):
    while pygame.mixer.get_busy():
        pass
    # Display the close image after the sound finishes
    close_image_1 = Image.open('K9AI/demo/display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    close_image_1 = close_image_1.resize(device.size).convert('1')
    device.display(close_image_1)
    
# Setting up the OLED display
serial = i2c(port=1, address=0x3C)  # Set the appropriate I2C port and address
device = sh1106(serial)

# Text to speech
def speak(text, auto_play=True):
    print('K9: ' + text)
    set_api_key("652cfcc78a55462e2d05ea895c3625ae")
    available_voices = voices()
    audio = generate(
      text=text,
      voice=available_voices[9],
      model="eleven_monolingual_v1"
    )
    save(audio, "K9AI/demo/speech/tts.mp3")
    play_sound("K9AI/demo/speech/tts.mp3", 1, True)

# Retrieves weather forecase using API, defaults to London
def get_weather(location):
    weather_key = "bf63b77834f1e14ad335ba6c23eea570"
    weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={weather_key}")
    weather = weather_data.json()['weather'][0]['main']
    temp = round(weather_data.json()['main']['temp'])
    if weather.lower() == "clouds":
        weather = 'Cloudy'
    if weather.lower() == "rain":
        weather = 'raining'
    if weather.lower() == "snow":
        weather = 'snowing'
    speak(f"Ok, in {location}, the temperature is {temp} degrees and it's {weather}.")
    
def get_news():
    try:
        # Fetch news data from the API
        news_data = requests.get('https://newsdata.io/api/1/news?apikey=pub_2224719bbcc10e32c3eaae46f288b9876718a&language=en&country=gb&domain=bbc')

        if news_data.status_code == 200:
            news = news_data.json()

            if "results" in news and len(news["results"]) > 0:
                titles = []
                for i in range(min(2, len(news["results"]))):
                    title = news["results"][i].get("title")
                    if title:
                        titles.append(title)
                if len(titles) > 0:
                    speak(f"The first one... {titles[0]}. And secondly... {titles[1]}")
                else:
                    speak("No news titles available.")
            else:
                speak("No news data available.")
        else:
            speak("Error occurred while fetching news. Status code: {}".format(news_data.status_code))
    except requests.exceptions.RequestException as e:
        speak("An error occurred while making a request: {}".format(str(e)))

        
# Returns a 2-part joke
def get_random_joke():
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
    
def main():
    set_head()
    time.sleep(0.5)
    
    raise_head()
    thread_turn()
    play_sound("K9AI/demo/speech/Greetings.mp3", 1, True)
    play_sound("K9AI/demo/speech/About.mp3", 1, True)

    play_sound("K9AI/demo/speech/playMusic.mp3", 1, True)
    lower_head()
    play_sound("K9AI/demo/speech/queen.mp3", 0.7, True)

    raise_head()
    thread_turn()
    play_sound("K9AI/demo/speech/getWeather.mp3", 1, False)
    get_weather("London")
    lower_head()

    thread_turn()
    play_sound("K9AI/demo/speech/getNews.mp3", 1, False)
    raise_head()
    get_news()

    thread_turn()
    play_sound("K9AI/demo/speech/calendar.mp3", 1, True)

    lower_head()
    thread_turn()
    play_sound("K9AI/demo/speech/joke.mp3", 1, False)
    get_random_joke()
#
    # Movement
    play_sound("K9AI/demo/speech/walk.mp3", 1, True)
    thread_walk()
    
    k9  =  Quadruped()
    k9.move("forwards")
    k9.move("stop")
    k9.move("backwards")
    k9.move("stop")
    k9.move("right")
    k9.move("stop")
    k9.move("left")
    k9.move("stop")
    k9.move("sit")
    time.sleep(2)
main()

