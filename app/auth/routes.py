from flask import request, jsonify
from app import db, bcrypt
from app.models import User
from app.auth import auth_bp
from flask_login import login_user, logout_user, login_required


@auth_bp.route('/register', methods=['POST'])
def register():
   
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(name=name, email=email, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing data"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200