from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import role_required
from database import db
from models import Appointment, Doctor, User, Patient
from datetime import datetime, date
import io, csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from sqlalchemy import func

reports_bp = Blueprint("reports_bp", __name__)

def _current_user_id():
    try:
        return int(get_jwt_identity())
    except:
        return get_jwt_identity()

def _month_range(ym: str):
    start = datetime.strptime(ym + "-01", "%Y-%m-%d").date()
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end

@reports_bp.route("/monthly/json", methods=["GET"])
@jwt_required()
@role_required(["admin","doctor"])
def monthly_json():
    # JSON Endpoint: Returns Summary Stats for Frontend Charts
    month = request.args.get("month")
    if not month:
        return jsonify({"msg":"month required (YYYY-MM)"}), 400
    try:
        start, end = _month_range(month)
    except Exception:
        return jsonify({"msg":"invalid month format"}), 400

    user_id = _current_user_id()
    doctor_id = request.args.get("doctor_id")

    q = db.session.query(func.date(Appointment.start_time).label("d"), func.count(Appointment.id).label("c")) \
        .filter(Appointment.start_time >= start, Appointment.start_time < end)

    if doctor_id:
        q = q.filter(Appointment.doctor_id == int(doctor_id))
    else:
        if Doctor.query.get(user_id):
            q = q.filter(Appointment.doctor_id == user_id)

    q = q.group_by(func.date(Appointment.start_time)).order_by(func.date(Appointment.start_time))
    rows = q.all()

    spec_q = db.session.query(Doctor.specialization, func.count(Appointment.id)) \
        .join(Appointment, Appointment.doctor_id == Doctor.id) \
        .filter(Appointment.start_time >= start, Appointment.start_time < end)

    if doctor_id:
        spec_q = spec_q.filter(Doctor.id == int(doctor_id))
    else:
        if Doctor.query.get(user_id):
            spec_q = spec_q.filter(Doctor.id == user_id)

    spec_q = spec_q.group_by(Doctor.specialization)
    spec_rows = spec_q.all()

    return jsonify({
        "by_date": [{"date": str(r.d), "count": r.c} for r in rows],
        "by_specialization": [{"specialization": s[0] or "Unknown", "count": s[1]} for s in spec_rows]
    }), 200

@reports_bp.route("/monthly/csv", methods=["GET"])
@jwt_required()
@role_required(["admin","doctor"])
def monthly_csv():
    # CSV Endpoint: Returns Detailed Records (Best for Excel analysis)
    month = request.args.get("month")
    if not month:
        return jsonify({"msg":"month required"}), 400
    try:
        start, end = _month_range(month)
    except Exception:
        return jsonify({"msg":"invalid month"}), 400

    user_id = _current_user_id()
    doctor_id = request.args.get("doctor_id")

    q = Appointment.query.filter(Appointment.start_time >= start, Appointment.start_time < end)

    if doctor_id:
        q = q.filter(Appointment.doctor_id == int(doctor_id))
    else:
        if Doctor.query.get(user_id):
            q = q.filter(Appointment.doctor_id == user_id)

    appts = q.order_by(Appointment.start_time).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Time", "Patient Name", "Doctor Name", "Status", "Diagnosis", "Prescription"])
    
    for a in appts:
        p_name = a.patient.user.name if a.patient and a.patient.user else "Unknown"
        d_name = a.doctor.user.name if a.doctor and a.doctor.user else "Unknown"
        diag = a.treatment.diagnosis if a.treatment else ""
        rx = a.treatment.prescription if a.treatment else ""
        
        writer.writerow([
            a.start_time.date() if a.start_time else "",
            a.start_time.strftime("%H:%M") if a.start_time else "",
            p_name,
            d_name,
            a.status,
            diag,
            rx
        ])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     download_name=f"monthly_report_{month}_detailed.csv",
                     as_attachment=True)

