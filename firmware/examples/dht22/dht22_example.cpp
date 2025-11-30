/**
 * Local Feather - DHT22 Sensor Example
 *
 * This example shows how to use DHT22 (or DHT11) temperature and humidity sensor
 * instead of the BME280.
 *
 * Hardware:
 * - ESP32 board
 * - DHT22 sensor (or DHT11)
 *
 * Wiring:
 * DHT22    →    ESP32
 * VCC      →    3.3V (or 5V for DHT22)
 * GND      →    GND
 * DATA     →    GPIO 4 (with 10K pullup resistor to VCC)
 *
 * Library Required:
 * Add to platformio.ini:
 *   adafruit/DHT sensor library@^1.4.4
 *
 * Changes from main.cpp:
 * 1. Replace BME280 includes with DHT includes
 * 2. Replace setupSensor() function
 * 3. Replace readSensor() function
 * 4. Update sendReadings() to send only temp & humidity
 */

#include <DHT.h>

// DHT Sensor Configuration
#define DHT_PIN 4              // Data pin
#define DHT_TYPE DHT22         // DHT22 (AM2302) or DHT11

// Create DHT sensor object
DHT dht(DHT_PIN, DHT_TYPE);

/**
 * Setup DHT sensor
 * Replace setupSensor() in main.cpp with this
 */
void setupSensor() {
    Serial.println("Initializing DHT22 sensor...");

    dht.begin();

    // Test reading
    delay(2000); // DHT needs 2 seconds to stabilize
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (!isnan(temp) && !isnan(humidity)) {
        Serial.println("✓ DHT22 sensor found!");
        Serial.printf("  Test reading: %.1f°C, %.1f%%\n", temp, humidity);
        sensorAvailable = true;
    } else {
        Serial.println("⚠ DHT22 sensor not responding");
        Serial.println("  Check wiring and pullup resistor");
        sensorAvailable = false;
    }
}

/**
 * Read DHT sensor values
 * Replace readSensor() in main.cpp with this
 */
bool readSensor(float &temp, float &humidity, float &pressure) {
    if (!sensorAvailable) {
        return false;
    }

    // Read sensor
    temp = dht.readTemperature();      // Celsius
    humidity = dht.readHumidity();      // Percent
    pressure = 0.0;                     // DHT doesn't measure pressure

    // Check for failed reading
    if (isnan(temp) || isnan(humidity)) {
        Serial.println("❌ Failed to read from DHT sensor");
        return false;
    }

    // Optional: Convert to Fahrenheit
    // float tempF = dht.readTemperature(true);

    return true;
}

/**
 * Send readings to server
 * Modify sendReadings() to send only 2 readings instead of 3
 */
bool sendReadings(float temp, float humidity, float pressure) {
    // ... existing code up to creating readings array ...

    if (sensorAvailable) {
        // Temperature
        JsonObject reading1 = readings.createNestedObject();
        reading1["sensor"] = "temperature";
        reading1["value"] = temp;
        reading1["unit"] = "C";
        reading1["timestamp"] = time(nullptr);

        // Humidity
        JsonObject reading2 = readings.createNestedObject();
        reading2["sensor"] = "humidity";
        reading2["value"] = humidity;
        reading2["unit"] = "%";
        reading2["timestamp"] = time(nullptr);

        // No pressure reading for DHT22
    }

    // ... rest of existing code ...
}

/**
 * Notes:
 *
 * DHT11 vs DHT22:
 * - DHT11: Cheaper, less accurate (±2°C, ±5% humidity)
 * - DHT22: More expensive, more accurate (±0.5°C, ±2% humidity)
 *
 * Change DHT_TYPE to DHT11 if using DHT11
 *
 * Common Issues:
 * 1. NaN readings → Check pullup resistor (10K ohm)
 * 2. Intermittent readings → Power supply issue (use 5V instead of 3.3V)
 * 3. Slow response → DHT sensors are slow, readings take ~2 seconds
 *
 * Reading Frequency:
 * - DHT22: Max 0.5 Hz (once every 2 seconds)
 * - DHT11: Max 1 Hz (once per second)
 *
 * Don't poll faster than sensor supports!
 */
