"""Authentication and authorization services."""

from .real_auth_service import get_current_user, get_current_parent
from .token_service import TokenService

# Note: JWTAuth requires fastapi-users and proper SQLAlchemy setup
try:
    from .jwt_auth import JWTAuth
    __all__ = [
        "JWTAuth",
        "get_current_user", 
        "get_current_parent",
        "TokenService",
    ]
except ImportError:
    # If jwt_auth fails to import, continue without it
    __all__ = [
        "get_current_user", 
        "get_current_parent",
        "TokenService",
    ]