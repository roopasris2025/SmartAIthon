from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.bin_controller import (
    get_bins, get_bin, create_bin, update_bin, delete_bin,
)

bin_bp = Blueprint("bin_bp", __name__)


@bin_bp.route("/", methods=["GET"])
@jwt_required()
def _get_bins():
    return get_bins()


@bin_bp.route("/", methods=["POST"])
@jwt_required()
def _create_bin():
    return create_bin()


@bin_bp.route("/<bin_id>", methods=["GET"])
@jwt_required()
def _get_bin(bin_id):
    return get_bin(bin_id)


@bin_bp.route("/<bin_id>", methods=["PATCH"])
@jwt_required()
def _update_bin(bin_id):
    return update_bin(bin_id)


@bin_bp.route("/<bin_id>", methods=["DELETE"])
@jwt_required()
def _delete_bin(bin_id):
    return delete_bin(bin_id)
