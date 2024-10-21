# app/main/routes.py
from flask import request, jsonify
from app.main import main_bp
from app import db
from app.models import UserGoal, UserInfo, UserMealPlanPreference
from flask_login import login_required, current_user
from datetime import datetime


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

    fitness_goals = data.get('fitness_goals', {})
    weight_goal = fitness_goals.get('weight_management')
    cardio_goal = fitness_goals.get('cardio_goals')
    resistance_goal = fitness_goals.get('resistance_training_goals')

    daily_routine = data.get('daily_routine', {})
    diet = daily_routine.get('particular_diet')
    activity_level = daily_routine.get('activity_level')

    # Validate required fields
    if not all([birthday, weight, height, sex]):
        return jsonify({"error": "Missing body_info fields"}), 400

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
        diet=diet,
        activity_level=activity_level
    )

    try:
        db.session.add(user_goal)
        db.session.add(user_info)
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