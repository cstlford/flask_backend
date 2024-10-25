import enum
from typing import Dict, Any

class ActivityLevel(enum.Enum):
    SEDENTARY = 1.2
    LIGHTLY_ACTIVE = 1.375
    MODERATELY_ACTIVE = 1.55
    VERY_ACTIVE = 1.725
    EXTRA_ACTIVE = 1.9

class Goal(enum.Enum):
    LOSE = 1
    MAINTAIN = 2
    GAIN = 3

class DietType(enum.Enum):
    OMNIVORE = 1
    CARNIVORE = 2
    KETO = 3
    VEGAN = 4
    VEGETARIAN = 5

def calculate_bmr(weight: float, height: float, age: int, is_male: bool) -> float:
    '''Calculates and returns basal metabolic rate given weight(kg), height(cm), age, and sex.'''
    if is_male:
        return 10 * weight + 6.25 * height - 5 * age + 5
    return  10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr: float,activity_level: float) -> float:
    '''Calculates and returns total daily energy expenditure given bmr and activity level'''
    return bmr * activity_level

def calculate_target_calories(tdee:float, goal: Goal) -> float:
    if goal == Goal.LOSE:
        return tdee * .75
    elif goal == Goal.GAIN:
        return tdee * 1.25
    else:
        return tdee

def calculate_macros(target_calories: float, goal: Goal, weight:float, diet_type: DietType) -> Dict[str,str]:
    if diet_type == DietType.OMNIVORE or diet_type == DietType.VEGETARIAN:
        return calculate_macros_omnivore(target_calories, goal, weight)
    elif diet_type == DietType.CARNIVORE:
         return calculate_macros_carnivore(target_calories, goal, weight)
    elif diet_type == DietType.KETO:
        return calculate_macros_keto(target_calories, goal, weight)
    elif diet_type == DietType.VEGAN :
        return calculate_macros_vegan(target_calories, goal, weight)
    else:
        return ValueError('Invalid diet type')


def calculate_macros_omnivore(target_calories: float, goal: Goal, weight: float) -> Dict[str, str]:
    '''Calculates macronutrient split for an omnivore diet based on goal (LOSE, GAIN, MAINTAIN) and weight (kg).'''
    
    if goal == Goal.LOSE:
        protein = weight * 2.1 # 2.1g per kg of body weight 
        fat = target_calories * 0.225 / 9 #22.5% of calories is fat. 9 calories per gram of fat
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4 #remaining calories are carbs. 4 calories per gram of carbs
    elif goal == Goal.GAIN:
        protein = weight  * 2.1 # 2.1g per kg of body weight
        fat = target_calories * .325 / 9#32.5% of calories
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4
    else:  # MAINTAIN
        protein = weight * 1.8  # 1.8g per kg of body weight
        fat = target_calories * .275 / 9 #27.5% of calories
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4 
    
    return {
        "protein": f'{round(protein)}',
        "fat": f'{round(fat)}',
        "carbs": f'{round(carbs)}'
    }

def calculate_macros_carnivore(target_calories: float, goal: Goal, weight: float) -> Dict[str, str]:
    '''Calculates macronutrient split for an carnivore diet based on goal (LOSE, GAIN, MAINTAIN) and weight (kg).'''
   
    if goal == Goal.LOSE:
        protein = weight * 3.0  # 3.0g per kg of body weight for weight loss
        fat = (target_calories - (protein * 4)) / 9  # remaining calories come from fat, carbs are near zero
        carbs = 0  # minimal carbs in a carnivore diet
    
    elif goal == Goal.GAIN:
        protein = weight * 2.5  # 2.5g per kg of body weight for weight gain
        fat = (target_calories - (protein * 4)) / 9  # remaining calories from fat
        carbs = 0  # minimal carbs
    
    else:  # MAINTAIN
        protein = weight * 2.7  # 2.7g per kg of body weight for maintenance
        fat = (target_calories - (protein * 4)) / 9  # remaining calories from fat
        carbs = 0  # minimal carbs
    
    return {
        "protein": f'{round(protein)}',
        "fat": f'{round(fat)}',
        "carbs": f'{carbs}'
    }

def calculate_macros_keto(target_calories: float, goal: Goal, weight: float) -> Dict[str, str]:
    '''Calculates macronutrient split for a ketogenic diet based on goal (LOSE, GAIN, MAINTAIN) and weight (kg).'''
    
    if goal == Goal.LOSE:
        protein = weight * 1.8  # 1.8g per kg of body weight for weight loss
        fat = target_calories * 0.75 / 9  # 75% of calories from fat
        carbs = (target_calories * 0.05) / 4  # 5% of calories from carbs (can adjust if stricter)
    
    elif goal == Goal.GAIN:
        protein = weight * 1.6  # 1.6g per kg of body weight for weight gain
        fat = target_calories * 0.70 / 9  # 70% of calories from fat
        carbs = (target_calories * 0.10) / 4  # 10% of calories from carbs
    
    else:  # MAINTAIN
        protein = weight * 1.4  # 1.4g per kg of body weight for maintenance
        fat = target_calories * 0.75 / 9  # 75% of calories from fat
        carbs = (target_calories * 0.05) / 4  # 5% of calories from carbs
    
    return {
        "protein": f'{round(protein)}',
        "fat": f'{round(fat)}',
        "carbs": f'{round(carbs)}'
    }

def calculate_macros_vegan(target_calories: float, goal: Goal, weight: float) -> Dict[str, str]:
    '''Calculates macronutrient split for a vegan diet based on goal (LOSE, GAIN, MAINTAIN) and weight (kg).'''
    
    if goal == Goal.LOSE:
        protein = weight * 2.0  # 2.0g per kg of body weight
        fat = target_calories * 0.20 / 9  # 20% of calories from fat
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4  # remaining calories from carbs
    
    elif goal == Goal.GAIN:
        protein = weight * 1.8  # 1.8g per kg of body weight
        fat = target_calories * 0.30 / 9  # 30% of calories from fat
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4
    
    else:  # MAINTAIN
        protein = weight * 1.6  # 1.6g per kg of body weight
        fat = target_calories * 0.25 / 9  # 25% of calories from fat
        carbs = (target_calories - (protein * 4 + fat * 9)) / 4
    
    return {
        "protein": f'{round(protein)}',
        "fat": f'{round(fat)}',
        "carbs": f'{round(carbs)}'
    }

def nutrition_plan(weight: float, height: float, age:int, is_male:bool, goal:Goal, diet_type: DietType, activity_level: ActivityLevel) -> Dict[str,Any]:
    bmr = calculate_bmr(weight,height,age,is_male)
    tdee = calculate_tdee(bmr, activity_level.value)
    target_calories = calculate_target_calories(tdee, goal)
    macros = calculate_macros(target_calories, goal, weight, diet_type)

    return{
        "target_calories": round(target_calories),
        "macros": macros
    }






