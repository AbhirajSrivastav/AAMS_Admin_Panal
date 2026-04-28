"""
app/routes/auth_routes.py
=========================
Authentication routes scaffold for future multi-user support.

Currently, the system operates in single-admin mode. This blueprint
provides placeholder endpoints that can be wired to Flask-Login,
Flask-Bcrypt, and JWT in a future SaaS upgrade.

Planned endpoints:
    GET  /login       -> Login page
    POST /login       -> Authenticate and create session
    GET  /logout      -> Clear session and redirect
    POST /register    -> Create new admin account (disabled in production)
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page and authentication handler.

    GET  -> Render login form
    POST -> Validate credentials and create session (placeholder)
    """
    if request.method == 'POST':
        # TODO: Implement real authentication with Flask-Login + Bcrypt
        username = request.form.get('username')
        password = request.form.get('password')
        # Placeholder success
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear user session and redirect to login."""
    # TODO: Clear Flask-Login session
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/auth/status')
def auth_status():
    """
    Return current authentication status.

    Future: check Flask-Login's current_user.is_authenticated
    """
    return jsonify({
        'authenticated': False,
        'user': None,
        'message': 'Authentication not yet implemented. See auth_routes.py scaffold.'
    })

