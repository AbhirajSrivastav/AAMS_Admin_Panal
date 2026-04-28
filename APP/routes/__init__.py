"""
app/routes/__init__.py
======================
Blueprint package initializer.

This file marks the routes/ folder as a Python package and can be used
to collect all blueprints for bulk registration.

Usage:
    from app.routes import dashboard_bp, student_bp, attendance_bp, auth_bp
"""

from .dashboard_routes import dashboard_bp
from .student_routes import student_bp
from .attendance_routes import attendance_bp
from .auth_routes import auth_bp

__all__ = ['dashboard_bp', 'student_bp', 'attendance_bp', 'auth_bp']

