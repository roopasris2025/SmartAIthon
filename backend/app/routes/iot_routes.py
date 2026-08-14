"""
app/routes/iot_routes.py  –  Routes for IoT sensor data ingestion and management
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.iot_controller import (
    receive_sensor_data,
    create_sensor,
    get_sensor,
    update_sensor,
    get_sensor_history,
)

iot_bp = Blueprint("iot_bp", __name__)


# ── Sensor Data Ingestion (No JWT required for IoT devices) ─────────────────────
@iot_bp.route("/sensor-data", methods=["POST"])
def _receive_sensor_data():
    """POST /api/iot/sensor-data - Receive data from IoT devices"""
    return receive_sensor_data()


# ── Sensor Management (Admin only) ──────────────────────────────────────────────
@iot_bp.route("/sensors", methods=["POST"])
@jwt_required()
def _create_sensor():
    """POST /api/iot/sensors - Create a new sensor (admin)"""
    return create_sensor()


@iot_bp.route("/sensors/<sensor_id>", methods=["GET"])
@jwt_required()
def _get_sensor(sensor_id):
    """GET /api/iot/sensors/:id - Get sensor configuration (admin)"""
    return get_sensor(sensor_id)


@iot_bp.route("/sensors/<sensor_id>", methods=["PATCH"])
@jwt_required()
def _update_sensor(sensor_id):
    """PATCH /api/iot/sensors/:id - Update sensor configuration (admin)"""
    return update_sensor(sensor_id)


# ── Sensor History (JWT required) ────────────────────────────────────────────────
@iot_bp.route("/bins/<bin_id>/sensor-history", methods=["GET"])
@jwt_required()
def _get_sensor_history(bin_id):
    """GET /api/iot/bins/:id/sensor-history - Get historical sensor readings"""
    return get_sensor_history(bin_id)
