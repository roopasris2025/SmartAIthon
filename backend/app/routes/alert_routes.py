"""
app/routes/alert_routes.py  –  Alert management routes
Blueprint for alert endpoints.
"""
from flask import Blueprint
from app.controllers.alert_controller import (
    get_alerts,
    get_alert,
    acknowledge_alert,
    resolve_alert,
    get_bin_alert_history,
)

alert_bp = Blueprint("alert_routes", __name__)

# ── Alert Management Endpoints ─────────────────────────────────────────────
alert_bp.route("/alerts", methods=["GET"])(get_alerts)
alert_bp.route("/alerts/<alert_id>", methods=["GET"])(get_alert)
alert_bp.route("/alerts/<alert_id>/acknowledge", methods=["PATCH"])(acknowledge_alert)
alert_bp.route("/alerts/<alert_id>/resolve", methods=["PATCH"])(resolve_alert)
alert_bp.route("/bins/<bin_id>/alerts", methods=["GET"])(get_bin_alert_history)
