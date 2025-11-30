# Local Feather - ESP32 Firmware

Firmware for ESP32-based sensor devices that send data to Local Feather server.

## Features

- ✅ **WiFiManager**: Easy WiFi setup via captive portal (no hardcoded credentials)
- ✅ **HTTPS Communication**: Secure data transmission to local server
- ✅ **Automatic Registration**: Devices register themselves on first connection
- ✅ **Sensor Support**: BME280 temperature/humidity/pressure sensor
- ✅ **Retry Logic**: Exponential backoff on failures
- ✅ **OTA Updates**: Check for firmware updates (implementation pending)
- ✅ **Time Sync**: Synchronizes clock with server
- ✅ **Watchdog Timer**: Auto-recovery from crashes
- ✅ **Status LED**: Visual feedback for connectivity and status

## Hardware Requirements

### Supported Boards

- ESP32 Dev Module
- ESP32 Feather (Adafruit, Unexpected Maker, etc.)
- ESP32-S2/S3 (with minor modifications)
- Any ESP32 board with WiFi

### Sensors Supported

**Out of the box**:
- BME280 (temperature, humidity, pressure) via I2C

**Easy to add** (see examples):
- DHT22 (temperature, humidity)
- DS18B20 (temperature)
- Any I2C, SPI, or analog sensor

### Wiring

**BME280 Sensor**:
```
BME280    →    ESP32
VCC       →    3.3V
GND       →    GND
SDA       →    GPIO 21
SCL       →    GPIO 22
```

**Status LED**:
- Built-in LED on GPIO 2 (most ESP32 boards)
- Or connect external LED to GPIO 2 + resistor

## Software Requirements

### PlatformIO (Recommended)

