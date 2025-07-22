"""ChatGPT endpoints router - simplified version without DI container."""

from fastapi import APIRouter
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/chatgpt", tags=["chatgpt"])


@router.get("/status")
async def get_chatgpt_status():
    """Get ChatGPT service status."""
    return {"status": "available", "service": "chatgpt"}


@router.post("/chat")
async def chat_endpoint():
    """Simple chat endpoint placeholder."""
    return {"message": "Chat functionality available"}
