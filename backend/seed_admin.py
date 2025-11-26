from app import create_app
from database import db
from werkzeug.security import generate_password_hash
from models import User, UserRole

def seed(email="admin@hms.com", password="admin123"):
    app = create_app()
    with app.app_context():
        db.create_all()
        if User.query.filter_by(email=email).first():
            print("admin exists")
            return
        user = User(email=email, password=generate_password_hash(password), name="Admin", role=UserRole.ADMIN)
        db.session.add(user)
        db.session.commit()
        print("admin created", email)

if __name__ == "__main__":
    seed()
