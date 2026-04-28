"""
wsgi.py
=======
Production WSGI entry point for deployment (Render / Gunicorn).
"""

from app import app

# Optional: local run (not used by Gunicorn in production)
if __name__ == "__main__":
    app.run()