"""
app/models/alert_model.py  –  Alert schemas and logic
Handles alert generation, deduplication, and history tracking.
"""
from datetime import datetime, timezone
from typing import Optional

# ── Alert Types ────────────────────────────────────────────────────────────
ALERT_TYPE_OVERFLOW = "bin_overflow"
ALERT_TYPE_FULL = "bin_full"
ALERT_TYPE_LOW_BATTERY = "sensor_low_battery"
ALERT_TYPE_SENSOR_OFFLINE = "sensor_offline"
ALERT_TYPE_MAINTENANCE = "bin_maintenance"

ALERT_TYPES = [
    ALERT_TYPE_OVERFLOW,
    ALERT_TYPE_FULL,
    ALERT_TYPE_LOW_BATTERY,
    ALERT_TYPE_SENSOR_OFFLINE,
    ALERT_TYPE_MAINTENANCE,
]

# ── Alert Severity ─────────────────────────────────────────────────────────
SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"

ALERT_SEVERITIES = [SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_CRITICAL]

# ── Alert Status ───────────────────────────────────────────────────────────
STATUS_ACTIVE = "active"
STATUS_ACKNOWLEDGED = "acknowledged"
STATUS_RESOLVED = "resolved"

ALERT_STATUSES = [STATUS_ACTIVE, STATUS_ACKNOWLEDGED, STATUS_RESOLVED]


def create_alert_schema(
    bin_id: str,
    alert_type: str,
    severity: str = SEVERITY_WARNING,
    message: str = "",
    metadata: dict = None,
) -> dict:
    """
    Create a new alert document.
    
    Args:
        bin_id: MongoDB ObjectId of the affected bin
        alert_type: Type of alert (overflow, full, low_battery, etc.)
        severity: Alert severity (info, warning, critical)
        message: Human-readable alert message
        metadata: Additional context (sensor_id, fill_level, battery_level, etc.)
    
    Returns:
        Alert document ready for insertion
    """
    return {
        "binId": bin_id,
        "alertType": alert_type,
        "severity": severity,
        "message": message,
        "metadata": metadata or {},
        "status": STATUS_ACTIVE,
        "createdAt": datetime.now(timezone.utc),
        "acknowledgedAt": None,
        "acknowledgedBy": None,
        "resolvedAt": None,
        "resolvedBy": None,
        "notes": "",
        "isDuplicate": False,
        "parentAlertId": None,  # For deduplication - links to original alert
    }


def create_alert_dedup_key(bin_id: str, alert_type: str, metadata: dict = None) -> str:
    """
    Create a deduplication key to prevent duplicate alerts.
    
    Combines bin_id, alert_type, and key metadata to create unique key.
    This prevents duplicate alerts within a time window.
    
    Args:
        bin_id: Bin ID
        alert_type: Alert type
        metadata: Alert metadata (sensor_id, etc.)
    
    Returns:
        Deduplication key string
    """
    sensor_id = ""
    if metadata and "sensorId" in metadata:
        sensor_id = str(metadata["sensorId"])
    
    return f"{bin_id}:{alert_type}:{sensor_id}"


def serialize_alert(alert_doc: dict) -> dict:
    """Convert MongoDB alert document to JSON-serialisable dict."""
    return {
        "id": str(alert_doc["_id"]),
        "binId": str(alert_doc.get("binId", "")),
        "alertType": alert_doc.get("alertType", ""),
        "severity": alert_doc.get("severity", ""),
        "message": alert_doc.get("message", ""),
        "metadata": alert_doc.get("metadata", {}),
        "status": alert_doc.get("status", ""),
        "createdAt": alert_doc["createdAt"].isoformat() if alert_doc.get("createdAt") else "",
        "acknowledgedAt": alert_doc["acknowledgedAt"].isoformat() if alert_doc.get("acknowledgedAt") else None,
        "acknowledgedBy": alert_doc.get("acknowledgedBy"),
        "resolvedAt": alert_doc["resolvedAt"].isoformat() if alert_doc.get("resolvedAt") else None,
        "resolvedBy": alert_doc.get("resolvedBy"),
        "notes": alert_doc.get("notes", ""),
        "isDuplicate": alert_doc.get("isDuplicate", False),
        "parentAlertId": alert_doc.get("parentAlertId"),
    }


def get_alert_severity(alert_type: str, metadata: dict = None) -> str:
    """
    Determine alert severity based on type and metadata.
    
    Args:
        alert_type: Type of alert
        metadata: Additional context
    
    Returns:
        Severity level (info, warning, critical)
    """
    if alert_type == ALERT_TYPE_OVERFLOW:
        return SEVERITY_CRITICAL
    elif alert_type == ALERT_TYPE_FULL:
        return SEVERITY_WARNING
    elif alert_type == ALERT_TYPE_LOW_BATTERY:
        return SEVERITY_WARNING
    elif alert_type == ALERT_TYPE_SENSOR_OFFLINE:
        return SEVERITY_WARNING
    elif alert_type == ALERT_TYPE_MAINTENANCE:
        return SEVERITY_INFO
    else:
        return SEVERITY_WARNING


def get_alert_message(alert_type: str, bin_label: str = "", metadata: dict = None) -> str:
    """
    Generate human-readable alert message.
    
    Args:
        alert_type: Type of alert
        bin_label: Bin label/name
        metadata: Additional context
    
    Returns:
        Message string
    """
    bin_ref = f"'{bin_label}'" if bin_label else "Bin"
    
    if alert_type == ALERT_TYPE_OVERFLOW:
        fill_level = metadata.get("fillLevel", "unknown") if metadata else "unknown"
        return f"{bin_ref} is at overflow status ({fill_level}%). Immediate collection required."
    
    elif alert_type == ALERT_TYPE_FULL:
        fill_level = metadata.get("fillLevel", "unknown") if metadata else "unknown"
        return f"{bin_ref} is full ({fill_level}%). Schedule collection soon."
    
    elif alert_type == ALERT_TYPE_LOW_BATTERY:
        battery = metadata.get("batteryLevel", "unknown") if metadata else "unknown"
        return f"Sensor battery for {bin_ref} is low ({battery}%). Replace soon."
    
    elif alert_type == ALERT_TYPE_SENSOR_OFFLINE:
        return f"Sensor for {bin_ref} is offline. No readings received."
    
    elif alert_type == ALERT_TYPE_MAINTENANCE:
        return f"{bin_ref} requires maintenance."
    
    else:
        return f"Alert generated for {bin_ref}."
