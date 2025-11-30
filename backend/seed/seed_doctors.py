from app import create_app
from database import db
from werkzeug.security import generate_password_hash
from models import User, UserRole, Doctor, Department

def seed_doctors():
    app = create_app()
    with app.app_context():
        # 1. Ensure Departments Exist
        departments_data = [
            "Cardiology", 
            "Neurology", 
            "Pediatrics", 
            "Orthopedics", 
            "General Surgery",
            "Obstetrics and Gynecology",
            "Oncology",
            "Plastic Surgery"
        ]
        departments_map = {}
        
        print("--- Seeding Departments ---")
        for name in departments_data:
            dept = Department.query.filter_by(name=name).first()
            if not dept:
                dept = Department(name=name, description=f"The {name} department.")
                db.session.add(dept)
                db.session.commit()
                print(f"Created Department: {name}")
            else:
                print(f"Department exists: {name}")
            departments_map[name] = dept

        # 2. Dummy Doctors Data
        dummy_doctors = [
            # Original List
            {
                "name": "Dr. Meredith Grey",
                "email": "meredith@example.com",
                "password": "password123",
                "specialization": "General Surgery",
                "dept": "General Surgery"
            },
            {
                "name": "Dr. Derek Shepherd",
                "email": "derek@example.com",
                "password": "password123",
                "specialization": "Neurosurgery",
                "dept": "Neurology"
            },
            {
                "name": "Dr. Alex Karev",
                "email": "alex@example.com",
                "password": "password123",
                "specialization": "Pediatric Surgery",
                "dept": "Pediatrics"
            },
            {
                "name": "Dr. Cristina Yang",
                "email": "cristina@example.com",
                "password": "password123",
                "specialization": "Cardiothoracic Surgery",
                "dept": "Cardiology"
            },
            {
                "name": "Dr. Callie Torres",
                "email": "callie@example.com",
                "password": "password123",
                "specialization": "Orthopedic Surgery",
                "dept": "Orthopedics"
            },
            
            # --- New Female Characters ---
            {
                "name": "Dr. Addison Montgomery",
                "email": "addison@example.com",
                "password": "password123",
                "specialization": "OB/GYN & Neonatal Surgery",
                "dept": "Obstetrics and Gynecology"
            },
            {
                "name": "Dr. Miranda Bailey",
                "email": "bailey@example.com",
                "password": "password123",
                "specialization": "General Surgery",
                "dept": "General Surgery"
            },
            {
                "name": "Dr. Arizona Robbins",
                "email": "arizona@example.com",
                "password": "password123",
                "specialization": "Pediatric Surgery",
                "dept": "Pediatrics"
            },
            {
                "name": "Dr. Amelia Shepherd",
                "email": "amelia@example.com",
                "password": "password123",
                "specialization": "Neurosurgery",
                "dept": "Neurology"
            },
            {
                "name": "Dr. Teddy Altman",
                "email": "teddy@example.com",
                "password": "password123",
                "specialization": "Cardiothoracic Surgery",
                "dept": "Cardiology"
            },
            {
                "name": "Dr. Izzie Stevens",
                "email": "izzie@example.com",
                "password": "password123",
                "specialization": "Surgical Oncology",
                "dept": "Oncology"
            },
            {
                "name": "Dr. Lexie Grey",
                "email": "lexie@example.com",
                "password": "password123",
                "specialization": "Neurosurgery",
                "dept": "Neurology"
            },
            {
                "name": "Dr. Jo Wilson",
                "email": "jo@example.com",
                "password": "password123",
                "specialization": "General Surgery",
                "dept": "General Surgery"
            }
        ]

        print("\n--- Seeding Doctors ---")
        for d in dummy_doctors:
            if User.query.filter_by(email=d["email"]).first():
                print(f"Skipping {d['email']} (already exists)")
                continue

            # Create User
            user = User(
                name=d["name"],
                email=d["email"],
                password=generate_password_hash(d["password"]),
                role=UserRole.DOCTOR
            )
            db.session.add(user)
            db.session.commit()

            # Create Doctor Profile linked to Department
            dept_obj = departments_map.get(d["dept"])
            dept_id = dept_obj.id if dept_obj else None

            doctor = Doctor(
                id=user.id,
                specialization=d["specialization"],
                department_id=dept_id
            )
            db.session.add(doctor)
            db.session.commit()
            
            print(f"Created: {d['name']} ({d['email']}) in {d['dept']}")

        print("--- Done ---")

if __name__ == "__main__":
    seed_doctors()