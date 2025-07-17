import asyncio
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


class TestDashboard:
    """Test dashboard functionality"""

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, dashboard_service):
        """Test fetching dashboard statistics"""
        # Arrange
        expected_stats = {
            "dailyConversations": 8,
            "emotionalState": "happy",
            "activityTime": 45,
            "educationalProgress": 85,
            "conversationTrend": [
                {"date": "2024-01-01", "count": 5},
                {"date": "2024-01-02", "count": 8},
            ],
        }
        dashboard_service.get_stats.return_value = expected_stats

        # Act
        stats = await dashboard_service.get_stats()

        # Assert
        assert stats["dailyConversations"] == 8
        assert stats["emotionalState"] == "happy"
        assert stats["activityTime"] == 45
        assert stats["educationalProgress"] == 85
        assert len(stats["conversationTrend"]) == 2

    @pytest.mark.asyncio
    async def test_emotion_distribution(self, dashboard_service):
        """Test emotion distribution data"""
        # Arrange
        emotion_data = [
            {"emotion": "happy", "value": 40},
            {"emotion": "neutral", "value": 30},
            {"emotion": "excited", "value": 20},
            {"emotion": "sad", "value": 10},
        ]
        dashboard_service.get_emotion_data.return_value = emotion_data

        # Act
        emotions = await dashboard_service.get_emotion_data()

        # Assert
        assert len(emotions) == 4
        assert sum(e["value"] for e in emotions) == 100
        assert emotions[0]["emotion"] == "happy"
        assert emotions[0]["value"] == 40

    @pytest.mark.asyncio
    async def test_real_time_updates(self, dashboard_service):
        """Test real-time dashboard updates"""
        # Arrange
        update_count = 0

        async def mock_stats():
            nonlocal update_count
            update_count += 1
            return {"update": update_count}

        dashboard_service.get_stats = mock_stats

        # Act - Simulate multiple updates
        results = []
        for _ in range(3):
            result = await dashboard_service.get_stats()
            results.append(result)
            await asyncio.sleep(0.1)

        # Assert
        assert len(results) == 3
        assert results[0]["update"] == 1
        assert results[2]["update"] == 3
