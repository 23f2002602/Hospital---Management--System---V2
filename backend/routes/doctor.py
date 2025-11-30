# backend/routes/doctor.py
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import *
from database import db
from backend.utils.utils import role_required
from datetime import datetime, date, timedelta, time as dt_time
from extensions import cache
from backend.utils.cache_utils import cache_response
from backend.utils.redis_utils import bump_namespace, get_namespace_version
import io, csv

doctor_bp = Blueprint("doctor_bp", __name__)

def _avail_cache_key(doctor_id: int):
    v = get_namespace_version(f"ns:doctor:{doctor_id}:availability_version")
    return f"doctor:{doctor_id}:availability:v={v}"

def _avail_next7_key(doctor_id: int):
    v = get_namespace_version(f"ns:doctor:{doctor_id}:availability_version")
    return f"doctor:{doctor_id}:availability:next7:v={v}"

def _doctor_id_from_token():
    ident = get_jwt_identity()
    try:
        return int(ident)
    except Exception:
        return ident

# APPOINTMENTS LIST
@doctor_bp.route("/appointments", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def list_appointments():
    doctor_id = _doctor_id_from_token()
    q = Appointment.query.filter_by(doctor_id=doctor_id)

    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)

    upcoming = request.args.get("upcoming")
    if upcoming and upcoming.lower() in ("1", "true", "yes"):
        q = q.filter(Appointment.status == "booked")

    q = q.order_by(Appointment.start_time.asc())
    appts = q.all()
    result = []
    for a in appts:
        result.append({
            "id": a.id,
            "patient_id": a.patient_id,
            "patient_name": getattr(a.patient.user, "name", None) if a.patient and a.patient.user else "Unknown",
            "start_time": a.start_time.isoformat() if a.start_time else None,
            "end_time": a.end_time.isoformat() if a.end_time else None,
            "date": a.date.isoformat() if a.date else None,
            "status": a.status,
            "problem": a.problem
        })
    return jsonify(result), 200

