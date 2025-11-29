from flask import Flask, jsonify
from config import Config
from extensions import migrate, jwt, cors, cache
from database import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.tasks import tasks_bp

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(doctor_bp, url_prefix="/api/doctor")
    app.register_blueprint(patient_bp, url_prefix="/api/patient")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

    @app.get("/")
    def index():
        return jsonify({"msg": "HMS API running"})

    return app

if (__name__ == "__main__"):
    app = create_app()
    app.run(debug=True)