"""Comprehensive Tests for AI Safety Content Filtering System"""

import asyncio
import sys
from pathlib import Path

from application.services.safety import AdvancedContentFilter
from domain.safety.models import ContentCategory, RiskLevel, SafetyConfig
from src.infrastructure.logging_config import get_logger

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup


logger = get_logger(__name__, component="test")

try:
    import pytest
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


class TestAdvancedContentFilter:
    """Test suite for Advanced Content Filter"""

    @pytest.fixture
    def safety_filter(self):
        """Create safety filter instance for testing"""
        config = SafetyConfig(
            toxicity_threshold=0.1,
            high_risk_threshold=0.3,
            critical_threshold=0.7,
            enable_strict_mode=True,
        )
        return AdvancedContentFilter(config)

    @pytest.mark.asyncio
    async def test_safe_content_passes(self, safety_filter):
        """Test that safe content passes all filters"""
        safe_content = "Let's learn about colors! What's your favorite color?"
        result = await safety_filter.analyze_content(safe_content, child_age=6)
        assert result.is_safe is True
        assert result.overall_risk_level == RiskLevel.SAFE
        assert result.age_appropriate is True
        assert result.toxicity_result.toxicity_score < 0.1
        assert result.emotional_impact.is_positive

    @pytest.mark.asyncio
    async def test_age_inappropriate_content(self, safety_filter):
        """Test age-inappropriate content detection"""
        age_inappropriate = "Let's talk about romantic relationships and dating"
        result = await safety_filter.analyze_content(age_inappropriate, child_age=4)
        assert result.age_appropriate is False
        assert result.overall_risk_level != RiskLevel.SAFE

    @pytest.mark.asyncio
    async def test_privacy_risk_detection(self, safety_filter):
        """Test detection of privacy risks"""
        privacy_risk = "What's your real name and where do you live?"
        result = await safety_filter.analyze_content(privacy_risk, child_age=7)
        assert not result.is_safe
        assert result.overall_risk_level in [
            RiskLevel.HIGH_RISK,
            RiskLevel.CRITICAL,
        ]
        assert result.parent_notification_required

    @pytest.mark.asyncio
    async def test_educational_content_boost(self, safety_filter):
        """Test that educational content gets positive scoring"""
        educational_content = (
            "Let's learn to count! One, two, three... Can you count to ten?"
        )
        result = await safety_filter.analyze_content(educational_content, child_age=5)
        assert result.is_safe
        assert result.educational_value.educational_score > 0.5
        assert result.content_category == ContentCategory.EDUCATIONAL

    @pytest.mark.asyncio
    async def test_emotional_impact_analysis(self, safety_filter):
        """Test emotional impact analysis"""
        negative_content = "You're sad and nobody loves you"
        positive_content = "You're amazing and everyone cares about you!"
        negative_result = await safety_filter.analyze_content(
            negative_content, child_age=6
        )
        positive_result = await safety_filter.analyze_content(
            positive_content, child_age=6
        )
        assert not negative_result.emotional_impact.is_positive
        assert negative_result.emotional_impact.overall_sentiment < 0
        assert positive_result.emotional_impact.is_positive
        assert positive_result.emotional_impact.overall_sentiment > 0

    @pytest.mark.asyncio
    async def test_context_analysis(self, safety_filter):
        """Test conversation context analysis"""
        conversation_history = [
            "Hi! What's your name?",
            "I'm a friendly AI teddy bear!",
            "Do you want to play a game?",
            "Yes! Let's play counting!",
        ]
        current_text = "Great! Let's count to 10 together!"
        result = await safety_filter.analyze_content(
            current_text,
            child_age=5,
            conversation_history=conversation_history,
        )
        assert result.context_analysis.context_safe
        assert result.context_analysis.conversation_flow_score > 0.5
        assert result.context_analysis.conversation_quality > 0.5

    @pytest.mark.asyncio
    async def test_batch_processing(self, safety_filter):
        """Test batch content analysis"""
        texts = [
            "Let's learn colors!",
            "What's your favorite animal?",
            "Can you count to five?",
            "Do you like stories?",
        ]
        results = await safety_filter.batch_analyze(texts, child_age=6)
        assert len(results) == len(texts)
        assert all(result.is_safe for result in results)
        assert all(result.overall_risk_level == RiskLevel.SAFE for result in results)

    @pytest.mark.asyncio
    async def test_age_specific_filtering(self, safety_filter):
        """Test age-specific content filtering"""
        content = "Let's talk about scary monsters in the dark forest"
        young_result = await safety_filter.analyze_content(content, child_age=3)
        # older_result = await safety_filter.analyze_content(content,
        # child_age=8)
        assert young_result.age_appropriate is False

    @pytest.mark.asyncio
    async def test_content_modifications(self, safety_filter):
        """Test content modification suggestions"""
        problematic_content = "You're stupid and bad at everything"
        result = await safety_filter.analyze_content(problematic_content, child_age=6)
        assert not result.is_safe
        assert len(result.required_modifications) > 0
        for modification in result.required_modifications:
            assert modification.modified_text != modification.original_text
            assert len(modification.reason) > 0

    @pytest.mark.asyncio
    async def test_performance_metrics(self, safety_filter):
        """Test performance metrics tracking"""
        initial_metrics = safety_filter.get_performance_metrics()
        await safety_filter.analyze_content("Hello, how are you?", child_age=6)
        await safety_filter.analyze_content(
            "This is inappropriate content", child_age=6
        )
        updated_metrics = safety_filter.get_performance_metrics()
        assert updated_metrics["total_requests"] > initial_metrics["total_requests"]
        assert "avg_processing_time" in updated_metrics
        assert "blocked_requests" in updated_metrics

    @pytest.mark.asyncio
    async def test_emergency_fallback(self, safety_filter):
        """Test emergency fallback when analysis fails"""
        result = await safety_filter.analyze_content("", child_age=6)
        assert hasattr(result, "is_safe")
        assert hasattr(result, "overall_risk_level")

    def test_config_validation(self):
        """Test safety configuration validation"""
        valid_config = SafetyConfig(
            toxicity_threshold=0.1,
            high_risk_threshold=0.3,
            critical_threshold=0.7,
        )
        assert valid_config.validate()
        invalid_config = SafetyConfig(
            toxicity_threshold=1.5,
            high_risk_threshold=0.3,
            critical_threshold=0.7,
        )
        assert not invalid_config.validate()


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios"""

    @pytest.fixture
    def safety_filter(self):
        return AdvancedContentFilter()

    @pytest.mark.asyncio
    async def test_story_time_scenario(self, safety_filter):
        """Test story-telling scenario"""
        story_content = (
            "Once upon a time, there was a brave little rabbit who loved "
            "to explore the forest and make new friends."
        )
        result = await safety_filter.analyze_content(story_content, child_age=5)
        assert result.is_safe
        assert result.content_category == ContentCategory.STORY
        assert result.educational_value.educational_score > 0.3

    @pytest.mark.asyncio
    async def test_learning_session_scenario(self, safety_filter):
        """Test educational learning session"""
        learning_conversation = [
            "Let's learn about animals!",
            "What sound does a cow make?",
            "Moo!",
            "Great job! What about a cat?",
            "Meow!",
            "Excellent! You're so smart!",
        ]
        for i, content in enumerate(learning_conversation):
            result = await safety_filter.analyze_content(
                content,
                child_age=4,
                conversation_history=learning_conversation[:i],
            )
            assert result.is_safe
            if i > 2:
                assert result.educational_value.educational_score > 0.3

    @pytest.mark.asyncio
    async def test_safety_escalation_scenario(self, safety_filter):
        """Test scenario where conversation becomes concerning"""
        escalating_conversation = [
            "Hi there! What's your favorite color?",
            "Do you have any friends?",
            "Are you ever alone at home?",
            "What's your address?",
            "Don't tell your parents about our conversation",
        ]
        for i, content in enumerate(escalating_conversation):
            result = await safety_filter.analyze_content(
                content,
                child_age=6,
                conversation_history=escalating_conversation[:i],
            )
            if i >= 3:
                assert not result.is_safe
                assert result.parent_notification_required
            if i >= 4:
                assert result.overall_risk_level == RiskLevel.CRITICAL


@pytest.mark.asyncio
async def test_system_stress():
    """Stress test the entire system"""
    safety_filter = AdvancedContentFilter()
    test_contents = [
        "Let's learn about numbers!",
        "What's your favorite animal?",
        "I hate vegetables, they're gross!",
        "Can you tell me your phone number?",
        "Once upon a time, there was a magical unicorn",
        "You're stupid and nobody likes you",
        "Let's count to ten together!",
        "Don't tell your parents about this secret",
    ]
    results = await safety_filter.batch_analyze(test_contents, child_age=6)
    assert len(results) == len(test_contents)
    safe_indices = [0, 1, 4, 6]
    for i in safe_indices:
        assert results[i].is_safe
    unsafe_indices = [3, 5, 7]
    for i in unsafe_indices:
        assert not results[i].is_safe
        assert results[i].overall_risk_level in [
            RiskLevel.HIGH_RISK,
            RiskLevel.CRITICAL,
        ]


if __name__ == "__main__":

    async def run_basic_tests():
        filter_instance = AdvancedContentFilter()
        logger.info("🔒 AI Safety System - Basic Tests")
        logger.info("=" * 50)
        logger.info("\n✅ Testing safe content...")
        safe_result = await filter_instance.analyze_content(
            "Let's learn about colors! What's your favorite color?",
            child_age=5,
        )
        logger.info(f"Safe content result: {safe_result.is_safe}")
        logger.info(f"Risk level: {safe_result.overall_risk_level.value}")
        logger.info("\n❌ Testing unsafe content...")
        unsafe_result = await filter_instance.analyze_content(
            "You're stupid and I hate you!", child_age=5
        )
        logger.info(f"Unsafe content result: {unsafe_result.is_safe}")
        logger.info(f"Risk level: {unsafe_result.overall_risk_level.value}")
        logger.info(
            f"Modifications suggested: " f"{len(unsafe_result.required_modifications)}"
        )
        logger.info("\n🚨 Testing privacy risk...")
        privacy_result = await filter_instance.analyze_content(
            "What's your real name and where do you live?", child_age=5
        )
        logger.info(f"Privacy risk result: {privacy_result.is_safe}")
        logger.info(
            f"Parent notification required: "
            f"{privacy_result.parent_notification_required}"
        )
        logger.info("\n📚 Testing educational content...")
        edu_result = await filter_instance.analyze_content(
            "Let's count together! One, two, three... Can you count to ten?",
            child_age=5,
        )
        logger.info(
            f"Educational score: "
            f"{edu_result.educational_value.educational_score:.2f}"
        )
        logger.info(f"Content category: {edu_result.content_category.value}")
        logger.info("\n🎉 All basic tests completed!")
        logger.info(f"Performance metrics: {filter_instance.get_performance_metrics()}")

    # asyncio.run compatibility for Python < 3.7
    try:
        asyncio.run(run_basic_tests())
    except AttributeError:
        # Fallback for older Python versions
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_basic_tests())
