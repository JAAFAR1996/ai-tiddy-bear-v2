"""Comprehensive test suite for application/services/accessibility_service.py

This test file validates the AccessibilityService including
profile creation, retrieval, adaptation recommendations, and
accessibility settings management for children with special needs.
"""

import logging
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from src.application.services.accessibility_service import AccessibilityService
from src.domain.value_objects.accessibility import (
    AccessibilityProfile,
    SpecialNeedType,
)


class MockAccessibilityProfileRepository:
    """Mock implementation of IAccessibilityProfileRepository for testing."""

    def __init__(self):
        self.profiles = {}
        self.save_profile_called = False
        self.get_profile_by_child_id_called = False
        self.should_raise_exception = False
        self.exception_message = "Repository error"

    async def save_profile(self, profile: AccessibilityProfile) -> None:
        """Mock save_profile implementation."""
        self.save_profile_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        self.profiles[profile.child_id] = profile

    async def get_profile_by_child_id(
        self, child_id: UUID
    ) -> AccessibilityProfile | None:
        """Mock get_profile_by_child_id implementation."""
        self.get_profile_by_child_id_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return self.profiles.get(child_id)


class MockAccessibilityConfig:
    """Mock implementation of AccessibilityConfig for testing."""

    def __init__(self):
        self.adaptation_rules = {
            "visual_impairment": [
                "audio_descriptions",
                "high_contrast",
                "large_text",
            ],
            "hearing_impairment": [
                "visual_indicators",
                "subtitles",
                "sign_language",
            ],
            "speech_impairment": [
                "alternative_input",
                "extended_timeout",
                "simplified_responses",
            ],
            "cognitive_delay": [
                "simplified_language",
                "repetition",
                "visual_cues",
            ],
            "motor_impairment": [
                "voice_control",
                "simplified_interface",
                "large_buttons",
            ],
            "sensory_sensitivity": [
                "reduced_stimuli",
                "calming_colors",
                "gentle_sounds",
            ],
        }

        self.accessibility_settings_rules = {
            "visual_impairment": {
                "visual_enabled": False,
                "audio_enabled": True,
                "high_contrast": True,
            },
            "hearing_impairment": {
                "audio_enabled": False,
                "visual_enabled": True,
                "subtitles_enabled": True,
            },
            "motor_impairment": {"simplified_ui": True, "voice_control": True},
            "cognitive_delay": {"simplified_ui": True, "slower_pace": True},
        }


@pytest.fixture
def mock_repository():
    """Create a mock accessibility profile repository."""
    return MockAccessibilityProfileRepository()


@pytest.fixture
def mock_config():
    """Create a mock accessibility config."""
    return MockAccessibilityConfig()


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def accessibility_service(mock_repository, mock_config, mock_logger):
    """Create AccessibilityService instance for testing."""
    return AccessibilityService(mock_repository, mock_config, mock_logger)


@pytest.fixture
def sample_child_id():
    """Create a sample child ID."""
    return uuid4()


@pytest.fixture
def sample_special_needs():
    """Create a sample list of special needs."""
    return [
        SpecialNeedType.VISUAL_IMPAIRMENT,
        SpecialNeedType.HEARING_IMPAIRMENT,
    ]


