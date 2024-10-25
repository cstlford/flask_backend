# app/models.py
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    # Relationships
    goals = db.relationship('UserGoal', backref='user', lazy=True)
    info = db.relationship('UserInfo', backref='user', uselist=False, lazy=True)
    meal_plan_preferences = db.relationship('UserMealPlanPreference', backref='user', lazy=True)
    nutrition = db.relationship('UserNutrition', backref='user', uselist=False)

    def get_id(self):
        return str(self.user_id)
    
    def __repr__(self):
        return f"<User {self.email}>"

class UserGoal(db.Model):
    __tablename__ = 'UserGoal'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    weight_goal = db.Column(db.String(64))
    cardio_goal = db.Column(db.String(64))
    resistance_goal = db.Column(db.String(64))

    def __repr__(self):
        return f"<UserGoal {self.user_id}>"

class UserInfo(db.Model):
    __tablename__ = 'UserInfo'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    diet = db.Column(db.String(64))
    activity_level = db.Column(db.String(64))

    def __repr__(self):
        return f"<UserInfo {self.user_id}>"

class UserMealPlanPreference(db.Model):
    __tablename__ = 'UserMealPlanPreferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    food_preferences = db.Column(db.String(256))
    food_avoidances = db.Column(db.String(256))
    meals_per_day = db.Column(db.Integer)
    plan_length = db.Column(db.Integer)


    def __repr__(self):
        return f"<UserMealPlanPreference {self.user_id}>"
    

class UserNutrition(db.Model):
    __tablename__ = 'UserNutrition'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)