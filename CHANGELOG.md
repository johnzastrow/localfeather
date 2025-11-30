# Changelog

All notable changes to the Local Feather project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Flask server implementation
- MariaDB database schema and migrations
- Web UI with HTMX and Tailwind CSS
- User authentication and authorization
- Device management interface
- Data visualization with Chart.js
- CSV/JSON export functionality
- Docker Compose deployment
- Installation scripts for Raspberry Pi

## [1.0.0] - 2025-11-30

### Added - Firmware v1.0.0

**Core Features:**
- Complete ESP32 firmware with PlatformIO build system
- WiFiManager captive portal for easy WiFi configuration
- Automatic device registration with server
- BME280 sensor support (temperature, humidity, pressure)
- AHT20 sensor support (temperature, humidity) - Adafruit #4566
- HTTPS POST communication to server
- JSON payload serialization with ArduinoJson
- NVS storage for configuration persistence
- Watchdog timer for automatic crash recovery
- LED status indicators for visual feedback
- Retry logic with exponential backoff
- Configurable reading intervals (default 60 seconds)

**OTA Updates (Fully Implemented):**
- Over-the-air firmware update support
- Automatic update checking every 6 hours
- Download progress monitoring
- Dual partition system for safe updates
- Automatic rollback on failed boot (after 3 attempts)
- Version management and comparison
- Comprehensive OTA documentation in `firmware/docs/OTA_GUIDE.md`

**Sensor Examples:**
- DHT22 temperature/humidity sensor (`examples/dht22/`)
- DS18B20 waterproof temperature sensor (`examples/ds18b20/`)
- Analog sensors (soil moisture, LDR, voltage) (`examples/analog/`)
- Multi-sensor setup combining multiple sensors (`examples/multi_sensor/`)
- AHT20 temperature/humidity sensor (`examples/aht20/`)

**Documentation:**
- Comprehensive firmware README with installation guide
- Hardware wiring diagrams for all supported sensors
- First-time setup walkthrough
- Troubleshooting guide for common issues
- OTA update guide with production deployment checklist
- Sensor migration guides (BME280 ↔ AHT20)

### Added - Project Documentation

**Architecture & Design:**
- REQUIREMENTS.md - Complete project requirements and user stories
- DESIGN.md - Simplified architecture (Flask + MariaDB + HTMX)
- CLAUDE.md - Development guide for AI assistants
- API.md - Complete API specification
- SETUP.md - Step-by-step setup guide for non-technical users
- DEPLOYMENT.md - Production deployment guide
- TROUBLESHOOTING.md - Common problems and solutions

**Design Decisions:**
- Simplified stack: Flask instead of FastAPI, HTMX instead of React
- MariaDB as primary database (SQLite for development only)
- Focus on non-technical user installation (<30 minutes)
- Local-network only, no cloud dependencies
- Clear growth paths from v1.0 → v2.0 → v3.0

### Technical Specifications

**Firmware:**
- Platform: ESP32 (espressif32)
- Framework: Arduino
- Build System: PlatformIO
- Language: C++
- Flash Partition: Dual OTA partitions (2x 1.3MB)
- Memory Usage: ~60KB RAM (including WiFi stack)

**Libraries:**
- WiFiManager 2.0.16-rc.2
- ArduinoJson 6.21.3
- Adafruit BME280 Library 2.2.2
- Adafruit AHTX0 2.0.3
- Adafruit Unified Sensor 1.1.9
- Adafruit BusIO 1.14.1

**Supported Hardware:**
- ESP32 Dev Module
- ESP32 Feather (Adafruit, Unexpected Maker)
- ESP32-S2/S3 (with minor modifications)
- BME280 sensor (I2C, address 0x76 or 0x77)
- AHT20 sensor (I2C, address 0x38)
- DHT22, DS18B20, analog sensors (via examples)

### Changed

**Architecture Simplification:**
- Removed: MQTT broker, React frontend, Nginx, PostgreSQL
- Replaced FastAPI with Flask for simplicity
- Changed primary database from SQLite to MariaDB
- Simplified frontend from React to Jinja2 + HTMX

### Fixed

**Repository Structure:**
- Removed duplicate nested `localfeather/` directory
- Consolidated all files to correct top-level structure
- Cleaned up documentation duplication

## [0.1.0] - 2025-11-29

### Added
- Initial project structure
- Original design documentation (now in `old/OLDDESIGN.md`)
- License (MIT)
- Basic README

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-11-30 | Complete ESP32 firmware with OTA, sensors, and documentation |
| 0.1.0 | 2025-11-29 | Initial project setup |

## Notes

**Current Status:**
- ✅ ESP32 firmware: **COMPLETE** (v1.0.0)
- ⏳ Flask server: Not started
- ⏳ Database schema: Not started
- ⏳ Web UI: Not started
- ⏳ Deployment: Not started

**Next Milestone:** Flask server implementation with MariaDB integration.

## Git Commits Reference

For detailed commit history, see:
```bash
git log --oneline --graph
```

Key commits:
- `33367b9` - Add AHT20 sensor support (2025-11-30)
- `f6f31ed` - Implement full OTA updates (2025-11-29)
- `6ef70f3` - Add sensor examples (2025-11-29)
- `684c33c` - Add troubleshooting and design docs (2025-11-29)
- `c06c4ae` - Add design and requirements (2025-11-29)
- `5f2cb9d` - Initial commit (2025-11-29)
