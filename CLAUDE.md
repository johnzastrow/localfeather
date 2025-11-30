# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local Feather is a simplified IoT sensor data collection system that enables ESP32 Feather devices to send sensor data directly to a local database server without requiring cloud connectivity. The system operates entirely on a local network and prioritizes **simplicity, ease of installation, and minimal resource usage**.

**Design Philosophy**: Start simple. Grow intentionally. Every component must justify its complexity cost.

## Architecture

The system consists of **three components only**:

1. **ESP32 Firmware**: Reads sensors, sends data via HTTPS POST (JSON)
2. **Flask Server**: Receives data, stores in MariaDB, serves web UI
3. **MariaDB Database**: Performant, MySQL-compatible database (SQLite fallback for dev)

### Communication Flow

```
ESP32 Devices → HTTPS POST (JSON) → Flask Server → MariaDB Database
                                           ↓
User Browser ← HTML + HTMX ← Flask Server (Jinja2 templates)
```

**That's it.** No MQTT broker, no reverse proxy, no separate frontend build, no microservices.

### Key Technologies

**Current stack** (v1.0):
- **Backend**: Flask 3.x + Gunicorn
- **Database**: MariaDB 10.5+ (primary), SQLite (dev/testing only)
- **Web UI**: Jinja2 templates + HTMX + Tailwind CSS
- **Charts**: Chart.js embedded in templates
- **Auth**: Flask-Login (session-based) + Flask-Bcrypt
- **Migrations**: Flask-Migrate (Alembic)
- **Firmware**: Arduino/PlatformIO with WiFiManager + HTTPClient
- **Communication**: HTTPS POST with JSON payloads
- **Deployment**: Docker Compose + install script for Raspberry Pi/Linux

**Why these choices**:
- **Flask**: Simpler than FastAPI for this scale, more flexible than Django
- **HTMX**: Modern dynamic UI without build pipeline or React complexity
- **MariaDB**: Free, performant, MySQL-compatible, excellent for time-series data, better concurrent writes than SQLite
- **SQLite (dev only)**: Optional for local development without MariaDB setup
- **Direct HTTPS**: Simpler than MQTT, easier to debug, ESP32 needs it for OTA anyway

## Project Status

**IMPORTANT**: This repository currently contains only design documentation. No implementation code exists yet. The design has been simplified from an initial over-engineered proposal.

**See**: `docs/OLDDESIGN.md` for the rejected complex design, `docs/DESIGN.md` for current simplified approach.

## Design Principles

1. **Simplicity First**: Only add complexity when requirements demand it
2. **Non-technical Users**: Installable in <30 minutes by non-technical users
3. **Minimal Resources**: Total memory <150MB on Raspberry Pi
4. **Clear Growth Paths**: Easy to add features later without rewrites
5. **Debuggable**: When things fail, errors are clear and solutions obvious

**Target scale**: 5-20 ESP32 devices, 1 reading/minute, Raspberry Pi server

## Code Architecture

### Clean Architecture (Simplified)

```
routes/        # Flask blueprints (HTTP endpoints)
services/      # Business logic
models/        # SQLAlchemy models
templates/     # Jinja2 HTML templates
static/        # CSS, JS, images
utils/         # Helpers (auth, validation)
```

**Layers**:
- **Routes**: Handle HTTP requests, validate input, call services
- **Services**: Business logic (device registration, data ingestion)
- **Models**: Database schema and queries
- **Templates**: User interface rendered server-side

**No repositories layer**: SQLAlchemy ORM used directly in services (simpler for this scale).

## Project Structure

