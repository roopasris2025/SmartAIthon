"""
app/utils/decorators.py  –  Custom route decorators for role-based access control
"""
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from app.utils.helpers import error_response


def admin_required(fn):
    """
    Decorator that ensures the authenticated user has the 'admin' role.
    Must be used AFTER @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response("Admin access required", 403)
        return fn(*args, **kwargs)
    return wrapper


def student_or_admin_required(fn):
    """
    Decorator that verifies JWT is present (student or admin can access).
    This is essentially an alias for @jwt_required but can be extended.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper


def roles_required(*roles):
    """
    Flexible role decorator — pass any number of allowed roles.
    Usage: @roles_required('admin', 'moderator')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return error_response(
                    f"Access denied. Required roles: {', '.join(roles)}", 403
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