# TREATMENT
@doctor_bp.route("/appointments/<int:appt_id>/treatment", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def treatment(appt_id):
    doctor_id = _doctor_id_from_token()
    data = request.get_json() or {}

    diagnosis = data.get("diagnosis", "")
    prescription = data.get("prescription", "")
    notes = data.get("notes", "")

    if not prescription:
        return jsonify({"msg": "Missing required fields: prescription"}), 400

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor_id:
        return jsonify({"msg": "Unauthorized"}), 403
    if appt.status == "completed":
        return jsonify({"msg":"already completed"}), 400

    if appt.treatment:
        return jsonify({"msg": "Treatment already recorded for this appointment"}), 400

    try:
        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        appt.status = "completed"
        db.session.add(treatment)
        db.session.add(appt)
        db.session.commit()

        try:
            bump_namespace(f"ns:doctor:{doctor_id}:availability_version")
        except Exception:
            current_app.logger.exception("Failed to bump availability namespace after treatment")

        return jsonify({"msg": "Treatment recorded successfully and appointment completed"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to save treatment", "error": str(e)}), 500

# CANCEL APPOINTMENT
@doctor_bp.route("/appointments/<int:appt_id>/cancel", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def cancel_appointment(appt_id):
    doctor_id = _doctor_id_from_token()
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor_id:
        return jsonify({"msg": "Unauthorized"}), 403
    if appt.status == "completed":
        return jsonify({"msg":"cannot cancel completed appointment"}), 400

    appt.status = "cancelled"
    db.session.add(appt)
    db.session.commit()

    try:
        bump_namespace(f"ns:doctor:{doctor_id}:availability_version")
    except Exception:
        current_app.logger.exception("Failed to bump availability namespace after cancel")

    return jsonify({"msg": "Appointment cancelled successfully"}), 200

# PATIENT LIST & HISTORY
@doctor_bp.route("/patients", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def list_patients():
    doctor_id = _doctor_id_from_token()
    qstr = request.args.get("q", "").strip()
    try:
        page = int(request.args.get("page", "1"))
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get("per_page", "20"))
    except Exception:
        per_page = 20

    patient_ids_subq = (
        db.session.query(Appointment.patient_id)
        .filter_by(doctor_id=doctor_id)
        .distinct()
        .subquery()
    )

    patient_q = Patient.query.filter(Patient.id.in_(patient_ids_subq))

    if qstr:
        patient_q = patient_q.join(User)
        ilike_term = f"%{qstr.lower()}%"
        patient_q = patient_q.filter(
            db.or_(
                db.func.lower(User.name).like(ilike_term),
                db.func.lower(User.email).like(ilike_term),
            )
        )

    total = patient_q.count()

    patients = (
        patient_q
        .order_by(Patient.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    plist = []
    for p in patients:
        dob = getattr(p, "dob", None) or getattr(p, "date_of_birth", None)
        phone = getattr(p, "phone", None) or getattr(p, "contact_number", None)
        plist.append({
            "id": p.id,
            "name": p.user.name if p.user else None,
            "email": p.user.email if p.user else None,
            "date_of_birth": dob.isoformat() if dob else None,
            "gender": getattr(p, "gender", None),
            "contact_number": phone
        })

    return jsonify({"total": total, "page": page, "per_page": per_page, "patients": plist}), 200

@doctor_bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def patient_history(patient_id):
    doctor_id = _doctor_id_from_token()
    assigned = Appointment.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if not assigned:
        return jsonify({"msg": "Unauthorized"}), 403

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

# AVAILABILITY (cached)
@doctor_bp.route("/availability/next", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
@cache_response(cache,
    key_func=lambda *a, **k: _avail_next7_key(int(get_jwt_identity())),
    ttl_getter=lambda: current_app.config.get("AVAILABILITY_CACHE_TTL", 300)
)
def next_available_slot():
    doctor_id = _doctor_id_from_token()
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
    return result, 200

@doctor_bp.route("/availability/week", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def set_weekly_availability():
    doctor_id = _doctor_id_from_token()
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
        current_app.logger.exception("Failed to bump availability namespace after weekly update")

    return jsonify({"msg":"weekly availability updated"}), 200

@doctor_bp.route("/availability/override", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def set_override():
    doctor_id = _doctor_id_from_token()
    data = request.get_json() or {}
    date_s = data.get("date")
    if not date_s:
        return jsonify({"msg":"date required"}), 400
    try:
        dobj = date.fromisoformat(date_s)
    except Exception:
        return jsonify({"msg":"invalid date format"}), 400
    is_avail = bool(data.get("is_available", False))
    existing = DoctorAvailabilityOverride.query.filter_by(doctor_id=doctor_id, date=dobj).first()
    if existing:
        existing.is_available = is_avail
    else:
        db.session.add(DoctorAvailabilityOverride(doctor_id=doctor_id, date=dobj, is_available=is_avail))
    db.session.commit()

    try:
        bump_namespace(f"ns:doctor:{doctor_id}:availability_version")
    except Exception:
        current_app.logger.exception("Failed to bump availability namespace after override update")

    return jsonify({"msg":"override saved"}), 200

# EXPORT (CSV) - UPDATED TO INCLUDE DETAILS
@doctor_bp.route("/appointments/export", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def export_appointments_csv():
    doctor_id = _doctor_id_from_token()
    appts = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_time).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Updated Headers
    writer.writerow(["ID","Patient ID","Patient Name","Date","Start Time","End Time","Status","Problem", "Diagnosis", "Prescription", "Notes"])
    
    for a in appts:
        writer.writerow([
            a.id,
            a.patient_id,
            a.patient.user.name if a.patient and a.patient.user else "Unknown",
            a.date.isoformat() if a.date else "",
            a.start_time.strftime("%H:%M") if a.start_time else "",
            a.end_time.strftime("%H:%M") if a.end_time else "",
            a.status,
            a.problem or "",
            # Treatment Details
            a.treatment.diagnosis if a.treatment else "",
            a.treatment.prescription if a.treatment else "",
            a.treatment.notes if a.treatment else ""
        ])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     download_name=f"doctor_appointments.csv",
                     as_attachment=True)