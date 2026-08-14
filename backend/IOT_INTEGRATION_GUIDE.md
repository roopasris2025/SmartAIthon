# IoT Bin Monitoring - ESP32 Integration Guide

## Overview

This guide explains how to set up an ESP32 microcontroller with an ultrasonic distance sensor to monitor smart waste bins and send data to the Smart Waste Management System.

## Architecture

```
┌─────────────────────┐
│  ESP32 + Sensor     │
│  (Ultrasonic HC-SR04│
│   or compatible)    │
└──────────┬──────────┘
           │ WiFi/HTTP
           ▼
┌──────────────────────────────┐
│  Smart Waste API             │
│  POST /api/iot/sensor-data   │
└──────────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  MongoDB IoT Readings        │
│  iot_readings collection     │
└──────────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Bin Status Updated          │
│  bins collection             │
└──────────────────────────────┘
```

## Hardware Requirements

### Minimum Configuration
- **Microcontroller**: ESP32 (or ESP8266 for basic setup)
- **Distance Sensor**: HC-SR04 Ultrasonic Sensor (or compatible)
- **Power Supply**: 5V / 2A (USB or 18650 battery with charging module)
- **Enclosure**: Waterproof case for outdoor deployment
- **WiFi**: Available WiFi network with 2.4 GHz band

### Recommended Configuration
- **Microcontroller**: ESP32 WROOM-32 (good WiFi range)
- **Distance Sensor**: JSN-SR04T (waterproof variant)
- **Power**: Solar panel (5V) + Li-Ion battery + TP4056 charging module
- **Connectivity**: 4G LTE module (SIM7070) for remote locations
- **Enclosure**: IP67 or IP68 rated enclosure

## Pin Mapping (ESP32)

For HC-SR04 Ultrasonic Sensor:

```
HC-SR04 Pin    ━━━    ESP32 Pin    Description
─────────────────────────────────────────────────
GND            ━━━    GND          Ground
VCC (5V)       ━━━    5V/VUSB      Power (5V)
TRIG           ━━━    GPIO 26      Trigger signal (send pulse)
ECHO           ━━━    GPIO 25      Echo signal (measure pulse duration)
```

For optional battery monitoring (on ESP32):
- Battery voltage divider connected to **GPIO 35** (ADC1_7)
  - High voltage (4.2V max) through 2x 10kΩ resistor divider

## Arduino Code (ESP32)

Save this as `smart_bin_sensor.ino`:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ──── WiFi Configuration ────────────────────────────────────────────────
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ──── API Configuration ────────────────────────────────────────────────
const char* serverUrl = "http://your-server-ip:5000/api/iot/sensor-data";
// For production, use https and valid SSL certificates

// ──── Sensor Configuration ────────────────────────────────────────────
const int TRIG_PIN = 26;          // GPIO pin connected to HC-SR04 TRIG
const int ECHO_PIN = 25;          // GPIO pin connected to HC-SR04 ECHO
const int BATTERY_PIN = 35;       // GPIO pin for battery voltage (optional)

// ──── Device Configuration ────────────────────────────────────────────
const char* BIN_ID = "YOUR_BIN_MONGODB_ID";           // From admin dashboard
const char* SENSOR_ID = "YOUR_SENSOR_MONGODB_ID";     // From sensor registration
const int UPDATE_INTERVAL = 300;  // 5 minutes (in seconds)

// ──── Calibration ────────────────────────────────────────────────────
const float MIN_DISTANCE = 5.0;   // Distance when bin is EMPTY (cm)
const float MAX_DISTANCE = 100.0; // Distance when bin is FULL (cm)

// ──── Global Variables ───────────────────────────────────────────────
unsigned long lastUpdate = 0;
int readingCount = 0;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\nStarting Smart Bin Sensor v1.0");
    
    // Initialize sensor pins
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    
    // Connect to WiFi
    connectToWiFi();
}

