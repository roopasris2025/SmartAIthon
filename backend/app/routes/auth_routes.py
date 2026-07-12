from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.auth_controller import register, login, get_me

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/register", methods=["POST"])
def _register():
    return register()


@auth_bp.route("/login", methods=["POST"])
def _login():
    return login()


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def _me():
    return get_me()
