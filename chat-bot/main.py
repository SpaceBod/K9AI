from functions import *
from music import *
from vision import scan_face
from watson import WatsonAssistant
import json
import pvporcupine
import pyaudio
from multiprocessing import Manager
from movement.control_quadruped import main_quad
from movement.quadruped import raise_head, lower_head
import time
import threading

# Separate process for movement
def second_file_process(sit):
    main_quad(sit)

# Initialise the chatbot components
def Initialise_chatbot():
    recognized_names = []

    # Read the API settings from the file
    with open('settings.json') as f:
        settings = json.load(f)
    spotify_settings = settings['spotify']
    watson_assistant_settings = settings['watson_assistant']
    wake_word_settings = settings['porcupine_wake_word']

    # Initialise speech recognition and audio output
    recogniser = speech_recognition.Recognizer()
    calibrate_mic(recogniser)
    print("Mic Calibrated")
    initialise_tts()
    pygame.init()

    # Initialise Spotify
    spot, dev_ID = initialise_spotify(
        client_id=spotify_settings['client_id'],
        client_secret=spotify_settings['client_secret'],
        redirect_uri=spotify_settings['redirect_uri'],
        username=spotify_settings['username'],
        device_name=spotify_settings['device_name'],
        scope=spotify_settings['scope']
    )
    send_variables(spot, dev_ID)
    play_sound("sound/startup.mp3", 1, blocking=False)

    # Scan faces and greet recognized individuals
    recognized_names = scan_face()
    for name in recognized_names:
        if name == "N" or name == "Unknown":
            play_sound("sound/greet.mp3", 1, blocking=True)
        else:
            speak(f"Hi {name}. I'm K9.")
    play_sound("sound/help.mp3", 1, blocking=False)

    # Create an instance of the WatsonAssistant class
    assistant = WatsonAssistant(
        api_key=watson_assistant_settings['api_key'],
        id=watson_assistant_settings['id'],
        service_url=watson_assistant_settings['service_url'],
        intents_file=watson_assistant_settings['intents_file']
    )
    return recogniser, assistant, wake_word_settings

# Initialise Porcupine wake word engine
def Initialise_porcupine(wake_word_settings):
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

# Main function
def main(shared_list):
    recogniser, assistant, wake_word_settings = Initialise_chatbot()
    porcupine, audio_stream = Initialise_porcupine(wake_word_settings)
    second_thread = threading.Thread(target=second_file_process, args=(shared_list,))
    second_thread.start()
    try:
        while True:
            # Wait for wake word "Hey K9"
            listen_for_wake_word(porcupine, audio_stream)
            raise_head()
            # Pauses Spotify to listen to request clearly
            if is_music_paused():
                pause_music('Pause')
                time.sleep(3)
            play_sound("sound/ready.mp3", 1, blocking=False)
            try:
                # Listens to the user and transfroms speech to text
                user_input = recognise_input(recogniser)
                print(f"[INPUT]\t{user_input}")
                # Passes the text to Watson
                assistant.watson_chat(user_input, shared_list)
            except speech_recognition.UnknownValueError:
                recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 1, blocking=True)
            lower_head()
    finally:
        second_thread.join()
        if porcupine is not None:
            porcupine.delete()

if __name__ == '__main__':
    # Create variables to be shared across processes
    manager = Manager()
    shared_list = manager.list([False, False])
    main(shared_list)
