from datetime import datetime, date
from database import db

class UserRole:
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    PATIENT = 'patient'

class AppointmentStatus:
    BOOKED = 'booked'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor_profile = db.relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = db.relationship("Patient", back_populates="user", uselist=False)

    def __repr__(self):
        return f'<User {self.id} {self.email} - {self.role}>'
    

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)

    doctors = db.relationship("Doctor", back_populates="department")

    def __repr__(self):
        return f"<Department {self.id} {self.name}>"
    
class Doctor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    specialization = db.Column(db.String(120))
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))

    user = db.relationship("User", back_populates="doctor_profile")
    department = db.relationship("Department", back_populates="doctors")

    appointments = db.relationship("Appointment", back_populates="doctor")

    availability = db.relationship("DoctorAvailability", back_populates="doctor")
    overrides = db.relationship("DoctorAvailabilityOverride", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor {self.id} {self.specialization}>"
    
class Patient(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    phone = db.Column(db.String(40))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))

    user = db.relationship("User", back_populates="patient_profile")

    appointments = db.relationship("Appointment", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.id}>"
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)

    date = db.Column(db.Date, nullable=False, default=date.today)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default=AppointmentStatus.BOOKED)
    problem = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", back_populates="appointments")
    patient = db.relationship("Patient", back_populates="appointments")
    treatment = db.relationship("Treatment", back_populates="appointment", uselist=False)

    def __repr__(self):
        return f"<Appointment {self.id} {self.start_time}>"
    
class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))

    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship("Appointment", back_populates="treatment")

    def __repr__(self):
        return f"<Treatment {self.id}>"
    
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.id}>"
    
class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))

    day_of_week = db.Column(db.String(10))  # "Monday", "Tuesday", ...
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    is_available = db.Column(db.Boolean, default=True)

    doctor = db.relationship("Doctor", back_populates="availability")

    def __repr__(self):
        return f"<Availability {self.doctor_id} {self.day_of_week}>"
    
class DoctorAvailabilityOverride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))

    date = db.Column(db.Date)
    is_available = db.Column(db.Boolean, default=True)

    doctor = db.relationship("Doctor", back_populates="overrides")

    def __repr__(self):
        return f"<Override {self.doctor_id} {self.date}>"