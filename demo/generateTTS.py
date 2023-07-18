from elevenlabslib.helpers import *
from elevenlabslib import *
from elevenlabs import *
# A script used to generate MP3 TTS files

api_key = "652cfcc78a55462e2d05ea895c3625ae"
user = ElevenLabsUser(api_key)
premadeVoice = user.get_voices_by_name("British")[0]

text = "Let me show you my walk!"

generationData = premadeVoice.generate_play_audio(text , stability=0.1, similarity_boost=0.3, playInBackground=False, latencyOptimizationLevel = 0)
save_audio_bytes(generationData[0], "sample.mp3", outputFormat="mp3")

# FUNCTION FOR DEMO:
# def speak(text, auto_play=True):
#     print('K9: ' + text)
#     set_api_key("652cfcc78a55462e2d05ea895c3625ae")
#     available_voices = voices()
#     audio = generate(
#       text=text,
#       voice=available_voices[9],
#       model="eleven_monolingual_v1"
#     )
#     save(audio, "tts.mp3")
