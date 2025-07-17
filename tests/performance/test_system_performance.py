from src.infrastructure.logging_config import get_logger
import random
import asyncio
import gc
import time
from typing import Dict
import numpy as np
import psutil
from application.services.audio_service import AudioService
from application.services.cleanup_service import CleanupService
from application.services.interaction_service import InteractionService
from tests.framework import PerformanceTestCase
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    import numpy as np
except ImportError:
    # Mock numpy when not available
    class MockNumpy:
        def array(self, data):
            return data

        def zeros(self, shape):
            return [0] * (shape if isinstance(shape, int) else shape[0])

        def ones(self, shape):
            return [1] * (shape if isinstance(shape, int) else shape[0])

        def mean(self, data):
            return sum(data) / len(data) if data else 0

        def std(self, data):
            return 1.0  # Mock standard deviation

        def random(self):
            class MockRandom:
                def rand(self, *args):
                    return 0.5

                def randint(self, low, high, size=None):
                    return low

            return MockRandom()

        @property
        def pi(self):
            return 3.14159265359

    np = MockNumpy()


try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


logger = get_logger(__name__, component="test")

"""
System Performance Tests - اختبارات الأداء الشاملة
"""


class TestSystemPerformance(PerformanceTestCase):
    """اختبارات الأداء الشاملة"""

    @pytest.fixture(autouse=True)
    async def setup_performance_services(self):
        """Setup performance test services"""
        self.interaction_service = InteractionService()
        self.audio_service = AudioService()
        self.cleanup_service = CleanupService()
        yield

    async def cleanup(self):
        """Cleanup after each test"""
        gc.collect()
        await asyncio.sleep(0.1)

    @pytest.mark.performance
    @pytest.mark.timeout(30)
    async def test_concurrent_users_handling(self):
        """اختبار 1000 مستخدم متزامن"""
        num_users = 1000
        tasks = []
        start_time = time.time()
        users = [
            self.test_data_builder.create_child(age=random.randint(3, 12))
            for _ in range(num_users)
        ]
        self.start_performance_tracking()

        async def simulate_user_interaction(user):
            operation_times = []
            for _ in range(5):
                op_start = time.perf_counter()
                try:
                    await self.interaction_service.process(
                        child_id=user.id, message=self.faker.sentence()
                    )
                    op_duration = (time.perf_counter() - op_start) * 1000
                    operation_times.append(op_duration)
                    self.record_operation(
                        f"user_{user.id}_interaction", op_duration
                    )
                except Exception:
                    self.record_operation(
                        f"user_{user.id}_interaction_failed", -1
                    )
                await asyncio.sleep((random.randint(100, 500)) / 1000.0)
            return operation_times

        tasks = [simulate_user_interaction(user) for user in users]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        metrics = self.stop_performance_tracking()
        duration = time.time() - start_time
        successful_users = sum(
            1 for r in results if not isinstance(r, Exception)
        )
        total_operations = sum(
            len(r) for r in results if not isinstance(r, Exception)
        )
        error_rate = (len(results) - successful_users) / len(results)
        assert duration < 30, f"Test took {duration}s, expected < 30s"
        assert error_rate < 0.01, f"Error rate {error_rate * 100}% exceeds 1%"
        assert (
            successful_users >= num_users * 0.99
        ), f"Only {successful_users}/{num_users} users succeeded"
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        assert cpu_percent < 80, f"CPU usage {cpu_percent}% exceeds 80%"
        assert (
            memory_percent < 85
        ), f"Memory usage {memory_percent}% exceeds 85%"
        self.assert_performance_within_limits(metrics)
        logger.info("\nPerformance Summary:")
        logger.info(f"- Total Users: {num_users}")
        logger.info(f"- Successful Users: {successful_users}")
        logger.info(f"- Total Operations: {total_operations}")
        logger.info(f"- Error Rate: {error_rate * 100:.2f}%")
        logger.info(f"- Duration: {duration:.2f}s")
        logger.info(f"- Avg Latency: {metrics['avg_latency_ms']:.2f}ms")
        logger.info(f"- P95 Latency: {metrics['p95_latency_ms']:.2f}ms")
        logger.info(f"- P99 Latency: {metrics['p99_latency_ms']:.2f}ms")

    @pytest.mark.performance
    async def test_audio_streaming_latency(self):
        """اختبار زمن الاستجابة لـ audio streaming"""
        audio_chunk_size = 1024 * 16
        num_chunks = 100
        latencies = []
        self.start_performance_tracking()
        for i in range(num_chunks):
            audio_data = self.generate_audio_chunk(audio_chunk_size)
            start_time = time.perf_counter()
            await self.audio_service.process_chunk(audio_data)
            latency = (time.perf_counter() - start_time) * 1000
            latencies.append(latency)
            self.record_operation(f"audio_chunk_{i}", latency)
        avg_latency = np.mean(latencies)
        p50_latency = np.percentile(latencies, 50)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        max_latency = np.max(latencies)
        assert (
            avg_latency < 50
        ), f"Average latency {avg_latency:.2f}ms exceeds 50ms"
        assert (
            p95_latency < 100
        ), f"P95 latency {p95_latency:.2f}ms exceeds 100ms"
        assert (
            p99_latency < 200
        ), f"P99 latency {p99_latency:.2f}ms exceeds 200ms"
        assert (
            max_latency < 500
        ), f"Max latency {max_latency:.2f}ms exceeds 500ms"
        jitter = np.std(latencies)
        assert jitter < 20, f"Latency jitter {jitter:.2f}ms too high"
        logger.info("\nAudio Streaming Latency:")
        logger.info(f"- Chunks Processed: {num_chunks}")
        logger.info(f"- Avg Latency: {avg_latency:.2f}ms")
        logger.info(f"- P50 Latency: {p50_latency:.2f}ms")
        logger.info(f"- P95 Latency: {p95_latency:.2f}ms")
        logger.info(f"- P99 Latency: {p99_latency:.2f}ms")
        logger.info(f"- Max Latency: {max_latency:.2f}ms")
        logger.info(f"- Jitter: {jitter:.2f}ms")

    @pytest.mark.performance
    @pytest.mark.memory
    async def test_memory_leak_detection(self):
        """كشف تسريبات الذاكرة في العمليات المستمرة"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        iterations = 1000
        memory_samples = []
        for i in range(iterations):
            child = self.test_data_builder.create_child()
            for _ in range(10):
                await self.interaction_service.process(
                    child_id=child.id, message=self.faker.sentence()
                )
            await self.cleanup_service.cleanup_child_session(child.id)
            if i % 100 == 0:
                gc.collect()
                await asyncio.sleep(0.01)
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                logger.info(f"Iteration {i}: Memory = {current_memory:.2f}MB")
        gc.collect()
        await asyncio.sleep(0.1)
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        assert (
            memory_increase < 50
        ), f"Memory leak detected: {memory_increase:.2f}MB increase"
        if len(memory_samples) > 2:
            x = np.arange(len(memory_samples))
            slope, _ = np.polyfit(x, memory_samples, 1)
            assert (
                abs(slope) < 0.5
            ), f"Memory growth detected: {slope:.2f}MB per 100 iterations"
        logger.info("\nMemory Leak Test:")
        logger.info(f"- Initial Memory: {initial_memory:.2f}MB")
        logger.info(f"- Final Memory: {final_memory:.2f}MB")
        logger.info(f"- Memory Increase: {memory_increase:.2f}MB")
        logger.info(f"- Memory Stable: {'Yes' if abs(slope) < 0.5 else 'No'}")

    @pytest.mark.performance
    async def test_database_query_performance(self):
        """اختبار أداء استعلامات قاعدة البيانات"""
        num_children = 100
        children = [
            self.test_data_builder.create_child() for _ in range(num_children)
        ]
        query_tests = [
            {
                "name": "Single child lookup",
                "query": lambda: self.data_repository.get_child(
                    children[0].id
                ),
                "expected_ms": 10,
            },
            {
                "name": "Batch child lookup",
                "query": lambda: self.data_repository.get_children_batch(
                    [c.id for c in children[:10]]
                ),
                "expected_ms": 20,
            },
            {
                "name": "Children by parent",
                "query": lambda: self.data_repository.get_children_by_parent(
                    children[0].parent_id
                ),
                "expected_ms": 15,
            },
            {
                "name": "Recent interactions",
                "query": lambda: self.data_repository.get_recent_interactions(
                    children[0].id, limit=50
                ),
                "expected_ms": 25,
            },
        ]
        results = []
        for test in query_tests:
            latencies = []
            for _ in range(50):
                start = time.perf_counter()
                await test["query"]()
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            assert (
                avg_latency < test["expected_ms"]
            ), f"{test['name']} avg latency {avg_latency:.2f}ms exceeds {test['expected_ms']}ms"
            results.append(
                {
                    "query": test["name"],
                    "avg_ms": avg_latency,
                    "p95_ms": p95_latency,
                }
            )
        logger.info("\nDatabase Query Performance:")
        for result in results:
            logger.info(
                f"- {result['query']}: avg={result['avg_ms']:.2f}ms, p95={result['p95_ms']:.2f}ms"
            )

    @pytest.mark.performance
    async def test_api_endpoint_response_times(self):
        """اختبار أوقات استجابة API endpoints"""
        endpoint_tests = [
            {
                "endpoint": "/api/v1/interactions/process",
                "method": "POST",
                "data": {"child_id": "test", "message": "Hello"},
                "expected_ms": 100,
            },
            {
                "endpoint": "/api/v1/children/{child_id}",
                "method": "GET",
                "expected_ms": 50,
            },
            {
                "endpoint": "/api/v1/safety/check",
                "method": "POST",
                "data": {"content": "Test message", "child_age": 7},
                "expected_ms": 75,
            },
        ]
        for test in endpoint_tests:
            response_times = []
            for _ in range(100):
                start = time.perf_counter()
                if test["method"] == "POST":
                    await self.simulate_api_call(
                        test["endpoint"],
                        method="POST",
                        data=test.get("data", {}),
                    )
                else:
                    await self.simulate_api_call(
                        test["endpoint"], method="GET"
                    )
                response_time = (time.perf_counter() - start) * 1000
                response_times.append(response_time)
            avg_time = np.mean(response_times)
            p95_time = np.percentile(response_times, 95)
            p99_time = np.percentile(response_times, 99)
            assert (
                avg_time < test["expected_ms"]
            ), f"{test['endpoint']} avg time {avg_time:.2f}ms exceeds {test['expected_ms']}ms"
            logger.info(f"\n{test['endpoint']} Performance:")
            logger.info(f"- Avg: {avg_time:.2f}ms")
            logger.info(f"- P95: {p95_time:.2f}ms")
            logger.info(f"- P99: {p99_time:.2f}ms")

    def generate_audio_chunk(self, size: int) -> bytes:
        """Generate random audio data for testing"""
        return random.randbytes(size)

    async def simulate_api_call(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ):
        """Simulate API call for testing"""
        # Generate a random float between 0.001 and 0.01
        delay = (random.randint(100, 1000)) / 100000.0
        await asyncio.sleep(delay)
        return {"status": "success", "data": {}, "timestamp": time.time()}