void loop() {
    unsigned long currentTime = millis();
    
    // Check if it's time to send data
    if (currentTime - lastUpdate >= UPDATE_INTERVAL * 1000) {
        sendSensorData();
        lastUpdate = currentTime;
    }
    
    delay(1000); // Check every second
}

// ──── WiFi Connection ───────────────────────────────────────────────────
void connectToWiFi() {
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nFailed to connect to WiFi. Retrying...");
        delay(5000);
        connectToWiFi();
    }
}

// ──── Measure Distance ────────────────────────────────────────────────────
float measureDistance() {
    // Send trigger pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    // Measure echo pulse duration
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    
    if (duration == 0) {
        Serial.println("ERROR: Sensor timeout - no echo received");
        return -1; // Error code
    }
    
    // Convert duration to distance (in cm)
    // Speed of sound = 343 m/s = 0.0343 cm/μs
    // Distance = (duration / 2) * 0.0343
    float distance = duration / 58.0;  // Simplified formula
    
    return distance;
}

// ──── Calculate Fill Level ────────────────────────────────────────────────
float calculateFillLevel(float distance) {
    if (distance < 0) {
        return -1; // Invalid reading
    }
    
    if (distance <= MIN_DISTANCE) {
        return 100.0; // Bin is full
    }
    
    if (distance >= MAX_DISTANCE) {
        return 0.0; // Bin is empty
    }
    
    // Linear interpolation
    float fillLevel = ((MAX_DISTANCE - distance) / (MAX_DISTANCE - MIN_DISTANCE)) * 100.0;
    
    // Clamp to 0-100
    if (fillLevel < 0) fillLevel = 0;
    if (fillLevel > 100) fillLevel = 100;
    
    return fillLevel;
}

// ──── Read Battery Level (Optional) ──────────────────────────────────────
float readBatteryLevel() {
    // Optional: implement if using battery monitoring
    // This example reads from ADC1_7 (GPIO 35)
    // Formula: voltage = (analogRead / 4095) * 3.3V
    // Then adjust for voltage divider: actual_voltage = voltage * 2
    // Battery %: (voltage - 3.0) / 1.2 * 100  (for Li-Ion 3.0V~4.2V)
    
    int adcValue = analogRead(BATTERY_PIN);
    float voltage = (adcValue / 4095.0) * 3.3 * 2.0;  // Adjust for divider
    
    // Map 3.0V-4.2V to 0-100%
    float batteryPct = ((voltage - 3.0) / 1.2) * 100.0;
    
    if (batteryPct < 0) batteryPct = 0;
    if (batteryPct > 100) batteryPct = 100;
    
    return batteryPct;
}

// ──── Send Sensor Data to Server ────────────────────────────────────────
void sendSensorData() {
    readingCount++;
    Serial.print("\nReading #");
    Serial.print(readingCount);
    Serial.println(" ─ Measuring distance...");
    
    // Measure distance (take average of 3 readings)
    float distances[3];
    float validReadings = 0;
    
    for (int i = 0; i < 3; i++) {
        distances[i] = measureDistance();
        Serial.print("  Attempt ");
        Serial.print(i + 1);
        Serial.print(": ");
        Serial.print(distances[i]);
        Serial.println(" cm");
        
        if (distances[i] > 0) {
            validReadings++;
        }
        delay(100); // Small delay between readings
    }
    
    if (validReadings == 0) {
        Serial.println("ERROR: All sensor readings failed!");
        return;
    }
    
    // Calculate average distance
    float avgDistance = 0;
    int count = 0;
    for (int i = 0; i < 3; i++) {
        if (distances[i] > 0) {
            avgDistance += distances[i];
            count++;
        }
    }
    avgDistance /= count;
    
    // Calculate fill level
    float fillLevel = calculateFillLevel(avgDistance);
    float batteryLevel = readBatteryLevel();
    
    Serial.print("Average distance: ");
    Serial.print(avgDistance);
    Serial.println(" cm");
    Serial.print("Fill level: ");
    Serial.print(fillLevel);
    Serial.println("%");
    Serial.print("Battery: ");
    Serial.print(batteryLevel);
    Serial.println("%");
    
    // Prepare JSON payload
    StaticJsonDocument<500> doc;
    doc["binId"] = BIN_ID;
    doc["sensorId"] = SENSOR_ID;
    doc["distance"] = avgDistance;
    doc["batteryLevel"] = batteryLevel;
    doc["timestamp"] = getCurrentISOTime();
    
    String payload;
    serializeJson(doc, payload);
    
    Serial.println("Sending to server...");
    
    // Send HTTP POST request
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");
        
        int httpResponseCode = http.POST(payload);
        
        if (httpResponseCode > 0) {
            Serial.print("Response code: ");
            Serial.println(httpResponseCode);
            
            String response = http.getString();
            Serial.println("Response: " + response);
            
            if (httpResponseCode == 201 || httpResponseCode == 200) {
                Serial.println("✓ Data sent successfully!");
            } else {
                Serial.println("✗ Unexpected response code");
            }
        } else {
            Serial.print("Error: ");
            Serial.println(http.errorToString(httpResponseCode));
        }
        
        http.end();
    } else {
        Serial.println("WiFi disconnected! Reconnecting...");
        connectToWiFi();
    }
}

