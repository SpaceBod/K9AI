from functions import *
import random

API_KEY = "f690740882be4d4a9dce062ebdafc9d1"
HEADERS = {"Content-Type": "application/json"}

def extract_recipe_number(user_input):
    number_words = {
        'one': 1,
        'two': 2,
        'three': 3,
    }
    # Extracts the number word from user input
    match = re.search(r'\bnumber\s*(\w+)\b', user_input, re.IGNORECASE)
    if match:
        number_word = match.group(1)
        if number_word in number_words:
            return number_words[number_word]
    return None

def remove_html_tags(text):
    # Removes HTML tags from a text string
    clean_text = ""
    inside_tag = False
    for char in text:
        if char == "<":
            inside_tag = True
        elif char == ">":
            inside_tag = False
        elif not inside_tag:
            clean_text += char
    return clean_text

def get_data_from_api(url):
    # Fetches data from the API based on the provided URL
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def search_recipe_by_name(dish_name):
    # Searches for a recipe by the specified dish name
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={dish_name}&number=1&apiKey={API_KEY}"
    data = get_data_from_api(url)

    if data and 'results' in data and len(data['results']) > 0:
        recipe_id = data['results'][0]['id']
        instructions = get_recipe_instructions(recipe_id)
        if instructions:
            recipe = {
                "title": data['results'][0]['title'],
                "instructions": instructions
            }
            return [recipe]

    print(f"Could not find instructions for {dish_name}")
    return []

def get_recipe_instructions(recipe_id):
    # Fetches the recipe instructions for a given recipe ID
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={API_KEY}"
    data = get_data_from_api(url)

    if data and len(data) > 0 and 'steps' in data[0]:
        instructions = [step['step'] for step in data[0]['steps']]
        return "\n".join(instructions)

    return "No instructions available."

def get_random_recipes(number, meal_type):
    # Retrieves random recipes of the specified meal type
    url = f"https://api.spoonacular.com/recipes/random?number={number}&tags={meal_type}&apiKey={API_KEY}"
    data = get_data_from_api(url)

    if data:
        recipes = [{"title": recipe['title'], "instructions": remove_html_tags(recipe['instructions'])} for recipe in data['recipes']]
        return recipes
    else:
        return []

def get_random_meal_by_phrase(phrase):
    local_recogniser = get_recogniser()
    meal_type = ""
    # Determine the meal type based on the provided phrase
    if "breakfast" in phrase.lower():
        meal_type = "breakfast"
    elif "lunch" in phrase.lower():
        meal_type = "lunch"
    elif "dinner" in phrase.lower():
        meal_type = "dinner"
    else:
        meal_type = random.choice(["lunch", "breakfast", "dinner"])

    random_meals = get_random_recipes(3, meal_type)

    if random_meals:
        play_sound("sound/recipeSearch.mp3", 1, blocking=True)
        meal_string = "\n"
        for meal in random_meals:
            meal_string += meal["title"] + ".\n"
        play_sound("sound/recipeSearchFiller.mp3", 1, blocking=False)
        speak(f"Here are some {meal_type.capitalize()} meals!{meal_string}")
        play_sound("sound/SayNumberMeals.mp3", 1, blocking=True)
        done=False
        while not done:
            try:
                user_reply = recognise_input(local_recogniser)
                print("Reply: ", user_reply)
                recipe_number = extract_recipe_number(user_reply)
                if "zero" in user_reply or "0" in user_reply:
                    play_sound("sound/noProblem.mp3", 1, blocking=True)
                    done = True
                elif recipe_number is not None and 1 <= recipe_number <= 3:
                    play_sound("sound/recipeFiller.mp3", 1, blocking=False)
                    speak(f'Instructions: {random_meals[recipe_number - 1]["instructions"]}')
                    done = True
                    play_sound("sound/recipeEnd.mp3", 1, blocking=True)
                else:
                    play_sound("sound/InvalidChoice.mp3", 1, blocking=True)
            except speech_recognition.UnknownValueError:
                local_recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 1, blocking=True)
    else:
        play_sound("sound/recipeRepeat.mp3", 1, blocking=True)

# Extracts the name of the meal
def extract_meal_name(prompt):
    pattern = r"(?i)\b(how to make|recipe for|instructions for|how do I make|tell me how to make|show me how to make)\b\s+(.*)"
    match = re.search(pattern, prompt)
    if match:
        return match.group(2).strip()
    return None

# Searches for the recipe of a given meal
def search_meal(prompt):
    meal_name = extract_meal_name(prompt)
    if meal_name != None:
        recipes = search_recipe_by_name(meal_name)
        if recipes:
            play_sound("sound/RecipeSearchFiller.mp3", 1, blocking=False)
            speak(f"These are the instructions for {recipes[0]['title']}: {recipes[0]['instructions']}")
        else:
            play_sound("sound/NoRecipesFound.mp3", 1, blocking=True)
    else:
        play_sound("sound/repeat.mp3", 1, blocking=True)
