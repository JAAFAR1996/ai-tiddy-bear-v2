"""🔍 Standardized Logging for AI Teddy Bear System
Consistent logging levels and patterns across all services"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import logging
import sys

class LogLevel(Enum):
    """Standardized log levels with clear usage guidelines."""
    DEBUG = "DEBUG"        # Detailed diagnostic info for development only
    INFO = "INFO"          # General information about system operation
    WARNING = "WARNING"    # Something unexpected but system continues
    ERROR = "ERROR"        # Serious problem occurred, but system continues
    CRITICAL = "CRITICAL"  # Very serious error, system may stop

class LogCategory(Enum):
    """Standardized log categories for consistent messaging."""
    CHILD_SAFETY = "CHILD_SAFETY"           # Child safety and COPPA compliance
    SECURITY = "SECURITY"                   # Security events and authentication
    PERFORMANCE = "PERFORMANCE"             # Performance metrics and optimization
    AI_PROCESSING = "AI_PROCESSING"         # AI service operations
    DATABASE = "DATABASE"                   # Database operations
    CACHE = "CACHE"                         # Caching operations
    API = "API"                             # API requests and responses
    DEVICE = "DEVICE"                       # Device management
    CONVERSATION = "CONVERSATION"           # Conversation handling
    SYSTEM = "SYSTEM"                       # General system operations

class StandardLogger:
    """
    Standardized logger wrapper providing consistent logging patterns.
    This ensures all services use consistent log levels, formats, and include necessary context for child safety compliance.
    """
    
    def __init__(self, name: str) -> None:
        from src.infrastructure.logging_config import get_logger
        logger = get_logger(__name__, component="infrastructure")
        self.service_name = name
    
    def _log_with_context(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        extra_context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> None:
        """
        Log message with standardized context and format.
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
            exc_info=exc_info
        )
    
    def child_safety_violation(self, message: str, child_id: Optional[str] = None, **kwargs) -> None:
        """Log child safety violations - always CRITICAL priority."""
        context = {"child_id": child_id} if child_id else {}
        context.update(kwargs)
        self._log_with_context(LogLevel.CRITICAL, LogCategory.CHILD_SAFETY, message, context)
    
    def child_safety_warning(self, message: str, child_id: Optional[str] = None, **kwargs) -> None:
        """Log child safety warnings - always ERROR priority."""
        context = {"child_id": child_id} if child_id else {}
        context.update(kwargs)
        self._log_with_context(LogLevel.ERROR, LogCategory.CHILD_SAFETY, message, context)
    
    def security_violation(self, message: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log security violations - always CRITICAL."""
        context = {"user_id": user_id} if user_id else {}
        context.update(kwargs)
        self._log_with_context(LogLevel.CRITICAL, LogCategory.SECURITY, message, context)
    
    def security_warning(self, message: str, **kwargs) -> None:
        """Log security warnings."""
        self._log_with_context(LogLevel.WARNING, LogCategory.SECURITY, message, kwargs)
    
    def authentication_failure(self, message: str, **kwargs) -> None:
        """Log authentication failures."""
        self._log_with_context(LogLevel.ERROR, LogCategory.SECURITY, message, kwargs)
    
    def system_startup(self, message: str, **kwargs) -> None:
        """Log system startup events."""
        self._log_with_context(LogLevel.INFO, LogCategory.SYSTEM, message, kwargs)
    
    def system_error(self, message: str, **kwargs) -> None:
        """Log system errors."""
        self._log_with_context(LogLevel.ERROR, LogCategory.SYSTEM, message, kwargs, exc_info=True)
    
    def system_warning(self, message: str, **kwargs) -> None:
        """Log system warnings."""
        self._log_with_context(LogLevel.WARNING, LogCategory.SYSTEM, message, kwargs)
    
    def ai_request_started(self, message: str, **kwargs) -> None:
        """Log AI request initiation."""
        self._log_with_context(LogLevel.INFO, LogCategory.AI_PROCESSING, message, kwargs)
    
    def ai_request_completed(self, message: str, duration_ms: Optional[float] = None, **kwargs) -> None:
        """Log AI request completion."""
        context = {"duration_ms": duration_ms} if duration_ms else {}
        context.update(kwargs)
        self._log_with_context(LogLevel.INFO, LogCategory.AI_PROCESSING, message, context)
    
    def ai_request_failed(self, message: str, **kwargs) -> None:
        """Log AI request failures."""
        self._log_with_context(LogLevel.ERROR, LogCategory.AI_PROCESSING, message, kwargs, exc_info=True)
    
    def database_connected(self, message: str, **kwargs) -> None:
        """Log successful database connections."""
        self._log_with_context(LogLevel.INFO, LogCategory.DATABASE, message, kwargs)
    
    def database_error(self, message: str, **kwargs) -> None:
        """Log database errors."""
        self._log_with_context(LogLevel.ERROR, LogCategory.DATABASE, message, kwargs, exc_info=True)
    
    def database_warning(self, message: str, **kwargs) -> None:
        """Log database warnings."""
        self._log_with_context(LogLevel.WARNING, LogCategory.DATABASE, message, kwargs)
    
    def performance_metric(self, message: str, duration_ms: float, **kwargs) -> None:
        """Log performance metrics."""
        context = {"duration_ms": duration_ms}
        context.update(kwargs)
        level = LogLevel.WARNING if duration_ms > 2000 else LogLevel.INFO  # 2s threshold for child attention
        self._log_with_context(level, LogCategory.PERFORMANCE, message, context)
    
    def api_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs) -> None:
        """Log API requests with standardized format."""
        context = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        context.update(kwargs)
        
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        message = f"{method} {path} -> {status_code} ({duration_ms:.2f}ms)"
        self._log_with_context(level, LogCategory.API, message, context)
    
    def cache_hit(self, key: str, **kwargs) -> None:
        """Log cache hits."""
        context = {"cache_key": key}
        context.update(kwargs)
        self._log_with_context(LogLevel.DEBUG, LogCategory.CACHE, f"Cache hit: {key}", context)
    
    def cache_miss(self, key: str, **kwargs) -> None:
        """Log cache misses."""
        context = {"cache_key": key}
        context.update(kwargs)
        self._log_with_context(LogLevel.DEBUG, LogCategory.CACHE, f"Cache miss: {key}", context)
    
    def cache_error(self, message: str, **kwargs) -> None:
        """Log cache errors."""
        self._log_with_context(LogLevel.ERROR, LogCategory.CACHE, message, kwargs)

def get_standard_logger(name: str) -> StandardLogger:
    """
    Get a standardized logger instance for a service.
    Args:
        name: Logger name (typically __name__ or service name)
    Returns:
        StandardLogger instance with consistent patterns
    """
    return StandardLogger(name)

def configure_logging(
    level: str = "INFO",
    format_style: str = "json",
    include_context: bool = True
) -> None:
    """
    Configure logging for the entire application with standardized settings.
    Args:
        level: Minimum log level
        format_style: "json" or "text" format
        include_context: Whether to include extra context in logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_style == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(service)s", '
            '"category": "%(category)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(category)s] - %(message)s'
        )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

__all__ = [
    "StandardLogger",
    "LogLevel",
    "LogCategory",
    "get_standard_logger",
    "configure_logging"
]