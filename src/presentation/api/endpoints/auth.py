"""API endpoints for authentication and authorization"""

from fastapi import APIRouter, Request
from fastapi.security import HTTPBearer

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


async def get_client_ip(request: Request) -> str:
    """Extract client IP for rate limiting."""
    # Check common proxy headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    # Direct IP
    return request.client.host if request.client else "unknown"


# Request/Response Models
