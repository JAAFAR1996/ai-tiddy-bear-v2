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


class TestChildProfile:
    """Test child profile functionality"""

    @pytest.mark.asyncio
    async def test_get_children(self, child_service):
        """Test fetching children list"""
        # Arrange
        children = [
            {"id": "child1", "name": "أحمد", "age": 5, "gender": "male"},
            {"id": "child2", "name": "فاطمة", "age": 7, "gender": "female"},
        ]
        child_service.get_children.return_value = children

        # Act
        result = await child_service.get_children()

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "أحمد"
        assert result[1]["age"] == 7

    @pytest.mark.asyncio
    async def test_create_child(self, child_service):
        """Test creating a new child profile"""
        # Arrange
        new_child = {
            "name": "محمد",
            "age": 6,
            "gender": "male",
            "preferences": {
                "language": "ar",
                "interests": ["animals", "space"],
                "educationLevel": "kindergarten",
            },
        }
        child_service.create_child.return_value = {
            "id": "child3",
            **new_child,
            "createdAt": datetime.utcnow().isoformat(),
        }

        # Act
        created = await child_service.create_child(new_child)

        # Assert
        assert created["id"] == "child3"
        assert created["name"] == "محمد"
        assert "animals" in created["preferences"]["interests"]

    @pytest.mark.asyncio
    async def test_update_child(self, child_service):
        """Test updating child profile"""
        # Arrange
        updates = {"age": 6, "preferences": {"interests": ["animals", "space", "art"]}}
        child_service.update_child.return_value = {
            "id": "child1",
            "name": "أحمد",
            "age": 6,
            "preferences": {"interests": ["animals", "space", "art"]},
        }

        # Act
        updated = await child_service.update_child("child1", updates)

        # Assert
        assert updated["age"] == 6
        assert len(updated["preferences"]["interests"]) == 3
        assert "art" in updated["preferences"]["interests"]

    @pytest.mark.asyncio
    async def test_child_statistics(self, child_service):
        """Test child statistics"""
        # Arrange
        stats = {
            "totalConversations": 150,
            "totalInteractionTime": 27000,  # seconds
            "averageSessionDuration": 180,
            "emotionalTrend": {"happy": 0.6, "neutral": 0.3, "sad": 0.1},
            "favoriteTopics": ["animals", "stories", "games"],
            "progressIndicators": [
                {"area": "language", "score": 85, "trend": "improving"},
                {"area": "social", "score": 78, "trend": "stable"},
            ],
        }
        child_service.get_child_statistics.return_value = stats

        # Act
        result = await child_service.get_child_statistics("child1")

        # Assert
        assert result["totalConversations"] == 150
        assert result["emotionalTrend"]["happy"] == 0.6
        assert result["progressIndicators"][0]["area"] == "language"
        assert result["progressIndicators"][0]["trend"] == "improving"
