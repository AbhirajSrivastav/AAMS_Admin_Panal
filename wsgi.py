"""
wsgi.py
=======
Production WSGI entry point for Render deployment.

Render's Python environment uses this file to boot the application
via Gunicorn instead of the Flask development server.

Usage:
    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2
"""

import os
import sys

# Ensure the project root is on Python path so 'app' package is importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app

# Default to production config on Render; fallback to development locally
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

