"""
app/routes/student_routes.py
============================
Student management routes and face recognition reload endpoint.

Blueprint prefix: None (root routes)
Registered endpoints:
    GET  /student-directory    -> Student list page
    GET  /api/students         -> JSON list of all students
    POST /api/reload-faces     -> Rescan image_data/ and reload encodings
"""

from flask import Blueprint, render_template, jsonify, request
from app.database.db import DatabaseManager
from app.services.face_recognition_service import FaceRecognitionService

student_bp = Blueprint('student', __name__)


# ------------------------------------------------------------------
# Page routes (HTML)
# ------------------------------------------------------------------

@student_bp.route('/student-directory')
def student_directory():
    """Render the student directory page."""
    return render_template('student_directory.html')


# ------------------------------------------------------------------
# API routes (JSON)
# ------------------------------------------------------------------

@student_bp.route('/api/students')
def get_students():
    """
    Return all registered students.

    Response: list of student dicts with id, name, student_id, email,
              phone, status, created_at.
    """
    db = DatabaseManager()
    students = db.get_all_students()
    return jsonify(students)


@student_bp.route('/api/reload-faces', methods=['POST'])
def reload_faces():
    """
    Admin endpoint to rescan the image_data/ folder and reload
    all face encodings without restarting the server.

    Returns:
        JSON summary with status, count of loaded students, and student names.
    """
    service = FaceRecognitionService()
    result = service.reload()
    return jsonify(result)

