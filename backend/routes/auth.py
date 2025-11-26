from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from database import db
from models import User, UserRole

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"msg": "Name, email, and password are required"})

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400
    
    user = User(email=email,
                name=name,
                password=generate_password_hash(password),
                role = UserRole.PATIENT)
    db.session.add(user)
    db.session.commit()

    from models import Patient
    patient = Patient(id=user.id)
    db.session.add(patient)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid email or password"}), 401
    token = create_access_token(identity={"id": user.id, "role":user.role})
    return jsonify({"access_token": token, "role": user.role, "id":user.id})