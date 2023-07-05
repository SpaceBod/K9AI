from PIL import Image
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
import pygame
from elevenlabs import generate, play, voices, save
from elevenlabs import set_api_key
import threading
import time

sound_effects = ["sound/ready.mp3", "sound/prompt.mp3", "sound/startup.mp3", "queen.mp3"]

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
    close_image_1 = Image.open('display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

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
    close_image_1 = Image.open('display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    image_1 = Image.open('display/1.png')  # Replace 'image_1_path.png' with the path to your image 1
    image_2 = Image.open('display/2.png')  # Replace 'image_2_path.png' with the path to your image 2
    image_3 = Image.open('display/3.png')  # Replace 'image_3_path.png' with the path to your image 3

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
    close_image_1 = Image.open('display/close.png')
    image_1 = Image.open('display/1.png')
    image_2 = Image.open('display/2.png')
    image_3 = Image.open('display/3.png')
    
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
    close_image_1 = Image.open('display/close.png')  # Replace 'close_image_1_path.png' with the path to your close image 1
    close_image_1 = close_image_1.resize(device.size).convert('1')
    device.display(close_image_1)
# Setting up the OLED display
serial = i2c(port=1, address=0x3C)  # Set the appropriate I2C port and address
device = sh1106(serial)

# Text to speech
def speak(text, auto_play=True):
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


def main():
    play_sound("Greetings.mp3", 1, True)
    play_sound("About.mp3", 1, True)
    play_sound("playMusic.mp3", 1, True)
    play_sound("queen.mp3", 0.4, False)

main()
