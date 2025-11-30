# Local Feather - Requirements

## Use Case

Local Feather enables ESP32 sensor devices to send data to a local database server over WiFi **without requiring internet access**. The system operates entirely on your local network, making it ideal for:

- Home automation and environmental monitoring
- Remote locations with limited or no internet
- Privacy-focused setups where data stays local
- Educational projects and hobbyist applications
- Small business sensor monitoring

The project prioritizes **simplicity** and **ease of use** for non-technical users while providing a solid foundation for advanced users to extend functionality.

## Primary Use Case

**Target User**: Home hobbyist or small office user with 5-20 ESP32 sensor devices sending temperature, humidity, or other environmental data to a local server (Raspberry Pi or similar).

**User Experience Goal**: "Plug in Raspberry Pi, flash ESP32, see sensor data on dashboard" with minimal technical knowledge required.

## Hardware Requirements

### Server (One of the following):

**Recommended: Raspberry Pi**
- Raspberry Pi 4 (2GB RAM minimum, 4GB recommended)
- Raspberry Pi 3 Model B+ (1GB RAM, will work but slower)
- 32GB+ microSD card (Class 10 or better)
- Power supply (official Raspberry Pi power supply recommended)
- Ethernet cable (optional but recommended for stability)

**Alternative: Linux Server/VM**
- Any AMD64 or ARM64 Linux system
- 2GB+ RAM
- 10GB+ free disk space
- Ubuntu 20.04+, Debian 11+, or similar

**Alternative: Windows Development Machine**
- Windows 10/11 with WSL2 (Windows Subsystem for Linux)
- 4GB+ RAM
- 10GB+ free disk space

### ESP32 Devices

