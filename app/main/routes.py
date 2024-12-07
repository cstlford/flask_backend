from flask import request, jsonify
from app.main import main_bp
from app import db
from app.models import SavedExercisePlan, UserGoal, UserInfo, UserMealPlanPreference, UserNutrition, MealPlan, Chat
from app.models import UserWeightHistory
from flask_login import login_required, current_user
from datetime import datetime

from app.utils.exercise_functions import WorkoutPlanner
from app.utils.exercise_prompt import get_workout_plan_from_gpt
from app.utils.nutrition import (
    nutrition_plan,
    Goal,
    DietType,
    ActivityLevel
)

from app.utils.nutrition_prompt import generate_meal_plan_cheap_llm, generate_meal_plan_expensive, chat_with_coach

@main_bp.route('/', methods=['Get'])
def main():
    return 'Connection Successful'


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


@main_bp.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    user_id = current_user.user_id

    # Fetch user goal, info, and nutrition data
    user_goal = UserGoal.query.filter_by(user_id=user_id).first()
    user_info = UserInfo.query.filter_by(user_id=user_id).first()
    user_nutrition = UserNutrition.query.filter_by(user_id=user_id).first()

    # Prepare the response data
    response_data = {
        'id': current_user.user_id,
        'name': current_user.name,
        'email': current_user.email,
        'height': user_info.height,
        'weight': user_info.weight,
        'birthday' : user_info.birthday,
        'sex': user_info.sex,
        'activity_level' : user_info.activity_level,
        'diet':user_info.diet,
        'goals': {
            'weight_goal': user_goal.weight_goal.capitalize() if user_goal else None,
            'cardio_goal': user_goal.cardio_goal if user_goal else None,
            'resistance_goal': user_goal.resistance_goal if user_goal else None,
        } if user_goal else None,
        'diet_type': user_info.diet.strip('DietType.').capitalize() if user_info else None,
        'calories': user_nutrition.calories if user_nutrition else None,
        'macronutrients': {
            'protein': user_nutrition.protein if user_nutrition else None,
            'fat': user_nutrition.fat if user_nutrition else None,
            'carbs': user_nutrition.carbs if user_nutrition else None,
        } if user_nutrition else None
    }

    return jsonify(response_data), 200

    
@main_bp.route('/submit-weight-history', methods=['POST'])
@login_required
def submit_weight_history():
    user_id = current_user.user_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    weight = data.get('weight')
    date = data.get('date')
    weight_history = UserWeightHistory(
        user_id = user_id,
        weight = weight,
        date_selected = date
    )
    try:
        db.session.add(weight_history)
        db.session.commit()
        return jsonify({"message": "Weight history submitted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit profile data"}), 500

@main_bp.route('/get-weight-history', methods=['GET'])
@login_required
def get_weight_history():
    user_id = current_user.user_id
    weight_history = UserWeightHistory.query.filter_by(user_id=user_id).all()
    
    if not weight_history:
        return jsonify({"message": "No weight history found"}), 404

    # Extracting the weight and date from the result
    weight_data = [{"weight": entry.weight, "date": entry.date_selected} for entry in weight_history]

    return jsonify({"weight_history": weight_data}), 200



