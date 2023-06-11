from functions import *
import random
import csv

def get_activity(text):
    local_recogniser = get_recogniser()
    categories = ["Exercise", "Gratitude", "Learning", "Reading"]
    folder_path = os.path.join('assets', 'behaviours')
    location = "Chelsea"  # adjust to dog location

    def get_suggestions():
        suggestions = []
        closest_temperature_diff = float('inf')
        closest_temperature_activity = None

        with open(file_path, 'r') as options:
            reader = csv.reader(options)
            for row in reader:
                row_weather = row[1]
                row_temperature = int(row[2])
                temperature_diff = abs(row_temperature - temp)

                if weather == row_weather:
                    if temperature_diff < closest_temperature_diff:
                        closest_temperature_diff = temperature_diff
                        closest_temperature_activity = row[3]

        if closest_temperature_activity:
            suggestions.append(closest_temperature_activity)

        return suggestions

    while True:
        weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&APPID={weather_key}")
        weather_json = weather_data.json()
        weather = weather_json['weather'][0]['main']
        temp = round(weather_json['main']['temp'])
        print(temp, weather)

        if weather == 'Sunny':
            category = 'Walking'
        else:
            category = random.choice(categories)

        print(category)
        file_path = os.path.join(folder_path, f'{category}.csv')

        suggestions = get_suggestions()
        motivation = random.choice(suggestions)
        prev_motivation = motivation
        prev_category = category

        speak(f"My suggestion is ... {motivation}")
        play_sound("sound/differentSuggestion.mp3", 0.5, blocking=False)

        attempt_counter = 0
        max_attempts = 3  # Set the maximum number of attempts

        while attempt_counter < max_attempts:
            category = random.choice(categories)
            try:
                response = recognise_input(local_recogniser)
                print("[INPUT] ", response)
                if 'yes' in response:
                    while prev_category == category:
                        category = random.choice(categories)
                    suggestions = get_suggestions()
                    if suggestions:
                        suggestions.remove(prev_motivation)  # Remove the previous suggestion from the available suggestions
                        if suggestions:
                            motivation = random.choice(suggestions)
                        else:
                            play_sound("sound/noSuggestions.mp3", 0.5, blocking=False)
                            break  # Exit the inner while loop
                        speak(f"Another suggestion is ... {motivation}")
                    else:
                        play_sound("sound/noSuggestions.mp3", 0.5, blocking=False)
                        break  # Exit the inner while loop
                    break  # Exit the inner while loop
                elif 'no' in response:
                    play_sound("sound/noProblem.mp3", 0.5, blocking=False)
                    break  # Exit the inner while loop
                else:
                    play_sound("sound/yesNoRespond.mp3", 0.5, blocking=False)
                attempt_counter += 1
            except speech_recognition.UnknownValueError:
                local_recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 0.5, blocking=False)

        if attempt_counter >= max_attempts:
            play_sound("sound/noSuggestions.mp3", 0.5, blocking=False)
        break  # Exit the outer while loop