"""
app/controllers/bin_controller.py  –  Smart Bin CRUD + fill-level updates
"""
from flask import request
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
from datetime import datetime, timezone

from app.utils.helpers    import get_db, success_response, error_response, is_valid_object_id
from app.utils.validators import validate_bin
from app.models.bin_model import create_bin_schema, serialize_bin, BIN_STATUSES
from app.models.iot_model import get_fill_level_status


# ── Get All Bins ───────────────────────────────────────────────────────────────
def get_bins():
    """
    GET /api/bins
    Query params: status, type
    Public-read (JWT still required for API consistency).
    """
    db     = get_db()
    params = request.args
    query: dict = {}

    if params.get("status") and params["status"] in BIN_STATUSES:
        query["status"] = params["status"]
    if params.get("type"):
        query["binType"] = params["type"]

    bins = list(db.bins.find(query).sort("createdAt", -1))
    return success_response("Bins fetched", [serialize_bin(b) for b in bins])


# ── Get Single Bin ─────────────────────────────────────────────────────────────
def get_bin(bin_id: str):
    """GET /api/bins/:id"""
    db = get_db()
    if not is_valid_object_id(bin_id):
        return error_response("Invalid bin ID", 400)

    bin_doc = db.bins.find_one({"_id": ObjectId(bin_id)})
    if not bin_doc:
        return error_response("Bin not found", 404)

    return success_response("Bin fetched", serialize_bin(bin_doc))


# ── Create Bin ─────────────────────────────────────────────────────────────────
def create_bin():
    """
    POST /api/bins
    Body: { label, location:{lat,lng,address?}, binType?, capacity? }
    Requires: JWT + admin
    """
    data = request.get_json(silent=True) or {}
    errors = validate_bin(data)
    if errors:
        return error_response("Validation failed", 422, errors)

    db      = get_db()
    user_id = get_jwt_identity()

    bin_doc = create_bin_schema(
        label=data["label"],
        location=data["location"],
        bin_type=data.get("binType", "general"),
        capacity=int(data.get("capacity", 100)),
    )
    bin_doc["addedBy"] = user_id

    result = db.bins.insert_one(bin_doc)
    bin_doc["_id"] = result.inserted_id

    return success_response("Bin created successfully", serialize_bin(bin_doc), 201)


# ── Update Bin (fill level / status) ──────────────────────────────────────────
def update_bin(bin_id: str):
    """
    PATCH /api/bins/:id
    Body: { fillLevel?, status?, label?, notes? }
    Requires: JWT + admin
    """
    data = request.get_json(silent=True) or {}
    errors = validate_bin({**{"label": "placeholder", "location": {"lat": 0, "lng": 0}}, **data})
    # Only re-validate updatable fields
    if "fillLevel" in data or "status" in data:
        subset_errors = validate_bin({
            "label": data.get("label", "ok"),
            "location": {"lat": 0, "lng": 0},
            **{k: v for k, v in data.items() if k in ("fillLevel", "binType")},
        })
        if subset_errors:
            return error_response("Validation failed", 422, subset_errors)

    db = get_db()
    if not is_valid_object_id(bin_id):
        return error_response("Invalid bin ID", 400)

    bin_doc = db.bins.find_one({"_id": ObjectId(bin_id)})
    if not bin_doc:
        return error_response("Bin not found", 404)

    updates: dict = {"updatedAt": datetime.now(timezone.utc)}
    allowed = ("fillLevel", "status", "label", "binType", "capacity")
    for field in allowed:
        if field in data:
            updates[field] = data[field]

    # Auto-set status based on fill level using refined thresholds
    if "fillLevel" in updates:
        level = float(updates["fillLevel"])
        # Use the IoT model's threshold logic
        updates["status"] = get_fill_level_status(level)

    # If being emptied (status→normal and fill goes low)
    if updates.get("fillLevel", 100) < 20 and updates.get("status") == "normal":
        updates["lastEmptied"] = datetime.now(timezone.utc)

    db.bins.update_one({"_id": ObjectId(bin_id)}, {"$set": updates})
    updated = db.bins.find_one({"_id": ObjectId(bin_id)})
    return success_response("Bin updated successfully", serialize_bin(updated))


# ── Delete Bin ─────────────────────────────────────────────────────────────────
def delete_bin(bin_id: str):
    """
    DELETE /api/bins/:id
    Requires: JWT + admin
    """
    db = get_db()
    if not is_valid_object_id(bin_id):
        return error_response("Invalid bin ID", 400)

    result = db.bins.delete_one({"_id": ObjectId(bin_id)})
    if result.deleted_count == 0:
        return error_response("Bin not found", 404)

    return success_response("Bin deleted successfully")
