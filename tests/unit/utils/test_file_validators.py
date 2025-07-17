"""
Comprehensive test suite for utils/file_validators.py

This test file validates all aspects of the file validation functionality
including MIME type validation, file size limits, error handling, and security.
"""

import pytest
import io
from unittest.mock import Mock, patch
from fastapi import UploadFile, HTTPException, status

from src.utils.file_validators import (
    validate_audio_file,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE,
)


class TestFileValidators:
    """Test suite for file validation utilities."""

    @pytest.fixture
    def mock_upload_file(self):
        """Create a mock UploadFile for testing."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_audio.wav"
        mock_file.size = 1024 * 1024  # 1MB
        mock_file.file = io.BytesIO(b"fake audio content")
        return mock_file

    @pytest.fixture
    def large_mock_upload_file(self):
        """Create a mock UploadFile that exceeds size limit."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "large_audio.wav"
        mock_file.size = MAX_FILE_SIZE + 1  # Exceed limit
        mock_file.file = io.BytesIO(b"fake large audio content")
        return mock_file

    @pytest.fixture
    def mock_file_content(self):
        """Mock file content for magic detection."""
        return b"fake audio file content for magic detection"

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_success(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test successful audio file validation."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.file.read.return_value = b"fake audio content"

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None  # Function returns None on success
        mock_upload_file.file.read.assert_called_once_with(2048)
        mock_upload_file.file.seek.assert_called_once_with(0)
        mock_magic.assert_called_once_with(b"fake audio content", mime=True)
        mock_logger.info.assert_called_once()

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_all_allowed_mime_types(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test validation with all allowed MIME types."""
        for mime_type in ALLOWED_MIME_TYPES:
            with pytest.subTest(mime_type=mime_type):
                # Arrange
                mock_magic.return_value = mime_type
                mock_upload_file.file.read.return_value = b"fake audio content"
                mock_upload_file.file.seek.reset_mock()
                mock_logger.reset_mock()

                # Act
                result = validate_audio_file(mock_upload_file)

                # Assert
                assert result is None
                mock_logger.info.assert_called_once()

    def test_validate_audio_file_size_too_large(self, large_mock_upload_file):
        """Test validation failure when file size exceeds limit."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(large_mock_upload_file)

        assert (
            exc_info.value.status_code
            == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
        assert "File size exceeds the limit" in str(exc_info.value.detail)
        assert f"{MAX_FILE_SIZE / 1024 / 1024} MB" in str(
            exc_info.value.detail
        )

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_unsupported_mime_type(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test validation failure with unsupported MIME type."""
        # Arrange
        unsupported_mime = "video/mp4"
        mock_magic.return_value = unsupported_mime
        mock_upload_file.file.read.return_value = b"fake video content"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(mock_upload_file)

        assert (
            exc_info.value.status_code
            == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
        assert f"Unsupported file type: {unsupported_mime}" in str(
            exc_info.value.detail
        )
        assert "Allowed types are:" in str(exc_info.value.detail)
        mock_logger.warning.assert_called_once_with(
            f"Invalid file type uploaded: {unsupported_mime}"
        )

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_dangerous_mime_types(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test validation with potentially dangerous MIME types."""
        dangerous_mime_types = [
            "application/x-executable",
            "application/x-msdownload",
            "text/html",
            "application/javascript",
            "application/x-php",
            "application/x-python-code",
        ]

        for mime_type in dangerous_mime_types:
            with pytest.subTest(mime_type=mime_type):
                # Arrange
                mock_magic.return_value = mime_type
                mock_upload_file.file.read.return_value = b"malicious content"
                mock_logger.reset_mock()

                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    validate_audio_file(mock_upload_file)

                assert (
                    exc_info.value.status_code
                    == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                )
                mock_logger.warning.assert_called_once()

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_file_read_error(
        self, mock_magic, mock_upload_file
    ):
        """Test handling of file read errors."""
        # Arrange
        mock_upload_file.file.read.side_effect = IOError("File read error")

        # Act & Assert
        with pytest.raises(IOError):
            validate_audio_file(mock_upload_file)

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_magic_library_error(
        self, mock_magic, mock_upload_file
    ):
        """Test handling of magic library errors."""
        # Arrange
        mock_magic.side_effect = Exception("Magic library error")
        mock_upload_file.file.read.return_value = b"fake content"

        # Act & Assert
        with pytest.raises(Exception):
            validate_audio_file(mock_upload_file)

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_empty_file(
        self, mock_magic, mock_upload_file
    ):
        """Test validation with empty file content."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.file.read.return_value = b""
        mock_upload_file.size = 0

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None
        mock_magic.assert_called_once_with(b"", mime=True)

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_file_seek_behavior(
        self, mock_magic, mock_upload_file
    ):
        """Test that file pointer is reset after reading."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.file.read.return_value = b"fake content"

        # Act
        validate_audio_file(mock_upload_file)

        # Assert
        mock_upload_file.file.seek.assert_called_once_with(0)

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_exact_size_limit(
        self, mock_magic, mock_upload_file
    ):
        """Test validation with file at exact size limit."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.size = MAX_FILE_SIZE
        mock_upload_file.file.read.return_value = b"fake content"

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None  # Should pass at exact limit

    def test_validate_audio_file_boundary_size_over_limit(
        self, mock_upload_file
    ):
        """Test validation with file just over size limit."""
        # Arrange
        mock_upload_file.size = MAX_FILE_SIZE + 1

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(mock_upload_file)

        assert (
            exc_info.value.status_code
            == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_case_sensitivity(
        self, mock_magic, mock_upload_file
    ):
        """Test that MIME type checking is case sensitive."""
        # Arrange
        mock_magic.return_value = "Audio/WAV"  # Different case
        mock_upload_file.file.read.return_value = b"fake content"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(mock_upload_file)

        assert (
            exc_info.value.status_code
            == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_partial_mime_match(
        self, mock_magic, mock_upload_file
    ):
        """Test that partial MIME type matches are rejected."""
        # Arrange
        mock_magic.return_value = "audio/wav-extended"  # Partial match
        mock_upload_file.file.read.return_value = b"fake content"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(mock_upload_file)

        assert (
            exc_info.value.status_code
            == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    @pytest.mark.parametrize(
        "file_size", [0, 1, 1024, 1024 * 1024, MAX_FILE_SIZE]
    )
    def test_validate_audio_file_various_valid_sizes(
        self, file_size, mock_upload_file
    ):
        """Test validation with various valid file sizes."""
        with patch(
            "src.utils.file_validators.magic.from_buffer"
        ) as mock_magic:
            # Arrange
            mock_magic.return_value = "audio/wav"
            mock_upload_file.size = file_size
            mock_upload_file.file.read.return_value = b"fake content"

            # Act
            result = validate_audio_file(mock_upload_file)

            # Assert
            assert result is None

    def test_constants_are_defined(self):
        """Test that required constants are properly defined."""
        assert isinstance(ALLOWED_MIME_TYPES, list)
        assert len(ALLOWED_MIME_TYPES) > 0
        assert all(isinstance(mime, str) for mime in ALLOWED_MIME_TYPES)
        assert isinstance(MAX_FILE_SIZE, int)
        assert MAX_FILE_SIZE > 0

    def test_allowed_mime_types_content(self):
        """Test that ALLOWED_MIME_TYPES contains expected audio formats."""
        expected_types = [
            "audio/mpeg",
            "audio/wav",
            "audio/x-wav",
            "audio/ogg",
            "audio/flac",
        ]

        for expected_type in expected_types:
            assert expected_type in ALLOWED_MIME_TYPES

    def test_max_file_size_value(self):
        """Test that MAX_FILE_SIZE is set to expected value."""
        expected_size = 10 * 1024 * 1024  # 10 MB
        assert MAX_FILE_SIZE == expected_size

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_none_filename(
        self, mock_magic, mock_upload_file
    ):
        """Test validation with None filename."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.filename = None
        mock_upload_file.file.read.return_value = b"fake content"

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None  # Should still pass validation

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_special_characters_filename(
        self, mock_magic, mock_upload_file
    ):
        """Test validation with special characters in filename."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.filename = "test@#$%^&*()_+.wav"
        mock_upload_file.file.read.return_value = b"fake content"

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None  # Should still pass validation

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_unicode_filename(
        self, mock_magic, mock_upload_file
    ):
        """Test validation with unicode characters in filename."""
        # Arrange
        mock_magic.return_value = "audio/wav"
        mock_upload_file.filename = "B5AB_D09;.wav"
        mock_upload_file.file.read.return_value = b"fake content"

        # Act
        result = validate_audio_file(mock_upload_file)

        # Assert
        assert result is None  # Should still pass validation

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_logging_behavior(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test that logging occurs correctly for various scenarios."""
        # Test successful validation logging
        mock_magic.return_value = "audio/wav"
        mock_upload_file.file.read.return_value = b"fake content"

        validate_audio_file(mock_upload_file)

        mock_logger.info.assert_called_once()
        info_call_args = mock_logger.info.call_args[0][0]
        assert "Successfully validated audio file" in info_call_args
        assert mock_upload_file.filename in info_call_args
        assert "audio/wav" in info_call_args

    @patch("src.utils.file_validators.magic.from_buffer")
    @patch("src.utils.file_validators.logger")
    def test_validate_audio_file_warning_logging(
        self, mock_logger, mock_magic, mock_upload_file
    ):
        """Test that warning logging occurs for invalid file types."""
        # Arrange
        invalid_mime = "application/pdf"
        mock_magic.return_value = invalid_mime
        mock_upload_file.file.read.return_value = b"fake content"

        # Act & Assert
        with pytest.raises(HTTPException):
            validate_audio_file(mock_upload_file)

        mock_logger.warning.assert_called_once_with(
            f"Invalid file type uploaded: {invalid_mime}"
        )

    def test_validate_audio_file_error_message_format(
        self, large_mock_upload_file
    ):
        """Test that error messages are properly formatted."""
        # Test size error message
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(large_mock_upload_file)

        error_detail = exc_info.value.detail
        assert "File size exceeds the limit" in error_detail
        assert "MB" in error_detail
        assert str(MAX_FILE_SIZE / 1024 / 1024) in error_detail

    @patch("src.utils.file_validators.magic.from_buffer")
    def test_validate_audio_file_unsupported_type_error_message(
        self, mock_magic, mock_upload_file
    ):
        """Test that unsupported type error messages are properly formatted."""
        # Arrange
        unsupported_mime = "text/plain"
        mock_magic.return_value = unsupported_mime
        mock_upload_file.file.read.return_value = b"fake content"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(mock_upload_file)

        error_detail = exc_info.value.detail
        assert f"Unsupported file type: {unsupported_mime}" in error_detail
        assert "Allowed types are:" in error_detail
        for mime_type in ALLOWED_MIME_TYPES:
            assert mime_type in error_detail

    def test_validate_audio_file_thread_safety(self, mock_upload_file):
        """Test that the validation function is thread-safe."""
        import threading

        results = []
        errors = []

        def validate_file():
            try:
                with patch(
                    "src.utils.file_validators.magic.from_buffer"
                ) as mock_magic:
                    mock_magic.return_value = "audio/wav"
                    mock_upload_file.file.read.return_value = b"fake content"
                    result = validate_audio_file(mock_upload_file)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=validate_file)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Assert all validations succeeded
        assert len(errors) == 0
        assert len(results) == 10
        assert all(result is None for result in results)
