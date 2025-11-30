/**
 * Local Feather - ESP32 Firmware
 *
 * Sends sensor data to local server without requiring cloud connectivity.
 *
 * Features:
 * - WiFiManager for easy WiFi setup (captive portal)
 * - HTTPS POST to send sensor readings
 * - OTA firmware updates
 * - Automatic retry with exponential backoff
 * - BME280 sensor support (temperature, humidity, pressure)
 *
 * Version: 1.0.0
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <esp_task_wdt.h>
#include <esp_ota_ops.h>

// Firmware version
const char* FIRMWARE_VERSION = VERSION;

// Pin definitions
#define LED_PIN 2              // Built-in LED for status indication
#define I2C_SDA 21             // I2C Data pin
#define I2C_SCL 22             // I2C Clock pin

// Configuration
#define READING_INTERVAL 60000  // Default: 60 seconds between readings
#define WATCHDOG_TIMEOUT 300    // 5 minutes watchdog timeout
#define MAX_RETRY_ATTEMPTS 3
#define RETRY_DELAY_BASE 5000   // Base delay for exponential backoff

// Global objects
WiFiManager wifiManager;
Preferences preferences;
Adafruit_BME280 bme;
HTTPClient http;

// Configuration storage
struct Config {
    char serverUrl[128];
    char deviceId[32];
    char apiKey[64];
    int readingInterval;
} config;

// Status tracking
unsigned long lastReadingTime = 0;
unsigned long lastOTACheck = 0;
int consecutiveFailures = 0;
bool sensorAvailable = false;

// Function declarations
void setupWiFi();
void loadConfig();
void saveConfig();
void setupSensor();
bool readSensor(float &temp, float &humidity, float &pressure);
bool sendReadings(float temp, float humidity, float pressure);
void checkForOTAUpdate();
void handleConfigPortal();
void blinkLED(int times, int delayMs);
String getDeviceId();

/**
 * Setup - runs once on boot
 */
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n\n=================================");
    Serial.println("Local Feather ESP32 Firmware");
    Serial.printf("Version: %s\n", FIRMWARE_VERSION);
    Serial.println("=================================\n");

    // Initialize LED
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // Initialize watchdog timer
    esp_task_wdt_init(WATCHDOG_TIMEOUT, true);
    esp_task_wdt_add(NULL);

    // Load configuration from NVS
    loadConfig();

    // Initialize I2C for sensors
    Wire.begin(I2C_SDA, I2C_SCL);

    // Setup sensor
    setupSensor();

    // Setup WiFi
    setupWiFi();

    // Initial LED pattern: 3 quick blinks = ready
    blinkLED(3, 200);

    Serial.println("\n✓ Setup complete - entering main loop\n");
}

/**
 * Main loop
 */
void loop() {
    // Reset watchdog timer
    esp_task_wdt_reset();

    // Check if it's time to take a reading
    if (millis() - lastReadingTime >= config.readingInterval) {
        lastReadingTime = millis();

        // Blink LED to show activity
        digitalWrite(LED_PIN, HIGH);

        if (sensorAvailable) {
            float temp, humidity, pressure;

            if (readSensor(temp, humidity, pressure)) {
                Serial.println("\n--- Sensor Reading ---");
                Serial.printf("Temperature: %.2f °C\n", temp);
                Serial.printf("Humidity: %.2f %%\n", humidity);
                Serial.printf("Pressure: %.2f hPa\n", pressure);

                // Send to server
                if (sendReadings(temp, humidity, pressure)) {
                    consecutiveFailures = 0;
                    blinkLED(1, 100); // Quick blink = success
                } else {
                    consecutiveFailures++;
                    Serial.printf("⚠ Consecutive failures: %d\n", consecutiveFailures);

                    // If too many failures, reboot after 24 hours
                    if (consecutiveFailures >= 288) { // 24 hours at 5min intervals
                        Serial.println("❌ Too many failures - rebooting...");
                        delay(1000);
                        ESP.restart();
                    }
                }
            } else {
                Serial.println("❌ Failed to read sensor");
            }
        } else {
            Serial.println("⚠ No sensor detected - sending dummy data");
            // Send dummy data to show device is alive
            sendReadings(0.0, 0.0, 0.0);
        }

        digitalWrite(LED_PIN, LOW);
    }

    // Check for OTA updates every 6 hours
    if (millis() - lastOTACheck >= 21600000) {
        lastOTACheck = millis();
        checkForOTAUpdate();
    }

    // Handle WiFi Manager if button pressed
    // (Hold BOOT button for 10 seconds to re-enter config mode)
    if (digitalRead(0) == LOW) { // BOOT button
        unsigned long pressStart = millis();
        while (digitalRead(0) == LOW && millis() - pressStart < 10000) {
            delay(100);
        }
        if (millis() - pressStart >= 10000) {
            Serial.println("\n🔧 Entering configuration mode...");
            handleConfigPortal();
        }
    }

    delay(100); // Small delay to prevent tight loop
}

