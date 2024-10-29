from openai import OpenAI
import time
import os
from dotenv import load_dotenv
import re


load_dotenv()
key = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key= key)
def generate_meal_plan_llm(user_data):

    plan_duration = {user_data['plan_duration']}
    meal_count = {user_data['meal_count']}

    calories = user_data['calories']
    carbs = (user_data['macros']['carbs'])
    fat = (user_data['macros']['fat'])
    protein = (user_data['macros']['protein'])
   
    diet_type = user_data['diet_type']
    preference_foods = user_data['flavor_preferences']
    avoid_foods = user_data['foods_to_avoid']

    timeStart = time.time()

    

def calculate(nutrient,output):

        '''
        LLM Output + Given Nutritional info -> % Error 
        '''

        sum = 0

        # search for all instances of nutrient 
        if nutrient == "calories":
            regex = "(\d{1,4})( cals)"
        else:
            regex = "(\d{1,4})(g "+nutrient+")"
        amounts = re.findall(regex, output)

        # sum nutrient
        for amount in amounts:
            sum += int(amount[0])
        return sum

## FIXME: Suggest tweaks to mealplan based on calories and corresponding macros
def check(output, calories, fat, carbs, protein):

    '''
    LLM Output + Given Nutritional info -> % Error 
    '''

    # extract macro information from given values
    fat = int(re.search(r"\d{1,4}", str(fat)).group())
    carbs = int(re.search(r"\d{1,4}", str(carbs)).group())
    protein = int(re.search(r"\d{1,4}", str(protein)).group())

    # extract calorie/macro sums from generated response
    gen_calories = calculate("calories",output)
    gen_fat = calculate("fat",output)
    gen_carbs = calculate("carbs",output)
    gen_protein = calculate("protein",output)
    
    # supply % error
    print(
        f'''
        Start {calories} => Generated {gen_calories} Error: {abs(calories - gen_calories)/calories}
        Start {fat} => Generated {gen_fat} Error: {abs(fat - gen_fat)/fat}
        Start {carbs} => Generated {gen_carbs} Error: {abs(carbs - gen_carbs)/carbs}
        Start {protein} => Generated {gen_protein} Error: {abs(protein - gen_protein)/protein}
        '''
    )

