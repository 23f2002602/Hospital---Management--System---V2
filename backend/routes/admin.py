# backend/routes/admin.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required
from database import db
from models import *
from utils import role_required
from tasks import export_appointments_csv
from celery.result import AsyncResult
from redis_utils import bump_namespace
# Added imports for availability logic
from datetime import datetime, date, timedelta, time as dt_time

admin_bp = Blueprint("admin_bp", __name__)

# ... [KEEP EXISTING ROUTES: create_doctor, list_doctors, get_doc, update_doc, delete_doc, etc.] ...
# ... [Paste the existing routes here or keep them as is] ...

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

    user = User(
        email=email,
        password=generate_password_hash(password),
        name=name,
        role=UserRole.DOCTOR
    )
    db.session.add(user)
    db.session.commit()

    doc = Doctor(id=user.id, specialization=specialization, department_id=department_id)
    db.session.add(doc)
    db.session.commit()

    try:
        bump_namespace("ns:doctors_search_version")
    except Exception:
        current_app.logger.exception("Failed to bump doctors search version after create_doctor")

    return jsonify({"msg": "Doctor created successfully", "doctor_id": doc.id}), 201

@admin_bp.route("/doctors", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_doctors():
    doctors = Doctor.query.all()
    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "name": doc.user.name if doc.user else None,
            "email": doc.user.email if doc.user else None,
            "specialization": doc.specialization,
            "department_id": doc.department_id 
        })
    return jsonify(result), 200

@admin_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def get_doc(doctor_id):
    d = Doctor.query.get_or_404(doctor_id)
    return jsonify({
        "id": d.id,
        "name": d.user.name if d.user else None,
        "email": d.user.email if d.user else None,
        "specialization": d.specialization,
        "department_id": d.department_id
    }), 200

@admin_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
@role_required([UserRole.ADMIN])
def update_doc(doctor_id):
    d = Doctor.query.get_or_404(doctor_id)
    data = request.get_json() or {}

    if data.get("name") is not None and d.user:
        d.user.name = data.get("name")
    if data.get("email") is not None and d.user:
        new_email = data.get("email")
        if User.query.filter(User.email == new_email, User.id != d.id).first():
            return jsonify({"msg": "Email already in use"}), 400
        d.user.email = new_email
    if data.get("specialization") is not None:
        d.specialization = data.get("specialization")
    if data.get("department_id") is not None:
        d.department_id = data.get("department_id")
    db.session.commit()

    try:
        bump_namespace("ns:doctors_search_version")
    except Exception:
        current_app.logger.exception("Failed to bump doctors search version after update_doc")

    return jsonify({"msg": "Doctor updated successfully"}), 200

@admin_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
@role_required([UserRole.ADMIN])
def delete_doc(doctor_id):
    d = Doctor.query.get_or_404(doctor_id)
    
    # Check for existing appointments to prevent IntegrityError
    if Appointment.query.filter_by(doctor_id=doctor_id).first():
        return jsonify({"msg": "Cannot delete doctor with existing appointments."}), 400

    user = User.query.get(doctor_id)
    try:
        db.session.delete(d)
        if user:
            db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg":"Failed to delete doctor","error":str(e)}), 500

    try:
        bump_namespace("ns:doctors_search_version")
    except Exception:
        current_app.logger.exception("Failed to bump doctors search version after delete_doc")

    return jsonify({"msg": "Doctor deleted successfully"}), 200

@admin_bp.route("/departments", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_dept():
    dept = Department.query.all()
    return jsonify([{"id": x.id, "name": x.name, "description": x.description} for x in dept]), 200

@admin_bp.route("/departments", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def create_dept():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"msg":"Missing required fields"}), 400
    if Department.query.filter_by(name=name).first():
        return jsonify({"msg":"Department with this name already exists"}), 400
    dept = Department(name=name, description=description)
    db.session.add(dept)
    db.session.commit()
    return jsonify({"msg":"Department created successfully","department_id":dept.id}), 201

@admin_bp.route("/departments/<int:dept_id>", methods=["DELETE"])
@jwt_required()
@role_required([UserRole.ADMIN])
def delete_dept(dept_id):
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({"msg":"Department deleted successfully"}), 200

@admin_bp.route("/patients", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def list_pats():
    pats = Patient.query.all()
    out = []
    for p in pats:
        out.append({
            "id": p.id,
            "email": p.user.email if p.user else None,
            "name": p.user.name if p.user else None,
            "phone": p.phone,
            "dob": p.dob.isoformat() if getattr(p, "dob", None) else None,
            "gender": p.gender
        })
    return jsonify(out), 200

@admin_bp.route("/patient/<int:patient_id>/history", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def admin_patient_history(patient_id):
    appts = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_time.desc()).all()
    phist = []
    for a in appts:
        phist.append({
            "appointment": {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "start_time": a.start_time.isoformat() if a.start_time else None,
                "end_time": a.end_time.isoformat() if a.end_time else None,
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

# --- NEW: Availability Routes for Admin ---

@admin_bp.route("/doctors/<int:doctor_id>/availability/next", methods=["GET"])
@jwt_required()
@role_required([UserRole.ADMIN])
def get_doctor_availability_next(doctor_id):
    weekly = {a.day_of_week: a for a in DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()}
    overrides = {ov.date: ov for ov in DoctorAvailabilityOverride.query.filter_by(doctor_id=doctor_id).all()}

    result = []
    today = date.today()
    for i in range(7):
        d = today + timedelta(days=i)
        weekday = d.strftime("%A")
        ov = overrides.get(d)
        if ov is not None:
            is_avail = ov.is_available
            start = None
            end = None
        else:
            wa = weekly.get(weekday)
            if wa and wa.is_available:
                is_avail = True
                start = wa.start_time.strftime("%H:%M") if wa.start_time else None
                end = wa.end_time.strftime("%H:%M") if wa.end_time else None
            else:
                is_avail = False
                start = None
                end = None
        result.append({
            "date": d.isoformat(),
            "day": weekday,
            "is_available": is_avail,
            "start_time": start,
            "end_time": end
        })
    return jsonify(result), 200

@admin_bp.route("/doctors/<int:doctor_id>/availability/week", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def set_doctor_weekly_availability(doctor_id):
    data = request.get_json() or {}
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        return jsonify({"msg":"entries list required"}), 400

    for ent in entries:
        day = ent.get("day_of_week")
        if not day:
            continue
        start = ent.get("start_time")
        end = ent.get("end_time")
        is_avail = bool(ent.get("is_available", True))

        st = None
        en = None
        try:
            if start:
                pts = list(map(int, start.split(":")))
                st = dt_time(hour=pts[0], minute=pts[1])
            if end:
                pts = list(map(int, end.split(":")))
                en = dt_time(hour=pts[0], minute=pts[1])
        except Exception:
            continue
        
        # Check start < end
        if st and en and st >= en:
             return jsonify({"msg": "Start time must be before end time"}), 400

        entry = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=day).first()
        if entry:
            entry.start_time = st
            entry.end_time = en
            entry.is_available = is_avail
        else:
            entry = DoctorAvailability(doctor_id=doctor_id, day_of_week=day, start_time=st, end_time=en, is_available=is_avail)
            db.session.add(entry)

    db.session.commit()

    try:
        bump_namespace(f"ns:doctor:{doctor_id}:availability_version")
    except Exception:
        current_app.logger.exception("Failed to bump availability namespace")

    return jsonify({"msg":"Weekly availability updated"}), 200