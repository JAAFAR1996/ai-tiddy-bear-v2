"""
Defines the AudioSession entity for managing audio recording sessions.

This entity represents a single audio recording session, capturing details
such as the associated child, start and end times, path to the audio data,
transcription, and processing status. It provides methods for creating new
sessions and marking them as processed.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class AudioSession:
    """Represents an audio recording session."""

    id: UUID
    child_id: UUID
    start_time: datetime
    end_time: datetime
    audio_data_path: str
    transcription: str
    processed: bool

    @classmethod
    def create_new(cls, child_id: UUID,
                   audio_data_path: str) -> "AudioSession":
        """
        Creates a new audio session.

        Args:
            child_id: The ID of the child associated with the session.
            audio_data_path: The path where the audio data is stored.

        Returns:
            A new AudioSession instance.
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            child_id=child_id,
            start_time=now,
            end_time=now,
            audio_data_path=audio_data_path,
            transcription="",
            processed=False,
        )

    def mark_processed(self, transcription: str) -> None:
        """
        Marks the audio session as processed and updates its transcription.

        Args:
            transcription: The transcribed text of the audio session.
        """
        self.transcription = transcription
        self.processed = True
        self.end_time = datetime.utcnow()
