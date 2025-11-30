/**
 * Local Feather - AHT20 Temperature & Humidity Sensor Example
 *
 * Adafruit Product: https://www.adafruit.com/product/4566
 *
 * This example shows how to use the AHT20 sensor with Local Feather.
 *
 * Sensor Specifications:
 * - Temperature range: -40°C to +85°C (±0.3°C accuracy)
 * - Humidity range: 0-100% RH (±2% accuracy)
 * - I2C address: 0x38 (fixed)
 * - Supply voltage: 2.0V to 5.5V
 * - Low power: ~0.25µA in sleep mode
 *
 * This is an excellent alternative to BME280 if you don't need pressure sensing.
 *
 * Hardware:
 * - ESP32 board
 * - AHT20 sensor breakout (Adafruit #4566)
 *
 * Library Required:
 * - Adafruit AHTX0 (handles AHT10/AHT20/AHT21)
 */

#include <Adafruit_AHTX0.h>

// Pin definitions (I2C)
#define I2C_SDA 21
#define I2C_SCL 22

// Sensor object
Adafruit_AHTX0 aht;

/**
 * Setup AHT20 sensor
 * Replace setupSensor() in main.cpp with this
 */
void setupSensor() {
    Serial.println("Initializing AHT20 sensor...");

    // Initialize I2C bus
    Wire.begin(I2C_SDA, I2C_SCL);

    // Initialize AHT20
    if (aht.begin()) {
        Serial.println("✓ AHT20 sensor found!");

        // Get sensor details
        sensors_event_t humidity, temp;
        aht.getEvent(&humidity, &temp);

        Serial.printf("  Temperature: %.2f °C\n", temp.temperature);
        Serial.printf("  Humidity: %.2f %%\n", humidity.relative_humidity);

        sensorAvailable = true;
    } else {
        Serial.println("❌ AHT20 sensor not found!");
        Serial.println("   Check wiring:");
        Serial.println("   - VIN → 3.3V");
        Serial.println("   - GND → GND");
        Serial.println("   - SDA → GPIO 21");
        Serial.println("   - SCL → GPIO 22");

        sensorAvailable = false;
    }
}

/**
 * Read AHT20 sensor values
 * Replace readSensor() in main.cpp with this
 */
bool readSensor(float &temp, float &humidity, float &pressure) {
    if (!sensorAvailable) {
        Serial.println("⚠ AHT20 not available");
        return false;
    }

    // Get sensor events
    sensors_event_t humidity_event, temp_event;
    aht.getEvent(&humidity_event, &temp_event);

    // Read values
    temp = temp_event.temperature;
    humidity = humidity_event.relative_humidity;
    pressure = 0.0; // AHT20 doesn't measure pressure

    // Validate readings
    if (isnan(temp) || isnan(humidity)) {
        Serial.println("❌ Failed to read from AHT20!");
        return false;
    }

    // AHT20 returns valid range checks
    if (temp < -40 || temp > 85) {
        Serial.printf("⚠ Temperature out of range: %.2f °C\n", temp);
        return false;
    }

    if (humidity < 0 || humidity > 100) {
        Serial.printf("⚠ Humidity out of range: %.2f %%\n", humidity);
        return false;
    }

    return true;
}

/**
 * WIRING DIAGRAM
 *
 * AHT20 Sensor Breakout (Adafruit #4566):
 *
 * AHT20 Breakout    →    ESP32
 * ─────────────────────────────
 * VIN (or 3V)       →    3.3V
 * GND               →    GND
 * SDA               →    GPIO 21
 * SCL               →    GPIO 22
 *
 * Notes:
 * - Breakout has built-in pull-up resistors (no external resistors needed)
 * - Can also use 5V for VIN if available (breakout has regulator)
 * - I2C address is fixed at 0x38 (cannot be changed)
 * - STEMMA QT / Qwiic compatible (use cable for tool-free connection)
 */

