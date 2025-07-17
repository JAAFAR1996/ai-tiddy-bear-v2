from uuid import UUID
import base64
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.application.dto.ai_response import AIResponse
from src.application.dto.esp32_request import ESP32Request
from src.application.use_cases.process_esp32_audio import ProcessESP32AudioUseCase
router = APIRouter()
from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

@router.post("/esp32/audio")
async def process_esp32_audio_http(request: ESP32Request, process_audio_use_case: ProcessESP32AudioUseCase) -> AIResponse:
    # Decode base64 audio data
    audio_data_bytes = base64.b64decode(request.audio_data)
    request.audio_data = audio_data_bytes  # Update the request with bytes
    response = await process_audio_use_case.execute(request)
    return response

@router.websocket("/ws/esp32/audio/{child_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    child_id: UUID,
    process_audio_use_case: ProcessESP32AudioUseCase,
) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # Assuming data is raw audio bytes, not base64 encoded for websocket
            request = ESP32Request(
                child_id=child_id, audio_data=data, language_code="en-US"
            )
            response = await process_audio_use_case.execute(request)
            await websocket.send_json(response.dict())
    except WebSocketDisconnect:
        logger.info(f"Client {child_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {child_id}: {e}")