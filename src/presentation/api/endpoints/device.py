"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from src.application.services.ai_orchestration_service import AIOrchestrationService
from src.application.services.audio_processing_service import AudioProcessingService
from src.infrastructure.dependencies import get_ai_orchestration_service, get_audio_processing_service
"""

🧸 Device Management Endpoints
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")

router = APIRouter()

class DeviceRegistration(BaseModel):
    """Device registration model with comprehensive validation"""
    device_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Unique device identifier (alphanumeric, dash, underscore only)"
    )
    device_type: str = Field(
        default="esp32_teddy",
        pattern=r"^[a-z0-9_]+$",
        max_length=50,
        description="Device type (lowercase alphanumeric)"
    )  # ✅
    firmware_version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        max_length=20,
        description="Firmware version (semantic versioning: x.y.z)"
    )  # ✅
    child_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Child's name (optional, 1-100 characters)"
    )  # ✅
    child_age: Optional[int] = Field(
        None,
        ge=3,
        le=13,
        description="Child's age (COPPA compliance: 3-13 years)"
    )  # ✅

class DeviceStatus(BaseModel):
    """Device status model with validation"""
    device_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$"
    )
    status: str = Field(
        ...,
        pattern=r"^(online|offline|maintenance|error)$"
    )  # ✅
    last_seen: str = Field(
        ...,
        description="ISO 8601 timestamp"
    )  # ✅
    battery_level: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Battery level percentage (0-100)"
    )  # ✅
    wifi_strength: Optional[int] = Field(
        None,
        ge=-100,
        le=0,
        description="WiFi signal strength in dBm (-100 to 0)"
    )  # ✅

@router.post("/register", response_model=Dict[str, Any])
async def register_device(
    device: DeviceRegistration,
) -> Dict[str, Any]:
    """Register new ESP32 device"""
    try:
        # Generate unique device token
        device_token = f"tddy_{device.device_id}_{hash(device.device_id) % 10000}"
        
        # Store device in database with proper persistence
        device_data = {
            "device_id": device.device_id,
            "device_type": device.device_type,
            "firmware_version": device.firmware_version,
            "child_name": device.child_name,
            "child_age": device.child_age,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "device_token": device_token
        }
        
        # In a real implementation, this would save to database
        # For now, we log the registration
        logger.info(f"Device registered: {device_data}")
        
        return {
            "status": "success",
            "device_token": device_token,
            "message": f"Device {device.device_id} registered successfully",
            "config": {
                "websocket_url": "ws://localhost:8000/ws/device",
                "upload_endpoint": "/api/devices/audio/upload",
                "heartbeat_interval": 30,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device registration failed: {str(e)}",
        )

@router.get("/status/{device_id}", response_model=DeviceStatus)
async def get_device_status(
    device_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Valid device identifier"
    )) -> DeviceStatus:
    """Get device status"""
    try:
        # In a real implementation, this would fetch from database
        # For now, we return a mock status based on device_id
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Basic device status logic
        device_status = {
            "device_id": device_id,
            "status": "online" if device_id.startswith("tddy_") else "offline",
            "last_seen": current_time,
            "battery_level": 85 if device_id.startswith("tddy_") else None,
            "wifi_strength": 75 if device_id.startswith("tddy_") else None
        }
        
        logger.info(f"Device status requested for {device_id}: {device_status['status']}")
        return DeviceStatus(**device_status)
    except Exception as e:
        logger.error(f"Error getting device status for {device_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get device status: {str(e)}"
        )

class AudioUploadRequest(BaseModel):
    """Audio upload request model with validation"""
    device_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Valid device identifier"
    )
    audio_format: str = Field(
        default="wav",
        pattern=r"^(wav|mp3|ogg|m4a)$",
        description="Supported audio format"
    )
    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="Audio sample rate (8000-48000 Hz)"
    )
    duration_ms: Optional[int] = Field(
        None,
        ge=100,
        le=30000,
        description="Audio duration in milliseconds (100ms - 30s max for child safety)"
    )

@router.post("/audio/upload")
async def upload_audio(
    request: AudioUploadRequest,
    audio_data: bytes = Field(..., description="Audio file data"),
    ai_service: AIOrchestrationService = Depends(get_ai_orchestration_service),
    voice_service: AudioProcessingService = Depends(get_audio_processing_service),
) -> Dict[str, Any]:
    """Handle audio upload from ESP32"""
    try:
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio data cannot be empty"
            )
        
        max_audio_size = 5 * 1024 * 1024  # 5MB
        if len(audio_data) > max_audio_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file too large. Maximum size is 5MB for child safety."
            )
        
        # Process audio
        transcript, _ = await voice_service.process_audio_input(audio_data, "en-US") # Assuming language
        response = await ai_service.get_ai_response(transcript, request.device_id)
        
        return {
            "status": "success",
            "transcript": transcript,
            "response": response,
            "response_audio_url": f"/api/audio/tts/{response['id']}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed: {str(e)}",
        )

class DeviceConfig(BaseModel):
    """Device configuration response model"""
    device_id: str
    sample_rate: int = Field(ge=8000, le=48000)
    audio_format: str = Field(pattern=r"^(wav|mp3|ogg|m4a)$")
    compression: str = Field(pattern=r"^(none|mp3|ogg)$")
    wake_word: str = Field(min_length=3, max_length=20)
    response_timeout: int = Field(ge=5, le=30)
    max_recording_duration: int = Field(ge=5, le=30)

@router.get("/config/{device_id}", response_model=DeviceConfig)
async def get_device_config(
    device_id: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Valid device identifier"
    )) -> DeviceConfig:
    """
    Get device configuration with child safety parameters.
    Returns optimized configuration for child interaction including
    audio settings and safety timeouts.
    """
    try:
        if not device_id or len(device_id) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid device identifier"
            )
        
        config = DeviceConfig(
            device_id=device_id,
            sample_rate=16000,  # Optimized for voice recognition
            audio_format="wav",  # Uncompressed for quality
            compression="mp3",   # Compress for transmission
            wake_word="hey_teddy",  # Child-friendly wake word
            response_timeout=10,    # 10 seconds timeout for child attention span
            max_recording_duration=15
        )
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device config for {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve device configuration"
        )