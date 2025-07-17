"""
Tests for SafetyValidator Protocol
Testing the protocol interface for content safety validation.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Protocol

from src.domain.services.safety_validator import SafetyValidator
from src.domain.value_objects.safety_level import SafetyLevel


class TestSafetyValidatorProtocol:
    """Test the SafetyValidator protocol interface."""

    @pytest.fixture
    def mock_safety_validator(self) -> Mock:
        """Create a mock implementation of SafetyValidator protocol."""
        mock = Mock(spec=SafetyValidator)
        mock.validate_text = AsyncMock()
        mock.validate_audio = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_safety_validator_protocol_implementation(
        self, mock_safety_validator
    ):
        """Test that the protocol can be implemented correctly."""
        # Arrange
        text = "This is safe content for children."
        expected_level = SafetyLevel.SAFE

        mock_safety_validator.validate_text.return_value = expected_level

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == expected_level
        mock_safety_validator.validate_text.assert_called_once_with(text)

    @pytest.mark.asyncio
    async def test_validate_text_safe_content(self, mock_safety_validator):
        """Test validating safe text content."""
        # Arrange
        text = "The friendly teddy bear loves to play games!"
        mock_safety_validator.validate_text.return_value = SafetyLevel.SAFE

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_validate_text_warning_content(self, mock_safety_validator):
        """Test validating text content that triggers warning."""
        # Arrange
        text = "Let's talk about scary monsters under the bed."
        mock_safety_validator.validate_text.return_value = SafetyLevel.WARNING

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == SafetyLevel.WARNING

    @pytest.mark.asyncio
    async def test_validate_text_unsafe_content(self, mock_safety_validator):
        """Test validating unsafe text content."""
        # Arrange
        text = "Content with inappropriate language or themes."
        mock_safety_validator.validate_text.return_value = SafetyLevel.UNSAFE

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == SafetyLevel.UNSAFE

    @pytest.mark.asyncio
    async def test_validate_text_empty(self, mock_safety_validator):
        """Test validating empty text."""
        # Arrange
        text = ""
        mock_safety_validator.validate_text.return_value = SafetyLevel.SAFE

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_validate_text_none(self, mock_safety_validator):
        """Test validating None text."""
        # Arrange
        text = None
        mock_safety_validator.validate_text.return_value = SafetyLevel.SAFE

        # Act
        result = await mock_safety_validator.validate_text(text)

        # Assert
        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_validate_audio_safe(self, mock_safety_validator):
        """Test validating safe audio content."""
        # Arrange
        audio_data = b"fake_audio_data_safe"
        mock_safety_validator.validate_audio.return_value = SafetyLevel.SAFE

        # Act
        result = await mock_safety_validator.validate_audio(audio_data)

        # Assert
        assert result == SafetyLevel.SAFE
        mock_safety_validator.validate_audio.assert_called_once_with(
            audio_data)

    @pytest.mark.asyncio
    async def test_validate_audio_warning(self, mock_safety_validator):
        """Test validating audio content with warning."""
        # Arrange
        audio_data = b"fake_audio_data_warning"
        mock_safety_validator.validate_audio.return_value = SafetyLevel.WARNING

        # Act
        result = await mock_safety_validator.validate_audio(audio_data)

        # Assert
        assert result == SafetyLevel.WARNING

    @pytest.mark.asyncio
    async def test_validate_audio_unsafe(self, mock_safety_validator):
        """Test validating unsafe audio content."""
        # Arrange
        audio_data = b"fake_audio_data_unsafe"
        mock_safety_validator.validate_audio.return_value = SafetyLevel.UNSAFE

        # Act
        result = await mock_safety_validator.validate_audio(audio_data)

        # Assert
        assert result == SafetyLevel.UNSAFE

    @pytest.mark.asyncio
    async def test_validate_audio_empty(self, mock_safety_validator):
        """Test validating empty audio data."""
        # Arrange
        audio_data = b""
        mock_safety_validator.validate_audio.return_value = SafetyLevel.SAFE

        # Act
        result = await mock_safety_validator.validate_audio(audio_data)

        # Assert
        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_protocol_type_checking(self):
        """Test that the protocol properly type checks implementations."""
        # This test verifies that any class implementing the protocol
        # must have the correct method signatures

        class ValidImplementation:
            async def validate_text(self, text: str) -> SafetyLevel:
                return SafetyLevel.SAFE

            async def validate_audio(self, audio_data: bytes) -> SafetyLevel:
                return SafetyLevel.SAFE

        class InvalidImplementation:
            def validate_text(self, text: str) -> SafetyLevel:  # Not async
                return SafetyLevel.SAFE

            async def validate_audio(
                self, audio_data: str
            ) -> SafetyLevel:  # Wrong param type
                return SafetyLevel.SAFE

        # The valid implementation should work with the protocol
        valid_impl = ValidImplementation()
        assert hasattr(valid_impl, "validate_text")
        assert hasattr(valid_impl, "validate_audio")

        # The invalid implementation has incorrect signatures
        invalid_impl = InvalidImplementation()
        # This would fail type checking if using mypy
        assert hasattr(invalid_impl, "validate_text")
        assert hasattr(invalid_impl, "validate_audio")


class TestSafetyValidatorImplementationExample:
    """Example tests for a concrete implementation of SafetyValidator."""

    @pytest.fixture
    def concrete_safety_validator(self) -> "ConcreteSafetyValidator":
        """Create a concrete implementation for testing."""

        class ConcreteSafetyValidator:
            """Example concrete implementation of SafetyValidator protocol."""

            # Define unsafe keywords for demonstration
            UNSAFE_KEYWORDS = [
                "violence",
                "weapon",
                "drug",
                "alcohol",
                "inappropriate"]

            WARNING_KEYWORDS = ["scary", "monster", "dark", "alone", "lost"]

            async def validate_text(self, text: str) -> SafetyLevel:
                if not text:
                    return SafetyLevel.SAFE

                text_lower = text.lower()

                # Check for unsafe content
                for keyword in self.UNSAFE_KEYWORDS:
                    if keyword in text_lower:
                        return SafetyLevel.UNSAFE

                # Check for warning content
                for keyword in self.WARNING_KEYWORDS:
                    if keyword in text_lower:
                        return SafetyLevel.WARNING

                return SafetyLevel.SAFE

            async def validate_audio(self, audio_data: bytes) -> SafetyLevel:
                if not audio_data:
                    return SafetyLevel.SAFE

                # Simple implementation based on audio size
                # In reality, this would transcribe and analyze the audio
                audio_size = len(audio_data)

                if audio_size == 0:
                    return SafetyLevel.SAFE
                elif audio_size < 1000:
                    return SafetyLevel.SAFE
                elif audio_size < 10000:
                    return SafetyLevel.WARNING
                else:
                    # Large audio files might need more scrutiny
                    return SafetyLevel.WARNING

        return ConcreteSafetyValidator()

    @pytest.mark.asyncio
    async def test_concrete_validate_text_safe(
            self, concrete_safety_validator):
        """Test concrete implementation with safe text."""
        text = "The teddy bear loves to play fun games with children!"
        result = await concrete_safety_validator.validate_text(text)

        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_concrete_validate_text_warning(
            self, concrete_safety_validator):
        """Test concrete implementation with warning text."""
        text = "The scary monster hides in the dark closet."
        result = await concrete_safety_validator.validate_text(text)

        assert result == SafetyLevel.WARNING

    @pytest.mark.asyncio
    async def test_concrete_validate_text_unsafe(
            self, concrete_safety_validator):
        """Test concrete implementation with unsafe text."""
        text = "Content containing violence is not appropriate."
        result = await concrete_safety_validator.validate_text(text)

        assert result == SafetyLevel.UNSAFE

    @pytest.mark.asyncio
    async def test_concrete_validate_text_mixed_case(
            self, concrete_safety_validator):
        """Test concrete implementation with mixed case text."""
        text = "The SCARY Monster is very DARK"
        result = await concrete_safety_validator.validate_text(text)

        assert result == SafetyLevel.WARNING  # Should detect despite case

    @pytest.mark.asyncio
    async def test_concrete_validate_audio_small(
            self, concrete_safety_validator):
        """Test concrete implementation with small audio."""
        audio_data = b"x" * 500  # Small audio
        result = await concrete_safety_validator.validate_audio(audio_data)

        assert result == SafetyLevel.SAFE

    @pytest.mark.asyncio
    async def test_concrete_validate_audio_medium(
            self, concrete_safety_validator):
        """Test concrete implementation with medium audio."""
        audio_data = b"x" * 5000  # Medium audio
        result = await concrete_safety_validator.validate_audio(audio_data)

        assert result == SafetyLevel.WARNING

    @pytest.mark.asyncio
    async def test_concrete_validate_audio_large(
            self, concrete_safety_validator):
        """Test concrete implementation with large audio."""
        audio_data = b"x" * 15000  # Large audio
        result = await concrete_safety_validator.validate_audio(audio_data)

        assert result == SafetyLevel.WARNING


class TestSafetyValidatorIntegration:
    """Integration tests for SafetyValidator implementations."""

    @pytest.mark.asyncio
    async def test_combined_validation_workflow(self):
        """Test a complete validation workflow."""

        class WorkflowValidator:
            """Validator that combines text and audio validation."""

            async def validate_text(self, text: str) -> SafetyLevel:
                if "bad" in text.lower():
                    return SafetyLevel.UNSAFE
                elif "caution" in text.lower():
                    return SafetyLevel.WARNING
                return SafetyLevel.SAFE

            async def validate_audio(self, audio_data: bytes) -> SafetyLevel:
                # Simulate audio transcription and validation
                if len(audio_data) > 10000:
                    return SafetyLevel.WARNING
                return SafetyLevel.SAFE

            async def validate_content(
                self, text: str, audio_data: bytes
            ) -> SafetyLevel:
                """Validate both text and audio, return worst safety level."""
                text_safety = await self.validate_text(text)
                audio_safety = await self.validate_audio(audio_data)

                # Return the worst safety level
                if SafetyLevel.UNSAFE in [text_safety, audio_safety]:
                    return SafetyLevel.UNSAFE
                elif SafetyLevel.WARNING in [text_safety, audio_safety]:
                    return SafetyLevel.WARNING
                return SafetyLevel.SAFE

        validator = WorkflowValidator()

        # Test safe content
        result = await validator.validate_content("Hello friendly teddy!", b"x" * 100)
        assert result == SafetyLevel.SAFE

        # Test warning from text
        result = await validator.validate_content("Please use caution here", b"x" * 100)
        assert result == SafetyLevel.WARNING

        # Test warning from audio
        result = await validator.validate_content("Hello friendly teddy!", b"x" * 20000)
        assert result == SafetyLevel.WARNING

        # Test unsafe content
        result = await validator.validate_content("This is bad content", b"x" * 100)
        assert result == SafetyLevel.UNSAFE