class TestAccessibilityService:
    """Test suite for AccessibilityService."""

    def test_init_sets_dependencies(self, mock_repository, mock_config, mock_logger):
        """Test that constructor properly sets dependencies."""
        service = AccessibilityService(mock_repository, mock_config, mock_logger)

        assert service.repository is mock_repository
        assert service.config is mock_config
        assert service.logger is mock_logger

    def test_init_with_default_logger(self, mock_repository, mock_config):
        """Test constructor with default logger."""
        with patch(
            "src.application.services.accessibility_service.logger"
        ) as mock_default_logger:
            service = AccessibilityService(mock_repository, mock_config)
            assert service.logger is mock_default_logger

    @pytest.mark.asyncio
    async def test_create_accessibility_profile_success(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test successful creation of accessibility profile."""
        # Act
        result = await accessibility_service.create_accessibility_profile(
            sample_child_id, sample_special_needs
        )

        # Assert
        assert isinstance(result, AccessibilityProfile)
        assert result.child_id == sample_child_id
        assert result.special_needs == sample_special_needs
        assert result.preferred_interaction_mode == "voice"
        assert result.voice_speed_adjustment == 1.0
        assert result.volume_level == 0.8
        assert result.subtitles_enabled is False
        assert result.additional_settings == {}

        # Verify repository was called
        assert accessibility_service.repository.save_profile_called
        assert sample_child_id in accessibility_service.repository.profiles

    @pytest.mark.asyncio
    async def test_create_accessibility_profile_logging(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test that profile creation is logged correctly."""
        # Act
        await accessibility_service.create_accessibility_profile(
            sample_child_id, sample_special_needs
        )

        # Assert
        assert accessibility_service.logger.info.call_count == 2

        # Check first log call (creating profile)
        first_call = accessibility_service.logger.info.call_args_list[0]
        assert (
            f"Creating accessibility profile for child: {sample_child_id}"
            in first_call[0][0]
        )

        # Check second log call (profile created)
        second_call = accessibility_service.logger.info.call_args_list[1]
        assert (
            f"Accessibility profile created and saved for child: {sample_child_id}"
            in second_call[0][0]
        )

    @pytest.mark.asyncio
    async def test_create_accessibility_profile_with_empty_needs(
        self, accessibility_service, sample_child_id
    ):
        """Test creating accessibility profile with empty special needs."""
        # Act
        result = await accessibility_service.create_accessibility_profile(
            sample_child_id, []
        )

        # Assert
        assert isinstance(result, AccessibilityProfile)
        assert result.child_id == sample_child_id
        assert result.special_needs == []
        assert accessibility_service.repository.save_profile_called

    @pytest.mark.asyncio
    async def test_create_accessibility_profile_with_all_needs(
        self, accessibility_service, sample_child_id
    ):
        """Test creating accessibility profile with all special needs types."""
        all_needs = list(SpecialNeedType)

        # Act
        result = await accessibility_service.create_accessibility_profile(
            sample_child_id, all_needs
        )

        # Assert
        assert isinstance(result, AccessibilityProfile)
        assert result.child_id == sample_child_id
        assert result.special_needs == all_needs
        assert accessibility_service.repository.save_profile_called

    @pytest.mark.asyncio
    async def test_create_accessibility_profile_repository_error(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test handling of repository errors during profile creation."""
        # Arrange
        accessibility_service.repository.should_raise_exception = True
        accessibility_service.repository.exception_message = "Database error"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await accessibility_service.create_accessibility_profile(
                sample_child_id, sample_special_needs
            )

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_accessibility_profile_found(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test successful retrieval of existing accessibility profile."""
        # Arrange - Create profile first
        created_profile = await accessibility_service.create_accessibility_profile(
            sample_child_id, sample_special_needs
        )

        # Act
        result = await accessibility_service.get_accessibility_profile(sample_child_id)

        # Assert
        assert result is not None
        assert isinstance(result, AccessibilityProfile)
        assert result.child_id == sample_child_id
        assert result.special_needs == sample_special_needs
        assert accessibility_service.repository.get_profile_by_child_id_called

    @pytest.mark.asyncio
    async def test_get_accessibility_profile_not_found(
        self, accessibility_service, sample_child_id
    ):
        """Test retrieval of non-existent accessibility profile."""
        # Act
        result = await accessibility_service.get_accessibility_profile(sample_child_id)

        # Assert
        assert result is None
        assert accessibility_service.repository.get_profile_by_child_id_called

    @pytest.mark.asyncio
    async def test_get_accessibility_profile_logging_found(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test logging when profile is found."""
        # Arrange
        await accessibility_service.create_accessibility_profile(
            sample_child_id, sample_special_needs
        )
        accessibility_service.logger.reset_mock()

        # Act
        await accessibility_service.get_accessibility_profile(sample_child_id)

        # Assert
        accessibility_service.logger.debug.assert_called_once()
        debug_call = accessibility_service.logger.debug.call_args[0][0]
        assert (
            f"Attempting to retrieve accessibility profile for child: {sample_child_id}"
            in debug_call
        )

        accessibility_service.logger.info.assert_called_once()
        info_call = accessibility_service.logger.info.call_args[0][0]
        assert f"Accessibility profile found for child: {sample_child_id}" in info_call

    @pytest.mark.asyncio
    async def test_get_accessibility_profile_logging_not_found(
        self, accessibility_service, sample_child_id
    ):
        """Test logging when profile is not found."""
        # Act
        await accessibility_service.get_accessibility_profile(sample_child_id)

        # Assert
        accessibility_service.logger.debug.assert_called_once()
        debug_call = accessibility_service.logger.debug.call_args[0][0]
        assert (
            f"Attempting to retrieve accessibility profile for child: {sample_child_id}"
            in debug_call
        )

        accessibility_service.logger.info.assert_called_once()
        info_call = accessibility_service.logger.info.call_args[0][0]
        assert (
            f"Accessibility profile not found for child: {sample_child_id}" in info_call
        )

    @pytest.mark.asyncio
    async def test_get_accessibility_profile_repository_error(
        self, accessibility_service, sample_child_id
    ):
        """Test handling of repository errors during profile retrieval."""
        # Arrange
        accessibility_service.repository.should_raise_exception = True
        accessibility_service.repository.exception_message = "Database connection error"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await accessibility_service.get_accessibility_profile(sample_child_id)

        assert "Database connection error" in str(exc_info.value)

    def test_get_adaptations_single_need(self, accessibility_service):
        """Test getting adaptations for a single special need."""
        # Arrange
        needs = [SpecialNeedType.VISUAL_IMPAIRMENT]

        # Act
        result = accessibility_service._get_adaptations(needs)

        # Assert
        expected = ["audio_descriptions", "high_contrast", "large_text"]
        assert set(result) == set(expected)

    def test_get_adaptations_multiple_needs(self, accessibility_service):
        """Test getting adaptations for multiple special needs."""
        # Arrange
        needs = [
            SpecialNeedType.VISUAL_IMPAIRMENT,
            SpecialNeedType.HEARING_IMPAIRMENT,
        ]

        # Act
        result = accessibility_service._get_adaptations(needs)

        # Assert
        expected = [
            "audio_descriptions",
            "high_contrast",
            "large_text",
            "visual_indicators",
            "subtitles",
            "sign_language",
        ]
        assert set(result) == set(expected)

    def test_get_adaptations_removes_duplicates(self, accessibility_service):
        """Test that get_adaptations removes duplicate recommendations."""
        # Arrange - modify config to have overlapping adaptations
        accessibility_service.config.adaptation_rules["visual_impairment"] = [
            "audio_descriptions",
            "high_contrast",
        ]
        accessibility_service.config.adaptation_rules["hearing_impairment"] = [
            "high_contrast",
            "subtitles",
        ]
        needs = [
            SpecialNeedType.VISUAL_IMPAIRMENT,
            SpecialNeedType.HEARING_IMPAIRMENT,
        ]

        # Act
        result = accessibility_service._get_adaptations(needs)

        # Assert
        expected = ["audio_descriptions", "high_contrast", "subtitles"]
        assert set(result) == set(expected)
        assert len(result) == len(set(result))  # No duplicates

    def test_get_adaptations_empty_needs(self, accessibility_service):
        """Test getting adaptations with empty needs list."""
        # Arrange
        needs = []

        # Act
        result = accessibility_service._get_adaptations(needs)

        # Assert
        assert result == []

    def test_get_adaptations_unknown_need(self, accessibility_service):
        """Test getting adaptations for unknown special need."""
        # Arrange
        needs = [SpecialNeedType.OTHER]

        # Act
        result = accessibility_service._get_adaptations(needs)

        # Assert
        assert result == []  # No adaptations for unknown need

    def test_get_accessibility_settings_default(self, accessibility_service):
        """Test getting accessibility settings with default values."""
        # Arrange
        needs = []

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        expected = {
            "audio_enabled": True,
            "visual_enabled": True,
            "simplified_ui": False,
        }
        assert result == expected

    def test_get_accessibility_settings_visual_impairment(self, accessibility_service):
        """Test accessibility settings for visual impairment."""
        # Arrange
        needs = [SpecialNeedType.VISUAL_IMPAIRMENT]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["visual_enabled"] is False
        assert result["audio_enabled"] is True
        assert result["high_contrast"] is True

    def test_get_accessibility_settings_hearing_impairment(self, accessibility_service):
        """Test accessibility settings for hearing impairment."""
        # Arrange
        needs = [SpecialNeedType.HEARING_IMPAIRMENT]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["audio_enabled"] is False
        assert result["visual_enabled"] is True
        assert result["subtitles_enabled"] is True

    def test_get_accessibility_settings_motor_impairment(self, accessibility_service):
        """Test accessibility settings for motor impairment."""
        # Arrange
        needs = [SpecialNeedType.MOTOR_IMPAIRMENT]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["simplified_ui"] is True
        assert result["voice_control"] is True

    def test_get_accessibility_settings_cognitive_delay(self, accessibility_service):
        """Test accessibility settings for cognitive delay."""
        # Arrange
        needs = [SpecialNeedType.COGNITIVE_DELAY]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["simplified_ui"] is True
        assert result["slower_pace"] is True

    def test_get_accessibility_settings_multiple_needs(self, accessibility_service):
        """Test accessibility settings for multiple special needs."""
        # Arrange
        needs = [
            SpecialNeedType.VISUAL_IMPAIRMENT,
            SpecialNeedType.HEARING_IMPAIRMENT,
        ]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["visual_enabled"] is False  # Visual impairment override
        assert result["audio_enabled"] is False  # Hearing impairment override
        assert result["high_contrast"] is True  # From visual impairment
        assert result["subtitles_enabled"] is True  # From hearing impairment

    def test_get_accessibility_settings_motor_and_cognitive(
        self, accessibility_service
    ):
        """Test accessibility settings for motor and cognitive impairments."""
        # Arrange
        needs = [
            SpecialNeedType.MOTOR_IMPAIRMENT,
            SpecialNeedType.COGNITIVE_DELAY,
        ]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["simplified_ui"] is True
        assert result["voice_control"] is True
        assert result["slower_pace"] is True

    def test_get_accessibility_settings_config_override(self, accessibility_service):
        """Test that config overrides are applied correctly."""
        # Arrange
        needs = [SpecialNeedType.VISUAL_IMPAIRMENT]
        accessibility_service.config.accessibility_settings_rules["visual_impairment"][
            "custom_setting"
        ] = "custom_value"

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        assert result["custom_setting"] == "custom_value"

    def test_get_accessibility_settings_speech_impairment(self, accessibility_service):
        """Test accessibility settings for speech impairment."""
        # Arrange
        needs = [SpecialNeedType.SPEECH_IMPAIRMENT]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        # Should not affect core audio/visual settings
        assert result["audio_enabled"] is True
        assert result["visual_enabled"] is True
        assert result["simplified_ui"] is False

    def test_get_accessibility_settings_sensory_sensitivity(
        self, accessibility_service
    ):
        """Test accessibility settings for sensory sensitivity."""
        # Arrange
        needs = [SpecialNeedType.SENSORY_SENSITIVITY]

        # Act
        result = accessibility_service._get_accessibility_settings(needs)

        # Assert
        # Should not affect core audio/visual settings
        assert result["audio_enabled"] is True
        assert result["visual_enabled"] is True
        assert result["simplified_ui"] is False

    @pytest.mark.asyncio
    async def test_full_workflow_create_and_retrieve(
        self, accessibility_service, sample_child_id, sample_special_needs
    ):
        """Test complete workflow of creating and retrieving a profile."""
        # Create profile
        created_profile = await accessibility_service.create_accessibility_profile(
            sample_child_id, sample_special_needs
        )

        # Retrieve profile
        retrieved_profile = await accessibility_service.get_accessibility_profile(
            sample_child_id
        )

        # Assert
        assert retrieved_profile is not None
        assert retrieved_profile.child_id == created_profile.child_id
        assert retrieved_profile.special_needs == created_profile.special_needs
        assert (
            retrieved_profile.preferred_interaction_mode
            == created_profile.preferred_interaction_mode
        )

    @pytest.mark.asyncio
    async def test_multiple_profiles_isolation(self, accessibility_service):
        """Test that multiple profiles are isolated from each other."""
        # Arrange
        child_id_1 = uuid4()
        child_id_2 = uuid4()
        needs_1 = [SpecialNeedType.VISUAL_IMPAIRMENT]
        needs_2 = [SpecialNeedType.HEARING_IMPAIRMENT]

        # Act
        profile_1 = await accessibility_service.create_accessibility_profile(
            child_id_1, needs_1
        )
        profile_2 = await accessibility_service.create_accessibility_profile(
            child_id_2, needs_2
        )

        # Assert
        assert profile_1.child_id != profile_2.child_id
        assert profile_1.special_needs != profile_2.special_needs

        # Verify retrieval
        retrieved_1 = await accessibility_service.get_accessibility_profile(child_id_1)
        retrieved_2 = await accessibility_service.get_accessibility_profile(child_id_2)

        assert retrieved_1.special_needs == needs_1
        assert retrieved_2.special_needs == needs_2

    @pytest.mark.asyncio
    async def test_concurrent_profile_operations(self, accessibility_service):
        """Test concurrent profile creation and retrieval."""
        import asyncio

        # Arrange
        child_ids = [uuid4() for _ in range(5)]
        needs_list = [
            [SpecialNeedType.VISUAL_IMPAIRMENT],
            [SpecialNeedType.HEARING_IMPAIRMENT],
            [SpecialNeedType.MOTOR_IMPAIRMENT],
            [SpecialNeedType.COGNITIVE_DELAY],
            [SpecialNeedType.SPEECH_IMPAIRMENT],
        ]

        # Act - Create profiles concurrently
        create_tasks = [
            accessibility_service.create_accessibility_profile(child_id, needs)
            for child_id, needs in zip(child_ids, needs_list, strict=False)
        ]
        created_profiles = await asyncio.gather(*create_tasks)

        # Act - Retrieve profiles concurrently
        retrieve_tasks = [
            accessibility_service.get_accessibility_profile(child_id)
            for child_id in child_ids
        ]
        retrieved_profiles = await asyncio.gather(*retrieve_tasks)

        # Assert
        assert len(created_profiles) == 5
        assert len(retrieved_profiles) == 5
        assert all(profile is not None for profile in retrieved_profiles)

    def test_special_need_type_enum_values(self):
        """Test that SpecialNeedType enum has expected values."""
        expected_values = [
            "visual_impairment",
            "hearing_impairment",
            "speech_impairment",
            "cognitive_delay",
            "motor_impairment",
            "sensory_sensitivity",
            "other",
        ]

        actual_values = [need.value for need in SpecialNeedType]
        assert set(actual_values) == set(expected_values)

    def test_accessibility_profile_dataclass_structure(self):
        """Test AccessibilityProfile dataclass structure."""
        # Arrange
        child_id = uuid4()
        special_needs = [SpecialNeedType.VISUAL_IMPAIRMENT]

        # Act
        profile = AccessibilityProfile(
            child_id=child_id,
            special_needs=special_needs,
            preferred_interaction_mode="voice",
            voice_speed_adjustment=0.8,
            volume_level=0.9,
            subtitles_enabled=True,
            additional_settings={"custom": "value"},
        )

        # Assert
        assert profile.child_id == child_id
        assert profile.special_needs == special_needs
        assert profile.preferred_interaction_mode == "voice"
        assert profile.voice_speed_adjustment == 0.8
        assert profile.volume_level == 0.9
        assert profile.subtitles_enabled is True
        assert profile.additional_settings == {"custom": "value"}

    def test_accessibility_profile_default_values(self):
        """Test AccessibilityProfile default values."""
        # Arrange
        child_id = uuid4()

        # Act
        profile = AccessibilityProfile(child_id=child_id)

        # Assert
        assert profile.child_id == child_id
        assert profile.special_needs == []
        assert profile.preferred_interaction_mode == "voice"
        assert profile.voice_speed_adjustment == 1.0
        assert profile.volume_level == 0.8
        assert profile.subtitles_enabled is False
        assert profile.additional_settings == {}

    @pytest.mark.asyncio
    async def test_error_handling_preserves_state(
        self, accessibility_service, sample_child_id
    ):
        """Test that errors don't corrupt service state."""
        # Arrange
        accessibility_service.repository.should_raise_exception = True

        # Act & Assert
        with pytest.raises(Exception):
            await accessibility_service.create_accessibility_profile(
                sample_child_id, []
            )

        # Reset error condition
        accessibility_service.repository.should_raise_exception = False

        # Should still work after error
        profile = await accessibility_service.create_accessibility_profile(
            sample_child_id, []
        )
        assert profile is not None

    def test_private_method_accessibility(self, accessibility_service):
        """Test that private methods are accessible for testing."""
        # These methods should be available for testing
        assert hasattr(accessibility_service, "_get_adaptations")
        assert hasattr(accessibility_service, "_get_accessibility_settings")
        assert callable(accessibility_service._get_adaptations)
        assert callable(accessibility_service._get_accessibility_settings)

    def test_service_dependencies_injection(self, mock_repository, mock_config):
        """Test that service properly accepts dependency injection."""
        # Different logger
        custom_logger = Mock(spec=logging.Logger)

        # Act
        service = AccessibilityService(mock_repository, mock_config, custom_logger)

        # Assert
        assert service.repository is mock_repository
        assert service.config is mock_config
        assert service.logger is custom_logger