def generate_meal_plan_cheap_llm(data=None):

    '''
    User data -> LLM generated mealplan (Cheap, takes less time/money)
    '''

    #User data

    ## calories
    calories = data['calories']

    ## macros
    carbs = (data['macros']['carbs'])
    fat = (data['macros']['fat'])
    protein = (data['macros']['protein'])


    ## diet type
    diet_type = data['diet_type']
    '''
    - Vegetarian
    - Vegan
    - Keto
    - Omnivore
    - Carnivore
    '''

    ## preferences
    preference_foods = data['flavor_preferences']
    meal_number = int(data['meal_count'])
    plan_number = int(data['plan_duration'])
    ## avoid 
    avoid_foods = data['foods_to_avoid']


    #LLM generation 

    ##!! FIXME: INCLUDE INGREDIENT LIST FOR GROCERY SHOPPERS !!##
    ## Prompt 1 -> Generate meal plan
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert nutritionist who builds nutrition plans tailored to your clients specific needs"},
            {
                "role": "user",
                "content":
                
                f"""
                    Step 1: Create a mealplan for a(n) {diet_type} client for {plan_number} day(s) with {meal_number} meals
                            They like {preference_foods} and will not eat {avoid_foods}
                    Calories: {calories}
                    Macros: 
                        Carbs: {carbs}
                        Fats: {fat}
                        Protein: {protein}


                    Step 2: Format the output to look like the following template, do not include nutritional information
                            There can be more than 2 foods each meal if needed
                            Feel free to add/subtract the amount of meals below, as long as there are {meal_number} main meals
                    Template Mealplan:
                        ## Day 1 <br>
                        ### *Breakfast: <br>
                        - 4 of food <br>
                        - 5g of food <br>
                        - 4 of food <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                        ### *Lunch: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                        ### *Snack: <br>
                        - 2 oz food <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                        ### *Dinner: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        - 2 oz food <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                        ### *Evening Snack: <br>
                        - 3 food <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                """
            }
        ]
    )

    mealplan = completion.choices[0].message.content

    # format data
    meals = []
    plan = []

    startpoint = 0

    for day in range(plan_number):
        text = mealplan[startpoint:]

        ## find meals for day
        if day != plan_number-1:
            span = re.search(f"## Day {day+2} <br>\n", text)
            meals = re.findall(r"### \*.*:", text[:span.end()])
        else:
            meals = re.findall(r"### \*.*:", text)

        print(meals)
        
        ## find foods for each meal
        dayObject = []
        for meal in meals:
            text = mealplan[startpoint:]

            ### clean meals
            index = meal.find(':')
            meal = meal[5:index]
            
            ### get meal group 
            span = re.search(r"### \*.*: <br>\n(-.* <br>\n)*", text)
            
            ### get ingredients
            ingredients = re.findall(r"-.* <br>\n", text[span.start():span.end()])

            ### get/clean ingredients
            for index in range(len(ingredients)):
                ingredients[index] = re.search(r"-(.*)<br>\n", ingredients[index]).group(1)
                    
            ### get directions group
            span = re.search(r"####.*: <br>\n(- Step.*<br>\n)*", text)

            ### get directions
            directions = re.findall(r"-.* <br>\n", text[span.start():span.end()])

            ### clean directions
            for index in range(len(directions)):
                directions[index] = re.search(r"- (Step.*)<br>\n*", directions[index]).group(1)

            ### prepare for next cycle
            startpoint += span.end() 
            
            ### set object
            mealObject = {"title" : meal,
                            "calories": 0,
                            "macros": {'protein': 0, 'fat': 0, 'carbs': 0},
                            "ingredients": ingredients,
                            "directions" : directions
                        }

            dayObject.append(mealObject)
        plan.append(dayObject)
        print("Done, shouldn't take too long now")
    return(plan)