```
localfeather/
├── firmware/                    # ESP32 code (PlatformIO)
│   ├── platformio.ini
│   ├── src/
│   │   ├── main.cpp            # Main loop
│   │   ├── config.h            # WiFi/server config
│   │   ├── sensors.cpp         # Sensor reading logic
│   │   └── api_client.cpp      # HTTPS POST client
│   └── README.md
│
├── server/                      # Flask application
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── models.py           # SQLAlchemy models (Device, Sensor, Reading, User)
│   │   ├── routes/
│   │   │   ├── api.py          # Device API endpoints
│   │   │   ├── web.py          # Web UI routes
│   │   │   └── auth.py         # Login/logout
│   │   ├── services/
│   │   │   ├── device_service.py    # Device management
│   │   │   ├── reading_service.py   # Data ingestion
│   │   │   └── ota_service.py       # OTA updates
│   │   ├── templates/
│   │   │   ├── base.html       # Base template with HTMX
│   │   │   ├── dashboard.html  # Main dashboard
│   │   │   ├── devices.html    # Device list
│   │   │   └── login.html      # Login page
│   │   ├── static/
│   │   │   ├── css/            # Tailwind CSS (via CDN)
│   │   │   ├── js/             # Chart.js configs
│   │   │   └── images/
│   │   └── utils/
│   │       ├── auth.py         # Auth helpers
│   │       └── validators.py   # Input validation
│   ├── migrations/             # Alembic database migrations
│   ├── tests/
│   │   ├── conftest.py         # Test fixtures
│   │   ├── test_api.py         # API endpoint tests
│   │   ├── test_models.py      # Model tests
│   │   └── test_services.py    # Service layer tests
│   ├── config.py               # Flask config
│   ├── requirements.txt        # Python dependencies
│   └── run.py                  # Entry point
│
├── docker-compose.yml          # Docker deployment
├── Dockerfile                  # Flask app container
├── install.sh                  # Linux install script
├── .env.example                # Environment variables template
├── docs/
│   ├── REQUIREMENTS.md         # Project requirements
│   ├── DESIGN.md               # Current simplified design
│   ├── OLDDESIGN.md            # Rejected complex design (for reference)
│   ├── AI_INSTRUCTIONS.md      # AI coding standards
│   └── AGENT_GUIDE.md          # Quick reference (template)
└── README.md
```

## Database Schema

**Models** (SQLAlchemy):

```python
# Device: Represents an ESP32 sensor node
class Device(db.Model):
    id: Integer (primary key)
    device_id: String (unique, indexed) - e.g., "esp32-sensor-01"
    name: String - friendly name
    api_key: String (hashed) - for authentication
    firmware_version: String
    last_seen: DateTime
    status: String (enum: active, offline, error)
    created_at: DateTime

# Sensor: Dynamic sensor types per device
class Sensor(db.Model):
    id: Integer (primary key)
    device_id: ForeignKey(Device)
    sensor_type: String - e.g., "temperature", "humidity"
    unit: String - e.g., "C", "%"
    last_value: Float (denormalized for dashboard)
    last_reading_at: DateTime

# Reading: Time-series sensor data
class Reading(db.Model):
    id: Integer (primary key)
    device_id: ForeignKey(Device)
    sensor_type: String (indexed)
    value: Float
    unit: String
    timestamp: DateTime (indexed) - device timestamp
    received_at: DateTime - server receipt time

# User: Web UI access
class User(db.Model):
    id: Integer (primary key)
    username: String (unique)
    password_hash: String (bcrypt)
    role: String (enum: admin, viewer)
    created_at: DateTime
```

**Indexes**:
- `readings.timestamp` - time-range queries
- `readings.device_id, timestamp` - per-device charts
- `devices.device_id` - API lookups

## API Design

### Device Endpoints

**POST /api/readings** - Submit sensor data
```json
Request:
{
  "device_id": "esp32-sensor-01",
  "api_key": "secret-key",
  "readings": [
    {"sensor": "temperature", "value": 23.5, "unit": "C", "timestamp": 1234567890}
  ]
}

Response (200):
{"status": "ok", "received": 1}

Response (401):
{"status": "error", "message": "Invalid API key"}
```

**GET /api/ota/check** - Check for firmware updates
```
Query: ?device_id=X&version=1.0.0
Response:
{
  "update_available": true,
  "version": "1.1.0",
  "url": "/api/ota/download/1.1.0",
  "size": 1024000,
  "checksum": "sha256-hash"
}
```

## Security

### Authentication

**Device Authentication**:
- API key per device (generated on registration)
- Sent in JSON body of POST requests
- Hashed in database (bcrypt)
- Rate limited: 10 requests/min per device

**Web UI Authentication**:
- Flask-Login session-based auth (cookies)
- Username + password (bcrypt hashed)
- Two roles: **admin** (full access), **viewer** (read-only)
- Session timeout: 7 days with activity
- CSRF protection via Flask-WTF

**HTTPS/TLS**:
- **Default**: HTTP-only (acceptable for local networks)
- **Optional**: HTTPS via self-signed certificate
- Documentation provides OpenSSL commands for cert generation
- ESP32 can skip cert validation for local network

### Security Requirements

- Validate all input at route handlers (JSON schema validation)
- Sanitize device_id and sensor names (alphanumeric + dash/underscore only)
- Never log API keys or passwords
- Use SQLAlchemy parameterized queries (prevents SQL injection)
- Rate limiting on API endpoints
- HTTPOnly cookies for sessions

