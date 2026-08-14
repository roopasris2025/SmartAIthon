"""
app/controllers/iot_controller.py  –  IoT sensor data ingestion and management
Handles receiving sensor data from ESP32 devices and updating bin fill levels.
"""
from flask import request
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional

from app.utils.helpers import (
    get_db, success_response, error_response, is_valid_object_id, now_utc
)
from app.utils.sensor_handler import create_sensor_handler, validate_iot_payload
from app.models.iot_model import (
    create_sensor_schema, create_iot_reading_schema, serialize_sensor, 
    serialize_iot_reading, get_fill_level_status, SENSOR_TYPES, SENSOR_STATUSES
)
from app.models.alert_model import (
    ALERT_TYPE_OVERFLOW,
    ALERT_TYPE_FULL,
    ALERT_TYPE_LOW_BATTERY,
)


# ── POST /api/iot/sensor-data (Receive IoT data) ────────────────────────────────
def receive_sensor_data():
    """
    POST /api/iot/sensor-data
    
    Receive raw sensor data from IoT device and update bin fill level.
    No authentication required (IoT devices can't easily manage JWT).
    Security: API key validation should be added in production.
    
    Expected request body:
    {
        "binId": "ObjectId string",
        "sensorId": "ObjectId string",
        "fillLevel": number (0-100+),
        "timestamp": ISO 8601 datetime,
        "sensorStatus": "ok" | "low_battery" | "malfunction",
        "batteryLevel": number (0-100) [optional],
        "rawDistance": number [optional, for ultrasonic sensors]
    }
    
    OR raw sensor format (processed by sensor handler):
    {
        "binId": "ObjectId string",
        "sensorId": "ObjectId string",
        "distance": number (cm) [for ultrasonic],
        "batteryLevel": number (0-100) [optional],
        "timestamp": ISO 8601 datetime [optional, defaults to now]
    }
    """
    data = request.get_json(silent=True) or {}
    db = get_db()
    
    # ── Validate required fields ──────────────────────────────────────────────
    if not data.get("binId"):
        return error_response("binId is required", 400)
    if not data.get("sensorId"):
        return error_response("sensorId is required", 400)
    
    # Parse ObjectIds
    try:
        bin_id = ObjectId(data["binId"])
        sensor_id = ObjectId(data["sensorId"])
    except Exception as e:
        return error_response(f"Invalid ObjectId format: {str(e)}", 400)
    
    # ── Fetch bin ─────────────────────────────────────────────────────────────
    bin_doc = db.bins.find_one({"_id": bin_id})
    if not bin_doc:
        return error_response("Bin not found", 404)
    
    # ── Fetch sensor configuration ────────────────────────────────────────────
    sensor_doc = db.sensors.find_one({"_id": sensor_id})
    if not sensor_doc:
        return error_response("Sensor not found", 404)
    
    if str(sensor_doc.get("binId")) != str(bin_id):
        return error_response("Sensor is not associated with this bin", 400)
    
    # ── Process sensor data through abstraction layer ─────────────────────────
    try:
        sensor_handler = create_sensor_handler(sensor_doc)
        
        # Check if data is already normalized or raw
        if "fillLevel" in data and "timestamp" in data and "sensorStatus" in data:
            # Already normalized format - validate and use directly
            is_valid, error = validate_iot_payload(data)
            if not is_valid:
                return error_response(f"Invalid payload: {error}", 422)
            processed_data = data
            processed_data["timestamp"] = (
                datetime.fromisoformat(data["timestamp"]) 
                if isinstance(data["timestamp"], str) 
                else data["timestamp"]
            )
        else:
            # Raw sensor format - process through handler
            processed_data = sensor_handler.process_reading(data)
    
    except ValueError as e:
        return error_response(f"Sensor data processing error: {str(e)}", 422)
    except Exception as e:
        return error_response(f"Unexpected error processing sensor data: {str(e)}", 500)
    
    # ── Store the sensor reading (time-series data) ──────────────────────────
    timestamp = (
        processed_data["timestamp"] 
        if isinstance(processed_data["timestamp"], datetime)
        else datetime.fromisoformat(processed_data["timestamp"])
    )
    
    reading_doc = create_iot_reading_schema(
        bin_id=bin_id,
        sensor_id=sensor_id,
        fill_level=processed_data.get("fillLevel", 0),
        timestamp=timestamp,
        sensor_status=processed_data.get("sensorStatus", "ok"),
        battery_level=processed_data.get("batteryLevel"),
        raw_distance=processed_data.get("rawDistance"),
    )
    
    try:
        result = db.iot_readings.insert_one(reading_doc)
        reading_doc["_id"] = result.inserted_id
    except Exception as e:
        return error_response(f"Failed to store sensor reading: {str(e)}", 500)
    
    # ── Update bin with new fill level and status ────────────────────────────
    fill_level = float(processed_data.get("fillLevel", 0))
    new_status = get_fill_level_status(fill_level)
    
    updates = {
        "fillLevel": fill_level,
        "status": new_status,
        "updatedAt": now_utc(),
    }
    
    # Track last empty if transitioning to normal/low levels
    if fill_level < 20 and new_status == "normal":
        updates["lastEmptied"] = now_utc()
    
    try:
        db.bins.update_one({"_id": bin_id}, {"$set": updates})
    except Exception as e:
        return error_response(f"Failed to update bin: {str(e)}", 500)
    
    # ── Generate alerts if needed ──────────────────────────────────────────────
    _check_and_create_alerts(bin_id, fill_level, new_status, processed_data)
    
    # ── Update sensor's last heartbeat ───────────────────────────────────────
    sensor_updates = {
        "lastHeartbeat": now_utc(),
        "sensorStatus": processed_data.get("sensorStatus", "ok"),
        "updatedAt": now_utc(),
    }
    if processed_data.get("batteryLevel") is not None:
        sensor_updates["batteryLevel"] = processed_data.get("batteryLevel")
    
    try:
        db.sensors.update_one({"_id": sensor_id}, {"$set": sensor_updates})
    except Exception as e:
        # Non-critical - log but don't fail the response
        print(f"Warning: Failed to update sensor heartbeat: {str(e)}")
    
    # ── Return success with updated bin data ────────────────────────────────
    updated_bin = db.bins.find_one({"_id": bin_id})
    
    return success_response(
        "Sensor data processed successfully",
        {
            "reading": serialize_iot_reading(reading_doc),
            "bin": {
                "id": str(updated_bin["_id"]),
                "fillLevel": updated_bin.get("fillLevel"),
                "status": updated_bin.get("status"),
            }
        },
        201
    )


