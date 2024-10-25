# app/main/routes.py
from flask import request, jsonify
from app.main import main_bp
from app import db
from app.models import UserGoal, UserInfo, UserMealPlanPreference, UserNutrition
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.nutrition import (
    nutrition_plan,
    Goal,
    DietType,
    ActivityLevel
)


@main_bp.route('/potato', methods=['GET'])
def potato():
    return 'hello potato'

@main_bp.route('/submit-profile-data', methods=['POST'])
@login_required
def submit_profile_data():
    data = request.get_json()

    if not data:
        return jsonify(message='No JSON data received'), 400

    body_info = data.get('body_info', {})
    birthday = body_info.get('birthday')
    try:
        birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid birthday format. Use YYYY-MM-DD."}), 400

    weight = body_info.get('weight')
    height = body_info.get('height')
    sex = body_info.get('sex')
    if sex == 'Male':
        is_male = True
    elif sex == 'Female':
        is_male = False
    else:
        return jsonify({'error': 'Invalid value for sex'}), 400


    fitness_goals = data.get('fitness_goals', {})
    weight_goal = fitness_goals.get('weight_management')
    cardio_goal = fitness_goals.get('cardio_goals')
    resistance_goal = fitness_goals.get('resistance_training_goals')

    daily_routine = data.get('daily_routine', {})
    diet_type = daily_routine.get('particular_diet')
    activity_level = daily_routine.get('activity_level')

    # Validate required fields
    if None in [weight, height, birthday, sex, weight_goal, diet_type, activity_level]:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
            # Convert date of birth to age
            today = datetime.today().date()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

            # Convert strings to enums
            goal = Goal[weight_goal.upper()]
            diet_type = DietType[diet_type.upper()]
            activity_level = ActivityLevel[activity_level.upper()]
    except Exception as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400


    try:
        result = nutrition_plan(
            weight=float(weight),
            height=float(height),
            age=int(age),
            is_male=bool(is_male),
            goal=goal,
            diet_type=diet_type,
            activity_level=activity_level
        )
    except Exception as e:
        return jsonify({'error': f'Error calculating nutrition plan: {str(e)}'}), 500
    
    # Save UserGoal
    user_goal = UserGoal(
        user_id=current_user.user_id,
        weight_goal=weight_goal,
        cardio_goal=cardio_goal,
        resistance_goal=resistance_goal,
    )

    # Save UserInfo
    user_info = UserInfo(
        user_id=current_user.user_id,
        birthday=birthday,
        weight=weight,
        height=height,
        sex=sex,
        diet=diet_type,
        activity_level=activity_level
    )

    user_nutrition = UserNutrition(
            user_id=current_user.user_id,
            calories=result['target_calories'],
            protein=float(result['macros']['protein']),
            fat=float(result['macros']['fat']),
            carbs=float(result['macros']['carbs'])
        )
    try:
        db.session.add(user_goal)
        db.session.add(user_info)
        db.session.add(user_nutrition)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit profile data"}), 500

    return jsonify(message='Profile data submitted successfully'), 200

@main_bp.route('/submit-mealplan-data', methods=['POST'])
@login_required
def submit_mealplan_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    food_preferences = data.get('flavorPreferences')  
    food_avoidances = data.get('foodsToAvoid')
    meals_per_day = data.get('mealCount')
    plan_length = data.get('planDuration')

    # Validate required fields
    if not all([food_preferences, food_avoidances, meals_per_day, plan_length]):
        return jsonify({"error": "Missing meal plan fields"}), 400

    mealplan_preference = UserMealPlanPreference(
        user_id=current_user.user_id,
        food_preferences=food_preferences,
        food_avoidances=food_avoidances,
        meals_per_day=meals_per_day,
        plan_length=plan_length
    )

    try:
        db.session.add(mealplan_preference)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit meal plan data"}), 500

    return jsonify(message='Meal plan data submitted successfully'), 200


@main_bp.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():

    meals = [
        [
            {
                "title": "Eggs & Toast",
                "calories": 350,
                "macros": {"protein": 20, "carbs": 40, "fat": 10},
                "ingredients": ["2 Eggs", "1Tb Butter", "1pc Toast"],
                "directions": "",
            },
            {
                "title": "Carrot Soup",
                "calories": 500,
                "macros": {"protein": 30, "carbs": 50, "fat": 20},
                "ingredients": [],
                "directions": "",
            },
            {
                "title": "Meatloaf",
                "calories": 600,
                "macros": {"protein": 35, "carbs": 60, "fat": 25},
                "ingredients": [],
                "directions": "",
            },
        ],
                [
            {
                "title": "Eggs & Toast",
                "calories": 350,
                "macros": {"protein": 20, "carbs": 40, "fat": 10},
                "ingredients": ["2 Eggs", "1Tb Butter", "1pc Toast"],
                "directions": "",
            },
            {
                "title": "Carrot Soup",
                "calories": 500,
                "macros": {"protein": 30, "carbs": 50, "fat": 20},
                "ingredients": [],
                "directions": "",
            },
            {
                "title": "Meatloaf",
                "calories": 600,
                "macros": {"protein": 35, "carbs": 60, "fat": 25},
                "ingredients": [],
                "directions": "",
            },
        ],
                [
            {
                "title": "Eggs & Toast",
                "calories": 350,
                "macros": {"protein": 20, "carbs": 40, "fat": 10},
                "ingredients": ["2 Eggs", "1Tb Butter", "1pc Toast"],
                "directions": "",
            },
            {
                "title": "Carrot Soup",
                "calories": 500,
                "macros": {"protein": 30, "carbs": 50, "fat": 20},
                "ingredients": [],
                "directions": "",
            },
            {
                "title": "Meatloaf",
                "calories": 600,
                "macros": {"protein": 35, "carbs": 60, "fat": 25},
                "ingredients": [],
                "directions": "",
            },
        ],
                [
            {
                "title": "Eggs & Toast",
                "calories": 350,
                "macros": {"protein": 20, "carbs": 40, "fat": 10},
                "ingredients": ["2 Eggs", "1Tb Butter", "1pc Toast"],
                "directions": "",
            },
            {
                "title": "Carrot Soup",
                "calories": 500,
                "macros": {"protein": 30, "carbs": 50, "fat": 20},
                "ingredients": [],
                "directions": "",
            },
            {
                "title": "Meatloaf",
                "calories": 600,
                "macros": {"protein": 35, "carbs": 60, "fat": 25},
                "ingredients": [],
                "directions": "",
            },
        ],
        # Add additional meal data as needed
    ]

    # Return the dummy data as JSON
    return jsonify(meals)