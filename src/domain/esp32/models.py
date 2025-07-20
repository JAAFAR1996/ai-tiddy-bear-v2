from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ESP32SensorReading:
    device_id: UUID
    timestamp: datetime
    temperature: float | None = None
    light_level: float | None = None
    sound_level: float | None = None
    battery_level: float | None = None


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
    axis_data: list[float] | None = None


@dataclass
class ESP32FirmwareUpdateStatus:
    device_id: UUID
    timestamp: datetime
    update_version: str
    status: str  # e.g., 'initiated', 'downloading', 'applying', 'completed', 'failed'
    progress: float | None = None  # 0.0 to 1.0
    error_message: str | None = None


@dataclass
class ESP32DeviceStatus:
    device_id: UUID
    timestamp: datetime
    is_online: bool
    firmware_version: str
    battery_level: float
    last_seen: datetime
    mesh_network_status: str | None = None


@dataclass
class ESP32EdgeAIResult:
    device_id: UUID
    timestamp: datetime
    model_name: str
    result_type: str
    result_value: str
    confidence: float | None = None
    raw_output: str | None = None
