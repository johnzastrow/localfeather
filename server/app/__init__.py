"""
Local Feather - Flask Application Factory

This module creates and configures the Flask application.
"""

from flask import Flask
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

    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint"""
        db_status = app.db.health_check()
        return {
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }, 200 if db_status else 503

    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint"""
        return {
            'name': 'Local Feather API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'readings': '/api/readings',
                'devices': '/api/devices',
                'ota_check': '/api/ota/check',
                'ota_download': '/api/ota/download/<version>'
            }
        }

    app.logger.info("Flask application created successfully")

    return app
