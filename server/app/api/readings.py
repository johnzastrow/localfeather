"""
Local Feather - Readings API Endpoints

Handles sensor reading submissions from ESP32 devices.
"""

from flask import request, jsonify, current_app
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal
import secrets

from app.api import api_bp
from app.models import Device, Reading
from app.database import get_db


def get_rate_limit_key():
    """Get rate limit key based on device_id if available, else IP address"""
    data = request.get_json(silent=True)
    if data and 'device_id' in data:
        return f"device:{data['device_id']}"
    return f"ip:{request.remote_addr}"


@api_bp.route('/readings', methods=['POST'])
def post_readings():
    """
    Receive sensor readings from ESP32 devices.

    Rate limit: 60 requests per minute per device.

    Expected JSON payload:
    {
        "device_id": "esp32-a1b2c3",
        "api_key": "...",  # Optional on first connection
        "readings": [
            {
                "sensor": "temperature",
                "value": 23.5,
                "unit": "C",
                "timestamp": 1234567890  # Optional
            }
        ]
    }

    Returns:
        200: Success with response data
        400: Bad request (missing fields)
        401: Unauthorized (invalid API key)
        403: Forbidden (device not approved)
        500: Server error
    """
    try:
        # Parse JSON payload
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required fields
        device_id = data.get('device_id')
        api_key = data.get('api_key', '')
        readings_data = data.get('readings', [])

        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400

        if not readings_data:
            return jsonify({'error': 'readings array is required'}), 400

        db = get_db()

        with db.session_scope() as session:
            # Find or create device
            device = session.query(Device).filter_by(device_id=device_id).first()

            # First-time device registration
            if not device:
                current_app.logger.info(f"New device registration: {device_id}")

                # Generate API key if not provided
                if not api_key:
                    api_key = secrets.token_hex(32)

                # Store plaintext key to return to device
                plaintext_api_key = api_key

                # Hash the API key for storage
                hashed_api_key = generate_password_hash(api_key).decode('utf-8')

                # Create new device
                device = Device(
                    device_id=device_id,
                    api_key=hashed_api_key,  # Store hashed key
                    approved=False,  # Requires admin approval
                    firmware_version=data.get('firmware_version'),
                    ip_address=request.remote_addr,
                    last_seen=datetime.utcnow()
                )
                session.add(device)
                session.flush()  # Get device.id

                current_app.logger.info(f"Device registered: {device_id} (approval required)")

                # Return plaintext API key to device (only time it's sent)
                return jsonify({
                    'status': 'registered',
                    'message': 'Device registered successfully. Awaiting approval.',
                    'api_key': plaintext_api_key,  # Return plaintext key
                    'approved': False,
                    'device_id': device_id
                }), 200

            # Verify API key for existing devices
            if not check_password_hash(device.api_key, api_key):
                current_app.logger.warning(f"Invalid API key for device: {device_id}")
                return jsonify({'error': 'Invalid API key'}), 401

            # Check if device is approved
            if not device.approved:
                current_app.logger.info(f"Unapproved device attempted to send data: {device_id}")
                return jsonify({
                    'status': 'pending_approval',
                    'message': 'Device is not approved yet. Please contact administrator.',
                    'approved': False
                }), 403

            # Update device metadata
            device.last_seen = datetime.utcnow()
            device.ip_address = request.remote_addr

            # Update firmware version if provided
            if 'firmware_version' in data:
                device.firmware_version = data['firmware_version']

            # Update network information if provided
            if 'mac_address' in data:
                device.mac_address = data['mac_address']
            if 'wifi_ssid' in data:
                device.wifi_ssid = data['wifi_ssid']
            if 'signal_strength' in data:
                device.signal_strength = data['signal_strength']

            # Process readings
            readings_created = 0
            for reading_data in readings_data:
                sensor = reading_data.get('sensor')
                value = reading_data.get('value')
                unit = reading_data.get('unit')
                timestamp = reading_data.get('timestamp')

                # Validate reading data
                if not all([sensor, value is not None, unit]):
                    current_app.logger.warning(f"Invalid reading data: {reading_data}")
                    continue

                # Convert timestamp if provided (Unix timestamp)
                if timestamp:
                    try:
                        dt = datetime.fromtimestamp(timestamp)
                    except (ValueError, OSError):
                        dt = datetime.utcnow()
                else:
                    dt = datetime.utcnow()

                # Create reading
                reading = Reading(
                    device_id=device.id,
                    sensor=sensor,
                    value=Decimal(str(value)),
                    unit=unit,
                    timestamp=dt,
                    received_at=datetime.utcnow()
                )
                session.add(reading)
                readings_created += 1

            # Update device stats
            device.last_reading_at = datetime.utcnow()
            device.total_readings += readings_created

            # Commit all changes
            session.commit()

            current_app.logger.info(
                f"Received {readings_created} readings from {device_id}"
            )

            # Prepare response
            response = {
                'status': 'ok',
                'message': 'Readings received successfully',
                'received': readings_created,
                'device_id': device_id,
                'approved': True,
                'server_time': int(datetime.utcnow().timestamp()),
            }

            # Include reading interval if device should update it
            if device.reading_interval:
                response['reading_interval'] = device.reading_interval

            return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Error processing readings: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/readings', methods=['GET'])
def get_readings():
    """
    Get readings (for web UI or external API).

    Query parameters:
        device_id: Filter by device
        sensor: Filter by sensor type
        limit: Number of readings to return (default 100, max 1000)
        offset: Pagination offset

    Returns:
        200: List of readings
    """
    try:
        db = get_db()

        # Parse query parameters
        device_id_filter = request.args.get('device_id')
        sensor_filter = request.args.get('sensor')
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))

        with db.session_scope() as session:
            query = session.query(Reading)

            # Apply filters
            if device_id_filter:
                device = session.query(Device).filter_by(
                    device_id=device_id_filter
                ).first()
                if device:
                    query = query.filter_by(device_id=device.id)

            if sensor_filter:
                query = query.filter_by(sensor=sensor_filter)

            # Order and paginate
            query = query.order_by(Reading.timestamp.desc())
            query = query.limit(limit).offset(offset)

            readings = query.all()

            # Format response
            return jsonify({
                'readings': [
                    {
                        'id': r.id,
                        'device_id': r.device_id,
                        'sensor': r.sensor,
                        'value': float(r.value),
                        'unit': r.unit,
                        'timestamp': r.timestamp.isoformat(),
                        'received_at': r.received_at.isoformat()
                    }
                    for r in readings
                ],
                'count': len(readings),
                'limit': limit,
                'offset': offset
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching readings: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
