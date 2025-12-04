# LocalFeather - Development Progress

**Last Updated:** 2025-12-04 08:00 EST

## Current Status: System Fully Operational ✅

### What We've Accomplished Today

1. ✅ **ESP32 Device ID Display**
   - Added device ID display after setup completes
   - Shows in serial monitor: `📟 Device ID: esp32-3323b0`
   - Updated troubleshooting docs

2. ✅ **Fixed WiFiManager Configuration Saving**
   - **CRITICAL BUG FIXED:** WiFiManager was rebooting before saving config to NVS
   - Added `setSaveConfigCallback()` to save settings BEFORE reboot
   - Config now persists across reboots

3. ✅ **Improved JSON Response Parsing**
   - Increased JSON buffer from 256 to 512 bytes
   - Added error logging for JSON parse failures
   - Added debug output when API key is saved

4. ✅ **Comprehensive Troubleshooting Documentation**
   - Added FAQ entries for common issues
   - Documented "port busy" errors and solutions
   - Added device approval workflow
   - Fixed table name case-sensitivity issues (lowercase `devices` not `Devices`)

5. ✅ **Fixed API Key Truncation Bug**
   - **Problem:** API key buffer was 64 bytes, but 64-char hex string needs 65 bytes (+ null terminator)
   - **Symptom:** API key gets truncated from `...087f` to `...087`, causing 401 errors
   - **Fix Applied:** Increased buffer size from 64 to 128 bytes in:
     - `Config` struct (`char apiKey[128]`)
     - `WiFiManagerParameter` initialization
   - **Status:** ✅ FIXED - Device authenticating successfully with full 64-char API key

6. ✅ **Flask Server Deployment**
   - Created systemd service file at `/home/jcz/Github/localfeather/server/localfeather.service`
   - Fixed service configuration: `app:app` → `'app:create_app()'` (factory pattern)
   - Fixed venv path: `venv` → `.venv`
   - **Status:** ✅ Server running on 192.168.1.234:5000 with Gunicorn (4 workers)

7. ✅ **Fixed I2C Pin Configuration for ESP32 Feather V2**
   - **Problem:** Firmware was using GPIO 21/22 (generic ESP32) instead of GPIO 3/4 (STEMMA QT)
   - **Symptom:** AHT20 sensor not detected on I2C bus
   - **Fix Applied:** Changed I2C_SDA to GPIO 3, I2C_SCL to GPIO 4 in `main.cpp`
   - Added I2C scanner function `scanI2C()` for debugging
   - **Status:** ✅ FIXED

8. ✅ **AHT20 Sensor Working**
   - **Root Cause:** Poor connection on first I2C connector of AHT20
   - **Solution:** Switched STEMMA QT cable to second connector on AHT20
   - **Status:** ✅ Transmitting real sensor data (Temperature: 23.82°C, Humidity: 28.62%)
   - Device successfully reading and transmitting data every 60 seconds

### System Status

**ESP32 Device:** `esp32-3323b0`
- ✅ Connected to WiFi (bobby24)
- ✅ Registered with server
- ✅ API key authentication working
- ✅ AHT20 sensor detected and reading
- ✅ Transmitting data every 60 seconds
- ✅ Server responding with HTTP 200

**Flask Server:** 192.168.1.234:5000
- ✅ Systemd service running
- ✅ Gunicorn with 4 workers
- ✅ Receiving and storing sensor data
- ✅ MariaDB connection healthy

**Latest Sensor Readings:**
- Temperature: 23.82°C
- Humidity: 28.62%
- Last updated: 2025-12-04 07:47:53

### Next Steps

The core system is now fully operational. Ready to move on to next features:

---

## Planned Features (Not Started)

### High Priority: Web UI for Device Management

**Goal:** Build Flask web interface to manage devices without terminal commands

**Features Needed:**
1. **Dashboard Page** (`/dashboard`)
   - List all devices with status (online/offline)
   - Show last reading time
   - Approve/deny pending devices with one click
   - Delete devices

