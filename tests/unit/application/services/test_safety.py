"""Tests for Safety Service
Testing advanced safety and content filtering functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.application.services.safety import SafetyService
from src.domain.safety.models import (
    ContentCategory,
    RiskLevel,
    SafetyAnalysisResult,
    SafetyConfig,
)


class TestSafetyService:
    """Test the Safety Service."""

    @pytest.fixture
    def mock_ai_provider(self):
        """Create a mock AI provider."""
        provider = Mock()
        provider.analyze_toxicity = AsyncMock()
        provider.analyze_emotion = AsyncMock()
        provider.evaluate_educational_value = AsyncMock()
        provider.analyze_context = AsyncMock()
        return provider

    @pytest.fixture
    def mock_performance_monitor(self):
        """Create a mock performance monitor."""
        monitor = Mock()
        monitor.record_safety_check = AsyncMock()
        return monitor

    @pytest.fixture
    def safety_config(self):
        """Create a test safety configuration."""
        return SafetyConfig(
            keyword_blacklist=["bad word", "inappropriate", "harmful"],
            toxicity_threshold=0.7,
            enable_content_analysis=True,
            enable_emotion_analysis=True,
            enable_educational_analysis=True,
        )

    @pytest.fixture
    def safety_service(self, safety_config, mock_ai_provider, mock_performance_monitor):
        """Create a safety service instance."""
        return SafetyService(
            config=safety_config,
            ai_provider=mock_ai_provider,
            performance_monitor=mock_performance_monitor,
        )

    def test_initialization(
        self,
        safety_service,
        safety_config,
        mock_ai_provider,
        mock_performance_monitor,
    ):
        """Test safety service initialization."""
        assert safety_service.config == safety_config
        assert safety_service.ai_provider == mock_ai_provider
        assert safety_service.performance_monitor == mock_performance_monitor

    def test_analyze_harmful_content_safe_content(self, safety_service):
        """Test harmful content analysis with safe content."""
        content = "Hello, how are you today?"
        result = SafetyAnalysisResult(original_content=content)

        safety_service._analyze_harmful_content(content, result)

        assert result.is_safe is True
        assert result.risk_level == RiskLevel.NONE
        assert len(result.modifications) == 0

    def test_analyze_harmful_content_harmful_content(self, safety_service):
        """Test harmful content analysis with harmful content."""
        content = "This contains a bad word in the message"
        result = SafetyAnalysisResult(original_content=content)

        with patch("src.application.services.safety.logger") as mock_logger:
            safety_service._analyze_harmful_content(content, result)

            assert result.is_safe is False
            assert result.risk_level == RiskLevel.HIGH
            assert result.content_category == ContentCategory.HARMFUL_CONTENT
            assert len(result.modifications) == 1
            assert result.modifications[0].type == "redaction"
            assert "bad word" in result.modifications[0].description

            mock_logger.warning.assert_called_once()

    def test_analyze_harmful_content_multiple_keywords(self, safety_service):
        """Test harmful content analysis with multiple harmful keywords."""
        content = "This is inappropriate and harmful content"
        result = SafetyAnalysisResult(original_content=content)

        safety_service._analyze_harmful_content(content, result)

        assert result.is_safe is False
        assert result.risk_level == RiskLevel.HIGH
        assert len(result.modifications) == 1
        modification = result.modifications[0]
        assert "inappropriate" in modification.description
        assert "harmful" in modification.description

    def test_analyze_harmful_content_case_insensitive(self, safety_service):
        """Test harmful content analysis is case insensitive."""
        test_cases = [
            "BAD WORD here",
            "Bad Word here",
            "bad word here",
            "Contains INAPPROPRIATE content",
            "HARMFUL stuff",
        ]

        for content in test_cases:
            result = SafetyAnalysisResult(original_content=content)
            safety_service._analyze_harmful_content(content, result)

            assert result.is_safe is False
            assert result.risk_level == RiskLevel.HIGH

    def test_analyze_harmful_content_invalid_input(self, safety_service):
        """Test harmful content analysis with invalid input."""
        result = SafetyAnalysisResult(original_content="test")

        # Test with None content
        with patch("src.application.services.safety.logger") as mock_logger:
            safety_service._analyze_harmful_content(None, result)

            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "Invalid content provided" in warning_msg

        # Test with non-string content
        with patch("src.application.services.safety.logger") as mock_logger:
            safety_service._analyze_harmful_content(123, result)

            mock_logger.warning.assert_called()

    def test_analyze_harmful_content_invalid_result(self, safety_service):
        """Test harmful content analysis with invalid result object."""
        content = "test content"

        with patch("src.application.services.safety.logger") as mock_logger:
            with pytest.raises(ValueError, match="Valid SafetyAnalysisResult required"):
                safety_service._analyze_harmful_content(content, None)

            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_toxicity_success(self, safety_service, mock_ai_provider):
        """Test toxicity analysis with successful AI call."""
        content = "Test content for toxicity"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.analyze_toxicity.return_value = 0.3  # Low toxicity

        await safety_service._analyze_toxicity(content, result)

        assert result.toxicity_result is not None
        assert result.toxicity_result.score == 0.3
        assert result.is_safe is True  # Below threshold
        mock_ai_provider.analyze_toxicity.assert_called_once_with(content)

    @pytest.mark.asyncio
    async def test_analyze_toxicity_high_score(self, safety_service, mock_ai_provider):
        """Test toxicity analysis with high toxicity score."""
        content = "Toxic content example"
        result = SafetyAnalysisResult(original_content=content)
        result.is_safe = True  # Start as safe
        result.risk_level = RiskLevel.NONE

        mock_ai_provider.analyze_toxicity.return_value = 0.9  # High toxicity

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_toxicity(content, result)

            assert result.toxicity_result.score == 0.9
            assert result.is_safe is False
            assert result.risk_level == RiskLevel.MEDIUM
            assert result.content_category == ContentCategory.TOXIC_CONTENT
            assert len(result.modifications) == 1
            assert result.modifications[0].type == "flag"

            mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_toxicity_ai_error(self, safety_service, mock_ai_provider):
        """Test toxicity analysis with AI provider error."""
        content = "Test content"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.analyze_toxicity.side_effect = Exception("AI service error")

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_toxicity(content, result)

            assert result.is_safe is False
            assert result.risk_level == RiskLevel.CRITICAL
            assert len(result.modifications) == 1
            assert result.modifications[0].type == "error"
            assert "Toxicity analysis error" in result.modifications[0].description

            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_emotional_impact_success(
        self, safety_service, mock_ai_provider
    ):
        """Test emotional impact analysis with successful AI call."""
        content = "Happy and joyful content"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.analyze_emotion.return_value = "joy"

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_emotional_impact(content, result)

            assert result.emotional_impact is not None
            assert result.emotional_impact.sentiment == "joy"
            mock_ai_provider.analyze_emotion.assert_called_once_with(content)
            mock_logger.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_emotional_impact_ai_error(
        self, safety_service, mock_ai_provider
    ):
        """Test emotional impact analysis with AI provider error."""
        content = "Test content"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.analyze_emotion.side_effect = Exception(
            "Emotion analysis failed"
        )

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_emotional_impact(content, result)

            assert result.emotional_impact is not None
            assert result.emotional_impact.sentiment == "error"
            assert result.risk_level == RiskLevel.CRITICAL
            assert len(result.modifications) == 1
            assert "Emotional analysis error" in result.modifications[0].description

            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_educational_value_success(
        self, safety_service, mock_ai_provider
    ):
        """Test educational value analysis with successful AI call."""
        content = "Educational content about science"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.evaluate_educational_value.return_value = {
            "score": 0.8,
            "topics": ["science", "learning"],
        }

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_educational_value(content, result)

            assert result.educational_value is not None
            assert result.educational_value.score == 0.8
            assert result.educational_value.topics == ["science", "learning"]
            mock_ai_provider.evaluate_educational_value.assert_called_once_with(content)
            mock_logger.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_educational_value_ai_error(
        self, safety_service, mock_ai_provider
    ):
        """Test educational value analysis with AI provider error."""
        content = "Test content"
        result = SafetyAnalysisResult(original_content=content)
        mock_ai_provider.evaluate_educational_value.side_effect = Exception(
            "Educational analysis failed"
        )

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_educational_value(content, result)

            assert result.educational_value is not None
            assert result.educational_value.score == 0.0
            assert result.risk_level == RiskLevel.CRITICAL
            assert len(result.modifications) == 1
            assert (
                "Educational value analysis error"
                in result.modifications[0].description
            )

            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_context_success(self, safety_service, mock_ai_provider):
        """Test context analysis with successful AI call."""
        context = {"user_input": "What's your name?", "session_data": {}}
        result = SafetyAnalysisResult(original_content="test")
        mock_ai_provider.analyze_context.return_value = {
            "is_personal_info": True,
            "is_sensitive_topic": False,
        }

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_context(context, result)

            assert result.context_analysis is not None
            assert result.context_analysis.is_personal_info is True
            assert result.context_analysis.is_sensitive_topic is False
            mock_ai_provider.analyze_context.assert_called_once_with(context)
            mock_logger.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_context_ai_error(self, safety_service, mock_ai_provider):
        """Test context analysis with AI provider error."""
        context = {"test": "data"}
        result = SafetyAnalysisResult(original_content="test")
        mock_ai_provider.analyze_context.side_effect = Exception(
            "Context analysis failed"
        )

        with patch.object(safety_service, "logger") as mock_logger:
            await safety_service._analyze_context(context, result)

            assert result.context_analysis is not None
            assert result.context_analysis.context_safe is False
            assert result.risk_level == RiskLevel.CRITICAL
            assert len(result.modifications) == 1
            assert "Context analysis error" in result.modifications[0].description

            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_content_comprehensive(
        self, safety_service, mock_ai_provider, mock_performance_monitor
    ):
        """Test comprehensive content analysis."""
        content = "This is safe educational content about animals"
        context = {"topic": "animals", "age_group": "child"}

        # Mock AI provider responses
        mock_ai_provider.analyze_toxicity.return_value = 0.1
        mock_ai_provider.analyze_emotion.return_value = "joy"
        mock_ai_provider.evaluate_educational_value.return_value = {
            "score": 0.9,
            "topics": ["animals"],
        }
        mock_ai_provider.analyze_context.return_value = {
            "is_personal_info": False,
            "is_sensitive_topic": False,
        }

        result = await safety_service.analyze_content(content, context)

        # Verify comprehensive analysis
        assert result.original_content == content
        assert result.is_safe is True
        assert result.toxicity_result.score == 0.1
        assert result.emotional_impact.sentiment == "joy"
        assert result.educational_value.score == 0.9
        assert result.context_analysis.is_personal_info is False

        # Verify performance monitoring
        mock_performance_monitor.record_safety_check.assert_called_once_with(
            result="total_checked"
        )

    @pytest.mark.asyncio
    async def test_analyze_content_unsafe_result(
        self, safety_service, mock_ai_provider, mock_performance_monitor
    ):
        """Test content analysis with unsafe result."""
        content = "This contains inappropriate harmful content"

        # Mock responses that would make content unsafe
        mock_ai_provider.analyze_toxicity.return_value = 0.9  # High toxicity
        mock_ai_provider.analyze_emotion.return_value = "anger"
        mock_ai_provider.evaluate_educational_value.return_value = {
            "score": 0.0,
            "topics": [],
        }

        result = await safety_service.analyze_content(content)

        # Should be marked as unsafe due to keywords and high toxicity
        assert result.is_safe is False
        assert result.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]

        # Verify blocked content was recorded
        assert mock_performance_monitor.record_safety_check.call_count == 2
        calls = mock_performance_monitor.record_safety_check.call_args_list
        assert calls[0][1]["result"] == "total_checked"
        assert calls[1][1]["result"] == "blocked_content"

    @pytest.mark.asyncio
    async def test_analyze_content_without_context(
        self, safety_service, mock_ai_provider
    ):
        """Test content analysis without context."""
        content = "Safe content without context"

        mock_ai_provider.analyze_toxicity.return_value = 0.2
        mock_ai_provider.analyze_emotion.return_value = "neutral"
        mock_ai_provider.evaluate_educational_value.return_value = {
            "score": 0.5,
            "topics": [],
        }

        result = await safety_service.analyze_content(content)

        assert result.original_content == content
        assert result.context_analysis is None  # No context provided

        # Other analyses should still run
        assert result.toxicity_result is not None
        assert result.emotional_impact is not None
        assert result.educational_value is not None

    @pytest.mark.asyncio
    async def test_concurrent_content_analysis(
        self, safety_service, mock_ai_provider, mock_performance_monitor
    ):
        """Test concurrent content analysis."""
        import asyncio

        contents = [
            "First safe content",
            "Second safe content",
            "Third educational content",
        ]

        # Mock consistent responses
        mock_ai_provider.analyze_toxicity.return_value = 0.1
        mock_ai_provider.analyze_emotion.return_value = "neutral"
        mock_ai_provider.evaluate_educational_value.return_value = {
            "score": 0.7,
            "topics": [],
        }

        # Analyze concurrently
        tasks = [safety_service.analyze_content(content) for content in contents]
        results = await asyncio.gather(*tasks)

        # All should be analyzed successfully
        assert len(results) == 3
        assert all(r.is_safe for r in results)
        assert all(r.toxicity_result.score == 0.1 for r in results)

        # Performance monitoring should be called for each
        assert mock_performance_monitor.record_safety_check.call_count == 3

    def test_get_metrics_deprecated_warning(self, safety_service):
        """Test that get_metrics shows deprecation warning."""
        with patch.object(safety_service, "logger") as mock_logger:
            metrics = safety_service.get_metrics()

            assert metrics == {}
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "deprecated" in warning_msg
            assert "PerformanceMonitor" in warning_msg

    @pytest.mark.asyncio
    async def test_risk_level_escalation(self, safety_service, mock_ai_provider):
        """Test that risk levels escalate properly."""
        content = "Test content"
        result = SafetyAnalysisResult(original_content=content)

        # Start with low risk
        result.risk_level = RiskLevel.NONE

        # Simulate high toxicity
        mock_ai_provider.analyze_toxicity.return_value = 0.9
        await safety_service._analyze_toxicity(content, result)
        assert result.risk_level == RiskLevel.MEDIUM

        # Simulate AI error (should escalate to CRITICAL)
        mock_ai_provider.analyze_emotion.side_effect = Exception("Error")
        await safety_service._analyze_emotional_impact(content, result)
        assert result.risk_level == RiskLevel.CRITICAL

    @pytest.mark.asyncio
    async def test_modification_tracking(self, safety_service, mock_ai_provider):
        """Test that modifications are properly tracked."""
        content = "inappropriate harmful content"

        # Mock AI errors to generate modifications
        mock_ai_provider.analyze_toxicity.side_effect = Exception("Toxicity error")
        mock_ai_provider.analyze_emotion.side_effect = Exception("Emotion error")
        mock_ai_provider.evaluate_educational_value.side_effect = Exception(
            "Educational error"
        )

        result = await safety_service.analyze_content(content)

        # Should have modifications from harmful content + AI errors
        assert len(result.modifications) >= 4  # 1 harmful + 3 AI errors

        modification_types = [mod.type for mod in result.modifications]
        assert "redaction" in modification_types  # From harmful content
        assert modification_types.count("error") >= 3  # From AI errors

    @pytest.mark.asyncio
    async def test_empty_content_handling(self, safety_service, mock_ai_provider):
        """Test handling of empty or whitespace content."""
        empty_contents = ["", "   ", "\n\t\n", None]

        for content in empty_contents:
            # Should handle gracefully without crashing
            if content is None:
                # None content should be handled in harmful content analysis
                result = SafetyAnalysisResult(original_content="")
                safety_service._analyze_harmful_content(content, result)
            else:
                result = await safety_service.analyze_content(content)
                assert isinstance(result, SafetyAnalysisResult)

    @pytest.mark.parametrize(
        "toxicity_score,expected_safe",
        [
            (0.0, True),
            (0.3, True),
            (0.6, True),
            (0.7, False),  # At threshold
            (0.8, False),
            (1.0, False),
        ],
    )
    @pytest.mark.asyncio
    async def test_toxicity_threshold_boundaries(
        self, safety_service, mock_ai_provider, toxicity_score, expected_safe
    ):
        """Test toxicity threshold boundary conditions."""
        content = "Test content"
        result = SafetyAnalysisResult(original_content=content)
        result.is_safe = True  # Start as safe

        mock_ai_provider.analyze_toxicity.return_value = toxicity_score

        await safety_service._analyze_toxicity(content, result)

        if expected_safe:
            # Should remain safe or not be marked unsafe by toxicity
            assert result.toxicity_result.score == toxicity_score
        else:
            # Should be marked unsafe
            assert result.is_safe is False
            assert result.risk_level >= RiskLevel.MEDIUM

    @pytest.mark.asyncio
    async def test_error_handling_comprehensive(self, safety_service, mock_ai_provider):
        """Test comprehensive error handling across all analysis methods."""
        content = "Test content for error handling"
        context = {"test": "context"}

        # Make all AI calls fail
        mock_ai_provider.analyze_toxicity.side_effect = Exception("Toxicity failed")
        mock_ai_provider.analyze_emotion.side_effect = Exception("Emotion failed")
        mock_ai_provider.evaluate_educational_value.side_effect = Exception(
            "Educational failed"
        )
        mock_ai_provider.analyze_context.side_effect = Exception("Context failed")

        with patch.object(safety_service, "logger"):
            result = await safety_service.analyze_content(content, context)

            # Should complete analysis despite all AI failures
            assert isinstance(result, SafetyAnalysisResult)
            assert result.original_content == content
            assert result.risk_level == RiskLevel.CRITICAL
            # One for each failed analysis
            assert len(result.modifications) >= 4
