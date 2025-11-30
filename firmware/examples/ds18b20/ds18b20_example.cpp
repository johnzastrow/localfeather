/**
 * Local Feather - DS18B20 Temperature Sensor Example
 *
 * This example shows how to use DS18B20 waterproof temperature sensor.
 * Great for outdoor or water temperature monitoring.
 *
 * Hardware:
 * - ESP32 board
 * - DS18B20 temperature sensor (waterproof probe available)
 *
 * Wiring:
 * DS18B20  →    ESP32
 * RED      →    3.3V
 * BLACK    →    GND
 * YELLOW   →    GPIO 4 (with 4.7K pullup resistor to 3.3V)
 *
 * Libraries Required:
 * Add to platformio.ini:
 *   paulstoffregen/OneWire@^2.3.7
 *   milesburton/DallasTemperature@^3.11.0
 *
 * Features:
 * - Multiple sensors on same bus (up to 127!)
 * - Each sensor has unique 64-bit address
 * - Waterproof versions available
 * - Wide temperature range: -55°C to +125°C
 * - Accuracy: ±0.5°C
 */

#include <OneWire.h>
#include <DallasTemperature.h>

// Pin configuration
#define ONE_WIRE_BUS 4         // Data pin (needs 4.7K pullup)

// Create OneWire instance
OneWire oneWire(ONE_WIRE_BUS);

// Create DallasTemperature instance
DallasTemperature sensors(&oneWire);

// Variables for sensor addresses
int numberOfSensors = 0;
DeviceAddress sensor1Address;  // Store first sensor address

/**
 * Setup DS18B20 sensor(s)
 * Replace setupSensor() in main.cpp with this
 */
void setupSensor() {
    Serial.println("Initializing DS18B20 sensor(s)...");

    sensors.begin();

    // Get number of sensors on bus
    numberOfSensors = sensors.getDeviceCount();
    Serial.printf("Found %d DS18B20 sensor(s)\n", numberOfSensors);

    if (numberOfSensors == 0) {
        Serial.println("⚠ No DS18B20 sensors found");
        Serial.println("  Check wiring and pullup resistor (4.7K ohm)");
        sensorAvailable = false;
        return;
    }

    // Get address of first sensor
    if (sensors.getAddress(sensor1Address, 0)) {
        Serial.print("✓ Sensor 0 address: ");
        printAddress(sensor1Address);
        Serial.println();

        // Set resolution (9-12 bits, higher = more accurate but slower)
        sensors.setResolution(sensor1Address, 12); // 12-bit = 0.0625°C resolution
        sensorAvailable = true;
    } else {
        Serial.println("❌ Failed to get sensor address");
        sensorAvailable = false;
    }

    // If you have multiple sensors, enumerate them:
    for (int i = 0; i < numberOfSensors; i++) {
        DeviceAddress tempAddress;
        if (sensors.getAddress(tempAddress, i)) {
            Serial.printf("Sensor %d: ", i);
            printAddress(tempAddress);
            Serial.println();
        }
    }
}

/**
 * Read DS18B20 sensor value
 * Replace readSensor() in main.cpp with this
 */
bool readSensor(float &temp, float &humidity, float &pressure) {
    if (!sensorAvailable) {
        return false;
    }

    // Request temperature reading
    sensors.requestTemperatures();

    // Read temperature from first sensor
    temp = sensors.getTempC(sensor1Address);

    // DS18B20 only measures temperature
    humidity = 0.0;
    pressure = 0.0;

    // Check for error (sensor returns -127°C on error)
    if (temp == DEVICE_DISCONNECTED_C || temp < -55 || temp > 125) {
        Serial.println("❌ DS18B20 reading error");
        return false;
    }

    return true;
}

/**
 * Send readings to server
 * Modify to send only temperature
 */
bool sendReadings(float temp, float humidity, float pressure) {
    // ... existing code up to creating readings array ...

    if (sensorAvailable) {
        // Temperature only
        JsonObject reading1 = readings.createNestedObject();
        reading1["sensor"] = "temperature";
        reading1["value"] = temp;
        reading1["unit"] = "C";
        reading1["timestamp"] = time(nullptr);
    }

    // ... rest of existing code ...
}

/**
 * Helper function to print sensor address
 */
void printAddress(DeviceAddress deviceAddress) {
    for (uint8_t i = 0; i < 8; i++) {
        if (deviceAddress[i] < 16) Serial.print("0");
        Serial.print(deviceAddress[i], HEX);
    }
}

/**
 * ADVANCED: Multiple Sensors Example
 *
 * If you have multiple DS18B20 sensors on the same bus,
 * you can read all of them and send separate readings:
 */

void readAndSendMultipleSensors() {
    sensors.requestTemperatures();

    for (int i = 0; i < numberOfSensors; i++) {
        DeviceAddress tempAddress;
        if (sensors.getAddress(tempAddress, i)) {
            float temp = sensors.getTempC(tempAddress);

            if (temp != DEVICE_DISCONNECTED_C) {
                // Create unique sensor name
                char sensorName[32];
                snprintf(sensorName, sizeof(sensorName), "temperature_%d", i);

                JsonObject reading = readings.createNestedObject();
                reading["sensor"] = sensorName;
                reading["value"] = temp;
                reading["unit"] = "C";
                reading["timestamp"] = time(nullptr);

                Serial.printf("Sensor %d: %.2f°C\n", i, temp);
            }
        }
    }
}

/**
 * ADVANCED: Use Specific Sensor Address
 *
 * If you want to always read from a specific sensor (even if order changes),
 * use its unique address:
 */

void useSpecificSensor() {
    // Replace with your sensor's actual address
    DeviceAddress specificSensor = {0x28, 0xFF, 0x64, 0x1E, 0x8C, 0x16, 0x03, 0x8E};

    sensors.requestTemperatures();
    float temp = sensors.getTempC(specificSensor);

    Serial.printf("Specific sensor temp: %.2f°C\n", temp);
}

/**
 * Notes:
 *
 * Resolution vs Speed:
 * - 9-bit: 0.5°C resolution, 93.75 ms conversion time
 * - 10-bit: 0.25°C resolution, 187.5 ms conversion time
 * - 11-bit: 0.125°C resolution, 375 ms conversion time
 * - 12-bit: 0.0625°C resolution, 750 ms conversion time
 *
 * Power Modes:
 * - Normal mode: Needs VCC + GND + DATA (3 wires)
 * - Parasitic mode: Power from DATA line (2 wires only)
 *   → Not recommended for ESP32 (power issues)
 *
 * Troubleshooting:
 * 1. Reads -127°C → Sensor disconnected or bad wiring
 * 2. No sensors found → Check pullup resistor (4.7K ohm required!)
 * 3. Erratic readings → Use shorter cable (<3 meters for reliable readings)
 * 4. Slow readings → Lower resolution or use async mode
 *
 * Waterproof Version:
 * - Available with stainless steel probe
 * - Perfect for aquariums, outdoor, sous-vide
 * - Cable length: 1-3 meters typical
 * - Same wiring, just waterproof!
 */
