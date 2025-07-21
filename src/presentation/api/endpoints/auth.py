from src.domain.models.validation_models import LoginRequest
"""API endpoints for authentication and authorization"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.rate_limiter_service import RateLimiterService
from src.infrastructure.security.auth.real_auth_service import (
    ProductionAuthService,
)
from src.presentation.api.decorators.rate_limit import moderate_limit, strict_limit

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
