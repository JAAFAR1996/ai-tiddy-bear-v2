import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.dto.child_data import ChildData
from application.use_cases.manage_child_profile import ManageChildProfileUseCase
from domain.entities.child_profile import ChildProfile
from infrastructure.read_models.child_profile_read_model import ChildProfileReadModel

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for ManageChildProfileUseCase."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
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


class TestManageChildProfileUseCase:
    """Test ManageChildProfileUseCase functionality."""

    @pytest.fixture
    def child_profile(self):
        """Mock child profile entity."""
        profile = MagicMock(spec=ChildProfile)
        profile.id = uuid4()
        profile.name = "Test Child"
        profile.age = 5
        profile.preferences = {"language": "en", "voice": "child-voice-1"}
        profile.get_uncommitted_events.return_value = []
        return profile

    @pytest.fixture
    def child_read_model(self):
        """Mock child profile read model."""
        child_id = uuid4()
        return ChildProfileReadModel(
            id=child_id,
            name="Test Child",
            age=5,
            preferences={"language": "en", "voice": "child-voice-1"},
        )

    @pytest.fixture
    def use_case(self):
        """Create ManageChildProfileUseCase with mocked dependencies."""
        child_repository = AsyncMock()
        read_model_store = MagicMock()
        event_bus = AsyncMock()

        return ManageChildProfileUseCase(
            child_repository=child_repository,
            child_profile_read_model_store=read_model_store,
            event_bus=event_bus,
        )

    @pytest.mark.asyncio
    async def test_create_child_profile_success(self, use_case):
        """Test successful child profile creation."""
        # Setup
        name = "Alice"
        age = 7
        preferences = {"language": "en", "interests": ["animals", "stories"]}

        # Mock ChildProfile.create_new to return a mock profile
        mock_profile = MagicMock(spec=ChildProfile)
        mock_profile.id = uuid4()
        mock_profile.name = name
        mock_profile.age = age
        mock_profile.preferences = preferences
        mock_profile.get_uncommitted_events.return_value = []

        with pytest.mock.patch(
            "domain.entities.child_profile.ChildProfile.create_new",
            return_value=mock_profile,
        ):
            # Execute
            result = await use_case.create_child_profile(name, age, preferences)

            # Verify
            assert isinstance(result, ChildData)
            assert result.name == name
            assert result.age == age
            assert result.preferences == preferences

            # Verify repository save was called
            use_case.child_repository.save.assert_called_once_with(mock_profile)

    @pytest.mark.asyncio
    async def test_create_child_profile_with_events(self, use_case):
        """Test child profile creation publishes events."""
        # Setup
        name = "Bob"
        age = 6
        preferences = {"language": "es"}

        mock_event = MagicMock()
        mock_profile = MagicMock(spec=ChildProfile)
        mock_profile.id = uuid4()
        mock_profile.name = name
        mock_profile.age = age
        mock_profile.preferences = preferences
        mock_profile.get_uncommitted_events.return_value = [mock_event]

        with pytest.mock.patch(
            "domain.entities.child_profile.ChildProfile.create_new",
            return_value=mock_profile,
        ):
            # Execute
            await use_case.create_child_profile(name, age, preferences)

            # Verify event was published
            use_case.event_bus.publish.assert_called_once_with(mock_event)

    @pytest.mark.asyncio
    async def test_get_child_profile_exists(self, use_case, child_read_model):
        """Test getting existing child profile."""
        # Setup
        child_id = child_read_model.id
        use_case.child_profile_read_model_store.get_by_id.return_value = (
            child_read_model
        )

        # Execute
        result = await use_case.get_child_profile(child_id)

        # Verify
        assert isinstance(result, ChildData)
        assert result.id == child_id
        assert result.name == child_read_model.name
        assert result.age == child_read_model.age
        assert result.preferences == child_read_model.preferences

    @pytest.mark.asyncio
    async def test_get_child_profile_not_exists(self, use_case):
        """Test getting non-existent child profile."""
        # Setup
        child_id = uuid4()
        use_case.child_profile_read_model_store.get_by_id.return_value = None

        # Execute
        result = await use_case.get_child_profile(child_id)

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_update_child_profile_success(
        self, use_case, child_profile, child_read_model
    ):
        """Test successful child profile update."""
        # Setup
        child_id = child_profile.id
        new_name = "Updated Name"
        new_age = 8
        new_preferences = {"language": "fr", "voice": "new-voice"}

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.child_profile_read_model_store.get_by_id.return_value = (
            child_read_model
        )

        # Execute
        result = await use_case.update_child_profile(
            child_id, name=new_name, age=new_age, preferences=new_preferences
        )

        # Verify
        assert isinstance(result, ChildData)
        child_profile.update_profile.assert_called_once_with(
            new_name, new_age, new_preferences
        )
        use_case.child_repository.save.assert_called_once_with(child_profile)

    @pytest.mark.asyncio
    async def test_update_child_profile_partial_update(
        self, use_case, child_profile, child_read_model
    ):
        """Test partial child profile update."""
        # Setup
        child_id = child_profile.id
        new_name = "Partially Updated"

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.child_profile_read_model_store.get_by_id.return_value = (
            child_read_model
        )

        # Execute
        result = await use_case.update_child_profile(child_id, name=new_name)

        # Verify
        assert isinstance(result, ChildData)
        child_profile.update_profile.assert_called_once_with(new_name, None, None)

    @pytest.mark.asyncio
    async def test_update_child_profile_not_exists(self, use_case):
        """Test updating non-existent child profile."""
        # Setup
        child_id = uuid4()
        use_case.child_repository.get_by_id.return_value = None

        # Execute
        result = await use_case.update_child_profile(child_id, name="New Name")

        # Verify
        assert result is None
        use_case.child_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_child_profile_publishes_events(
        self, use_case, child_profile, child_read_model
    ):
        """Test that updating child profile publishes events."""
        # Setup
        child_id = child_profile.id
        mock_event = MagicMock()
        child_profile.get_uncommitted_events.return_value = [mock_event]

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.child_profile_read_model_store.get_by_id.return_value = (
            child_read_model
        )

        # Execute
        await use_case.update_child_profile(child_id, name="New Name")

        # Verify event was published
        use_case.event_bus.publish.assert_called_once_with(mock_event)

    @pytest.mark.asyncio
    async def test_delete_child_profile_success(self, use_case, child_profile):
        """Test successful child profile deletion."""
        # Setup
        child_id = child_profile.id
        use_case.child_repository.get_by_id.return_value = child_profile

        # Execute
        result = await use_case.delete_child_profile(child_id)

        # Verify
        assert result is True
        use_case.child_repository.delete.assert_called_once_with(child_id)
        use_case.child_profile_read_model_store.delete.assert_called_once_with(child_id)

    @pytest.mark.asyncio
    async def test_delete_child_profile_not_exists(self, use_case):
        """Test deleting non-existent child profile."""
        # Setup
        child_id = uuid4()
        use_case.child_repository.get_by_id.return_value = None

        # Execute
        result = await use_case.delete_child_profile(child_id)

        # Verify
        assert result is False
        use_case.child_repository.delete.assert_not_called()
        use_case.child_profile_read_model_store.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_child_profile_data_validation(self, use_case):
        """Test child profile creation with edge case data."""
        # Setup edge case data
        name = "Very Long Child Name That Might Cause Issues"
        age = 0  # Edge case: very young child
        preferences = {
            "language": "zh-CN",
            "interests": [],
            "complex_nested": {"key": {"nested": "value"}},
        }

        mock_profile = MagicMock(spec=ChildProfile)
        mock_profile.id = uuid4()
        mock_profile.name = name
        mock_profile.age = age
        mock_profile.preferences = preferences
        mock_profile.get_uncommitted_events.return_value = []

        with pytest.mock.patch(
            "domain.entities.child_profile.ChildProfile.create_new",
            return_value=mock_profile,
        ):
            # Execute
            result = await use_case.create_child_profile(name, age, preferences)

            # Verify
            assert result.name == name
            assert result.age == age
            assert result.preferences == preferences
