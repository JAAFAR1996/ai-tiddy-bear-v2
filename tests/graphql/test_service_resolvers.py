import pytest

try:
    from src.infrastructure.graphql.service_resolvers.service_resolvers import (
        AIServiceResolvers,
        ChildServiceResolvers,
        MonitoringServiceResolvers,
        SafetyServiceResolvers,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestServiceResolvers:
    """Test service resolvers."""

    @pytest.mark.asyncio
    async def test_child_service_resolvers(self):
        """Test child service resolvers."""
        # Test get_child
        child = await ChildServiceResolvers.get_child("test-child-id")
        assert child is not None
        assert child.id == "test-child-id"
        assert child.name == "Ahmed"

        # Test get_children
        children = await ChildServiceResolvers.get_children("parent-123")
        assert len(children) == 2
        assert all(child.parent_id == "parent-123" for child in children)

    @pytest.mark.asyncio
    async def test_ai_service_resolvers(self):
        """Test AI service resolvers."""
        ai_profile = await AIServiceResolvers.get_ai_profile("child-123")
        assert ai_profile is not None
        assert len(ai_profile.personality_traits) > 0

    @pytest.mark.asyncio
    async def test_monitoring_service_resolvers(self):
        """Test monitoring service resolvers."""
        usage_stats = await MonitoringServiceResolvers.get_usage_statistics(
            "child-123", "daily"
        )
        assert usage_stats is not None
        assert usage_stats.total_session_time > 0

    @pytest.mark.asyncio
    async def test_safety_service_resolvers(self):
        """Test safety service resolvers."""
        safety_profile = await SafetyServiceResolvers.get_safety_profile("child-123")
        assert safety_profile is not None
        assert safety_profile.safety_score > 0
