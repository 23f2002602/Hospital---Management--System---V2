from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import *
from utils import role_required
from tasks import export_appointments_csv
from celery.result import AsyncResult

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/create_doctor", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def create_doctor():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    specialization = data.get("specialization", "")
    department_id = data.get("department_id", None)

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

    doc = Doctor(id=user.id, 
                 specialization=specialization, 
                 department_id=department_id)
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
            "specialization": doc.specialization,
            "department": doc.department_id})
    return jsonify(result), 200


@admin_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def get_doc(doctor_id):
    d = Doctor.query.get_or_404
    return jsonify({
        "id": d.id,
        "name": d.user.name,
        "email": d.user.email,
        "specialization": d.specialization,
        "department": d.department_id
    }), 200


@admin_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
@role_required([UserRole.ADMIN])
def update_doc(doctor_id):
    d = Doctor.query.get_or_404(doctor_id)
    data = request.get_json() or {}

    if data.get("name") is not None:
        d.user.name = data.get("name")
    if data.get("email") is not None:
        if User.query.filter(User.email == data.get("email"), User.id != d.id).first():
            return jsonify({"msg": "Email already in use"}), 400
        d.user.email = data.get("email")
    if data.get("specialization") is not None:
        d.specialization = data.get("specialization")
    if data.get("department_id") is not None:
        d.department_id = data.get("department_id")
    db.session.commit()
    return jsonify({"msg": "Doctor updated successfully"}), 200


@admin_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
@role_required([UserRole.ADMIN])
def delete_doc(doctor_id):
    d =Doctor.query.get_or_404(doctor_id)
    db.session.delete(d)
    user = User.query.get(doctor_id)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "Doctor deleted successfully"}), 200


@admin_bp.route("/departments", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_dept():
    dept = Department.query.all()

    return jsonify([{"id": x.id, "name": x.name,
                     "description": x.description} for x in dept]), 200

@admin_bp.route("/departments", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def create_dept():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"msg": "Missing required fields"}), 400
    if Department.query.filter_by(name=name).first():
        return jsonify({"msg": "Department with this name already exists"}), 400
    dept = Department(name=name, description=description)
    db.session.add(dept)
    db.session.commit()

    return jsonify({"msg": "Department created successfully", "department_id": dept.id}), 201

@admin_bp.route("/departments/<int:dept_id>", methods=["DELETE"])
@jwt_required()
@role_required([UserRole.ADMIN])
def delete_dept(dept_id):
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({"msg": "Department deleted successfully"}), 200

@admin_bp.route("/patients", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_pats():
    pats = Patient.query.all()
    out = []
    for p in pats:
        out.append({
            "id": p.id,
            "email": p.user.email,
            "name": p.user.name,
            "phone": p.phone
            "dob" : p.dob.isoformat() if p.dob else None
            "gender": p.gender
        })
    return jsonify(out), 200

@admin_bp.route("/patient/<int:patient_id>/history", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def admin_patient_history(patient_id):
    appts = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_time.desc()).all()
    assigned = Appointment.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if not assigned:
        return jsonify({"msg": "Unauthorized"}), 403
    
    appts = Appointment.query.filter_by(patient_id = patient_id).order_by(Appointment.start_time.desc()).all()
    phist = []
    for a in appts:
        phist.append({
            "appointment": {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "start_time": a.start_time.isoformat(),
                "end_time": a.end_time.isoformat(),
                "status": a.status,
                "problem": a.problem
            },
            "treatment": {
                "id": a.treatment.id if a.treatment else None,
                "diagnosis": a.treatment.diagnosis if a.treatment else None,
                "prescription": a.treatment.prescription if a.treatment else None,
                "notes": a.treatment.notes if a.treatment else None,
            }
        })
    return jsonify({"history": phist}), 200

@admin_bp.route("/appointments/export/<int:doctor_id>", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def enqueue_export(doctor_id):
    task = export_appointments_csv.delay(doctor_id)
    return jsonify({"task_id": task.id}), 202

@admin_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def task_status(task_id):
    res = AsyncResult(task_id)
    return jsonify({"id": task_id, "status": res.status, "result": res.result}), 200