from flask import request, jsonify
from app.main import main_bp
from app import db
from app.models import UserGoal, UserInfo, UserMealPlanPreference, UserNutrition, MealPlan, Chat
from app.models import UserWeightHistory
from flask_login import login_required, current_user
from datetime import datetime

from app.utils.nutrition import (
    nutrition_plan,
    Goal,
    DietType,
    ActivityLevel
)

from app.utils.llm import generate_meal_plan_cheap_llm, generate_meal_plan_expensive, chat_with_coach

@main_bp.route('/', methods=['Get'])
def main():
    return 'Connection Successful'
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
    if selector != -1:
        user_data['flavor_preferences'] = user_data['flavor_preferences'][selector+1:]
        try:
            meal_plan = generate_meal_plan_expensive(user_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    ## cheap
    else:
        try:

            """
            "title": "Eggs & Toast",
                "calories": 350,
                "macros": {"protein": 20, "carbs": 40, "fat": 10},
                "ingredients": ["2 Eggs", "1Tb Butter", "1pc Toast"],
                "directions": "",
            
            """
            meal_plan = generate_meal_plan_cheap_llm(user_data)
       

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
        meals = [
            # Day 1
            [
                {
                    "title": "Oatmeal with Berries",
                    "calories": 350,
                    "macros": {"protein": 15, "carbs": 60, "fat": 8},
                    "ingredients": ["1/2 cup Oats", "1 cup Almond Milk", "1/4 cup Berries", "1 Tbsp Honey"],
                    "directions": "Cook oats in almond milk, top with berries and honey."
                },
                {
                    "title": "Grilled Chicken Salad",
                    "calories": 450,
                    "macros": {"protein": 35, "carbs": 40, "fat": 15},
                    "ingredients": ["100g Grilled Chicken", "Mixed Greens", "1/2 Avocado", "Cherry Tomatoes", "Balsamic Dressing"],
                    "directions": "Combine ingredients, top with balsamic dressing."
                },
                {
                    "title": "Salmon and Quinoa",
                    "calories": 600,
                    "macros": {"protein": 40, "carbs": 55, "fat": 20},
                    "ingredients": ["150g Salmon", "1/2 cup Quinoa", "Steamed Broccoli", "1 Tbsp Olive Oil"],
                    "directions": "Grill salmon, serve with cooked quinoa and steamed broccoli."
                },
            ],
            # Day 2
            [
                {
                    "title": "Greek Yogurt with Granola",
                    "calories": 300,
                    "macros": {"protein": 20, "carbs": 45, "fat": 8},
                    "ingredients": ["1 cup Greek Yogurt", "1/4 cup Granola", "Honey drizzle"],
                    "directions": "Top yogurt with granola and honey."
                },
                {
                    "title": "Turkey Wrap",
                    "calories": 400,
                    "macros": {"protein": 30, "carbs": 40, "fat": 12},
                    "ingredients": ["Whole Wheat Wrap", "100g Turkey Breast", "Lettuce", "Tomato", "1 Tbsp Hummus"],
                    "directions": "Assemble wrap with ingredients."
                },
                {
                    "title": "Beef Stir-Fry",
                    "calories": 550,
                    "macros": {"protein": 40, "carbs": 50, "fat": 18},
                    "ingredients": ["100g Beef Strips", "Mixed Vegetables", "1 cup Brown Rice", "Soy Sauce"],
                    "directions": "Stir-fry beef and vegetables, serve with rice."
                },
            ],
            # Day 3
            [
                {
                    "title": "Avocado Toast with Egg",
                    "calories": 300,
                    "macros": {"protein": 15, "carbs": 35, "fat": 14},
                    "ingredients": ["1 Slice Whole Grain Bread", "1/2 Avocado", "1 Egg"],
                    "directions": "Toast bread, top with mashed avocado and fried egg."
                },
                {
                    "title": "Quinoa Salad",
                    "calories": 400,
                    "macros": {"protein": 20, "carbs": 60, "fat": 12},
                    "ingredients": ["1/2 cup Quinoa", "Mixed Vegetables", "1 Tbsp Olive Oil", "Lemon Juice"],
                    "directions": "Mix ingredients and season with lemon juice."
                },
                {
                    "title": "Shrimp and Veggies",
                    "calories": 500,
                    "macros": {"protein": 35, "carbs": 40, "fat": 15},
                    "ingredients": ["150g Shrimp", "Steamed Vegetables", "1 cup Couscous"],
                    "directions": "Sauté shrimp, serve with couscous and vegetables."
                },
            ],
            # Day 4
            [
                {
                    "title": "Smoothie Bowl",
                    "calories": 350,
                    "macros": {"protein": 20, "carbs": 55, "fat": 10},
                    "ingredients": ["1 Banana", "1/2 cup Berries", "1 scoop Protein Powder", "1 Tbsp Almond Butter"],
                    "directions": "Blend ingredients, top with granola."
                },
                {
                    "title": "Tuna Salad",
                    "calories": 450,
                    "macros": {"protein": 35, "carbs": 30, "fat": 18},
                    "ingredients": ["100g Tuna", "Mixed Greens", "Olives", "1 Tbsp Olive Oil"],
                    "directions": "Mix ingredients with olive oil."
                },
                {
                    "title": "Chicken Stir-Fry",
                    "calories": 600,
                    "macros": {"protein": 45, "carbs": 55, "fat": 15},
                    "ingredients": ["100g Chicken Breast", "Mixed Vegetables", "1 cup Rice"],
                    "directions": "Cook chicken and vegetables, serve with rice."
                },
            ],
            # Day 5
            [
                {
                    "title": "Egg and Veggie Scramble",
                    "calories": 320,
                    "macros": {"protein": 20, "carbs": 20, "fat": 18},
                    "ingredients": ["2 Eggs", "Bell Peppers", "Onion", "1 Tbsp Olive Oil"],
                    "directions": "Scramble eggs with vegetables."
                },
                {
                    "title": "Chicken Wrap",
                    "calories": 420,
                    "macros": {"protein": 30, "carbs": 40, "fat": 15},
                    "ingredients": ["Whole Wheat Wrap", "100g Chicken Breast", "Lettuce", "Hummus"],
                    "directions": "Wrap ingredients together."
                },
                {
                    "title": "Beef and Sweet Potato",
                    "calories": 550,
                    "macros": {"protein": 35, "carbs": 50, "fat": 15},
                    "ingredients": ["100g Beef", "1 Sweet Potato", "Green Beans"],
                    "directions": "Cook beef and serve with roasted sweet potato and green beans."
                },
            ],
            # Day 6
            [
                {
                    "title": "Chia Pudding",
                    "calories": 300,
                    "macros": {"protein": 10, "carbs": 45, "fat": 12},
                    "ingredients": ["3 Tbsp Chia Seeds", "1 cup Almond Milk", "1 Tbsp Honey"],
                    "directions": "Mix chia seeds with almond milk and let sit overnight."
                },
                {
                    "title": "Turkey and Avocado Salad",
                    "calories": 420,
                    "macros": {"protein": 35, "carbs": 30, "fat": 18},
                    "ingredients": ["100g Turkey", "Mixed Greens", "1/2 Avocado"],
                    "directions": "Combine ingredients."
                },
                {
                    "title": "Baked Salmon and Asparagus",
                    "calories": 550,
                    "macros": {"protein": 40, "carbs": 40, "fat": 20},
                    "ingredients": ["150g Salmon", "Asparagus", "1/2 cup Brown Rice"],
                    "directions": "Bake salmon and serve with rice and asparagus."
                },
            ],
            # Day 7
            [
                {
                    "title": "Veggie Omelette",
                    "calories": 350,
                    "macros": {"protein": 20, "carbs": 30, "fat": 15},
                    "ingredients": ["3 Eggs", "Bell Peppers", "Spinach", "1 Tbsp Olive Oil"],
                    "directions": "Cook vegetables, then add eggs to make an omelette."
                },
                {
                    "title": "Lentil Soup",
                    "calories": 400,
                    "macros": {"protein": 25, "carbs": 50, "fat": 10},
                    "ingredients": ["1 cup Lentils", "Carrots", "Celery", "Garlic"],
                    "directions": "Simmer lentils with vegetables until tender."
                },
                {
                    "title": "Chicken and Quinoa Bowl",
                    "calories": 600,
                    "macros": {"protein": 45, "carbs": 55, "fat": 15},
                    "ingredients": ["100g Grilled Chicken", "1/2 cup Quinoa", "Steamed Broccoli"],
                    "directions": "Combine grilled chicken with quinoa and broccoli."
                },
            ],
        ]
    return jsonify({'ai':meal_plan,'meals':meals}), 200

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

    return jsonify("yeet"), 200
 