/**
 * COMPARISON: AHT20 vs BME280
 *
 * Similarities:
 * ✓ Both measure temperature and humidity
 * ✓ Both use I2C communication
 * ✓ Similar accuracy (±0.3°C temp, ±2% humidity)
 * ✓ Similar price point (~$5-10)
 * ✓ Low power consumption
 *
 * Differences:
 *
 * AHT20:
 * ✓ Simpler (only temp + humidity)
 * ✓ Fixed I2C address (0x38)
 * ✓ Slightly better humidity accuracy (±2% vs ±3%)
 * ✓ Faster readings (~80ms)
 * ✗ No pressure sensor
 * ✗ Only one I2C address option
 *
 * BME280:
 * ✓ Measures pressure (barometric altitude)
 * ✓ Two I2C addresses (0x76 or 0x77)
 * ✓ More environmental data
 * ✗ More complex (more configuration options)
 * ✗ Slightly lower humidity accuracy (±3%)
 *
 * When to use AHT20:
 * - Indoor monitoring (temperature + humidity only)
 * - Lower power requirements
 * - Simpler setup
 * - Don't need pressure/altitude data
 * - Already have multiple BME280s (avoid I2C address conflicts)
 *
 * When to use BME280:
 * - Weather stations (need pressure)
 * - Altitude measurement
 * - Need multiple sensors on same I2C bus
 */

/**
 * ADVANCED: Power Optimization for Battery Operation
 */
void setupLowPower() {
    // AHT20 automatically enters low-power mode between readings
    // Typical power consumption:
    // - Active measurement: ~980µA for 80ms
    // - Idle: ~0.25µA

    Serial.println("AHT20 power optimization:");
    Serial.println("  - Sensor auto-sleeps between readings");
    Serial.println("  - No manual sleep command needed");
    Serial.println("  - Consider ESP32 deep sleep for battery operation");
}

/**
 * ADVANCED: Multiple AHT20 Sensors
 *
 * Problem: AHT20 has fixed I2C address (0x38)
 *
 * Solution 1: Use I2C multiplexer (TCA9548A)
 * - Allows up to 8 AHT20 sensors on one I2C bus
 * - Switch between sensors via multiplexer
 *
 * Solution 2: Use multiple I2C buses
 * - ESP32 can have multiple I2C buses
 * - Wire.begin(21, 22) for bus 0
 * - Wire1.begin(25, 26) for bus 1
 */

// Example: Two AHT20 sensors via multiplexer
#ifdef USE_MULTIPLEXER
#include <Wire.h>
#define TCAADDR 0x70

Adafruit_AHTX0 aht1;
Adafruit_AHTX0 aht2;

void tcaSelect(uint8_t channel) {
    if (channel > 7) return;
    Wire.beginTransmission(TCAADDR);
    Wire.write(1 << channel);
    Wire.endTransmission();
}

void setupMultipleSensors() {
    Wire.begin(I2C_SDA, I2C_SCL);

    // Initialize first AHT20 on channel 0
    tcaSelect(0);
    if (aht1.begin()) {
        Serial.println("✓ AHT20 #1 found (indoor)");
    }

    // Initialize second AHT20 on channel 1
    tcaSelect(1);
    if (aht2.begin()) {
        Serial.println("✓ AHT20 #2 found (outdoor)");
    }
}

void readMultipleSensors(JsonArray &readings) {
    sensors_event_t humidity, temp;

    // Read first sensor
    tcaSelect(0);
    aht1.getEvent(&humidity, &temp);
    JsonObject r1 = readings.createNestedObject();
    r1["sensor"] = "indoor_temperature";
    r1["value"] = temp.temperature;
    r1["unit"] = "C";

    // Read second sensor
    tcaSelect(1);
    aht2.getEvent(&humidity, &temp);
    JsonObject r2 = readings.createNestedObject();
    r2["sensor"] = "outdoor_temperature";
    r2["value"] = temp.temperature;
    r2["unit"] = "C";
}
#endif

/**
 * TROUBLESHOOTING
 *
 * Sensor not found (returns false):
 * 1. Check wiring connections
 * 2. Verify I2C address: Run I2C scanner
 *    ```cpp
 *    Wire.beginTransmission(0x38);
 *    byte error = Wire.endTransmission();
 *    if (error == 0) Serial.println("AHT20 found at 0x38");
 *    ```
 * 3. Try different I2C pins if default don't work
 * 4. Check if SDA/SCL are swapped
 * 5. Ensure sensor has power (check 3.3V with multimeter)
 *
 * Reading NaN or invalid values:
 * 1. Wait 100ms after begin() before first reading
 * 2. Check if sensor is genuine AHT20 (not counterfeit)
 * 3. Try resetting ESP32
 * 4. Update Adafruit_AHTX0 library to latest version
 *
 * Inconsistent readings:
 * 1. Add 0.1µF capacitor between VIN and GND (near sensor)
 * 2. Use shorter I2C wires (<30cm for reliable operation)
 * 3. Move sensor away from heat sources (ESP32 chip can heat up)
 * 4. Average multiple readings for stability
 *
 * I2C bus conflicts:
 * 1. Check if other devices are using address 0x38
 * 2. Use I2C scanner to see all devices on bus
 * 3. Consider using I2C multiplexer for address conflicts
 */