# ── POST /api/sensors (Create sensor) ───────────────────────────────────────────
def create_sensor():
    """
    POST /api/sensors
    Requires: JWT + admin role
    
    Body:
    {
        "binId": "ObjectId string",
        "sensorType": "ultrasonic" | "infrared" | "pressure" | "weight",
        "deviceId": "unique device identifier",
        "apiKey": "secret key for authentication" [optional],
        "calibrationData": {
            "minDistance": number (cm),
            "maxDistance": number (cm)
        }
    }
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admin access required", 403)
    
    data = request.get_json(silent=True) or {}
    db = get_db()
    
    # ── Validate ──────────────────────────────────────────────────────────────
    if not data.get("binId"):
        return error_response("binId is required", 400)
    if not data.get("sensorType"):
        return error_response("sensorType is required", 400)
    if data["sensorType"] not in SENSOR_TYPES:
        return error_response(
            f"sensorType must be one of: {', '.join(SENSOR_TYPES)}", 400
        )
    
    # ── Verify bin exists ─────────────────────────────────────────────────────
    try:
        bin_id = ObjectId(data["binId"])
    except Exception:
        return error_response("Invalid binId format", 400)
    
    bin_doc = db.bins.find_one({"_id": bin_id})
    if not bin_doc:
        return error_response("Bin not found", 404)
    
    # ── Create sensor ─────────────────────────────────────────────────────────
    sensor_doc = create_sensor_schema(
        bin_id=bin_id,
        sensor_type=data["sensorType"],
        device_id=data.get("deviceId", ""),
        api_key=data.get("apiKey", ""),
    )
    
    # ── Apply calibration data if provided ─────────────────────────────────────
    if "calibrationData" in data and isinstance(data["calibrationData"], dict):
        calib = data["calibrationData"]
        if "minDistance" in calib:
            sensor_doc["calibrationData"]["minDistance"] = float(calib["minDistance"])
        if "maxDistance" in calib:
            sensor_doc["calibrationData"]["maxDistance"] = float(calib["maxDistance"])
    
    # ── Apply config if provided ───────────────────────────────────────────────
    if "config" in data and isinstance(data["config"], dict):
        cfg = data["config"]
        if "updateInterval" in cfg:
            sensor_doc["config"]["updateInterval"] = int(cfg["updateInterval"])
        if "enableBattery" in cfg:
            sensor_doc["config"]["enableBattery"] = bool(cfg["enableBattery"])
    
    if "notes" in data:
        sensor_doc["notes"] = data.get("notes", "")
    
    # ── Insert ────────────────────────────────────────────────────────────────
    try:
        result = db.sensors.insert_one(sensor_doc)
        sensor_doc["_id"] = result.inserted_id
    except Exception as e:
        return error_response(f"Failed to create sensor: {str(e)}", 500)
    
    return success_response("Sensor created successfully", serialize_sensor(sensor_doc), 201)


# ── GET /api/sensors/:id (Get sensor config) ───────────────────────────────────
def get_sensor(sensor_id: str):
    """
    GET /api/sensors/:id
    Requires: JWT + admin role
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admin access required", 403)
    
    db = get_db()
    if not is_valid_object_id(sensor_id):
        return error_response("Invalid sensor ID", 400)
    
    sensor_doc = db.sensors.find_one({"_id": ObjectId(sensor_id)})
    if not sensor_doc:
        return error_response("Sensor not found", 404)
    
    return success_response("Sensor fetched", serialize_sensor(sensor_doc))


