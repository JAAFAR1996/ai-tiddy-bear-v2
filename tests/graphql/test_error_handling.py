from unittest.mock import AsyncMock

import pytest

try:
    from src.infrastructure.graphql.authentication import create_auth_service
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


@pytest.fixture
async def auth_service(auth_config):
    """Authentication service fixture."""
    return await create_auth_service(auth_config)


@pytest.mark.skipif(
    not FEDERATION_AVAILABLE, reason="Federation not available"
)
class TestErrorHandling:
    """Test error handling in federation."""

    @pytest.mark.asyncio
    async def test_service_error_handling(self, federation_gateway):
        """Test handling of service errors."""
        # Mock service error
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = (
            500
        )
        federation_gateway.http_client.post.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Internal Server Error"
        )

        # Test error handling in service query
        config = federation_gateway.services["child_service"]

        with pytest.raises(Exception):
            await federation_gateway._query_service(
                config, "query { child { name } }", {}, None
            )

    @pytest.mark.asyncio
    async def test_authentication_errors(self, auth_service):
        """Test authentication error handling."""
        # Test invalid token
        invalid_user = await auth_service.verify_token("invalid-token")
        assert invalid_user is None

        # Test rate limiting
        # Simulate multiple failed login attempts
        for _ in range(6):  # Exceed max attempts
            await auth_service.authenticate_user("nonexistent", "wrong")

        # Should be rate limited now
        with pytest.raises(Exception):  # Should raise HTTP 429
            await auth_service.authenticate_user("nonexistent", "wrong")
