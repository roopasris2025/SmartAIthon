from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.user_controller import (
    get_leaderboard, get_all_users, get_user,
    update_profile, award_points, toggle_user_status,
)

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def _leaderboard():
    return get_leaderboard()


@user_bp.route("/", methods=["GET"])
@jwt_required()
def _all_users():
    return get_all_users()


@user_bp.route("/me", methods=["PATCH"])
@jwt_required()
def _update_profile():
    return update_profile()


@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def _get_user(user_id):
    return get_user(user_id)


@user_bp.route("/<user_id>/points", methods=["POST"])
@jwt_required()
def _award_points(user_id):
    return award_points(user_id)


@user_bp.route("/<user_id>/status", methods=["PATCH"])
@jwt_required()
def _toggle_status(user_id):
    return toggle_user_status(user_id)
