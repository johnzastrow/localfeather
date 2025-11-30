# Local Feather - API Documentation

**Version 1.0**

This document describes the HTTP API used by ESP32 devices and available for developers to integrate with Local Feather.

## Base URL

```
http://your-server:5000/api
```

Replace `your-server` with:
- `raspberrypi.local` (Raspberry Pi with mDNS)
- `localhost` (local development)
- Your server's IP address (e.g., `192.168.1.100`)

## Authentication

### Device Authentication

ESP32 devices authenticate using API keys sent in the request body.

**Format**:
```json
{
  "device_id": "esp32-sensor-01",
  "api_key": "your-device-api-key-here",
  ...
}
```

### Web/User Authentication

Web UI uses session-based authentication (cookies). API endpoints for programmatic access require authentication header:

```
Authorization: Bearer <api-token>
```

(API tokens coming in v2.0)

---

## Device Endpoints

### POST /api/readings

Submit sensor readings from ESP32 device.

**Authentication**: Device API key required

**Request**:
```json
{
  "device_id": "esp32-sensor-01",
  "api_key": "abc123...",
  "readings": [
    {
      "sensor": "temperature",
      "value": 23.5,
      "unit": "C",
      "timestamp": 1234567890
    },
    {
      "sensor": "humidity",
      "value": 65.2,
      "unit": "%",
      "timestamp": 1234567890
    }
  ]
}
```

**Fields**:
- `device_id` (string, required): Unique device identifier
- `api_key` (string, required): Device API key (generated on registration)
- `readings` (array, required): Array of sensor readings
  - `sensor` (string, required): Sensor type (alphanumeric, dash, underscore only)
  - `value` (number, required): Sensor reading value
  - `unit` (string, required): Unit of measurement
  - `timestamp` (integer, required): Unix timestamp (seconds since epoch)

**Response (200 OK)**:
```json
{
  "status": "ok",
  "received": 2,
  "device_name": "Living Room Sensor",
  "server_time": 1234567890
}
```

**Response (401 Unauthorized)**:
```json
{
  "status": "error",
  "message": "Invalid API key"
}
```

**Response (429 Too Many Requests)**:
```json
{
  "status": "error",
  "message": "Rate limit exceeded. Try again in 60 seconds."
}
```

**Response (400 Bad Request)**:
```json
{
  "status": "error",
  "message": "Invalid data format",
  "details": {
    "readings[0].value": "Must be a number"
  }
}
```

**Rate Limit**: 10 requests per minute per device

---

### POST /api/devices/register

Register a new ESP32 device with the server.

**Authentication**: None (but device must be on local network)

**Request**:
```json
{
  "device_id": "esp32-sensor-01",
  "firmware_version": "1.0.0",
  "mac_address": "AA:BB:CC:DD:EE:FF"
}
```

**Response (200 OK)**:
```json
{
  "status": "ok",
  "api_key": "generated-api-key-here",
  "server_time": 1234567890,
  "reading_interval": 60
}
```

**Response (409 Conflict)** (device already exists):
```json
{
  "status": "error",
  "message": "Device already registered. Use existing API key."
}
```

**Notes**:
- Device ID must be unique
- API key is returned only once - ESP32 should store it in NVS
- Admin must approve device in web UI before it can send readings

---

### GET /api/ota/check

Check if firmware update is available for device.

**Authentication**: Device ID in query string

**Request**:
```
GET /api/ota/check?device_id=esp32-sensor-01&version=1.0.0
```

**Query Parameters**:
- `device_id` (string, required): Device identifier
- `version` (string, required): Current firmware version (semver format)

**Response (200 OK)** - Update Available:
```json
{
  "update_available": true,
  "version": "1.1.0",
  "url": "/api/ota/download/1.1.0",
  "size": 1048576,
  "checksum": "sha256:abc123...",
  "release_notes": "Bug fixes and improvements"
}
```

**Response (200 OK)** - No Update:
```json
{
  "update_available": false,
  "current_version": "1.0.0"
}
```

---

### GET /api/ota/download/:version

Download firmware binary for OTA update.

**Authentication**: None (file is public but requires knowing version)

