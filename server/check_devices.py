#!/usr/bin/env python3
"""
Quick script to check device status in the database
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db
from app.models import Device

def main():
    print("Checking devices in database...\n")

    # Initialize database
    config_path = Path(__file__).parent / 'database' / 'config.ini'
    db = init_db(config_path=str(config_path), use_dev=False, echo=False)

    with db.session_scope() as session:
        devices = session.query(Device).all()

        if not devices:
            print("No devices found in database")
            return

        print(f"Found {len(devices)} device(s):\n")

        for device in devices:
            print(f"Device ID: {device.device_id}")
            print(f"  Name: {device.name or '(unnamed)'}")
            print(f"  API Key (first 20 chars): {device.api_key[:20]}...")
            print(f"  API Key Length: {len(device.api_key)} chars")
            print(f"  Is Hashed: {'Yes' if device.api_key.startswith('$2b$') else 'No (plaintext!)'}")
            print(f"  Approved: {'Yes' if device.approved else 'No'}")
            print(f"  Last Seen: {device.last_seen}")
            print(f"  Firmware: {device.firmware_version or 'Unknown'}")
            print(f"  Total Readings: {device.total_readings}")
            print()

if __name__ == '__main__':
    main()
