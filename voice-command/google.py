from neuralintents import GenericAssistant
import speech_recognition, pyttsx3 as tts, sys, re

recogniser = speech_recognition.Recognizer()

speaker = tts.init()
speaker.setProperty('rate', 150)

def recognise_input(recognizer):
    with speech_recognition.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.2)
        audio = recognizer.listen(mic)
        message = recognizer.recognize_google(audio)
        message = message.lower()
        return message

def extract_song_and_artist(text):
    # Extract the song name and artist from the user input
    match = re.search(r'play(?: me)?\s(.+?)(?:\sby\s(.+))?$', text, re.IGNORECASE)
    song_name = match.group(1).strip() if match.group(1) is not None else None
    artist = match.group(2).strip() if match.group(2) is not None else ""
    return song_name, artist



def play_song():
    global recogniser
    print("[K9]\tSong Request")
    speaker.say("Sure, what song do you want to listen to?")
    speaker.runAndWait()

    done = False
    while not done:
        try:
            song = recognise_input(recogniser)
            print("[K9]\tSearching song...")
            speaker.say(f"Searching spotify for: {song}")
            speaker.runAndWait()
            done = True
        except speech_recognition.UnknownValueError:
            recogniser = speech_recognition.Recognizer()
            speaker.say("Please repeat...")
            speaker.runAndWait()

def play_specific_song():
    global message
    song_name, artist = extract_song_and_artist(message)
    if artist == "":
        print(f"[K9] Playing {song_name}.")
        speaker.say(f"Playing {song_name}.")
        speaker.runAndWait()
    else:
        print(f"[K9] Playing {song_name} by {artist}.")
        speaker.say(f"Playing {song_name}.")
        speaker.runAndWait()

    

def greeting():
    print("[K9]\tGreeting")
    speaker.say("Hello. What can I do for you?")
    speaker.runAndWait()

def quit():
    print("[K9]\tExit")
    speaker.say("Bye")
    speaker.runAndWait()
    sys.exit(0)

mappings = {
    "greetings": greeting,
    "play_song": play_song,
    "play_specific_song": play_specific_song,
    "exit": quit
}

assistant = GenericAssistant('intents.json', intent_methods=mappings)
assistant.train_model()
#assistant.load_model("model")

while True:
    try:
        message = recognise_input(recogniser)
        print(f"[INPUT]\t{message}")
        assistant.request(message)
    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        print("unknown")
