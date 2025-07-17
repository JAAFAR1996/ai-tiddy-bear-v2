from collections.abc import Callable, Coroutine
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class ComprehensiveMonitoring:
    """A comprehensive monitoring system for the AI Teddy Bear application."""

    def __init__(
        self,
        enable_logging: bool = True,
        enable_metrics: bool = True,
    ) -> None:
        self.enable_logging = enable_logging
        self.enable_metrics = enable_metrics
        self.metrics: dict[str, Any] = {
            "requests_total": 0,
            "errors_total": 0,
            "latency_ms": [],
        }

    def log_event(self, event_name: str, details: dict[str, Any]) -> None:
        """Logs a specific event if logging is enabled."""
        if self.enable_logging:
            logger.info(f"Event: {event_name}", extra=details)

    def update_metric(self, metric_name: str, value: Any) -> None:
        """Updates a metric if metrics are enabled."""
        if self.enable_metrics:
            if metric_name in self.metrics:
                if isinstance(self.metrics[metric_name], list):
                    self.metrics[metric_name].append(value)
                else:
                    self.metrics[metric_name] += value
            else:
                self.metrics[metric_name] = value

    def get_metrics(self) -> dict[str, Any]:
        """Returns the current metrics."""
        return self.metrics

    def monitor_function(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to monitor a synchronous function."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.log_event(f"{func.__name__}_started", {})
            self.update_metric("requests_total", 1)
            try:
                result = func(*args, **kwargs)
                self.log_event(f"{func.__name__}_succeeded", {})
                return result
            except Exception as e:
                self.log_event(f"{func.__name__}_failed", {"error": str(e)})
                self.update_metric("errors_total", 1)
                raise

        return wrapper

    def monitor_coroutine(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        """Decorator to monitor an asynchronous function."""

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.log_event(f"{coro.__name__}_started", {})
            self.update_metric("requests_total", 1)
            try:
                result = await coro(*args, **kwargs)
                self.log_event(f"{coro.__name__}_succeeded", {})
                return result
            except Exception as e:
                self.log_event(f"{coro.__name__}_failed", {"error": str(e)})
                self.update_metric("errors_total", 1)
                raise

        return wrapper
