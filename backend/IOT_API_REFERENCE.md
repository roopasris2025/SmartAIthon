# Smart Waste IoT API Documentation

## Base URL
```
http://your-server:5000/api/iot
```

## Authentication

### Public Endpoints (No Authentication Required)
- `POST /iot/sensor-data` - For IoT devices to send readings
  
### Protected Endpoints (JWT Required)
- `POST /iot/sensors` - Admin only
- `GET /iot/sensors/:id` - Admin only
- `PATCH /iot/sensors/:id` - Admin only
- `GET /iot/bins/:id/sensor-history` - Authenticated users

**Authorization Header**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Endpoints

### 1. POST /iot/sensor-data

**Purpose**: Receive sensor data from IoT devices and update bin fill level

**No Authentication Required**

**Request Body** (Option A: Raw Sensor Data):
```json
{
  "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
  "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
  "distance": 45.5,
  "batteryLevel": 87,
  "timestamp": "2025-08-13T10:30:45Z"
}
```

**Request Body** (Option B: Normalized Data):
```json
{
  "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
  "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
  "fillLevel": 55.3,
  "timestamp": "2025-08-13T10:30:45Z",
  "sensorStatus": "ok",
  "batteryLevel": 87,
  "rawDistance": 45.5
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Sensor data processed successfully",
  "data": {
    "reading": {
      "id": "65a1b2c3d4e5f6g7h8i9j0k3",
      "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
      "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
      "fillLevel": 55.3,
      "timestamp": "2025-08-13T10:30:45Z",
      "sensorStatus": "ok",
      "batteryLevel": 87,
      "rawDistance": 45.5,
      "recordedAt": "2025-08-13T10:30:46Z"
    },
    "bin": {
      "id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "fillLevel": 55.3,
      "status": "normal"
    }
  }
}
```

**Error Responses**:
```json
{
  "success": false,
  "message": "Bin not found",
  "errors": null
}
```

**Status Codes**:
- `201` - Data received and bin updated successfully
- `400` - Invalid request (missing fields, invalid ObjectId)
- `404` - Bin or sensor not found
- `422` - Validation error (invalid sensor data)
- `500` - Server error

**Notes**:
- System automatically handles both raw (sensor-specific) and normalized formats
- For ultrasonic sensors: raw format includes `distance` (cm), processed into fillLevel
- System calculates fill level using calibration data (minDistance, maxDistance)
- Sensor status is stored in time-series collection for analytics
- Bin status auto-updates based on fill level thresholds

---

### 2. POST /iot/sensors

**Purpose**: Register a new IoT sensor

**Authentication**: Required (JWT) - Admin role

**Request Body**:
```json
{
  "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
  "sensorType": "ultrasonic",
  "deviceId": "esp32-bin-001",
  "apiKey": "secret-key-here",
  "calibrationData": {
    "minDistance": 5,
    "maxDistance": 100
  },
  "config": {
    "updateInterval": 300,
    "enableBattery": true
  },
  "notes": "Main campus bin A - Building 3"
}
```

**Request Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| binId | string | Yes | MongoDB ObjectId of the bin |
| sensorType | string | Yes | Type: `ultrasonic`, `infrared`, `pressure`, `weight` |
| deviceId | string | No | Unique identifier (MAC, serial number) |
| apiKey | string | No | Secret key for authentication (future use) |
| calibrationData | object | No | Sensor calibration settings |
| calibrationData.minDistance | number | No | Distance when bin is empty (cm) - default: 0 |
| calibrationData.maxDistance | number | No | Distance when bin is full (cm) - default: 100 |
| config | object | No | Sensor configuration |
| config.updateInterval | number | No | Seconds between readings - default: 300 |
| config.enableBattery | boolean | No | Track battery level - default: true |
| notes | string | No | Notes about this sensor |

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Sensor created successfully",
  "data": {
    "id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-bin-001",
    "status": "active",
    "lastHeartbeat": null,
    "batteryLevel": null,
    "sensorStatus": "ok",
    "calibrationData": {
      "minDistance": 5,
      "maxDistance": 100
    },
    "config": {
      "updateInterval": 300,
      "enableBattery": true
    },
    "notes": "Main campus bin A - Building 3",
    "createdAt": "2025-08-13T10:30:00Z",
    "updatedAt": "2025-08-13T10:30:00Z"
  }
}
```

**Error Responses**:
```json
{
  "success": false,
  "message": "Admin access required",
  "errors": null
}
```

**Status Codes**:
- `201` - Sensor registered successfully
- `400` - Invalid sensor type or missing required fields
- `403` - Admin access required
- `404` - Bin not found
- `500` - Server error

---

### 3. GET /iot/sensors/:id

**Purpose**: Get sensor configuration and status

**Authentication**: Required (JWT) - Admin role

**URL Parameters**:
- `id` (string, required) - MongoDB ObjectId of the sensor

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Sensor fetched",
  "data": {
    "id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-bin-001",
    "status": "active",
    "lastHeartbeat": "2025-08-13T10:30:45Z",
    "batteryLevel": 87,
    "sensorStatus": "ok",
    "calibrationData": {
      "minDistance": 5,
      "maxDistance": 100
    },
    "config": {
      "updateInterval": 300,
      "enableBattery": true
    },
    "notes": "Main campus bin A",
    "createdAt": "2025-08-13T10:00:00Z",
    "updatedAt": "2025-08-13T10:30:45Z"
  }
}
```

---

