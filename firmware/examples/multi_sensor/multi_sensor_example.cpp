/**
 * Local Feather - Multi-Sensor Example
 *
 * This example shows how to combine multiple sensors on one ESP32.
 *
 * Sensors in this example:
 * - BME280: Temperature, Humidity, Pressure (I2C)
 * - DS18B20: Waterproof temperature (1-Wire)
 * - Soil moisture: Analog
 * - Light sensor (LDR): Analog
 *
 * This demonstrates:
 * 1. Multiple sensor types on one device
 * 2. Different communication protocols
 * 3. Sending many readings in one POST
 */

#include <Wire.h>
#include <Adafruit_BME280.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pin definitions
#define I2C_SDA 21
#define I2C_SCL 22
#define ONE_WIRE_BUS 4
#define SOIL_MOISTURE_PIN 34
#define LIGHT_SENSOR_PIN 35

// Sensor objects
Adafruit_BME280 bme;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);

// Sensor availability flags
bool bmeAvailable = false;
bool ds18b20Available = false;

/**
 * Setup all sensors
 */
void setupSensor() {
    Serial.println("Initializing sensors...");

    // I2C Bus
    Wire.begin(I2C_SDA, I2C_SCL);

    // BME280
    if (bme.begin(0x76) || bme.begin(0x77)) {
        Serial.println("✓ BME280 found (I2C)");
        bme.setSampling(Adafruit_BME280::MODE_FORCED,
                       Adafruit_BME280::SAMPLING_X1,
                       Adafruit_BME280::SAMPLING_X1,
                       Adafruit_BME280::SAMPLING_X1,
                       Adafruit_BME280::FILTER_OFF);
        bmeAvailable = true;
    } else {
        Serial.println("⚠ BME280 not found");
    }

    // DS18B20
    ds18b20.begin();
    if (ds18b20.getDeviceCount() > 0) {
        Serial.printf("✓ DS18B20 found (%d sensor(s))\n", ds18b20.getDeviceCount());
        ds18b20Available = true;
    } else {
        Serial.println("⚠ DS18B20 not found");
    }

    // Analog sensors
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);
    Serial.println("✓ Analog sensors configured");

    // At least one sensor should be available
    sensorAvailable = bmeAvailable || ds18b20Available;
}

/**
 * Read all sensors
 */
bool readAllSensors(JsonArray &readings) {
    unsigned long timestamp = time(nullptr);
    bool hasData = false;

    // Read BME280 (indoor environment)
    if (bmeAvailable) {
        bme.takeForcedMeasurement();

        float temp = bme.readTemperature();
        float humidity = bme.readHumidity();
        float pressure = bme.readPressure() / 100.0F;

        if (!isnan(temp)) {
            JsonObject r1 = readings.createNestedObject();
            r1["sensor"] = "indoor_temperature";
            r1["value"] = temp;
            r1["unit"] = "C";
            r1["timestamp"] = timestamp;
            hasData = true;
        }

        if (!isnan(humidity)) {
            JsonObject r2 = readings.createNestedObject();
            r2["sensor"] = "indoor_humidity";
            r2["value"] = humidity;
            r2["unit"] = "%";
            r2["timestamp"] = timestamp;
            hasData = true;
        }

        if (!isnan(pressure)) {
            JsonObject r3 = readings.createNestedObject();
            r3["sensor"] = "pressure";
            r3["value"] = pressure;
            r3["unit"] = "hPa";
            r3["timestamp"] = timestamp;
            hasData = true;
        }
    }

    // Read DS18B20 (outdoor/waterproof temperature)
    if (ds18b20Available) {
        ds18b20.requestTemperatures();
        float outdoorTemp = ds18b20.getTempCByIndex(0);

        if (outdoorTemp != DEVICE_DISCONNECTED_C && outdoorTemp > -55) {
            JsonObject r4 = readings.createNestedObject();
            r4["sensor"] = "outdoor_temperature";
            r4["value"] = outdoorTemp;
            r4["unit"] = "C";
            r4["timestamp"] = timestamp;
            hasData = true;
        }
    }

    // Read soil moisture
    int soilRaw = analogRead(SOIL_MOISTURE_PIN);
    float soilMoisture = map(soilRaw, 3100, 1400, 0, 100); // Calibrate these values!
    soilMoisture = constrain(soilMoisture, 0, 100);

    JsonObject r5 = readings.createNestedObject();
    r5["sensor"] = "soil_moisture";
    r5["value"] = soilMoisture;
    r5["unit"] = "%";
    r5["timestamp"] = timestamp;
    hasData = true;

    // Read light level
    int lightRaw = analogRead(LIGHT_SENSOR_PIN);
    float lightLevel = map(lightRaw, 4095, 0, 0, 100); // 0=dark, 100=bright

    JsonObject r6 = readings.createNestedObject();
    r6["sensor"] = "light_level";
    r6["value"] = lightLevel;
    r6["unit"] = "%";
    r6["timestamp"] = timestamp;
    hasData = true;

    return hasData;
}

