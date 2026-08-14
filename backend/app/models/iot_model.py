"""
app/models/iot_model.py  –  IoT sensor and sensor data schema helpers
Defines data structures for IoT devices, sensor readings, and configuration.
"""
from datetime import datetime, timezone
from typing import Optional


# ── Sensor Types ──────────────────────────────────────────────────────────────
SENSOR_TYPES = ["ultrasonic", "infrared", "pressure", "weight"]
SENSOR_STATUSES = ["active", "inactive", "error", "calibration"]


def create_sensor_schema(
    bin_id: str,
    sensor_type: str = "ultrasonic",
    device_id: str = "",
    api_key: str = "",
) -> dict:
    """
    Create a new sensor configuration document.
    
    Args:
        bin_id: MongoDB ObjectId of the associated bin
        sensor_type: Type of sensor (ultrasonic, infrared, pressure, weight)
        device_id: Unique identifier for the IoT device (e.g., MAC address, serial number)
        api_key: Secret key for sensor authentication
    
    Returns:
        A new sensor configuration dict ready for insertion into MongoDB
    """
    return {
        "binId": bin_id,
        "sensorType": sensor_type,
        "deviceId": device_id,
        "apiKey": api_key,
        "status": "active",  # active | inactive | error | calibration
        "lastHeartbeat": None,
        "batteryLevel": None,
        "sensorStatus": "ok",  # ok | low_battery | malfunction
        "calibrationData": {
            "minDistance": 0,      # cm - distance when bin is empty
            "maxDistance": 100,    # cm - distance when bin is full
        },
        "config": {
            "updateInterval": 300,  # seconds between readings (default 5 min)
            "enableBattery": True,
        },
        "notes": "",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }


def create_iot_reading_schema(
    bin_id: str,
    sensor_id: str,
    fill_level: float,
    timestamp: datetime,
    sensor_status: str = "ok",
    battery_level: Optional[float] = None,
    raw_distance: Optional[float] = None,
) -> dict:
    """
    Create a new IoT sensor reading (time-series data).
    
    Args:
        bin_id: MongoDB ObjectId of the bin
        sensor_id: MongoDB ObjectId of the sensor
        fill_level: Percentage fill level (0-100+)
        timestamp: When the reading was taken
        sensor_status: Sensor health status (ok, low_battery, malfunction)
        battery_level: Battery percentage (0-100) if available
        raw_distance: Raw sensor distance reading (cm) for diagnostics
    
    Returns:
        A new reading document ready for insertion into MongoDB
    """
    return {
        "binId": bin_id,
        "sensorId": sensor_id,
        "fillLevel": float(fill_level),
        "timestamp": timestamp,
        "sensorStatus": sensor_status,
        "batteryLevel": float(battery_level) if battery_level is not None else None,
        "rawDistance": float(raw_distance) if raw_distance is not None else None,
        "recordedAt": datetime.now(timezone.utc),
    }


def get_fill_level_status(fill_level: float) -> str:
    """
    Determine bin status based on fill level with refined thresholds.
    
    Thresholds:
    - Below 80% = normal
    - 80–89% = warning (full)
    - 90–99% = critical (overflow reserved for 100%+)
    - 100%+ = overflow
    
    Args:
        fill_level: Current fill percentage
    
    Returns:
        Status string: normal, full (warning), overflow
    """
    if fill_level >= 100:
        return "overflow"
    elif fill_level >= 90:
        return "overflow"  # Critical state still mapped to overflow for collection
    elif fill_level >= 80:
        return "full"  # Warning state
    else:
        return "normal"


def serialize_sensor(sensor_doc: dict) -> dict:
    """
    Convert a MongoDB sensor document to JSON-serialisable dict.
    Excludes sensitive fields like apiKey.
    """
    return {
        "id": str(sensor_doc["_id"]),
        "binId": str(sensor_doc.get("binId", "")),
        "sensorType": sensor_doc.get("sensorType", "ultrasonic"),
        "deviceId": sensor_doc.get("deviceId", ""),
        "status": sensor_doc.get("status", "active"),
        "lastHeartbeat": sensor_doc["lastHeartbeat"].isoformat() if sensor_doc.get("lastHeartbeat") else None,
        "batteryLevel": sensor_doc.get("batteryLevel"),
        "sensorStatus": sensor_doc.get("sensorStatus", "ok"),
        "calibrationData": sensor_doc.get("calibrationData", {}),
        "config": sensor_doc.get("config", {}),
        "notes": sensor_doc.get("notes", ""),
        "createdAt": sensor_doc["createdAt"].isoformat() if sensor_doc.get("createdAt") else "",
        "updatedAt": sensor_doc["updatedAt"].isoformat() if sensor_doc.get("updatedAt") else "",
    }


def serialize_iot_reading(reading_doc: dict) -> dict:
    """Convert a MongoDB IoT reading document to JSON-serialisable dict."""
    return {
        "id": str(reading_doc["_id"]),
        "binId": str(reading_doc.get("binId", "")),
        "sensorId": str(reading_doc.get("sensorId", "")),
        "fillLevel": reading_doc.get("fillLevel", 0),
        "timestamp": reading_doc["timestamp"].isoformat() if reading_doc.get("timestamp") else "",
        "sensorStatus": reading_doc.get("sensorStatus", "ok"),
        "batteryLevel": reading_doc.get("batteryLevel"),
        "rawDistance": reading_doc.get("rawDistance"),
        "recordedAt": reading_doc["recordedAt"].isoformat() if reading_doc.get("recordedAt") else "",
    }