/**
 * Setup WiFi using WiFiManager
 */
void setupWiFi() {
    Serial.println("Setting up WiFi...");

    // Set custom parameters for config portal
    WiFiManagerParameter custom_server("server", "Server URL", config.serverUrl, 128);
    WiFiManagerParameter custom_device_id("device_id", "Device ID", config.deviceId, 32);
    WiFiManagerParameter custom_api_key("api_key", "API Key (leave blank for new device)", config.apiKey, 64);

    wifiManager.addParameter(&custom_server);
    wifiManager.addParameter(&custom_device_id);
    wifiManager.addParameter(&custom_api_key);

    // Set timeout for config portal
    wifiManager.setConfigPortalTimeout(300); // 5 minutes

    // Custom AP name based on device ID
    String apName = "LocalFeather-" + getDeviceId();

    // Try to connect to saved WiFi
    Serial.printf("Connecting to WiFi (AP: %s)...\n", apName.c_str());

    if (!wifiManager.autoConnect(apName.c_str())) {
        Serial.println("❌ Failed to connect - rebooting...");
        delay(3000);
        ESP.restart();
    }

    Serial.println("✓ WiFi connected!");
    Serial.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Signal Strength: %d dBm\n", WiFi.RSSI());

    // Save configuration from portal
    strncpy(config.serverUrl, custom_server.getValue(), sizeof(config.serverUrl));
    strncpy(config.deviceId, custom_device_id.getValue(), sizeof(config.deviceId));
    strncpy(config.apiKey, custom_api_key.getValue(), sizeof(config.apiKey));

    // Use MAC-based device ID if none provided
    if (strlen(config.deviceId) == 0) {
        String devId = getDeviceId();
        strncpy(config.deviceId, devId.c_str(), sizeof(config.deviceId));
    }

    saveConfig();

    // Register with server if no API key
    if (strlen(config.apiKey) == 0) {
        Serial.println("\nNo API key found - registering with server...");
        // Registration happens on first data send
    }
}

/**
 * Handle config portal (re-enter setup mode)
 */
void handleConfigPortal() {
    wifiManager.resetSettings();
    ESP.restart();
}

/**
 * Load configuration from NVS (non-volatile storage)
 */
void loadConfig() {
    preferences.begin("localfeather", false);

    preferences.getString("serverUrl", config.serverUrl, sizeof(config.serverUrl));
    preferences.getString("deviceId", config.deviceId, sizeof(config.deviceId));
    preferences.getString("apiKey", config.apiKey, sizeof(config.apiKey));
    config.readingInterval = preferences.getInt("interval", READING_INTERVAL);

    preferences.end();

    Serial.println("\n--- Configuration ---");
    Serial.printf("Server URL: %s\n", strlen(config.serverUrl) > 0 ? config.serverUrl : "(not set)");
    Serial.printf("Device ID: %s\n", strlen(config.deviceId) > 0 ? config.deviceId : "(not set)");
    Serial.printf("API Key: %s\n", strlen(config.apiKey) > 0 ? "***configured***" : "(not set)");
    Serial.printf("Reading Interval: %d ms\n", config.readingInterval);
    Serial.println();
}

/**
 * Save configuration to NVS
 */
void saveConfig() {
    preferences.begin("localfeather", false);

    preferences.putString("serverUrl", config.serverUrl);
    preferences.putString("deviceId", config.deviceId);
    preferences.putString("apiKey", config.apiKey);
    preferences.putInt("interval", config.readingInterval);

    preferences.end();

    Serial.println("✓ Configuration saved");
}

/**
 * Setup sensor (BME280)
 */
void setupSensor() {
    Serial.println("Initializing BME280 sensor...");

    unsigned status = bme.begin(0x76); // Try address 0x76
    if (!status) {
        status = bme.begin(0x77); // Try address 0x77
    }

    if (status) {
        Serial.println("✓ BME280 sensor found!");
        sensorAvailable = true;

        // Configure sensor for indoor monitoring
        bme.setSampling(Adafruit_BME280::MODE_FORCED,
                       Adafruit_BME280::SAMPLING_X1, // temperature
                       Adafruit_BME280::SAMPLING_X1, // pressure
                       Adafruit_BME280::SAMPLING_X1, // humidity
                       Adafruit_BME280::FILTER_OFF);
    } else {
        Serial.println("⚠ BME280 sensor not found");
        Serial.println("  Check wiring: SDA=GPIO21, SCL=GPIO22");
        Serial.println("  Device will continue without sensor");
        sensorAvailable = false;
    }
}