**Recommended**: Adafruit ESP32 Feather boards
- Example: [Adafruit ESP32-S2 Feather](https://www.adafruit.com/product/5400)
- Any ESP32 or ESP32-S2/S3 board will work
- Minimum 4MB flash

**Sensors** (examples):
- [Adafruit STEMMA QT sensors](https://www.adafruit.com/product/4566) (temperature, humidity, pressure, light, etc.)
- Any I2C, SPI, or analog sensors compatible with ESP32
- Built-in sensors (hall effect, touch, etc.)

### Network Requirements

- WiFi router with 2.4GHz support (ESP32 requirement)
- DHCP enabled (automatic IP assignment)
- Devices and server on same network/subnet
- **No internet required** (optional for package installation and updates)

## Functional Requirements

### Core Features (v1.0)

**Device Management**:
- ✅ ESP32 connects to local WiFi via captive portal setup
- ✅ Multiple ESP32 devices supported (5-20 devices tested)
- ✅ Automatic device registration with server
- ✅ Device status monitoring (online/offline, last seen)
- ✅ Device naming and configuration via web interface

**Data Collection**:
- ✅ Send sensor readings from ESP32 to server via HTTPS
- ✅ Support multiple sensor types per device (temperature, humidity, etc.)
- ✅ Configurable reading intervals (default: 60 seconds)
- ✅ Timestamp synchronization (server provides time on connection)
- ✅ Graceful handling of network interruptions (retry with backoff)

**Data Storage**:
- ✅ Store readings in MariaDB database (primary support)
- ✅ Fallback SQLite support for single-device setups
- ✅ Automatic database schema management (migrations)
- ✅ Data retention policies (configurable, default: 90 days raw data)

**Web Interface**:
- ✅ Dashboard showing latest readings from all devices
- ✅ Time-series charts (24 hours, 7 days, 30 days views)
- ✅ Real-time updates (auto-refresh every 10 seconds)
- ✅ Device list with status indicators
- ✅ Per-device detail pages with charts
- ✅ Data export (CSV, JSON) for selected date ranges
- ✅ Simple, responsive design (works on desktop, tablet, mobile)

**Security & Authentication**:
- ✅ Web UI login with username/password
- ✅ Two user roles: Admin (full access), Viewer (read-only)
- ✅ Device authentication via API keys
- ✅ Optional HTTPS/TLS (HTTP by default for local network)
- ✅ Session-based authentication (no token management complexity)
- ✅ Rate limiting on API endpoints (prevent device flooding)

**Firmware Management**:
- ✅ Over-the-air (OTA) firmware updates for ESP32
- ✅ Upload new firmware via web interface
- ✅ Automatic device update notifications
- ✅ Safe rollback on failed updates

**Diagnostics & Troubleshooting**:
- ✅ Device online/offline status
- ✅ Last seen timestamps
- ✅ Error logging and display
- ✅ Health check endpoint
- ✅ Clear error messages for common issues

### Enhanced Features (v2.0 - Future)

**Advanced Data Management**:
- ⏳ Data aggregation (hourly/daily summaries for long-term storage)
- ⏳ Automatic data cleanup (configurable retention periods)
- ⏳ Data backup and restore via web interface
- ⏳ Database optimization tools

**Alerting**:
- ⏳ Threshold-based alerts (email, webhook)
- ⏳ Alert history and management
- ⏳ Configurable alert rules per sensor

**Integration**:
- ⏳ Home Assistant integration (MQTT bridge)
- ⏳ Webhook support for external services
- ⏳ Optional cloud backup/sync
- ⏳ Prometheus metrics endpoint

**Advanced UI**:
- ⏳ Interactive charts (zoom, pan)
- ⏳ Custom dashboards (drag-and-drop widgets)
- ⏳ Comparison views (multiple sensors/devices)
- ⏳ Mobile app (iOS/Android)

**Bidirectional Communication**:
- ⏳ Send commands to ESP32 devices (restart, config changes)
- ⏳ MQTT support for pub/sub patterns
- ⏳ Remote sensor calibration

## Non-Functional Requirements

### Usability

**Installation Simplicity** (Critical):
- Installation completes in <30 minutes for non-technical users
- Single-command installation on Raspberry Pi: `curl -sSL install.sh | bash`
- OR Docker Compose: `docker-compose up -d`
- Automatic dependency installation
- Clear, step-by-step documentation with screenshots
- Troubleshooting guide for common issues

**ESP32 Setup** (Critical):
- Flash firmware to ESP32 in <10 minutes
- Captive portal guides user through WiFi setup (no typing config files)
- Automatic server discovery on local network (mDNS)
- Fallback: Manual server IP entry
- Visual feedback (LED blinks) for connection status

**User Interface**:
- Intuitive navigation (no training required)
- Accessible on phone, tablet, desktop
- Works in modern browsers (Chrome, Firefox, Safari, Edge)
- Clear labels and help text
- Undo functionality for critical actions (device deletion, etc.)

### Performance

**Targets** (Raspberry Pi 4):
- Dashboard loads in <1 second on local network
- Chart rendering <1 second (7-day view)
- API response time <100ms per request
- Supports 20 devices @ 1 reading/minute = 20 requests/minute (trivial load)
- Memory usage <200MB total
- CPU usage <10% average
- Database queries <50ms for typical dashboard

**Scalability**:
- v1.0 tested for 5-20 devices
- v2.0 target: 50+ devices with PostgreSQL/MariaDB

### Reliability

**Uptime**:
- System runs 24/7 without manual intervention
- Automatic recovery from temporary failures
- Graceful degradation (server down = ESP32 retries)
- Auto-restart on crash (systemd, Docker health checks)

**Data Integrity**:
- No data loss during normal operation
- Database transactions for atomic writes
- Input validation prevents malformed data
- Backup mechanism for disaster recovery

**Network Resilience**:
- ESP32 retry logic: immediate, 30s, 5min intervals
- Server accepts batched readings after reconnection
- Clear status indication when devices are offline
- No data sent over internet (stays local)

### Maintainability

**Code Quality**:
- Simple, readable code (prioritize clarity over cleverness)
- Comprehensive comments for non-obvious logic
- Unit tests for critical paths (>70% coverage target)
- Integration tests for API endpoints
- Consistent code style (enforced by linters)

**Documentation**:
- README with quick start
- SETUP.md for detailed installation
- API.md for developers
- TROUBLESHOOTING.md for common issues
- Inline code documentation
- Architecture diagrams

**Modularity**:
- Sensor drivers are pluggable (easy to add new sensor types)
- Service layer isolates business logic
- Database abstraction allows switching (SQLite → MariaDB → PostgreSQL)
- Clear separation: routes → services → models

**Updates & Upgrades**:
- Database migrations handle schema changes
- Backward-compatible API changes
- Clear release notes
- Easy rollback procedure

### Security

**Threat Model**: Unauthorized access from devices on the **local network**. Internet-based attacks are out of scope (system is local-only).

**Authentication**:
- ✅ Web UI: Username/password (bcrypt hashed)
- ✅ Device API: API key per device (hashed storage)
- ✅ Session-based auth (secure cookies)
- ✅ CSRF protection on forms
- ✅ Rate limiting (prevent brute force)

**Data Protection**:
- ✅ Input validation (prevent injection attacks)
- ✅ Parameterized SQL queries (prevent SQL injection)
- ✅ API keys never logged
- ✅ Password reset mechanism (admin only in v1)

**Network Security**:
- ✅ Optional HTTPS/TLS (self-signed certs for local network)
- ✅ Default HTTP acceptable for trusted local networks
- ⏳ Certificate management guide for advanced users

**Privacy**:
- No telemetry or analytics sent to external servers
- No cloud dependencies (optional in v2)
- User data stays on local network
- Clear data retention policies

### Compatibility

**Database Support**:
- **Primary**: MariaDB 10.5+ (recommended for multi-device)
- **Fallback**: SQLite 3.35+ (single device or development)
- **Future**: PostgreSQL 12+ (v2.0 if requested)

**Operating Systems (Server)**:
- Raspberry Pi OS (Debian-based)
- Ubuntu 20.04+, 22.04 LTS
- Debian 11+
- Windows 10/11 with WSL2 (development)

**ESP32 Platforms**:
- Arduino IDE 2.0+
- PlatformIO (recommended for development)
- ESP-IDF (advanced users, future)

**Browsers (Web UI)**:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers on iOS/Android

### Resource Constraints

**Server Requirements**:
- Minimum: Raspberry Pi 3B+, 1GB RAM, 16GB storage
- Recommended: Raspberry Pi 4, 2GB RAM, 32GB storage
- Optimal: 4GB RAM for 20+ devices with MariaDB

**ESP32 Constraints**:
- Available RAM: ~160-200KB (after WiFi stack)
- Flash: 4-16MB depending on model
- Firmware size: <1MB target
- Network: 2.4GHz WiFi only

**Network Bandwidth**:
- Per device: ~1KB/minute @ 60s intervals
- 20 devices: ~20KB/minute = negligible
- OTA updates: ~500KB-1MB per device (infrequent)

### Development Constraints

**Technology Choices** (Justified):
- Flask 3.x (proven, simple, extensive ecosystem)
- MariaDB (free, performant, MySQL-compatible)
- HTMX (no build pipeline, modern UX)
- Jinja2 templates (server-rendered, fast development)
- SQLAlchemy (database abstraction)
- PlatformIO (reproducible ESP32 builds)

**Dependencies**:
- Minimize third-party libraries (reduce attack surface)
- Use well-maintained, popular projects
- Pin versions for reproducibility
- Regular security updates

### Regulatory & Standards

**WiFi Compliance**:
- ESP32 devices use certified modules (FCC, CE)
- Operate on 2.4GHz ISM band (globally available)
- Follow local WiFi power regulations

**Data Privacy**:
- No GDPR concerns (data stays local, no PII collected by default)
- User responsible for data handling in their use case
- Clear documentation on data storage and retention

**Open Source**:
- MIT or Apache 2.0 license
- No proprietary dependencies
- Community contributions welcome

## Out of Scope (Explicitly)

### v1.0 Does NOT Include:

- ❌ Cloud integration (no AWS, Azure, Google Cloud)
- ❌ Mobile native apps (web UI is responsive)
- ❌ Complex analytics (basic charts only)
- ❌ Multi-tenant support (single installation per network)
- ❌ Real-time streaming (polling is sufficient)
- ❌ Support for non-ESP32 devices
- ❌ Machine learning / AI predictions
- ❌ Video/image storage
- ❌ External API integrations (Home Assistant, etc.)
- ❌ Localization/translation (English only)
- ❌ Advanced user permissions (only admin/viewer)

These features may be added in v2.0+ if there is demand.

## Success Criteria

Version 1.0 is considered **successful** if:

1. ✅ A non-technical user can install on Raspberry Pi in <30 minutes
2. ✅ ESP32 device is provisioned and sending data in <15 minutes
3. ✅ System runs continuously for 30 days without intervention
4. ✅ Dashboard loads in <1 second on local network
5. ✅ Total memory usage <200MB on Raspberry Pi 4
6. ✅ 20 devices sending data every minute works without issues
7. ✅ Clear error messages guide users to solutions
8. ✅ Complete documentation exists for setup and troubleshooting
9. ✅ Users can export their data to CSV/JSON
10. ✅ Firmware updates work reliably via OTA

## Testing Requirements

### Unit Tests
- Service layer functions (>80% coverage)
- Input validation
- Authentication and authorization
- Database models

### Integration Tests
- API endpoints (POST /api/readings, OTA, etc.)
- Web UI workflows (login, view dashboard, export data)
- Database migrations
- ESP32 connection flow (simulated)

### Performance Tests
- 20 concurrent devices sending data
- Dashboard load time with 10,000+ readings
- Chart rendering with large datasets
- Database query performance

### Security Tests
- SQL injection prevention
- XSS prevention in web UI
- Authentication bypass attempts
- API rate limiting
- Session security

### Hardware Tests
- ESP32 firmware on multiple board types
- WiFi connection reliability
- Sensor reading accuracy
- OTA update success rate
- Power consumption measurement

## User Stories

### Non-Technical User

**As a** homeowner with no programming experience,
**I want to** monitor temperature in my garage and basement,
**So that** I know if my freezer stops working or pipes might freeze.

**Acceptance**:
- I can follow a visual guide to install on Raspberry Pi
- I can plug in ESP32 sensors and see them on dashboard
- I understand what the charts mean
- I get alerts if temperature goes out of range (v2)

### Home Automation Enthusiast

**As a** home automation hobbyist,
**I want to** collect sensor data locally without cloud services,
**So that** my data stays private and works offline.

**Acceptance**:
- All data stays on my network
- I can export data for use in other tools
- System works without internet access
- I can add custom sensors easily (v2)

### Small Business Owner

**As a** small business owner,
**I want to** monitor temperature and humidity in my storage room,
**So that** I can prevent product damage and comply with regulations.

**Acceptance**:
- System is reliable (30+ days uptime)
- I can generate reports for compliance
- Multiple users can view dashboard (admin + employees)
- Historical data is retained for 1+ year

### Developer

**As a** developer,
**I want to** extend the system with custom sensors,
**So that** I can use it for specialized applications.

**Acceptance**:
- Clear API documentation
- Modular architecture
- Example sensor drivers
- Easy local development setup
- Unit tests pass before merging

## Assumptions

- Users have access to a Raspberry Pi or similar Linux system
- Users have WiFi network with DHCP
- Users can download files and follow instructions
- ESP32 devices have power supply (USB or battery)
- Sensors are pre-assembled or user can solder if needed
- Local network is reasonably secure (home/office, not public WiFi)
- Users accept HTTP for local network (HTTPS is optional)

## Risks & Mitigations

### Risk: SD card failure on Raspberry Pi
**Impact**: High - Data loss, system down
**Mitigation**:
- Use quality SD cards (Samsung, SanDisk)
- Automatic database backups
- Easy restore procedure
- Document backup best practices

### Risk: WiFi connectivity issues
**Impact**: Medium - Missing data
**Mitigation**:
- ESP32 retry logic
- Clear offline indicators
- Troubleshooting guide for WiFi
- Ethernet option for Raspberry Pi

### Risk: User cannot complete setup
**Impact**: High - Abandonment
**Mitigation**:
- Extremely detailed SETUP.md with screenshots
- Video installation guide
- Community forum for questions
- Install script handles most complexity

### Risk: Database performance degrades over time
**Impact**: Medium - Slow dashboard
**Mitigation**:
- Data retention policies (auto-delete old data)
- Database indexes on key columns
- Query optimization
- Aggregation for old data (v2)

### Risk: Security vulnerability discovered
**Impact**: Medium - Unauthorized access
**Mitigation**:
- Regular dependency updates
- Security testing
- Clear disclosure process
- Easy update mechanism

## Dependencies

### External Projects (Open Source):
- Flask 3.x (BSD license)
- MariaDB 10.5+ (GPL)
- SQLAlchemy (MIT)
- HTMX (BSD)
- Chart.js (MIT)
- WiFiManager (MIT)
- ArduinoJson (MIT)

### Hardware:
- ESP32 modules (widely available)
- Raspberry Pi (optional, any Linux works)
- Sensors (I2C/SPI compatible)

### Network:
- WiFi router (2.4GHz)
- DHCP server
- Optional: mDNS for automatic discovery

## Version History

- **v1.0** (Current): Core features, MariaDB primary, SQLite fallback, Flask + HTMX, basic dashboard
- **v0.9** (Planned): Beta release for testing
- **v2.0** (Future): Alerting, MQTT, advanced charts, Home Assistant integration
- **v3.0** (Future): Mobile app, cloud sync (optional), multi-tenancy

---

**Last Updated**: 2024-11-29
**Status**: Design Phase - No code implementation yet
