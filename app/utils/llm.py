from openai import OpenAI
import time
import os

key = os.environ("OPENAI_API_KEY")
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

    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert nutritionist who builds nutrition plans tailored to your clients specific needs"},
            {
                "role": "user",
                "content":
                
                f"""
                    Step 1: Create a mealplan for a(n) {diet_type} client for {plan_duration} day(s) with {meal_count} meals
                            They like {preference_foods} and will not eat {avoid_foods}
                    Calories: {calories}
                    Macros: 
                        Carbs: {carbs}
                        Fats: {fat}
                        Protein: {protein}


                    Step 2: Format the output to look like the following template, do not include nutritional information, include a list of ingredients for the mealplan at the end
                            There can be more than 2 foods each meal if needed, and meals/snacks can be cut to adhere to the requirements above
           
                    Template Mealplan:
                        ## Breakfast: <br>
                        - 4 of food <br>
                        - 5g of food <br>
                        - 4 of food <br>
                        ... etc
                        ## Lunch: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        ... etc
                        ## Snack: <br>
                        - 2 oz food <br>
                        ... etc 
                        ## Dinner: <br>
                        - 8 oz food <br>
                        - 2 oz food <br>
                        - 2 oz food <br>
                        ... etc 
                        ## Evening Snack:
                        - 3 food <br>
                        ... etc

                """
            }
        ]
    )


    mealplan = completion.choices[0].message.content

    timeEnd = time.time()
    

    #Output needs:
    #Meal
    ## Food 1
    ## Food 2... etc
    #Ingredients (done)
    #Directions (generated daily)

    return mealplan+"<br>Time to execute: "+str(timeEnd-timeStart)
