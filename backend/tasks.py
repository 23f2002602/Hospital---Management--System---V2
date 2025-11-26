from app import create_app, make_celery
from config import Config
from database import db
from models import Appointment
import csv

app = create_app()
celery = make_celery(app)

@celery.task
def export_appointments_csv():
    with app.app_context():
        appts = Appointment.query.all()

        path = "/tmp/appointments_export.csv"

        with open(path, "w", newline="") as c :
            writer = csv.writer(c)
            writer.writerow(["ID", "Patient ID", 
                             "Doctor ID", "Date", 
                             "Start Time", "End Time", 
                             "Status"])
            for a in appts:
                writer.wrtierrow([a.id, a.patient_id, 
                                 a.doctor_id, a.date, 
                                 a.start_time, a.end_time, 
                                 a.status])
        return path
