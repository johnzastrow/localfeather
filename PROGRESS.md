# LocalFeather - Development Progress

**Last Updated:** 2025-12-04 02:50 EST

## Current Status: API Key Buffer Fix In Progress ✅

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

5. 🔧 **Currently Fixing: API Key Truncation Bug**
   - **Problem:** API key buffer was 64 bytes, but 64-char hex string needs 65 bytes (+ null terminator)
   - **Symptom:** API key gets truncated from `...087f` to `...087`, causing 401 errors
   - **Fix Applied:** Increased buffer size from 64 to 128 bytes in:
     - `Config` struct (`char apiKey[128]`)
     - `WiFiManagerParameter` initialization
   - **Status:** Code fixed, needs testing

### Next Steps (Resume Here)

1. **Upload Fixed Firmware (IMMEDIATE):**
   ```bash
   # Delete device from database
   mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "DELETE FROM devices WHERE device_id='esp32-3323b0';"

   # Close serial monitor, then upload
   cd firmware
   pio run --target upload
   pio device monitor
   ```

2. **Verify API Key Saved Correctly:**
   - After registration, check that printed API key is **64 characters** (not 63)
   - Example: `456993da455ac7ab677d1f17fd655d1072a6ef777573c2d9592160ab6ecf087f`
   - Should NOT be truncated at the end

3. **Approve Device:**
   ```bash
   mysql -ujcz -pyub.miha -h192.168.1.234 localfeather -e "UPDATE devices SET approved=1 WHERE device_id='esp32-3323b0';"
   ```

4. **Verify Successful Data Submission:**
   - Wait 60 seconds for next reading cycle
   - Should see: `"status": "ok"` and `"approved": true`
   - No more 401 errors

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

### 1. AHT20 Sensor Not Detected
**Symptom:** `⚠ AHT20 sensor not found`

**Not Critical:** Firmware sends dummy data (0.0, 0.0) to keep device alive

**To Fix Later:**
- Check wiring (SDA=GPIO21, SCL=GPIO22, VCC=3.3V, GND)
- Verify I2C address is 0x38
- Try different I2C pull-up resistors if needed

### 2. Connection Reset Errors (Intermittent)
**Symptom:** `errno: 104, "Connection reset by peer"`

**Cause:** Server closing connection during POST

**Status:** Happens occasionally, ESP32 retries successfully

**To Investigate:**
- Check Flask server logs during reset
- May be related to Werkzeug dev server (not production-ready)
- Consider switching to Gunicorn for production

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

**After uploading fixed firmware:**

- [ ] ESP32 boots and shows config portal
- [ ] Configure via web UI at 192.168.4.1
- [ ] See "WiFiManager: Config saved callback triggered"
- [ ] See "✓ Configuration saved to NVS"
- [ ] ESP32 reboots and connects to WiFi
- [ ] Registers with server (200 response)
- [ ] API key printed is **64 characters** (not truncated)
- [ ] See "✓ Device registered - API key saved"
- [ ] Approve device in database
- [ ] Next POST gets 200 with "status": "ok"
- [ ] No more 401 errors
- [ ] Readings persist across ESP32 reboots

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

## Notes for Tomorrow

1. **Test the API key buffer fix first** - This should resolve all 401 errors
2. **If successful, start building the web UI** - Much easier than terminal commands
3. **Consider adding password hashing** - Current plaintext storage is insecure
4. **Fix the AHT20 sensor detection** - Check wiring and I2C communication
5. **Test OTA updates** - Haven't tested this feature yet

**Web UI Priority Features:**
1. Device approval button (replace SQL commands)
2. Device list with status
3. Regenerate API key button
4. View readings chart

**Good luck tomorrow! 🚀**
