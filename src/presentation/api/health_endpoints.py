from fastapi import APIRouter

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(tags=["Health"])
