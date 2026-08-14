# IoT Bin Monitoring - Quick Reference Card

## Quick Start (5 minutes)

### 1. Register a Sensor
```bash
curl -X POST http://localhost:5000/api/iot/sensors \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "binId": "65a1b2c3...",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-01",
    "calibrationData": {"minDistance": 5, "maxDistance": 100}
  }'
```

### 2. Send Sensor Data (from ESP32)
```bash
curl -X POST http://localhost:5000/api/iot/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "binId": "65a1b2c3...",
    "sensorId": "65a1b2c4...",
    "distance": 45.5,
    "batteryLevel": 87,
    "timestamp": "2025-08-13T10:30:00Z"
  }'
```

### 3. Check Bin Status
```bash
curl -X GET http://localhost:5000/api/bins/65a1b2c3... \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. View Sensor History
```bash
curl -X GET "http://localhost:5000/api/iot/bins/65a1b2c3.../sensor-history?limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Arduino/ESP32 Quick Start

### 1. Install Libraries (Arduino IDE)
- File → Preferences → Add URL:
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- Tools → Board Manager → Install "esp32"
- Sketch → Include Library → Manage Libraries:
  - Install "ArduinoJson"

### 2. Pin Configuration
```cpp
const int TRIG_PIN = 26;    // ESP32 GPIO 26
const int ECHO_PIN = 25;    // ESP32 GPIO 25
const int BATTERY_PIN = 35; // ADC input
```

### 3. Wiring (HC-SR04 to ESP32)
```
VCC    → 5V
GND    → GND
TRIG   → GPIO 26
ECHO   → GPIO 25
```

### 4. Configure Credentials
```cpp
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://192.168.1.100:5000/api/iot/sensor-data";
const char* BIN_ID = "65a1b2c3...";
const char* SENSOR_ID = "65a1b2c4...";
```

---

## API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/iot/sensor-data` | ❌ | Receive sensor data |
| POST | `/api/iot/sensors` | ✅ Admin | Register sensor |
| GET | `/api/iot/sensors/:id` | ✅ Admin | Get sensor config |
| PATCH | `/api/iot/sensors/:id` | ✅ Admin | Update sensor |
| GET | `/api/iot/bins/:id/sensor-history` | ✅ User | View history |

---

## Status Mapping

| Fill Level | Status | Action |
|------------|--------|--------|
| 0-79% | `normal` | No action |
| 80-89% | `full` | Schedule collection |
| 90-99% | `overflow` | Urgent |
| 100%+ | `overflow` | Critical |

---

## Database Collections

### `sensors`
Stores IoT device configurations
```javascript
{
  _id: ObjectId,
  binId: ObjectId,
  sensorType: "ultrasonic",
  deviceId: "esp32-01",
  status: "active",
  calibrationData: { minDistance: 5, maxDistance: 100 },
  lastHeartbeat: Date,
  batteryLevel: 87,
  createdAt: Date,
  updatedAt: Date
}
```

### `iot_readings`
Time-series sensor data
```javascript
{
  _id: ObjectId,
  binId: ObjectId,
  sensorId: ObjectId,
  fillLevel: 55.3,
  timestamp: Date,
  sensorStatus: "ok",
  batteryLevel: 87,
  rawDistance: 45.5,
  recordedAt: Date
}
```

### `bins` (Updated)
Now includes real-time sensor data
```javascript
{
  _id: ObjectId,
  fillLevel: 55.3,      // Updated from sensors
  status: "normal",     // Auto-calculated
  lastEmptied: Date,
  updatedAt: Date,
  // ... other fields
}
```

---

## Sensor Handler Interface

```python
from app.utils.sensor_handler import create_sensor_handler

# Create handler based on sensor type
handler = create_sensor_handler(sensor_config)

# Process raw data
result = handler.process_reading({
    "distance": 45.5,
    "batteryLevel": 87,
    "timestamp": "2025-08-13T10:30:00Z"
})

# Returns normalized data
{
    "fillLevel": 55.3,
    "sensorStatus": "ok",
    "batteryLevel": 87,
    "rawDistance": 45.5,
    "timestamp": <datetime>,
    "sensorType": "ultrasonic"
}
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "Bin not found" | Invalid binId | Use correct MongoDB ObjectId |
| "Sensor not found" | Sensor not registered | Create sensor via POST /api/iot/sensors |
| "Sensor timeout" | ESP32 connection issue | Check WiFi, USB cable, pin wiring |
| "Low battery" | Battery < threshold | Replace/charge battery or disable monitoring |
| CORS error | Wrong frontend URL | Update CORS settings in app |

---

## Environment Setup

```env
# Database
MONGO_URI=mongodb://localhost:27017/smartwaste_db
DB_NAME=smartwaste_db

