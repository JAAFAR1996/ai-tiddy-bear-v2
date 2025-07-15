"""Conftest for voice service tests"""

# Mock classes for voice service tests
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"

class STTProvider(Enum):
    WHISPER = "whisper"
    GOOGLE = "google"

class WhisperModel(Enum):
    BASE = "base"
    SMALL = "small"

@dataclass
class VoiceServiceConfig:
    stt_provider: STTProvider = STTProvider.WHISPER
    audio_format: AudioFormat = AudioFormat.WAV
    whisper_model: WhisperModel = WhisperModel.BASE

@dataclass
class AudioRequest:
    audio_data: bytes
    format: AudioFormat
    child_id: str
    metadata: Dict[str, Any] = None

@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    language: str = "en"
    metadata: Dict[str, Any] = None
