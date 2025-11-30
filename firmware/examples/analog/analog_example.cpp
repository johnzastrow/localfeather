/**
 * Local Feather - Analog Sensor Examples
 *
 * This example shows how to read analog sensors using ESP32's ADC.
 *
 * Examples included:
 * 1. Soil moisture sensor
 * 2. Light sensor (LDR)
 * 3. Generic voltage sensor
 * 4. Potentiometer (for testing)
 *
 * Hardware:
 * - ESP32 board
 * - Analog sensor(s)
 *
 * ESP32 ADC Specs:
 * - Resolution: 12-bit (0-4095)
 * - Input voltage: 0V to 3.3V (MAX!)
 * - ADC1: GPIOs 32-39 (recommended - WiFi compatible)
 * - ADC2: GPIOs 0,2,4,12-15,25-27 (NOT usable with WiFi!)
 *
 * ⚠️ IMPORTANT: Never exceed 3.3V on ADC pins! Use voltage divider if needed.
 */

// Pin definitions - Use ADC1 pins (GPIO 32-39) for WiFi compatibility
#define SOIL_MOISTURE_PIN 34   // Soil moisture sensor
#define LIGHT_SENSOR_PIN 35    // LDR (Light Dependent Resistor)
#define VOLTAGE_SENSOR_PIN 36  // Generic voltage input
#define POTENTIOMETER_PIN 39   // For testing/calibration

// Calibration values (adjust for your sensors)
#define SOIL_DRY_VALUE 3100    // ADC value in dry soil
#define SOIL_WET_VALUE 1400    // ADC value in wet soil

/**
 * Setup analog sensors
 * Replace setupSensor() in main.cpp with this
 */
void setupSensor() {
    Serial.println("Initializing analog sensors...");

    // Configure ADC resolution (9-12 bits)
    analogReadResolution(12); // 12-bit = 0-4095

    // Configure ADC attenuation (affects voltage range)
    // ADC_0db: 0-1.1V
    // ADC_2_5db: 0-1.5V
    // ADC_6db: 0-2.2V
    // ADC_11db: 0-3.3V (default, most common)
    analogSetAttenuation(ADC_11db);

    // Test readings
    int soilRaw = analogRead(SOIL_MOISTURE_PIN);
    int lightRaw = analogRead(LIGHT_SENSOR_PIN);

    Serial.printf("✓ Soil moisture raw: %d\n", soilRaw);
    Serial.printf("✓ Light sensor raw: %d\n", lightRaw);

    sensorAvailable = true;
}

/**
 * Read analog sensor values
 * Replace readSensor() in main.cpp with this
 */
bool readSensor(float &temp, float &humidity, float &pressure) {
    if (!sensorAvailable) {
        return false;
    }

    // Read raw ADC values
    int soilRaw = analogRead(SOIL_MOISTURE_PIN);
    int lightRaw = analogRead(LIGHT_SENSOR_PIN);
    int voltageRaw = analogRead(VOLTAGE_SENSOR_PIN);

    // Convert to meaningful values
    float soilMoisture = mapSoilMoisture(soilRaw);
    float lightLevel = mapLightLevel(lightRaw);
    float voltage = mapVoltage(voltageRaw);

    // Use the function parameters to return values
    temp = soilMoisture;   // Repurpose as soil moisture %
    humidity = lightLevel; // Repurpose as light level
    pressure = voltage;    // Repurpose as voltage

    return true;
}

/**
 * Convert soil moisture sensor reading to percentage
 */
float mapSoilMoisture(int rawValue) {
    // Map ADC value to 0-100% moisture
    // Lower ADC = more moisture (sensor resistance decreases)
    if (rawValue >= SOIL_DRY_VALUE) return 0.0;
    if (rawValue <= SOIL_WET_VALUE) return 100.0;

    float moisture = map(rawValue, SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100);
    return constrain(moisture, 0, 100);
}

/**
 * Convert light sensor (LDR) reading to lux (approximate)
 */
float mapLightLevel(int rawValue) {
    // Simple mapping - calibrate for your specific LDR
    // Dark: ~3800-4095
    // Room light: ~2000-3000
    // Bright: ~0-1000

    // Map to 0-1000 lux (approximate)
    float lux = map(rawValue, 4095, 0, 0, 1000);
    return constrain(lux, 0, 1000);
}

/**
 * Convert ADC reading to voltage
 */
float mapVoltage(int rawValue) {
    // ADC_11db: 0-3.3V range
    // 12-bit: 0-4095 steps
    float voltage = (rawValue / 4095.0) * 3.3;
    return voltage;
}

/**
 * Send analog readings to server
 * Modify sendReadings() to use correct sensor names
 */