# ── PATCH /api/sensors/:id (Update sensor config) ───────────────────────────────
def update_sensor(sensor_id: str):
    """
    PATCH /api/sensors/:id
    Requires: JWT + admin role
    
    Updatable fields:
    - status: active | inactive | error | calibration
    - calibrationData: { minDistance, maxDistance }
    - config: { updateInterval, enableBattery }
    - notes: string
    """
    claims = get_jwt()
    if claims.get("role") != "admin":
        return error_response("Admin access required", 403)
    
    data = request.get_json(silent=True) or {}
    db = get_db()
    
    if not is_valid_object_id(sensor_id):
        return error_response("Invalid sensor ID", 400)
    
    sensor_doc = db.sensors.find_one({"_id": ObjectId(sensor_id)})
    if not sensor_doc:
        return error_response("Sensor not found", 404)
    
    # ── Build updates ─────────────────────────────────────────────────────────
    updates = {"updatedAt": now_utc()}
    
    if "status" in data:
        if data["status"] not in SENSOR_STATUSES:
            return error_response(
                f"status must be one of: {', '.join(SENSOR_STATUSES)}", 400
            )
        updates["status"] = data["status"]
    
    if "calibrationData" in data:
        if isinstance(data["calibrationData"], dict):
            calib = data["calibrationData"]
            if "minDistance" in calib:
                sensor_doc["calibrationData"]["minDistance"] = float(calib["minDistance"])
            if "maxDistance" in calib:
                sensor_doc["calibrationData"]["maxDistance"] = float(calib["maxDistance"])
            updates["calibrationData"] = sensor_doc["calibrationData"]
    
    if "config" in data:
        if isinstance(data["config"], dict):
            cfg = data["config"]
            if "updateInterval" in cfg:
                sensor_doc["config"]["updateInterval"] = int(cfg["updateInterval"])
            if "enableBattery" in cfg:
                sensor_doc["config"]["enableBattery"] = bool(cfg["enableBattery"])
            updates["config"] = sensor_doc["config"]
    
    if "notes" in data:
        updates["notes"] = str(data["notes"])
    
    try:
        db.sensors.update_one({"_id": ObjectId(sensor_id)}, {"$set": updates})
    except Exception as e:
        return error_response(f"Failed to update sensor: {str(e)}", 500)
    
    updated = db.sensors.find_one({"_id": ObjectId(sensor_id)})
    return success_response("Sensor updated successfully", serialize_sensor(updated))