def generate_meal_plan_expensive(data=None):
    
    start = time.time()

    '''
    User data -> LLM generated mealplan (Expensive, takes more time/money)
    '''

    #User data

    ## calories
    calories = data['calories']

    ## macros
    carbs = (data['macros']['carbs'])
    fat = (data['macros']['fat'])
    protein = (data['macros']['protein'])


    ## diet type
    diet_type = data['diet_type']
    '''
    - Vegetarian
    - Vegan
    - Keto
    - Omnivore
    - Carnivore
    '''

    ## preferences
    preference_foods = data['flavor_preferences']
    meal_number = int(data['meal_count'])
    plan_number = int(data['plan_duration'])
    ## avoid 
    avoid_foods = data['foods_to_avoid']


    #LLM generation 

    client = OpenAI()
    

    ## Prompt 1 -> generate foodlist 
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert nutritionist who builds nutrition plans tailored to your clients specific needs"},
            {
                "role": "user",
                "content":
                
                f"""
                    Step 1: Find a list of about 50 healthy, diverse foods to be used in a mealplan for a(n) {diet_type} client.
                            The client likes {preference_foods} and will not eat {avoid_foods}

                    Step 2: Gather nutritional information for each food found in the 1st step corresponding to its serving size

                    Return the list
                """
            }
        ]
    )


    foodlist = completion.choices[0].message.content
    
    
    ## Prompt 2 -> build nutrition plan
    completion1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert nutritionist who builds nutrition plans tailored to your clients specific needs"},
            {
                "role": "user",
                "content":
                
                f"""
                    Step 1: Create a mealplan for a(n) {diet_type} client for {plan_number} day(s) with {meal_number} meals
                        Use the following foods to create the mealplan:
                        {foodlist}
                        Make sure to include all {plan_number} days in the plan
                        

                    Step 2: After the mealplan has been created, audit the mealplan to fit the following nutritional requirements:
                        Daily Calories: {calories}
                        Daily Carbs: {carbs}
                        Daily Fat: {fat}
                        Daily Protein: {protein}

                    Step 3: Format the output to look like the following sample (there can be more than 2 foods each meal if needed)           
                            Feel free to add/subtract the amount of meals below, as long as there are {meal_number} main meals
                            Only include '*' in front of meal names
                            "cals" MUST be used instead of "calories" for foods
                            "calories" must be used in daily total
                    Sample Mealplan:
                        ## Day 1 <br>
                        ### *Breakfast: <br>
                        - 4 of food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        - 4 of food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        - 4 of food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        ... etc
                        ### *Lunch: <br>
                        - 8 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        - 2 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        .
                        ### *Snack: <br>
                        - 2 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        .
                        ### *Dinner: <br>
                        - 8 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        - 2 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        - 2 oz food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        .
                        ### *Evening Snack:
                        - 3 food [x cals, [x]g fat, [x]g carbs, [x]g protein] <br>
                        ... etc
                        #### Preparation Steps: <br>
                        - Step 1: ... <br>
                        - Step 2: ... <br>
                        - Step 3: ... <br>
                        .
                        ### Totals: - Calories: x - Fat: [x]g - Carbs: [x]g - Protein: [x]g <br>
                """
            }
        ]
    )

    mealplan = completion1.choices[0].message.content
    print(mealplan)

    # format data
    meals = []
    plan = []

    startpoint = 0

    for day in range(plan_number):
        text = mealplan[startpoint:]

        ## find meals for day
        if day != plan_number-1:
            span = re.search(f"## Day {day+2} <br>\n", text)
            meals = re.findall(r"### \*.*:", text[:span.end()])

            ## Check output for accuracy
            check(text[:span.end()], calories, fat, carbs, protein)
        else:
            meals = re.findall(r"### \*.*:", text)

            ## Check output for accuracy
            check(text, calories, fat, carbs, protein)

        
        ## find foods for each meal
        dayObject = []
        for meal in meals:
            meal_cals = 0
            meal_fat = 0
            meal_carbs = 0
            meal_protein = 0

            text = mealplan[startpoint:]

            ### clean meals
            index = meal.find(':')
            meal = meal[5:index]
            
            ### get meal group 
            span = re.search(r"### \*.*: <br>\n(-.* <br>\n)*", text)
            
            
            ### get ingredients
            ingredients = re.findall(r"-.* <br>\n", text[span.start():span.end()])


            ### clean ingredients
            for index in range(len(ingredients)):
                # get ingredient properties (name, # cals, # fat, # carbs, # protein)
                ingredient = re.search(r"-(.*) \[(.*) cals, (.*)g fat, (.*)g carbs, (.*)g protein\]", ingredients[index])


                # add name/amount of ingredient to ingredients list
                ingredients[index] = ingredient.group(1)

                # add nutritional info to meal variables
                meal_cals += float(ingredient.group(2))
                meal_fat += float(ingredient.group(3))
                meal_carbs += float(ingredient.group(4))
                meal_protein += float(ingredient.group(5))

            
            ### get directions group
            span = re.search(r"####.*: <br>\n(- Step.*<br>\n)*", text)

            ### get directions
            directions = re.findall(r"-.* <br>\n", text[span.start():span.end()])

            ### clean directions
            for index in range(len(directions)):
                directions[index] = re.search(r"- (Step.*)<br>\n*", directions[index]).group(1)

            ### prepare for next cycle
            startpoint += span.end() 
            
            ### set object
            mealObject = {"title" : meal,
                            "calories": meal_cals,
                            "macros": {"protein": meal_protein, "carbs": meal_carbs, "fat": meal_fat},
                            "ingredients": ingredients,
                            "directions" : directions
                        }
            dayObject.append(mealObject)
        plan.append(dayObject)

        end = time.time()

    print(f"Time to execute: {end - start}")
    print(plan)

    return plan



