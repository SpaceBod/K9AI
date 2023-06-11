from functions import *
from music import *
from vision import scan_face
from watson import WatsonAssistant
import json
import pvporcupine
import pyaudio
import os

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
    calibrate_mic(recogniser)
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
    play_sound("sound/startup.mp3", 0.5, blocking=False)
    recognized_names = scan_face()
    for name in recognized_names:
        #print(name)
        if name == "N" or name == "Unknown":
            play_sound("sound/greet.mp3", 0.5, blocking=True)
            #speak("Hi, I don't think we have met. I'm K9. If you want me to greet you by name, say Hey K9, Add me!")
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
        frames_per_buffer=1024,
        output=False
    )
    return porcupine, audio_stream

def main():
    recogniser, assistant, wake_word_settings = initialize_chatbot()
    porcupine, audio_stream = initialize_porcupine(wake_word_settings)

    try:
        while True:
            listen_for_wake_word(porcupine, audio_stream)
            if (is_music_paused() == True):
                pause_music('Pause')
            play_sound("sound/ready.mp3", 0.5, blocking=False)
            try:
                user_input = recognise_input(recogniser)
                print(f"[INPUT]\t{user_input}")
                assistant.watson_chat(user_input)
            except speech_recognition.UnknownValueError:
                recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 0.5, blocking=True)
    finally:
        if porcupine is not None:
            porcupine.delete()

if __name__ == '__main__':
    main()