# ── GET /api/bins/:id/sensor-history (Get sensor readings) ──────────────────────
def get_sensor_history(bin_id: str):
    """
    GET /api/bins/:id/sensor-history?limit=100&offset=0
    Requires: JWT
    
    Get historical sensor readings for a bin.
    """
    db = get_db()
    if not is_valid_object_id(bin_id):
        return error_response("Invalid bin ID", 400)
    
    bin_doc = db.bins.find_one({"_id": ObjectId(bin_id)})
    if not bin_doc:
        return error_response("Bin not found", 404)
    
    # ── Pagination ────────────────────────────────────────────────────────────
    try:
        limit = min(int(request.args.get("limit", 100)), 500)
        offset = int(request.args.get("offset", 0))
    except ValueError:
        limit, offset = 100, 0
    
    # ── Fetch readings ────────────────────────────────────────────────────────
    try:
        readings = list(
            db.iot_readings.find({"binId": ObjectId(bin_id)})
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )
        total = db.iot_readings.count_documents({"binId": ObjectId(bin_id)})
    except Exception as e:
        return error_response(f"Failed to fetch sensor history: {str(e)}", 500)
    
    return success_response(
        "Sensor history fetched",
        {
            "readings": [serialize_iot_reading(r) for r in readings],
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": offset + limit < total,
            }
        }
    )


# ═════════════════════════════════════════════════════════════════════════════
# Internal Helper Functions
# ═════════════════════════════════════════════════════════════════════════════

def _check_and_create_alerts(
    bin_id: ObjectId,
    fill_level: float,
    status: str,
    processed_data: dict
) -> None:
    """
    Check bin state and create alerts if needed.
    
    Args:
        bin_id: Bin ID
        fill_level: Fill level percentage
        status: Current bin status (normal/full/overflow)
        processed_data: Processed sensor data with battery info
    """
    try:
        from app.controllers.alert_controller import check_and_create_alert
        
        db = get_db()
        bin_doc = db.bins.find_one({"_id": bin_id})
        bin_label = bin_doc.get("label", "Bin") if bin_doc else "Bin"
        
        # Check for overflow alert
        if status == "overflow":
            check_and_create_alert(
                bin_id=str(bin_id),
                alert_type=ALERT_TYPE_OVERFLOW,
                metadata={
                    "fillLevel": fill_level,
                    "sensorId": processed_data.get("sensorId", ""),
                    "binLabel": bin_label,
                },
                dedup_window_seconds=3600,  # 1 hour dedup window
            )
        
        # Check for full alert
        elif status == "full":
            check_and_create_alert(
                bin_id=str(bin_id),
                alert_type=ALERT_TYPE_FULL,
                metadata={
                    "fillLevel": fill_level,
                    "sensorId": processed_data.get("sensorId", ""),
                    "binLabel": bin_label,
                },
                dedup_window_seconds=7200,  # 2 hour dedup window
            )
        
        # Check for low battery alert
        battery = processed_data.get("batteryLevel")
        if battery is not None and battery < 20:
            check_and_create_alert(
                bin_id=str(bin_id),
                alert_type=ALERT_TYPE_LOW_BATTERY,
                metadata={
                    "batteryLevel": battery,
                    "sensorId": processed_data.get("sensorId", ""),
                    "binLabel": bin_label,
                },
                dedup_window_seconds=86400,  # 24 hour dedup window
            )
    
    except Exception as e:
        print(f"Warning: Failed to check/create alerts for bin {bin_id}: {e}")