2. **Device Detail Page** (`/devices/<device_id>`)
   - View device info (name, IP, firmware version)
   - Edit device name
   - Regenerate API key
   - View recent readings (chart)

3. **Readings Page** (`/readings`)
   - Table of recent readings
   - Filter by device and sensor type
   - Export to CSV

4. **Authentication**
   - Login page (already implemented in design docs)
   - Session-based auth with Flask-Login
   - Admin vs Viewer roles

**Implementation Files to Create:**
- `server/app/web/__init__.py` - Web blueprint
- `server/app/web/dashboard.py` - Dashboard routes
- `server/app/web/devices.py` - Device management routes
- `server/app/web/auth.py` - Login/logout routes
- `server/app/templates/base.html` - Base template with HTMX
- `server/app/templates/dashboard.html` - Main dashboard
- `server/app/templates/devices.html` - Device list
- `server/app/templates/device_detail.html` - Single device view
- `server/app/templates/login.html` - Login form

**Tech Stack (Already Decided in CLAUDE.md):**
- Jinja2 templates (server-side rendering)
- HTMX for dynamic updates (no React/Vue needed)
- Tailwind CSS via CDN
- Chart.js for sensor graphs

**Quick Start Guide:**
See `docs/DESIGN.md` section "Web UI Design" for wireframes and routes

---

## Known Issues

### ~~1. AHT20 Sensor Not Detected~~ ✅ RESOLVED
**Was:** `⚠ AHT20 sensor not found`

**Root Cause:**
1. Incorrect I2C pins (GPIO 21/22 instead of GPIO 3/4 for ESP32 Feather V2)
2. Poor connection on first I2C connector of AHT20 sensor

**Resolution:**
- Fixed I2C pin configuration to GPIO 3/4 (STEMMA QT pins)
- Switched STEMMA QT cable to second connector on AHT20
- Sensor now working and transmitting real data

### ~~2. Connection Reset Errors~~ ✅ RESOLVED
**Was:** `errno: 104, "Connection reset by peer"`

**Root Cause:** Flask development server (Werkzeug) not running

**Resolution:**
- Deployed Flask server as systemd service with Gunicorn
- Server now stable and handling requests reliably

---

## Database Schema (Current State)

### `devices` table
```sql
+--------------+------+------------------------------------------------------------------+----------+---------------------+
| device_id    | name | api_key                                                          | approved | last_seen           |
+--------------+------+------------------------------------------------------------------+----------+---------------------+
| esp32-3323b0 | NULL | 456993da455ac7ab677d1f17fd655d1072a6ef777573c2d9592160ab6ecf087f |        1 | 2025-12-04 02:46:23 |
+--------------+------+------------------------------------------------------------------+----------+---------------------+
```

**Note:** `api_key` is stored as **plaintext** (not hashed!)
- This is a security issue but matches current firmware implementation
- Server compares plaintext keys directly (line 98 in `readings.py`)
- To fix: Need to hash keys on registration and compare hashes

---

## Server Configuration

**Location:** 192.168.1.234:5000

**Database Credentials:**
- Host: 192.168.1.234
- User: `jcz`
- Password: `yub.miha`
- Database: `localfeather`

**Quick Commands:**
```bash
# View devices
mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "SELECT * FROM devices;"

# View recent readings
mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10;"

# Approve device
mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "UPDATE devices SET approved=1 WHERE device_id='esp32-3323b0';"

# Delete device (for fresh start)
mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "DELETE FROM devices WHERE device_id='esp32-3323b0';"
```

---

## ESP32 Configuration

**Device ID:** `esp32-3323b0` (MAC-based: last 3 bytes of MAC address)

**Network:**
- WiFi: bobby24
- IP: 192.168.1.83
- Signal: -53 to -61 dBm

**Firmware Version:** 1.0.0

