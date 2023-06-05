from elevenlabslib.helpers import *
from elevenlabslib import *

api_key = "ecf8b902a86fab1c3ec866b9a8ed6fc3"
user = ElevenLabsUser(api_key)
premadeVoice = user.get_voices_by_name("Jarvis")[0]

text = "Sorry, the specified article number is out of range."

generationData = premadeVoice.generate_play_audio(text , stability=0.4, similarity_boost=0.4, playInBackground=False, latencyOptimizationLevel = 0)
save_audio_bytes(generationData[0], "sample.mp3", outputFormat="mp3")