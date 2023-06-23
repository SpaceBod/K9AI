from functions import *
from music import *
from vision import scan_face
from watson import WatsonAssistant
import json
import pvporcupine
import pyaudio
import os
from multiprocessing import Manager
from movement.control_quadruped import main_quad
import subprocess
import time
import pulsectl
import threading

# Rest of your code...

def second_file_process(sit):
    main_quad(sit)

def initialize_chatbot():
    recognized_names = []
    # Read the settings from the file
    with open('settings.json') as f:
        settings = json.load(f)
    # Extract the variables
    spotify_settings = settings['spotify']
    watson_assistant_settings = settings['watson_assistant']
    wake_word_settings = settings['porcupine_wake_word']
    # Initialising chat bot
    recogniser = speech_recognition.Recognizer()
    print("got recogniser")
    calibrate_mic(recogniser)
    print("calibrated mic")
    initialise_tts()
    pygame.init()
    # Initialising Spotify
    spot, dev_ID = initialise_spotify(
        client_id=spotify_settings['client_id'],
        client_secret=spotify_settings['client_secret'],
        redirect_uri=spotify_settings['redirect_uri'],
        username=spotify_settings['username'],
        device_name=spotify_settings['device_name'],
        scope=spotify_settings['scope']
    )
    send_variables(spot, dev_ID)
    print("before playsound 1")
    play_sound("sound/startup.mp3", 0.4, blocking=False)
    print("recognized names")
    recognized_names = scan_face()
    for name in recognized_names:
        if name == "N" or name == "Unknown":
            play_sound("sound/greet.mp3", 0.5, blocking=True)
        else:
            speak(f"Hi {name}. I'm K9.")
    play_sound("sound/help.mp3", 0.5, blocking=False)
    
    # Create an instance of the WatsonAssistant class
    assistant = WatsonAssistant(
        api_key=watson_assistant_settings['api_key'],
        id=watson_assistant_settings['id'],
        service_url=watson_assistant_settings['service_url'],
        intents_file=watson_assistant_settings['intents_file']
    )
    return recogniser, assistant, wake_word_settings

def initialize_porcupine(wake_word_settings):
    access_key = wake_word_settings['api_key']
    custom_keyword_path = wake_word_settings['model_path']
    sensitivity = 0.7

    porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[custom_keyword_path], sensitivities=[sensitivity])
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        output=False
    )
    return porcupine, audio_stream

def main(sit):
    recogniser, assistant, wake_word_settings = initialize_chatbot()
    porcupine, audio_stream = initialize_porcupine(wake_word_settings)
    second_thread = threading.Thread(target=second_file_process, args=(sit,))
    second_thread.start()
    try:
        while True:
            listen_for_wake_word(porcupine, audio_stream)
            if is_music_paused():
                pause_music('Pause')
                time.sleep(3)
            play_sound("sound/ready.mp3", 0.4, blocking=False)
            try:
                user_input = recognise_input(recogniser)
                print(f"[INPUT]\t{user_input}")
                assistant.watson_chat(user_input, sit)
            except speech_recognition.UnknownValueError:
                recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 0.4, blocking=True)
            # Check process using the speaker device
    finally:
        second_thread.join()
        if porcupine is not None:
            porcupine.delete()

if __name__ == '__main__':
    manager = Manager()
    sit = manager.Value('b', False)
    main(sit)