**Threat model**: Unauthorized access from local network. Out of scope: Internet-based attacks (system is local-only).

## ESP32 Firmware Design

**Flow**:
```
Boot → WiFiManager (captive portal) → Connect WiFi → Register with server →
Read sensors → POST to /api/readings → Sleep → Repeat
```

**Libraries**:
- `WiFiManager` - Captive portal for WiFi setup
- `HTTPClient` - HTTPS POST
- `ArduinoJson` - JSON serialization
- `ESP32HTTPUpdate` - OTA updates
- `Preferences` - Store server URL and API key in NVS

**No persistent buffering in v1**: If network fails, data is lost. Trade-off: simpler firmware, faster development. Growth path: Add LittleFS buffering in v2.

**Error handling**:
- Retry on HTTP failure: immediate, 30s, 5min intervals
- After 24h offline: Reboot
- Serial logging for debugging

**Memory target**: <60KB RAM usage

## Development Workflow

### Backend Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Create admin user
flask create-admin

# Run dev server
flask run --debug

# Run tests
pytest tests/ -v

# Lint and format (use ruff when available)
ruff check .
ruff format .
```

### Frontend Development

**No build step!**
- Edit templates in `templates/`
- Use Tailwind CSS via CDN
- HTMX loaded from CDN
- Chart.js loaded from CDN
- Reload browser to see changes

**HTMX examples**:

Auto-refresh:
```html
<div hx-get="/dashboard/latest" hx-trigger="every 10s" hx-swap="innerHTML">
  <!-- Updated content -->
</div>
```

Inline edit:
```html
<form hx-post="/devices/{{ device.id }}/rename" hx-target="#device-name">
  <input type="text" name="name" value="{{ device.name }}">
  <button>Save</button>
</form>
```

### Firmware Development

```bash
# PlatformIO
pio run                    # Build
pio run --target upload    # Flash
pio device monitor         # Serial monitor

# Arduino IDE
# Open firmware/localfeather-firmware.ino
# Select board: ESP32 Dev Module
# Upload
```

## Testing Strategy

**Backend tests** (pytest):
```
tests/
  conftest.py           # Fixtures (app, db, client)
  test_models.py        # Model validation
  test_api.py           # API endpoints (POST /api/readings)
  test_auth.py          # Login/logout/sessions
  test_services.py      # Business logic
```

**Test coverage target**: >80% for services and routes

**Firmware tests**: PlatformIO native tests for utility functions

## Deployment

### Option 1: Docker Compose (Recommended)

```bash
git clone <repo>
cd localfeather
cp .env.example .env
# Edit .env
docker-compose up -d
```

Access: `http://localhost:5000`

### Option 2: Install Script (Raspberry Pi/Linux)

```bash
curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
```

What it does:
1. Installs Python 3.9+ if needed
2. Creates virtualenv
3. Installs dependencies
4. Runs migrations
5. Creates systemd service
6. Enables auto-start on boot
7. Creates admin user

Access: `http://raspberrypi.local:5000` or `http://<IP>:5000`

**Logs**: `journalctl -u localfeather -f`

## Performance Targets

- Dashboard load: <500ms
- API response: <100ms
- Chart rendering: <1s (7-day view)
- Concurrent devices: 20 @ 1/min = trivial load
- Memory usage: <150MB total
- CPU usage: <5% average (Raspberry Pi 4)

## Growth Paths

The design supports gradual enhancement:

### Phase 2 (if needed):
- **MQTT**: Add Mosquitto for bidirectional communication
- **PostgreSQL**: Alternative to MariaDB if preferred (same migrations work)
- **Persistent buffering**: LittleFS on ESP32
- **Advanced charts**: Plotly.js for interactivity
- **API docs**: Flask-RESTX for OpenAPI/Swagger
- **Alerting**: Threshold monitoring + email/webhook
- **Aggregation**: Hourly stats table for long time ranges
- **MariaDB Replication**: Master-slave setup for high availability

### Phase 3 (enterprise):
- **Mobile app**: Reuse JSON API
- **Home Assistant**: MQTT bridge or webhook
- **Cloud sync**: Optional backup to cloud storage
- **Multi-tenancy**: Organizations and user scoping
- **High availability**: PostgreSQL + Redis + load balancer

## Common Commands

**Database**:
```bash
flask db migrate -m "Add field"  # Create migration
flask db upgrade                 # Apply migrations
flask db downgrade               # Rollback
flask shell                      # Interactive shell
```

