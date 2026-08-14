"""
app/controllers/task_controller.py  –  Task management API endpoints
Handles collection task creation, assignment, and completion tracking.
"""
from datetime import datetime, timezone
from flask import request, jsonify
from bson import ObjectId
from pymongo import DESCENDING

from app.utils.helpers import get_db, error_response, validate_objectid
from app.models.worker_model import (
    create_task_schema,
    serialize_task,
    get_task_completion_percentage,
    TASK_STATUSES,
    TASK_PRIORITIES,
    TASK_STATUS_PENDING,
    TASK_STATUS_ASSIGNED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    WORKER_STATUS_BUSY,
    WORKER_STATUS_AVAILABLE,
)
from app.utils.decorators import token_required, admin_required


# ═════════════════════════════════════════════════════════════════════════════
# 1. POST /tasks  –  Create collection task
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def create_task():
    """
    Create a new collection task.
    
    Request Body:
        - binIds (required): List of bin IDs to collect
        - assignedTo (optional): Worker ID
        - priority (optional): Priority level (low, medium, high, critical)
        - description (optional): Task notes
        - dueDate (optional): Target completion date (ISO format)
    
    Returns:
        {"success": True, "task": {...}}
    """
    try:
        data = request.get_json() or {}
        bin_ids = data.get("binIds", [])
        
        if not bin_ids or not isinstance(bin_ids, list):
            return jsonify({"success": False, "error": "binIds must be a non-empty list"}), 400
        
        # Validate bin IDs
        db = get_db()
        valid_bin_ids = []
        for bid in bin_ids:
            if validate_objectid(bid):
                bin_doc = db.bins.find_one({"_id": ObjectId(bid)})
                if bin_doc:
                    valid_bin_ids.append(ObjectId(bid))
        
        if not valid_bin_ids:
            return jsonify({"success": False, "error": "No valid bins found"}), 400
        
        # Validate worker if provided
        assigned_to = data.get("assignedTo")
        if assigned_to:
            if not validate_objectid(assigned_to):
                return jsonify({"success": False, "error": "Invalid worker ID"}), 400
            worker = db.workers.find_one({"_id": ObjectId(assigned_to)})
            if not worker:
                return jsonify({"success": False, "error": "Worker not found"}), 404
        
        # Validate priority
        priority = data.get("priority", "medium").strip().lower()
        if priority not in TASK_PRIORITIES:
            return jsonify({"success": False, "error": "Invalid priority"}), 400
        
        # Parse due date if provided
        due_date = None
        if "dueDate" in data:
            try:
                due_date = datetime.fromisoformat(data["dueDate"].replace("Z", "+00:00"))
            except:
                return jsonify({"success": False, "error": "Invalid due date format"}), 400
        
        # Create task
        task = create_task_schema(
            bin_ids=valid_bin_ids,
            assigned_to=ObjectId(assigned_to) if assigned_to else None,
            priority=priority,
            description=data.get("description", "").strip(),
            due_date=due_date,
        )
        task["createdBy"] = ObjectId(request.user_id)
        
        result = db.tasks.insert_one(task)
        task["_id"] = result.inserted_id
        
        # If assigned, update worker status
        if assigned_to:
            db.workers.update_one(
                {"_id": ObjectId(assigned_to)},
                {
                    "$set": {"currentTaskId": result.inserted_id, "status": WORKER_STATUS_BUSY},
                    "$inc": {"totalTasksAssigned": 1}
                }
            )
        
        return jsonify({
            "success": True,
            "task": serialize_task(task),
            "message": f"Task created with {len(valid_bin_ids)} bin(s)"
        }), 201
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 2. GET /tasks  –  Get all tasks with filtering
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def get_tasks():
    """
    Retrieve tasks with optional filtering.
    
    Query Parameters:
        - status: Filter by status
        - priority: Filter by priority
        - assignedTo: Filter by worker
        - limit: Number to return (default: 50)
        - skip: Pagination offset
    
    Returns:
        {"success": True, "tasks": [...], "total": N}
    """
    try:
        db = get_db()
        filters = {}
        
        status = request.args.get("status", "").strip()
        if status:
            if status not in TASK_STATUSES:
                return jsonify({"success": False, "error": "Invalid status"}), 400
            filters["status"] = status
        
        priority = request.args.get("priority", "").strip()
        if priority:
            if priority not in TASK_PRIORITIES:
                return jsonify({"success": False, "error": "Invalid priority"}), 400
            filters["priority"] = priority
        
        assigned_to = request.args.get("assignedTo", "").strip()
        if assigned_to:
            if not validate_objectid(assigned_to):
                return jsonify({"success": False, "error": "Invalid worker ID"}), 400
            filters["assignedTo"] = ObjectId(assigned_to)
        
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        
        tasks = list(
            db.tasks.find(filters)
            .sort("createdAt", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        total = db.tasks.count_documents(filters)
        
        return jsonify({
            "success": True,
            "tasks": [serialize_task(t) for t in tasks],
            "total": total,
            "limit": limit,
            "skip": skip,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 3. GET /tasks/:id  –  Get specific task
# ═════════════════════════════════════════════════════════════════════════════

@token_required
def get_task(task_id):
    """
    Retrieve a specific task with full details.
    
    Path Parameters:
        - task_id: Task ID
    
    Returns:
        {"success": True, "task": {...}, "completionPercentage": N}
    """
    try:
        if not validate_objectid(task_id):
            return jsonify({"success": False, "error": "Invalid task ID"}), 400
        
        db = get_db()
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        
        return jsonify({
            "success": True,
            "task": serialize_task(task),
            "completionPercentage": get_task_completion_percentage(task),
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 4. PATCH /tasks/:id/assign  –  Assign task to worker
# ═════════════════════════════════════════════════════════════════════════════

@token_required
@admin_required
def assign_task(task_id):
    """
    Assign a task to a worker.
    
    Path Parameters:
        - task_id: Task ID
    
    Request Body:
        - workerId (required): Worker ID
    
    Returns:
        {"success": True, "task": {...}}
    """
    try:
        if not validate_objectid(task_id):
            return jsonify({"success": False, "error": "Invalid task ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        worker_id = data.get("workerId", "").strip()
        
        if not worker_id:
            return jsonify({"success": False, "error": "workerId is required"}), 400
        
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        # Verify task exists
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        
        # Verify worker exists
        worker = db.workers.find_one({"_id": ObjectId(worker_id)})
        if not worker:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        # Update task
        result = db.tasks.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "assignedTo": ObjectId(worker_id),
                    "status": TASK_STATUS_ASSIGNED,
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )
        
        # Update worker
        db.workers.update_one(
            {"_id": ObjectId(worker_id)},
            {
                "$set": {"currentTaskId": ObjectId(task_id), "status": WORKER_STATUS_BUSY},
                "$inc": {"totalTasksAssigned": 1}
            }
        )
        
        return jsonify({
            "success": True,
            "task": serialize_task(result),
            "message": f"Task assigned to worker {worker.get('name')}"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 5. PATCH /tasks/:id/start  –  Worker starts task
# ═════════════════════════════════════════════════════════════════════════════

@token_required
def start_task(task_id):
    """
    Mark task as in progress (worker action).
    
    Path Parameters:
        - task_id: Task ID
    
    Returns:
        {"success": True, "task": {...}}
    """
    try:
        if not validate_objectid(task_id):
            return jsonify({"success": False, "error": "Invalid task ID"}), 400
        
        db = get_db()
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        
        if task["status"] not in [TASK_STATUS_ASSIGNED, TASK_STATUS_IN_PROGRESS]:
            return jsonify({
                "success": False,
                "error": f"Cannot start task with status '{task['status']}'"
            }), 400
        
        result = db.tasks.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "status": TASK_STATUS_IN_PROGRESS,
                    "startedAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc),
                }
            },
            return_document=True,
        )
        
        return jsonify({
            "success": True,
            "task": serialize_task(result),
            "message": "Task started"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 6. PATCH /tasks/:id/complete  –  Mark bins as collected
# ═════════════════════════════════════════════════════════════════════════════

@token_required
def complete_task_bin(task_id):
    """
    Mark a bin as collected in a task.
    
    Path Parameters:
        - task_id: Task ID
    
    Request Body:
        - binId (required): Bin ID that was collected
    
    Returns:
        {"success": True, "task": {...}, "completionPercentage": N}
    """
    try:
        if not validate_objectid(task_id):
            return jsonify({"success": False, "error": "Invalid task ID"}), 400
        
        db = get_db()
        data = request.get_json() or {}
        bin_id = data.get("binId", "").strip()
        
        if not bin_id:
            return jsonify({"success": False, "error": "binId is required"}), 400
        
        if not validate_objectid(bin_id):
            return jsonify({"success": False, "error": "Invalid bin ID"}), 400
        
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"success": False, "error": "Task not found"}), 404
        
        if ObjectId(bin_id) not in [ObjectId(bid) for bid in task["binIds"]]:
            return jsonify({"success": False, "error": "Bin not in this task"}), 400
        
        # Add to completed bins if not already there
        if ObjectId(bin_id) not in task.get("completedBins", []):
            result = db.tasks.find_one_and_update(
                {"_id": ObjectId(task_id)},
                {
                    "$addToSet": {"completedBins": ObjectId(bin_id)},
                    "$set": {"updatedAt": datetime.now(timezone.utc)},
                },
                return_document=True,
            )
        else:
            result = task
        
        # Check if task is complete
        if len(result["completedBins"]) == len(result["binIds"]):
            result = db.tasks.find_one_and_update(
                {"_id": ObjectId(task_id)},
                {
                    "$set": {
                        "status": TASK_STATUS_COMPLETED,
                        "completedAt": datetime.now(timezone.utc),
                        "updatedAt": datetime.now(timezone.utc),
                    }
                },
                return_document=True,
            )
            
            # Update worker stats
            if result.get("assignedTo"):
                worker = db.workers.find_one({"_id": result["assignedTo"]})
                if worker:
                    completed = worker.get("totalTasksCompleted", 0) + 1
                    db.workers.update_one(
                        {"_id": result["assignedTo"]},
                        {
                            "$set": {
                                "totalTasksCompleted": completed,
                                "currentTaskId": None,
                                "status": WORKER_STATUS_AVAILABLE,
                            }
                        }
                    )
        
        return jsonify({
            "success": True,
            "task": serialize_task(result),
            "completionPercentage": get_task_completion_percentage(result),
            "message": "Bin marked as collected"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ═════════════════════════════════════════════════════════════════════════════
# 7. GET /workers/:id/tasks  –  Get tasks for a specific worker
# ═════════════════════════════════════════════════════════════════════════════

@token_required
def get_worker_tasks(worker_id):
    """
    Retrieve all tasks assigned to a worker.
    
    Path Parameters:
        - worker_id: Worker ID
    
    Query Parameters:
        - status: Filter by status
        - limit: Number to return (default: 50)
    
    Returns:
        {"success": True, "tasks": [...], "total": N}
    """
    try:
        if not validate_objectid(worker_id):
            return jsonify({"success": False, "error": "Invalid worker ID"}), 400
        
        db = get_db()
        
        # Verify worker exists
        worker = db.workers.find_one({"_id": ObjectId(worker_id)})
        if not worker:
            return jsonify({"success": False, "error": "Worker not found"}), 404
        
        filters = {"assignedTo": ObjectId(worker_id)}
        
        status = request.args.get("status", "").strip()
        if status:
            if status not in TASK_STATUSES:
                return jsonify({"success": False, "error": "Invalid status"}), 400
            filters["status"] = status
        
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        
        tasks = list(
            db.tasks.find(filters)
            .sort("createdAt", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        total = db.tasks.count_documents(filters)
        
        return jsonify({
            "success": True,
            "worker": {
                "id": str(worker["_id"]),
                "name": worker.get("name", ""),
                "status": worker.get("status", ""),
            },
            "tasks": [serialize_task(t) for t in tasks],
            "total": total,
            "limit": limit,
            "skip": skip,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
