"""
app/__init__.py
===============
Flask Application Factory for the AI Attendance Management System.

This module follows the Application Factory pattern, which is the recommended
way to create Flask apps. It allows for easier testing, configuration switching,
and scaling (e.g., multiple app instances behind a load balancer).

Usage:
    from app import create_app
    app = create_app()
"""

from flask import Flask
from app.config import config_by_name
from app.database.db import DatabaseManager
from app.services.face_recognition_service import FaceRecognitionService

# Global service instances (initialized inside create_app)
db_manager = None
face_service = None


def create_app(config_name='development'):
    """
    Application Factory: creates and configures the Flask app.

    Args:
        config_name (str): 'development', 'production', or 'testing'

    Returns:
        Flask: Configured Flask application instance
    """
    global db_manager, face_service

    # 1. Create the Flask app instance
    app = Flask(
        __name__,
        template_folder='templates',       # Jinja2 templates location
        static_folder='static',            # Static files (CSS, JS, images)
        instance_relative_config=True      # Allow instance/ folder configs
    )

    # 2. Load configuration from config.py classes
    app.config.from_object(config_by_name[config_name])

    # 3. Initialize the database manager (PostgreSQL)
    db_manager = DatabaseManager()

    # 4. Initialize the face recognition service
    #    This scans image_data/ folders and pre-computes face encodings.
    face_service = FaceRecognitionService()
    face_service.load_known_faces()

    # 5. Register Blueprints (modular route groups)
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.student_routes import student_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(auth_bp)

    # 6. Initialize device status in database on startup
    _init_device_status()

    return app


def _init_device_status():
    """
    Record initial system health into the database.
    Called once during app creation.
    """
    from app.database.db import DatabaseManager
    db = DatabaseManager()
    db.update_device_status('Camera', 'Active', 'Main entrance camera - ready')
    db.update_device_status(
        'Face Recognition AI', 'Active',
        f'face_recognition loaded: {len(face_service.known_face_names)} student(s)'
    )
    db.update_device_status('Database', 'Active', 'PostgreSQL - ready')
    db.update_device_status('Flask Server', 'Active', 'Port 5000 - running')

