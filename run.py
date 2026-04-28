"""
AAMS - Attendance Management System
===================================
Entry point for the Flask application.

Usage:
    python run.py

This file initializes the app using the Application Factory pattern
and starts the development server.
"""

import sys
import os

# Ensure the project root is on Python path so 'app' package is importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app

# Create the Flask application instance using the factory
app = create_app()

if __name__ == '__main__':
    # Run the Flask development server
    # use_reloader=False prevents the camera thread from being duplicated
    app.run(debug=True, use_reloader=False, threaded=True, port=5000)

