"""
app/controllers/user_controller.py  –  User profile, leaderboard, admin tools
"""
from flask import request
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timezone

from app.utils.helpers import get_db, success_response, error_response, is_valid_object_id, paginate, build_pagination_meta
from app.models.user_model import serialize_user


# ── Leaderboard ───────────────────────────────────────────────────────────────
def get_leaderboard():
    """
    GET /api/users/leaderboard
    Query params: limit (default 10, max 50)
    Returns top users ranked by points (only students).
    """
    db = get_db()
    try:
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except (ValueError, TypeError):
        limit = 10

    top_users = list(
        db.users.find({"role": "student", "isActive": True})
        .sort("points", -1)
        .limit(limit)
    )

    leaderboard = []
    for rank, user in enumerate(top_users, start=1):
        entry = serialize_user(user)
        entry["rank"] = rank
        leaderboard.append(entry)

    return success_response("Leaderboard fetched", leaderboard)


# ── Get All Users (admin) ──────────────────────────────────────────────────────
def get_all_users():
    """
    GET /api/users
    Query params: role, page, limit
    Requires: JWT + admin
    """
    db     = get_db()
    params = request.args
    query: dict = {}

    if params.get("role") and params["role"] in ("student", "admin"):
        query["role"] = params["role"]

    try:
        page  = max(1, int(params.get("page", 1)))
        limit = min(100, max(1, int(params.get("limit", 20))))
    except (ValueError, TypeError):
        page, limit = 1, 20

    skip = (page - 1) * limit
    total = db.users.count_documents(query)
    users = list(db.users.find(query).sort("points", -1).skip(skip).limit(limit))

    return success_response(
        "Users fetched",
        {
            "users": [serialize_user(u) for u in users],
            "pagination": build_pagination_meta(total, page, limit),
        },
    )


# ── Get User By ID ─────────────────────────────────────────────────────────────
def get_user(user_id: str):
    """
    GET /api/users/:id
    Students can only fetch their own profile.
    Admins can fetch any profile.
    """
    db      = get_db()
    claims  = get_jwt()
    caller  = get_jwt_identity()
    role    = claims.get("role", "student")

    if not is_valid_object_id(user_id):
        return error_response("Invalid user ID", 400)

    if role != "admin" and caller != user_id:
        return error_response("Not authorised to view this profile", 403)

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return error_response("User not found", 404)

    return success_response("User fetched", serialize_user(user))


# ── Update Own Profile ─────────────────────────────────────────────────────────
def update_profile():
    """
    PATCH /api/users/me
    Body: { name? }
    Users can update their own name only.
    Requires: JWT
    """
    data    = request.get_json(silent=True) or {}
    db      = get_db()
    user_id = get_jwt_identity()

    updates: dict = {"updatedAt": datetime.now(timezone.utc)}

    if data.get("name", "").strip():
        updates["name"] = data["name"].strip()

    if len(updates) == 1:  # only updatedAt, nothing useful
        return error_response("No updatable fields provided", 400)

    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    updated = db.users.find_one({"_id": ObjectId(user_id)})
    return success_response("Profile updated", serialize_user(updated))


# ── Manually Award Points (admin) ──────────────────────────────────────────────
def award_points(user_id: str):
    """
    POST /api/users/:id/points
    Body: { points, reason? }
    Requires: JWT + admin
    """
    data = request.get_json(silent=True) or {}
    db   = get_db()

    if not is_valid_object_id(user_id):
        return error_response("Invalid user ID", 400)

    try:
        pts = int(data.get("points", 0))
    except (ValueError, TypeError):
        return error_response("'points' must be an integer", 400)

    if pts == 0:
        return error_response("Points value cannot be zero", 400)

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return error_response("User not found", 404)

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"points": pts}, "$set": {"updatedAt": datetime.now(timezone.utc)}},
    )
    updated = db.users.find_one({"_id": ObjectId(user_id)})
    return success_response(
        f"{pts} points awarded to {updated['name']}",
        serialize_user(updated),
    )


# ── Deactivate / Reactivate User (admin) ─────────────────────────────────────
def toggle_user_status(user_id: str):
    """
    PATCH /api/users/:id/status
    Body: { isActive: bool }
    Requires: JWT + admin
    """
    data = request.get_json(silent=True) or {}
    db   = get_db()

    if not is_valid_object_id(user_id):
        return error_response("Invalid user ID", 400)

    is_active = data.get("isActive")
    if is_active is None:
        return error_response("'isActive' field is required", 400)

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return error_response("User not found", 404)

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"isActive": bool(is_active), "updatedAt": datetime.now(timezone.utc)}},
    )
    status_text = "activated" if is_active else "deactivated"
    return success_response(f"User {status_text} successfully")