// ──── Get Current Time in ISO 8601 Format ───────────────────────────────
String getCurrentISOTime() {
    // Simple implementation - for production, sync with NTP server
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    
    char buffer[30];
    strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", timeinfo);
    return String(buffer);
}
```

## Setup Instructions

### 1. Hardware Assembly

1. Connect HC-SR04 sensor to ESP32:
   - VCC → 5V (USB power or separate 5V supply)
   - GND → GND
   - TRIG → GPIO 26
   - ECHO → GPIO 25

2. Connect power:
   - USB cable for development
   - For deployment: battery + solar panel

3. Install in weatherproof enclosure

### 2. Arduino IDE Setup

1. Install ESP32 board support:
   - File → Preferences
   - Add to "Additional Boards Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board Manager → Search "esp32" → Install

2. Install required libraries:
   - Sketch → Include Library → Manage Libraries
   - Search and install:
     - `ArduinoJson` (by Benoit Blanchon)
     - `WiFi` (built-in with ESP32)
     - `HTTPClient` (built-in with ESP32)

3. Configure board:
   - Tools → Board → ESP32 WROOM-32
   - Tools → Port → (select your USB port)

### 3. Configure Code

Edit `smart_bin_sensor.ino`:

```cpp
// Replace with your WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Replace with your server details
const char* serverUrl = "http://192.168.1.100:5000/api/iot/sensor-data";

