"""
Local Feather - Devices API Endpoints

Handles device management and queries.
"""

from flask import request, jsonify, current_app
from datetime import datetime

from app.api import api_bp
from app.models import Device
from app.database import get_db


@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """
    Get all devices.

    Query parameters:
        approved: Filter by approval status (true/false)
        online: Filter by online status (true/false)

    Returns:
        200: List of devices
    """
    try:
        db = get_db()

        # Parse query parameters
        approved_filter = request.args.get('approved')
        online_filter = request.args.get('online')

        with db.session_scope() as session:
            query = session.query(Device)

            # Apply filters
            if approved_filter is not None:
                approved = approved_filter.lower() == 'true'
                query = query.filter_by(approved=approved)

            devices = query.all()

            # Filter by online status if requested
            if online_filter is not None:
                online = online_filter.lower() == 'true'
                devices = [d for d in devices if d.is_online() == online]

            # Format response
            return jsonify({
                'devices': [
                    {
                        'id': d.id,
                        'device_id': d.device_id,
                        'name': d.name,
                        'approved': d.approved,
                        'firmware_version': d.firmware_version,
                        'reading_interval': d.reading_interval,
                        'ip_address': d.ip_address,
                        'mac_address': d.mac_address,
                        'wifi_ssid': d.wifi_ssid,
                        'signal_strength': d.signal_strength,
                        'location': d.location,
                        'notes': d.notes,
                        'last_seen': d.last_seen.isoformat() if d.last_seen else None,
                        'last_reading_at': d.last_reading_at.isoformat() if d.last_reading_at else None,
                        'total_readings': d.total_readings,
                        'online': d.is_online()
                    }
                    for d in devices
                ],
                'count': len(devices)
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching devices: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """
    Get a specific device by device_id.

    Returns:
        200: Device details
        404: Device not found
    """
    try:
        db = get_db()

        with db.session_scope() as session:
            device = session.query(Device).filter_by(device_id=device_id).first()

            if not device:
                return jsonify({'error': 'Device not found'}), 404

            return jsonify({
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name,
                'approved': device.approved,
                'firmware_version': device.firmware_version,
                'reading_interval': device.reading_interval,
                'ip_address': device.ip_address,
                'mac_address': device.mac_address,
                'wifi_ssid': device.wifi_ssid,
                'signal_strength': device.signal_strength,
                'location': device.location,
                'notes': device.notes,
                'created_at': device.created_at.isoformat(),
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'last_reading_at': device.last_reading_at.isoformat() if device.last_reading_at else None,
                'total_readings': device.total_readings,
                'online': device.is_online()
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching device: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/devices/<device_id>/approve', methods=['POST'])
def approve_device(device_id):
    """
    Approve a device (admin only - auth to be added).

    Returns:
        200: Device approved
        404: Device not found
    """
    try:
        db = get_db()

        with db.session_scope() as session:
            device = session.query(Device).filter_by(device_id=device_id).first()

            if not device:
                return jsonify({'error': 'Device not found'}), 404

            device.approved = True
            session.commit()

            current_app.logger.info(f"Device approved: {device_id}")

            return jsonify({
                'status': 'ok',
                'message': 'Device approved successfully',
                'device_id': device_id,
                'approved': True
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error approving device: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """
    Update device settings.

    JSON body can include:
        name: User-friendly name
        location: Physical location
        notes: User notes
        reading_interval: Reading interval in milliseconds

    Returns:
        200: Device updated
        404: Device not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        db = get_db()

        with db.session_scope() as session:
            device = session.query(Device).filter_by(device_id=device_id).first()

            if not device:
                return jsonify({'error': 'Device not found'}), 404

            # Update allowed fields
            if 'name' in data:
                device.name = data['name']
            if 'location' in data:
                device.location = data['location']
            if 'notes' in data:
                device.notes = data['notes']
            if 'reading_interval' in data:
                device.reading_interval = int(data['reading_interval'])

            session.commit()

            current_app.logger.info(f"Device updated: {device_id}")

            return jsonify({
                'status': 'ok',
                'message': 'Device updated successfully',
                'device_id': device_id
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error updating device: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """
    Delete a device (admin only - auth to be added).

    Returns:
        200: Device deleted
        404: Device not found
    """
    try:
        db = get_db()

        with db.session_scope() as session:
            device = session.query(Device).filter_by(device_id=device_id).first()

            if not device:
                return jsonify({'error': 'Device not found'}), 404

            session.delete(device)
            session.commit()

            current_app.logger.info(f"Device deleted: {device_id}")

            return jsonify({
                'status': 'ok',
                'message': 'Device deleted successfully',
                'device_id': device_id
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting device: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