**Backup**:
```bash
flask backup create              # Manual backup
flask backup restore <file>      # Restore from backup
```

**Users**:
```bash
flask create-admin               # Interactive admin creation
flask create-user --role viewer # Create viewer user
```

## Monitoring & Debugging

**Built-in tools**:
- `/health` endpoint - JSON status (db, disk, uptime)
- Device status page - online/offline, last seen
- Error log page - recent 100 errors
- Serial monitor - ESP32 debugging

**Logging**:
- Structured JSON logs
- Levels: DEBUG, INFO, WARNING, ERROR
- Docker: stdout | Systemd: `/var/log/localfeather/`
- Automatic rotation (10MB files, keep 5)

## Tooling

**Python** (when implementing):
- `uv` for fast package management (optional, can use pip)
- `ruff` for linting and formatting
- `pytest` for testing
- `flask` CLI for admin tasks

**Install helpful tools**:
```bash
pip install uv ruff pytest-cov
```

## AI Agent Guidance

When working in this codebase:

**Priorities**:
1. Simplicity over cleverness
2. Clear error messages
3. Minimal dependencies
4. Obvious debugging paths
5. Documentation for non-technical users

**Patterns**:
- Small, focused functions
- Explicit error handling
- Input validation at route layer
- Service layer for business logic
- SQLAlchemy for database (no raw SQL)

**Avoid**:
- Over-engineering for hypothetical scale
- Adding features not in requirements
- Complex abstractions for simple operations
- Micro-optimizations without profiling

**Security**:
- Validate all external input
- Hash passwords and API keys (bcrypt)
- Use parameterized queries
- Rate limit API endpoints
- Log security events (failed auth, rate limits)

## Mermaid Diagram Theme

Use Forest Dark theme:

```mermaid
%%{init: {'theme': 'forest', 'themeVariables': {'darkMode': true}, "flowchart" : { "curve" : "basis" } } }%%
```

## Version Management

- Semantic versioning: `MAJOR.MINOR.PATCH`
- Version stored in: `server/app/__init__.py` (single source)
- Display in: `/version` endpoint, web UI footer, logs
- Increment: patch (bug fix), minor (feature), major (breaking change)

## Non-Goals (v1)

Explicitly out of scope:
- Cloud integration
- Mobile native app
- Complex analytics
- Multi-user collaboration
- Advanced alerting
- External integrations (can be added later)
- Support for non-ESP32 devices
- Real-time streaming (HTMX polling is sufficient)

## Success Criteria

v1.0 is successful if:
1. ✅ Non-technical user installs on Raspberry Pi in <30 min
2. ✅ ESP32 provisioned and sending data in <15 min
3. ✅ Runs 30 days without intervention
4. ✅ Memory <200MB on Raspberry Pi
5. ✅ Dashboard loads <1s on local network
6. ✅ Clear error messages guide users
7. ✅ Complete setup/troubleshooting docs
8. ✅ Easy data export

## Documentation

See `docs/` for:
- `DESIGN.md` - Full architecture and design decisions
- `REQUIREMENTS.md` - Functional/non-functional requirements
- `OLDDESIGN.md` - Rejected complex design (reference only)
- `AI_INSTRUCTIONS.md` - Coding standards and AI persona

## Key Architectural Decisions

**Why Flask not FastAPI?**
- Simpler for this scale (20 devices @ 1 req/min)
- No async complexity needed
- Huge ecosystem
- Easier for community contributions

**Why HTMX not React?**
- No build pipeline
- No Node.js dependency
- One codebase (Python only)
- Modern UX without JavaScript framework
- Faster development

**Why MariaDB not PostgreSQL or SQLite?**
- **vs PostgreSQL**: More familiar (MySQL-compatible), lighter resource usage, easier Raspberry Pi setup
- **vs SQLite**: Better concurrent write handling, no database locking issues, built-in replication for growth
- **Production ready**: Handles 20+ devices without performance issues
- **Free and open source**: GPL license, truly open (no corporate control)
- **Easy backups**: Standard `mysqldump` tooling

**Why HTTPS not MQTT?**
- Simpler deployment (one less service)
- Easier debugging (standard HTTP tools)
- ESP32 needs HTTPS for OTA anyway
- Sufficient for 5-20 devices
- MQTT adds value at 50+ devices

**Why no persistent buffering on ESP32?**
- Simpler firmware
- Faster development
- Most sensors tolerate occasional data gaps
- Can add LittleFS in v2 if users need it

These decisions optimize for **simplicity and development speed** while preserving **clear growth paths** for future needs.
