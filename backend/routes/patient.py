# backend/routes/patient.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import *
from utils import role_required
from datetime import datetime
from sqlalchemy import and_, or_
from extensions import cache
from cache_utils import cache_response
from redis_utils import bump_namespace, get_namespace_version

patient_bp = Blueprint("patient_bp", __name__)

def _patient_id_from_token():
    try:
        return int(get_jwt_identity())
    except Exception:
        return get_jwt_identity()

# Helper: doctor search cache key (namespace versioning)
def _doctor_search_key(q, page, per_page):
    v = get_namespace_version("ns:doctors_search_version")
    qnorm = (q or "").strip().lower()
    return f"doctors:search:v={v}:q={qnorm}:page={page}:per={per_page}"

# ----------------- PROFILE ------------------------ #
@patient_bp.route("/profile", methods=["GET"])
@jwt_required()
@role_required([UserRole.PATIENT])
def get_profile():
    pid = _patient_id_from_token()
    p = Patient.query.get_or_404(pid)
    user = p.user
    return jsonify({
        "id": p.id,
        "name": user.name,
        "email": user.email,
        "phone": p.phone,
        "dob": p.dob.isoformat() if getattr(p, "dob", None) else None,
        "gender": p.gender
    }), 200

@patient_bp.route("/profile", methods=["PUT"])
@jwt_required()
@role_required([UserRole.PATIENT])
def update_profile():
    pid = _patient_id_from_token()
    data = request.get_json() or {}
    p = Patient.query.get_or_404(pid)
    user = p.user
    if data.get("name") is not None:
        user.name = data.get("name")
    if data.get("phone") is not None:
        p.phone = data.get("phone")
    if data.get("dob") is not None:
        try:
            p.dob = datetime.fromisoformat(data.get("dob")).date()
        except Exception:
            return jsonify({"msg":"invalid dob format, use YYYY-MM-DD"}), 400
    if data.get("gender") is not None:
        p.gender = data.get("gender")
    db.session.commit()
    return jsonify({"msg":"profile updated"}), 200

# ----------------- DOCTORS (cached search) ------------------------ #
@patient_bp.route("/doctors", methods=["GET"])
@jwt_required(optional=True)
@cache_response(cache,
    key_func=lambda *a, **k: _doctor_search_key(request.args.get("q",""), request.args.get("page",1), request.args.get("per_page",20)),
    ttl_getter=lambda: current_app.config.get("DOCTOR_SEARCH_CACHE_TTL", 60)
)
def search_doctors():
    q = request.args.get("q","").strip()
    try:
        page = int(request.args.get("page",1))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get("per_page",20))
    except Exception:
        per_page = 20

    query = Doctor.query.join(Doctor.user)
    if q:
        ilike = f"%{q.lower()}%"
        query = query.filter(
            db.or_(
                db.func.lower(User.name).like(ilike),
                db.func.lower(Doctor.specialization).like(ilike),
                db.func.lower(User.email).like(ilike)
            )
        )
    total = query.count()
    docs = query.offset((page-1)*per_page).limit(per_page).all()
    out = []
    for d in docs:
        out.append({
            "id": d.id,
            "name": d.user.name,
            "email": d.user.email,
            "specialization": d.specialization,
            "department_id": d.department_id
        })
    return {"total": total, "page": page, "per_page": per_page, "doctors": out}, 200

# ------------------ BOOKING ---------------------- #
def _is_doctor_available_on(doctor_id:int, start_dt:datetime, end_dt:datetime):
    d = start_dt.date()
    ov = DoctorAvailabilityOverride.query.filter_by(doctor_id=doctor_id, date=d).first()
    if ov:
        if not ov.is_available:
            return False, "Doctor not available (override)"

    weekday = start_dt.strftime("%A")
    wa = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=weekday).first()
    if not wa or not wa.is_available:
        return False, "Doctor not available on this weekday"

    if wa.start_time and wa.end_time:
        st = wa.start_time
        en = wa.end_time
        if not (st <= start_dt.time() and end_dt.time() <= en):
            return False, "Requested time outside doctor's working hours"

    overlapping = Appointment.query.filter(
        Appointment.doctor_id==doctor_id,
        Appointment.status=="booked",
        db.or_(
            db.and_(Appointment.start_time <= start_dt, Appointment.end_time > start_dt),
            db.and_(Appointment.start_time < end_dt, Appointment.end_time >= end_dt),
            db.and_(Appointment.start_time >= start_dt, Appointment.end_time <= end_dt)
        )
    ).first()
    if overlapping:
        return False, "Time slot already booked"
    return True, "available"