1. Install [PlatformIO IDE](https://platformio.org/install/ide?install=vscode) (VS Code extension)
2. Or install [PlatformIO CLI](https://platformio.org/install/cli)

### Arduino IDE (Alternative)

1. Install [Arduino IDE 2.0+](https://www.arduino.cc/en/software)
2. Add ESP32 board support:
   - File → Preferences
   - Additional Board Manager URLs: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "esp32" → Install

## Installation

### Method 1: PlatformIO (Recommended)

```bash
# Clone repository
git clone https://github.com/YOUR_REPO/localfeather.git
cd localfeather/firmware

# Connect ESP32 via USB
# Build and upload
pio run --target upload

# Monitor serial output
pio device monitor
```

### Method 2: Arduino IDE

1. Open `firmware/src/main.cpp` in Arduino IDE
2. Select board: **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
3. Select port: **Tools → Port → COMx** (Windows) or **/dev/ttyUSB0** (Linux)
4. Click Upload button (→)
5. Open Serial Monitor (Ctrl+Shift+M) at 115200 baud

## First-Time Setup

### Step 1: Flash Firmware

Flash the firmware using one of the methods above.

### Step 2: Connect to Setup WiFi

1. After flashing, ESP32 creates a WiFi network named: **LocalFeather-XXXXXX** (XXXXXX = last 6 digits of MAC)
2. Connect to this network with your phone/laptop
3. Captive portal should open automatically
   - If not, browse to: `http://192.168.4.1`

### Step 3: Configure WiFi and Server

In the captive portal:

1. Click "Configure WiFi"
2. Select your home/office WiFi network
3. Enter WiFi password
4. Enter server details:
   - **Server URL**: `http://raspberrypi.local:5000` (or your server's IP)
   - **Device ID**: Leave blank for auto-generated (e.g., `esp32-a1b2c3`)
   - **API Key**: Leave blank (generated on first connection)
5. Click "Save"

### Step 4: Verify Connection

1. ESP32 will restart and connect to your WiFi
2. Open Serial Monitor (115200 baud)
3. You should see:
   ```
   ✓ WiFi connected!
   IP Address: 192.168.1.XXX
   ✓ BME280 sensor found!
   ✓ Data sent successfully
   ✓ Device registered - API key saved
   ```

### Step 5: Approve Device (Server Side)

1. Go to Local Feather web interface
2. You should see notification: "New device detected"
3. Click "Approve" and give it a friendly name

**Done!** Your sensor is now sending data every 60 seconds.

## Configuration

### Change Reading Interval

**Option 1: Via Server** (Recommended)
- Server can update interval remotely
- Change in web UI: Device → Settings → Reading Interval

**Option 2: Modify Code**
Edit `main.cpp`:
```cpp
#define READING_INTERVAL 60000  // Change to desired value in milliseconds
```

Rebuild and upload.

### Re-enter Setup Mode

**Hold BOOT button for 10 seconds** - ESP32 will reset WiFi settings and restart in AP mode.

Or via code:
```cpp
wifiManager.resetSettings();
ESP.restart();
```

### Reset Everything

**Upload new firmware** - this clears all stored configuration.

Or erase flash manually:
```bash
# PlatformIO
pio run --target erase

# ESP tool
esptool.py erase_flash
```

## LED Status Indicators

| Pattern | Meaning |
|---------|---------|
| 3 quick blinks on boot | Setup complete, entering main loop |
| Single blink during reading | Successfully sent data |
| Solid on briefly | Taking sensor reading |
| Rapid continuous blinking | Setup mode / Captive portal active |

## Serial Monitor Output

**Normal operation**:
```
=================================
Local Feather ESP32 Firmware
Version: 1.0.0
=================================

--- Configuration ---
Server URL: http://192.168.1.100:5000
Device ID: esp32-a1b2c3
API Key: ***configured***
Reading Interval: 60000 ms

✓ WiFi connected!
IP Address: 192.168.1.105
Signal Strength: -45 dBm

✓ BME280 sensor found!

--- Sensor Reading ---
Temperature: 23.45 °C
Humidity: 55.20 %
Pressure: 1013.25 hPa

POST http://192.168.1.100:5000/api/readings
Response code: 200
Response: {"status":"ok","received":3}
✓ Data sent successfully
```

**Errors**:
```
❌ Failed to connect - rebooting...           # WiFi connection failed
❌ HTTP error: 401                            # Invalid API key
⚠ BME280 sensor not found                    # Sensor wiring issue
⚠ Rate limited - backing off                 # Sending too fast
⚠ Consecutive failures: 5                    # Server unreachable
```

## Troubleshooting

### ESP32 Won't Enter Setup Mode

1. **Power cycle**: Unplug and replug USB
2. **Force reset**: Hold BOOT, press/release RESET, release BOOT after 3 seconds
3. **Re-flash firmware**: Upload firmware again

### Can't Connect to WiFi

**Check**:
- Is WiFi 2.4GHz? (ESP32 doesn't support 5GHz)
- Is password correct? (case-sensitive!)
- Is network hidden? (unhide temporarily or configure manually)
- Is MAC filtering enabled? (add ESP32's MAC to allow list)

**Debug**:
- Open Serial Monitor at 115200 baud
- Look for WiFi connection errors
- Note signal strength (should be > -70 dBm)

### Sensor Not Detected

**Check wiring**:
- VCC → 3.3V (NOT 5V!)
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22

**Test I2C connection**:
```cpp
// Add to setup():
Wire.beginTransmission(0x76);
byte error = Wire.endTransmission();
Serial.printf("I2C device 0x76: %s\n", error == 0 ? "Found" : "Not found");
```

**BME280 has two possible I2C addresses**: 0x76 or 0x77
- Firmware tries both automatically
- Check your module's documentation

### Data Not Sending

**Check Serial Monitor**:
- "✓ Data sent successfully" = working
- "❌ HTTP error: XXX" = see error code

**Common errors**:
- **401**: Invalid API key → Re-register device
- **429**: Rate limited → Reduce frequency
- **-1**: Can't reach server → Check server IP/URL

**Verify server is reachable**:
```bash
# From another device on same network
curl http://192.168.1.100:5000/api/health
```

### High Failure Rate

**Check**:
- WiFi signal strength (Serial Monitor shows dBm)
- Server is running (`systemctl status localfeather`)
- Network congestion (too many devices)

**Improve reliability**:
- Move ESP32 closer to router
- Use Ethernet for server (Raspberry Pi)
- Increase READING_INTERVAL to reduce load

## Adding Custom Sensors

### Example: DHT22 Temperature/Humidity Sensor

1. **Install library**:

Edit `platformio.ini`:
```ini
lib_deps =
    ...existing...
    adafruit/DHT sensor library@^1.4.4
```

2. **Add includes** (main.cpp):
```cpp
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
```

3. **Initialize in setup()**:
```cpp
dht.begin();
```

4. **Read in main loop**:
```cpp
float temp = dht.readTemperature();
float humidity = dht.readHumidity();

if (!isnan(temp) && !isnan(humidity)) {
    sendReadings(temp, humidity, 0);
}
```

### Example: DS18B20 Temperature Sensor

See `examples/ds18b20/` for complete code.

### Example: Analog Sensor

```cpp
#define ANALOG_PIN 34

// Read analog value (0-4095)
int rawValue = analogRead(ANALOG_PIN);

// Convert to voltage (0-3.3V)
float voltage = rawValue * (3.3 / 4095.0);

// Send to server
JsonObject reading = readings.createNestedObject();
reading["sensor"] = "analog_sensor";
reading["value"] = voltage;
reading["unit"] = "V";
```

## Power Consumption

**Typical current draw**:
- Active (WiFi TX): ~120-160mA
- Active (idle): ~50-80mA
- Deep sleep: ~10µA (not implemented in v1.0)

**Battery operation**:
- 2000mAh battery: ~25-40 hours continuous
- With deep sleep (future): weeks to months

**For battery operation**:
- Use 3.7V LiPo battery
- Add TP4056 charging module
- Consider deep sleep mode (v2.0 feature)

## OTA Updates

**Currently**: OTA check is implemented but update download is not yet complete.

**Manual update procedure**:
1. Build new firmware
2. Connect ESP32 via USB
3. Upload new firmware

**Future v2.0**: Full OTA update support via server upload.

## Advanced Configuration

### Custom API Endpoint

Modify in code:
```cpp
String url = String(config.serverUrl) + "/api/readings";
// Change to: "/api/v2/readings" or custom endpoint
```

### Change I2C Pins

```cpp
#define I2C_SDA 21  // Change to your preferred pin
#define I2C_SCL 22  // Change to your preferred pin
```

### Disable Watchdog Timer

```cpp
// Comment out in setup():
// esp_task_wdt_init(WATCHDOG_TIMEOUT, true);
// esp_task_wdt_add(NULL);

// And in loop():
// esp_task_wdt_reset();
```

## Firmware Version

Current version: **1.0.0**

To change version, edit `platformio.ini`:
```ini
build_flags =
    -D VERSION=\"1.1.0\"  # Change here
```

Version is displayed in serial monitor and sent to server.

## Contributing

See main project [CONTRIBUTING.md](../docs/CONTRIBUTING.md)

**Adding sensor support?**
1. Create example in `examples/your_sensor/`
2. Document wiring and code changes
3. Submit pull request

## License

MIT License - see [LICENSE](../LICENSE)

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_REPO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_REPO/discussions)
- **Docs**: [Full documentation](../docs/)

---

**Built with**:
- Arduino framework for ESP32
- WiFiManager by tzapu
- ArduinoJson by Benoit Blanchon
- Adafruit BME280 library