**Request**:
```
GET /api/ota/download/1.1.0
```

**Response (200 OK)**:
- Content-Type: `application/octet-stream`
- Binary firmware file

**Response (404 Not Found)**:
```json
{
  "status": "error",
  "message": "Firmware version not found"
}
```

---

## Query Endpoints (Read Data)

### GET /api/devices

List all registered devices.

**Authentication**: Session (web UI) or API token (future)

**Request**:
```
GET /api/devices
```

**Response (200 OK)**:
```json
{
  "devices": [
    {
      "id": 1,
      "device_id": "esp32-sensor-01",
      "name": "Living Room Sensor",
      "firmware_version": "1.0.0",
      "status": "online",
      "last_seen": "2024-11-29T12:34:56Z",
      "sensors": [
        {"type": "temperature", "last_value": 23.5, "unit": "C"},
        {"type": "humidity", "last_value": 65.2, "unit": "%"}
      ]
    }
  ]
}
```

---

### GET /api/devices/:device_id/readings

Get sensor readings for a specific device.

**Authentication**: Session or API token

**Request**:
```
GET /api/devices/esp32-sensor-01/readings?sensor=temperature&start=1234567890&end=1234599999&limit=1000
```

**Query Parameters**:
- `sensor` (string, optional): Filter by sensor type
- `start` (integer, optional): Start timestamp (Unix seconds)
- `end` (integer, optional): End timestamp (Unix seconds)
- `limit` (integer, optional): Maximum results (default: 1000, max: 10000)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response (200 OK)**:
```json
{
  "device_id": "esp32-sensor-01",
  "readings": [
    {
      "id": 12345,
      "sensor": "temperature",
      "value": 23.5,
      "unit": "C",
      "timestamp": "2024-11-29T12:34:56Z"
    }
  ],
  "total": 5432,
  "limit": 1000,
  "offset": 0
}
```

---

### GET /api/export

Export sensor data in CSV or JSON format.

**Authentication**: Session or API token

**Request**:
```
GET /api/export?device=esp32-sensor-01&format=csv&start=2024-11-01&end=2024-11-30
```

**Query Parameters**:
- `device` (string, optional): Device ID (omit for all devices)
- `sensor` (string, optional): Sensor type
- `format` (string, required): `csv` or `json`
- `start` (string, required): Start date (YYYY-MM-DD)
- `end` (string, required): End date (YYYY-MM-DD)

**Response (200 OK)** - CSV:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="localfeather-export-2024-11-29.csv"

