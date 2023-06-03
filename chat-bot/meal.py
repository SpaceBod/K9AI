import requests
import random

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

def get_random_recipes(number, meal_type):
    api_key = "f690740882be4d4a9dce062ebdafc9d1"
    headers = {
        "Content-Type": "application/json"
    }
    url = f"https://api.spoonacular.com/recipes/random?number={number}&tags={meal_type}&apiKey={api_key}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        recipes = [{"title": recipe['title'], "instructions": remove_html_tags(recipe['instructions'])} for recipe in data['recipes']]
        return recipes

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return []

def recommend_meals(text):
    print("Welcome to the Meal Recommender!")
    print("Let me recommend some meals for you to make.")

    meal_type = ""
    if "breakfast" in text.lower():
        meal_type = "breakfast"
    elif "lunch" in text.lower():
        meal_type = "lunch"
    elif "dinner" in text.lower():
        meal_type = "dinner"

    if meal_type:
        recipes = get_random_recipes(3, meal_type)
        if recipes:
            print(f"Recommended {meal_type.capitalize()} Meals:")
            for i, recipe in enumerate(recipes, start=1):
                print(f"{i}. {recipe['title']}")
            
            user_choice = input("Enter the number of the recipe you want to hear the instructions for (or enter 0 to exit): ")
            if user_choice.isdigit():
                index = int(user_choice) - 1
                if index >= 0 and index < len(recipes):
                    selected_recipe = recipes[index]
                    print("Instructions:")
                    print(selected_recipe["instructions"])
                elif index == -1:
                    return
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("Invalid choice. Please try again.")
        else:
            print(f"Sorry, couldn't find any {meal_type} recipes. Please try again.")
    else:
        print("Couldn't identify the meal type. Fetching 3 random recipes:")
        recipes = get_random_recipes(3, "")
        if recipes:
            print("Recommended Meals:")
            for i, recipe in enumerate(recipes, start=1):
                print(f"{i}. {recipe['title']}")
            
            user_choice = input("Enter the number of the recipe you want to hear the instructions for (or enter 0 to exit): ")
            if user_choice.isdigit():
                index = int(user_choice) - 1
                if index >= 0 and index < len(recipes):
                    selected_recipe = recipes[index]
                    print("Instructions:")
                    print(selected_recipe["instructions"])
                elif index == -1:
                    return
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Sorry, something went wrong. Please try again.")

text_input = input("Please enter your request: ")
recommend_meals(text_input)
