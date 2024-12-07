import re
import numpy as np
from scipy.optimize import lsq_linear

def calculate(meals:list):
        
        '''
        LLM Output + Given Nutritional info -> % Error 
        '''

        sum_cals = 0
        sum_fats = 0
        sum_carbs = 0
        sum_protein = 0
        # search for all instances of nutrient 
        #amounts = re.findall(r"-.*\[(\d*) CAL\w*, (\d*)G F\w*, (\d*)G C\w*, (\d*)G P\w*\]", output)

        for meal in meals:
            meal_ingredients = meal['ingredients']
            for ingredient in meal_ingredients:
                sum_cals += float(ingredient['calories'])
                sum_fats += float(ingredient['fat'])
                sum_carbs += float(ingredient['carbs'])
                sum_protein += float(ingredient['protein'])
        return [sum_cals, sum_fats, sum_carbs, sum_protein]

## FIXME: Suggest tweaks to mealplan based on calories and corresponding macros
def generate_error_report(meals: list, calories: int, protein: int, fat: int, carbs: int):

    '''
    LLM meals + Given Nutritional info -> % Error 
    '''

    nutrients = calculate(meals)

    calories_error = abs(calories - nutrients[0])/calories
    fat_error = abs(fat - nutrients[1])/fat
    if carbs == 0:
        carbs = 1
    carbs_error = abs(carbs - nutrients[2])/carbs
    protein_error = abs(protein - nutrients[3])/protein
    
    
    # supply % error
    
    print(
        #
        f'''
        Start {calories} => Generated {nutrients[0]} Error: {calories_error}
        Start {fat} => Generated {nutrients[1]} Error: {fat_error}
        Start {carbs} => Generated {nutrients[2]} Error: {carbs_error}
        Start {protein} => Generated {nutrients[3]} Error: {protein_error}
        '''
    )
    return[
    [calories_error, fat_error, carbs_error, protein_error],
    [calories, nutrients[0]],
    [fat, nutrients[1], ],
    [carbs, nutrients[2]],
    [protein, nutrients[3]]
    ]

def correct_day(plan: list, calories: int, protein: int, fat: int, carbs: int, ):
    adjusted_day = []
    num_meals = len(plan)
    for meal in plan:
        ingredients = meal['ingredients']

        ingredients_info = [[], #calories 
                            [], #protein 
                            [], #fat
                            [], #carbs
        ]
        
        goals = [round(calories / num_meals), #calories 
                round(protein /  num_meals), #protein 
                round(fat / num_meals), #fat
                round(carbs / num_meals)] #fat
                

        #gather info of each ingredient 
        for ingredient in ingredients:
            amount = ingredient['amount']
            ing_calories = round(float(ingredient['calories']) / float(amount))
            ing_protein = round(float(ingredient['protein']) / float(amount))
            ing_fat = round(float(ingredient['fat']) / float(amount))
            ing_carbs = round(float(ingredient['carbs']) / float(amount))

            ingredients_info[0].append(ing_calories)
            ingredients_info[1].append(ing_protein)
            ingredients_info[2].append(ing_fat)
            ingredients_info[3].append(ing_carbs)
        

        ## Cool linear algebra stuff

        # define ingredients matrix
        matrix_a = np.array(ingredients_info)

        # define goal vector
        vector_b = np.array(goals)

        # debug:
        print(f"DEBUG\n{matrix_a}")
        print(f"DEBUG\n{vector_b}")

        # Iterate least squares solutions until one is found meeting the criteria below (essentially 'non-negative' solutions)
        n = matrix_a.shape[1]
        results = lsq_linear(matrix_a, vector_b, bounds=np.array([(0.,np.inf) for i in range(n)]).T, lsmr_tol='auto', verbose=0)

        #convert from np.float to python float (rounded)
        results_processed = []
        for result in results.x:
            results_processed.append(int(round(result)))

        final_cals = 0
        final_macros = {'protein':0,'fat':0, 'carbs':0}


        #adjust mealplan
        for index in range(len(ingredients)):
            amount = results_processed[index]

            #set nutritional info
            ingredients[index]['calories'] = round(amount * (float(ingredients[index]['calories']) / float(ingredients[index]['amount'])))
            ingredients[index]['protein'] = round(amount * (float(ingredients[index]['protein']) / float(ingredients[index]['amount'])))
            ingredients[index]['fat'] = round(amount * (float(ingredients[index]['fat']) / float(ingredients[index]['amount'])))
            ingredients[index]['carbs'] = round(amount * (float(ingredients[index]['carbs']) / float(ingredients[index]['amount'])))

            final_cals += ingredients[index]['calories']

            final_macros['protein'] += ingredients[index]['protein']
            final_macros['fat'] +=  ingredients[index]['fat']
            final_macros['carbs'] += ingredients[index]['carbs']

            #set amount of ingredient
            ingredients[index]['amount'] = amount

        meal['ingredients'] = ingredients
        meal['macros'] = final_macros
        meal['calories'] = final_cals
        adjusted_day.append(meal)
    return(adjusted_day)