### 4. PATCH /iot/sensors/:id

**Purpose**: Update sensor configuration

**Authentication**: Required (JWT) - Admin role

**URL Parameters**:
- `id` (string, required) - MongoDB ObjectId of the sensor

**Request Body** (all fields optional):
```json
{
  "status": "active",
  "calibrationData": {
    "minDistance": 5,
    "maxDistance": 100
  },
  "config": {
    "updateInterval": 600,
    "enableBattery": true
  },
  "notes": "Updated calibration"
}
```

**Updatable Fields**:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| status | string | `active`, `inactive`, `error`, `calibration` | Sensor operational status |
| calibrationData.minDistance | number | > 0 | Distance when bin is empty |
| calibrationData.maxDistance | number | > minDistance | Distance when bin is full |
| config.updateInterval | number | >= 60 | Seconds between readings |
| config.enableBattery | boolean | true/false | Enable battery monitoring |
| notes | string | any | Free-form notes |

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Sensor updated successfully",
  "data": {
    "id": "65a1b2c3d4e5f6g7h8i9j0k2",
    "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-bin-001",
    "status": "active",
    "lastHeartbeat": "2025-08-13T10:30:45Z",
    "batteryLevel": 87,
    "sensorStatus": "ok",
    "calibrationData": {
      "minDistance": 5,
      "maxDistance": 100
    },
    "config": {
      "updateInterval": 600,
      "enableBattery": true
    },
    "notes": "Updated calibration",
    "createdAt": "2025-08-13T10:00:00Z",
    "updatedAt": "2025-08-13T10:31:00Z"
  }
}
```

---

### 5. GET /iot/bins/:id/sensor-history

**Purpose**: Get historical sensor readings for a bin

**Authentication**: Required (JWT)

**URL Parameters**:
- `id` (string, required) - MongoDB ObjectId of the bin

**Query Parameters**:
- `limit` (number, optional) - Max readings to return (default: 100, max: 500)
- `offset` (number, optional) - Pagination offset (default: 0)

**Example Request**:
```
GET /iot/bins/65a1b2c3d4e5f6g7h8i9j0k1/sensor-history?limit=50&offset=0
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Sensor history fetched",
  "data": {
    "readings": [
      {
        "id": "65a1b2c3d4e5f6g7h8i9j0k5",
        "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
        "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
        "fillLevel": 55.3,
        "timestamp": "2025-08-13T10:30:45Z",
        "sensorStatus": "ok",
        "batteryLevel": 87,
        "rawDistance": 45.5,
        "recordedAt": "2025-08-13T10:30:46Z"
      },
      {
        "id": "65a1b2c3d4e5f6g7h8i9j0k6",
        "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
        "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
        "fillLevel": 54.8,
        "timestamp": "2025-08-13T10:25:45Z",
        "sensorStatus": "ok",
        "batteryLevel": 87,
        "rawDistance": 45.7,
        "recordedAt": "2025-08-13T10:25:46Z"
      }
    ],
    "pagination": {
      "total": 1024,
      "limit": 50,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

---

## Status Codes Reference

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 403 | Forbidden | Admin access required |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal server error |

---

## Fill Level Status Mapping

The system automatically determines bin status based on fill level:

| Fill Level Range | Status | Collection Priority |
|------------------|--------|---------------------|
| 0% - 79% | normal | Low - no action needed |
| 80% - 89% | full | Medium - schedule collection |
| 90% - 99% | overflow | High - urgent collection |
| 100%+ | overflow | Critical - immediate collection |

---

## Data Retention

- **Sensor readings**: Stored indefinitely in `iot_readings` collection
- **Sensor configuration**: Stored in `sensors` collection
- **Bin data**: Updated in real-time in `bins` collection
- **Indexes**: Created for efficient queries on timestamp, binId, sensorId

---

## Rate Limiting (Recommended for Production)

To prevent abuse, implement rate limiting:
- Per IP: 100 requests/minute for public endpoints
- Per user: 1000 requests/hour for protected endpoints
- Per sensor device: 1 request/60 seconds (configurable)

---

## Testing with cURL

### Send sensor data:
```bash
curl -X POST http://localhost:5000/api/iot/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
    "sensorId": "65a1b2c3d4e5f6g7h8i9j0k2",
    "distance": 45.5,
    "batteryLevel": 87,
    "timestamp": "2025-08-13T10:30:45Z"
  }'
```

### Register sensor:
```bash
curl -X POST http://localhost:5000/api/iot/sensors \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "binId": "65a1b2c3d4e5f6g7h8i9j0k1",
    "sensorType": "ultrasonic",
    "deviceId": "esp32-bin-001"
  }'
```

### Get sensor history:
```bash
curl -X GET "http://localhost:5000/api/iot/bins/65a1b2c3d4e5f6g7h8i9j0k1/sensor-history?limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Error Handling

All error responses follow this format:
```json
{
  "success": false,
  "message": "Human-readable error message",
  "errors": ["Detailed error 1", "Detailed error 2"]
}
```

---

## Webhook Notifications (Future Enhancement)

Coming in Phase 2:
- `bin.overflow` - Bin at critical level
- `bin.full` - Bin needs collection
- `sensor.low_battery` - Battery below threshold
- `sensor.malfunction` - Sensor error detected

---

## Version History

- **v1.0** (2025-08-13) - Initial IoT sensor data ingestion
  - Ultrasonic sensor support
  - Time-series data storage
  - Sensor registration and management
