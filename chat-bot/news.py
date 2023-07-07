from functions import *

with open('settings.json') as f:
        settings = json.load(f)
API_KEY = settings['newsdata']['api_key']

def extract_article_number(user_input):
    number_words = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5
    }
    # Extracts the number word from user input
    match = re.search(r'\bnumber\s*(\w+)\b', user_input, re.IGNORECASE)
    if match:
        number_word = match.group(1)
        if number_word in number_words:
            return number_words[number_word]
    return None

def get_news(user_input):
    local_recogniser = get_recogniser()
    # Fetch news data from the API
    url = 'https://newsdata.io/api/1/news?apikey={API_KEY}&language=en&country=gb&domain=bbc'
    news_data = requests.get(url)
    news = news_data.json()
    titles = ""
    # Extract the titles of the news articles
    for i in range(min(5, len(news["results"]))):
        titles += news["results"][i]["title"] + "\n"
    play_sound("sound/newsSearchFiller.mp3", 1, blocking=False)
    speak("Here's the latest news: \n" + titles)
    play_sound("sound/newsSelection.mp3", 1, blocking=False)
    done = False
    while not done:
        try:
            user_reply = recognise_input(local_recogniser)
            print("Reply: ", user_reply)
            if user_reply == "repeat":
                play_sound("sound/tts.mp3", 1, blocking=True)
                play_sound("sound/1to5.mp3", 1, blocking=True)
            elif user_reply == "no":
                play_sound("sound/noProblem.mp3", 1, blocking=True)
                done = True
            else:
                play_sound("sound/sure.mp3", 1, blocking=True)
                article_number = extract_article_number(user_reply)
                if article_number is not None:
                    article_index = article_number - 1
                    if 0 <= article_index < min(5, len(news["results"])):
                        play_sound("sound/newsFiller.mp3", 1, blocking=False)
                        # Speak the description of the selected news article
                        speak(news["results"][article_index]["description"])
                        done = True
                    else:
                        play_sound("sound/outOfRange.mp3", 1, blocking=True)
                        done = True
                else:
                    play_sound("sound/1to5.mp3", 1, blocking=True)
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=True)

def get_specific_news(user_input):
    local_recogniser = get_recogniser()
    matches = [
        re.search(r'\bon\s(?P<substring>.+)', user_input),
        re.search(r'\babout\s(?P<substring>.+)', user_input),
        re.search(r'\bon the\s(?P<substring>.+)', user_input),
        re.search(r'\babout the\s(?P<substring>.+)', user_input)
    ]

    max_position = -1
    substring_max = ""

    for match in matches:
        if match:
            substring = match.group("substring")
            position = match.start("substring")
            if position > max_position:
                max_position = position
                substring_max = substring

    # Fetch news data based on the specified topic from the API
    url = 'https://newsdata.io/api/1/news?apikey={API_KEY}&language=en&country=gb&q={substring_max}'
    news_data = requests.get(url)
    news = news_data.json()
    titles = ""
    # Extract the titles of the news articles
    for i in range(min(5, len(news["results"]))):
        titles += news["results"][i]["title"] + "\n"
    play_sound("sound/newsTopicSearchFiller.mp3", 1, blocking=False)
    speak(f"These are the latest news on {substring_max}: \n" + titles)
    play_sound("sound/newsSelection.mp3", 1, blocking=True)
    done = False
    while not done:
        try:
            user_reply = recognise_input(local_recogniser)
            print("Reply: ", user_reply)
            article_number = extract_article_number(user_reply)
            if user_reply == "repeat":
                play_sound("sound/tts.mp3", 1, blocking=True)
            elif user_reply == "no":
                play_sound("sound/noProblem.mp3", 1, blocking=True)
                done = True
            elif article_number is not None and 1 <= article_number <= 5:
                play_sound("sound/newsFiller.mp3", 1, blocking=False)
                # Speak the description of the selected news article
                speak(news["results"][article_number - 1]["description"])
                done = True
            else:
                play_sound("sound/1to5.mp3", 1, blocking=True)
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=True)
