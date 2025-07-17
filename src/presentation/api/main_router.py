import logging

try:
    from fastapi import APIRouter
    FASTAPI_AVAILABLE = True
except ImportError as e:
    raise ImportError("FastAPI is required for production API deployment. "
        "Install with: pip install fastapi uvicorn") from e

"""Main router for all endpoints"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")

# Import all endpoint routers
from src.presentation.api.endpoints.auth import router as auth_router
from src.presentation.api.endpoints.children import router as children_router
from src.presentation.api.endpoints.conversations import router as conversations_router
from src.presentation.api.middleware.consent_verification import (
    ConsentVerificationMiddleware,
)  # ✅ COPPA middleware

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(children_router)
api_router.include_router(conversations_router)

# Add health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Teddy Bear API",
        "version": "2.0.0",
        "timestamp": "2025-01-01T00:00:00Z",
    }

# Add API info endpoint
@api_router.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "AI Teddy Bear API",
        "version": "2.0.0",
        "description": "Child-safe AI interaction platform",
        "endpoints": {
            "auth": "/api/v1/auth",
            "children": "/api/v1/children",
            "conversations": "/api/v1/conversations",
            "health": "/api/v1/health",
        },
        "features": [
            "COPPA compliant",
            "Real-time safety monitoring",
            "Parental controls",
            "Content filtering",
            "Multilingual support",
        ],
    }

# ✅ COPPA Consent Verification Integration
# ConsentVerificationMiddleware should be applied at the FastAPI app level:
# app.add_middleware(ConsentVerificationMiddleware, consent_required_paths={
#     "/api/v1/process-audio": ["data_collection", "voice_recording"],
#     "/api/v1/children": ["data_collection"],
#     "/api/v1/conversations": ["data_collection", "usage_analytics"],
# })
# This ensures parental consent is verified at ALL child data collection points