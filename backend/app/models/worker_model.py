"""
app/models/worker_model.py  –  Worker and Task schemas
Handles worker profiles, roles, and collection task management.
"""
from datetime import datetime, timezone
from typing import Optional

# ── Worker Status ──────────────────────────────────────────────────────────
WORKER_STATUS_AVAILABLE = "available"
WORKER_STATUS_BUSY = "busy"
WORKER_STATUS_OFFLINE = "offline"
WORKER_STATUS_ON_LEAVE = "on_leave"

WORKER_STATUSES = [
    WORKER_STATUS_AVAILABLE,
    WORKER_STATUS_BUSY,
    WORKER_STATUS_OFFLINE,
    WORKER_STATUS_ON_LEAVE,
]

# ── Task Status ────────────────────────────────────────────────────────────
TASK_STATUS_PENDING = "pending"
TASK_STATUS_ASSIGNED = "assigned"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_CANCELLED = "cancelled"

TASK_STATUSES = [
    TASK_STATUS_PENDING,
    TASK_STATUS_ASSIGNED,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_CANCELLED,
]

# ── Task Priority ─────────────────────────────────────────────────────────
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

TASK_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL]


def create_worker_schema(
    name: str,
    phone_number: str,
    assigned_zone: str = "",
    availability: bool = True,
) -> dict:
    """
    Create a new worker document.
    
    Args:
        name: Worker's full name
        phone_number: Worker's phone number
        assigned_zone: Zone/region assigned to this worker (e.g., "Zone A", "Downtown")
        availability: Whether worker is available
    
    Returns:
        Worker document ready for insertion
    """
    return {
        "name": name,
        "phoneNumber": phone_number,
        "assignedZone": assigned_zone,
        "availability": availability,
        "status": WORKER_STATUS_AVAILABLE,
        "currentTaskId": None,
        "totalTasksCompleted": 0,
        "totalTasksAssigned": 0,
        "averageCompletionTime": 0,  # in minutes
        "lastActiveAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
        "isActive": True,
    }


def create_task_schema(
    bin_ids: list,
    assigned_to: Optional[str] = None,
    priority: str = PRIORITY_MEDIUM,
    description: str = "",
    due_date: Optional[datetime] = None,
) -> dict:
    """
    Create a new collection task.
    
    Args:
        bin_ids: List of bin IDs to collect
        assigned_to: Worker ID if assigned
        priority: Task priority (low, medium, high, critical)
        description: Task description/notes
        due_date: Target completion date
    
    Returns:
        Task document ready for insertion
    """
    return {
        "binIds": bin_ids,
        "assignedTo": assigned_to,
        "status": TASK_STATUS_PENDING if not assigned_to else TASK_STATUS_ASSIGNED,
        "priority": priority,
        "description": description,
        "dueDate": due_date,
        "startedAt": None,
        "completedAt": None,
        "completedBins": [],  # List of bin IDs actually collected
        "notes": "",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
        "createdBy": None,  # Admin who created the task
    }


def serialize_worker(worker_doc: dict) -> dict:
    """Convert MongoDB worker document to JSON-serialisable dict."""
    return {
        "id": str(worker_doc["_id"]),
        "name": worker_doc.get("name", ""),
        "phoneNumber": worker_doc.get("phoneNumber", ""),
        "assignedZone": worker_doc.get("assignedZone", ""),
        "availability": worker_doc.get("availability", True),
        "status": worker_doc.get("status", ""),
        "currentTaskId": worker_doc.get("currentTaskId"),
        "totalTasksCompleted": worker_doc.get("totalTasksCompleted", 0),
        "totalTasksAssigned": worker_doc.get("totalTasksAssigned", 0),
        "averageCompletionTime": worker_doc.get("averageCompletionTime", 0),
        "lastActiveAt": worker_doc["lastActiveAt"].isoformat() if worker_doc.get("lastActiveAt") else "",
        "createdAt": worker_doc["createdAt"].isoformat() if worker_doc.get("createdAt") else "",
        "updatedAt": worker_doc["updatedAt"].isoformat() if worker_doc.get("updatedAt") else "",
        "isActive": worker_doc.get("isActive", True),
    }


def serialize_task(task_doc: dict) -> dict:
    """Convert MongoDB task document to JSON-serialisable dict."""
    return {
        "id": str(task_doc["_id"]),
        "binIds": [str(bid) for bid in task_doc.get("binIds", [])],
        "assignedTo": task_doc.get("assignedTo"),
        "status": task_doc.get("status", ""),
        "priority": task_doc.get("priority", ""),
        "description": task_doc.get("description", ""),
        "dueDate": task_doc["dueDate"].isoformat() if task_doc.get("dueDate") else None,
        "startedAt": task_doc["startedAt"].isoformat() if task_doc.get("startedAt") else None,
        "completedAt": task_doc["completedAt"].isoformat() if task_doc.get("completedAt") else None,
        "completedBins": [str(bid) for bid in task_doc.get("completedBins", [])],
        "notes": task_doc.get("notes", ""),
        "createdAt": task_doc["createdAt"].isoformat() if task_doc.get("createdAt") else "",
        "updatedAt": task_doc["updatedAt"].isoformat() if task_doc.get("updatedAt") else "",
        "createdBy": task_doc.get("createdBy"),
    }


def get_task_completion_percentage(task_doc: dict) -> int:
    """
    Calculate task completion percentage.
    
    Args:
        task_doc: Task document
    
    Returns:
        Percentage (0-100)
    """
    total_bins = len(task_doc.get("binIds", []))
    if total_bins == 0:
        return 0
    
    completed_bins = len(task_doc.get("completedBins", []))
    return int((completed_bins / total_bins) * 100)
