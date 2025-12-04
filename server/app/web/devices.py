"""
Local Feather - Device Management Routes

Device approval, editing, and deletion.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.web import web_bp
from app.models import Device, Reading
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
import secrets


@web_bp.route('/devices')
@login_required
def devices_list():
    """List all devices"""
    db = current_app.db

    with db.session() as session:
        stmt = select(Device).order_by(Device.created_at.desc())
        devices = session.execute(stmt).scalars().all()

        device_list = []
        for device in devices:
            device_list.append({
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name or device.device_id,
                'approved': device.approved,
                'firmware_version': device.firmware_version,
                'last_seen': device.last_seen,
                'is_online': device.is_online(threshold_minutes=5),
                'total_readings': device.total_readings,
                'created_at': device.created_at,
                'ip_address': device.ip_address,
                'wifi_ssid': device.wifi_ssid,
                'signal_strength': device.signal_strength
            })

    return render_template('devices.html', devices=device_list)


@web_bp.route('/devices/<int:device_id>')
@login_required
def device_detail(device_id):
    """Device detail page with readings chart"""
    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            flash('Device not found', 'error')
            return redirect(url_for('web.devices_list'))

        # Get readings for last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        stmt = select(Reading).where(
            Reading.device_id == device_id,
            Reading.timestamp > week_ago
        ).order_by(Reading.timestamp.asc())
        readings = session.execute(stmt).scalars().all()

        # Group readings by sensor type
        readings_by_sensor = {}
        for reading in readings:
            if reading.sensor not in readings_by_sensor:
                readings_by_sensor[reading.sensor] = {
                    'unit': reading.unit,
                    'data': []
                }
            readings_by_sensor[reading.sensor]['data'].append({
                'timestamp': reading.timestamp.isoformat(),
                'value': float(reading.value)
            })

        device_data = {
            'id': device.id,
            'device_id': device.device_id,
            'name': device.name or device.device_id,
            'approved': device.approved,
            'firmware_version': device.firmware_version or 'Unknown',
            'last_seen': device.last_seen,
            'is_online': device.is_online(threshold_minutes=5),
            'total_readings': device.total_readings,
            'created_at': device.created_at,
            'ip_address': device.ip_address,
            'mac_address': device.mac_address,
            'wifi_ssid': device.wifi_ssid,
            'signal_strength': device.signal_strength,
            'location': device.location,
            'notes': device.notes
        }

    return render_template('device_detail.html',
                          device=device_data,
                          readings=readings_by_sensor)


@web_bp.route('/devices/<int:device_id>/approve', methods=['POST'])
@login_required
def device_approve(device_id):
    """Approve a device"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        device.approved = True
        session.commit()

        flash(f'Device {device.device_id} approved', 'success')

    # Return HTML fragment for HTMX
    return f'<span class="text-green-600">Approved</span>'


@web_bp.route('/devices/<int:device_id>/rename', methods=['POST'])
@login_required
def device_rename(device_id):
    """Rename a device"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    new_name = request.form.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        device.name = new_name
        session.commit()

        flash(f'Device renamed to {new_name}', 'success')

    return jsonify({'success': True, 'name': new_name})


@web_bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def device_delete(device_id):
    """Delete a device"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        device_id_str = device.device_id
        session.delete(device)
        session.commit()

        flash(f'Device {device_id_str} deleted', 'success')

    return redirect(url_for('web.devices_list'))


@web_bp.route('/devices/<int:device_id>/regenerate-key', methods=['POST'])
@login_required
def device_regenerate_key(device_id):
    """Regenerate API key for a device"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        # Generate new API key
        new_api_key = secrets.token_hex(32)
        device.api_key = new_api_key
        session.commit()

        flash(f'New API key generated for {device.device_id}', 'success')

    return jsonify({'success': True, 'api_key': new_api_key})


@web_bp.route('/devices/<int:device_id>/update-location', methods=['POST'])
@login_required
def device_update_location(device_id):
    """Update device location"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    location = request.form.get('location', '').strip()

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        device.location = location if location else None
        session.commit()

        flash(f'Device location updated', 'success')

    return jsonify({'success': True, 'location': location})


@web_bp.route('/devices/<int:device_id>/update-notes', methods=['POST'])
@login_required
def device_update_notes(device_id):
    """Update device notes"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    notes = request.form.get('notes', '').strip()

    db = current_app.db

    with db.session() as session:
        stmt = select(Device).where(Device.id == device_id)
        device = session.execute(stmt).scalar_one_or_none()

        if not device:
            return jsonify({'error': 'Device not found'}), 404

        device.notes = notes if notes else None
        session.commit()

        flash(f'Device notes updated', 'success')

    return jsonify({'success': True, 'notes': notes})