/**
 * EXAMPLE: Averaging for Stability
 */
bool readSensorAveraged(float &temp, float &humidity, float &pressure, int samples = 5) {
    if (!sensorAvailable) return false;

    float tempSum = 0;
    float humiditySum = 0;
    int validSamples = 0;

    for (int i = 0; i < samples; i++) {
        sensors_event_t h, t;
        aht.getEvent(&h, &t);

        if (!isnan(t.temperature) && !isnan(h.relative_humidity)) {
            tempSum += t.temperature;
            humiditySum += h.relative_humidity;
            validSamples++;
        }

        delay(100); // Wait between samples
    }

    if (validSamples == 0) return false;

    temp = tempSum / validSamples;
    humidity = humiditySum / validSamples;
    pressure = 0.0;

    return true;
}

/**
 * EXAMPLE SERIAL OUTPUT
 *
 * Normal operation:
 * ```
 * Initializing AHT20 sensor...
 * ✓ AHT20 sensor found!
 *   Temperature: 23.45 °C
 *   Humidity: 55.20 %
 *
 * --- Sensor Reading ---
 * Temperature: 23.50 °C
 * Humidity: 55.10 %
 * ```
 *
 * Error case:
 * ```
 * Initializing AHT20 sensor...
 * ❌ AHT20 sensor not found!
 *    Check wiring:
 *    - VIN → 3.3V
 *    - GND → GND
 *    - SDA → GPIO 21
 *    - SCL → GPIO 22
 * ```
 */

/**
 * MIGRATION FROM BME280
 *
 * If you're switching from BME280 to AHT20:
 *
 * 1. Update platformio.ini:
 *    Remove: adafruit/Adafruit BME280 Library
 *    Add: adafruit/Adafruit AHTX0@^2.0.3
 *
 * 2. Change includes in main.cpp:
 *    Remove: #include <Adafruit_BME280.h>
 *    Add: #include <Adafruit_AHTX0.h>
 *
 * 3. Update sensor object:
 *    Remove: Adafruit_BME280 bme;
 *    Add: Adafruit_AHTX0 aht;
 *
 * 4. Change initialization:
 *    Remove: bme.begin(0x76) || bme.begin(0x77)
 *    Add: aht.begin()
 *
 * 5. Update reading code:
 *    Remove: bme.readTemperature(), bme.readHumidity()
 *    Add: aht.getEvent(&humidity, &temp)
 *
 * 6. Update server data (if tracking pressure):
 *    - Remove pressure readings from database
 *    - Or keep them and just send 0.0 for AHT20 devices
 *
 * Note: You can mix BME280 and AHT20 devices on the same server!
 * Just give them different device IDs.
 */

/**
 * PERFORMANCE NOTES
 *
 * Reading Time:
 * - AHT20: ~80ms per reading
 * - BME280: ~40ms per reading
 * - DHT22: ~2000ms per reading
 *
 * Power Consumption (3.3V):
 * - AHT20: 980µA active, 0.25µA sleep
 * - BME280: 714µA active, 0.1µA sleep
 * - DHT22: 2500µA active, 40µA standby
 *
 * For battery operation, AHT20 is excellent!
 */

/**
 * ADDITIONAL RESOURCES
 *
 * - Adafruit Product Page: https://www.adafruit.com/product/4566
 * - Adafruit Tutorial: https://learn.adafruit.com/adafruit-aht20
 * - Library Docs: https://github.com/adafruit/Adafruit_AHTX0
 * - Datasheet: Search "AHT20 datasheet" for full specifications
 * - I2C Scanner: https://playground.arduino.cc/Main/I2cScanner/
 */
