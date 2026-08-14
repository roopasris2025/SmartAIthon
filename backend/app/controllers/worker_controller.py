"""
app/controllers/worker_controller.py  –  Worker management API endpoints
Handles worker CRUD operations and status management.
"""
from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId
from pymongo import DESCENDING

from app.utils.helpers import get_db, error_response, validate_objectid
from app.models.worker_model import (
    create_worker_schema,
    serialize_worker,
    WORKER_STATUSES,
)
from app.utils.decorators import token_required, admin_required


# ═════════════════════════════════════════════════════════════════════════════
# 1. POST /workers  –  Create a new worker
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def create_worker():
    """
    Create a new collection worker.
    
    Request Body:
        - name (required): Worker's full name
        - phoneNumber (required): Phone number
        - assignedZone (optional): Zone assignment
        - availability (optional): Boolean
    
    Returns:
        {"success": True, "worker": {...}}
    """
    try:
        data = request.get_json() or {}
        
        # Validation
        name = data.get("name", "").strip()
        phone = data.get("phoneNumber", "").strip()
        
        if not name:
            return jsonify({"success": False, "error": "Name is required"}), 400
        if not phone:
            return jsonify({"success": False, "error": "Phone number is required"}), 400
        
        # Check if phone number already exists
        db = get_db()
        existing = db.workers.find_one({"phoneNumber": phone})
        if existing:
            return jsonify({"success": False, "error": "Phone number already registered"}), 400
        
        zone = data.get("assignedZone", "").strip()
        availability = data.get("availability", True)
        
        # Create worker
        worker = create_worker_schema(
            name=name,
            phone_number=phone,
            assigned_zone=zone,
            availability=availability,
        )
        
        result = db.workers.insert_one(worker)
        worker["_id"] = result.inserted_id
        
        return jsonify({
            "success": True,
            "worker": serialize_worker(worker),
            "message": f"Worker '{name}' created successfully"
        }), 201
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 2. GET /workers  –  Get all workers
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def get_workers():
    """
    Retrieve all workers with optional filtering.
    
    Query Parameters:
        - status: Filter by status (available, busy, offline, on_leave)
        - zone: Filter by assigned zone
        - active: Filter by active status (true/false)
        - limit: Number to return (default: 50)
        - skip: Pagination offset
    
    Returns:
        {"success": True, "workers": [...], "total": N}
    """
    try:
        db = get_db()
        filters = {}
        
        # Status filter
        status = request.args.get("status", "").strip()
        if status:
            if status not in WORKER_STATUSES:
                return jsonify({"success": False, "error": "Invalid status"}), 400
            filters["status"] = status
        
        # Zone filter
        zone = request.args.get("zone", "").strip()
        if zone:
            filters["assignedZone"] = zone
        
        # Active filter
        active = request.args.get("active", "").strip().lower()
        if active in ["true", "false"]:
            filters["isActive"] = active == "true"
        
        # Pagination
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        
        workers = list(
            db.workers.find(filters)
            .sort("createdAt", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        total = db.workers.count_documents(filters)
        
        return jsonify({
            "success": True,
            "workers": [serialize_worker(w) for w in workers],
            "total": total,
            "limit": limit,
            "skip": skip,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 3. GET /workers/:id  –  Get specific worker
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def get_worker(worker_id):
    """
    Retrieve a specific worker's details.
    
    Path Parameters:
        - worker_id: Worker ID
    
    Returns:
        {"success": True, "worker": {...}}
    """
    try:
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        db = get_db()
        worker = db.workers.find_one({"_id": ObjectId(worker_id)})
        
        if not worker:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        return jsonify({"success": True, "worker": serialize_worker(worker)})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 4. PATCH /workers/:id  –  Update worker details
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def update_worker(worker_id):
    """
    Update worker information.
    
    Path Parameters:
        - worker_id: Worker ID
    
    Request Body:
        - name: Full name
        - phoneNumber: Phone number
        - assignedZone: Zone assignment
        - availability: Availability status
        - status: Worker status
        - isActive: Active status
    
    Returns:
        {"success": True, "worker": {...}}
    """
    try:
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        
        # Verify worker exists
        worker = db.workers.find_one({"_id": ObjectId(worker_id)})
        if not worker:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        # Prepare update
        update = {"updatedAt": datetime.now(timezone.utc)}
        
        if "name" in data:
            update["name"] = data.get("name", "").strip()
        
        if "phoneNumber" in data:
            phone = data.get("phoneNumber", "").strip()
            # Check if phone already used by another worker
            existing = db.workers.find_one({
                "_id": {"$ne": ObjectId(worker_id)},
                "phoneNumber": phone
            })
            if existing:
                return jsonify({"success": False, "error": "Phone number already in use"}), 400
            update["phoneNumber"] = phone
        
        if "assignedZone" in data:
            update["assignedZone"] = data.get("assignedZone", "").strip()
        
        if "availability" in data:
            update["availability"] = bool(data.get("availability"))
        
        if "status" in data:
            status = data.get("status", "").strip()
            if status not in WORKER_STATUSES:
                return jsonify({"success": False, "error": "Invalid status"}), 400
            update["status"] = status
        
        if "isActive" in data:
            update["isActive"] = bool(data.get("isActive"))
        
        result = db.workers.find_one_and_update(
            {"_id": ObjectId(worker_id)},
            {"$set": update},
            return_document=True,
        )
        
        return jsonify({
            "success": True,
            "worker": serialize_worker(result),
            "message": "Worker updated successfully"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 5. PATCH /workers/:id/status  –  Update worker status
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def update_worker_status(worker_id):
    """
    Update worker availability status.
    
    Path Parameters:
        - worker_id: Worker ID
    
    Request Body:
        - status: New status (available, busy, offline, on_leave)
    
    Returns:
        {"success": True, "worker": {...}}
    """
    try:
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        status = data.get("status", "").strip()
        
        if not status:
            return jsonify({"success": False, "error": "Status is required"}), 400
        
        if status not in WORKER_STATUSES:
            return jsonify({"success": False, "error": "Invalid status"}), 400
        
        result = db.workers.find_one_and_update(
            {"_id": ObjectId(worker_id)},
            {
                "$set": {
                    "status": status,
                    "lastActiveAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )
        
        if not result:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        return jsonify({
            "success": True,
            "worker": serialize_worker(result),
            "message": f"Worker status updated to '{status}'"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 6. DELETE /workers/:id  –  Deactivate worker (soft delete)
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def delete_worker(worker_id):
    """
    Deactivate a worker (soft delete - preserves history).
    
    Path Parameters:
        - worker_id: Worker ID
    
    Returns:
        {"success": True, "message": "..."}
    """
    try:
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        db = get_db()
        
        result = db.workers.find_one_and_update(
            {"_id": ObjectId(worker_id)},
            {
                "$set": {
                    "isActive": False,
                    "status": "offline",
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )
        
        if not result:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        return jsonify({
            "success": True,
            "message": f"Worker '{result.get('name')}' has been deactivated"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
