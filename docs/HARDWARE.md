# Hardware Documentation

This document details the specific hardware used in the LocalFeather project, including pinouts, configurations, and troubleshooting notes.

## Development Hardware

### ESP32 Development Board

**Model:** Adafruit ESP32 Feather V2 with 8MB Flash + 2MB PSRAM
**Product:** https://www.adafruit.com/product/5400

**Specifications:**
- Microcontroller: ESP32-PICO-V3-02 (ESP32-D0WD-V3)
- Flash: 8 MB
- PSRAM: 2 MB
- WiFi: 2.4 GHz 802.11b/g/n
- Bluetooth: BLE 4.2
- Operating Voltage: 3.3V
- USB: USB-C (CP2104 USB-to-Serial converter)
- Battery: JST-PH 2-pin connector for LiPoly battery (with built-in charger)
- Dimensions: 2.0" x 0.9" (51mm x 23mm)

**Key Features:**
- Built-in RGB NeoPixel LED (GPIO 0)
- Built-in blue LED (GPIO 2)
- STEMMA QT / Qwiic connector for I2C devices (no soldering required)
- Reset and Boot buttons
- Auto-reset for uploading code

**MAC Address:** `24:DC:C3:B8:33:B0`
**Device ID:** `esp32-3323b0` (derived from last 3 bytes of MAC)

### Sensor Hardware

**Model:** Adafruit AHT20 Temperature & Humidity Sensor
**Product:** https://www.adafruit.com/product/4566

**Specifications:**
- Temperature Range: -40°C to 85°C (±0.3°C accuracy)
- Humidity Range: 0% to 100% RH (±2% accuracy)
- I2C Address: 0x38 (fixed, not configurable)
- Operating Voltage: 2.2V to 5.5V (works with 3.3V from ESP32)
- Interface: I2C via STEMMA QT / Qwiic connectors
- Dimensions: 1.0" x 0.7" (25mm x 18mm)

**Key Features:**
- Two STEMMA QT connectors (daisy-chainable)
- Pre-calibrated, ready to use
- Low power consumption
- No external components required

**Connection Notes:**
- Both I2C connectors are functional (if one has poor connection, try the other)
- Uses 4-pin JST SH cable (STEMMA QT standard)
- No pull-up resistors needed (included on breakout board)

## Pin Configuration

### ESP32 Feather V2 STEMMA QT Pinout

**CRITICAL:** The ESP32 Feather V2 uses **GPIO 3 and GPIO 4** for the STEMMA QT connector, NOT the typical GPIO 21/22 used on generic ESP32 boards.

```
STEMMA QT Connector Pinout:
┌─────────────────┐
│ 1  2  3  4      │  (Looking at connector from front)
└─────────────────┘
  │  │  │  │
  │  │  │  └─ SDA  (GPIO 3)  - White wire
  │  │  └─── SCL  (GPIO 4)  - Yellow wire
  │  └────── 3.3V            - Red wire
  └───────── GND             - Black wire
```

### Pin Definitions in Firmware

```cpp
// firmware/src/main.cpp
#define LED_PIN 2              // Built-in blue LED
#define I2C_SDA 3              // STEMMA QT SDA (I2C Data)
#define I2C_SCL 4              // STEMMA QT SCL (I2C Clock)
```

### I2C Bus Initialization

```cpp
Wire.begin(I2C_SDA, I2C_SCL);
Wire.setClock(100000);  // 100 kHz I2C clock (standard mode)
```

**Notes:**
- I2C frequency: 100 kHz (standard mode, compatible with most sensors)
- Pull-up resistors: 10kΩ included on AHT20 breakout
- Multiple devices: Can daisy-chain up to ~10 devices on STEMMA QT bus

## Common Pitfalls

### ❌ Wrong I2C Pins
**Problem:** Using GPIO 21/22 (generic ESP32 pins) instead of GPIO 3/4
**Symptom:** I2C scanner finds no devices, sensor not detected
**Solution:** Always use GPIO 3/4 for ESP32 Feather V2 STEMMA QT

### ❌ Poor Connector Contact
**Problem:** STEMMA QT connector not fully seated
**Symptom:** Intermittent sensor readings, device disappears from I2C bus
**Solution:**
- Firmly press connector until it clicks
- Try the other connector on the sensor (both are functional)
- Check for debris in connector

### ❌ Wrong I2C Address
**Problem:** Scanning for wrong I2C address
**Symptom:** Device not found even with correct wiring
**Solution:** AHT20 is always at address 0x38 (not configurable)

