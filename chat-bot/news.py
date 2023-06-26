from functions import *

def extract_article_number(user_input):
    number_words = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5
    }
    match = re.search(r'\bnumber\s*(\w+)\b', user_input, re.IGNORECASE)
    if match:
        number_word = match.group(1)
        if number_word in number_words:
            return number_words[number_word]
    return None

def get_news(user_input):
    local_recogniser = get_recogniser()
    news_data = requests.get('https://newsdata.io/api/1/news?apikey=pub_2224719bbcc10e32c3eaae46f288b9876718a&language=en&country=gb&domain=bbc')
    news = news_data.json()
    titles = ""
    for i in range(min(5, len(news["results"]))):
        titles += news["results"][i]["title"] + "\n"
    speak("Here's the latest news: \n" + titles)
    play_sound("sound/newsSelection.mp3", 1, blocking=False)
    done = False
    while not done:
        try:
            user_reply = recognise_input(local_recogniser)
            print("Reply: ", user_reply)
            if user_reply == "repeat":
                speak("Here are the latest news: \n" + titles)
                play_sound("sound/1to5.mp3", 1, blocking=False)
            elif user_reply == "no":
                play_sound("sound/noProblem.mp3", 1, blocking=False)
                done = True
            else:
                play_sound("sound/sure.mp3", 1, blocking=False)
                article_number = extract_article_number(user_reply)
                if article_number is not None:
                    article_index = article_number - 1
                    if 0 <= article_index < min(5, len(news["results"])):
                        speak(news["results"][article_index]["description"])
                        done = True
                    else:
                        play_sound("sound/outOfRange.mp3", 1, blocking=False)
                        done = True
                else:
                    play_sound("sound/1to5.mp3", 1, blocking=False)
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=False)

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

    news_data = requests.get(f'https://newsdata.io/api/1/news?apikey=pub_2224719bbcc10e32c3eaae46f288b9876718a&language=en&country=gb&q={substring_max}')
    news = news_data.json()
    titles = ""
    for i in range(min(5, len(news["results"]))):
        titles += news["results"][i]["title"] + "\n"
    speak(f"These are the latest news on {substring_max}: \n" + titles)
    play_sound("sound/newsSelection.mp3", 1, blocking=False)
    done = False
    while not done:
        try:
            user_reply = recognise_input(local_recogniser)
            print("Reply: ", user_reply)
            article_number = extract_article_number(user_reply)
            if user_reply == "repeat":
                speak(f"These are the latest news on {substring_max}: \n" + titles)
            elif user_reply == "no":
                play_sound("sound/noProblem.mp3", 1, blocking=False)
                done = True
            elif article_number is not None and 1 <= article_number <= 5:
                speak(news["results"][article_number - 1]["description"])
                done = True
            else:
                play_sound("sound/1to5.mp3", 1, blocking=False)
        except speech_recognition.UnknownValueError:
            local_recogniser = speech_recognition.Recognizer()
            play_sound("sound/repeat.mp3", 1, blocking=False)