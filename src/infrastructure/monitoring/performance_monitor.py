import time
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from prometheus_client import Counter, Histogram

# Prometheus metrics
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency", ["endpoint"]
)
REQUEST_COUNT = Counter(
    "request_count",
    "Request count",
    ["endpoint", "method", "status"],
)


def monitor_performance(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator to monitor the performance of an async function."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            status = "success"
            return result
        except Exception as e:
            status = "error"
            raise e
        finally:
            latency = time.time() - start_time
            endpoint_name = func.__name__
            REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(latency)
            REQUEST_COUNT.labels(
                endpoint=endpoint_name,
                method="unknown",
                status=status,
            ).inc()

    return wrapper
