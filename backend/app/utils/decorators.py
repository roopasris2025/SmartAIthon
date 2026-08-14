"""
app/utils/decorators.py  –  Custom route decorators for role-based access control
"""
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from flask import request
from app.utils.helpers import error_response


def token_required(fn):
    """
    Decorator that verifies a valid JWT token is present.
    Attaches user_id to the request context.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_id = get_jwt_identity()
        # Attach user_id to request context for use in route handlers
        request.user_id = user_id
        request.user_claims = claims
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """
    Decorator that ensures the authenticated user has the 'admin' role.
    Must be used AFTER @token_required or @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return error_response("Admin access required", 403)
        user_id = get_jwt_identity()
        request.user_id = user_id
        request.user_claims = claims
        return fn(*args, **kwargs)
    return wrapper


def worker_required(fn):
    """
    Decorator that ensures the authenticated user has the 'worker' role.
    Must be used AFTER @token_required or @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "worker":
            return error_response("Worker access required", 403)
        user_id = get_jwt_identity()
        request.user_id = user_id
        request.user_claims = claims
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
            user_id = get_jwt_identity()
            request.user_id = user_id
            request.user_claims = claims
            return fn(*args, **kwargs)
        return wrapper
    return decorator
