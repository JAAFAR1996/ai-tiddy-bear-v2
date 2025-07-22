from src.domain.models.emergency_models import HealthResponse
from datetime import datetime
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from src.infrastructure.health import (
    HealthStatus,
    get_health_manager,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(tags=["Health"])
