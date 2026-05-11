"""Flask application factory for the AAMS project.

The application package lives under the directory named `APP`.
Entry points (`run.py`, `wsgi.py`) import `create_app` via `from app import create_app`,
where `app.py` re-exports it.

This file must therefore expose a real `create_app` callable.
"""

from __future__ import annotations

from flask import Flask

from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .routes.attendance_routes import attendance_bp
from .routes.auth_routes import auth_bp
from .routes.dashboard_routes import dashboard_bp
from .routes.student_routes import student_bp

from .services.face_recognition_service import FaceRecognitionService
from .utils.camera import CameraManager


def create_app():
    """Application factory."""
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Basic config selection
    # (For simplicity we use FLASK_ENV / ENVIRONMENT if present; default to development)
    env = (app.config.get('ENV') or None)  # placeholder for possible future config
    import os
    env = os.getenv('FLASK_ENV') or os.getenv('ENVIRONMENT') or 'development'

    config_cls = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }.get(env, DevelopmentConfig)

    app.config.from_object(config_cls)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(auth_bp)

    # Warm-up services that rely on app context (optional)
    # Keep lightweight: do not start camera thread here.
    app.extensions['face_recognition'] = FaceRecognitionService()
    app.extensions['camera_manager'] = CameraManager()

    return app

