"""
app/routes/attendance_routes.py
===============================
Attendance logging routes and log viewing.

Blueprint prefix: None (root routes)
Registered endpoints:
    GET /attendance-logs          -> Attendance logs page
    GET /api/attendance-logs      -> JSON all logs
    GET /api/attendance-logs/<date> -> JSON logs for specific date
"""

from flask import Blueprint, render_template, jsonify, request
from app.database.db import DatabaseManager

attendance_bp = Blueprint('attendance', __name__)


# ------------------------------------------------------------------
# Page routes (HTML)
# ------------------------------------------------------------------

@attendance_bp.route('/attendance-logs')
def attendance_logs():
    """Render the attendance logs page."""
    return render_template('attendance_logs.html')


# ------------------------------------------------------------------
# API routes (JSON)
# ------------------------------------------------------------------

@attendance_bp.route('/api/attendance-logs')
def get_attendance_logs():
    """
    Return all attendance records with student names.

    Query param:
        limit (int): max rows (default 50)
    """
    limit = request.args.get('limit', 50, type=int)
    db = DatabaseManager()
    logs = db.get_all_attendance_logs(limit=limit)
    return jsonify(logs)


@attendance_bp.route('/api/attendance-logs/<date>')
def get_attendance_by_date(date):
    """
    Return attendance records for a specific date.

    Args:
        date (str): Date in YYYY-MM-DD format.

    Returns:
        JSON list of attendance log dicts.
    """
    db = DatabaseManager()
    logs = db.get_attendance_by_date(date)
    return jsonify(logs)

