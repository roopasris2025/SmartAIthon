from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.report_controller import (
    create_report, get_reports, get_report,
    update_report, delete_report, get_stats,
)

report_bp = Blueprint("report_bp", __name__)


@report_bp.route("/", methods=["POST"])
@jwt_required()
def _create_report():
    return create_report()


@report_bp.route("/", methods=["GET"])
@jwt_required()
def _get_reports():
    return get_reports()


@report_bp.route("/stats", methods=["GET"])
@jwt_required()
def _stats():
    return get_stats()


@report_bp.route("/<report_id>", methods=["GET"])
@jwt_required()
def _get_report(report_id):
    return get_report(report_id)


@report_bp.route("/<report_id>", methods=["PATCH"])
@jwt_required()
def _update_report(report_id):
    return update_report(report_id)


@report_bp.route("/<report_id>", methods=["DELETE"])
@jwt_required()
def _delete_report(report_id):
    return delete_report(report_id)
