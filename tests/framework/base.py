"""Test Framework Base Classes"""



# Mock structlog
class MockLogger:
    def info(self, message, **kwargs):
        print(f"INFO: {message}")

    def error(self, message, **kwargs):
        print(f"ERROR: {message}")

    def warning(self, message, **kwargs):
        print(f"WARNING: {message}")


def get_logger(name=None):
    return MockLogger()


# Use mock if structlog not available
try:
    import structlog
except ImportError:
    import sys

    sys.modules["structlog"] = type(
        "MockStructlog", (), {"get_logger": get_logger}
    )
    structlog = sys.modules["structlog"]


class BaseTestCase:
    """Base test case for all tests"""

    def __init__(self):
        self.logger = structlog.get_logger()

    def setup_method(self):
        """Setup method for each test"""

    def teardown_method(self):
        """Teardown method for each test"""


class ChildSafetyTestCase(BaseTestCase):
    """Test case for child safety features"""

    def __init__(self):
        super().__init__()
        self.safety_checks = []

    def assert_child_safe(self, content: str) -> bool:
        """Assert content is child-safe"""
        # Mock safety check
        unsafe_words = ["violence", "inappropriate", "dangerous"]
        is_safe = not any(word in content.lower() for word in unsafe_words)
        self.safety_checks.append({"content": content, "safe": is_safe})
        return is_safe

    def assert_age_appropriate(self, content: str, age: int) -> bool:
        """Assert content is age-appropriate"""
        # Mock age appropriateness check
        if age < 5:
            return len(content) < 100 and "simple" in content.lower()
        elif age < 10:
            return len(content) < 200
        return True


class PerformanceTestCase(BaseTestCase):
    """Test case for performance testing"""

    def __init__(self):
        super().__init__()
        self.performance_metrics = []

    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time"""
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        self.performance_metrics.append(
            {
                "function": func.__name__,
                "execution_time": execution_time,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
            }
        )

        return result

    def assert_execution_time_under(self, max_time_seconds: float):
        """Assert last execution was under specified time"""
        if self.performance_metrics:
            last_metric = self.performance_metrics[-1]
            assert (
                last_metric["execution_time"] < max_time_seconds
            ), f"Execution took {last_metric['execution_time']}s, expected under {max_time_seconds}s"
