"""
app/utils/helpers.py  –  Shared utility functions used across controllers
"""
from flask import current_app, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import re


# ── Standard API response builders ───────────────────────────────────────────
def success_response(message: str, data=None, status_code: int = 200):
    """Return a standardised JSON success response."""
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error_response(message: str, status_code: int = 400, errors=None):
    """Return a standardised JSON error response."""
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status_code


# ── ObjectId helpers ──────────────────────────────────────────────────────────
def is_valid_object_id(oid: str) -> bool:
    """Return True if the string is a valid MongoDB ObjectId."""
    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


def parse_object_id(oid: str):
    """Parse string → ObjectId.  Returns None on failure."""
    try:
        return ObjectId(oid)
    except (InvalidId, TypeError):
        return None


# ── DB accessor ───────────────────────────────────────────────────────────────
def get_db():
    """Return the PyMongo database attached to the current app."""
    return current_app.db


# ── Pagination helpers ────────────────────────────────────────────────────────
def paginate(query_params: dict) -> tuple[int, int]:
    """
    Extract page and limit from query parameters.
    Returns (skip, limit) tuple for MongoDB queries.
    """
    try:
        page  = max(1, int(query_params.get("page",  1)))
        limit = min(100, max(1, int(query_params.get("limit", 10))))
    except (ValueError, TypeError):
        page, limit = 1, 10
    return (page - 1) * limit, limit


def build_pagination_meta(total: int, page: int, limit: int) -> dict:
    """Build pagination metadata for API responses."""
    return {
        "total":      total,
        "page":       page,
        "limit":      limit,
        "totalPages": -(-total // limit),  # ceiling division
        "hasNext":    page * limit < total,
        "hasPrev":    page > 1,
    }


# ── Validation helpers ────────────────────────────────────────────────────────
def is_valid_email(email: str) -> bool:
    """Simple RFC-ish email format check."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)