@main_bp.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan1():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # Extract data from request
    food_preferences = data.get('flavorPreferences')  
    food_avoidances = data.get('foodsToAvoid')
    meals_per_day = data.get('mealCount')
    plan_length = data.get('planDuration')

    # Validate required fields
    if not all([meals_per_day, plan_length]):
        return jsonify({"error": "Missing meal plan fields"}), 400

    # Retrieve user data from the database
    user_id = current_user.user_id

    user_info = UserInfo.query.filter_by(user_id=user_id).first()
    user_nutrition = UserNutrition.query.filter_by(user_id=user_id).first()

    # Extract the necessary data
    diet_type = user_info.diet.strip('DietType.').capitalize() if user_info and user_info.diet else None
    calories = user_nutrition.calories if user_nutrition else None
    macros = {
        'protein': user_nutrition.protein if user_nutrition else None,
        'fat': user_nutrition.fat if user_nutrition else None,
        'carbs': user_nutrition.carbs if user_nutrition else None,
    }
  

    # Prepare the data for the LLM
    user_data = {
        'diet_type': diet_type,
        'calories': calories,
        'macros': macros,
        'foods_to_avoid': food_avoidances,
        'flavor_preferences': food_preferences,
        'meal_count': meals_per_day,
        'plan_duration': plan_length,
    }
    user_meal_plan_preference = UserMealPlanPreference(

            user_id=user_id,
            food_preferences=food_preferences,
            food_avoidances=food_avoidances,
            meals_per_day=meals_per_day,
            plan_length= plan_length,
           

    )
    try:
        db.session.add(user_meal_plan_preference)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit profile data"}), 500



    # Call the LLM function to generate the meal plan
    selector = user_data['flavor_preferences'].find("Show me macros")

    ## expensive 
    try:
        meal_plan = generate_meal_plan_expensive(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'ai':meal_plan,'meals':meal_plan}), 200

@main_bp.route('/delete-chat-history', methods=['DELETE'])
@login_required
def delete_chat_history():
    try:
        user_id = current_user.user_id  # Ensure current_user is correctly set
        deleted_rows = Chat.query.filter_by(user_id=user_id).delete()

        if deleted_rows > 0:
            db.session.commit()
            return '', 204  # No content returned, but successful deletion
        else:
            return jsonify({'error': 'No chat history found'}), 404  # Chat history not found

    except Exception as e:
        db.session.rollback()  # Rollback if there is an error
        return jsonify({'error': str(e)}), 500  # Return the error message

@main_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    
    data = request.get_json()

    if not data:
        return jsonify(message='No JSON data received'), 400
    
   
    user_response = data.get("message")
    user_id = current_user.user_id
    user_info = UserInfo.query.filter_by(user_id=user_id).first()
    user_nutrition = UserNutrition.query.filter_by(user_id=user_id).first()
    user_meal_plan_preference = UserMealPlanPreference.query.filter_by(user_id=user_id).first()
    user_goal = UserGoal.query.filter_by(user_id=user_id).first()
    chat_history = Chat.query.filter_by(user_id=user_id).all()
    chat_data = ""
    
    for chat in chat_history:
        chat_data += f"User: {chat.user_text}"
        chat_data += f"Agent: {chat.agent_text}"

      

 
  
    response_data = {
        "User Name": current_user.name,
        "User Birthday": user_info.birthday.strftime('%Y-%m-%d') if user_info and user_info.birthday else "No Birthday Set",
        "User Weight": user_info.weight,
        "User Height": user_info.height,
        "User Sex": user_info.sex,
        "User Diet Type": user_info.diet,
        "User Activity Level": user_info.activity_level,
        "User Food Preferences": user_meal_plan_preference.food_preferences if user_meal_plan_preference else "No food Preferences Set",
        "User Food Restrictions": user_meal_plan_preference.food_avoidances if user_meal_plan_preference else "No food restrictions set",
        "User Calories Intake": user_nutrition.calories,
        "User Protein Per Day": user_nutrition.protein,
        "User Fat Per Day": user_nutrition.fat,
        "User Carbs Per Day": user_nutrition.carbs,
        "User Weight Goal": user_goal.weight_goal,
        "User Cardio Goal": user_goal.cardio_goal,
        "User Resistance Goal": user_goal.resistance_goal

    }
    


   
    agent_response = chat_with_coach(user_info=response_data, user_message=user_response, chat_history=chat_data)
    chat = Chat(
        user_id = user_id,
        user_text = user_response,
        agent_text = agent_response

    )
    try:
        db.session.add(chat)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to save Chat"}), 500
    
   
   
    response = {
        'message': agent_response.content if hasattr(agent_response, 'content') else str(agent_response),
        'role': 'assistant'
    }
    
    return jsonify(response)
    

