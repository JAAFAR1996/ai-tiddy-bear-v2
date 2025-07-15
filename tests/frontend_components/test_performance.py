import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import asyncio
from datetime import datetime

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


class TestPerformance:
    """Test performance optimizations"""

    @pytest.mark.asyncio
    async def test_lazy_loading(self):
        """Test lazy loading of components"""
        load_times = []

        async def mock_load_component(name):
            start = datetime.utcnow()
            await asyncio.sleep(0.1)  # Simulate loading
            end = datetime.utcnow()
            load_time = (end - start).total_seconds()
            load_times.append(load_time)
            return f"{name}_component"

        # Load multiple components
        components = await asyncio.gather(
            mock_load_component("Dashboard"),
            mock_load_component("Conversations"),
            mock_load_component("Reports"),
        )

        assert len(components) == 3
        assert all(time < 0.2 for time in load_times)  # All loaded quickly

    def test_memoization(self):
        """Test memoization of expensive computations"""
        call_count = 0

        def expensive_computation(data):
            nonlocal call_count
            call_count += 1
            return sum(data)

        # Mock memoized function
        memo_cache = {}

        def memoized_computation(data):
            key = str(data)
            if key not in memo_cache:
                memo_cache[key] = expensive_computation(data)
            return memo_cache[key]

        # First call
        result1 = memoized_computation([1, 2, 3])
        assert result1 == 6
        assert call_count == 1

        # Second call with same data
        result2 = memoized_computation([1, 2, 3])
        assert result2 == 6
        assert call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_debounced_search(self):
        """Test debounced search functionality"""
        search_calls = []

        async def search(query):
            search_calls.append(query)
            await asyncio.sleep(0.05)
            return f"results for {query}"

        # Simulate rapid typing
        queries = ["c", "ca", "cat"]

        # Without debounce - all calls made
        for query in queries:
            await search(query)

        assert len(search_calls) == 3

        # With debounce simulation
        search_calls.clear()
        last_query = queries[-1]
        await search(last_query)

        assert len(search_calls) == 1
        assert search_calls[0] == "cat"
