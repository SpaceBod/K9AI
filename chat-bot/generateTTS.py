from elevenlabslib.helpers import *
from elevenlabslib import *

# A script used to generate MP3 TTS files

with open('settings.json') as f:
        settings = json.load(f)
api_key = settings['elevenLabsAPI']

user = ElevenLabsUser(api_key)
premadeVoice = user.get_voices_by_name("Jarvis")[0]

text = "Turning On the Lights"

generationData = premadeVoice.generate_play_audio(text , stability=0.4, similarity_boost=0.1, playInBackground=False, latencyOptimizationLevel = 0)
save_audio_bytes(generationData[0], "sample.mp3", outputFormat="mp3")
