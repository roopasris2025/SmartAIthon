"""
app/models/report_model.py  –  Waste Report schema helpers
"""
from datetime import datetime, timezone


# ── Status constants ──────────────────────────────────────────────────────────
STATUS_PENDING  = "pending"
STATUS_VERIFIED = "verified"
STATUS_PROGRESS = "in_progress"
STATUS_CLEANED  = "cleaned"
VALID_STATUSES  = [STATUS_PENDING, STATUS_VERIFIED, STATUS_PROGRESS, STATUS_CLEANED]

# ── Waste type constants ───────────────────────────────────────────────────────
WASTE_TYPES = ["general", "recyclable", "organic", "hazardous", "e-waste"]


def create_report_schema(
    user_id: str,
    description: str,
    location: dict,
    waste_type: str = "general",
    image_url: str | None = None,
    priority: str = "medium",
) -> dict:
    """Build and return a new waste report document."""
    return {
        "description": description.strip(),
        "location": {
            "lat":     float(location.get("lat", 0)),
            "lng":     float(location.get("lng", 0)),
            "address": location.get("address", ""),
        },
        "wasteType": waste_type,
        "imageUrl":  image_url,
        "status":    STATUS_PENDING,
        "priority":  priority,          # low | medium | high
        "createdBy": user_id,
        "cleanedBy": None,
        "pointsAwarded": 0,
        "notes": "",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
        "cleanedAt": None,
    }


def serialize_report(report: dict) -> dict:
    """Convert a MongoDB report document to JSON-serialisable dict."""
    return {
        "id":          str(report["_id"]),
        "description": report.get("description", ""),
        "location":    report.get("location", {}),
        "wasteType":   report.get("wasteType", "general"),
        "imageUrl":    report.get("imageUrl"),
        "status":      report.get("status", STATUS_PENDING),
        "priority":    report.get("priority", "medium"),
        "createdBy":   str(report.get("createdBy", "")),
        "cleanedBy":   str(report["cleanedBy"]) if report.get("cleanedBy") else None,
        "pointsAwarded": report.get("pointsAwarded", 0),
        "notes":       report.get("notes", ""),
        "createdAt":   report["createdAt"].isoformat() if report.get("createdAt") else "",
        "updatedAt":   report["updatedAt"].isoformat() if report.get("updatedAt") else "",
        "cleanedAt":   report["cleanedAt"].isoformat() if report.get("cleanedAt") else None,
    }
