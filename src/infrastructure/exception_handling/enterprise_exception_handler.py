
from dataclasses import dataclass
from typing import Any
from fastapi import HTTPException, status
import logging


@dataclass
class ExceptionHandlerConfig:
    enable_structured_logging: bool = False
    enable_correlation_ids: bool = False
    enable_error_tracking: bool = False
    enable_circuit_breaker: bool = False
    max_retry_attempts: int = 0
    retry_delay_seconds: float = 0.0
    exponential_backoff: bool = False
    log_sensitive_data: bool = False
    error_threshold_per_minute: int = 0
    circuit_breaker_timeout_seconds: int = 0


class EnterpriseExceptionHandler:
    def __init__(self, config: ExceptionHandlerConfig) -> None:
        self.config = config
        self.logger = logging.getLogger("enterprise_exception_handler")

    def handle_exception(
        self,
        exception: Exception,
        error_code: str | None = None,
        additional_data: dict[str, Any] | None = None,
        reraise: bool = True,
    ):
        self.logger.error(f"Exception occurred: {exception}", exc_info=True)
        if reraise:
            raise exception
        return None

    def create_safe_error_response(
        self,
        exception: Exception,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        user_message: str = "An error occurred",
        error_code: str | None = None,
        additional_data: dict[str, Any] | None = None,
    ):
        self.logger.error(f"Safe error response: {exception}", exc_info=True)
        # يمكن تخصيص الاستجابة أكثر حسب الحاجة
        return HTTPException(
            status_code=status_code,
            detail={
                "message": user_message,
                "error_code": error_code,
                "data": additional_data,
            },
        )

    def get_circuit_breaker(self, service_name: str):
        try:
            import pybreaker
        except ImportError:
            self.logger.critical("pybreaker not installed. Circuit breaker unavailable.")
            raise RuntimeError("pybreaker not installed. Please install pybreaker for circuit breaker support.")
        # Configure a production circuit breaker
        return pybreaker.CircuitBreaker(
            fail_max=self.config.error_threshold_per_minute or 5,
            reset_timeout=self.config.circuit_breaker_timeout_seconds or 60,
            name=service_name,
        )


# Factory function to get a singleton handler (يمكن تطويرها لاحقاً)
_enterprise_exception_handler = None


def get_enterprise_exception_handler():
    global _enterprise_exception_handler
    if _enterprise_exception_handler is None:
        config = ExceptionHandlerConfig(
            enable_structured_logging=True,
            enable_error_tracking=True,
        )
        _enterprise_exception_handler = EnterpriseExceptionHandler(config)
    return _enterprise_exception_handler


def handle_exceptions(*args, **kwargs):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def with_retry(*args, **kwargs):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
