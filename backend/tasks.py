import os
import csv
import io
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, date
from flask import current_app, render_template_string
from celery.schedules import crontab

from celery import shared_task
from celery.utils.log import get_task_logger

from database import db
from models import Appointment, Treatment, User, Patient, Doctor

logger = get_task_logger(__name__)

celery = None
def init_celery(celery_app):
    global celery
    celery = celery_app

# ----------------------- #

def send_email(to_email, subject, body, html_body=None):
    smtp_host = current_app.config.get("MAIL_SERVER", "localhost")
    smtp_port = current_app.config.get("MAIL_PORT", 1025)
    smtp_user = current_app.config.get("MAIL_USERNAME", None)
    smtp_pass = current_app.config.get("MAIL_PASSWORD", None)
    from_addr = current_app.config.get("MAIL_DEFAULT_SENDER", "no-reply@example.com")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        if smtp_user and smtp_pass:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
        server.send_message(msg)
        server.quit()
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as e:
        logger.exception("Failed to send email to %s: %s", to_email, e)
        return False

# Change 2: Use @shared_task instead of @celery.task
@shared_task(bind=True, name="tasks.export_treatment_history")
def export_treatment_history(self, patient_id):
    try:
        # Query appointments and treatments
        appts = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_time.desc()).all()

        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["appointment_id","doctor_id","doctor_name","start_time","end_time","status","problem","diagnosis","prescription","notes","treatment_id"])

        for a in appts:
            doctor_name = a.doctor.user.name if a.doctor and a.doctor.user else ""
            diagnosis = a.treatment.diagnosis if a.treatment else ""
            prescription = a.treatment.prescription if a.treatment else ""
            notes = a.treatment.notes if a.treatment else ""
            writer.writerow([
                a.id, a.doctor_id, doctor_name,
                a.start_time.isoformat() if a.start_time else "",
                a.end_time.isoformat() if a.end_time else "",
                a.status, a.problem or "", diagnosis, prescription, notes,
                a.treatment.id if a.treatment else ""
            ])

        data = csv_buf.getvalue().encode("utf-8")
        timestamp = int(datetime.utcnow().timestamp())
        fname = f"/tmp/patient_{patient_id}_treatment_{timestamp}.csv"
        with open(fname, "wb") as f:
            f.write(data)

        # Optionally: notify via email (if patient has email)
        patient_user = Patient.query.get(patient_id).user if Patient.query.get(patient_id) else None
        if patient_user and patient_user.email:
            send_email(patient_user.email, "Your treatment history export is ready",
                       f"Your export is ready. Download path: {fname}")
        return {"status": "ok", "path": fname}
    except Exception as e:
        logger.exception("export_treatment_history failed: %s", e)
        return {"status": "error", "error": str(e)}

# Change 3: Use @shared_task
@shared_task(bind=True, name="tasks.send_daily_reminders")
def send_daily_reminders(self, days_ahead=0):
    try:
        target_date = date.today() + timedelta(days=days_ahead)
        logger.info("Running daily reminders for %s", target_date.isoformat())
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())

        appts = Appointment.query.filter(Appointment.start_time >= start_dt, Appointment.start_time <= end_dt, Appointment.status == "booked").all()
        sent = 0
        for a in appts:
            patient_user = a.patient.user if a.patient else None
            doctor_user = a.doctor.user if a.doctor else None
            if patient_user and patient_user.email:
                subj = f"Reminder: Appointment on {a.start_time.strftime('%Y-%m-%d %H:%M')}"
                body = f"Dear {patient_user.name}, this is a reminder for your appointment with Dr. {doctor_user.name if doctor_user else ''} at {a.start_time}."
                send_email(patient_user.email, subj, body)
            if doctor_user and doctor_user.email:
                subj = f"Upcoming appointment with {patient_user.name if patient_user else 'patient'}"
                body = f"Dear Dr. {doctor_user.name}, you have an appointment with {patient_user.name if patient_user else ''} at {a.start_time}."
                send_email(doctor_user.email, subj, body)
            sent += 1
        return {"status": "ok", "sent": sent}
    except Exception as e:
        logger.exception("send_daily_reminders failed: %s", e)
        return {"status":"error", "error": str(e)}