/**
 * Read sensor values
 */
bool readSensor(float &temp, float &humidity, float &pressure) {
    if (!sensorAvailable) {
        return false;
    }

    // Trigger measurement
    bme.takeForcedMeasurement();

    temp = bme.readTemperature();
    humidity = bme.readHumidity();
    pressure = bme.readPressure() / 100.0F; // Convert Pa to hPa

    // Check for valid readings
    if (isnan(temp) || isnan(humidity) || isnan(pressure)) {
        return false;
    }

    return true;
}

/**
 * Send readings to server via HTTPS POST
 */
bool sendReadings(float temp, float humidity, float pressure) {
    if (strlen(config.serverUrl) == 0) {
        Serial.println("❌ Server URL not configured");
        return false;
    }

    String url = String(config.serverUrl) + "/api/readings";
    Serial.printf("\nPOST %s\n", url.c_str());

    // Create JSON payload
    StaticJsonDocument<512> doc;
    doc["device_id"] = config.deviceId;
    doc["api_key"] = strlen(config.apiKey) > 0 ? config.apiKey : ""; // Empty if not registered

    JsonArray readings = doc.createNestedArray("readings");

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

        // Pressure
        JsonObject reading3 = readings.createNestedObject();
        reading3["sensor"] = "pressure";
        reading3["value"] = pressure;
        reading3["unit"] = "hPa";
        reading3["timestamp"] = time(nullptr);
    } else {
        // Send heartbeat even without sensor
        JsonObject reading1 = readings.createNestedObject();
        reading1["sensor"] = "heartbeat";
        reading1["value"] = 1;
        reading1["unit"] = "status";
        reading1["timestamp"] = time(nullptr);
    }

    String payload;
    serializeJson(doc, payload);

    // Send HTTP POST
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(10000); // 10 second timeout

    int httpCode = http.POST(payload);
    String response = http.getString();

    Serial.printf("Response code: %d\n", httpCode);
    Serial.printf("Response: %s\n", response.c_str());

    bool success = false;

    if (httpCode == 200) {
        Serial.println("✓ Data sent successfully");

        // Parse response to get server time and update interval
        StaticJsonDocument<256> responseDoc;
        DeserializationError error = deserializeJson(responseDoc, response);

        if (!error) {
            if (responseDoc.containsKey("api_key")) {
                // New device registration - save API key
                const char* newApiKey = responseDoc["api_key"];
                strncpy(config.apiKey, newApiKey, sizeof(config.apiKey));
                saveConfig();
                Serial.println("✓ Device registered - API key saved");
            }

            if (responseDoc.containsKey("server_time")) {
                // Sync time with server
                time_t serverTime = responseDoc["server_time"];
                struct timeval tv = { .tv_sec = serverTime };
                settimeofday(&tv, NULL);
                Serial.printf("✓ Time synced: %s", ctime(&serverTime));
            }

            if (responseDoc.containsKey("reading_interval")) {
                int newInterval = responseDoc["reading_interval"];
                if (newInterval != config.readingInterval) {
                    config.readingInterval = newInterval * 1000; // Convert to ms
                    saveConfig();
                    Serial.printf("✓ Reading interval updated: %d seconds\n", newInterval);
                }
            }
        }

        success = true;
    } else if (httpCode == 401) {
        Serial.println("❌ Invalid API key - device may need re-registration");
    } else if (httpCode == 429) {
        Serial.println("⚠ Rate limited - backing off");
        delay(60000); // Wait 1 minute
    } else {
        Serial.printf("❌ HTTP error: %d\n", httpCode);
    }

    http.end();
    return success;
}

/**
 * Check for and perform OTA firmware updates
 */