def proccess_LLM_output(output: str, calories: int, protein: int, fat: int, carbs: int):
    #Standardize data
    #food_list = food_list.upper()
    output = output.upper()

    #Get foods as a list containing match groups from food list 
    #foods = re.findall(r"\d.*\*\*(.*).*\(*.*\)*\*\*.*\n.*-\WCAL\w*:\W(\d*).*P\w*:\W(\d*).*F\w*:\W*(\d*).*C\w*:\W(\d*).*", food_list)

    ## used to store food list data
    trimmed_foods = []
    '''
    for list in foods:
        food = list[0]
        excess = food.find("(")
        if excess != -1:
            food = food[:excess].strip()
        trimmed_foods.append(food)
        trimmed_foods.append([list[1],list[2],list[3],list[4]])
    ''' 

    #get ingredient + nutritional information. 
    ## search if ingredient in foods list. If so, use foodlist macros. Otherwise, use own macros

    mealplan = output
    startindex = 0
    ##This will be the final list sent to the front end
    final_mealplan = []

    days = re.findall(r".*(DAY\W*\d*)", mealplan)

    #for each day 
    for day in range(len(days)):
            ## check if not on the last element of days
            if day+1 != len(days):
                ## find the index where day x ends and day x+1 begins. This will help create a range which will be used to search for meals specific to the current day.
                endindex = mealplan.find(days[day+1])
            ## last day case
            else:
                ## set end index to last character of mealplan
                endindex = len(mealplan)

            ## find all meals in current day range
            meals = re.findall(r".*\*(.*):", mealplan[startindex:endindex])
            
            
            #for each meal in day
            ## create section of mealplan to be used when searching for ingredients
            mealplan_section = mealplan[startindex:endindex]
            start_section_index = 0
            
            ## used to hold all of the meals of the current day
            meals_of_day = []
            for meal in range(len(meals)):
                ## checks if not on the last element of meals
                if meal+1 != len(meals):
                    ## find the index where meal x ends and meal x+1 begins. This will help create a range which will be used to search for ingredients specific to the current meal.
                    end_section_index = mealplan_section.find(meals[meal+1])
                ## last meal case
                else:
                    end_section_index = len(mealplan_section)

                ## find all ingredients of the current meal
                ingredients = re.findall(r"-(.\d*)\W*([OZG]*)\W*(.*)\[(\d*).*CAL\w*,\W*(\d*).*F\w*,\W*(\d*).*C\w*,\W*(\d*).*P\w*\]", mealplan_section[start_section_index:end_section_index])

                ## see if better macro data exists. If so, replace what is found in the mealplan then format. If not, format data 
                final_ingredients = []
                for list in ingredients:
                    ## get ingredient name
                    ingredient = list[2].strip()
                    ## see if ingredient is in known foods
                    if ingredient in trimmed_foods:
                        ## get food's nutritional data from list of known foods
                        nutrition = trimmed_foods[trimmed_foods.index(ingredient)+1]
                        ## format data for frontend
                        final_ingredients.append({"ingredient": ingredient, "amount": "100", "unit": "G", "calories": nutrition[0], "fat": nutrition[2], "carbs": nutrition[3], "protein": nutrition[1]})
                    else:
                        ## format data for frontend
                        final_ingredients.append({"ingredient": ingredient, "amount": list[0].strip(), "unit": list[1], "calories": list[3], "fat": list[4], "carbs": list[5], "protein": list[6]})


                ## find all of the directions of the current meal
                directions = re.findall(r"- STEP.*\d*.*:([^\.]*)\W*<BR>", mealplan_section[start_section_index:end_section_index])
                ## Note: since there is only one match group, result is the matched string instead of list containing match groups
                final_directions = []
                for direction in directions:
                    #add direction text to list to be used by frontend
                    final_directions.append(direction.strip())
                
                #create meal object
                current_meal = {
                    "title": meals[meal],
                    "ingredients" : final_ingredients,
                    "directions" : final_directions
                }

                ##set up next loop
                meals_of_day.append(current_meal)
                start_section_index = end_section_index 

            corrected_day_plan = correct_day(meals_of_day, calories, protein, fat, carbs)
            generate_error_report(corrected_day_plan,calories,protein,fat,carbs)


            ## set up next loop
            final_mealplan.append(corrected_day_plan)
            startindex = endindex
    return final_mealplan


'''
sample_output = """## Day 3 <br>
### *Breakfast: <br>
- 2 eggs sunny side up [140 cals, 10g fat, 1g carbs, 12g protein] <br>
- 1 whole grain English muffin [130 cals, 1.5g fat, 26g carbs, 5g protein] <br>
- 2 tbsp peanut butter [188 cals, 16g fat, 6g carbs, 8g protein] <br>
#### Preparation Steps: <br>
- Step 1: Cook eggs in a non-stick skillet until whites are set. <br>
- Step 2: Toast the English muffin and spread peanut butter on top. <br>

### *Lunch: <br>
- 6 oz grilled pork tenderloin [280 cals, 10g fat, 0g carbs, 46g protein] <br>
- 1 cup sautéed bell peppers [40 cals, 0g fat, 10g carbs, 1g protein] <br>
- 1 cup cooked couscous [176 cals, 0g fat, 36g carbs, 6g protein] <br>
#### Preparation Steps: <br>
- Step 1: Grill pork tenderloin until cooked through. <br>
- Step 2: Sauté bell peppers until tender. <br>
- Step 3: Prepare couscous according to package instructions. <br>

### *Dinner: <br>
- 8 oz grilled shrimp [320 cals, 4g fat, 0g carbs, 68g protein] <br>
- 1 cup pasta (whole-wheat) with olive oil [320 cals, 14g fat, 56g carbs, 12g protein] <br>
- 1 cup arugula salad with lemon vinaigrette [85 cals, 6g fat, 6g carbs, 1g protein] <br>
#### Preparation Steps: <br>
- Step 1: Grill shrimp until pink and opaque. <br>
- Step 2: Cook pasta according to package directions, then toss with olive oil. <br>
- Step 3: Toss arugula salad with lemon vinaigrette. <br>


"""

calories = 2600
protein = 170 
fat = 130 
carbs = 300

plan = proccess_LLM_output(sample_output, calories, protein, fat, carbs)

for x in plan: 
    print(x)
    break

'''