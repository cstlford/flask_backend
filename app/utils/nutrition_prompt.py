from openai import OpenAI
import time
import os
from dotenv import load_dotenv
import re
import google.generativeai as genai

from app.utils.llm_functions import proccess_LLM_output

## Initialize Client ##
load_dotenv()
key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key= key)
##-------------------##


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
    print(plan_number)
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
    '''
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
    '''
    
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
                        Make sure to include all {plan_number} days in the plan
                        

                    Step 2: After the mealplan has been created, audit the mealplan to fit the following nutritional requirements:
                        Daily Calories: {calories}
                        Daily Carbs: {carbs}
                        Daily Fat: {fat}
                        Daily Protein: {protein}

                    Step 3: Format the output to look like the following sample (there can be more than 2 foods each meal if needed)           
                            There should be exactly {meal_number} meals. Exclude snacks if needed
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
                        
                Only include the above format in your response, leave out any recommendations or totals.
                """
            }
        ]
    )

    mealplan = completion1.choices[0].message.content

    print(mealplan)

    plan = proccess_LLM_output(mealplan,calories,protein,fat,carbs)

    end = time.time()
    print(f"Time to execute: {end - start}")

    return plan

## testing
'''
data = {'calories':2600,
        'macros':{'carbs':300,
                  'fat':150, 
                  'protein':170},
        'diet_type':"Omnivore",
        'flavor_preferences':'',
        'meal_count':3,
        'plan_duration':3,
        'foods_to_avoid':''
                  }

print(generate_meal_plan_expensive(data))
'''


def chat_with_coach(user_info, user_message, chat_history):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Create the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-002",
    generation_config=generation_config,
    system_instruction=
    f""" 
             
                You are Hercules, an expert AI assistant and professional nutrition advisor with extensive knowledge across fitness, 
                health, and wellness frameworks. Use user data to guide them toward their specific diet, fitness goals, and health needs. 
                Your role is to provide clear, accurate, and actionable information that aligns with best practices in nutrition, exercise, 
                and health management.

                <system_constraints>

                Use user data to create personalized and precise advice.
                Adjust responses according to the user's fitness level, health status, and dietary preferences.
                Respect user privacy and provide only relevant health-related context to avoid over-personalization. </system_constraints>
                <response_guidelines>

                IMPORTANT: Focus on direct, specific advice. Avoid excessive explanations unless the user requests more detail.
                IMPORTANT: When discussing sensitive topics like weight loss, aim for constructive, supportive language.
                ULTRA IMPORTANT: Do NOT be verbose. Always prioritize clarity, and avoid providing unnecessary information unless requested.
                ULTRA IMPORTANT: Always base advice on established nutritional guidelines and fitness science. </response_guidelines>
                <special_handling_for_user_data>

                If the user provides physical metrics (e.g., weight, height, activity level), adjust dietary and fitness recommendations accordingly.
                Keep fitness plans adaptable and provide options for both dietary adjustments and exercise routines.
                Adjust advice based on dietary restrictions, preferences, and lifestyle (e.g., vegan, gluten-free, sedentary). </special_handling_for_user_data>

                If user ask for meal plan use this template:
                Template Mealplan:
                        ## Day 1 <br>
                        ### *Breakfast: <br>
                        - 4 of food <br>
                        - 5g of food <br>
                        - 4 of food <br>
                        ... etc
                        ### *Lunch: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        ... etc
                        ### *Snack: <br>
                        - 2 oz food <br>
                        ... etc
                        ### *Dinner: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        - 2 oz food <br>
                        ... etc
                        ### *Evening Snack: <br>
                        - 3 food <br>
                        ... etc
                User Info: {user_info}""",
    )

    chat_session = model.start_chat(
    history=[
    ]
    )

    response = chat_session.send_message(f"Chat History: {chat_history} \n User Message: {user_message}")




    print(response.text)
    return response.text