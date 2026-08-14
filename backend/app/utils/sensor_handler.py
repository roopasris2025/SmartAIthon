"""
app/utils/sensor_handler.py  –  Modular sensor abstraction layer
Provides extensible interface for different sensor types.
Keep decoupled from specific sensor implementations for easy replacement.
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime, timezone


# ── Sensor Base Class (Abstract Interface) ─────────────────────────────────────
class SensorHandler(ABC):
    """
    Abstract base class for sensor implementations.
    Subclass this to add support for new sensor types (IR, pressure, weight, etc).
    """
    
    def __init__(self, sensor_config: dict):
        """
        Initialize with sensor configuration document from MongoDB.
        
        Args:
            sensor_config: The sensor document dict from the sensors collection
        """
        self.config = sensor_config
        self.sensor_type = sensor_config.get("sensorType", "unknown")
        self.sensor_id = str(sensor_config.get("_id", ""))
        self.bin_id = str(sensor_config.get("binId", ""))
    
    @abstractmethod
    def process_reading(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw sensor data and return normalized output.
        
        Expected raw_data keys (example for ultrasonic):
        - distance: distance in cm
        - rawAdc: ADC reading from sensor
        
        Should return dict with:
        - fillLevel: normalized percentage (0-100+)
        - sensorStatus: "ok" | "low_battery" | "malfunction"
        - batteryLevel: battery percentage (0-100) if available
        - rawDistance: raw distance value for diagnostics
        - timestamp: datetime when reading was taken
        
        Args:
            raw_data: Raw sensor data from IoT device
        
        Returns:
            Normalized sensor reading dict
        """
        pass
    
    @abstractmethod
    def validate_data(self, raw_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate raw sensor data before processing.
        
        Args:
            raw_data: Raw sensor data from IoT device
        
        Returns:
            Tuple (is_valid, error_message)
        """
        pass


# ── Ultrasonic Sensor Implementation ───────────────────────────────────────────
class UltrasonicSensorHandler(SensorHandler):
    """
    Handler for ultrasonic distance sensors (e.g., HC-SR04 on ESP32).
    
    Calibration:
    - minDistance (cm): distance when bin is empty
    - maxDistance (cm): distance when bin is full
    
    Calculation:
    fillLevel = ((maxDistance - distance) / (maxDistance - minDistance)) * 100
    """
    
    def validate_data(self, raw_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate ultrasonic sensor data."""
        if not isinstance(raw_data, dict):
            return False, "raw_data must be a dict"
        
        if "distance" not in raw_data:
            return False, "distance field is required"
        
        try:
            distance = float(raw_data["distance"])
            if distance < 0:
                return False, "distance cannot be negative"
        except (ValueError, TypeError):
            return False, "distance must be a number (cm)"
        
        return True, None
    
    def process_reading(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ultrasonic sensor reading.
        
        Expected fields:
        - distance: measured distance in cm
        - batteryLevel (optional): battery percentage
        - timestamp (optional): reading timestamp (defaults to now)
        """
        is_valid, error = self.validate_data(raw_data)
        if not is_valid:
            raise ValueError(f"Invalid sensor data: {error}")
        
        # Get calibration data (with defaults)
        calib = self.config.get("calibrationData", {})
        min_dist = float(calib.get("minDistance", 5))      # 5 cm when empty
        max_dist = float(calib.get("maxDistance", 100))    # 100 cm when full
        
        distance = float(raw_data["distance"])
        battery = raw_data.get("batteryLevel")
        timestamp = raw_data.get("timestamp")
        
        # Clamp distance to calibration range
        if distance <= min_dist:
            fill_level = 100.0
        elif distance >= max_dist:
            fill_level = 0.0
        else:
            # Linear interpolation: percentage = ((max - measured) / (max - min)) * 100
            fill_level = ((max_dist - distance) / (max_dist - min_dist)) * 100
            # Clamp to 0-110 (allow slight overflow)
            fill_level = max(0, min(110, fill_level))
        
        # Determine sensor health status
        sensor_status = "ok"
        if battery is not None:
            try:
                batt_pct = float(battery)
                if batt_pct < 20:
                    sensor_status = "low_battery"
            except (ValueError, TypeError):
                pass
        
        return {
            "fillLevel": round(fill_level, 2),
            "sensorStatus": sensor_status,
            "batteryLevel": float(battery) if battery is not None else None,
            "rawDistance": distance,
            "timestamp": timestamp or datetime.now(timezone.utc),
            "sensorType": "ultrasonic",
        }


# ── Infrared Sensor Implementation (Template) ──────────────────────────────────
class InfraredSensorHandler(SensorHandler):
    """
    Handler for infrared proximity sensors.
    Placeholder for future expansion.
    """
    
    def validate_data(self, raw_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate IR sensor data."""
        if "proximity" not in raw_data:
            return False, "proximity field is required"
        return True, None
    
    def process_reading(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process IR sensor reading.
        Similar to ultrasonic but using proximity value.
        """
        is_valid, error = self.validate_data(raw_data)
        if not is_valid:
            raise ValueError(f"Invalid sensor data: {error}")
        
        # Simplified IR processing (extend as needed)
        proximity = float(raw_data.get("proximity", 0))
        fill_level = min(100, max(0, proximity))
        
        return {
            "fillLevel": round(fill_level, 2),
            "sensorStatus": "ok",
            "batteryLevel": raw_data.get("batteryLevel"),
            "rawDistance": None,
            "timestamp": raw_data.get("timestamp") or datetime.now(timezone.utc),
            "sensorType": "infrared",
        }


# ── Sensor Factory ────────────────────────────────────────────────────────────
def create_sensor_handler(sensor_config: dict) -> SensorHandler:
    """
    Factory function to create the appropriate sensor handler.
    
    Args:
        sensor_config: Sensor configuration document from MongoDB
    
    Returns:
        SensorHandler subclass instance
    
    Raises:
        ValueError: If sensor type is not supported
    """
    sensor_type = sensor_config.get("sensorType", "ultrasonic").lower()
    
    handlers: Dict[str, type] = {
        "ultrasonic": UltrasonicSensorHandler,
        "infrared": InfraredSensorHandler,
        # "pressure": PressureSensorHandler,  # Future
        # "weight": WeightSensorHandler,      # Future
    }
    
    if sensor_type not in handlers:
        raise ValueError(
            f"Unsupported sensor type: {sensor_type}. "
            f"Supported types: {', '.join(handlers.keys())}"
        )
    
    handler_class = handlers[sensor_type]
    return handler_class(sensor_config)


# ── Validation utilities ──────────────────────────────────────────────────────
def validate_iot_payload(payload: dict) -> tuple[bool, Optional[str]]:
    """
    Validate incoming IoT sensor data payload.
    
    Expected fields:
    - binId: MongoDB ObjectId of the bin
    - sensorId: MongoDB ObjectId of the sensor
    - fillLevel: fill percentage (0-100+)
    - timestamp: ISO 8601 datetime
    - sensorStatus: sensor health status
    - batteryLevel (optional): battery percentage
    
    Args:
        payload: Raw payload dict from HTTP request
    
    Returns:
        Tuple (is_valid, error_message)
    """
    required = {"binId", "sensorId", "fillLevel", "timestamp", "sensorStatus"}
    if not required.issubset(set(payload.keys())):
        missing = required - set(payload.keys())
        return False, f"Missing required fields: {', '.join(missing)}"
    
    try:
        fill_level = float(payload["fillLevel"])
        if fill_level < 0:
            return False, "fillLevel cannot be negative"
    except (ValueError, TypeError):
        return False, "fillLevel must be a number"
    
    if payload["sensorStatus"] not in ("ok", "low_battery", "malfunction"):
        return False, "sensorStatus must be 'ok', 'low_battery', or 'malfunction'"
    
    return True, None
