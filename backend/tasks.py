from celery_app import make_celery
from flask import current_app
from app import create_app, make_celery
from database import db
from models import Appointment, User
import csv, io
from datetime import datetime, timedelta

app = create_app()
celery = make_celery(app)

@celery.task(bind=True)
def export_appointments_csv(self, doctor_id):
    # prepare CSV in memory
    appts = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_time).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","patient_id","patient_name","start_time","end_time","status","problem"])
    for a in appts:
        writer.writerow([a.id, a.patient_id, a.patient.user.name if a.patient and a.patient.user else "", a.start_time.isoformat(), a.end_time.isoformat(), a.status, a.problem or ""])
    data = output.getvalue().encode("utf-8")
    filename = f"/tmp/appointments_{doctor_id}_{int(datetime.utcnow().timestamp())}.csv"
    with open(filename, "wb") as f:
        f.write(data)
    return {"path": filename, "size": len(data)}

@celery.task(bind=True)
def send_appointment_reminder(self, appointment_id):
    appt = Appointment.query.get(appointment_id)
    if not appt:
        return {"status":"not_found"}
    # build message
    patient = appt.patient.user if appt.patient else None
    doctor = appt.doctor.user if appt.doctor else None
    subj = f"Appointment reminder: {appt.start_time.strftime('%Y-%m-%d %H:%M')}"
    body = f"Dear {patient.name if patient else 'Patient'}, this is a reminder for your appointment with Dr. {doctor.name if doctor else ''} at {appt.start_time}."
    # send email (here, simple console log or integrate SMTP)
    current_app.logger.info("Reminder: %s -> %s : %s", patient.email if patient else "unknown", subj, body)
    # TODO: integrate SMTP / sendgrid
    return {"status":"sent", "to": patient.email if patient else None}