# IoT Configuration
IOT_ULTRASONIC_MIN_DISTANCE=5
IOT_ULTRASONIC_MAX_DISTANCE=100
IOT_DEFAULT_UPDATE_INTERVAL=300
IOT_LOW_BATTERY_THRESHOLD=20
IOT_HEARTBEAT_TIMEOUT=1200

# Server
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret

# Frontend
FRONTEND_URL=http://localhost:5173
```

---

## Testing

### Run Python Syntax Check
```bash
python -m py_compile app/models/iot_model.py
python -m py_compile app/utils/sensor_handler.py
python -m py_compile app/controllers/iot_controller.py
```

### Test App Import
```bash
python -c "from app import create_app; print('✓ OK')"
```

### Test API (cURL)
```bash
# Health check
curl http://localhost:5000/api/health

# Send test data
curl -X POST http://localhost:5000/api/iot/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"binId": "test", "sensorId": "test", "fillLevel": 50, ...}'
```

---

## File Locations

| File | Purpose |
|------|---------|
| `app/models/iot_model.py` | Data schemas & status mapping |
| `app/utils/sensor_handler.py` | Sensor abstraction layer |
| `app/controllers/iot_controller.py` | API logic |
| `app/routes/iot_routes.py` | Route definitions |
| `IOT_API_REFERENCE.md` | API documentation |
| `IOT_INTEGRATION_GUIDE.md` | ESP32 setup & code |
| `PHASE1_IMPLEMENTATION.md` | Implementation summary |

---

## Key Classes & Functions

### SensorHandler (Abstract)
```python
class SensorHandler(ABC):
    def process_reading(self, raw_data) -> dict
    def validate_data(self, raw_data) -> tuple[bool, str]
```

### UltrasonicSensorHandler
```python
handler = UltrasonicSensorHandler(sensor_config)
result = handler.process_reading({"distance": 45.5})
```

### Status Mapping
```python
from app.models.iot_model import get_fill_level_status
status = get_fill_level_status(fill_level=55.3)  # "normal"
```

---

## Performance Tips

1. **Reduce Update Frequency**: Increase `updateInterval` in sensor config
2. **Batch Requests**: Send multiple readings in one request (future enhancement)
3. **Enable Compression**: Use gzip for large payloads
4. **Add Indexing**: MongoDB indexes auto-created on startup
5. **Archive Old Data**: Implement retention policy for iot_readings

---

## Security Considerations

- ⚠️ No authentication on `/api/iot/sensor-data` (intentional for IoT)
- ⚠️ Consider API key in production (code ready, not enabled)
- ⚠️ Use HTTPS for production deployment
- ✅ Admin endpoints require JWT + admin role
- ✅ All inputs validated before processing

---

## Monitoring Checklist

- [ ] Sensor heartbeat (last update within IOT_HEARTBEAT_TIMEOUT)
- [ ] Battery level (alert if < IOT_LOW_BATTERY_THRESHOLD)
- [ ] Fill level trends (sudden changes indicate sensor error)
- [ ] API response times (should be < 500ms)
- [ ] MongoDB connection pool (prevent connection exhaustion)
- [ ] Disk space (iot_readings can grow large)

---

## Resources

📖 Full Documentation:
- [IOT_API_REFERENCE.md](IOT_API_REFERENCE.md) - Complete API specs
- [IOT_INTEGRATION_GUIDE.md](IOT_INTEGRATION_GUIDE.md) - Hardware & ESP32 setup
- [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) - Architecture & testing

🔗 External:
- ESP32 Docs: https://docs.espressif.com/
- Arduino JSON: https://arduinojson.org/
- MongoDB: https://docs.mongodb.com/
- Flask: https://flask.palletsprojects.com/

---

**Last Updated**: 2025-08-13
**Version**: 1.0
**Status**: Ready for Development
