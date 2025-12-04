"""
Local Feather - Authentication Routes

Handles user login, logout, and session management.
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.web import web_bp
from app.models import User
from sqlalchemy import select


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')

        # Query user from database
        db = current_app.db
        with db.session() as session:
            stmt = select(User).where(User.username == username, User.active == True)
            user = session.execute(stmt).scalar_one_or_none()

            if user and check_password_hash(user.password_hash, password):
                # Update last login
                user.last_login = db.func.now()
                session.commit()

                # Log in user
                login_user(user, remember=remember)

                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('web.dashboard'))
            else:
                flash('Invalid username or password', 'error')

    return render_template('login.html')


@web_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('web.login'))