bool sendReadings(float soilMoisture, float lightLevel, float voltage) {
    // ... existing code up to creating readings array ...

    if (sensorAvailable) {
        // Soil Moisture
        JsonObject reading1 = readings.createNestedObject();
        reading1["sensor"] = "soil_moisture";
        reading1["value"] = soilMoisture;
        reading1["unit"] = "%";
        reading1["timestamp"] = time(nullptr);

        // Light Level
        JsonObject reading2 = readings.createNestedObject();
        reading2["sensor"] = "light_level";
        reading2["value"] = lightLevel;
        reading2["unit"] = "lux";
        reading2["timestamp"] = time(nullptr);

        // Voltage (if using voltage sensor)
        JsonObject reading3 = readings.createNestedObject();
        reading3["sensor"] = "voltage";
        reading3["value"] = voltage;
        reading3["unit"] = "V";
        reading3["timestamp"] = time(nullptr);
    }

    // ... rest of existing code ...
}

/**
 * EXAMPLE: Soil Moisture Sensor
 *
 * Wiring:
 * Sensor VCC → 3.3V
 * Sensor GND → GND
 * Sensor AOUT → GPIO 34
 *
 * Calibration:
 * 1. Insert sensor in dry soil/air
 * 2. Note ADC value → set SOIL_DRY_VALUE
 * 3. Insert sensor in wet soil/water
 * 4. Note ADC value → set SOIL_WET_VALUE
 */

/**
 * EXAMPLE: LDR (Light Dependent Resistor)
 *
 * Wiring (voltage divider):
 * 3.3V → LDR → GPIO 35 → 10K resistor → GND
 *
 * How it works:
 * - Bright light → LDR resistance low → ADC reads low value
 * - Dark → LDR resistance high → ADC reads high value
 *
 * Use 10K resistor for general purpose light sensing.
 */

/**
 * EXAMPLE: Voltage Divider for >3.3V Inputs
 *
 * To measure 0-5V or 0-12V, use voltage divider:
 *
 * For 0-5V input:
 * INPUT_VOLTAGE → 10K resistor → GPIO 36 → 6.8K resistor → GND
 * This divides 5V to ~2V (safe for ESP32)
 *
 * Reading formula:
 * actualVoltage = (adcVoltage / R2) * (R1 + R2)
 * Where R1=10K, R2=6.8K
 */

float readDividedVoltage(int pin, float R1, float R2) {
    int raw = analogRead(pin);
    float adcVoltage = (raw / 4095.0) * 3.3;
    float actualVoltage = adcVoltage * ((R1 + R2) / R2);
    return actualVoltage;
}

/**
 * ADVANCED: Averaging for Stable Readings
 */
float readAnalogAveraged(int pin, int samples = 10) {
    long sum = 0;
    for (int i = 0; i < samples; i++) {
        sum += analogRead(pin);
        delay(10); // Small delay between readings
    }
    return sum / (float)samples;
}

/**
 * ADVANCED: Calibration Helper
 *
 * Run this once to find your sensor's min/max values
 */
void calibrateAnalogSensor(int pin, unsigned long duration = 30000) {
    Serial.printf("Calibrating sensor on GPIO %d for %d seconds...\n", pin, duration / 1000);
    Serial.println("Move sensor through full range (min to max)");

    int minValue = 4095;
    int maxValue = 0;
    unsigned long startTime = millis();

    while (millis() - startTime < duration) {
        int value = analogRead(pin);

        if (value < minValue) minValue = value;
        if (value > maxValue) maxValue = value;

        Serial.printf("Current: %d | Min: %d | Max: %d\r", value, minValue, maxValue);
        delay(100);
    }

    Serial.printf("\n\n✓ Calibration complete!\n");
    Serial.printf("  Minimum value: %d\n", minValue);
    Serial.printf("  Maximum value: %d\n", maxValue);
    Serial.println("\nUpdate your code with these values.");
}

/**
 * Notes:
 *
 * ADC Accuracy:
 * - ESP32 ADC is non-linear, especially at extremes
 * - For precision: Use external ADC (ADS1115) or voltage reference
 * - For general sensing: Built-in ADC is fine
 *
 * WiFi Impact:
 * - WiFi causes ADC noise
 * - Use averaging to smooth readings
 * - ADC1 pins (32-39) are less affected than ADC2
 *
 * Pin Selection:
 * ✅ Use: GPIO 32, 33, 34, 35, 36, 39 (ADC1, WiFi safe)
 * ❌ Avoid: GPIO 0, 2, 4, 12-15, 25-27 (ADC2, conflicts with WiFi)
 *
 * Sampling Rate:
 * - Don't read ADC in tight loop
 * - Add delays between readings
 * - Use averaging for stability
 *
 * Common Sensors:
 * - Soil moisture: Capacitive (better) or resistive (cheaper)
 * - LDR: Light level (simple, cheap)
 * - Thermistor: Temperature (analog alternative to digital sensors)
 * - Hall effect: Magnetic field
 * - Potentiometer: User input, calibration
 * - Photoresistor: Light intensity
 * - Flex sensor: Bend detection
 *
 * Troubleshooting:
 * 1. Reading always 4095 → Pin floating, add pulldown resistor
 * 2. Reading always 0 → Short to GND or voltage too low
 * 3. Noisy readings → Add 0.1µF capacitor across sensor
 * 4. Unstable → Use averaging, increase delay between reads
 */
