from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Doctor, UserRole
from utils import role_required

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/create_doctor", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def create_doc():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    specialization = data.get("specialization", "")

    if not email or not password or not name:
        return jsonify({"msg": "Missing required fields"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with this email already exists"}), 400
    
    user = User(email=email, 
                password = generate_password_hash(password), 
                name = name,
                role=UserRole.DOCTOR)
    db.session.add(user)
    db.session.commit()

    doc = Doctor(id=user.id, specialization=specialization)
    db.session.add(doc)
    db.session.commit()

    return jsonify({"msg": "Doctor created successfully", "doctor_id": doc.id}), 201

@admin_bp.route("/doctors", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_doctors():
    doctors = Doctor.query.all()
    result = []
    for doc in doctors:
        user = User.query.get(doc.id)
        result.append({
            "id": doc.id,
            "name": doc.user.name,
            "email": doc.user.email,
            "specialization": doc.specialization
        })
    return jsonify(result), 200