@patient_bp.route("/appointments/book", methods=["POST"])
@jwt_required()
@role_required([UserRole.PATIENT])
def book_appointment():
    pid = _patient_id_from_token()
    data = request.get_json() or {}
    doctor_id = data.get("doctor_id")
    start_s = data.get("start_time")
    end_s = data.get("end_time")
    problem = data.get("problem", "")

    if not doctor_id or not start_s or not end_s:
        return jsonify({"msg":"doctor_id, start_time and end_time required"}), 400
    try:
        start_dt = datetime.fromisoformat(start_s)
        end_dt = datetime.fromisoformat(end_s)
    except Exception:
        return jsonify({"msg":"invalid datetime format, use ISO format"}), 400

    if end_dt <= start_dt:
        return jsonify({"msg":"end_time must be after start_time"}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"msg":"doctor not found"}), 404

    ok, msg = _is_doctor_available_on(doctor_id, start_dt, end_dt)
    if not ok:
        return jsonify({"msg": msg}), 400

    try:
        with db.session.begin():
            overlap_filter = and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status == "booked",
                or_(
                    and_(Appointment.start_time <= start_dt, Appointment.end_time > start_dt),
                    and_(Appointment.start_time < end_dt, Appointment.end_time >= end_dt),
                    and_(Appointment.start_time >= start_dt, Appointment.end_time <= end_dt)
                )
            )

            overlapping_q = Appointment.query.filter(overlap_filter)
            try:
                overlapping = overlapping_q.with_for_update(nowait=False).first()
            except Exception:
                overlapping = overlapping_q.first()

            if overlapping:
                return jsonify({"msg":"Time slot already booked"}), 400

            appt = Appointment(
                doctor_id = doctor_id,
                patient_id = pid,
                start_time = start_dt,
                end_time = end_dt,
                status = "booked",
                problem = problem,
                date = start_dt.date()
            )
            db.session.add(appt)
            db.session.flush()
            appt_id = appt.id

        # bump availability namespace for this doctor
        try:
            bump_namespace(f"ns:doctor:{doctor_id}:availability_version")
        except Exception:
            current_app.logger.exception("Failed to bump availability namespace after booking")

        return jsonify({"msg":"appointment booked", "appointment_id": appt_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg":"booking failed", "error": str(e)}), 500

@patient_bp.route("/appointments/<int:appt_id>/reschedule", methods=["POST"])
@jwt_required()
@role_required([UserRole.PATIENT])
def reschedule_appointment(appt_id):
    pid = _patient_id_from_token()
    data = request.get_json() or {}
    start_s = data.get("start_time")
    end_s = data.get("end_time")

    if not start_s or not end_s:
        return jsonify({"msg":"start_time and end_time required"}), 400
    try:
        start_dt = datetime.fromisoformat(start_s)
        end_dt = datetime.fromisoformat(end_s)
    except Exception:
        return jsonify({"msg":"invalid datetime format"}), 400

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != pid:
        return jsonify({"msg":"forbidden"}), 403
    if appt.status != "booked":
        return jsonify({"msg":"only booked appointments can be rescheduled"}), 400

    ok, msg = _is_doctor_available_on(appt.doctor_id, start_dt, end_dt)
    if not ok:
        return jsonify({"msg":msg}), 400

    try:
        with db.session.begin():
            overlap_filter = and_(
                Appointment.doctor_id == appt.doctor_id,
                Appointment.status == "booked",
                Appointment.id != appt.id,
                or_(
                    and_(Appointment.start_time <= start_dt, Appointment.end_time > start_dt),
                    and_(Appointment.start_time < end_dt, Appointment.end_time >= end_dt),
                    and_(Appointment.start_time >= start_dt, Appointment.end_time <= end_dt)
                )
            )

            overlapping_q = Appointment.query.filter(overlap_filter)
            try:
                overlapping = overlapping_q.with_for_update(nowait=False).first()
            except Exception:
                overlapping = overlapping_q.first()

            if overlapping:
                return jsonify({"msg":"Time slot already booked"}), 400

            appt.start_time = start_dt
            appt.end_time = end_dt
            appt.date = start_dt.date()
            db.session.add(appt)
            db.session.flush()

        # bump availability namespace for this doctor
        try:
            bump_namespace(f"ns:doctor:{appt.doctor_id}:availability_version")
        except Exception:
            current_app.logger.exception("Failed to bump availability namespace after reschedule")

        return jsonify({"msg":"appointment rescheduled"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg":"reschedule failed", "error": str(e)}), 500

@patient_bp.route("/appointments/<int:appt_id>/cancel", methods=["POST"])
@jwt_required()
@role_required([UserRole.PATIENT])
def cancel_appointment(appt_id):
    pid = _patient_id_from_token()
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != pid:
        return jsonify({"msg":"forbidden"}), 403
    if appt.status in ("cancelled", "completed"):
        return jsonify({"msg":"cannot cancel"}), 400
    appt.status = "cancelled"
    db.session.add(appt)
    db.session.commit()

    # bump availability namespace
    try:
        bump_namespace(f"ns:doctor:{appt.doctor_id}:availability_version")
    except Exception:
        current_app.logger.exception("Failed to bump availability namespace after cancel")

    return jsonify({"msg":"appointment cancelled"}), 200

@patient_bp.route("/appointments/history", methods=["GET"])
@jwt_required()
@role_required([UserRole.PATIENT])
def patient_full_history():
    pid = _patient_id_from_token()
    appts = Appointment.query.filter_by(patient_id=pid).order_by(Appointment.start_time.desc()).all()
    phist = []
    for a in appts:
        phist.append({
            "appointment": {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "doctor_name": a.doctor.user.name if a.doctor and a.doctor.user else None,
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
                "created_at": a.treatment.created_at.isoformat() if a.treatment and getattr(a.treatment, "created_at", None) else None
            }
        })
    return jsonify({"history": phist}), 200