**Reading Interval:** 60 seconds (60000 ms)

**Current API Key:** (Will be regenerated after buffer fix upload)

---

## Files Modified Today

### Firmware (`firmware/src/main.cpp`)
1. Added device ID display in setup
2. Increased JSON buffer (256→512)
3. Added WiFiManager save callback
4. Added JSON parse error logging
5. Increased API key buffer (64→128)
6. Fixed I2C pin configuration (GPIO 21/22 → GPIO 3/4 for ESP32 Feather V2 STEMMA QT)
7. Added I2C scanner function `scanI2C()` for debugging

### Server (`/home/jcz/Github/localfeather/server/`)
1. Created systemd service file `localfeather.service`
2. Configured Gunicorn with 4 workers
3. Set up logging to `/home/jcz/localfeather/logs/`
4. Fixed application factory pattern reference: `'app:create_app()'`

### Documentation
1. `docs/TROUBLESHOOTING.md`
   - Added FAQ: "How do I find my ESP32's device ID?"
   - Added FAQ: "I see 'Device registered successfully. Awaiting approval.'"
   - Added FAQ: "Table 'Devices' doesn't exist" (case-sensitivity)
   - Added FAQ: "How do I erase ESP32's stored configuration?"
   - Fixed all SQL examples to use lowercase table names

2. `CLAUDE.md`
   - Added "Troubleshooting Documentation Workflow" to AI Agent Guidance
   - Instructions to update docs when answering user questions

---

## Testing Checklist

**System Verification:** ✅ ALL TESTS PASSED

- ✅ ESP32 boots and shows config portal
- ✅ Configure via web UI at 192.168.4.1
- ✅ See "WiFiManager: Config saved callback triggered"
- ✅ See "✓ Configuration saved to NVS"
- ✅ ESP32 reboots and connects to WiFi
- ✅ Registers with server (200 response)
- ✅ API key printed is **64 characters** (not truncated)
- ✅ See "✓ Device registered - API key saved"
- ✅ Approve device in database
- ✅ Next POST gets 200 with "status": "ok"
- ✅ No more 401 errors
- ✅ Readings persist across ESP32 reboots
- ✅ AHT20 sensor detected on I2C bus
- ✅ Real sensor data transmitted (not dummy 0.0 values)
- ✅ Flask server running as systemd service
- ✅ Database receiving and storing readings

---

## Resources

**Documentation:**
- `CLAUDE.md` - Project overview and AI instructions
- `docs/DESIGN.md` - Architecture and design decisions
- `docs/TROUBLESHOOTING.md` - Common issues and solutions
- `docs/REQUIREMENTS.md` - Functional requirements

**Key Code Locations:**
- Firmware: `firmware/src/main.cpp`
- API endpoint: `server/app/api/readings.py`
- Database models: `server/app/models.py`

**Useful Links:**
- PlatformIO docs: https://docs.platformio.org/
- WiFiManager library: https://github.com/tzapu/WiFiManager
- Flask docs: https://flask.palletsprojects.com/

---

## Next Development Phase

The core ESP32 sensor system is now fully operational. Ready for next features:

### High Priority: Web UI Development
According to CLAUDE.md, the next major feature is building the Flask web interface:

**Priority Features:**
1. Dashboard page - Device list with online/offline status
2. Device approval button (replace SQL commands)
3. View sensor readings with charts
4. Device management (rename, delete, regenerate API key)
5. Authentication (Flask-Login with admin/viewer roles)

**Tech Stack (from CLAUDE.md):**
- Jinja2 templates (server-side rendering)
- HTMX for dynamic updates
- Tailwind CSS via CDN
- Chart.js for sensor graphs

See `docs/DESIGN.md` for detailed web UI design and routes.

### Other Possible Features:
1. Password/API key hashing (security improvement)
2. OTA firmware updates (test existing implementation)
3. Multiple device support (already supported, need multiple ESP32s)
4. Data export (CSV)
