import requests
import random

API_KEY = "f690740882be4d4a9dce062ebdafc9d1"
HEADERS = {"Content-Type": "application/json"}

def remove_html_tags(text):
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
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def search_recipe_by_name(dish_name):
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
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={API_KEY}"
    data = get_data_from_api(url)

    if data and len(data) > 0 and 'steps' in data[0]:
        instructions = [step['step'] for step in data[0]['steps']]
        return "\n".join(instructions)

    return "No instructions available."

def get_random_recipes(number, meal_type):
    url = f"https://api.spoonacular.com/recipes/random?number={number}&tags={meal_type}&apiKey={API_KEY}"
    data = get_data_from_api(url)

    if data:
        recipes = [{"title": recipe['title'], "instructions": remove_html_tags(recipe['instructions'])} for recipe in data['recipes']]
        return recipes
    else:
        return []

def get_random_meal_by_phrase(phrase):
    meal_type = ""
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
        print(f"Random {meal_type.capitalize()} Meals:")
        for i, meal in enumerate(random_meals, start=1):
            print(f"{i}. {meal['title']}")

        user_choice = input("Enter the number of the meal you want to get instructions for (or enter 0 to exit): ")
        if user_choice.isdigit():
            index = int(user_choice) - 1
            if index >= 0 and index < len(random_meals):
                selected_meal = random_meals[index]
                print("Instructions:")
                print(selected_meal["instructions"])
            elif index == -1:
                return
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please try again.")
    else:
        print(f"Sorry, couldn't find any {meal_type} meals. Please try again.")


# Example usage for getting food recommendations:
# Accepts phrases with: breakfast lunch dinner, if none found, gets random meal
phrase = "I want a random  recipe"
get_random_meal_by_phrase(phrase)

print("\n\n\n")

# Example usage for getting recipe from name:
dish_name = "burger"
recipes = search_recipe_by_name(dish_name)
if recipes:
    print(f"Title: {recipes[0]['title']}")
    print("Instructions:")
    print(recipes[0]['instructions'])
else:
    print("No recipe found for the given dish name.")