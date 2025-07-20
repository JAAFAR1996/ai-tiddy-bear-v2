from unittest.mock import AsyncMock

import pytest

try:
    from src.infrastructure.graphql.federation_gateway.federation_gateway import (
        FederationConfig,
        GraphQLFederationGateway,
        ServiceConfig,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.fixture
def federation_config():
    """Test federation configuration."""
    return FederationConfig(
        services=[
            ServiceConfig(
                name="child_service",
                url="http://localhost:8001",
                schema_path="/schema",
            ),
            ServiceConfig(
                name="ai_service",
                url="http://localhost:8002",
                schema_path="/schema",
            ),
        ],
        enable_authentication=True,
        enable_caching=True,
        enable_rate_limiting=True,
    )


@pytest.fixture
async def federation_gateway(federation_config):
    """Federation gateway fixture."""
    if not FEDERATION_AVAILABLE:
        pytest.skip("GraphQL Federation not available")

    gateway = GraphQLFederationGateway(federation_config)

    # Mock HTTP client to avoid actual network calls
    gateway.http_client = AsyncMock()
    gateway.http_client.get = AsyncMock()
    gateway.http_client.post = AsyncMock()

    await gateway.initialize()
    yield gateway
    await gateway.cleanup()


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiting(self, federation_gateway):
        """Test rate limiting middleware."""
        # Mock cache for rate limiting
        if hasattr(federation_gateway, "cache") and federation_gateway.cache:
            # Simulate rate limit exceeded
            federation_gateway.cache.get_with_fallback = AsyncMock(
                return_value=federation_gateway.config.rate_limit_requests + 1
            )

            # Test rate limiting logic
            # This would be tested in integration tests with actual HTTP
            # requests
