from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ESP32SensorReadingDTO(BaseModel):
    device_id: UUID
    timestamp: datetime
    temperature: Optional[float] = None
    light_level: Optional[float] = None
    sound_level: Optional[float] = None
    battery_level: Optional[float] = None

class ESP32VoiceCommandDTO(BaseModel):
    device_id: UUID
    timestamp: datetime
    command_text: str
    confidence: float

class ESP32GestureEventDTO(BaseModel):
    device_id: UUID
    timestamp: datetime
    gesture_type: str
    confidence: float
    axis_data: Optional[List[float]] = None

class ESP32FirmwareUpdateStatusDTO(BaseModel):
    device_id: UUID
    timestamp: datetime
    update_version: str
    status: str
    progress: Optional[float] = None
    error_message: Optional[str] = None

class ESP32DeviceStatusDTO(BaseModel):
    device_id: UUID
    timestamp: datetime
    is_online: bool
    firmware_version: str
    battery_level: float
    last_seen: datetime
    mesh_network_status: Optional[str] = None

class ESP32EdgeAIResultDTO(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    device_id: UUID
    timestamp: datetime
    model_name: str
    result_type: str
    result_value: str
    confidence: Optional[float] = None
    raw_output: Optional[str] = None