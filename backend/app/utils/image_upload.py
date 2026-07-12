"""
app/utils/image_upload.py  –  Image handling: Cloudinary or base64 local fallback
"""
import base64
import os
import re
from datetime import datetime

try:
    import cloudinary
    import cloudinary.uploader
    _CLOUDINARY_AVAILABLE = True
except ImportError:
    _CLOUDINARY_AVAILABLE = False


def configure_cloudinary():
    """Initialize Cloudinary from environment variables (call once at startup)."""
    if _CLOUDINARY_AVAILABLE:
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
        )


def upload_image(image_data: str, folder: str = "smartwaste/reports") -> str | None:
    """
    Upload an image and return a URL.

    Accepts:
      - A base64 data URI  (data:image/...;base64,<data>)
      - A regular URL string (passed through as-is)

    Tries Cloudinary first; falls back to returning the base64 string itself.
    """
    if not image_data:
        return None

    # Already a URL → pass through
    if image_data.startswith("http://") or image_data.startswith("https://"):
        return image_data

    # Try Cloudinary upload
    if _CLOUDINARY_AVAILABLE and os.getenv("CLOUDINARY_CLOUD_NAME"):
        try:
            result = cloudinary.uploader.upload(
                image_data,
                folder=folder,
                public_id=f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                overwrite=False,
                resource_type="image",
            )
            return result.get("secure_url")
        except Exception as exc:
            print(f"[WARN] Cloudinary upload failed: {exc}")

    # Fallback: return the base64 data URI directly (store in MongoDB)
    # This is fine for small images; not recommended for production scale.
    return image_data if image_data.startswith("data:image") else None
