"""
app/controllers/alert_controller.py  –  Alert management API endpoints
Handles alert generation, tracking, and deduplication.
"""
from datetime import datetime, timezone, timedelta
from flask import request, jsonify
from bson import ObjectId
from pymongo import DESCENDING

from app.utils.helpers import get_db, error_response, success_response, validate_objectid
from app.models.alert_model import (
    create_alert_schema,
    create_alert_dedup_key,
    serialize_alert,
    get_alert_severity,
    get_alert_message,
    ALERT_TYPES,
    ALERT_SEVERITIES,
    STATUS_ACTIVE,
    STATUS_ACKNOWLEDGED,
    STATUS_RESOLVED,
)
from app.models.bin_model import serialize_bin
from app.utils.decorators import token_required, admin_required


# ═════════════════════════════════════════════════════════════════════════════
# 1. GET /alerts  –  Get all alerts (with filtering)
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def get_alerts():
    """
    Retrieve alerts with optional filtering.
    
    Query Parameters:
        - status: Filter by status (active, acknowledged, resolved)
        - severity: Filter by severity (info, warning, critical)
        - binId: Filter by specific bin
        - limit: Number of alerts to return (default: 50)
        - skip: Pagination offset (default: 0)
    
    Returns:
        {"success": True, "alerts": [...], "total": N}
    """
    try:
        db = get_db()
        filters = {}
        
        # Status filter
        status = request.args.get("status", "").strip()
        if status:
            if status not in ["active", "acknowledged", "resolved"]:
                return jsonify({"success": False, "error": "Invalid status"}), 400
            filters["status"] = status
        
        # Severity filter
        severity = request.args.get("severity", "").strip()
        if severity:
            if severity not in ALERT_SEVERITIES:
                return jsonify({"success": False, "error": "Invalid severity"}), 400
            filters["severity"] = severity
        
        # Bin filter
        bin_id = request.args.get("binId", "").strip()
        if bin_id:
            if not validate_objectid(bin_id):
                return jsonify({"success": False, "error": "Invalid binId"}), 400
            filters["binId"] = ObjectId(bin_id)
        
        # Pagination
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        
        # Query
        alerts = list(
            db.alerts.find(filters)
            .sort("createdAt", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        total = db.alerts.count_documents(filters)
        
        return jsonify({
            "success": True,
            "alerts": [serialize_alert(a) for a in alerts],
            "total": total,
            "limit": limit,
            "skip": skip,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 2. GET /alerts/:id  –  Get specific alert with bin details
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def get_alert(alert_id):
    """
    Retrieve a specific alert with full details.
    
    Path Parameters:
        - alert_id: Alert ID
    
    Returns:
        {"success": True, "alert": {...}, "bin": {...}}
    """
    try:
        if not validate_objectid(alert_id):
            return jsonify({"success": False, "error": "Invalid alert ID"}), 400
        
        db = get_db()
        alert = db.alerts.find_one({"_id": ObjectId(alert_id)})
        
        if not alert:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        
        # Get bin details
        bin_doc = db.bins.find_one({"_id": alert.get("binId")})
        
        response = {"success": True, "alert": serialize_alert(alert)}
        if bin_doc:
            response["bin"] = serialize_bin(bin_doc)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 3. PATCH /alerts/:id/acknowledge  –  Mark alert as acknowledged
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def acknowledge_alert(alert_id):
    """
    Acknowledge an alert (mark as seen by admin).
    
    Path Parameters:
        - alert_id: Alert ID
    
    Request Body:
        - notes: Optional notes about the acknowledgment
    
    Returns:
        {"success": True, "alert": {...}}
    """
    try:
        if not validate_objectid(alert_id):
            return jsonify({"success": False, "error": "Invalid alert ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        
        update = {
            "status": STATUS_ACKNOWLEDGED,
            "acknowledgedAt": datetime.now(timezone.utc),
            "acknowledgedBy": request.user_id,
        }
        
        if "notes" in data:
            update["notes"] = data.get("notes", "").strip()
        
        result = db.alerts.find_one_and_update(
            {"_id": ObjectId(alert_id)},
            {"$set": update},
            return_document=True,
        )
        
        if not result:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        
        return jsonify({"success": True, "alert": serialize_alert(result)})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 4. PATCH /alerts/:id/resolve  –  Resolve an alert
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def resolve_alert(alert_id):
    """
    Resolve an alert (mark as handled).
    
    Path Parameters:
        - alert_id: Alert ID
    
    Request Body:
        - notes: Optional resolution notes
    
    Returns:
        {"success": True, "alert": {...}}
    """
    try:
        if not validate_objectid(alert_id):
            return jsonify({"success": False, "error": "Invalid alert ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        
        update = {
            "status": STATUS_RESOLVED,
            "resolvedAt": datetime.now(timezone.utc),
            "resolvedBy": request.user_id,
        }
        
        if "notes" in data:
            update["notes"] = data.get("notes", "").strip()
        
        result = db.alerts.find_one_and_update(
            {"_id": ObjectId(alert_id)},
            {"$set": update},
            return_document=True,
        )
        
        if not result:
            return jsonify({"success": False, "error": "Alert not found"}), 404
        
        return jsonify({"success": True, "alert": serialize_alert(result)})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 5. GET /alerts/bin/:id/history  –  Get alert history for a bin
# ═════════════════════════════════════════════════════════════════════════════

@token_required
def get_bin_alert_history(bin_id):
    """
    Retrieve alert history for a specific bin.
    
    Path Parameters:
        - bin_id: Bin ID
    
    Query Parameters:
        - limit: Number of alerts to return (default: 50)
        - skip: Pagination offset (default: 0)
    
    Returns:
        {"success": True, "alerts": [...], "total": N}
    """
    try:
        if not validate_objectid(bin_id):
            return jsonify({"success": False, "error": "Invalid bin ID"}), 400
        
        db = get_db()
        
        # Verify bin exists (user can only view alerts for bins they have access to)
        bin_doc = db.bins.find_one({"_id": ObjectId(bin_id)})
        if not bin_doc:
            return jsonify({"success": False, "error": "Bin not found"}), 404
        
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        
        alerts = list(
            db.alerts.find({"binId": ObjectId(bin_id)})
            .sort("createdAt", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        total = db.alerts.count_documents({"binId": ObjectId(bin_id)})
        
        return jsonify({
            "success": True,
            "alerts": [serialize_alert(a) for a in alerts],
            "total": total,
            "limit": limit,
            "skip": skip,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# Internal Helper Functions (Called by other controllers)
# ═════════════════════════════════════════════════════════════════════════════

def check_and_create_alert(
    bin_id: str,
    alert_type: str,
    metadata: dict = None,
    dedup_window_seconds: int = 3600,
) -> dict:
    """
    Check if alert already exists, create if not (handles deduplication).
    
    Args:
        bin_id: Bin ID
        alert_type: Alert type
        metadata: Alert metadata (fillLevel, sensorId, etc.)
        dedup_window_seconds: Time window for deduplication (default: 1 hour)
    
    Returns:
        {"created": bool, "alert": alert_doc or None, "isDuplicate": bool}
    """
    db = get_db()
    
    try:
        # Check for recent active alert of same type
        dedup_key = create_alert_dedup_key(bin_id, alert_type, metadata)
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=dedup_window_seconds)
        
        existing_alert = db.alerts.find_one({
            "binId": ObjectId(bin_id),
            "alertType": alert_type,
            "status": STATUS_ACTIVE,
            "createdAt": {"$gt": cutoff_time},
        })
        
        if existing_alert:
            return {
                "created": False,
                "alert": existing_alert,
                "isDuplicate": True,
            }
        
        # Create new alert
        bin_doc = db.bins.find_one({"_id": ObjectId(bin_id)})
        bin_label = bin_doc.get("label", "Unknown") if bin_doc else "Unknown"
        
        severity = get_alert_severity(alert_type, metadata)
        message = get_alert_message(alert_type, bin_label, metadata)
        
        alert_doc = create_alert_schema(
            bin_id=ObjectId(bin_id),
            alert_type=alert_type,
            severity=severity,
            message=message,
            metadata=metadata or {},
        )
        
        result = db.alerts.insert_one(alert_doc)
        alert_doc["_id"] = result.inserted_id
        
        return {
            "created": True,
            "alert": alert_doc,
            "isDuplicate": False,
        }
    
    except Exception as e:
        print(f"Error creating alert: {e}")
        return {
            "created": False,
            "alert": None,
            "isDuplicate": False,
            "error": str(e),
        }
