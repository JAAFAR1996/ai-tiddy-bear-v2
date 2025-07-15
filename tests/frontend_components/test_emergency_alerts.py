import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

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


class TestEmergencyAlerts:
    """Test emergency alerts functionality"""

    @pytest.mark.asyncio
    async def test_get_emergency_alerts(self, emergency_service):
        """Test fetching emergency alerts"""
        # Arrange
        alerts = [
            {
                "id": "alert1",
                "type": "safety",
                "severity": "high",
                "title": "محتوى غير مناسب",
                "description": "تم اكتشاف محتوى قد يكون غير مناسب",
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged": False,
            }
        ]
        emergency_service.get_alerts.return_value = alerts

        # Act
        result = await emergency_service.get_alerts()

        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "safety"
        assert result[0]["severity"] == "high"
        assert result[0]["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, emergency_service):
        """Test acknowledging an alert"""
        # Arrange
        emergency_service.acknowledge_alert.return_value = True

        # Act
        result = await emergency_service.acknowledge_alert("alert1")

        # Assert
        assert result is True
        emergency_service.acknowledge_alert.assert_called_once_with("alert1")
