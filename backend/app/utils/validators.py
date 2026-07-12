"""
app/utils/validators.py  –  Input validation functions for request bodies
"""
from app.utils.helpers import is_valid_email
from app.models.report_model import WASTE_TYPES, VALID_STATUSES
from app.models.bin_model import BIN_TYPES


def validate_register(data: dict) -> list[str]:
    """Validate registration payload. Returns list of error strings."""
    errors = []
    if not data.get("name", "").strip():
        errors.append("Name is required")
    if not data.get("email", "").strip():
        errors.append("Email is required")
    elif not is_valid_email(data["email"]):
        errors.append("Invalid email format")
    if not data.get("password", ""):
        errors.append("Password is required")
    elif len(data["password"]) < 6:
        errors.append("Password must be at least 6 characters")
    if data.get("role") and data["role"] not in ("student", "admin"):
        errors.append("Role must be 'student' or 'admin'")
    return errors


def validate_login(data: dict) -> list[str]:
    """Validate login payload."""
    errors = []
    if not data.get("email", "").strip():
        errors.append("Email is required")
    elif not is_valid_email(data["email"]):
        errors.append("Invalid email format")
    if not data.get("password", ""):
        errors.append("Password is required")
    return errors


def validate_report(data: dict) -> list[str]:
    """Validate waste report creation payload."""
    errors = []
    if not data.get("description", "").strip():
        errors.append("Description is required")
    loc = data.get("location", {})
    if not isinstance(loc, dict):
        errors.append("Location must be an object with lat/lng")
    else:
        try:
            float(loc.get("lat", ""))
            float(loc.get("lng", ""))
        except (TypeError, ValueError):
            errors.append("Location must have valid numeric lat and lng")
    if data.get("wasteType") and data["wasteType"] not in WASTE_TYPES:
        errors.append(f"wasteType must be one of: {', '.join(WASTE_TYPES)}")
    if data.get("priority") and data["priority"] not in ("low", "medium", "high"):
        errors.append("Priority must be 'low', 'medium', or 'high'")
    return errors


def validate_report_update(data: dict) -> list[str]:
    """Validate report PATCH payload."""
    errors = []
    if "status" in data and data["status"] not in VALID_STATUSES:
        errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")
    return errors


def validate_bin(data: dict) -> list[str]:
    """Validate bin creation payload."""
    errors = []
    if not data.get("label", "").strip():
        errors.append("Bin label is required")
    loc = data.get("location", {})
    if not isinstance(loc, dict):
        errors.append("Location must be an object with lat/lng")
    else:
        try:
            float(loc.get("lat", ""))
            float(loc.get("lng", ""))
        except (TypeError, ValueError):
            errors.append("Location must have valid numeric lat and lng")
    if data.get("binType") and data["binType"] not in BIN_TYPES:
        errors.append(f"binType must be one of: {', '.join(BIN_TYPES)}")
    if "fillLevel" in data:
        try:
            level = float(data["fillLevel"])
            if not (0 <= level <= 100):
                errors.append("fillLevel must be between 0 and 100")
        except (TypeError, ValueError):
            errors.append("fillLevel must be a number")
    return errors