@reports_bp.route("/monthly/pdf", methods=["GET"])
@jwt_required()
@role_required(["admin","doctor"])
def monthly_pdf():
    # PDF Endpoint: COMBINED (Summary Page + Detailed Pages)
    month = request.args.get("month")
    if not month:
        return jsonify({"msg":"month required"}), 400
    try:
        start, end = _month_range(month)
    except Exception:
        return jsonify({"msg":"invalid month format"}), 400

    user_id = _current_user_id()
    doctor_id = request.args.get("doctor_id")

    # 1. Fetch Summary Stats
    q_date_stats = db.session.query(func.date(Appointment.start_time).label("d"), func.count(Appointment.id).label("c")) \
        .filter(Appointment.start_time >= start, Appointment.start_time < end)
    
    q_spec_stats = db.session.query(Doctor.specialization, func.count(Appointment.id)) \
        .join(Appointment, Appointment.doctor_id == Doctor.id) \
        .filter(Appointment.start_time >= start, Appointment.start_time < end)

    # 2. Fetch Detailed Records
    q_details = Appointment.query.filter(Appointment.start_time >= start, Appointment.start_time < end)

    if doctor_id:
        q_date_stats = q_date_stats.filter(Appointment.doctor_id == int(doctor_id))
        q_spec_stats = q_spec_stats.filter(Doctor.id == int(doctor_id))
        q_details = q_details.filter(Appointment.doctor_id == int(doctor_id))
    else:
        if Doctor.query.get(user_id):
            q_date_stats = q_date_stats.filter(Appointment.doctor_id == user_id)
            q_spec_stats = q_spec_stats.filter(Doctor.id == user_id)
            q_details = q_details.filter(Appointment.doctor_id == user_id)

    date_rows = q_date_stats.group_by(func.date(Appointment.start_time)).all()
    spec_rows = q_spec_stats.group_by(Doctor.specialization).all()
    appts = q_details.order_by(Appointment.start_time).all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 20 * mm
    top = height - 20 * mm

    # ==========================
    # PAGE 1: SUMMARY DASHBOARD
    # ==========================
    p.setFont("Helvetica-Bold", 16)
    p.drawString(left, top, f"HMS Monthly Report — {month}")
    p.setFont("Helvetica", 10)
    p.drawString(left, top - 15, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    
    y = top - 40
    
    # Section: By Date
    p.setFont("Helvetica-Bold", 12)
    p.drawString(left, y, "Daily Summary")
    y -= 15
    p.setFont("Helvetica-Bold", 10)
    p.drawString(left, y, "Date")
    p.drawString(left + 60*mm, y, "Appointments")
    p.setFont("Helvetica", 10)
    y -= 12
    for r in date_rows:
        p.drawString(left, y, str(r.d))
        p.drawString(left + 60*mm, y, str(r.c))
        y -= 12
    
    y -= 10
    
    # Section: By Specialization
    p.setFont("Helvetica-Bold", 12)
    p.drawString(left, y, "By Specialization")
    y -= 15
    p.setFont("Helvetica-Bold", 10)
    for s in spec_rows:
        spec = s[0] or "Unknown"
        cnt = s[1]
        p.drawString(left, y, f"{spec}")
        p.drawString(left + 60*mm, y, str(cnt))
        y -= 12

    # ==========================
    # PAGE 2+: DETAILED LIST
    # ==========================
    p.showPage() 
    y = top # Reset Y to top of new page
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left, y, "Detailed Appointment List")
    y -= 25
    
    # Table Headers
    p.setFont("Helvetica-Bold", 9)
    p.drawString(left, y, "Date/Time")
    p.drawString(left + 35*mm, y, "Patient")
    p.drawString(left + 70*mm, y, "Doctor")
    p.drawString(left + 105*mm, y, "Status")
    p.drawString(left + 130*mm, y, "Diagnosis")
    y -= 15
    p.setFont("Helvetica", 8)

    for a in appts:
        # Check if we need a new page
        if y < 20 * mm:
            p.showPage()
            y = top
            p.setFont("Helvetica", 8)
        
        d_str = a.start_time.strftime("%Y-%m-%d %H:%M") if a.start_time else ""
        p_name = (a.patient.user.name if a.patient and a.patient.user else "Unknown")[:18]
        d_name = (a.doctor.user.name if a.doctor and a.doctor.user else "Unknown")[:18]
        status = a.status
        diag = (a.treatment.diagnosis if a.treatment else "")[:25] # Truncate long text

        p.drawString(left, y, d_str)
        p.drawString(left + 35*mm, y, p_name)
        p.drawString(left + 70*mm, y, d_name)
        p.drawString(left + 105*mm, y, status)
        p.drawString(left + 130*mm, y, diag)
        y -= 12

    p.save()
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", download_name=f"monthly_report_{month}_full.pdf", as_attachment=True)