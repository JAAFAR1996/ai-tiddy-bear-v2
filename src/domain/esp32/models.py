from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

@dataclass
class ESP32SensorReading:
    device_id: UUID
    timestamp: datetime
    temperature: Optional[float] = None
    light_level: Optional[float] = None
    sound_level: Optional[float] = None
    battery_level: Optional[float] = None

@dataclass
class ESP32VoiceCommand:
    device_id: UUID
    timestamp: datetime
    command_text: str
    confidence: float

@dataclass
class ESP32GestureEvent:
    device_id: UUID
    timestamp: datetime
    gesture_type: str
    confidence: float
    axis_data: Optional[List[float]] = None

@dataclass
class ESP32FirmwareUpdateStatus:
    device_id: UUID
    timestamp: datetime
    update_version: str
    status: str  # e.g., 'initiated', 'downloading', 'applying', 'completed', 'failed'
    progress: Optional[float] = None  # 0.0 to 1.0
    error_message: Optional[str] = None

@dataclass
class ESP32DeviceStatus:
    device_id: UUID
    timestamp: datetime
    is_online: bool
    firmware_version: str
    battery_level: float
    last_seen: datetime
    mesh_network_status: Optional[str] = None

@dataclass
class ESP32EdgeAIResult:
    device_id: UUID
    timestamp: datetime
    model_name: str
    result_type: str
    result_value: str
    confidence: Optional[float] = None
    raw_output: Optional[str] = None