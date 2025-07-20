"""Test cases for AudioSession entity."""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from src.domain.entities.audio_session import AudioSession


class TestAudioSession:
    """Test suite for AudioSession entity."""

    def test_create_new_audio_session(self):
        """Test creating a new audio session with factory method."""
        child_id = uuid4()
        audio_path = "/path/to/audio/file.wav"

        session = AudioSession.create_new(child_id, audio_path)

        assert isinstance(session.id, UUID)
        assert session.child_id == child_id
        assert session.audio_data_path == audio_path
        assert session.transcription == ""
        assert session.processed is False
        assert isinstance(session.start_time, datetime)
        assert isinstance(session.end_time, datetime)
        assert session.start_time == session.end_time

    def test_mark_processed(self):
        """Test marking an audio session as processed."""
        child_id = uuid4()
        audio_path = "/path/to/audio/file.wav"
        session = AudioSession.create_new(child_id, audio_path)

        # Store original times
        original_start = session.start_time
        original_end = session.end_time

        # Wait a tiny bit to ensure time difference
        import time

        time.sleep(0.01)

        # Mark as processed
        transcription_text = "Hello, how are you today?"
        session.mark_processed(transcription_text)

        assert session.transcription == transcription_text
        assert session.processed is True
        assert session.start_time == original_start  # Start time should not change
        assert session.end_time > original_end  # End time should be updated

    def test_direct_initialization(self):
        """Test direct initialization of AudioSession."""
        session_id = uuid4()
        child_id = uuid4()
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=5)
        audio_path = "/path/to/audio.wav"
        transcription = "Test transcription"

        session = AudioSession(
            id=session_id,
            child_id=child_id,
            start_time=start_time,
            end_time=end_time,
            audio_data_path=audio_path,
            transcription=transcription,
            processed=True,
        )

        assert session.id == session_id
        assert session.child_id == child_id
        assert session.start_time == start_time
        assert session.end_time == end_time
        assert session.audio_data_path == audio_path
        assert session.transcription == transcription
        assert session.processed is True

    def test_multiple_sessions_unique_ids(self):
        """Test that multiple sessions have unique IDs."""
        child_id = uuid4()
        sessions = [
            AudioSession.create_new(child_id, f"/path/audio_{i}.wav") for i in range(10)
        ]

        session_ids = [session.id for session in sessions]
        assert len(set(session_ids)) == len(session_ids)  # All IDs should be unique

    def test_empty_transcription_not_processed(self):
        """Test that new session starts with empty transcription and not processed."""
        session = AudioSession.create_new(uuid4(), "/audio.wav")

        assert session.transcription == ""
        assert session.processed is False

    def test_mark_processed_with_empty_transcription(self):
        """Test marking as processed with empty transcription."""
        session = AudioSession.create_new(uuid4(), "/audio.wav")

        session.mark_processed("")

        assert session.transcription == ""
        assert session.processed is True

    def test_mark_processed_updates_only_necessary_fields(self):
        """Test that mark_processed only updates transcription, processed, and end_time."""
        session = AudioSession.create_new(uuid4(), "/audio.wav")

        # Store all original values
        original_id = session.id
        original_child_id = session.child_id
        original_start_time = session.start_time
        original_audio_path = session.audio_data_path

        session.mark_processed("New transcription")

        # These should not change
        assert session.id == original_id
        assert session.child_id == original_child_id
        assert session.start_time == original_start_time
        assert session.audio_data_path == original_audio_path

    def test_session_duration_calculation(self):
        """Test calculating session duration from start and end times."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=3, seconds=30)

        session = AudioSession(
            id=uuid4(),
            child_id=uuid4(),
            start_time=start_time,
            end_time=end_time,
            audio_data_path="/audio.wav",
            transcription="",
            processed=False,
        )

        duration = session.end_time - session.start_time
        assert duration.total_seconds() == 210  # 3 minutes 30 seconds

    def test_audio_session_with_long_path(self):
        """Test audio session with very long file path."""
        long_path = "/very/long/path/" + "subdir/" * 50 + "audio_file.wav"
        session = AudioSession.create_new(uuid4(), long_path)

        assert session.audio_data_path == long_path
        assert len(session.audio_data_path) > 500

    def test_audio_session_with_special_characters(self):
        """Test audio session with special characters in path."""
        special_path = "/path/with/special/chars/audio_文件_αρχείο_файл.wav"
        session = AudioSession.create_new(uuid4(), special_path)

        assert session.audio_data_path == special_path

    def test_mark_processed_idempotent(self):
        """Test that marking as processed multiple times works correctly."""
        session = AudioSession.create_new(uuid4(), "/audio.wav")

        # First processing
        session.mark_processed("First transcription")
        first_end_time = session.end_time

        # Wait a bit
        import time

        time.sleep(0.01)

        # Second processing
        session.mark_processed("Second transcription")

        assert session.transcription == "Second transcription"
        assert session.processed is True
        assert session.end_time > first_end_time