## Firmware Configuration

### PlatformIO Configuration

**File:** `platformio.ini`

```ini
[env:adafruit_feather_esp32_v2]
platform = espressif32
board = adafruit_feather_esp32_v2
framework = arduino
monitor_speed = 115200
upload_speed = 921600

lib_deps =
    adafruit/Adafruit AHTX0@^2.0.5
    bblanchon/ArduinoJson@^7.2.1
    tzapu/WiFiManager@^2.0.17
```

### Upload Settings

**Serial Port:** Auto-detected (CP2104 USB-to-Serial)
**Upload Speed:** 921600 baud
**Monitor Speed:** 115200 baud

**Upload Commands:**
```bash
cd firmware
pio run --target upload          # Build and upload
pio device monitor               # Open serial monitor
```

## Power Configuration

### USB Power
- Voltage: 5V via USB-C
- Current: Up to 500mA from USB port
- Usage: Development and testing

### Battery Power (Optional)
- Connector: JST-PH 2-pin
- Battery: 3.7V LiPoly/LiIon
- Capacity: 500mAh to 6000mAh recommended
- Charging: Automatic via USB when connected
- Charge Rate: 200mA

**Power Consumption (Measured):**
- Active (WiFi on): ~80-120 mA
- Sensor reading: ~2-3 mA additional
- Deep sleep: ~10 µA (not currently implemented)

## Network Configuration

### WiFi Settings

**SSID:** bobby24
**Frequency:** 2.4 GHz (5 GHz not supported by ESP32)
**Security:** WPA2
**IP Address:** 192.168.1.83 (DHCP assigned)
**Signal Strength:** -53 to -61 dBm (excellent)

**Configuration Method:**
1. On first boot, ESP32 creates WiFi access point: `LocalFeather-Setup`
2. Connect to this network from phone/laptop
3. Captive portal opens automatically (or visit 192.168.4.1)
4. Enter WiFi credentials and server URL
5. ESP32 reboots and connects to configured network

**WiFiManager Portal:**
- AP SSID: `LocalFeather-Setup`
- AP Password: None (open network)
- Portal IP: 192.168.4.1
- Timeout: 180 seconds (3 minutes)

### Server Configuration

**Server URL:** http://192.168.1.234:5000
**Device Registration:** POST /api/register
**Data Submission:** POST /api/readings
**Reading Interval:** 60 seconds (60000 ms)

## Sensor Calibration

### AHT20 Calibration

**Factory Calibration:**
- The AHT20 comes pre-calibrated from factory
- No user calibration required
- Calibration data stored in sensor's non-volatile memory

**Accuracy Specifications:**
- Temperature: ±0.3°C (typical)
- Humidity: ±2% RH (typical)

**Verification:**
- Compare readings with known reference (e.g., weather station)
- Typical room temperature: 20-25°C (68-77°F)
- Typical indoor humidity: 30-50% RH

**Current Readings (Verified):**
- Temperature: 23.82°C (74.88°F) - reasonable for indoor environment
- Humidity: 28.62% RH - reasonable for dry indoor environment

## Troubleshooting Hardware

### I2C Scanner Tool

Built-in I2C scanner function in firmware (added during development):

```cpp
void scanI2C() {
    Serial.println("\nScanning I2C bus...");
    byte error, address;
    int devicesFound = 0;

    for (address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();

        if (error == 0) {
            Serial.printf("  ✓ Device found at address 0x%02X\n", address);
            devicesFound++;
        }
    }

    if (devicesFound == 0) {
        Serial.println("  ⚠ No I2C devices found");
        Serial.println("  Check wiring and pull-up resistors");
    } else {
        Serial.printf("  Found %d device(s)\n", devicesFound);
    }
}
```

**Expected Output (AHT20 connected):**
```
Scanning I2C bus...
  ✓ Device found at address 0x38
  Found 1 device(s)
```

### Serial Monitor Commands

**View Device Info:**
- Device ID printed on boot
- MAC address printed on boot
- WiFi connection status
- Sensor readings every 60 seconds

**Monitor Output:**
```bash
pio device monitor
```

**Expected Boot Sequence:**
```
LocalFeather ESP32 - Temperature & Humidity Monitor
Version: 1.0.0
==================================================

📟 Device ID: esp32-3323b0

Connecting to WiFi: bobby24
WiFi connected!
IP Address: 192.168.1.83
Signal Strength: -53 dBm

Scanning I2C bus...
  ✓ Device found at address 0x38
  Found 1 device(s)

✓ AHT20 sensor initialized

Temperature: 23.82°C
Humidity: 28.62%
```

