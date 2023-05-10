from neuralintents import GenericAssistant
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import speech_recognition
import pyttsx3 as tts
import sys
import json

IAM_KEY = IAMAuthenticator("-")
speech_to_text = SpeechToTextV1(authenticator=IAM_KEY)
speech_to_text.set_service_url("")

recogniser = speech_recognition.Recognizer()

speaker = tts.init()
speaker.setProperty('rate', 150)

def play_song():
    global recogniser

    speaker.say("Sure, what song do you want to listen to?")
    speaker.runAndWait

    done = False

    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recogniser.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recogniser.listen(mic)
                note = recogniser.recognize_google(audio)
                note = note.lower()

                speaker.say("choose a filename!")
                speaker.runAndWait()

                recogniser.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recogniser.listen(mic)

                filename = recogniser.recognize_google(audio)
                filename = filename.lower()

            with open(filename, 'w') as f:
                f.write(note)
                done = True
                speaker.say(f"I successfully created the note {filename}")
                speaker.runAndWait()
        except speech_recognition.UnknownValueError:
            recogniser = speech_recognition.Recognizer()
            speaker.say("I did not understand you! Please try again!")
            speaker.runAndWait()

def greeting():
    print("[greeting detected]")
    speaker.say("Hello. What can I do for you?")
    speaker.runAndWait()

def quit():
    speaker.say("Bye")
    speaker.runAndWait()
    sys.exit(0)

mappings = {
"greeting": greeting,
"play_song": play_song,
"quit": quit
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)
assistant.train_model( )
# assistant.save_model("model")
#assistant.load_model("model")

while True:

    try:
        with speech_recognition.Microphone() as mic:
            recogniser.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recogniser.listen(mic)

        message = speech_to_text.recognize(audio=audio.get_wav_data(), content_type='audio/wav', model='en-GB_NarrowbandModel').get_result()
        parsed_data = json.loads(json.dumps(message, indent=2))
        transcript = parsed_data["results"][0]["alternatives"][0]["transcript"]
        print(transcript)
        # assistant.request(message)

    except speech_recognition.UnknownValueError:
        recogniser = speech_recognition.Recognizer()
        print("unknown")
