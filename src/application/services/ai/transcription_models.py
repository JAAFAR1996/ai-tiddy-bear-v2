"""Defines data models for speech-to-text transcription results.

This module provides the `TranscriptionResult` dataclass, which encapsulates
all relevant information about a transcribed audio segment, including the
text, language, confidence score, provider details, processing times, and
segment-level metadata. These models are crucial for standardizing data
exchange within the transcription pipeline.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TranscriptionResult:
    """Represents the result of a speech-to-text transcription."""

    text: str
    language: str
    confidence: float
    provider: str
    processing_time_ms: int
    audio_duration_ms: int
    segments: list[dict[str, Any]]
    metadata: dict[str, Any]
