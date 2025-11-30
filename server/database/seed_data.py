#!/usr/bin/env python3
"""
Local Feather - Database Seed Data Script

Populates the database with initial test data for development.
"""

import sys
import os
import secrets
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db
from app.models import (
    User, Device, Reading, Firmware, Setting,
    DeviceUpdate, APIKey, DeviceLog, Alert
)
from werkzeug.security import generate_password_hash


def seed_users(session):
    """Create default users"""
    print("Creating users...")

    # Admin user
    admin = User(
        username='admin',
        email='admin@localfeather.local',
        password_hash=generate_password_hash('admin123'),  # Change in production!
        role='admin',
        active=True,
        last_login=datetime.utcnow()
    )

    # Viewer user
    viewer = User(
        username='viewer',
        email='viewer@localfeather.local',
        password_hash=generate_password_hash('viewer123'),
        role='viewer',
        active=True
    )

    session.add_all([admin, viewer])
    session.commit()

    print(f"  ✓ Created admin user (username: admin, password: admin123)")
    print(f"  ✓ Created viewer user (username: viewer, password: viewer123)")

    return admin, viewer


def seed_devices(session):
    """Create sample devices"""
    print("Creating devices...")

    devices = [
        Device(
            device_id='esp32-living-room',
            name='Living Room Sensor',
            api_key=secrets.token_hex(32),
            approved=True,
            firmware_version='1.0.0',
            reading_interval=60000,
            ip_address='192.168.1.101',
            mac_address='AA:BB:CC:DD:EE:01',
            wifi_ssid='HomeNetwork',
            signal_strength=-45,
            location='Living Room',
            notes='BME280 sensor on bookshelf',
            last_seen=datetime.utcnow() - timedelta(minutes=5),
            last_reading_at=datetime.utcnow() - timedelta(minutes=5),
            total_readings=1440  # 24 hours of readings
        ),
        Device(
            device_id='esp32-bedroom',
            name='Bedroom Sensor',
            api_key=secrets.token_hex(32),
            approved=True,
            firmware_version='1.0.0',
            reading_interval=60000,
            ip_address='192.168.1.102',
            mac_address='AA:BB:CC:DD:EE:02',
            wifi_ssid='HomeNetwork',
            signal_strength=-52,
            location='Master Bedroom',
            notes='AHT20 sensor on nightstand',
            last_seen=datetime.utcnow() - timedelta(minutes=2),
            last_reading_at=datetime.utcnow() - timedelta(minutes=2),
            total_readings=720
        ),
        Device(
            device_id='esp32-garage',
            name='Garage Sensor',
            api_key=secrets.token_hex(32),
            approved=True,
            firmware_version='1.0.0',
            reading_interval=300000,  # 5 minutes
            ip_address='192.168.1.103',
            mac_address='AA:BB:CC:DD:EE:03',
            wifi_ssid='HomeNetwork',
            signal_strength=-68,
            location='Garage',
            notes='DHT22 sensor near workbench',
            last_seen=datetime.utcnow() - timedelta(hours=1),
            last_reading_at=datetime.utcnow() - timedelta(hours=1),
            total_readings=288
        ),
        Device(
            device_id='esp32-pending',
            name=None,
            api_key=secrets.token_hex(32),
            approved=False,  # Not approved yet
            firmware_version='1.0.0',
            reading_interval=60000,
            ip_address='192.168.1.104',
            mac_address='AA:BB:CC:DD:EE:04',
            last_seen=datetime.utcnow() - timedelta(minutes=10),
            location='Unknown',
            notes='New device awaiting approval'
        ),
    ]

    session.add_all(devices)
    session.commit()

    print(f"  ✓ Created {len(devices)} devices")
    for device in devices:
        status = "✓ Approved" if device.approved else "⏳ Pending"
        print(f"    - {device.device_id} ({status})")
        print(f"      API Key: {device.api_key}")

    return devices


def seed_readings(session, devices):
    """Create sample sensor readings"""
    print("Creating sample readings...")

    # Only create readings for approved devices
    approved_devices = [d for d in devices if d.approved]

    readings = []
    now = datetime.utcnow()

    for device in approved_devices:
        # Generate readings for the last 24 hours
        for i in range(48):  # Every 30 minutes
            timestamp = now - timedelta(minutes=i * 30)

            # Simulate realistic sensor data with variation
            base_temp = 22.0
            base_humidity = 55.0
            base_pressure = 1013.25

            # Add some variation
            temp_variation = (i % 10) * 0.5 - 2.5
            humidity_variation = (i % 8) * 2 - 8

            readings.extend([
                Reading(
                    device_id=device.id,
                    sensor='temperature',
                    value=Decimal(str(round(base_temp + temp_variation, 2))),
                    unit='C',
                    timestamp=timestamp,
                    received_at=timestamp
                ),
                Reading(
                    device_id=device.id,
                    sensor='humidity',
                    value=Decimal(str(round(base_humidity + humidity_variation, 2))),
                    unit='%',
                    timestamp=timestamp,
                    received_at=timestamp
                ),
            ])

            # Add pressure readings for BME280 sensors (living room)
            if device.device_id == 'esp32-living-room':
                readings.append(
                    Reading(
                        device_id=device.id,
                        sensor='pressure',
                        value=Decimal(str(round(base_pressure + (i % 5) * 0.2, 2))),
                        unit='hPa',
                        timestamp=timestamp,
                        received_at=timestamp
                    )
                )

    # Batch insert for performance
    session.bulk_save_objects(readings)
    session.commit()

    print(f"  ✓ Created {len(readings)} readings")


