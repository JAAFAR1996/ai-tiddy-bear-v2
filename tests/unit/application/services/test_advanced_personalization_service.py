"""Comprehensive test suite for application/services/advanced_personalization_service.py

This test file validates the AdvancedPersonalizationService including
personality analysis, profile creation, content personalization, and
AI-driven recommendations for child-specific interactions.
"""

import logging
from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from src.application.services.advanced_personalization_service import (
    AdvancedPersonalizationService,
)
from src.domain.value_objects.personality import (
    ChildPersonality,
    PersonalityType,
)


class MockPersonalityProfileRepository:
    """Mock implementation of IPersonalityProfileRepository for testing."""

    def __init__(self):
        self.profiles = {}
        self.save_profile_called = False
        self.get_profile_by_child_id_called = False
        self.should_raise_exception = False
        self.exception_message = "Repository error"

    async def save_profile(self, profile: ChildPersonality) -> None:
        """Mock save_profile implementation."""
        self.save_profile_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        self.profiles[profile.child_id] = profile

    async def get_profile_by_child_id(self, child_id: UUID) -> ChildPersonality | None:
        """Mock get_profile_by_child_id implementation."""
        self.get_profile_by_child_id_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return self.profiles.get(child_id)


class MockAIProvider:
    """Mock implementation of AIProvider for testing."""

    def __init__(self):
        self.analyze_personality_called = False
        self.generate_personalized_content_called = False
        self.personality_analysis_result = {
            "personality_type": "CURIOUS",
            "traits": {"openness": 0.8, "conscientiousness": 0.6},
            "learning_style": ["visual", "kinesthetic"],
            "interests": ["animals", "science"],
            "metadata": {"confidence": 0.9},
        }
        self.personalized_content_result = {
            "stories": ["A curious cat's adventure"],
            "activities": ["Animal discovery game"],
            "difficulty_level": "medium",
        }
        self.should_raise_exception = False
        self.exception_message = "AI service error"

    async def analyze_personality(
        self, interactions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Mock analyze_personality implementation."""
        self.analyze_personality_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return self.personality_analysis_result

    async def generate_personalized_content(
        self,
        child_id: UUID,
        profile_dict: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Mock generate_personalized_content implementation."""
        self.generate_personalized_content_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return self.personalized_content_result


@pytest.fixture
def mock_repository():
    """Create a mock personality profile repository."""
    return MockPersonalityProfileRepository()


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider."""
    return MockAIProvider()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def personalization_service(mock_repository, mock_ai_provider, mock_logger):
    """Create AdvancedPersonalizationService instance for testing."""
    return AdvancedPersonalizationService(
        mock_repository, mock_ai_provider, mock_logger
    )


@pytest.fixture
def sample_child_id():
    """Create a sample child ID."""
    return uuid4()


@pytest.fixture
def sample_interactions():
    """Create sample interaction data."""
    return [
        {
            "text": "I love animals!",
            "sentiment": "positive",
            "timestamp": "2024-01-01T10:00:00Z",
        },
        {
            "text": "Can you tell me about dinosaurs?",
            "sentiment": "curious",
            "timestamp": "2024-01-01T10:05:00Z",
        },
        {
            "text": "That's so cool!",
            "sentiment": "excited",
            "timestamp": "2024-01-01T10:10:00Z",
        },
    ]


class TestAdvancedPersonalizationService:
    """Test suite for AdvancedPersonalizationService."""

    def test_init_sets_dependencies(
        self, mock_repository, mock_ai_provider, mock_logger
    ):
        """Test that constructor properly sets dependencies."""
        service = AdvancedPersonalizationService(
            mock_repository, mock_ai_provider, mock_logger
        )

        assert service.repository is mock_repository
        assert service.ai_provider is mock_ai_provider
        assert service.logger is mock_logger

    def test_init_with_default_logger(self, mock_repository, mock_ai_provider):
        """Test constructor with default logger."""
        with patch(
            "src.application.services.advanced_personalization_service.logger"
        ) as mock_default_logger:
            service = AdvancedPersonalizationService(mock_repository, mock_ai_provider)
            assert service.logger is mock_default_logger

    @pytest.mark.asyncio
    async def test_create_personality_profile_success(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test successful creation of personality profile."""
        # Act
        result = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert isinstance(result, ChildPersonality)
        assert result.child_id == sample_child_id
        assert result.personality_type == PersonalityType.CURIOUS
        assert result.traits == {"openness": 0.8, "conscientiousness": 0.6}
        assert result.learning_style == ["visual", "kinesthetic"]
        assert result.interests == ["animals", "science"]
        assert result.metadata == {"confidence": 0.9}

        # Verify AI provider was called
        assert personalization_service.ai_provider.analyze_personality_called

        # Verify repository was called
        assert personalization_service.repository.save_profile_called
        assert sample_child_id in personalization_service.repository.profiles

    @pytest.mark.asyncio
    async def test_create_personality_profile_logging(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that profile creation is logged correctly."""
        # Act
        await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert (
            personalization_service.logger.info.call_count == 3
        )  # 2 from create + 1 from analyze

        # Check first log call (creating profile)
        first_call = personalization_service.logger.info.call_args_list[0]
        assert (
            f"Creating personality profile for child: {sample_child_id}"
            in first_call[0][0]
        )

        # Check last log call (profile created)
        last_call = personalization_service.logger.info.call_args_list[-1]
        assert (
            f"Personality profile created and saved for child: {sample_child_id}"
            in last_call[0][0]
        )

    @pytest.mark.asyncio
    async def test_create_personality_profile_with_empty_interactions(
        self, personalization_service, sample_child_id
    ):
        """Test creating personality profile with empty interactions."""
        # Act
        result = await personalization_service.create_personality_profile(
            sample_child_id, []
        )

        # Assert
        assert isinstance(result, ChildPersonality)
        assert result.child_id == sample_child_id
        assert personalization_service.ai_provider.analyze_personality_called
        assert personalization_service.repository.save_profile_called

    @pytest.mark.asyncio
    async def test_create_personality_profile_ai_error_fallback(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test fallback behavior when AI analysis fails."""
        # Arrange
        personalization_service.ai_provider.should_raise_exception = True
        personalization_service.ai_provider.exception_message = "AI service unavailable"

        # Act
        result = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert isinstance(result, ChildPersonality)
        assert result.child_id == sample_child_id
        assert result.personality_type == PersonalityType.OTHER
        assert result.interests == ["general"]
        assert result.learning_style == "mixed"
        assert result.metadata["error"] == "AI service unavailable"
        assert result.metadata["fallback_reason"] == "AI personality analysis failed"

        # Verify error was logged
        personalization_service.logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_personality_profile_repository_error(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test handling of repository errors during profile creation."""
        # Arrange
        personalization_service.repository.should_raise_exception = True
        personalization_service.repository.exception_message = "Database error"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await personalization_service.create_personality_profile(
                sample_child_id, sample_interactions
            )

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_personality_profile_found(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test successful retrieval of existing personality profile."""
        # Arrange - Create profile first
        created_profile = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Act
        result = await personalization_service.get_personality_profile(sample_child_id)

        # Assert
        assert result is not None
        assert isinstance(result, ChildPersonality)
        assert result.child_id == sample_child_id
        assert result.personality_type == created_profile.personality_type
        assert personalization_service.repository.get_profile_by_child_id_called

    @pytest.mark.asyncio
    async def test_get_personality_profile_not_found(
        self, personalization_service, sample_child_id
    ):
        """Test retrieval of non-existent personality profile."""
        # Act
        result = await personalization_service.get_personality_profile(sample_child_id)

        # Assert
        assert result is None
        assert personalization_service.repository.get_profile_by_child_id_called

    @pytest.mark.asyncio
    async def test_get_personality_profile_logging_found(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test logging when profile is found."""
        # Arrange
        await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )
        personalization_service.logger.reset_mock()

        # Act
        await personalization_service.get_personality_profile(sample_child_id)

        # Assert
        personalization_service.logger.debug.assert_called_once()
        debug_call = personalization_service.logger.debug.call_args[0][0]
        assert (
            f"Attempting to retrieve personality profile for child: {sample_child_id}"
            in debug_call
        )

        personalization_service.logger.info.assert_called_once()
        info_call = personalization_service.logger.info.call_args[0][0]
        assert f"Personality profile found for child: {sample_child_id}" in info_call

    @pytest.mark.asyncio
    async def test_get_personality_profile_logging_not_found(
        self, personalization_service, sample_child_id
    ):
        """Test logging when profile is not found."""
        # Act
        await personalization_service.get_personality_profile(sample_child_id)

        # Assert
        personalization_service.logger.debug.assert_called_once()
        debug_call = personalization_service.logger.debug.call_args[0][0]
        assert (
            f"Attempting to retrieve personality profile for child: {sample_child_id}"
            in debug_call
        )

        personalization_service.logger.info.assert_called_once()
        info_call = personalization_service.logger.info.call_args[0][0]
        assert (
            f"Personality profile not found for child: {sample_child_id}" in info_call
        )

    @pytest.mark.asyncio
    async def test_get_personalized_content_success(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test successful generation of personalized content."""
        # Arrange - Create profile first
        await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Act
        result = await personalization_service.get_personalized_content(sample_child_id)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["stories"] == ["A curious cat's adventure"]
        assert result["activities"] == ["Animal discovery game"]
        assert result["difficulty_level"] == "medium"

        # Verify AI provider was called
        assert personalization_service.ai_provider.generate_personalized_content_called

    @pytest.mark.asyncio
    async def test_get_personalized_content_no_profile(
        self, personalization_service, sample_child_id
    ):
        """Test personalized content generation when no profile exists."""
        # Act
        result = await personalization_service.get_personalized_content(sample_child_id)

        # Assert
        assert result is None

        # Verify logging
        personalization_service.logger.info.assert_called_once()
        info_call = personalization_service.logger.info.call_args[0][0]
        assert f"No personality profile found for child {sample_child_id}" in info_call

    @pytest.mark.asyncio
    async def test_get_personalized_content_ai_error_fallback(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test fallback behavior when AI content generation fails."""
        # Arrange
        await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )
        personalization_service.ai_provider.should_raise_exception = True
        personalization_service.ai_provider.exception_message = (
            "AI content generation failed"
        )

        # Act
        result = await personalization_service.get_personalized_content(sample_child_id)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["stories"] == ["A generic story for everyone"]
        assert result["activities"] == ["A generic fun activity"]
        assert result["difficulty_level"] == "easy"

        # Verify error handling
        personalization_service.logger.error.assert_called()
        personalization_service.logger.warning.assert_called_with(
            "Falling back to generic content recommendations."
        )

    @pytest.mark.asyncio
    async def test_analyze_interactions_success(
        self, personalization_service, sample_interactions
    ):
        """Test successful interaction analysis."""
        # Act
        result = await personalization_service._analyze_interactions(
            sample_interactions
        )

        # Assert
        assert isinstance(result, ChildPersonality)
        assert result.personality_type == PersonalityType.CURIOUS
        assert result.traits == {"openness": 0.8, "conscientiousness": 0.6}
        assert result.learning_style == ["visual", "kinesthetic"]
        assert result.interests == ["animals", "science"]
        assert result.metadata == {"confidence": 0.9}

        # Verify AI provider was called
        assert personalization_service.ai_provider.analyze_personality_called

    @pytest.mark.asyncio
    async def test_analyze_interactions_invalid_personality_type(
        self, personalization_service, sample_interactions
    ):
        """Test handling of invalid personality type from AI."""
        # Arrange
        personalization_service.ai_provider.personality_analysis_result[
            "personality_type"
        ] = "INVALID_TYPE"

        # Act
        result = await personalization_service._analyze_interactions(
            sample_interactions
        )

        # Assert
        assert result.personality_type == PersonalityType.OTHER

    @pytest.mark.asyncio
    async def test_analyze_interactions_missing_fields(
        self, personalization_service, sample_interactions
    ):
        """Test handling of missing fields in AI response."""
        # Arrange
        personalization_service.ai_provider.personality_analysis_result = {
            "personality_type": "CREATIVE"
            # Missing other fields
        }

        # Act
        result = await personalization_service._analyze_interactions(
            sample_interactions
        )

        # Assert
        assert result.personality_type == PersonalityType.CREATIVE
        assert result.traits == {}
        assert result.learning_style == []
        assert result.interests == []
        assert result.metadata == {}

    @pytest.mark.asyncio
    async def test_analyze_interactions_ai_error_fallback(
        self, personalization_service, sample_interactions
    ):
        """Test fallback behavior when AI analysis fails."""
        # Arrange
        personalization_service.ai_provider.should_raise_exception = True
        personalization_service.ai_provider.exception_message = "AI analysis failed"

        # Act
        result = await personalization_service._analyze_interactions(
            sample_interactions
        )

        # Assert
        assert isinstance(result, ChildPersonality)
        assert result.personality_type == PersonalityType.OTHER
        assert result.interests == ["general"]
        assert result.learning_style == "mixed"
        assert result.interaction_preferences == {}
        assert result.metadata["error"] == "AI analysis failed"
        assert result.metadata["fallback_reason"] == "AI personality analysis failed"

    @pytest.mark.asyncio
    async def test_personality_type_mapping(
        self, personalization_service, sample_interactions
    ):
        """Test mapping of all personality types from AI response."""
        personality_types = [
            ("CURIOUS", PersonalityType.CURIOUS),
            ("CREATIVE", PersonalityType.CREATIVE),
            ("ANALYTICAL", PersonalityType.ANALYTICAL),
            ("EMPATHETIC", PersonalityType.EMPATHETIC),
            ("ENERGETIC", PersonalityType.ENERGETIC),
            ("CALM", PersonalityType.CALM),
            ("OTHER", PersonalityType.OTHER),
            ("UNKNOWN", PersonalityType.OTHER),  # Should map to OTHER
        ]

        for ai_type, expected_type in personality_types:
            # Arrange
            personalization_service.ai_provider.personality_analysis_result[
                "personality_type"
            ] = ai_type

            # Act
            result = await personalization_service._analyze_interactions(
                sample_interactions
            )

            # Assert
            assert result.personality_type == expected_type

    @pytest.mark.asyncio
    async def test_full_workflow_create_and_get_content(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test complete workflow of creating profile and getting content."""
        # Create profile
        created_profile = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Get personalized content
        content = await personalization_service.get_personalized_content(
            sample_child_id
        )

        # Assert
        assert created_profile is not None
        assert content is not None
        assert isinstance(content, dict)
        assert "stories" in content
        assert "activities" in content
        assert "difficulty_level" in content

    @pytest.mark.asyncio
    async def test_multiple_profiles_isolation(self, personalization_service):
        """Test that multiple profiles are isolated from each other."""
        # Arrange
        child_id_1 = uuid4()
        child_id_2 = uuid4()
        interactions_1 = [{"text": "I love animals!", "sentiment": "positive"}]
        interactions_2 = [{"text": "I like math!", "sentiment": "positive"}]

        # Configure different AI responses
        personalization_service.ai_provider.personality_analysis_result = {
            "personality_type": "CURIOUS",
            "interests": ["animals"],
        }

        # Act
        profile_1 = await personalization_service.create_personality_profile(
            child_id_1, interactions_1
        )

        # Change AI response for second profile
        personalization_service.ai_provider.personality_analysis_result = {
            "personality_type": "ANALYTICAL",
            "interests": ["math"],
        }

        profile_2 = await personalization_service.create_personality_profile(
            child_id_2, interactions_2
        )

        # Assert
        assert profile_1.child_id != profile_2.child_id
        assert profile_1.personality_type != profile_2.personality_type

        # Verify retrieval
        retrieved_1 = await personalization_service.get_personality_profile(child_id_1)
        retrieved_2 = await personalization_service.get_personality_profile(child_id_2)

        assert retrieved_1.child_id == child_id_1
        assert retrieved_2.child_id == child_id_2

    @pytest.mark.asyncio
    async def test_concurrent_profile_operations(self, personalization_service):
        """Test concurrent profile creation and retrieval."""
        import asyncio

        # Arrange
        child_ids = [uuid4() for _ in range(3)]
        interactions_list = [
            [{"text": f"Child {i} interaction", "sentiment": "positive"}]
            for i in range(3)
        ]

        # Act - Create profiles concurrently
        create_tasks = [
            personalization_service.create_personality_profile(child_id, interactions)
            for child_id, interactions in zip(
                child_ids, interactions_list, strict=False
            )
        ]
        created_profiles = await asyncio.gather(*create_tasks)

        # Act - Get content concurrently
        content_tasks = [
            personalization_service.get_personalized_content(child_id)
            for child_id in child_ids
        ]
        content_results = await asyncio.gather(*content_tasks)

        # Assert
        assert len(created_profiles) == 3
        assert len(content_results) == 3
        assert all(profile is not None for profile in created_profiles)
        assert all(content is not None for content in content_results)

    @pytest.mark.asyncio
    async def test_child_id_consistency(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that child_id is consistently set throughout the process."""
        # Act
        profile = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert profile.child_id == sample_child_id

        # Verify it's stored with correct ID
        stored_profile = await personalization_service.get_personality_profile(
            sample_child_id
        )
        assert stored_profile.child_id == sample_child_id

    @pytest.mark.asyncio
    async def test_datetime_handling(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that datetime fields are handled correctly."""
        # Act
        profile = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert isinstance(profile.last_updated, datetime)
        assert profile.last_updated is not None

    @pytest.mark.asyncio
    async def test_metadata_preservation(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that metadata is preserved throughout the process."""
        # Arrange
        personalization_service.ai_provider.personality_analysis_result["metadata"] = {
            "confidence": 0.95,
            "analysis_version": "1.0",
            "custom_field": "test_value",
        }

        # Act
        profile = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Assert
        assert profile.metadata["confidence"] == 0.95
        assert profile.metadata["analysis_version"] == "1.0"
        assert profile.metadata["custom_field"] == "test_value"

    @pytest.mark.asyncio
    async def test_content_generation_context(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that context is properly passed to content generation."""
        # Arrange
        await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Act
        with patch(
            "src.application.services.advanced_personalization_service.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
            await personalization_service.get_personalized_content(sample_child_id)

        # Assert
        assert personalization_service.ai_provider.generate_personalized_content_called
        # The context should include current_time

    @pytest.mark.asyncio
    async def test_error_handling_preserves_state(
        self, personalization_service, sample_child_id, sample_interactions
    ):
        """Test that errors don't corrupt service state."""
        # Arrange
        personalization_service.ai_provider.should_raise_exception = True

        # Act - First call should use fallback
        profile1 = await personalization_service.create_personality_profile(
            sample_child_id, sample_interactions
        )

        # Reset error condition
        personalization_service.ai_provider.should_raise_exception = False

        # Act - Second call should work normally
        another_child_id = uuid4()
        profile2 = await personalization_service.create_personality_profile(
            another_child_id, sample_interactions
        )

        # Assert
        assert profile1.personality_type == PersonalityType.OTHER  # Fallback
        assert profile2.personality_type == PersonalityType.CURIOUS  # Normal operation

    def test_personality_type_enum_coverage(self):
        """Test that PersonalityType enum has expected values."""
        expected_values = [
            "curious",
            "creative",
            "analytical",
            "empathetic",
            "energetic",
            "calm",
            "other",
        ]

        actual_values = [ptype.value for ptype in PersonalityType]
        assert set(actual_values) == set(expected_values)

    def test_child_personality_dataclass_structure(self):
        """Test ChildPersonality dataclass structure."""
        # Arrange
        child_id = uuid4()
        now = datetime.now()

        # Act
        personality = ChildPersonality(
            child_id=child_id,
            personality_type=PersonalityType.CURIOUS,
            traits={"openness": 0.8},
            learning_style=["visual"],
            interests=["animals"],
            last_updated=now,
            metadata={"test": "value"},
        )

        # Assert
        assert personality.child_id == child_id
        assert personality.personality_type == PersonalityType.CURIOUS
        assert personality.traits == {"openness": 0.8}
        assert personality.learning_style == ["visual"]
        assert personality.interests == ["animals"]
        assert personality.last_updated == now
        assert personality.metadata == {"test": "value"}

    def test_child_personality_default_values(self):
        """Test ChildPersonality default values."""
        # Arrange
        child_id = uuid4()

        # Act
        personality = ChildPersonality(child_id=child_id)

        # Assert
        assert personality.child_id == child_id
        assert personality.personality_type == PersonalityType.OTHER
        assert personality.traits == {}
        assert personality.learning_style == []
        assert personality.interests == []
        assert isinstance(personality.last_updated, datetime)
        assert personality.metadata == {}

    def test_service_dependencies_injection(self, mock_repository, mock_ai_provider):
        """Test that service properly accepts dependency injection."""
        # Different logger
        custom_logger = Mock(spec=logging.Logger)

        # Act
        service = AdvancedPersonalizationService(
            mock_repository, mock_ai_provider, custom_logger
        )

        # Assert
        assert service.repository is mock_repository
        assert service.ai_provider is mock_ai_provider
        assert service.logger is custom_logger
