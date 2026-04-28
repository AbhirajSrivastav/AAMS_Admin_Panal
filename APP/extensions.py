"""
app/extensions.py
=================
Extension registry for the Flask application.

This file acts as a central place to initialize third-party Flask extensions.
Currently, it is a placeholder since we use raw SQL for the database.

Future SaaS enhancements to add here:
    - Flask-Login   : User session management
    - Flask-Mail    : Email notifications for absent reports
    - Flask-Migrate : Database schema migrations (Alembic)
    - Flask-RESTful : Structured REST API endpoints
    - Celery        : Background task queue for report generation

Usage:
    from app.extensions import login_manager
    login_manager.init_app(app)
"""

# Example placeholder for Flask-Login (uncomment when ready):
# from flask_login import LoginManager
# login_manager = LoginManager()

# Example placeholder for Flask-Mail (uncomment when ready):
# from flask_mail import Mail
# mail = Mail()