def seed_firmware(session, admin_user):
    """Create sample firmware versions"""
    print("Creating firmware versions...")

    firmware_versions = [
        Firmware(
            version='1.0.0',
            filename='firmware_1.0.0.bin',
            original_filename='firmware.bin',
            file_size=987654,
            file_hash='a' * 64,  # Fake SHA-256
            release_notes='Initial release with BME280 support and OTA updates',
            uploaded_by=admin_user.id,
            uploaded_at=datetime.utcnow() - timedelta(days=30),
            active=True,
            download_count=3
        ),
        Firmware(
            version='1.0.1',
            filename='firmware_1.0.1.bin',
            original_filename='firmware.bin',
            file_size=989123,
            file_hash='b' * 64,
            release_notes='Bug fixes and performance improvements',
            uploaded_by=admin_user.id,
            uploaded_at=datetime.utcnow() - timedelta(days=7),
            active=True,
            download_count=1
        ),
    ]

    session.add_all(firmware_versions)
    session.commit()

    print(f"  ✓ Created {len(firmware_versions)} firmware versions")

    return firmware_versions


def seed_device_logs(session, devices):
    """Create sample device logs"""
    print("Creating device logs...")

    logs = []
    now = datetime.utcnow()

    for device in devices[:3]:  # Only for first 3 devices
        logs.extend([
            DeviceLog(
                device_id=device.id,
                log_level='info',
                message='Device booted successfully',
                details={'firmware': '1.0.0', 'free_heap': 256000},
                created_at=now - timedelta(hours=24)
            ),
            DeviceLog(
                device_id=device.id,
                log_level='info',
                message='Connected to WiFi',
                details={'ssid': device.wifi_ssid, 'ip': device.ip_address},
                created_at=now - timedelta(hours=24, minutes=1)
            ),
            DeviceLog(
                device_id=device.id,
                log_level='info',
                message='Sensor initialized',
                created_at=now - timedelta(hours=24, minutes=2)
            ),
        ])

    # Add a warning log
    if len(devices) > 0:
        logs.append(
            DeviceLog(
                device_id=devices[0].id,
                log_level='warning',
                message='Low WiFi signal strength',
                details={'rssi': -68},
                created_at=now - timedelta(hours=12)
            )
        )

    session.add_all(logs)
    session.commit()

    print(f"  ✓ Created {len(logs)} device logs")


def seed_alerts(session, devices):
    """Create sample alert rules"""
    print("Creating alert rules...")

    alerts = [
        Alert(
            alert_name='High Temperature Alert',
            device_id=devices[0].id if devices else None,
            sensor='temperature',
            condition='above',
            threshold=Decimal('30.0'),
            enabled=True,
            notify_email='admin@localfeather.local',
            cooldown_minutes=60
        ),
        Alert(
            alert_name='Low Temperature Alert',
            device_id=None,  # Applies to all devices
            sensor='temperature',
            condition='below',
            threshold=Decimal('10.0'),
            enabled=True,
            notify_email='admin@localfeather.local',
            cooldown_minutes=120
        ),
    ]

    session.add_all(alerts)
    session.commit()

    print(f"  ✓ Created {len(alerts)} alert rules")


def main():
    """Main seeding function"""
    print("\n" + "=" * 60)
    print("Local Feather - Database Seeding")
    print("=" * 60 + "\n")

    # Initialize database
    print("Initializing database connection...")
    try:
        db = init_db(use_dev=False, echo=False)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nPlease create database/config.ini from config.example.ini")
        return 1

    # Test connection
    if not db.health_check():
        print("❌ Database connection failed!")
        return 1

    print("✓ Database connection successful\n")

    # Create tables if they don't exist
    print("Creating database tables...")
    db.create_tables()
    print("✓ Tables created\n")

    # Seed data
    with db.session_scope() as session:
        # Check if already seeded
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("⚠ Database already contains data!")
            response = input("Do you want to continue and add more seed data? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return 0

        admin, viewer = seed_users(session)
        devices = seed_devices(session)
        seed_readings(session, devices)
        firmware = seed_firmware(session, admin)
        seed_device_logs(session, devices)
        seed_alerts(session, devices)

    print("\n" + "=" * 60)
    print("✓ Database seeding complete!")
    print("=" * 60)
    print("\nDefault login credentials:")
    print("  Admin:  username=admin,  password=admin123")
    print("  Viewer: username=viewer, password=viewer123")
    print("\n⚠  IMPORTANT: Change these passwords in production!")
    print("=" * 60 + "\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
