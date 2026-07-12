"""
app/controllers/auth_controller.py  –  Registration & Login logic
"""
from flask import request
from flask_jwt_extended import create_access_token
from pymongo.errors import DuplicateKeyError

from app.utils.helpers  import get_db, success_response, error_response
from app.utils.validators import validate_register, validate_login
from app.models.user_model import create_user_schema, check_password, serialize_user


def register():
    """
    POST /api/auth/register
    Body: { name, email, password, role? }
    """
    data = request.get_json(silent=True) or {}

    # ── Validate ──────────────────────────────────────────────────────────────
    errors = validate_register(data)
    if errors:
        return error_response("Validation failed", 422, errors)

    db = get_db()

    # ── Check duplicate email ─────────────────────────────────────────────────
    if db.users.find_one({"email": data["email"].lower().strip()}):
        return error_response("Email already registered", 409)

    # ── Create document ───────────────────────────────────────────────────────
    user_doc = create_user_schema(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "student"),
    )

    try:
        result = db.users.insert_one(user_doc)
    except DuplicateKeyError:
        return error_response("Email already registered", 409)

    user_doc["_id"] = result.inserted_id

    # ── Issue JWT with role claim ─────────────────────────────────────────────
    token = create_access_token(
        identity=str(result.inserted_id),
        additional_claims={"role": user_doc["role"], "name": user_doc["name"]},
    )

    return success_response(
        "Account created successfully",
        {"user": serialize_user(user_doc), "token": token},
        201,
    )


def login():
    """
    POST /api/auth/login
    Body: { email, password }
    """
    data = request.get_json(silent=True) or {}

    # ── Validate ──────────────────────────────────────────────────────────────
    errors = validate_login(data)
    if errors:
        return error_response("Validation failed", 422, errors)

    db = get_db()

    # ── Find user ─────────────────────────────────────────────────────────────
    user = db.users.find_one({"email": data["email"].lower().strip()})
    if not user:
        return error_response("Invalid email or password", 401)

    # ── Check password ────────────────────────────────────────────────────────
    if not check_password(data["password"], user["password"]):
        return error_response("Invalid email or password", 401)

    # ── Check active ──────────────────────────────────────────────────────────
    if not user.get("isActive", True):
        return error_response("Account is deactivated", 403)

    # ── Issue JWT ─────────────────────────────────────────────────────────────
    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": user["role"], "name": user["name"]},
    )

    return success_response(
        "Login successful",
        {"user": serialize_user(user), "token": token},
    )


def get_me():
    """
    GET /api/auth/me
    Returns the currently authenticated user's profile.
    Requires: JWT
    """
    from flask_jwt_extended import get_jwt_identity
    from bson import ObjectId

    db = get_db()
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return error_response("User not found", 404)

    return success_response("Profile fetched", serialize_user(user))
