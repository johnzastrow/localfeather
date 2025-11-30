#!/usr/bin/env python3
"""
Local Feather - Development Server

This script runs the Flask development server.
For production, use Gunicorn or uWSGI instead.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app


def main():
    """Run the development server"""

    # Create Flask app
    config_path = os.path.join(
        os.path.dirname(__file__),
        'database/config.ini'
    )

    try:
        app = create_app(config_path=config_path)
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        return 1

    # Run development server
    print("\n" + "=" * 60)
    print("Local Feather - Development Server")
    print("=" * 60)
    print(f"Database: Connected")
    print(f"API Endpoints: /api")
    print(f"Health Check: /health")
    print("=" * 60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
