"""
Local Feather - API Blueprint

This module contains all API endpoints for device communication.
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api import readings, devices, ota


def apply_rate_limits(limiter):
    """Apply rate limiting to API endpoints"""
    from app.api.readings import post_readings, get_rate_limit_key

    # Apply rate limit to readings endpoint
    limiter.limit("60 per minute", key_func=get_rate_limit_key)(post_readings)
