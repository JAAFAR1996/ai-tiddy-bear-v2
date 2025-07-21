# src/infrastructure/monitoring/performance_monitor.py

import threading
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("infrastructure.performance_monitor")

class PerformanceMonitor:
    """
    Central performance monitoring for the AI Teddy Bear project.
    Tracks requests, latency, and error rates.
    Ready for Prometheus, Datadog, or custom logging.
    """

    _instance = None
    _lock = threading.Lock()

    # Singleton
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PerformanceMonitor, cls).__new__(cls)
                cls._instance._init_metrics()
            return cls._instance

    def _init_metrics(self):
        self.metrics = {
            "requests_total": 0,
            "errors_total": 0,
            "latency_sum": 0.0,
            "latency_count": 0,
            "custom": {}
        }
        self.active_requests = 0
        self.start_time = time.time()

    def log_request(self, endpoint: str):
        self.metrics["requests_total"] += 1
        self.active_requests += 1
        logger.debug(f"[PERF] Request started: {endpoint}")

    def log_response(self, endpoint: str, latency: float, error: Optional[Exception] = None):
        self.metrics["latency_sum"] += latency
        self.metrics["latency_count"] += 1
        self.active_requests = max(0, self.active_requests - 1)
        if error:
            self.metrics["errors_total"] += 1
            logger.warning(f"[PERF] Error at {endpoint}: {error}")
        logger.debug(f"[PERF] Response {endpoint}, latency={latency:.3f}s")

    def record_metric(self, key: str, value: Any):
        self.metrics["custom"][key] = value
        logger.info(f"[PERF] Custom metric: {key}={value}")

    def get_summary(self) -> Dict[str, Any]:
        avg_latency = (
            self.metrics["latency_sum"] / self.metrics["latency_count"]
            if self.metrics["latency_count"] > 0 else 0.0
        )
        uptime = time.time() - self.start_time
        summary = {
            "requests_total": self.metrics["requests_total"],
            "errors_total": self.metrics["errors_total"],
            "avg_latency": avg_latency,
            "active_requests": self.active_requests,
            "uptime_sec": uptime,
            "custom": self.metrics["custom"],
        }
        return summary

    def report(self):
        summary = self.get_summary()
        logger.info(f"[PERF] SUMMARY: {summary}")
        return summary

    # --- Decorators for auto-monitoring ---
    def monitor(self, endpoint: str):
        """
        Decorator to wrap any endpoint/function for automatic performance logging.
        Usage:
            @performance_monitor.monitor('/api/v1/ask')
            def my_func(...): ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.log_request(endpoint)
                start = time.time()
                error = None
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as ex:
                    error = ex
                    raise
                finally:
                    latency = time.time() - start
                    self.log_response(endpoint, latency, error)
            return wrapper
        return decorator

# For DI container compatibility:
performance_monitor = PerformanceMonitor()
