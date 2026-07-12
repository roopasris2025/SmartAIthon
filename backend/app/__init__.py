"""
app/__init__.py  –  Application Factory
Creates and configures the Flask app, registers blueprints, middleware, and extensions.
"""
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from config import ActiveConfig

# ── Shared extensions (initialised later in factory) ─────────────────────────
jwt = JWTManager()
mongo_client: MongoClient | None = None
db = None  # PyMongo Database object


def create_app(config_class=ActiveConfig) -> Flask:
    """Application factory – creates a fully configured Flask instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS(
        app,
        origins=[config_class.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
        supports_credentials=True,
    )

    # ── JWT ──────────────────────────────────────────────────────────────────
    jwt.init_app(app)

    # ── MongoDB connection ────────────────────────────────────────────────────
    global mongo_client, db
    mongo_client = MongoClient(config_class.MONGO_URI)
    db = mongo_client[config_class.DB_NAME]
    app.db = db  # attach to app context

    # Create indexes for performance
    _create_indexes(db)

    # ── Register Blueprints ───────────────────────────────────────────────────
    from app.routes.auth_routes import auth_bp
    from app.routes.report_routes import report_bp
    from app.routes.bin_routes import bin_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(auth_bp,   url_prefix="/api/auth")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(bin_bp,    url_prefix="/api/bins")
    app.register_blueprint(user_bp,   url_prefix="/api/users")

    # ── JWT error handlers ────────────────────────────────────────────────────
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"success": False, "message": f"Unauthorized: {reason}"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"success": False, "message": f"Invalid token: {reason}"}), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired"}), 401

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({"success": False, "message": "Internal server error", "error": str(err)}), 500

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"success": True, "message": "SmartWaste API is running 🌱", "version": "1.0.0"})

    return app


def _create_indexes(database) -> None:
    """Create MongoDB indexes for performance and data integrity."""
    database.users.create_index("email", unique=True)
    database.reports.create_index("createdBy")
    database.reports.create_index("status")
    database.reports.create_index("createdAt")
    database.bins.create_index([("location.lat", 1), ("location.lng", 1)])
