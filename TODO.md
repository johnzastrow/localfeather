# TODO - Local Feather

This document tracks planned features, improvements, and known issues for Local Feather.

**Last Updated:** 2025-11-30

---

## Priority Legend
- 🔴 **Critical** - Blocking core functionality
- 🟡 **High** - Important for v1.0 release
- 🟢 **Medium** - Nice to have
- 🔵 **Low** - Future enhancement

## Status Legend
- ⏳ **Not Started**
- 🏗️ **In Progress**
- ✅ **Complete**
- ❌ **Blocked**
- 🚫 **Cancelled**

---

## v1.0 - Core Functionality (Server Implementation)

### Flask Server - 🟡 High Priority

#### Backend Core
- [ ] ⏳ 🟡 Set up Flask application structure
- [ ] ⏳ 🟡 Configure Flask blueprints (auth, api, devices, readings)
- [ ] ⏳ 🟡 Implement application factory pattern
- [ ] ⏳ 🟡 Add configuration management (dev/prod configs)
- [ ] ⏳ 🟡 Set up logging with rotation

#### Database
- [ ] ⏳ 🔴 Create MariaDB schema and migrations
  - [ ] Users table (id, username, password_hash, role, created_at)
  - [ ] Devices table (id, device_id, name, api_key, approved, last_seen)
  - [ ] Readings table (id, device_id, sensor, value, unit, timestamp)
  - [ ] Firmware table (id, version, filename, upload_date)
  - [ ] Settings table (key-value pairs for configuration)
- [ ] ⏳ 🔴 Implement database migrations (Flask-Migrate / Alembic)
- [ ] ⏳ 🟡 Add database connection pooling
- [ ] ⏳ 🟢 Add SQLite fallback for development
- [ ] ⏳ 🟢 Create database seeding script for test data

#### API Endpoints
- [ ] ⏳ 🔴 `POST /api/readings` - Receive sensor data
- [ ] ⏳ 🔴 `POST /api/register` - Device registration
- [ ] ⏳ 🟡 `GET /api/ota/check` - Check for firmware updates
- [ ] ⏳ 🟡 `GET /api/ota/download/<version>` - Download firmware
- [ ] ⏳ 🟢 `GET /api/devices` - List all devices
- [ ] ⏳ 🟢 `GET /api/devices/<id>/readings` - Get device readings
- [ ] ⏳ 🟢 `PUT /api/devices/<id>` - Update device settings
- [ ] ⏳ 🟢 `DELETE /api/devices/<id>` - Remove device
- [ ] ⏳ 🟢 `GET /api/export` - Export data (CSV/JSON)

#### Authentication & Security
- [ ] ⏳ 🔴 Implement API key validation for devices
- [ ] ⏳ 🟡 User authentication (Flask-Login)
- [ ] ⏳ 🟡 Password hashing (bcrypt)
- [ ] ⏳ 🟢 Session management
- [ ] ⏳ 🟢 CSRF protection
- [ ] ⏳ 🟢 Rate limiting (Flask-Limiter)
- [ ] ⏳ 🔵 Optional HTTPS/TLS support

### Web UI - 🟡 High Priority

#### Templates (Jinja2 + HTMX)
- [ ] ⏳ 🔴 Base template with navigation
- [ ] ⏳ 🔴 Dashboard page (overview of all devices)
- [ ] ⏳ 🟡 Device list page
- [ ] ⏳ 🟡 Device detail page (graphs, recent readings)
- [ ] ⏳ 🟡 Login/logout pages
- [ ] ⏳ 🟢 Settings page
- [ ] ⏳ 🟢 Firmware upload page
- [ ] ⏳ 🟢 User management page (admin only)

#### Styling (Tailwind CSS)
- [ ] ⏳ 🟡 Set up Tailwind CSS build pipeline
- [ ] ⏳ 🟡 Create responsive layout
- [ ] ⏳ 🟡 Design component library (cards, buttons, forms)
- [ ] ⏳ 🟢 Dark mode support
- [ ] ⏳ 🔵 Custom color theme

#### Interactive Features (HTMX)
- [ ] ⏳ 🟡 Real-time data updates (polling)
- [ ] ⏳ 🟡 Device approval workflow
- [ ] ⏳ 🟢 Inline editing of device names
- [ ] ⏳ 🟢 Dynamic filtering and sorting
- [ ] ⏳ 🔵 Live notifications for new devices

#### Visualization (Chart.js)
- [ ] ⏳ 🟡 Line charts for temperature/humidity over time
- [ ] ⏳ 🟢 Bar charts for comparison across devices
- [ ] ⏳ 🟢 Customizable time ranges (1h, 24h, 7d, 30d)
- [ ] ⏳ 🔵 Export charts as images

### Deployment - 🟡 High Priority

#### Docker
- [ ] ⏳ 🟡 Create Dockerfile for Flask app
- [ ] ⏳ 🟡 Create docker-compose.yml (Flask + MariaDB)
- [ ] ⏳ 🟢 Add health checks
- [ ] ⏳ 🟢 Volume management for data persistence
- [ ] ⏳ 🔵 Multi-stage builds for smaller images

#### Installation Scripts
- [ ] ⏳ 🟡 Raspberry Pi install script
- [ ] ⏳ 🟢 Ubuntu/Debian install script
- [ ] ⏳ 🔵 macOS install script (Homebrew?)
- [ ] ⏳ 🔵 Windows install guide (WSL2)