/**
 * Modified send function to use readAllSensors
 */
bool sendReadings(float unused1, float unused2, float unused3) {
    if (strlen(config.serverUrl) == 0) {
        Serial.println("❌ Server URL not configured");
        return false;
    }

    String url = String(config.serverUrl) + "/api/readings";
    Serial.printf("\nPOST %s\n", url.c_str());

    // Create JSON payload
    StaticJsonDocument<1024> doc; // Larger buffer for multiple sensors
    doc["device_id"] = config.deviceId;
    doc["api_key"] = strlen(config.apiKey) > 0 ? config.apiKey : "";

    JsonArray readings = doc.createNestedArray("readings");

    // Read all sensors
    if (!readAllSensors(readings)) {
        Serial.println("❌ No sensor data available");
        return false;
    }

    String payload;
    serializeJson(doc, payload);

    Serial.printf("Payload size: %d bytes\n", payload.length());
    Serial.printf("Sending %d readings\n", readings.size());

    // Send HTTP POST
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(15000); // Longer timeout for more data

    int httpCode = http.POST(payload);
    String response = http.getString();

    Serial.printf("Response code: %d\n", httpCode);

    bool success = (httpCode == 200);
    if (success) {
        Serial.println("✓ All sensor data sent successfully");
    }

    http.end();
    return success;
}

/**
 * Example Serial Output:
 *
 * Initializing sensors...
 * ✓ BME280 found (I2C)
 * ✓ DS18B20 found (1 sensor(s))
 * ✓ Analog sensors configured
 *
 * POST http://192.168.1.100:5000/api/readings
 * Payload size: 687 bytes
 * Sending 6 readings
 * Response code: 200
 * ✓ All sensor data sent successfully
 *
 * Dashboard will show:
 * - Indoor Temperature: 22.5°C (BME280)
 * - Indoor Humidity: 55% (BME280)
 * - Pressure: 1013 hPa (BME280)
 * - Outdoor Temperature: 15.2°C (DS18B20)
 * - Soil Moisture: 45% (Analog)
 * - Light Level: 78% (Analog)
 */

/**
 * Benefits of Multi-Sensor Setup:
 *
 * 1. Single device, multiple measurements
 * 2. All data timestamped together
 * 3. Reduced WiFi overhead (one POST vs many)
 * 4. Better correlation (indoor vs outdoor temp)
 * 5. More complete environmental picture
 *
 * Use Cases:
 * - Greenhouse: Indoor temp/humidity + soil moisture + light
 * - Aquarium: Water temp (DS18B20) + room temp (BME280)
 * - Weather station: Outdoor temp + pressure + light
 * - Smart garden: Soil moisture + light + temperature
 */

/**
 * Tips:
 *
 * 1. Power Consumption:
 *    - More sensors = more power
 *    - Consider deep sleep for battery operation
 *    - Disable unused sensors in code
 *
 * 2. I2C Address Conflicts:
 *    - Each I2C device needs unique address
 *    - BME280: 0x76 or 0x77
 *    - If conflict, use I2C multiplexer (TCA9548A)
 *
 * 3. Timing:
 *    - DS18B20 conversion takes 750ms (12-bit)
 *    - DHT sensors need 2-second delay
 *    - Plan your reading sequence
 *
 * 4. JSON Size:
 *    - More sensors = bigger JSON payload
 *    - Increase StaticJsonDocument size if needed
 *    - Monitor serial output for "payload size"
 *
 * 5. Error Handling:
 *    - Check each sensor individually
 *    - Send partial data if some sensors fail
 *    - Log which sensor failed
 */
