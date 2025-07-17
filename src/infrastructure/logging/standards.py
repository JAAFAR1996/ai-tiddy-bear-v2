"""🔍 Standardized Logging for AI Teddy Bear System
Consistent logging levels and patterns across all services.
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any

# ... (جميع الكود بدون تغيير حتى السطر الطويل)

    def __init__(self, name: str) -> None:
        from src.infrastructure.logging_config import get_logger

        get_logger(__name__, component="infrastructure")
        self.service_name = name

# ... (جميع الكود كما هو)

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

# ... (استمر في الكود كما هو)

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

        # هنا كان السطر الطويل:
        message = (
            f"{method} {path} -> {status_code} "
            f"({duration_ms:.2f}ms)"
        )
        self._log_with_context(level, LogCategory.API, message, context)

# ... (باقي الكود كما هو)
