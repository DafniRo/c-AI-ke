import requests
import json

# API
API_URL = "https://api.edamam.com/search"

def suggest_recipe(ingredients, app_id, app_key, dietary_preferences):
    ingredients_str = ','.join(ingredients)
    query_params = {
        'q': ingredients_str,
        'app_id': app_id,
        'app_key': app_key
    }
    if dietary_preferences:
        query_params['health'] = ','.join(dietary_preferences)
    response = requests.get(API_URL, params=query_params)
    if response.status_code != 200:
        raise Exception("Failed to fetch recipes")
    response_json = response.json()
    recipes = response_json['hits']
    return recipes

def main():
    # Edamam API id and key
    app_id = "4ba914f4"
    app_key = "2496a27507075c06755af5c64bdcde9f"

    # Ask the user for diet
    dietary_preferences = []
    DIET = input("Do you have any dietary restrictions? (yes/no) ").lower()
    if DIET == 'yes':
        while True:
        #if this is the first time the program runs it will ask dietary retrictions (the else statment is explained later)
            if len(dietary_preferences)==0:
                dietary_req = input("What are your dietary restrictions? (you can add more than one) ").lower()
            else: 
                dietary_req = input("You have one more chance to properly spell the ones you missed/forgot ").lower()

            # these if statements will append the relevant restrictions even if the user writes "vegetarian, vegan and I guess pescatarian"
            if 'vegetarian' in dietary_req.lower():
                dietary_preferences.append('vegetarian')
            if 'vegan' in dietary_req.lower():
                dietary_preferences.append('vegan')
            if 'pescatarian' in dietary_req.lower():
                dietary_preferences.append('pescetarian')
            if 'halal' in dietary_req.lower():
                dietary_preferences.append('halal')
            if 'lactose' in dietary_req.lower():
                dietary_preferences.append('lactose free')
            #there are ike 5-10 more we can add

            
            if len(dietary_preferences)>0:
                print('Dietary restrictions:', dietary_preferences)
                correction = input("Just to confirm, your restrictions are the above? ").lower()

                if 'maybe' in correction:
                    print('TI MAYBE RE MPAGLAMA? RE FIGE RE MALAKA APO DO RE BRO')
                    dietary_preferences=[]
                    print('otan eisai malakas den sou dinoume options')
                    break
                elif 'ye' or 'yup' or 'ya' in correction:
                    print('Perfect! Dietary restrictions:', dietary_preferences)
                break
            else: 
                print('Dietary restriction not found! We either not have it in the system or you suck at spelling IDIOT, please try again')
    elif DIET == 'no':
        dietary_preferences = ['none']
        print('Alright bet. Dietary restrictions:', dietary_preferences)
    else: 
        print('Are you illiterate? I said YES/NO')


    # Ask the user for ingredients
    ingredients = input("Tell me what ingredients you have, if you have any that is. Separated by commas please, I'm dumb. : ").split(',')
    ingredients = [ingredient.strip() for ingredient in ingredients]

    # Recipes based on the ingredients
    recipes = suggest_recipe(ingredients, app_id, app_key, dietary_preferences)
    if not recipes:
        print("No recipes found.")
    else:
        print("Here are your recipes then, Idiot. :")
        for recipe in recipes:
            author = recipe['recipe'].get('source', 'Unknown')
            print(f"- {recipe['recipe']['label']} by {author}")
            print(f"  Link: {recipe['recipe']['url']}")

if __name__ == '__main__':
    main()
