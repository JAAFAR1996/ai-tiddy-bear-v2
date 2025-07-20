from src.domain.interfaces.logging_interface import LogLevel
"""🔍 Standardized Logging for AI Teddy Bear System
Consistent logging levels and patterns across all services.
"""

from datetime import datetime
from enum import Enum
from typing import Any


    """Standard log categories for the system."""

    SECURITY = "SECURITY"
    CHILD_SAFETY = "CHILD_SAFETY"
    PERFORMANCE = "PERFORMANCE"
    API = "API"
    AUDIO = "AUDIO"
    AI_PROCESSING = "AI_PROCESSING"
    DATABASE = "DATABASE"
    SYSTEM = "SYSTEM"


class StandardizedLogger:
    """Standardized logger with consistent formatting and context."""

    def __init__(self, name: str) -> None:
        from src.infrastructure.logging_config import get_logger

        self.logger = get_logger(__name__, component="infrastructure")
        self.service_name = name

    def _log_with_context(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        extra_context: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Log message with standardized context and format.

        Args:
            level: Log level
            category: Log category
            message: The log message
            extra_context: Additional context data
            exc_info: Whether to include exception info

        """
        context = {
            "service": self.service_name,
            "category": category.value,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if extra_context:
            context.update(extra_context)

        formatted_message = f"[{category.value}] {message}"
        getattr(self.logger, level.value.lower())(
            formatted_message,
            extra=context,
            exc_info=exc_info,
        )

    def security_event(
        self,
        event_type: str,
        details: dict[str, Any] | None = None,
        severity: LogLevel = LogLevel.WARNING,
    ) -> None:
        """Log security events."""
        context = {"event_type": event_type}
        if details:
            context.update(details)

        self._log_with_context(
            severity,
            LogCategory.SECURITY,
            f"Security event: {event_type}",
            context,
        )

    def child_safety_event(
        self,
        event_type: str,
        child_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Log child safety events."""
        context = {"event_type": event_type}
        if child_id:
            context["child_id"] = child_id
        if details:
            context.update(details)

        self._log_with_context(
            LogLevel.INFO,
            LogCategory.CHILD_SAFETY,
            f"Child safety event: {event_type}",
            context,
        )

    def performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        **kwargs,
    ) -> None:
        """Log performance metrics."""
        context = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
        }
        context.update(kwargs)

        self._log_with_context(
            LogLevel.INFO,
            LogCategory.PERFORMANCE,
            f"Performance metric: {metric_name} = {value}{unit}",
            context,
        )

    def api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """Log API requests with standardized format."""
        context = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }
        context.update(kwargs)

        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO

        # Split long message for better readability
        message = f"{method} {path} -> {status_code} " f"({duration_ms:.2f}ms)"
        self._log_with_context(level, LogCategory.API, message, context)

    def audio_processing(
        self,
        operation: str,
        duration_ms: float | None = None,
        quality_score: float | None = None,
        **kwargs,
    ) -> None:
        """Log audio processing events."""
        context = {"operation": operation}
        if duration_ms is not None:
            context["duration_ms"] = duration_ms
        if quality_score is not None:
            context["quality_score"] = quality_score
        context.update(kwargs)

        self._log_with_context(
            LogLevel.INFO,
            LogCategory.AUDIO,
            f"Audio processing: {operation}",
            context,
        )

    def ai_processing(
        self,
        model_name: str,
        operation: str,
        confidence: float | None = None,
        processing_time_ms: float | None = None,
        **kwargs,
    ) -> None:
        """Log AI processing events."""
        context = {
            "model_name": model_name,
            "operation": operation,
        }
        if confidence is not None:
            context["confidence"] = confidence
        if processing_time_ms is not None:
            context["processing_time_ms"] = processing_time_ms
        context.update(kwargs)

        self._log_with_context(
            LogLevel.INFO,
            LogCategory.AI_PROCESSING,
            f"AI processing: {model_name} - {operation}",
            context,
        )

    def database_operation(
        self,
        operation: str,
        table: str | None = None,
        duration_ms: float | None = None,
        affected_rows: int | None = None,
        **kwargs,
    ) -> None:
        """Log database operations."""
        context = {"operation": operation}
        if table:
            context["table"] = table
        if duration_ms is not None:
            context["duration_ms"] = duration_ms
        if affected_rows is not None:
            context["affected_rows"] = affected_rows
        context.update(kwargs)

        self._log_with_context(
            LogLevel.INFO,
            LogCategory.DATABASE,
            f"Database operation: {operation}",
            context,
        )

    def system_event(
        self,
        event_type: str,
        severity: LogLevel = LogLevel.INFO,
        **kwargs,
    ) -> None:
        """Log system events."""
        self._log_with_context(
            severity,
            LogCategory.SYSTEM,
            f"System event: {event_type}",
            kwargs,
        )

    def error(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        exc_info: bool = True,
        **kwargs,
    ) -> None:
        """Log errors with exception info."""
        self._log_with_context(
            LogLevel.ERROR,
            category,
            message,
            kwargs,
            exc_info=exc_info,
        )

    def warning(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs,
    ) -> None:
        """Log warnings."""
        self._log_with_context(
            LogLevel.WARNING,
            category,
            message,
            kwargs,
        )

    def info(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs,
    ) -> None:
        """Log info messages."""
        self._log_with_context(
            LogLevel.INFO,
            category,
            message,
            kwargs,
        )

    def debug(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs,
    ) -> None:
        """Log debug messages."""
        self._log_with_context(
            LogLevel.DEBUG,
            category,
            message,
            kwargs,
        )


def get_standardized_logger(service_name: str) -> StandardizedLogger:
    """Get a standardized logger for a service."""
    return StandardizedLogger(service_name)
