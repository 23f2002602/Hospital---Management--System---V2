from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Doctor, Appointment, Patient, UserRole
from database import db
from utils import role_required
from datetime import datetime

patient_bp = Blueprint("patient_bp", __name__)

@patient_bp.route("/doctors", methods=["GET"])
@jwt_required()
@role_required([UserRole.PATIENT])
def show_doctors():
    docs = Doctor.query.all()
    out = [{"id": d.id,
            "name": d.user.name,
            "specialization": d.specialization} for d in docs]
    return jsonify(out), 200

@patient_bp.route("/book", methods=["POST"])
@jwt_required()
@role_required([UserRole.PATIENT])
def book():
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    date = data.get("date")
    start = data.get("start_time")
    end = data.get("end_time")
    problem = data.get("problem", "")

    if not doctor_id or not date or not start or not end:
        return jsonify({"msg": "Missing required fields"}), 400
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    conflict = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "booked",
        Appointment.start_time < end_dt,
        Appointment.end_time > start_dt
    ).first()
    if conflict:
        return jsonify({"msg": "The selected time slot is not available"}), 409
    
    identity = get_jwt_identity()
    patient_id = identity["id"]
    appo = Appointment(doctor_id=doctor_id, 
                       patient_id=patient_id, 
                       date = date,
                       start_time=start, 
                       end_time=end, 
                       problem=problem)
    db.session.add(appo)
    db.session.commit()

    return jsonify({"msg": "Appointment booked successfully", "appointment_id": appo.id}), 201

