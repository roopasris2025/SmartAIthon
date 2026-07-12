"""
config.py  –  Centralised configuration loaded from .env
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # ── MongoDB ────────────────────────────────────────────
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/smartwaste_db")
    DB_NAME: str = os.getenv("DB_NAME", "smartwaste_db")

    # ── JWT ────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    )

    # ── Cloudinary (optional) ──────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # ── CORS ───────────────────────────────────────────────
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ── Points System ──────────────────────────────────────
    POINTS_PER_REPORT: int = int(os.getenv("POINTS_PER_REPORT", 10))
    POINTS_PER_VERIFIED: int = int(os.getenv("POINTS_PER_VERIFIED", 25))
    POINTS_PER_CLEANED: int = int(os.getenv("POINTS_PER_CLEANED", 50))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

ActiveConfig = config_map.get(os.getenv("FLASK_ENV", "development"), DevelopmentConfig)
