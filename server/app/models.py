"""
Local Feather - SQLAlchemy Database Models

These models map to the MariaDB schema defined in database/schema.sql
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime,
    DECIMAL, BigInteger, Enum, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """Web UI user accounts with authentication"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum('admin', 'viewer', name='user_role'),
        nullable=False,
        default='viewer'
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    uploaded_firmware: Mapped[List["Firmware"]] = relationship("Firmware", back_populates="uploader")
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == 'admin'


class Device(Base):
    """ESP32 device information and configuration"""
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment='Unique device identifier (e.g., esp32-a1b2c3)'
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment='User-friendly device name'
    )
    api_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment='API authentication key'
    )
    approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        comment='Whether device is approved to send data'
    )
    firmware_version: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment='Current firmware version (e.g., 1.0.0)'
    )
    reading_interval: Mapped[int] = mapped_column(
        Integer,
        default=60000,
        comment='Reading interval in milliseconds'
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        comment='Last known IP address (IPv4 or IPv6)'
    )
    mac_address: Mapped[Optional[str]] = mapped_column(
        String(17),
        comment='Device MAC address'
    )
    wifi_ssid: Mapped[Optional[str]] = mapped_column(
        String(32),
        comment='Connected WiFi network'
    )
    signal_strength: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment='WiFi signal strength in dBm'
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment='Physical location description'
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment='User notes about the device'
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment='Last successful communication'
    )
    last_reading_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='Last reading received'
    )
    total_readings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment='Total number of readings received'
    )

    # Relationships
    readings: Mapped[List["Reading"]] = relationship(
        "Reading",
        back_populates="device",
        cascade="all, delete-orphan"
    )
    updates: Mapped[List["DeviceUpdate"]] = relationship(
        "DeviceUpdate",
        back_populates="device",
        cascade="all, delete-orphan"
    )
    logs: Mapped[List["DeviceLog"]] = relationship(
        "DeviceLog",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Device {self.device_id} ({self.name or 'Unnamed'})>"

    def is_online(self, threshold_minutes: int = 10) -> bool:
        """Check if device has been seen recently"""
        if not self.last_seen:
            return False
        delta = datetime.utcnow() - self.last_seen
        return delta.total_seconds() < (threshold_minutes * 60)


class Reading(Base):
    """Sensor readings from devices"""
    __tablename__ = 'readings'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        nullable=False,
        comment='Foreign key to devices table'
    )
    sensor: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment='Sensor type (e.g., temperature, humidity)'
    )
    value: Mapped[float] = mapped_column(
        DECIMAL(10, 4),
        nullable=False,
        comment='Sensor reading value'
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='Unit of measurement (e.g., C, %, hPa)'
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        index=True,
        comment='Reading timestamp from device'
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        comment='Server received timestamp'
    )

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="readings")

    # Indexes
    __table_args__ = (
        Index('idx_device_sensor', 'device_id', 'sensor'),
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_readings_device_time_sensor', 'device_id', 'timestamp', 'sensor'),
    )

    def __repr__(self):
        return f"<Reading {self.sensor}={self.value}{self.unit} @ {self.timestamp}>"


class Firmware(Base):
    """Firmware binaries for OTA updates"""
    __tablename__ = 'firmware'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment='Firmware version (e.g., 1.0.1)'
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Stored filename on disk'
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment='Original uploaded filename'
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='File size in bytes'
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment='SHA-256 hash of firmware file'
    )
    release_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        comment='Release notes for this version'
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL')
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        comment='Whether this version is available for OTA'
    )
    download_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment='Number of times downloaded'
    )

    # Relationships
    uploader: Mapped[Optional["User"]] = relationship("User", back_populates="uploaded_firmware")
    device_updates: Mapped[List["DeviceUpdate"]] = relationship(
        "DeviceUpdate",
        back_populates="firmware"
    )

    def __repr__(self):
        return f"<Firmware v{self.version} ({'active' if self.active else 'inactive'})>"


class DeviceUpdate(Base):
    """Tracks which devices have updated to which firmware versions"""
    __tablename__ = 'device_updates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        nullable=False
    )
    firmware_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('firmware.id', ondelete='CASCADE'),
        nullable=False
    )
    previous_version: Mapped[Optional[str]] = mapped_column(String(20))
    new_version: Mapped[str] = mapped_column(String(20), nullable=False)
    update_started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    update_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum('pending', 'downloading', 'success', 'failed', name='update_status'),
        default='pending'
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="updates")
    firmware: Mapped["Firmware"] = relationship("Firmware", back_populates="device_updates")

    # Indexes
    __table_args__ = (
        Index('idx_device_status', 'device_id', 'status'),
    )

    def __repr__(self):
        return f"<DeviceUpdate {self.new_version} ({self.status})>"


class Setting(Base):
    """Application configuration as key-value pairs"""
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    setting_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment='Setting identifier'
    )
    setting_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment='Setting value (JSON for complex types)'
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        comment='Human-readable description'
    )
    value_type: Mapped[str] = mapped_column(
        Enum('string', 'integer', 'boolean', 'json', name='setting_type'),
        default='string'
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL')
    )

    def __repr__(self):
        return f"<Setting {self.setting_key}={self.setting_value}>"

    def get_typed_value(self):
        """Return the setting value converted to its proper type"""
        if self.value_type == 'integer':
            return int(self.setting_value)
        elif self.value_type == 'boolean':
            return self.setting_value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.setting_value)
        else:
            return self.setting_value


class APIKey(Base):
    """API tokens for external integrations"""
    __tablename__ = 'api_keys'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='Descriptive name for this key'
    )
    api_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment='The actual API key'
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE')
    )
    permissions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment='JSON object defining permissions'
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='Optional expiration date'
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey {self.key_name} ({'active' if self.active else 'inactive'})>"

    def is_expired(self) -> bool:
        """Check if the API key has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class DeviceLog(Base):
    """Stores important events and errors from devices"""
    __tablename__ = 'device_logs'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    device_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        nullable=False
    )
    log_level: Mapped[str] = mapped_column(
        Enum('debug', 'info', 'warning', 'error', 'critical', name='log_level'),
        default='info'
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment='Additional structured log data'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        index=True
    )

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="logs")

    # Indexes
    __table_args__ = (
        Index('idx_device_level', 'device_id', 'log_level'),
    )

    def __repr__(self):
        return f"<DeviceLog [{self.log_level}] {self.message[:50]}>"


class Alert(Base):
    """Alert rules and triggered alerts"""
    __tablename__ = 'alerts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        comment='NULL = applies to all devices'
    )
    sensor: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='Which sensor to monitor'
    )
    condition: Mapped[str] = mapped_column(
        Enum('above', 'below', 'equals', name='alert_condition'),
        nullable=False
    )
    threshold: Mapped[float] = mapped_column(
        DECIMAL(10, 4),
        nullable=False,
        comment='Threshold value'
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    notify_email: Mapped[Optional[str]] = mapped_column(String(100))
    notify_webhook: Mapped[Optional[str]] = mapped_column(String(255))
    cooldown_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        comment='Minutes before re-alerting'
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_device_sensor', 'device_id', 'sensor'),
    )

    def __repr__(self):
        return f"<Alert {self.alert_name} ({self.sensor} {self.condition} {self.threshold})>"

    def can_trigger(self) -> bool:
        """Check if alert is ready to trigger (not in cooldown)"""
        if not self.enabled:
            return False
        if not self.last_triggered_at:
            return True
        delta = datetime.utcnow() - self.last_triggered_at
        return delta.total_seconds() > (self.cooldown_minutes * 60)
