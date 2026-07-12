"""
app/controllers/report_controller.py  –  Waste Report CRUD + status updates
"""
from flask import request
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime, timezone

from app.utils.helpers    import get_db, success_response, error_response, paginate, build_pagination_meta, is_valid_object_id
from app.utils.validators import validate_report, validate_report_update
from app.utils.image_upload import upload_image
from app.models.report_model import (
    create_report_schema, serialize_report,
    STATUS_CLEANED, STATUS_VERIFIED, STATUS_PROGRESS,
)
from config import ActiveConfig


# ── Create Report ─────────────────────────────────────────────────────────────
def create_report():
    """
    POST /api/reports
    Body: { description, location:{lat,lng,address?}, wasteType?, priority?, imageUrl? }
    Requires: JWT (student or admin)
    Awards: POINTS_PER_REPORT points to the reporter
    """
    data = request.get_json(silent=True) or {}
    errors = validate_report(data)
    if errors:
        return error_response("Validation failed", 422, errors)

    db = get_db()
    user_id = get_jwt_identity()

    # Handle image upload (Cloudinary / base64 fallback)
    image_url = upload_image(data.get("imageUrl") or data.get("image"))

    report_doc = create_report_schema(
        user_id=user_id,
        description=data["description"],
        location=data["location"],
        waste_type=data.get("wasteType", "general"),
        image_url=image_url,
        priority=data.get("priority", "medium"),
    )

    result = db.reports.insert_one(report_doc)
    report_doc["_id"] = result.inserted_id

    # Award reporter points
    points = ActiveConfig.POINTS_PER_REPORT
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"points": points, "reportsCount": 1}},
    )
    report_doc["pointsAwarded"] = points

    return success_response("Report created successfully", serialize_report(report_doc), 201)


# ── Get All Reports (with filter + pagination) ────────────────────────────────
def get_reports():
    """
    GET /api/reports
    Query params:
      status  – filter by status
      type    – filter by wasteType
      userId  – filter by createdBy
      page    – page number (default 1)
      limit   – results per page (default 10, max 100)
      from    – ISO date string (reports created after)
      to      – ISO date string (reports created before)
    Requires: JWT
    """
    db = get_db()
    params = request.args
    query: dict = {}

    # Apply filters
    if params.get("status"):
        query["status"] = params["status"]
    if params.get("type"):
        query["wasteType"] = params["type"]
    if params.get("userId") and is_valid_object_id(params["userId"]):
        query["createdBy"] = params["userId"]

    # Date range
    date_filter: dict = {}
    if params.get("from"):
        try:
            date_filter["$gte"] = datetime.fromisoformat(params["from"])
        except ValueError:
            pass
    if params.get("to"):
        try:
            date_filter["$lte"] = datetime.fromisoformat(params["to"])
        except ValueError:
            pass
    if date_filter:
        query["createdAt"] = date_filter

    # Pagination
    try:
        page  = max(1, int(params.get("page", 1)))
        limit = min(100, max(1, int(params.get("limit", 10))))
    except (ValueError, TypeError):
        page, limit = 1, 10

    skip = (page - 1) * limit
    total = db.reports.count_documents(query)
    reports = list(
        db.reports.find(query)
        .sort("createdAt", -1)
        .skip(skip)
        .limit(limit)
    )

    return success_response(
        "Reports fetched",
        {
            "reports": [serialize_report(r) for r in reports],
            "pagination": build_pagination_meta(total, page, limit),
        },
    )


# ── Get Single Report ─────────────────────────────────────────────────────────
def get_report(report_id: str):
    """
    GET /api/reports/:id
    Requires: JWT
    """
    db = get_db()
    if not is_valid_object_id(report_id):
        return error_response("Invalid report ID", 400)

    report = db.reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        return error_response("Report not found", 404)

    return success_response("Report fetched", serialize_report(report))


# ── Update Report Status ──────────────────────────────────────────────────────
def update_report(report_id: str):
    """
    PATCH /api/reports/:id
    Body: { status?, notes? }

    - Admin can change any status.
    - Student can only cancel their own pending report.
    - Awarding extra points when status → verified or → cleaned.
    Requires: JWT
    """
    data = request.get_json(silent=True) or {}
    errors = validate_report_update(data)
    if errors:
        return error_response("Validation failed", 422, errors)

    db = get_db()
    if not is_valid_object_id(report_id):
        return error_response("Invalid report ID", 400)

    report = db.reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        return error_response("Report not found", 404)

    claims  = get_jwt()
    user_id = get_jwt_identity()
    role    = claims.get("role", "student")

    # Permission guard
    if role != "admin" and str(report["createdBy"]) != user_id:
        return error_response("Not authorised to update this report", 403)

    updates: dict = {"updatedAt": datetime.now(timezone.utc)}

    new_status = data.get("status")
    if new_status:
        updates["status"] = new_status

    if data.get("notes") is not None:
        updates["notes"] = data["notes"]

    # If marking cleaned → set timestamp + cleanedBy
    if new_status == STATUS_CLEANED:
        updates["cleanedAt"] = datetime.now(timezone.utc)
        updates["cleanedBy"] = user_id

    # Award extra points on status transitions
    extra_points = 0
    reporter_id  = str(report["createdBy"])

    if new_status == STATUS_VERIFIED and report["status"] != STATUS_VERIFIED:
        extra_points = ActiveConfig.POINTS_PER_VERIFIED

    elif new_status == STATUS_CLEANED and report["status"] != STATUS_CLEANED:
        extra_points = ActiveConfig.POINTS_PER_CLEANED
        updates["pointsAwarded"] = report.get("pointsAwarded", 0) + extra_points

    db.reports.update_one({"_id": ObjectId(report_id)}, {"$set": updates})

    if extra_points > 0:
        db.users.update_one(
            {"_id": ObjectId(reporter_id)},
            {"$inc": {"points": extra_points}},
        )

    updated = db.reports.find_one({"_id": ObjectId(report_id)})
    return success_response("Report updated successfully", serialize_report(updated))


# ── Delete Report (admin only) ────────────────────────────────────────────────
def delete_report(report_id: str):
    """
    DELETE /api/reports/:id
    Requires: JWT + admin role
    """
    db = get_db()
    if not is_valid_object_id(report_id):
        return error_response("Invalid report ID", 400)

    result = db.reports.delete_one({"_id": ObjectId(report_id)})
    if result.deleted_count == 0:
        return error_response("Report not found", 404)

    return success_response("Report deleted successfully")


# ── Report Stats (admin dashboard) ───────────────────────────────────────────
def get_stats():
    """
    GET /api/reports/stats
    Returns aggregate counts for all report statuses.
    Requires: JWT + admin role
    """
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    result = list(db.reports.aggregate(pipeline))
    stats = {item["_id"]: item["count"] for item in result}
    stats["total"] = sum(stats.values())
    return success_response("Stats fetched", stats)
