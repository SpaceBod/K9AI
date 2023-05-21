from playsound import playsound as sound
from functions import *
from watson import WatsonAssistant
import json

# Read the settings from the file
with open('settings.json') as f:
    settings = json.load(f)

# Extract the variables
spotify_settings = settings['spotify']
watson_assistant_settings = settings['watson_assistant']

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
speak("Hi, I'm K9. What can I help you with?")

# Create an instance of the WatsonAssistant class
assistant = WatsonAssistant(
    api_key=watson_assistant_settings['api_key'],
    id=watson_assistant_settings['id'],
    service_url=watson_assistant_settings['service_url'],
    intents_file=watson_assistant_settings['intents_file']
)

# Constantly listen for commands to send to Watson
while True:
    try:
        user_input = recognise_input(recogniser)
        print(f"[INPUT]\t{user_input}")
        assistant.watson_chat(user_input)
    except speech_recognition.UnknownValueError:
        recogniser = speech_recognition.Recognizer()
        speak("I didn't quite catch that...")