// Get these from Smart Waste admin dashboard after registering sensor
const char* BIN_ID = "65a1b2c3d4e5f6g7h8i9j0k1";
const char* SENSOR_ID = "65a1b2c3d4e5f6g7h8i9j0k2";
```

### 4. Register Sensor in Admin Dashboard

Before uploading to ESP32:

1. Create a bin (if not already created)
2. Register sensor:
   ```bash
   curl -X POST http://your-server:5000/api/iot/sensors \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
       "sensorType": "ultrasonic",
       "deviceId": "esp32-bin-001",
       "calibrationData": {
         "minDistance": 5,
         "maxDistance": 100
       }
     }'
   ```

3. Copy the returned `sensorId` to your Arduino code

### 5. Calibration

To calibrate your sensor:

1. Place sensor above bin and measure distances:
   - When bin is **empty**: record distance (minDistance)
   - When bin is **full**: record distance (maxDistance)

2. Update calibration in code or admin dashboard:
   ```cpp
   const float MIN_DISTANCE = 5.0;    // measured empty distance
   const float MAX_DISTANCE = 100.0;  // measured full distance
   ```

3. Update via API:
   ```bash
   curl -X PATCH http://your-server:5000/api/iot/sensors/SENSOR_ID \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "calibrationData": {
         "minDistance": 5,
         "maxDistance": 100
       }
     }'
   ```

### 6. Upload and Test

1. Connect ESP32 via USB
2. Arduino IDE → Sketch → Upload
3. Open Serial Monitor (9600 baud) to see debug output
4. Verify readings appear in API response

## API Endpoint Reference

### POST /api/iot/sensor-data

**Description**: Receive raw sensor data from IoT devices

**Endpoint**: `POST /api/iot/sensor-data`

**No authentication required** (can be added later with API keys)

**Request Body** (raw sensor format):
```json
{
  "binId": "MongoDB ObjectId",
  "sensorId": "MongoDB ObjectId",
  "distance": 45.2,
  "batteryLevel": 87,
  "timestamp": "2025-08-13T10:30:00Z"
}
```

Or **normalized format**:
```json
{
  "binId": "MongoDB ObjectId",
  "sensorId": "MongoDB ObjectId",
  "fillLevel": 55.3,
  "timestamp": "2025-08-13T10:30:00Z",
  "sensorStatus": "ok",
  "batteryLevel": 87
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Sensor data processed successfully",
  "data": {
    "reading": {
      "id": "...",
      "binId": "...",
      "fillLevel": 55.3,
      "timestamp": "2025-08-13T10:30:00Z",
      "sensorStatus": "ok"
    },
    "bin": {
      "id": "...",
      "fillLevel": 55.3,
      "status": "normal"
    }
  }
}
```

### POST /api/iot/sensors

**Description**: Register a new sensor (admin only)

**Endpoint**: `POST /api/iot/sensors`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "binId": "MongoDB ObjectId",
  "sensorType": "ultrasonic",
  "deviceId": "esp32-bin-001",
  "calibrationData": {
    "minDistance": 5,
    "maxDistance": 100
  }
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Sensor created successfully",
  "data": {
    "id": "sensor_mongodb_id",
    "binId": "bin_mongodb_id",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-bin-001",
    "status": "active",
    "calibrationData": {...}
  }
}
```

## Troubleshooting

### Sensor reads 0 or negative distance
- Check HC-SR04 wiring
- Verify power supply (5V is required)
- Test with multimeter: TRIG should pulse, ECHO should return pulse

### WiFi connection fails
- Verify SSID and password are correct
- Check if 2.4 GHz band is enabled on router
- Reduce distance to router or increase transmit power

### API returns 404
- Verify binId and sensorId are correct MongoDB ObjectIds
- Check server URL and port
- Ensure sensor is registered before sending data

### Fill level incorrect
- Recalibrate minDistance and maxDistance
- Ensure sensor is mounted vertically
- Check for obstacles or tilted bin

### High battery drain
- Increase UPDATE_INTERVAL to reduce WiFi transmissions
- Use deep sleep mode between readings
- Add power management code

## Data Retention & Analytics

Sensor readings are stored in MongoDB `iot_readings` collection and can be queried for:
- Historical fill level trends
- Collection schedule optimization
- Sensor health monitoring
- Predictive maintenance

Query historical data:
```bash
GET /api/iot/bins/BIN_ID/sensor-history?limit=100&offset=0
```

## Production Deployment Checklist

- [ ] Configure HTTPS with valid SSL certificate
- [ ] Add API key authentication to `/api/iot/sensor-data`
- [ ] Test WiFi range and signal strength
- [ ] Implement battery-backed power supply
- [ ] Set up regular firmware updates mechanism
- [ ] Add sensor malfunction alerts
- [ ] Implement data aggregation for analytics
- [ ] Test overflow scenarios
- [ ] Configure collection route optimization
- [ ] Add GPS tracking for collection vehicles

## Future Enhancements

- [ ] LTE/4G connectivity for remote areas
- [ ] LoRaWAN long-range communication
- [ ] Temperature/humidity sensors
- [ ] Odor detection sensors
- [ ] Illegal dumping detection (motion + fill level)
- [ ] QR code for quick status check
- [ ] Over-the-air (OTA) firmware updates
- [ ] Multi-sensor per bin (redundancy)
