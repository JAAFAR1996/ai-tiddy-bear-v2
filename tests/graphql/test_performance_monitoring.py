import pytest

try:
    from src.infrastructure.graphql.performance_monitor import (
        create_performance_monitor,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestPerformanceMonitoring:
    """Test performance monitoring."""

    @pytest.mark.asyncio
    async def test_query_monitoring(self):
        """Test query performance monitoring."""
        try:
            monitor = create_performance_monitor(enable_prometheus=False)

            # Start monitoring
            query = 'query { child(id: "123") { name } }'
            query_hash = await monitor.start_query_monitoring(query, {}, "getChild")

            assert query_hash is not None
            assert monitor.current_queries == 1

            # Finish monitoring
            await monitor.finish_query_monitoring(
                query_hash=query_hash,
                query=query,
                variables={},
                operation_name="getChild",
                execution_time_ms=150.5,
                fields_requested=["name"],
                services_involved=["child_service"],
                cache_hit=False,
                error_count=0,
            )

            assert monitor.current_queries == 0

            # Check metrics
            summary = monitor.get_performance_summary()
            assert summary["summary"]["total_queries"] > 0

        except ImportError:
            pytest.skip("Performance monitoring not available")

    @pytest.mark.asyncio
    async def test_service_call_recording(self):
        """Test service call metrics recording."""
        try:
            monitor = create_performance_monitor(enable_prometheus=False)

            await monitor.record_service_call(
                service_name="child_service",
                query_hash="test-hash",
                execution_time_ms=75.2,
                response_size_bytes=1024,
                success=True,
            )

            # Check that metrics were recorded
            assert len(monitor.service_metrics) > 0

        except ImportError:
            pytest.skip("Performance monitoring not available")
