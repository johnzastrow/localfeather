"""
Local Feather - Web UI Blueprint

This module provides the web interface for managing devices and viewing data.
"""

from flask import Blueprint

web_bp = Blueprint('web', __name__, template_folder='../templates', static_folder='../static')

# Import routes to register them with the blueprint
from app.web import dashboard, devices, auth
