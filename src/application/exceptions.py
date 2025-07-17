"""Custom exceptions for the application layer."""


class ApplicationException(Exception):
    """Base exception for application-level errors."""


class ServiceException(ApplicationException):
    """Base exception for service layer errors."""


class InvalidInputException(ApplicationException):
    """Exception raised for invalid input data."""


class NotFoundException(ApplicationException):
    """Exception raised when a requested resource is not found."""


class AudioProcessingError(ApplicationException):
    """Exception raised for errors during audio processing."""


class TranscriptionError(ApplicationException):
    """Exception raised for errors during speech-to-text transcription."""
