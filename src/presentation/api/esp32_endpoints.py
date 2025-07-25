from datetime import datetime

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from src.application.services.ai.ai_orchestration_service import AIOrchestrationService
from src.application.services.audio.transcription_service import TranscriptionService
from src.application.services.audio.tts_service import TTSService
from src.domain.models.user import User
from src.infrastructure.di.container import Container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.real_database_service import DatabaseService

from .middleware.consent_verification import require_consent

logger = get_logger(__name__, component="api")

router = APIRouter()
security = HTTPBearer()


async def get_current_user_esp32(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Verify user authentication for ESP32 endpoints"""
    try:
        from src.infrastructure.security.auth.real_auth_service import (
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

        return User(
            user_id=payload["sub"],
            email=payload["email"],
            role=payload.get("role", "parent"),
            is_active=payload.get("is_active", True),
            permissions=payload.get("permissions", []),
        )
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
    current_user: User = Depends(get_current_user_esp32),
    ai_orchestration_service: AIOrchestrationService = Depends(
        Provide[Container.ai_orchestration_service]
    ),
    database_service: DatabaseService = Depends(Provide[Container.database_service]),
    transcription_service: TranscriptionService = Depends(
        Provide[Container.transcription_service]
    ),
    tts_service: TTSService = Depends(Provide[Container.tts_service]),
):
    """Process audio from ESP32 device"""
    try:
        from src.infrastructure.security.child_safety import get_consent_manager

        consent_manager = get_consent_manager()

        # Verify consent for voice recording and data collection
        parent_id = current_user.user_id
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

        # جلب سجل المحادثات من قاعدة البيانات
        conversation_history = await database_service.get_conversation_history(
            request.child_id
        )

        # جلب voice_id من ملف الطفل أو إعداداته
        voice_id = child.get("voice_id", "default")

        # تحويل الصوت إلى نص باستخدام خدمة حقيقية
        transcribed_text = await transcription_service.transcribe(
            audio_base64=request.audio_data, language=request.language
        )

        # Generate AI response
        ai_response = await ai_orchestration_service.get_ai_response(
            child_id=request.child_id,
            conversation_history=conversation_history,
            current_input=transcribed_text,
            voice_id=voice_id,
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

        # تحويل الرد النصي إلى صوت باستخدام خدمة TTS حقيقية
        audio_response = await tts_service.synthesize(
            text=ai_response.response_text, voice_id=voice_id, language=request.language
        )

        return AudioResponse(
            response_text=ai_response.response_text,
            audio_response=audio_response,  # Base64 encoded audio from TTS
            emotion=ai_response.emotion,
            safe=ai_response.safe,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e!s}")


# Device Status Endpoint
@router.post("/device-status")
async def update_device_status(
    request: DeviceStatusRequest,
    current_user: User = Depends(get_current_user_esp32),
    database_service: DatabaseService = Depends(Provide[Container.database_service]),
):
    """Update ESP32 device status"""
    try:
        await database_service.update_device_status(
            device_id=request.device_id,
            status=request.status,
            battery_level=request.battery_level,
            updated_at=request.timestamp,
            user_id=current_user.user_id,
        )
        return {
            "status": "ok",
            "device_id": request.device_id,
            "received_at": datetime.now().isoformat(),
            "battery_level": request.battery_level,
            "next_check_in": 300,  # 5 minutes
        }
    except Exception as e:
        logger.error(f"Error updating device status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error updating device status: {e!s}"
        )


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
    current_user: User = Depends(get_current_user_esp32),
    database_service: DatabaseService = Depends(Provide[Container.database_service]),
):
    """Get device configuration"""
    try:
        config = await database_service.get_device_config(device_id)
        if not config:
            raise HTTPException(status_code=404, detail="Device config not found")
        return config
    except Exception as e:
        logger.error(f"Error getting device config: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting device config: {e!s}"
        )
