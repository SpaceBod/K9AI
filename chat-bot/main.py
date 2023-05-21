from playsound import playsound as sound
from functions import *
from watson import WatsonAssistant
import os

# Initialising chat bot
recogniser = speech_recognition.Recognizer()
calibrate_mic(recogniser)
initialise_tts()

# Initialising spotify 
spot, dev_ID = initialise_spotify(
    client_id="3112161c7e454bce81ee3277ac772ceb",
    client_secret="a4e72d15ac164dba8c3f1559aa1ef7c1",
    redirect_uri="http://localhost:8888/callback",
    username="lucabod8",
    device_name="PC-BOD",
    scope="user-read-private user-read-playback-state user-modify-playback-state"
    )
send_variables(spot, dev_ID)

sound("assets/startup.mp3")
speak("Hi, I'm K9. What can I help you with?")

# Create an instance of the WatsonAssistant class
assistant = WatsonAssistant(
    api_key='IAuFqAtAVH6VNoar1hF6piBPIBDaEdgfNun5u69nwCsw',
    id='403bbca5-1481-422c-901c-bc1cb08d5611',
    service_url='https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/8031f7af-d4e8-43d4-a1c1-a93bbefb216a',
    intents_file='assets/intents.csv'
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
