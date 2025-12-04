"""
Local Feather - Flask Application Factory

This module creates and configures the Flask application.
"""

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os


def create_app(config_path: str = None) -> Flask:
    """
    Application factory pattern for Flask.

    Args:
        config_path: Path to config.ini file

    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    # Initialize database
    from app.database import init_db
    try:
        db = init_db(config_path=config_path, use_dev=False, echo=False)
        app.db = db
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        from app.models import User
        from sqlalchemy import select

        with app.db.session_scope() as session:
            stmt = select(User).where(User.id == int(user_id))
            user = session.execute(stmt).scalar_one_or_none()
            if user:
                # Detach from session so it can be used outside the context
                session.expunge(user)
            return user

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    app.limiter = limiter

    # Register blueprints
    from app.api import api_bp, apply_rate_limits
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.web import web_bp
    app.register_blueprint(web_bp)

    # Apply rate limits after blueprints are registered
    apply_rate_limits(limiter)

    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint"""
        db_status = app.db.health_check()
        return {
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }, 200 if db_status else 503

    # Root endpoint - redirect to dashboard
    @app.route('/')
    def index():
        """Root endpoint - redirect to dashboard"""
        return redirect(url_for('web.dashboard'))

    app.logger.info("Flask application created successfully")

    return app