## Hardware Expansion

### Adding More Sensors

The STEMMA QT system allows daisy-chaining multiple I2C devices:

**Compatible Sensors:**
- SCD-40 (CO2, temperature, humidity) - 0x62
- BMP390 (pressure, temperature) - 0x77
- SGP30 (air quality) - 0x58
- VEML7700 (light) - 0x10
- Many more Adafruit STEMMA QT sensors

**Connection:**
1. Connect first sensor to ESP32 STEMMA QT port
2. Connect second sensor to first sensor's second STEMMA QT port
3. Continue daisy-chaining as needed
4. Each sensor must have a unique I2C address

**Firmware Changes Required:**
- Initialize additional sensor libraries
- Add sensor reading functions
- Update JSON payload to include new sensors

### Adding More ESP32 Devices

**Current Device:** `esp32-3323b0`

**To Add More Devices:**
1. Each ESP32 gets unique device ID (from MAC address)
2. Each device gets unique API key on registration
3. Server already supports multiple devices
4. No server code changes needed

**Scaling Limits:**
- Server can handle 20+ devices @ 1 reading/min
- Network: Limited by WiFi AP capacity (typically 30-50 devices)
- Database: Essentially unlimited with proper indexing

## Reference Links

**ESP32 Feather V2:**
- Product Page: https://www.adafruit.com/product/5400
- Pinout Diagram: https://learn.adafruit.com/adafruit-esp32-feather-v2
- Schematic: https://learn.adafruit.com/adafruit-esp32-feather-v2/downloads

**AHT20 Sensor:**
- Product Page: https://www.adafruit.com/product/4566
- Datasheet: https://cdn-learn.adafruit.com/assets/assets/000/091/676/original/AHT20-datasheet-2020-4-16.pdf
- Arduino Library: https://github.com/adafruit/Adafruit_AHTX0

**STEMMA QT / Qwiic:**
- Standard: https://learn.adafruit.com/introducing-adafruit-stemma-qt
- Compatible with Qwiic (SparkFun)
- 4-pin JST SH 1.0mm pitch connector

**PlatformIO:**
- Documentation: https://docs.platformio.org/
- ESP32 Platform: https://docs.platformio.org/en/latest/platforms/espressif32.html
- Board Definition: https://docs.platformio.org/en/latest/boards/espressif32/adafruit_feather_esp32_v2.html

## Development Notes

### Lessons Learned

1. **I2C Pin Confusion:**
   - Always check board-specific pinouts
   - ESP32 Feather V2 STEMMA QT uses GPIO 3/4, not generic GPIO 21/22
   - Spent significant time debugging before discovering pin mismatch

2. **Connector Issues:**
   - STEMMA QT connectors can have poor contact
   - Both connectors on sensor are functional - try both if one fails
   - Always verify with I2C scanner before assuming hardware failure

3. **Buffer Sizing:**
   - C strings need +1 byte for null terminator
   - 64-character hex string requires 65-byte buffer minimum
   - Used 128 bytes to provide safety margin

4. **WiFi Reliability:**
   - 2.4 GHz WiFi required (ESP32 doesn't support 5 GHz)
   - Signal strength of -50 to -70 dBm is excellent
   - WiFiManager makes setup easy for non-technical users

### Future Hardware Considerations

1. **Power Optimization:**
   - Implement deep sleep between readings
   - Could extend battery life from hours to weeks
   - Trade-off: More complex wake-up logic

2. **Additional Sensors:**
   - CO2 sensor (SCD-40) for air quality monitoring
   - Pressure sensor (BMP390) for weather prediction
   - Light sensor (VEML7700) for room occupancy

3. **Enclosure:**
   - Need ventilated enclosure for accurate readings
   - Consider 3D printed case with mounting holes
   - Ensure sensor has airflow access

4. **External Antenna:**
   - ESP32 Feather V2 has U.FL connector for external antenna
   - Could improve WiFi range if needed
   - Not required for typical home use

## Version History

**Firmware Version:** 1.0.0

**Hardware Revisions:**
- v1.0 (2025-12-04): Initial working configuration with ESP32 Feather V2 + AHT20

**Changes Since Initial Development:**
- Fixed I2C pins from GPIO 21/22 to GPIO 3/4
- Added I2C scanner for diagnostics
- Increased API key buffer from 64 to 128 bytes
- Verified sensor accuracy with real-world readings
