from datetime import datetime
from typing import Any

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from src.application.services.ai_orchestration_service import (
    AIOrchestrationService,
)
from src.infrastructure.di.container import Container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.real_database_service import (
    DatabaseService,
)

from .middleware.consent_verification import require_consent

logger = get_logger(__name__, component="api")

router = APIRouter()
security = HTTPBearer()


async def get_current_user_esp32(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Verify user authentication for ESP32 endpoints"""
    try:
        from src.infrastructure.security.real_auth_service import (
            create_auth_service,
        )

        auth_service = create_auth_service()
        token = credentials.credentials
        payload = await auth_service.verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": payload["sub"],
            "email": payload["email"],
            "role": payload.get("role", "parent"),
        }
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Pydantic models for request/response
class AudioRequest(BaseModel):
    child_id: str = Field(..., min_length=1, max_length=255)
    audio_data: str = Field(
        ..., min_length=10
    )  # Base64 encoded audio, min length for non-empty
    language: str = Field("en", pattern="^[a-z]{2}$")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AudioResponse(BaseModel):
    response_text: str
    audio_response: str  # Base64 encoded audio response
    emotion: str
    safe: bool
    conversation_id: str
    timestamp: str


class DeviceStatusRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., pattern="^(online|offline|charging|low_battery)$")
    battery_level: int = Field(..., ge=0, le=100)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ESP32 Audio Processing Endpoint
@require_consent("data_collection", "voice_recording")
@router.post("/process-audio", response_model=AudioResponse)
async def process_audio(
    request: AudioRequest,
    current_user: dict[str, Any] = Depends(get_current_user_esp32),
    ai_orchestration_service: AIOrchestrationService = Depends(
        Provide[Container.ai_orchestration_service]
    ),
    database_service: DatabaseService = Depends(Provide[Container.database_service]),
):
    """Process audio from ESP32 device"""
    try:
        # Verify parental consent before processing child data
        from src.infrastructure.security.coppa import get_consent_manager

        consent_manager = get_consent_manager()

        # Verify consent for voice recording and data collection
        parent_id = current_user["user_id"]
        for consent_type in ["data_collection", "voice_recording"]:
            has_consent = await consent_manager.verify_parental_consent(
                parent_id=parent_id,
                child_id=request.child_id,
                consent_type=consent_type,
            )
            if not has_consent:
                raise HTTPException(
                    status_code=403,
                    detail=f"Parental consent required for {consent_type}",
                )

        # Get child profile
        child = await database_service.get_child(request.child_id)
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")

        # Simulate audio transcription (in real implementation, this would use Whisper)
        transcribed_text = "Hello, I want to hear a story about animals"

        # Generate AI response
        ai_response = await ai_orchestration_service.get_ai_response(
            child_id=request.child_id,
            conversation_history=[],  # Placeholder, should be retrieved from DB
            current_input=transcribed_text,
            voice_id="default",  # Placeholder
            child_preferences=child["preferences"],
        )

        # Log safety event if needed
        if not ai_response.safe:
            await database_service.record_safety_event(
                request.child_id,
                "content_filter",
                ai_response.safety_analysis.severity,
                "Inappropriate content detected and filtered",
                {"original_text": transcribed_text},
            )

        # Save conversation
        conversation_id = await database_service.save_conversation(
            request.child_id,
            [
                {"role": "user", "content": transcribed_text},
                {"role": "assistant", "content": ai_response.response_text},
            ],
            {
                "emotion": ai_response.emotion,
                "safety_check": ai_response.safety_analysis.model_dump(),
                "response_type": ai_response.response_type,
            },
        )

        return AudioResponse(
            response_text=ai_response.response_text,
            audio_response="base64_encoded_audio_response",  # Would be actual TTS output
            emotion=ai_response.emotion,
            safe=ai_response.safe,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e!s}")


# Device Status Endpoint
@router.post("/device-status")
async def update_device_status(
    request: DeviceStatusRequest,
    current_user: dict[str, Any] = Depends(get_current_user_esp32),
):
    """Update ESP32 device status"""
    # In a real implementation, this would update device status in database
    return {
        "status": "ok",
        "device_id": request.device_id,
        "received_at": datetime.now().isoformat(),
        "battery_level": request.battery_level,
        "next_check_in": 300,  # 5 minutes
    }


# Health Check Endpoint
@router.get("/health")
async def health_check():
    """Check ESP32 service health"""
    return {
        "status": "healthy",
        "service": "ESP32 API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
    }


# Configuration Endpoint
@router.get("/config/{device_id}")
async def get_device_config(
    device_id: str,
    current_user: dict[str, Any] = Depends(get_current_user_esp32),
):
    """Get device configuration"""
    return {
        "device_id": device_id,
        "audio_quality": "high",
        "language": "en",
        "wake_word": "teddy",
        "volume": 70,
        "brightness": 80,
        "safety_mode": "strict",
        "check_in_interval": 300,
    }
