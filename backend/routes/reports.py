from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import role_required
from database import db
from models import Appointment, Doctor
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
        "by_date": [{"date": r.d.isoformat(), "count": r.c} for r in rows],
        "by_specialization": [{"specialization": s[0] or "Unknown", "count": s[1]} for s in spec_rows]
    }), 200

@reports_bp.route("/monthly/csv", methods=["GET"])
@jwt_required()
@role_required(["admin","doctor"])
def monthly_csv():
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

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date","Appointments"])
    for r in rows:
        writer.writerow([r.d.isoformat(), r.c])
    writer.writerow([])
    writer.writerow(["Specialization","Appointments"])
    for s in spec_rows:
        writer.writerow([s[0] or "Unknown", s[1]])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     download_name=f"monthly_report_{month}.csv",
                     as_attachment=True)

@reports_bp.route("/monthly/pdf", methods=["GET"])
@jwt_required()
@role_required(["admin","doctor"])
def monthly_pdf():
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

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 20 * mm
    top = height - 20 * mm

    p.setFont("Helvetica-Bold", 16)
    p.drawString(left, top, f"HMS Monthly Report — {month}")
    p.setFont("Helvetica", 10)
    p.drawString(left, top - 12, f"Generated: {datetime.utcnow().isoformat()} UTC")

    y = top - 36
    p.setFont("Helvetica-Bold", 11)
    p.drawString(left, y, "Date")
    p.drawString(left + 60*mm, y, "Appointments")
    p.setFont("Helvetica", 10)
    y -= 12
    for r in rows:
        p.drawString(left, y, r.d.isoformat())
        p.drawString(left + 60*mm, y, str(r.c))
        y -= 12
        if y < 40*mm:
            p.showPage()
            y = height - 30*mm

    y -= 8
    p.setFont("Helvetica-Bold", 11)
    p.drawString(left, y, "By Specialization")
    y -= 12
    p.setFont("Helvetica", 10)
    for s in spec_rows:
        spec = s[0] or "Unknown"
        cnt = s[1]
        p.drawString(left, y, f"{spec}")
        p.drawString(left + 60*mm, y, str(cnt))
        y -= 12
        if y < 40*mm:
            p.showPage()
            y = height - 30*mm

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", download_name=f"monthly_report_{month}.pdf", as_attachment=True)
