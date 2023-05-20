from playsound import playsound as sound
from functions import *
from watson import WatsonAssistant

# Initialising chat bot
recogniser = speech_recognition.Recognizer()
calibrate_mic(recogniser)
initialise_tts()

sound("assets/startup.mp3")
speak("Hi, I'm K9. What can I help you with?")

# Create an instance of the WatsonAssistant class
assistant = WatsonAssistant(
    api_key='IAuFqAtAVH6VNoar1hF6piBPIBDaEdgfNun5u69nwCsw',
    id='a73e095b-e164-4e97-a310-391e26013c82',
    service_url='https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/8031f7af-d4e8-43d4-a1c1-a93bbefb216a',
    intents_file='assets/intents.csv'
)

while True:
    try:
        user_input = recognise_input(recogniser)
        print(f"[INPUT]\t{user_input}")
        assistant.watson_chat(user_input)
    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        speak("I didn't quite catch that...")
