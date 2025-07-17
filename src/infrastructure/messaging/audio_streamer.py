from src.infrastructure.logging_config import get_logger
from typing import AsyncGenerator
import logging
from fastapi import WebSocket

logger = get_logger(__name__, component="infrastructure")

class AudioStreamer:
    def __init__(self) -> None:
        self.connections: dict[str, WebSocket] = {}
    
    async def connect(self, child_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[child_id] = websocket
    
    def disconnect(self, child_id: str) -> None:
        del self.connections[child_id]
    
    async def stream_audio_to_child(self, child_id: str, audio_data: bytes) -> None:
        if child_id in self.connections:
            await self.connections[child_id].send_bytes(audio_data)
    
    async def receive_audio_from_child(self, child_id: str) -> AsyncGenerator[bytes, None]:
        if child_id in self.connections:
            websocket = self.connections[child_id]
            try:
                while True:
                    data = await websocket.receive_bytes()
                    yield data
            except Exception as e:
                logger.error(f"Error receiving audio from {child_id}: {e}")