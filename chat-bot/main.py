from playsound import playsound as sound
from functions import *
from watson import WatsonAssistant
import json
import pvporcupine
import pyaudio
import struct
import cv2

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
    sound("assets/startup.mp3")
    recognized_names = scan_face()
    for name in recognized_names:
        #print(name)
        if name == "N" or name == "Unknown":
            speak("Hi, I don't think we have met. I'm K9. If you want me to greet you by name, say Hey K9, Add me!")
        else:
            speak(f"Hi {name}. I'm K9.")
    speak("What can I help you with?")

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
        frames_per_buffer=porcupine.frame_length
    )
    return porcupine, audio_stream

def main():
    recogniser, assistant, wake_word_settings = initialize_chatbot()
    porcupine, audio_stream = initialize_porcupine(wake_word_settings)

    try:
        while True:
            listen_for_wake_word(porcupine, audio_stream)
            sound("assets/ready.mp3")
            try:
                user_input = recognise_input(recogniser)
                print(f"[INPUT]\t{user_input}")
                assistant.watson_chat(user_input)
            except speech_recognition.UnknownValueError:
                recogniser = speech_recognition.Recognizer()
                speak("I didn't quite catch that...")
    finally:
        if porcupine is not None:
            porcupine.delete()

if __name__ == '__main__':
    main()


#if someone says "Add me"
# ask for a name 
# call function add_face with their name as paramter
