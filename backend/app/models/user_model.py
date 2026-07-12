"""
app/models/user_model.py  –  User schema helper functions
Uses PyMongo (dict-based), not an ORM.
"""
from datetime import datetime, timezone
import bcrypt


# ── Schema factory ────────────────────────────────────────────────────────────
def create_user_schema(name: str, email: str, password: str, role: str = "student") -> dict:
    """
    Build and return a new user document ready for insertion into MongoDB.
    Password is hashed before storage.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return {
        "name": name.strip(),
        "email": email.lower().strip(),
        "password": hashed,
        "role": role,          # 'student' | 'admin'
        "points": 0,
        "badges": [],
        "reportsCount": 0,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
        "isActive": True,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def check_password(plain: str, hashed: bytes) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed)


def serialize_user(user: dict) -> dict:
    """
    Convert a MongoDB user document to a safe JSON-serialisable dict.
    Removes sensitive fields (password) and converts ObjectId to string.
    """
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "student"),
        "points": user.get("points", 0),
        "badges": user.get("badges", []),
        "reportsCount": user.get("reportsCount", 0),
        "createdAt": user.get("createdAt", "").isoformat() if user.get("createdAt") else "",
    }
