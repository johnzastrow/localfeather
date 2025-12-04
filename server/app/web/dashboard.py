"""
Local Feather - Dashboard Routes

Main dashboard showing device status and recent readings.
"""

from flask import render_template, jsonify, current_app
from flask_login import login_required, current_user
from app.web import web_bp
from app.models import Device, Reading
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta


@web_bp.route('/')
@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    db = current_app.db

    with db.session() as session:
        # Get all devices with their latest readings
        stmt = select(Device).order_by(Device.last_seen.desc())
        devices = session.execute(stmt).scalars().all()

        # Convert to list of dicts for template
        device_list = []
        for device in devices:
            device_list.append({
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name or device.device_id,
                'approved': device.approved,
                'firmware_version': device.firmware_version or 'Unknown',
                'last_seen': device.last_seen,
                'is_online': device.is_online(threshold_minutes=5),
                'total_readings': device.total_readings,
                'ip_address': device.ip_address,
                'signal_strength': device.signal_strength
            })

        # Get total stats
        total_devices = len(device_list)
        online_devices = sum(1 for d in device_list if d['is_online'])
        pending_approvals = sum(1 for d in device_list if not d['approved'])

        # Get recent readings count (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        stmt = select(func.count(Reading.id)).where(Reading.timestamp > yesterday)
        recent_readings = session.execute(stmt).scalar() or 0

    return render_template('dashboard.html',
                          devices=device_list,
                          total_devices=total_devices,
                          online_devices=online_devices,
                          pending_approvals=pending_approvals,
                          recent_readings=recent_readings)


@web_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics (for HTMX updates)"""
    db = current_app.db

    with db.session() as session:
        # Count devices by status
        stmt = select(Device)
        devices = session.execute(stmt).scalars().all()

        total_devices = len(devices)
        online_devices = sum(1 for d in devices if d.is_online(threshold_minutes=5))
        pending_approvals = sum(1 for d in devices if not d.approved)

        # Recent readings
        yesterday = datetime.utcnow() - timedelta(hours=24)
        stmt = select(func.count(Reading.id)).where(Reading.timestamp > yesterday)
        recent_readings = session.execute(stmt).scalar() or 0

    return jsonify({
        'total_devices': total_devices,
        'online_devices': online_devices,
        'pending_approvals': pending_approvals,
        'recent_readings': recent_readings
    })


@web_bp.route('/dashboard/devices')
@login_required
def dashboard_devices():
    """Get device list (for HTMX updates)"""
    db = current_app.db

    with db.session() as session:
        stmt = select(Device).order_by(Device.last_seen.desc())
        devices = session.execute(stmt).scalars().all()

        device_list = []
        for device in devices:
            # Get latest readings
            stmt = select(Reading).where(
                Reading.device_id == device.id
            ).order_by(Reading.timestamp.desc()).limit(2)
            latest_readings = session.execute(stmt).scalars().all()

            reading_data = {}
            for reading in latest_readings:
                reading_data[reading.sensor] = {
                    'value': float(reading.value),
                    'unit': reading.unit,
                    'timestamp': reading.timestamp.isoformat()
                }

            device_list.append({
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name or device.device_id,
                'approved': device.approved,
                'firmware_version': device.firmware_version or 'Unknown',
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'is_online': device.is_online(threshold_minutes=5),
                'total_readings': device.total_readings,
                'ip_address': device.ip_address,
                'signal_strength': device.signal_strength,
                'readings': reading_data
            })

    return render_template('partials/device_list.html', devices=device_list)
