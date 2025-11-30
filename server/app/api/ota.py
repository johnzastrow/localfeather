"""
Local Feather - OTA Update API Endpoints

Handles firmware update checks and downloads for ESP32 devices.
"""

from flask import request, jsonify, current_app, send_file
from datetime import datetime
import os

from app.api import api_bp
from app.models import Device, Firmware, DeviceUpdate
from app.database import get_db


@api_bp.route('/ota/check', methods=['GET'])
def ota_check():
    """
    Check if a firmware update is available.

    Query parameters:
        device_id: Device identifier
        version: Current firmware version

    Returns:
        200: Update information
        {
            "update_available": true/false,
            "current_version": "1.0.0",
            "new_version": "1.0.1",
            "file_size": 987654,
            "url": "/api/ota/download/1.0.1",
            "release_notes": "..."
        }
    """
    try:
        device_id = request.args.get('device_id')
        current_version = request.args.get('version', '0.0.0')

        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400

        db = get_db()

        with db.session_scope() as session:
            # Verify device exists
            device = session.query(Device).filter_by(device_id=device_id).first()
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            # Get latest active firmware
            latest_firmware = session.query(Firmware)\
                .filter_by(active=True)\
                .order_by(Firmware.uploaded_at.desc())\
                .first()

            if not latest_firmware:
                return jsonify({
                    'update_available': False,
                    'current_version': current_version,
                    'message': 'No firmware available'
                }), 200

            # Check if update is needed
            update_available = latest_firmware.version != current_version

            response = {
                'update_available': update_available,
                'current_version': current_version
            }

            if update_available:
                response.update({
                    'new_version': latest_firmware.version,
                    'file_size': latest_firmware.file_size,
                    'url': f'/api/ota/download/{latest_firmware.version}',
                    'release_notes': latest_firmware.release_notes
                })

                current_app.logger.info(
                    f"OTA update available for {device_id}: "
                    f"{current_version} → {latest_firmware.version}"
                )
            else:
                current_app.logger.debug(
                    f"No OTA update for {device_id}: already on {current_version}"
                )

            return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Error checking OTA update: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/ota/download/<version>', methods=['GET'])
def ota_download(version):
    """
    Download a specific firmware version.

    Path parameter:
        version: Firmware version to download

    Query parameter:
        device_id: Device requesting the update (for tracking)

    Returns:
        200: Binary firmware file
        404: Firmware not found
    """
    try:
        device_id = request.args.get('device_id')

        db = get_db()

        with db.session_scope() as session:
            # Get firmware record
            firmware = session.query(Firmware).filter_by(
                version=version,
                active=True
            ).first()

            if not firmware:
                return jsonify({'error': 'Firmware not found'}), 404

            # Track the update attempt
            if device_id:
                device = session.query(Device).filter_by(device_id=device_id).first()
                if device:
                    # Create update record
                    update = DeviceUpdate(
                        device_id=device.id,
                        firmware_id=firmware.id,
                        previous_version=device.firmware_version,
                        new_version=version,
                        status='downloading'
                    )
                    session.add(update)

                    # Increment download count
                    firmware.download_count += 1

                    session.commit()

                    current_app.logger.info(
                        f"OTA download started: {device_id} → {version}"
                    )

            # Get firmware file path
            # TODO: Implement actual file storage
            # For now, return placeholder
            firmware_dir = '/tmp/firmware'  # Placeholder
            firmware_path = os.path.join(firmware_dir, firmware.filename)

            if not os.path.exists(firmware_path):
                current_app.logger.error(f"Firmware file not found: {firmware_path}")
                return jsonify({'error': 'Firmware file not found on server'}), 404

            return send_file(
                firmware_path,
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f"firmware_{version}.bin"
            )

    except Exception as e:
        current_app.logger.error(f"Error downloading firmware: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/ota/status', methods=['POST'])
def ota_status():
    """
    Report OTA update status from device.

    JSON body:
        device_id: Device identifier
        version: Firmware version that was installed
        status: 'success' or 'failed'
        error_message: Error details if failed

    Returns:
        200: Status recorded
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        device_id = data.get('device_id')
        version = data.get('version')
        status = data.get('status')
        error_message = data.get('error_message')

        if not all([device_id, version, status]):
            return jsonify({'error': 'Missing required fields'}), 400

        db = get_db()

        with db.session_scope() as session:
            device = session.query(Device).filter_by(device_id=device_id).first()
            if not device:
                return jsonify({'error': 'Device not found'}), 404

            # Find the update record
            update = session.query(DeviceUpdate)\
                .filter_by(device_id=device.id, new_version=version)\
                .order_by(DeviceUpdate.update_started_at.desc())\
                .first()

            if update:
                update.status = status
                update.update_completed_at = datetime.utcnow()
                if error_message:
                    update.error_message = error_message

            # Update device firmware version if successful
            if status == 'success':
                device.firmware_version = version

            session.commit()

            current_app.logger.info(
                f"OTA update {status}: {device_id} → {version}"
            )

            return jsonify({
                'status': 'ok',
                'message': 'Update status recorded'
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error recording OTA status: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
