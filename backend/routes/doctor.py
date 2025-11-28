from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import *
from database import db
from utils import role_required
from datetime import datetime, date, timedelta, time
import io, csv

doctor_bp = Blueprint("doctor_bp", __name__)

#----------#

def _doctor_id_from_token():
    return get_jwt_identity()

# ---------- APPOINTMENTS ---------- #

@doctor_bp.route("/appointments", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def list_appointments():
    doctor_id = _doctor_id_from_token()
    q = Appointment.query.filter_by(doctor_id=doctor_id)
    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)
    frm = request.args.get("from")
    to = request.args.get("to")
    if frm:
        try:
            frm_date = datetime.fromisoformat(frm)
            q = q.filter(Appointment.date >= frm_date)
        except:
            pass
    if to:
        try:
            to_date = datetime.fromisoformat(to)
            q = q.filter(Appointment.date <= to_date)
        except:
            pass
    upcoming = request.args.get("upcoming")
    if upcoming and upcoming.lower() in ("1", "true", "yes"):
        q = q.filter(Appointment.start_time >= datetime)

    q = q.order_by(Appointment.start_time.asc())
    appts = q.all()
    result = []
    for a in appts:
        result.append({
            "id": a.id,
            "patient_id": a.patient_id,
            "patient_name": getattr(a.patient.user, "name", None),
            "start_time": a.start_time.isoformat(),
            "end_time": a.end_time.isoformat(),
            "date": a.date.isoformat(),
            "status": a.status
            "problem": a.problem
        })
    return jsonify(result), 200

# ------------------------------------------- #

@doctor_bp.route("/appointments/<int:appt_id>/treatement", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def treatement(appt_id):
    doctor_id = _doctor_id_from_token()
    data = request.get_json() or {}

    diagnosis = data.get("diagnosis", "")
    prescription = data.get("prescription")
    if not prescription:
        return jsonify({"msg": "Missing required fields"}), 400

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor_id:
        return jsonify({"msg": "Unauthorized"}), 403
    if appt.status == "completed":
        return jsonify({"msg":"already completed"}), 400
    
    appt.status = "completed"
    db.session.add(appt)

    if appt.treatment:
        return jsonify({"msg": "Treatment already recorded for this appointment"}), 400

    treatment = Treatment(
        appointment_id=appt.id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes = data.get("notes","")
    )
    db.session.add(treatment)
    db.session.commit()

    return jsonify({"msg": "Treatment recorded successfully and appointment completed"}), 201

# ------------------------------- #

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
    
    appt.status = "canceled"
    db.session.add(appt)
    db.session.commit()

    return jsonify({"msg": "Appointment canceled successfully"}), 200

# ---------- PATIENT LIST AND HISTORY ----------- #

@doctor_bp.route("/patients", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def list_patients():
    doctor_id = _doctor_id_from_token()
    """
        List distinct patients assigned to this doctor (via appointments).
        Query params:
        - q: search name/email
        - page: page number (1-based)
        - per_page: items per page (default 20, max 100)
        Returns JSON: { total, page, per_page, total_pages, patients: [...] }
    """
    qstr = request.args.get("q", "").strip()
    try:
        page = int(request.arges.get("page", "1"))
    except(TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", "20"))
    except(TypeError, ValueError):
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
        plist.append({
            "id": p.id,
            "name": p.user.name,
            "email": p.user.email,
            "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
            "gender": p.gender,
            "contact_number": p.contact_number
        })

    return jsonify({"total": total, "page": page, "per_page": per_page, "patients": plist}), 200

# ------------------------------------------- #

@doctor_bp.route("/patients/<int:patient_id>/history", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def patient_history(patient_id):
    doctor_id = _doctor_id_from_token()

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

# -----------------AVAILABILITY------------------------ #

@doctor_bp.route("/availability/next", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def next_available_slot():
    """
    Return combined availability for next 7 days:
      - consult weekly availability entries (DoctorAvailability)
      - consult overrides (DoctorAvailabilityOverride)
    Output: { date: YYYY-MM-DD, day: Monday, is_available: bool, start_time, end_time }
    """

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
                start = wa.start_time.isoformat() if wa.start_time else None
                end = wa.end_time.isoformat() if wa.end_time else None
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

#------------------------------------------- #

@doctor_bp.route("/availability/week", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def set_weekly_availability():
    """
    Accepts list of availability objects:
    [{ "day_of_week":"Monday","start_time":"09:00","end_time":"12:00","is_available":true }, ...]
    This will upsert entries for the doctor for those days.
    """
    doctor_id = _doctor_id_from_token()
    data = request.get_json() or []
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        return jsonify({"msg": "entries list required"}), 400
    
    for entry in entries:
        day = entry.get("day_of_week")
        if not day:
            continue
        start = entry.get("start_time")
        end = entry.get("end_time")
        is_avail = entry.get("is_available", False)
        
        st = None
        et = None
        try:
            if start:
                h,m = map(int, start.split(":"))
                st = time(hour=h, minute=m)
            if end:
                h,m = map(int, end.split(":"))
                en = time(hour=h, minute=m)
        except:
            continue
        existing = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day_of_week=day).first()
        if existing:
            existing.start_time = st
            existing.end_time = en
            existing.is_available = is_avail
        else:
            na = DoctorAvailability(doctor_id=doctor_id, day_of_week=day, start_time=st, end_time=en, is_available=is_avail)
            db.session.add(na)
    db.session.commit()
    return jsonify({"msg":"weekly availability updated"}), 200

#------------------------------------------- #

@doctor_bp.route("/availability/override", methods=["POST"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def set_overrine():
    doctor_id = _doctor_id_from_token()
    data = request.get_json() or {}
    date_s = data.get("date")
    if not date_s:
        return jsonify({"msg":"date required"}), 400
    try:
        dobj = date.fromisoformat(date_s)
    except:
        return jsonify({"msg":"invalid date format"}), 400
    is_avail = bool(data.get("is_available", False))
    existing = DoctorAvailabilityOverride.query.filter_by(doctor_id=doctor_id, date=dobj).first()
    if existing:
        existing.is_available = is_avail
    else:
        db.session.add(DoctorAvailabilityOverride(doctor_id=doctor_id, date=dobj, is_available=is_avail))
    db.session.commit()
    return jsonify({"msg":"override saved"}), 200

# ---------- export (CSV) and notifications (stubs) ----------

@doctor_bp.route("/appointments/export", methods=["GET"])
@jwt_required()
@role_required([UserRole.DOCTOR])
def export_appointments_csv():
    doctor_id = _doctor_id_from_token()
    appts = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_time).all()
    # create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","patient_id","patient_name","start_time","end_time","status","problem"])
    for a in appts:
        writer.writerow([a.id, a.patient_id, a.patient.user.name if a.patient and a.patient.user else "", a.start_time.isoformat(), a.end_time.isoformat(), a.status, a.problem or ""])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")), mimetype="text/csv",
                     download_name=f"appointments_doctor_{doctor_id}.csv", as_attachment=True)