from src.domain.models.validation_models import LoginRequest, LoginResponse
from datetime import datetime
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from src.infrastructure.di.container import Container
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# Request/Response Models
