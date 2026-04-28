"""
app/routes/dashboard_routes.py
==============================
Dashboard routes: home page, live video feed, statistics, and charts API.

Blueprint prefix: None (root routes)
Registered endpoints:
    GET  /           -> index (dashboard home)
    GET  /reports    -> reports page
    GET  /device-status -> device status page
    GET  /video_feed -> MJPEG live camera stream
    GET  /api/stats  -> JSON dashboard statistics
    GET  /api/data   -> JSON recent attendance records
    GET  /api/weekly-stats -> JSON weekly breakdown
"""

from flask import Blueprint, render_template, Response, jsonify, current_app, request
from app.services.report_service import ReportService
from app.services.face_recognition_service import FaceRecognitionService
from app.utils.camera import CameraManager
from app.utils.helpers import generate_frames

# Create Blueprint: no url_prefix so these sit at root
dashboard_bp = Blueprint('dashboard', __name__)

# Shared service instances (in a production SaaS app these would be injected
# via dependency injection or Flask's g object)
report_service = ReportService()
camera_manager = CameraManager()


# ------------------------------------------------------------------
# Page routes (HTML)
# ------------------------------------------------------------------

@dashboard_bp.route('/')
def index():
    """Render the main dashboard home page."""
    return render_template('index.html')


@dashboard_bp.route('/reports')
def reports():
    """Render the analytics and reports page."""
    return render_template('reports.html')


@dashboard_bp.route('/device-status')
def device_status():
    """Render the system health and device monitoring page."""
    return render_template('device_status.html')


# ------------------------------------------------------------------
# Video streaming
# ------------------------------------------------------------------

@dashboard_bp.route('/video_feed')
def video_feed():
    """
    Stream live camera feed in MJPEG format.

    This endpoint starts the camera thread on first request and yields
    JPEG frames indefinitely with multipart/x-mixed-replace headers.
    """
    return Response(
        generate_frames(camera_manager),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# ------------------------------------------------------------------
# API routes (JSON)
# ------------------------------------------------------------------

@dashboard_bp.route('/api/stats')
def get_stats():
    """
    Return dashboard summary statistics for today.

    Response format:
        {
            "total_students": 285,
            "present_today": 250,
            "absent_today": 35,
            "late_today": 15,
            "attendance_rate": 97.9
        }
    """
    stats = report_service.get_dashboard_stats()
    return jsonify(stats)


@dashboard_bp.route('/api/data')
def get_data():
    """
    Return recent attendance records (joined with student names).

    Query param:
        limit (int): max rows to return (default 100)
    """
    from app.database.db import DatabaseManager
    db = DatabaseManager()
    limit = request.args.get('limit', 100, type=int)
    logs = db.get_all_attendance_logs(limit=limit)
    return jsonify(logs)


@dashboard_bp.route('/api/weekly-stats')
def get_weekly_stats():
    """
    Return daily attendance breakdown for the current or past week.

    Query param:
        offset (int): weeks in the past (0 = current week)
    """
    offset = request.args.get('offset', 0, type=int)
    stats = report_service.get_weekly_breakdown(week_offset=offset)
    return jsonify(stats)


@dashboard_bp.route('/api/device-status')
def get_device_status():
    """
    Return current status of all monitored system devices.
    """
    devices = report_service.get_device_health()
    return jsonify(devices)

