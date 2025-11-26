from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Appointment, Doctor, Treatment, UserRole
from database import db
from utils import role_required
from datetime import datetime

doctor_bp = Blueprint("doctor_bp", __name__)

@doctor_bp.route("/appointments", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def get_appointments():
    doctor_id = get_jwt_identity()
    appo = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_time).all()
    result = []
    for a in appo:
        result.append({
            "id": a.id,
            "patient_id": a.patient_id,
            "start_time": a.start_time.isoformat(),
            "end_time": a.end_time.isoformat(),
            "date": a.date.isoformat(),
            "status": a.status
        })
    return jsonify(result), 200

@doctor_bp.route("/appointments/<int:appo_id>/treatement", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def treatement(appo_id):
    data = request.get_json() or {}
    diagnosis = data.get("diagnosis", "")
    prescription = data.get("prescription")

    if not prescription:
        return jsonify({"msg": "Missing required fields"}), 400

    appo = Appointment.query.get(appo_id)
    if not appo:
        return jsonify({"msg": "Appointment not found"}), 404

    appo.status = "completed"
    db.session.add(appo)

    if appo.treatment:
        return jsonify({"msg": "Treatment already recorded for this appointment"}), 400

    treatment = Treatment(
        appointment_id=appo_id,
        diagnosis=diagnosis,
        prescription=prescription,
        treated_at=datetime.utcnow()
    )
    db.session.add(treatment)
    db.session.commit()

    return jsonify({"msg": "Treatment recorded successfully and appointment completed"}), 201