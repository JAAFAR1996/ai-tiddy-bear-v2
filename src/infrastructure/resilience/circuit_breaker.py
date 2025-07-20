import asyncio
import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any

from src.infrastructure.logging_config import get_logger

"""Circuit Breaker pattern implementation for preventing cascade failures."""

logger = get_logger(__name__, component="infrastructure")


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """Circuit breaker implementation to prevent cascade failures.
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests are passed through
    - OPEN: Circuit is open, requests are rejected immediately
    - HALF_OPEN: Limited requests are allowed to test if service is back.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
            expected_exception: Exception type that counts as failure

        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        logger.info(
            f"Circuit breaker initialized: threshold={failure_threshold}, timeout={timeout}s",
        )

    def _can_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout

    def _record_success(self) -> None:
        """Record successful operation."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        logger.debug("Circuit breaker: success recorded, circuit closed")

    def _record_failure(self) -> None:
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures. "
                f"Will attempt reset in {self.timeout}s",
            )
        else:
            logger.debug(
                f"Circuit breaker: failure {self.failure_count}/{self.failure_threshold}",
            )

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Call function through circuit breaker(synchronous).

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        Returns:
            Function result
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails

        """
        if self.state == CircuitBreakerState.OPEN:
            if self._can_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is open. Will retry in "
                    f"{self.timeout - (time.time() - self.last_failure_time):.1f}s",
                )

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception:
            self._record_failure()
            raise

    async def call_async(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Call async function through circuit breaker.

        Args:
            func: Async function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        Returns:
            Function result
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If function fails

        """
        if self.state == CircuitBreakerState.OPEN:
            if self._can_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is open. Will retry in "
                    f"{self.timeout - (time.time() - self.last_failure_time):.1f}s",
                )

        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except self.expected_exception:
            self._record_failure()
            raise

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "timeout": self.timeout,
            "can_attempt_reset": (
                self._can_attempt_reset()
                if self.state == CircuitBreakerState.OPEN
                else None
            ),
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejecting calls."""


def circuit_breaker(
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: type = Exception,
) -> Callable:
    """Decorator that applies circuit breaker pattern to a function.

    Args:
        failure_threshold: Number of failures before opening circuit
        timeout: Time in seconds before attempting to close circuit
        expected_exception: Exception type that counts as failure
    Returns:
        Decorated function with circuit breaker logic

    """
    breaker = CircuitBreaker(failure_threshold, timeout, expected_exception)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call_async(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return breaker.call(func, *args, **kwargs)

        # Add status method to decorated function
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.circuit_breaker = breaker
        wrapper.get_circuit_status = breaker.get_status
        return wrapper

    return decorator


# Global circuit breakers for common external services
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: type = Exception,
) -> CircuitBreaker:
    """Get or create a named circuit breaker.

    Args:
        name: Unique name for the circuit breaker
        failure_threshold: Number of failures before opening circuit
        timeout: Time in seconds before attempting to close circuit
        expected_exception: Exception type that counts as failure
    Returns:
        Circuit breaker instance

    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
        )
        logger.info(f"Created circuit breaker '{name}'")
    return _circuit_breakers[name]


def get_all_circuit_breaker_status() -> dict[str, dict[str, Any]]:
    """Get status of all circuit breakers."""
    return {name: breaker.get_status() for name, breaker in _circuit_breakers.items()}