timestamp,device_id,device_name,sensor,value,unit
2024-11-29T12:00:00Z,esp32-sensor-01,Living Room,temperature,23.5,C
2024-11-29T12:01:00Z,esp32-sensor-01,Living Room,temperature,23.6,C
...
```

**Response (200 OK)** - JSON:
```json
{
  "export_date": "2024-11-29T12:34:56Z",
  "period": {"start": "2024-11-01", "end": "2024-11-30"},
  "readings": [
    {
      "timestamp": "2024-11-29T12:00:00Z",
      "device_id": "esp32-sensor-01",
      "device_name": "Living Room",
      "sensor": "temperature",
      "value": 23.5,
      "unit": "C"
    }
  ]
}
```

---

## System Endpoints

### GET /api/health

Health check endpoint for monitoring.

**Authentication**: None

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "database": "connected",
  "disk_free_percent": 65,
  "active_devices": 12
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "database": "disconnected",
  "error": "Database connection failed"
}
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success |
| 400 | Bad Request | Check request format, fix validation errors |
| 401 | Unauthorized | Invalid or missing API key/session |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limited - wait and retry |
| 500 | Internal Server Error | Server issue - check logs, retry later |
| 503 | Service Unavailable | Server starting up or database down |

---

## Rate Limiting

**Device API** (`/api/readings`, `/api/ota/*`):
- 10 requests per minute per device
- 429 response if exceeded
- Rate limit resets every 60 seconds

**Query API** (`/api/devices`, `/api/export`):
- 60 requests per minute per user
- Designed for occasional queries, not real-time streaming

**No rate limiting** on `/api/health` (monitoring)

---

## Best Practices

### For ESP32 Developers

**1. Store API Key Securely**
```cpp
#include <Preferences.h>

Preferences prefs;
prefs.begin("localfeather", false);
prefs.putString("api_key", api_key);
String key = prefs.getString("api_key", "");
```

**2. Batch Readings**

Send multiple readings in one request instead of multiple requests:

✅ Good:
```json
{
  "readings": [
    {"sensor": "temp", "value": 23.5, ...},
    {"sensor": "humidity", "value": 65, ...}
  ]
}
```

❌ Bad:
- Two separate POST requests

**3. Handle Errors Gracefully**

```cpp
int retryCount = 0;
while (retryCount < 3) {
  int httpCode = http.POST(payload);

  if (httpCode == 200) {
    break; // Success
  } else if (httpCode == 401) {
    // Invalid API key - don't retry
    break;
  } else if (httpCode == 429) {
    // Rate limited - wait longer
    delay(60000);
  } else {
    // Server error - retry with backoff
    delay(5000 * (retryCount + 1));
  }
  retryCount++;
}
```

**4. Use Server Time**

ESP32 clocks drift. Use server time from registration response:
```cpp
time_t serverTime = response["server_time"];
// Synchronize ESP32 RTC
```

**5. Check for Updates Periodically**

```cpp
// Check for OTA updates every 6 hours
if (millis() - lastOTACheck > 6 * 3600 * 1000) {
  checkForOTAUpdate();
  lastOTACheck = millis();
}
```

### For Integrators

**1. Use Export API for Bulk Data**

Don't poll `/api/devices/:id/readings` frequently. Use `/api/export` for historical data.

**2. Respect Rate Limits**

Implement exponential backoff on 429 responses.

**3. Handle Pagination**

```python
offset = 0
limit = 1000
all_readings = []

while True:
    response = requests.get(f'/api/devices/{id}/readings',
                           params={'limit': limit, 'offset': offset})
    readings = response.json()['readings']

    if not readings:
        break

    all_readings.extend(readings)
    offset += limit
```

---

## Examples

### Python - Get Latest Readings

```python
import requests

# Assuming you're logged in (session cookies)
session = requests.Session()
session.post('http://raspberrypi.local:5000/auth/login',
             data={'username': 'admin', 'password': 'password'})

# Get latest readings
response = session.get('http://raspberrypi.local:5000/api/devices/esp32-sensor-01/readings',
                       params={'limit': 10})

for reading in response.json()['readings']:
    print(f"{reading['timestamp']}: {reading['sensor']} = {reading['value']} {reading['unit']}")
```

### JavaScript - Real-time Dashboard

```javascript
async function fetchDevices() {
  const response = await fetch('/api/devices');
  const data = await response.json();

  data.devices.forEach(device => {
    console.log(`${device.name}: ${device.status}`);
    device.sensors.forEach(sensor => {
      console.log(`  ${sensor.type}: ${sensor.last_value} ${sensor.unit}`);
    });
  });
}

// Poll every 10 seconds
setInterval(fetchDevices, 10000);
```

### cURL - Export Data

```bash
# Export all data for November 2024 as CSV
curl -X GET "http://raspberrypi.local:5000/api/export?format=csv&start=2024-11-01&end=2024-11-30" \
  --cookie "session=your-session-cookie" \
  --output data-november.csv
```

---

## Webhook Integration (v2.0)

Coming in v2.0: Ability to send sensor data to external webhooks.

**Configuration** (via web UI):
- URL: `https://your-service.com/webhook`
- Trigger: On new reading, threshold crossed, device offline
- Payload: Customizable JSON template

---

## GraphQL API (Future)

Considering GraphQL API in v3.0 for more flexible queries.

**Example query**:
```graphql
query {
  devices {
    name
    status
    readings(last: 10, sensor: "temperature") {
      timestamp
      value
    }
  }
}
```

---

## Support

- Report API bugs: GitHub Issues
- Request new endpoints: GitHub Discussions
- Security issues: Email [security@example.com]

---

**API Version**: 1.0
**Last Updated**: 2024-11-29
**Stability**: Stable (v1.0 endpoints won't change)
