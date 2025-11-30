from app import create_app
from database import db
from werkzeug.security import generate_password_hash
from models import User, UserRole, Patient
from datetime import date

def seed_patients():
    app = create_app()
    with app.app_context():
        # List of dummy patients to create
        dummy_patients = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123",
                "phone": "1234567890",
                "dob": date(1990, 5, 15),
                "gender": "male"
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "password": "password123",
                "phone": "9876543210",
                "dob": date(1995, 8, 22),
                "gender": "female"
            },
            {
                "name": "Alice Brown",
                "email": "alice@example.com",
                "password": "password123",
                "phone": "5551234567",
                "dob": date(1988, 1, 10),
                "gender": "female"
            },
            {
                "name": "Bob White",
                "email": "bob@example.com",
                "password": "password123",
                "phone": "4449876543",
                "dob": date(2000, 12, 5),
                "gender": "male"
            }
        ]

        print("--- Seeding Patients ---")
        
        for p in dummy_patients:
            # Check if user already exists
            if User.query.filter_by(email=p["email"]).first():
                print(f"Skipping {p['email']} (already exists)")
                continue

            # 1. Create User
            user = User(
                name=p["name"],
                email=p["email"],
                password=generate_password_hash(p["password"]),
                role=UserRole.PATIENT
            )
            db.session.add(user)
            db.session.commit()  # Commit to generate the user.id

            # 2. Create Patient Profile
            patient = Patient(
                id=user.id,
                phone=p["phone"],
                dob=p["dob"],
                gender=p["gender"]
            )
            db.session.add(patient)
            db.session.commit()
            
            print(f"Created: {p['name']} ({p['email']})")

        print("--- Done ---")

if __name__ == "__main__":
    seed_patients()