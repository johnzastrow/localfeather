#!/usr/bin/env python3
"""
Migration: Hash API Keys
Date: 2025-01-04
Description:
- Increase api_key column size from 64 to 255 characters
- Hash existing plaintext API keys using bcrypt
- Update devices table to store hashed keys

IMPORTANT: This migration will:
1. Read all existing plaintext API keys
2. Hash them with bcrypt
3. Update the database with hashed keys
4. Modify the column to support 255 characters

Note: This is a breaking change for existing devices.
The devices will need to be re-registered OR you need to manually
update the ESP32 firmware to re-register.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask_bcrypt import generate_password_hash
from sqlalchemy import text
from app.database import init_db
from app.models import Device


def run_migration():
    """Execute the migration"""
    print("Starting API key hashing migration...")

    # Initialize database
    config_path = Path(__file__).parent.parent / 'config.ini'
    db = init_db(config_path=str(config_path), use_dev=False, echo=False)

    # Step 1: Extend the api_key column size
    print("\n1. Extending api_key column size to 255 characters...")
    with db.engine.connect() as conn:
        conn.execute(
            text("ALTER TABLE devices MODIFY COLUMN api_key VARCHAR(255) NOT NULL")
        )
        conn.commit()
    print("   ✓ Column extended successfully")

    # Step 2: Read all devices and hash their API keys
    print("\n2. Hashing existing API keys...")
    with db.session_scope() as session:
        devices = session.query(Device).all()

        if not devices:
            print("   No devices found - nothing to hash")
            return

        print(f"   Found {len(devices)} device(s) to process")

        for device in devices:
            # Store original key (for display only - truncated for security)
            original_key_preview = device.api_key[:8] + "..." if len(device.api_key) > 8 else device.api_key

            # Check if already hashed (bcrypt hashes start with $2b$)
            if device.api_key.startswith('$2b$'):
                print(f"   - {device.device_id}: Already hashed, skipping")
                continue

            # Hash the API key
            hashed_key = generate_password_hash(device.api_key).decode('utf-8')
            device.api_key = hashed_key

            print(f"   - {device.device_id}: Hashed key (was: {original_key_preview})")

        session.commit()
        print(f"\n   ✓ Successfully hashed {len(devices)} API key(s)")

    print("\n✓ Migration completed successfully!")
    print("\nIMPORTANT: Devices with old plaintext API keys will need to:")
    print("  1. Re-register with the server (server will generate new key)")
    print("  2. OR manually update their stored API key in EEPROM")


def rollback_migration():
    """Rollback the migration (not recommended - you'll lose the plaintext keys)"""
    print("WARNING: Rollback not supported for this migration")
    print("Plaintext API keys cannot be recovered from bcrypt hashes")
    print("Devices will need to re-register to get new keys")


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
            rollback_migration()
        else:
            run_migration()
    except Exception as e:
        print(f"\n✗ Migration failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
