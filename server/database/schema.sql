-- ============================================================================
-- Local Feather - Database Schema
-- ============================================================================
-- MariaDB 10.5+ Schema Definition
-- Version: 1.0.0
-- Created: 2025-11-30
-- ============================================================================

-- Create database (run this first if database doesn't exist)
-- CREATE DATABASE IF NOT EXISTS localfeather CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE localfeather;

-- ============================================================================
-- Users Table
-- ============================================================================
-- Stores web UI user accounts with authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'viewer') NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL DEFAULT NULL,
    active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Devices Table
-- ============================================================================
-- Stores ESP32 device information and configuration
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL UNIQUE COMMENT 'Unique device identifier (e.g., esp32-a1b2c3)',
    name VARCHAR(100) DEFAULT NULL COMMENT 'User-friendly device name',
    api_key VARCHAR(64) NOT NULL UNIQUE COMMENT 'API authentication key',
    approved BOOLEAN DEFAULT FALSE COMMENT 'Whether device is approved to send data',
    firmware_version VARCHAR(20) DEFAULT NULL COMMENT 'Current firmware version (e.g., 1.0.0)',
    reading_interval INT DEFAULT 60000 COMMENT 'Reading interval in milliseconds',
    ip_address VARCHAR(45) DEFAULT NULL COMMENT 'Last known IP address (IPv4 or IPv6)',
    mac_address VARCHAR(17) DEFAULT NULL COMMENT 'Device MAC address',
    wifi_ssid VARCHAR(32) DEFAULT NULL COMMENT 'Connected WiFi network',
    signal_strength INT DEFAULT NULL COMMENT 'WiFi signal strength in dBm',
    location VARCHAR(100) DEFAULT NULL COMMENT 'Physical location description',
    notes TEXT DEFAULT NULL COMMENT 'User notes about the device',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NULL DEFAULT NULL COMMENT 'Last successful communication',
    last_reading_at TIMESTAMP NULL DEFAULT NULL COMMENT 'Last reading received',
    total_readings INT DEFAULT 0 COMMENT 'Total number of readings received',
    INDEX idx_device_id (device_id),
    INDEX idx_api_key (api_key),
    INDEX idx_approved (approved),
    INDEX idx_last_seen (last_seen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Readings Table
-- ============================================================================
-- Stores all sensor readings from devices
CREATE TABLE IF NOT EXISTS readings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL COMMENT 'Foreign key to devices table',
    sensor VARCHAR(50) NOT NULL COMMENT 'Sensor type (e.g., temperature, humidity)',
    value DECIMAL(10, 4) NOT NULL COMMENT 'Sensor reading value',
    unit VARCHAR(20) NOT NULL COMMENT 'Unit of measurement (e.g., C, %, hPa)',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Reading timestamp from device',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Server received timestamp',
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_sensor (device_id, sensor),
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_timestamp (device_id, timestamp),
    INDEX idx_sensor (sensor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Partition the readings table by month for better performance
-- Uncomment when table has data:
-- ALTER TABLE readings PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
--     PARTITION p_2025_11 VALUES LESS THAN (UNIX_TIMESTAMP('2025-12-01')),
--     PARTITION p_2025_12 VALUES LESS THAN (UNIX_TIMESTAMP('2026-01-01')),
--     PARTITION p_future VALUES LESS THAN MAXVALUE
-- );

-- ============================================================================
-- Firmware Table
-- ============================================================================
-- Stores firmware binaries for OTA updates
CREATE TABLE IF NOT EXISTS firmware (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE COMMENT 'Firmware version (e.g., 1.0.1)',
    filename VARCHAR(255) NOT NULL COMMENT 'Stored filename on disk',
    original_filename VARCHAR(255) NOT NULL COMMENT 'Original uploaded filename',
    file_size INT NOT NULL COMMENT 'File size in bytes',
    file_hash VARCHAR(64) NOT NULL COMMENT 'SHA-256 hash of firmware file',
    release_notes TEXT DEFAULT NULL COMMENT 'Release notes for this version',
    uploaded_by INT DEFAULT NULL COMMENT 'User who uploaded (foreign key to users)',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE COMMENT 'Whether this version is available for OTA',
    download_count INT DEFAULT 0 COMMENT 'Number of times downloaded',
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_version (version),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Device Updates Table
-- ============================================================================
-- Tracks which devices have updated to which firmware versions
CREATE TABLE IF NOT EXISTS device_updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    firmware_id INT NOT NULL,
    previous_version VARCHAR(20) DEFAULT NULL,
    new_version VARCHAR(20) NOT NULL,
    update_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_completed_at TIMESTAMP NULL DEFAULT NULL,
    status ENUM('pending', 'downloading', 'success', 'failed') DEFAULT 'pending',
    error_message TEXT DEFAULT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    FOREIGN KEY (firmware_id) REFERENCES firmware(id) ON DELETE CASCADE,
    INDEX idx_device_status (device_id, status),
    INDEX idx_firmware (firmware_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Settings Table
-- ============================================================================
-- Stores application configuration as key-value pairs
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE COMMENT 'Setting identifier',
    setting_value TEXT NOT NULL COMMENT 'Setting value (JSON for complex types)',
    description TEXT DEFAULT NULL COMMENT 'Human-readable description',
    value_type ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT DEFAULT NULL COMMENT 'User who last updated',
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- API Keys Table (Optional - for future API token management)
-- ============================================================================
-- Stores API tokens for external integrations
CREATE TABLE IF NOT EXISTS api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) NOT NULL COMMENT 'Descriptive name for this key',
    api_key VARCHAR(64) NOT NULL UNIQUE COMMENT 'The actual API key',
    user_id INT DEFAULT NULL COMMENT 'User who created this key',
    permissions JSON DEFAULT NULL COMMENT 'JSON object defining permissions',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL DEFAULT NULL COMMENT 'Optional expiration date',
    last_used_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_api_key (api_key),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Device Logs Table
-- ============================================================================
-- Stores important events and errors from devices
CREATE TABLE IF NOT EXISTS device_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    log_level ENUM('debug', 'info', 'warning', 'error', 'critical') DEFAULT 'info',
    message TEXT NOT NULL,
    details JSON DEFAULT NULL COMMENT 'Additional structured log data',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_level (device_id, log_level),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Alerts Table (Future use)
-- ============================================================================
-- Stores alert rules and triggered alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    device_id INT DEFAULT NULL COMMENT 'NULL = applies to all devices',
    sensor VARCHAR(50) NOT NULL COMMENT 'Which sensor to monitor',
    condition ENUM('above', 'below', 'equals') NOT NULL,
    threshold DECIMAL(10, 4) NOT NULL COMMENT 'Threshold value',
    enabled BOOLEAN DEFAULT TRUE,
    notify_email VARCHAR(100) DEFAULT NULL,
    notify_webhook VARCHAR(255) DEFAULT NULL,
    cooldown_minutes INT DEFAULT 60 COMMENT 'Minutes before re-alerting',
    last_triggered_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_enabled (enabled),
    INDEX idx_device_sensor (device_id, sensor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Default Settings
-- ============================================================================
INSERT INTO settings (setting_key, setting_value, description, value_type) VALUES
    ('site_name', 'Local Feather', 'Application name displayed in UI', 'string'),
    ('default_reading_interval', '60000', 'Default reading interval in milliseconds', 'integer'),
    ('auto_approve_devices', 'false', 'Automatically approve new devices', 'boolean'),
    ('data_retention_days', '365', 'Days to keep reading data (0 = forever)', 'integer'),
    ('enable_ota_updates', 'true', 'Allow OTA firmware updates', 'boolean'),
    ('max_devices', '50', 'Maximum number of devices allowed', 'integer'),
    ('timezone', 'America/New_York', 'Server timezone', 'string')
ON DUPLICATE KEY UPDATE setting_value=setting_value;

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- Latest reading for each sensor on each device
CREATE OR REPLACE VIEW latest_readings AS
SELECT
    r.id,
    r.device_id,
    d.device_id AS device_identifier,
    d.name AS device_name,
    r.sensor,
    r.value,
    r.unit,
    r.timestamp,
    r.received_at
FROM readings r
INNER JOIN (
    SELECT device_id, sensor, MAX(timestamp) AS max_timestamp
    FROM readings
    GROUP BY device_id, sensor
) latest ON r.device_id = latest.device_id
    AND r.sensor = latest.sensor
    AND r.timestamp = latest.max_timestamp
INNER JOIN devices d ON r.device_id = d.id;

-- Device statistics summary
CREATE OR REPLACE VIEW device_stats AS
SELECT
    d.id,
    d.device_id,
    d.name,
    d.approved,
    d.firmware_version,
    d.last_seen,
    d.total_readings,
    COUNT(DISTINCT r.sensor) AS sensor_count,
    MIN(r.timestamp) AS first_reading_at,
    MAX(r.timestamp) AS last_reading_at,
    TIMESTAMPDIFF(HOUR, d.last_seen, NOW()) AS hours_since_seen
FROM devices d
LEFT JOIN readings r ON d.id = r.device_id
GROUP BY d.id;

-- ============================================================================
-- Performance Optimization
-- ============================================================================

-- Create composite indexes for common query patterns
CREATE INDEX idx_readings_device_time_sensor ON readings(device_id, timestamp DESC, sensor);

-- ============================================================================
-- Cleanup / Maintenance Procedures
-- ============================================================================

-- Stored procedure to clean up old readings (run periodically)
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS cleanup_old_readings(IN days_to_keep INT)
BEGIN
    DELETE FROM readings
    WHERE timestamp < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);

    SELECT ROW_COUNT() AS rows_deleted;
END //
DELIMITER ;

-- Stored procedure to update device statistics
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS update_device_stats()
BEGIN
    UPDATE devices d
    LEFT JOIN (
        SELECT device_id, COUNT(*) AS total
        FROM readings
        GROUP BY device_id
    ) r ON d.id = r.device_id
    SET d.total_readings = COALESCE(r.total, 0);
END //
DELIMITER ;

-- ============================================================================
-- Database Information
-- ============================================================================
-- Display table sizes and row counts
SELECT
    table_name AS 'Table',
    table_rows AS 'Rows',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = DATABASE()
ORDER BY (data_length + index_length) DESC;