void checkForOTAUpdate() {
    if (strlen(config.serverUrl) == 0 || strlen(config.deviceId) == 0) {
        return;
    }

    String url = String(config.serverUrl) + "/api/ota/check?device_id=" +
                 String(config.deviceId) + "&version=" + String(FIRMWARE_VERSION);

    Serial.printf("\n🔍 Checking for OTA updates...\n");
    Serial.printf("Current version: %s\n", FIRMWARE_VERSION);
    Serial.printf("URL: %s\n", url.c_str());

    http.begin(url);
    int httpCode = http.GET();

    if (httpCode != 200) {
        Serial.printf("❌ Failed to check for updates: HTTP %d\n", httpCode);
        http.end();
        return;
    }

    String response = http.getString();
    http.end();

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);

    if (error) {
        Serial.printf("❌ Failed to parse OTA response: %s\n", error.c_str());
        return;
    }

    bool updateAvailable = doc["update_available"] | false;

    if (!updateAvailable) {
        Serial.println("✓ Firmware is up to date");
        return;
    }

    // Update available!
    const char* newVersion = doc["version"];
    const char* downloadUrl = doc["url"];
    int fileSize = doc["size"] | 0;
    const char* checksum = doc["checksum"];

    Serial.println("\n🔄 ================================");
    Serial.println("     OTA UPDATE AVAILABLE");
    Serial.println("   ================================");
    Serial.printf("   Current:  %s\n", FIRMWARE_VERSION);
    Serial.printf("   New:      %s\n", newVersion);
    Serial.printf("   Size:     %d bytes\n", fileSize);
    Serial.println("   ================================\n");

    // Construct full download URL
    String firmwareUrl = String(config.serverUrl) + String(downloadUrl);
    Serial.printf("Downloading from: %s\n", firmwareUrl.c_str());

    // Disable watchdog during update
    esp_task_wdt_delete(NULL);

    // LED pattern: Rapid blinking during update
    for (int i = 0; i < 5; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        delay(100);
    }

    // Configure HTTP Update
    httpUpdate.setLedPin(LED_PIN, LOW); // LED on during download
    httpUpdate.rebootOnUpdate(false);   // We'll reboot manually after verification

    // Register update callbacks
    httpUpdate.onStart([]() {
        Serial.println("\n📥 Starting OTA update...");
        Serial.println("⚠ DO NOT power off device!");
    });

    httpUpdate.onEnd([]() {
        Serial.println("\n✓ Download complete");
    });

    httpUpdate.onProgress([](int current, int total) {
        static int lastPercent = -1;
        int percent = (current * 100) / total;
        if (percent != lastPercent && percent % 10 == 0) {
            Serial.printf("📊 Progress: %d%% (%d / %d bytes)\n", percent, current, total);
            lastPercent = percent;
        }
    });

    httpUpdate.onError([](int err) {
        Serial.printf("\n❌ Update failed: Error %d\n", err);
        switch(err) {
            case HTTP_UPDATE_FAILED_ERROR:
                Serial.println("   HTTP update failed");
                break;
            case HTTP_UPDATE_FAILED_SERVER_ERROR:
                Serial.println("   Server error");
                break;
            case HTTP_UPDATE_FAILED_NO_UPDATE:
                Serial.println("   No update available");
                break;
            case HTTP_UPDATE_FAILED_NOT_ENOUGH_SPACE:
                Serial.println("   Not enough space for update");
                break;
            default:
                Serial.println("   Unknown error");
        }
    });

    // Perform update
    Serial.println("\n🚀 Starting firmware download and installation...\n");

    WiFiClient client;
    t_httpUpdate_return ret = httpUpdate.update(client, firmwareUrl);

    switch (ret) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("❌ Update FAILED: %s\n", httpUpdate.getLastErrorString().c_str());
            Serial.println("⚠ Staying on current firmware version");
            // Re-enable watchdog
            esp_task_wdt_add(NULL);
            break;

        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("ℹ No update needed (already up to date)");
            esp_task_wdt_add(NULL);
            break;

        case HTTP_UPDATE_OK:
            Serial.println("\n✅ ================================");
            Serial.println("     UPDATE SUCCESSFUL!");
            Serial.println("   ================================");
            Serial.printf("   Updated to version: %s\n", newVersion);
            Serial.println("   ================================\n");
            Serial.println("🔄 Rebooting in 3 seconds...\n");

            // Verify the update
            const esp_partition_t* update_partition = esp_ota_get_next_update_partition(NULL);
            if (update_partition != NULL) {
                Serial.printf("✓ Update partition verified: %s\n", update_partition->label);
            }

            // Success LED pattern: 3 long blinks
            for (int i = 0; i < 3; i++) {
                digitalWrite(LED_PIN, HIGH);
                delay(500);
                digitalWrite(LED_PIN, LOW);
                delay(500);
            }

            delay(3000);

            // Reboot to new firmware
            Serial.println("Rebooting NOW...");
            Serial.flush();
            ESP.restart();
            break;
    }
}

/**
 * Blink LED pattern
 */
void blinkLED(int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(delayMs);
        digitalWrite(LED_PIN, LOW);
        delay(delayMs);
    }
}

/**
 * Get unique device ID based on MAC address
 */
String getDeviceId() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char deviceId[32];
    snprintf(deviceId, sizeof(deviceId), "esp32-%02x%02x%02x",
             mac[3], mac[4], mac[5]);
    return String(deviceId);
}
