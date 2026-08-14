"""
app/routes/worker_routes.py  –  Worker and task management routes
Blueprint for worker and task endpoints.
"""
from flask import Blueprint
from app.controllers.worker_controller import (
    create_worker,
    get_workers,
    get_worker,
    update_worker,
    update_worker_status,
    delete_worker,
)
from app.controllers.task_controller import (
    create_task,
    get_tasks,
    get_task,
    assign_task,
    start_task,
    complete_task_bin,
    get_worker_tasks,
)

worker_bp = Blueprint("worker_routes", __name__)

# ── Worker Management Endpoints ────────────────────────────────────────────
worker_bp.route("/workers", methods=["POST"])(create_worker)
worker_bp.route("/workers", methods=["GET"])(get_workers)
worker_bp.route("/workers/<worker_id>", methods=["GET"])(get_worker)
worker_bp.route("/workers/<worker_id>", methods=["PATCH"])(update_worker)
worker_bp.route("/workers/<worker_id>/status", methods=["PATCH"])(update_worker_status)
worker_bp.route("/workers/<worker_id>", methods=["DELETE"])(delete_worker)

# ── Task Management Endpoints ──────────────────────────────────────────────
worker_bp.route("/tasks", methods=["POST"])(create_task)
worker_bp.route("/tasks", methods=["GET"])(get_tasks)
worker_bp.route("/tasks/<task_id>", methods=["GET"])(get_task)
worker_bp.route("/tasks/<task_id>/assign", methods=["PATCH"])(assign_task)
worker_bp.route("/tasks/<task_id>/start", methods=["PATCH"])(start_task)
worker_bp.route("/tasks/<task_id>/complete", methods=["PATCH"])(complete_task_bin)
worker_bp.route("/workers/<worker_id>/tasks", methods=["GET"])(get_worker_tasks)