# Change 4: Use @shared_task
@shared_task(bind=True, name="tasks.generate_monthly_report")
def generate_monthly_report(self, year, month, doctor_id):
    try:
        # compute month start and end
        from calendar import monthrange
        start_dt = datetime(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_dt = datetime(year, month, end_day, 23, 59, 59)

        appts = Appointment.query.filter(Appointment.doctor_id==doctor_id, Appointment.start_time >= start_dt, Appointment.start_time <= end_dt).order_by(Appointment.start_time.asc()).all()

        # Collect treatment summaries
        rows = []
        diag_count = {}
        for a in appts:
            tr = a.treatment
            diag = tr.diagnosis if tr else ""
            rows.append({
                "date": a.start_time.isoformat() if a.start_time else "",
                "patient": a.patient.user.name if a.patient and a.patient.user else "",
                "status": a.status,
                "diagnosis": diag,
                "prescription": tr.prescription if tr else ""
            })
            if diag:
                diag_count[diag] = diag_count.get(diag, 0) + 1
        
        html = render_template_string("""
        <html><head><meta charset="utf-8"><title>Monthly Report</title></head>
        <body>
          <h2>Monthly Report for Dr. {{ doctor_name }} — {{ month }}-{{ year }}</h2>
          <h3>Summary</h3>
          <p>Total appointments: {{ total }}</p>
          <h4>Top diagnoses</h4>
          <ul>
          {% for d,c in diag_items %}
            <li>{{ d }} — {{ c }}</li>
          {% endfor %}
          </ul>

          <h3>Appointments</h3>
          <table border="1" cellpadding="8" cellspacing="0">
            <thead><tr><th>Date</th><th>Patient</th><th>Status</th><th>Diagnosis</th><th>Prescription</th></tr></thead>
            <tbody>
            {% for r in rows %}
              <tr>
                <td>{{ r.date }}</td>
                <td>{{ r.patient }}</td>
                <td>{{ r.status }}</td>
                <td>{{ r.diagnosis }}</td>
                <td>{{ r.prescription }}</td>
              </tr>
            {% endfor %}
            </tbody>
          </table>
        </body></html>
        """, doctor_name=(Doctor.query.get(doctor_id).user.name if Doctor.query.get(doctor_id) and Doctor.query.get(doctor_id).user else "Doctor"), month=month, year=year, total=len(rows), rows=rows, diag_items=sorted(diag_count.items(), key=lambda x:-x[1])[:20])

        timestamp = int(datetime.utcnow().timestamp())
        html_path = f"/tmp/doctor_{doctor_id}_report_{year}_{month}_{timestamp}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        pdf_path = None
        if current_app.config.get("ENABLE_PDF_REPORTS", False):
            try:
                # try wkhtmltopdf
                pdf_path = html_path.replace(".html", ".pdf")
                import subprocess
                subprocess.run(["wkhtmltopdf", html_path, pdf_path], check=True)
            except Exception as e:
                logger.warning("PDF generation failed: %s", e)
                pdf_path = None

        doc = Doctor.query.get(doctor_id)
        doc_email = doc.user.email if doc and doc.user else None
        if doc_email:
            send_email(doc_email, f"Monthly report {year}-{month}", f"The monthly report for {year}-{month} is generated. HTML: {html_path} PDF: {pdf_path or 'not generated'}")

        return {"status":"ok", "html_path": html_path, "pdf_path": pdf_path}
    
    except Exception as e:
        logger.exception("generate_monthly_report failed: %s", e)
        return {"status":"error", "error": str(e)}

# Important: Ensure export_appointments_csv is defined if referenced in admin.py
@shared_task(bind=True, name="tasks.export_appointments_csv")
def export_appointments_csv(self, doctor_id):
    # Implementation for exporting doctor appointments...
    # (Similar logic to export_treatment_history but for doctor view)
    pass