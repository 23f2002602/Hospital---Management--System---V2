from pathlib import Path
from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from celery.result import AsyncResult
from tasks import export_treatment_history, generate_monthly_report, send_daily_reminders
from backend.utils.utils import role_required
from models import *
from database import db
import os

tasks_bp = Blueprint("tasks_bp", __name__)

@tasks_bp.route("/export/patient/history", methods=["POST"])
@jwt_required()
@role_required([UserRole.PATIENT])
def trigger_patient_export():
    # get_jwt_identity should return the current user's id (int or str)
    patient_id = int(get_jwt_identity())
    task = export_treatment_history.delay(patient_id)
    return jsonify({"task_id": task.id}), 202

@tasks_bp.route("/admin/report/monthly", methods=["POST"])
@jwt_required()
@role_required([UserRole.ADMIN])
def trigger_monthly_report():
    data = request.get_json() or {}
    year = int(data.get("year"))
    month = int(data.get("month"))
    doctor_id = int(data.get("doctor_id"))
    task = generate_monthly_report.delay(year, month, doctor_id)
    return jsonify({"task_id": task.id}), 202

@tasks_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required()
def task_status(task_id):
    res = AsyncResult(task_id)
    return jsonify({"id": task_id, "status": res.status, "result": res.result}), 200

@tasks_bp.route("/tasks/download", methods=["GET"])
@jwt_required()
def download_file():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"msg":"file not found"}), 404
    # you may add permission checks here
    return send_file(path, as_attachment=True)