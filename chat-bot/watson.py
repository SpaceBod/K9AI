from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from functions import *
from news import *
from recipes import *
from vision import *
from activities import *
from music import *
import csv

class WatsonAssistant:
    def __init__(self, api_key, id, service_url, intents_file):
        self.api_key = api_key
        self.id = id
        self.service_url = service_url
        self.intents_dict = self.read_intents_from_csv(intents_file)

        authenticator = IAMAuthenticator(api_key)
        self.assistant = AssistantV2(
            version='2021-11-27',
            authenticator=authenticator
        )
        self.assistant.set_service_url(service_url)
        response = self.assistant.create_session(assistant_id=id).get_result()
        self.session_id = response['session_id']

        self.intent_mapping = {
            'Weather': get_weather,
            'Day': get_day,
            'Song': request_song,
            'Song Request': request_specific_song,
            'Playlist': request_playlist,
            'Playlist Request': request_specific_playlist,
            'Pause': pause_music,
            'Play': play_music,
            'Play Liked Songs': play_liked,
            'Next Song': play_next,
            'Previous Song': play_previous,
            'News': get_news,
            'News Topic': get_specific_news,
            'Volume Up': increase_vol,
            'Volume Down': decrease_vol,
            'Volume Set': set_vol,
            'Add New Face': add_face,
            'Positive Behaviours': get_activity,
            'Greet By Name': greet_me,
            'Podcast Request': request_specific_podcast,
            'Podcast': request_podcast,
            'Joke': get_random_joke,
            'Podcast Suggestion': request_random_podcast,
            'Podcast Genre': request_genre_podcast,
            'Meal Recommend': get_random_meal_by_phrase,
            'Meal Search': search_meal,
            'Podcast Feedback Fav': podcast_feedback_fav,
            'Podcast Feedback Love': podcast_feedback_love,
            'Podcast Feedback Like': podcast_feedback_like,
            'Podcast Feedback Dislike': podcast_feedback_dis,
            'Podcast Feedback Strong Dislike': podcast_feedback_stdis,
            'Podcast Feedback Hate': podcast_feedback_hate,
            'Calendar Event': extract_calendar_info
        }

    def read_intents_from_csv(self, file_path):
        intents = {}
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            intents = {intent_id: intent_text for intent_id, intent_text in reader}
        return intents

    def watson_chat(self, speech_input):
        message_response = self.assistant.message(assistant_id=self.id, session_id=self.session_id,
                                                  input={'message_type': 'text', 'text': speech_input}).get_result()
        if 'generic' in message_response['output']:
            generic_responses = message_response['output']['generic']
            if generic_responses:
                assistant_reply = generic_responses[0].get('text')
                if assistant_reply:
                    intents = message_response['output'].get('intents', [])
                    if intents:
                        intent = intents[0]['intent']
                        intent_text = self.intents_dict.get(intent, 'Unknown intent')
                        print('Intent:', intent_text, "\tID: ", intent)
                        # Call the corresponding function based on the intent with TTS
                        if intent_text in self.intent_mapping:
                            speak(assistant_reply)
                            self.intent_mapping[intent_text](speech_input)
                        else:
                            speak(assistant_reply)

                    else:
                        speak("Oops! I am not sure how to respond to that.")
                else:
                    speak("Oops! I am not sure how to respond to that.")
            else:
                intents = message_response['output'].get('intents', [])
                if intents:
                    intent = intents[0]['intent']
                    intent_text = self.intents_dict.get(intent, 'Unknown intent')
                    print('Intent:', intent_text, "\tID: ", intent)
                    # Call the corresponding function based on the intent without TTS
                    if intent_text in self.intent_mapping:
                        self.intent_mapping[intent_text](speech_input)
                else:
                    speak("I am not sure how to respond to that.")
        else:
            speak("Oops! I am not sure how to respond to that.")