@main_bp.route('/save-meal-plan', methods=['POST'])
@login_required
def save_meal_plan():
    data = request.get_json()
    meals = data.get('meals')
    if not meals:
        return jsonify({'error': 'No meal data provided'}), 400

    try:
        meal_plan = MealPlan(
            user_id=current_user.user_id,
            meals=meals 
        )
        db.session.add(meal_plan)
        db.session.commit()
        return jsonify({'message': 'Meal plan saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error saving meal plan: {e}")
        return jsonify({'error': 'Failed to save meal plan'}), 500


@main_bp.route('/get-meal-plans', methods=['GET'])
@login_required
def get_meal_plans():
    try:
        # Query all meal plans for the current user
        meal_plans = MealPlan.query.filter_by(user_id=current_user.user_id).all()
        
        # Serialize meal plans
        serialized_meal_plans = []
        for plan in meal_plans:
            serialized_plan = {
                'id': plan.id,
                'meals': plan.meals,  
            }
            serialized_meal_plans.append(serialized_plan)
        
        return jsonify({'meal_plans': serialized_meal_plans}), 200
    except Exception as e:
        print(f"Error fetching meal plans: {e}")
        return jsonify({'error': 'Failed to fetch meal plans'}), 500
    

@main_bp.route('/generate-exercise-plan', methods=['POST'])
@login_required
def generate_exercise_plan():

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
    print(data)


    daysPerWeek = data.get('daysPerWeek')
    if daysPerWeek >= 5:
        split_llm = "Push/Pull/Legs"
        split = split_llm
        num_plans = 3
    elif daysPerWeek == 4:
        split_llm = "Upper/Lower/Upper/Lower"
        split = "Upper/Lower"
        num_plans = 4
    else:
        split_llm = "Full Body"
        split = split_llm
        num_plans = daysPerWeek

    timePerWorkout = data.get('timePerWorkout')
    equipment = data.get('equipment')
    if equipment == 1:
        equipment = "Full gym"
    elif equipment == 2:
        equipment = "No equipment. Just bodyweight"
    else:
        equipment = f"{data.get('customEquipment')}, and bodyweight"

    user_id = current_user.user_id
    user_goal = UserGoal.query.filter_by(user_id=user_id).first()
    resistance_goal = user_goal.resistance_goal
    cardio_goal = user_goal.cardio_goal

    planner = WorkoutPlanner()
    structure = planner.plan_workout(total_time_minutes=timePerWorkout, goal=resistance_goal)

    workout_plans = get_workout_plan_from_gpt(num_plans, split_llm, structure, equipment)
    
    return jsonify({"workout_plan":workout_plans, "split": split}), 200


@main_bp.route('/save-exercise-plan', methods=['POST'])
@login_required
def save_exercise_plan():
    try:

        data = request.get_json()

        workout = data.get('workout')
        split = data.get('split')
        if not workout or not split:
            return jsonify({"error": "Invalid input. 'workout' and 'split' are required."}), 400

        new_plan = SavedExercisePlan(
            user_id=current_user.user_id, 
            workout=workout,
            split=split
        )

        db.session.add(new_plan)
        db.session.commit()

        return jsonify({"success": True, "message": "Exercise plan saved successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while saving the exercise plan.", "details": str(e)}), 500
    

@main_bp.route('/get-exercise-plans', methods=['GET'])
@login_required
def get_exercise_plans():
    try:
        # Query all exercise plans for the current user
        exercise_plans = SavedExercisePlan.query.filter_by(user_id=current_user.user_id).all()
        
        # Serialize exercise plans
        serialized_exercise_plans = []
        for plan in exercise_plans:
            serialized_plan = {
                'id': plan.id,
                'workout': plan.workout,  
            }
            serialized_exercise_plans.append(serialized_plan)
        return jsonify({'workout': serialized_exercise_plans}), 200
    except Exception as e:
        print(f"Error fetching meal plans: {e}")
        return jsonify({'error': 'Failed to fetch exercise plans'}), 500