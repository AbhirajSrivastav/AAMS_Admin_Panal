"""
wsgi.py
=======
Production WSGI entry point for deployment (Render / Gunicorn).
"""

import sys
import os

# Ensure the project root is on Python path so 'app' package is importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app

app = create_app()

# Optional: local run (not used by Gunicorn in production)
if __name__ == "__main__":
    app.run()