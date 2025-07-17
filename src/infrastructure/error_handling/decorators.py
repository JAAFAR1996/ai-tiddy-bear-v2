from typing import Callable, Type, Any, Tuple, Optional
import functools
import asyncio

from .error_types import BaseApplicationError, ExternalServiceError
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


def handle_errors(
    *error_mappings: Tuple[Type[Exception], Type[BaseApplicationError]],
    default_error: Optional[Type[BaseApplicationError]] = None,
    log_errors: bool = True,
):
    """
    Maps exceptions to application errors and handles logging.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except BaseApplicationError:
                raise
            except Exception as e:
                for source_type, target_type in error_mappings:
                    if isinstance(e, source_type):
                        mapped_error = target_type(str(e))
                        if log_errors:
                            logger.warning(
                                f"Mapped {type(e).__name__} to {target_type.__name__}: {e}",
                            )
                        raise mapped_error from e

                if default_error:
                    mapped_error = default_error(f"Unexpected error: {e!s}")
                    if log_errors:
                        logger.error(
                            f"Unmapped error {type(e).__name__}, using default: {e}",
                            exc_info=True,
                        )
                    raise mapped_error from e

                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseApplicationError:
                raise
            except Exception as e:
                for source_type, target_type in error_mappings:
                    if isinstance(e, source_type):
                        mapped_error = target_type(str(e))
                        if log_errors:
                            logger.warning(
                                f"Mapped {type(e).__name__} to {target_type.__name__}: {e}",
                            )
                        raise mapped_error from e

                if default_error:
                    mapped_error = default_error(f"Unexpected error: {e!s}")
                    if log_errors:
                        logger.error(
                            f"Unmapped error {type(e).__name__}, using default: {e}",
                            exc_info=True,
                        )
                    raise mapped_error from e

                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def retry_on_error(
    max_retries: int = 3,
    retry_exceptions: Tuple[Type[Exception], ...] = (ExternalServiceError,),
    delay: float = 1.0,
    backoff: float = 2.0,
):
    """
    Decorator to retry function on specific errors.
    Usage: @retry_on_error(max_retries=3, retry_exceptions=(ExternalServiceError,))
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except retry_exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.info(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {type(e).__name__}: {e}",
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as other_error:
                    logger.error(
                        f"Unexpected error in {func.__name__}: {other_error}"
                    )
                    raise

            logger.error(
                f"All {max_retries} retries failed for {func.__name__}"
            )
            raise last_error

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time

            last_error = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.info(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {type(e).__name__}: {e}",
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as other_error:
                    logger.error(
                        f"Unexpected error in {func.__name__}: {other_error}"
                    )
                    raise

            logger.error(
                f"All {max_retries} retries failed for {func.__name__}"
            )
            raise last_error

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def safe_execution(
    fallback_value: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
):
    """
    Decorator for safe execution with fallback value.
    Usage: @safe_execution(fallback_value=[], log_errors=True)
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {e}", exc_info=True
                    )
                if reraise:
                    raise
                return fallback_value

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {e}", exc_info=True
                    )
                if reraise:
                    raise
                return fallback_value

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def validate_result(
    validator: Callable[[Any], bool],
    error_class: Type[BaseApplicationError],
    error_message: str = "Result validation failed",
):
    """
    Decorator to validate the result of a function and raise error if invalid.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if not validator(result):
                raise error_class(error_message)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not validator(result):
                raise error_class(error_message)
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


__all__ = [
    "handle_errors",
    "retry_on_error",
    "safe_execution",
    "validate_result",
]
