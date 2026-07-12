"""
app/models/bin_model.py  –  Smart Bin schema helpers
"""
from datetime import datetime, timezone


BIN_STATUSES    = ["normal", "full", "overflow", "maintenance"]
BIN_TYPES       = ["general", "recyclable", "organic", "hazardous"]


def create_bin_schema(
    label: str,
    location: dict,
    bin_type: str = "general",
    capacity: int = 100,
) -> dict:
    """Build and return a new smart bin document."""
    return {
        "label":      label.strip(),
        "location": {
            "lat":     float(location.get("lat", 0)),
            "lng":     float(location.get("lng", 0)),
            "address": location.get("address", ""),
        },
        "binType":    bin_type,   # general | recyclable | organic | hazardous
        "capacity":   capacity,   # percentage (0–100)
        "fillLevel":  0,          # current fill percentage
        "status":     "normal",   # normal | full | overflow | maintenance
        "lastEmptied": None,
        "addedBy":    None,
        "createdAt":  datetime.now(timezone.utc),
        "updatedAt":  datetime.now(timezone.utc),
    }


def serialize_bin(bin_doc: dict) -> dict:
    """Convert a MongoDB bin document to JSON-serialisable dict."""
    return {
        "id":         str(bin_doc["_id"]),
        "label":      bin_doc.get("label", ""),
        "location":   bin_doc.get("location", {}),
        "binType":    bin_doc.get("binType", "general"),
        "capacity":   bin_doc.get("capacity", 100),
        "fillLevel":  bin_doc.get("fillLevel", 0),
        "status":     bin_doc.get("status", "normal"),
        "lastEmptied": bin_doc["lastEmptied"].isoformat() if bin_doc.get("lastEmptied") else None,
        "addedBy":    str(bin_doc["addedBy"]) if bin_doc.get("addedBy") else None,
        "createdAt":  bin_doc["createdAt"].isoformat() if bin_doc.get("createdAt") else "",
        "updatedAt":  bin_doc["updatedAt"].isoformat() if bin_doc.get("updatedAt") else "",
    }
