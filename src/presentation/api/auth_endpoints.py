"""Auth endpoints router - simplified version without DI container."""

from fastapi import APIRouter
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status")
async def get_auth_status():
    """Get authentication service status."""
    return {"status": "available", "service": "auth"}


@router.post("/login")
async def login_endpoint():
    """Simple login endpoint placeholder."""
    return {"message": "Login functionality available"}


@router.post("/logout")
async def logout_endpoint():
    """Simple logout endpoint placeholder."""
    return {"message": "Logout functionality available"}