#### Production Setup
- [ ] ⏳ 🟡 Gunicorn configuration
- [ ] ⏳ 🟡 Systemd service file
- [ ] ⏳ 🟢 Nginx reverse proxy configuration (optional)
- [ ] ⏳ 🟢 Log rotation setup
- [ ] ⏳ 🟢 Backup scripts for database
- [ ] ⏳ 🔵 Monitoring and alerting

### Documentation
- [ ] ⏳ 🟡 Server installation guide
- [ ] ⏳ 🟡 API documentation with examples
- [ ] ⏳ 🟢 Database schema diagram
- [ ] ⏳ 🟢 Development setup guide
- [ ] ⏳ 🟢 Contributing guidelines
- [ ] ⏳ 🔵 Video tutorials

### Testing
- [ ] ⏳ 🟡 Unit tests for API endpoints (pytest)
- [ ] ⏳ 🟢 Integration tests for database operations
- [ ] ⏳ 🟢 End-to-end tests for workflows
- [ ] ⏳ 🔵 Load testing for concurrent devices
- [ ] ⏳ 🔵 Security testing (OWASP)

---

## v2.0 - Enhanced Features

### Firmware Improvements
- [ ] ⏳ 🟢 Deep sleep mode for battery operation
- [ ] ⏳ 🟢 Local data buffering with LittleFS
- [ ] ⏳ 🟢 Multiple sensors per device
- [ ] ⏳ 🔵 Bluetooth configuration (alternative to WiFi captive portal)
- [ ] ⏳ 🔵 ESP32-S3 support with camera

### Server Features
- [ ] ⏳ 🟢 Alert system (email/webhook on threshold breach)
- [ ] ⏳ 🟢 Data retention policies (auto-delete old readings)
- [ ] ⏳ 🟢 Advanced analytics (min/max/avg over time)
- [ ] ⏳ 🟢 Multi-user support with roles (admin, viewer)
- [ ] ⏳ 🔵 MQTT support as alternative to HTTPS
- [ ] ⏳ 🔵 Webhook integrations (Home Assistant, IFTTT)
- [ ] ⏳ 🔵 Mobile app (React Native)

### Data Export & Integration
- [ ] ⏳ 🟢 Scheduled exports (daily CSV via email)
- [ ] ⏳ 🟢 InfluxDB integration for time-series data
- [ ] ⏳ 🟢 Grafana dashboard templates
- [ ] ⏳ 🔵 Prometheus metrics endpoint
- [ ] ⏳ 🔵 Home Assistant MQTT discovery

### Security Enhancements
- [ ] ⏳ 🟢 OTA firmware signing and verification
- [ ] ⏳ 🟢 Two-factor authentication (TOTP)
- [ ] ⏳ 🔵 Device certificate authentication
- [ ] ⏳ 🔵 Encrypted sensor data transmission

---

## v3.0 - Advanced Features

### Cloud Integration (Optional)
- [ ] ⏳ 🔵 Cloud backup of readings
- [ ] ⏳ 🔵 Remote access via VPN/tunnel
- [ ] ⏳ 🔵 Multi-site support (aggregate data from multiple locations)

### Advanced Analytics
- [ ] ⏳ 🔵 Machine learning for anomaly detection
- [ ] ⏳ 🔵 Predictive maintenance alerts
- [ ] ⏳ 🔵 Energy consumption tracking and optimization

### Ecosystem
- [ ] ⏳ 🔵 Plugin system for custom sensors
- [ ] ⏳ 🔵 Marketplace for community sensor drivers
- [ ] ⏳ 🔵 API for third-party integrations

---

## Known Issues

### Firmware
- [ ] 🟢 OTA updates over slow WiFi can timeout (increase HTTP timeout if needed)
- [ ] 🔵 ESP32 ADC is non-linear at voltage extremes (document workaround)

### Server
- [ ] 🔴 **NOT YET IMPLEMENTED** - Server doesn't exist yet!

### Documentation
- [ ] 🟢 Need more troubleshooting examples for common WiFi issues
- [ ] 🔵 Video tutorials for first-time users

---

## Deferred / Won't Implement (v1.0)

These features were considered but deferred to keep v1.0 simple:

- ❌ React frontend (using HTMX instead)
- ❌ MQTT broker (HTTP POST is simpler)
- ❌ PostgreSQL (MariaDB is lighter)
- ❌ Nginx (optional, not required)
- ❌ Kubernetes deployment (overkill for home use)
- ❌ GraphQL API (REST is sufficient)
- ❌ Real-time WebSocket updates (HTMX polling is good enough)

---

## Quick Reference - Next Actions

**Immediate Next Steps (for v1.0):**

1. 🔴 Create MariaDB schema and migrations
2. 🔴 Implement `POST /api/readings` endpoint
3. 🔴 Implement API key authentication
4. 🟡 Create basic Flask app structure
5. 🟡 Build dashboard template with Tailwind CSS
6. 🟡 Add Chart.js visualization for readings
7. 🟡 Create Docker Compose setup
8. 🟡 Write Raspberry Pi install script

**When Server is Working:**
- Test with real ESP32 devices
- Write unit tests
- Update documentation with screenshots
- Create demo video

---

## How to Update This File

When completing a task:
1. Change `[ ]` to `[x]` and update status from ⏳ to ✅
2. Add entry to CHANGELOG.md
3. Update commit message referencing the TODO item

When adding new tasks:
1. Choose appropriate version (v1.0, v2.0, v3.0)
2. Assign priority (🔴🟡🟢🔵)
3. Add clear description with acceptance criteria

---

**Last Review:** 2025-11-30 (Initial creation)
