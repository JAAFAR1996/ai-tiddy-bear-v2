import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# !/usr/bin/env python3

"""
Comprehensive Unit Tests for Child Repository
Tests all CRUD operations,  search functionality,  and business logic
"""

import os
import tempfile
from datetime import date, datetime, timedelta
from unittest.mock import Mock

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

from domain.entities.child import Child
from infrastructure.persistence.child_sqlite_repository import ChildSQLiteRepository


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def mock_session_factory():
    """Mock session factory for testing"""
    return Mock()


@pytest.fixture
def child_repository(temp_db, mock_session_factory):
    """Create a Child repository instance for testing"""
    repo = ChildSQLiteRepository(mock_session_factory, temp_db)
    return repo


@pytest.fixture
def sample_child_data():
    """Sample child data for testing"""
    return {
        "id": "test-child-001",
        "name": "Alice",
        "age": 8,
        "date_of_birth": date(2015, 5, 15),
        "gender": "female",
        "personality_traits": ["curious", "creative", "energetic"],
        "learning_preferences": {"visual": 0.8, "auditory": 0.6, "kinesthetic": 0.4},
        "communication_style": "playful",
        "max_daily_interaction_time": 3600,
        "total_interaction_time": 1200,
        "last_interaction": datetime.now() - timedelta(hours=2),
        "allowed_topics": ["science", "stories", "games"],
        "restricted_topics": ["violence", "adult_content"],
        "language_preference": "en",
        "cultural_background": "american",
        "parental_controls": {"bedtime_mode": True, "content_filter": "strict"},
        "emergency_contacts": [
            {"name": "Mom", "phone": "+1234567890", "relation": "parent"},
            {"name": "Dad", "phone": "+1234567891", "relation": "parent"},
        ],
        "medical_notes": "No known allergies",
        "educational_level": "elementary",
        "special_needs": ["adhd_support"],
        "is_active": True,
        "privacy_settings": {"data_sharing": False, "analytics": True},
        "custom_settings": {"favorite_color": "blue", "pet_name": "Fluffy"},
    }


@pytest.fixture
def sample_child(sample_child_data):
    """Create a sample Child entity"""
    return Child(**sample_child_data)


class TestChildRepositoryBasicOperations:
    """Test basic CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_child(self, child_repository, sample_child):
        """Test creating a new child"""
        #  Act
        result = await child_repository.create(sample_child)
        #  Assert
        assert result is not None
        assert result.id is not None
        assert result.name == sample_child.name
        assert result.age == sample_child.age
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_get_child_by_id(self, child_repository, sample_child):
        """Test retrieving a child by ID"""
        #  Arrange
        created_child = await child_repository.create(sample_child)
        #  Act
        retrieved_child = await child_repository.get_by_id(created_child.id)
        #  Assert
        assert retrieved_child is not None
        assert retrieved_child.id == created_child.id
        assert retrieved_child.name == sample_child.name
        assert retrieved_child.personality_traits == sample_child.personality_traits

    @pytest.mark.asyncio
    async def test_update_child(self, child_repository, sample_child):
        """Test updating an existing child"""
        #  Arrange
        created_child = await child_repository.create(sample_child)
        created_child.name = "Alice Updated"
        created_child.age = 9
        #  Act
        updated_child = await child_repository.update(created_child)
        #  Assert
        assert updated_child.name == "Alice Updated"
        assert updated_child.age == 9

    @pytest.mark.asyncio
    async def test_delete_child(self, child_repository, sample_child):
        """Test soft deleting a child"""
        #  Arrange
        created_child = await child_repository.create(sample_child)
        #  Act
        delete_result = await child_repository.delete(created_child.id)
        #  Assert
        assert delete_result is True

    @pytest.mark.asyncio
    async def test_list_children(self, child_repository):
        """Test listing multiple children"""
        #  Arrange
        children_data = [
            {"name": "Alice", "age": 8},
            {"name": "Bob", "age": 10},
            {"name": "Charlie", "age": 6},
        ]
        created_children = []
        for data in children_data:
            child = Child(
                name=data["name"],
                age=data["age"],
                personality_traits=[],
                learning_preferences={},
            )
            created_children.append(await child_repository.create(child))
        #  Act
        all_children = await child_repository.list()
        #  Assert
        assert len(all_children) >= 3


class TestChildRepositorySearchAndFiltering:
    """Test search and filtering functionality"""

    @pytest.mark.asyncio
    async def test_find_by_name(self, child_repository, sample_child):
        """Test finding a child by name"""
        #  Arrange
        await child_repository.create(sample_child)
        #  Act
        found_child = await child_repository.find_by_name(sample_child.name)
        #  Assert
        assert found_child is not None
        assert found_child.name == sample_child.name

    @pytest.mark.asyncio
    async def test_find_by_age_range(self, child_repository):
        """Test finding children by age range"""
        #  Arrange
        children = [
            Child(name="Young", age=5, personality_traits=[], learning_preferences={}),
            Child(name="Middle", age=8, personality_traits=[], learning_preferences={}),
            Child(name="Older", age=12, personality_traits=[], learning_preferences={}),
        ]
        for child in children:
            await child_repository.create(child)
        #  Act
        children_in_range = await child_repository.find_by_age_range(6, 10)
        #  Assert
        assert len(children_in_range) >= 1
        ages = [child.age for child in children_in_range]
        assert all(6 <= age <= 10 for age in ages)


class TestChildRepositoryBusinessLogic:
    """Test business logic and advanced functionality"""

    @pytest.mark.asyncio
    async def test_get_children_needing_attention(self, child_repository):
        """Test finding children that need attention"""
        #  Arrange
        old_interaction_child = Child(
            name="Old Interaction",
            age=8,
            last_interaction=datetime.now() - timedelta(days=5),
            personality_traits=[],
            learning_preferences={},
        )
        special_needs_child = Child(
            name="Special Needs",
            age=8,
            special_needs=["autism"],
            personality_traits=[],
            learning_preferences={},
        )
        await child_repository.create(old_interaction_child)
        await child_repository.create(special_needs_child)
        #  Act
        attention_needed = await child_repository.get_children_needing_attention()
        #  Assert
        assert len(attention_needed) >= 2

    @pytest.mark.asyncio
    async def test_get_engagement_insights(self, child_repository, sample_child):
        """Test generating engagement insights"""
        #  Arrange
        created_child = await child_repository.create(sample_child)
        #  Act
        insights = await child_repository.get_engagement_insights(created_child.id)
        #  Assert
        assert insights is not None
        assert "child_id" in insights
        assert "engagement_level" in insights
        assert "recommendations" in insights
        assert insights["child_id"] == created_child.id


if __name__ == "__main__":
    #  Run tests
    pytest.main([__file__, "-v", "--tb=short"])
