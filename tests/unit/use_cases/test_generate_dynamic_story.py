from domain.entities.child_profile import ChildProfile
from application.dto.story_response import StoryResponse
from application.dto.story_request import StoryRequest
from application.use_cases.generate_dynamic_story import (
    GenerateDynamicStoryUseCase,
)
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for GenerateDynamicStoryUseCase."""

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


class TestGenerateDynamicStoryUseCase:
    """Test GenerateDynamicStoryUseCase functionality."""

    @pytest.fixture
    def child_profile(self):
        """Mock child profile."""
        profile = MagicMock(spec=ChildProfile)
        profile.id = uuid4()
        profile.name = "Emma"
        profile.age = 6
        profile.preferences = {
            "language": "en",
            "interests": ["animals", "adventure"],
            "favorite_characters": ["princess", "talking animals"],
            "reading_level": "beginner",
        }
        return profile

    @pytest.fixture
    def story_request(self):
        """Mock story request."""
        return StoryRequest(
            child_id=uuid4(),
            theme="friendship",
            characters=["rabbit", "owl"],
            setting="enchanted forest",
            moral_lesson="helping others",
            story_length="short",
        )

    @pytest.fixture
    def story_response(self):
        """Mock story response."""
        return StoryResponse(
            title="The Helpful Rabbit and Wise Owl",
            content="Once upon a time, in an enchanted forest, there lived a kind rabbit named Rosie and a wise owl named Oliver...",
            characters=["Rosie the Rabbit", "Oliver the Owl"],
            moral_lesson="Helping friends makes everyone happy",
            estimated_duration=5,
            age_appropriate=True,
            safety_checked=True,
            personalization_score=0.9,
        )

    @pytest.fixture
    def use_case(self):
        """Create GenerateDynamicStoryUseCase with mocked dependencies."""
        dynamic_story_service = AsyncMock()
        child_repository = AsyncMock()

        return GenerateDynamicStoryUseCase(
            dynamic_story_service=dynamic_story_service,
            child_repository=child_repository,
        )

    @pytest.mark.asyncio
    async def test_execute_success(
        self, use_case, story_request, child_profile, story_response
    ):
        """Test successful story generation."""
        # Setup
        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            story_response
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify
        assert isinstance(result, StoryResponse)
        assert result.title == "The Helpful Rabbit and Wise Owl"
        assert result.moral_lesson == "Helping friends makes everyone happy"
        assert result.age_appropriate is True
        assert result.safety_checked is True

        # Verify service calls
        use_case.child_repository.get_by_id.assert_called_once_with(
            story_request.child_id
        )
        use_case.dynamic_story_service.generate_story.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_child_not_found(self, use_case, story_request):
        """Test story generation when child profile not found."""
        # Setup
        use_case.child_repository.get_by_id.return_value = None

        # Execute
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(story_request)

        assert "Child profile not found" in str(exc_info.value)
        use_case.dynamic_story_service.generate_story.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_personalized_story(
        self, use_case, child_profile, story_response
    ):
        """Test that story is personalized based on child preferences."""
        # Setup
        story_request = StoryRequest(
            child_id=child_profile.id,
            theme="adventure",
            characters=None,  # Should use child's preferences
            setting=None,  # Should use child's preferences
            moral_lesson=None,
            story_length="medium",
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            story_response
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify personalization
        assert result.personalization_score > 0.8  # High personalization

        # Verify service was called with child preferences
        call_args = use_case.dynamic_story_service.generate_story.call_args
        assert call_args[1]["child_profile"] == child_profile
        assert call_args[1]["theme"] == "adventure"

    @pytest.mark.asyncio
    async def test_execute_age_appropriate_content(
        self, use_case, child_profile, story_request
    ):
        """Test that generated story is age-appropriate."""
        # Setup for younger child
        child_profile.age = 3
        child_profile.preferences["reading_level"] = "toddler"

        age_appropriate_story = StoryResponse(
            title="The Happy Little Duck",
            content="Quack! Quack! said the little duck. The duck was very happy in the pond...",
            characters=["Little Duck"],
            moral_lesson="Being happy is wonderful",
            estimated_duration=2,
            age_appropriate=True,
            safety_checked=True,
            personalization_score=0.85,
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            age_appropriate_story
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify age-appropriate content
        assert result.estimated_duration <= 3  # Short for young child
        assert result.age_appropriate is True
        assert result.safety_checked is True
        assert len(result.content.split()) < 100  # Simple vocabulary

    @pytest.mark.asyncio
    async def test_execute_with_custom_characters(
        self, use_case, child_profile, story_response
    ):
        """Test story generation with custom characters."""
        # Setup
        story_request = StoryRequest(
            child_id=child_profile.id,
            theme="space adventure",
            characters=["astronaut cat", "robot dog", "alien friend"],
            setting="spaceship",
            moral_lesson="teamwork",
            story_length="long",
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            story_response
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify custom elements were used
        call_args = use_case.dynamic_story_service.generate_story.call_args
        assert "astronaut cat" in call_args[1]["characters"]
        assert "robot dog" in call_args[1]["characters"]
        assert call_args[1]["setting"] == "spaceship"
        assert call_args[1]["moral_lesson"] == "teamwork"

    @pytest.mark.asyncio
    async def test_execute_safety_validation(
        self, use_case, child_profile, story_request
    ):
        """Test that safety validation is performed."""
        # Setup story that might need safety checking
        potentially_unsafe_story = StoryResponse(
            title="The Adventure Story",
            content="This story contains some elements that needed safety review...",
            characters=["Hero", "Helper"],
            moral_lesson="Being brave",
            estimated_duration=7,
            age_appropriate=True,
            safety_checked=True,  # Should be validated
            personalization_score=0.7,
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            potentially_unsafe_story
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify safety was checked
        assert result.safety_checked is True
        assert result.age_appropriate is True

    @pytest.mark.asyncio
    async def test_execute_story_length_preferences(
        self, use_case, child_profile
    ):
        """Test story generation with different length preferences."""
        # Test short story
        short_request = StoryRequest(
            child_id=child_profile.id, theme="bedtime", story_length="short"
        )

        short_story = StoryResponse(
            title="Sleepy Time Tale",
            content="A short, calming bedtime story...",
            characters=["Sleepy Bear"],
            moral_lesson="Rest is important",
            estimated_duration=3,
            age_appropriate=True,
            safety_checked=True,
            personalization_score=0.8,
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            short_story
        )

        # Execute
        result = await use_case.execute(short_request)

        # Verify short story characteristics
        assert result.estimated_duration <= 5
        assert (
            "short"
            in use_case.dynamic_story_service.generate_story.call_args[1][
                "story_length"
            ]
        )

    @pytest.mark.asyncio
    async def test_execute_multilingual_support(
        self, use_case, child_profile, story_request
    ):
        """Test story generation in different languages."""
        # Setup Spanish-speaking child
        child_profile.preferences["language"] = "es"

        spanish_story = StoryResponse(
            title="El Conejo Amable y el Búho Sabio",
            content="Había una vez, en un bosque encantado, un conejo amable llamado Rosa...",
            characters=["Rosa la Coneja", "Oliverio el Búho"],
            moral_lesson="Ayudar a los amigos hace feliz a todos",
            estimated_duration=5,
            age_appropriate=True,
            safety_checked=True,
            personalization_score=0.9,
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            spanish_story
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify language-appropriate content
        assert "Rosa la Coneja" in result.characters
        assert "bosque encantado" in result.content

        # Verify service received language preference
        call_args = use_case.dynamic_story_service.generate_story.call_args
        assert call_args[1]["child_profile"].preferences["language"] == "es"

    @pytest.mark.asyncio
    async def test_execute_moral_lesson_integration(
        self, use_case, child_profile, story_request
    ):
        """Test that moral lessons are properly integrated."""
        # Setup request with specific moral lesson
        story_request.moral_lesson = "sharing is caring"

        moral_story = StoryResponse(
            title="The Sharing Bears",
            content="The bears learned that sharing their honey made everyone happier...",
            characters=["Bear Family"],
            moral_lesson="Sharing makes everyone happy",
            estimated_duration=6,
            age_appropriate=True,
            safety_checked=True,
            personalization_score=0.85,
        )

        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.dynamic_story_service.generate_story.return_value = (
            moral_story
        )

        # Execute
        result = await use_case.execute(story_request)

        # Verify moral lesson integration
        assert "sharing" in result.moral_lesson.lower()
        assert "sharing" in result.content.lower()

        call_args = use_case.dynamic_story_service.generate_story.call_args
        assert call_args[1]["moral_lesson"] == "sharing is caring"
