"""Circuit Breaker implementation to prevent repeated calls to failing services."""

import asyncio
import time
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any


class CircuitBreakerState:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpen(Exception):
    """Exception raised when the circuit is open."""


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = 0

    def __call__(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == CircuitBreakerState.OPEN:
                # Use asyncio.sleep(0) to yield control and prevent blocking
                await asyncio.sleep(0)  # Yield control to event loop
                if (
                    time.monotonic() - self.last_failure_time
                    > self.recovery_timeout
                ):
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker {self.name} is open"
                    )

            try:
                result = await func(*args, **kwargs)
                self._reset()
                return result
            except Exception as e:
                self._record_failure()
                raise e

        return wrapper

    def _record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = time.monotonic()

    def _reset(self) -> None:
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
