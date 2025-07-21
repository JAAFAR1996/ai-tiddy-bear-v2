from unittest.mock import AsyncMock

import pytest

try:
    from src.infrastructure.graphql.authentication import create_auth_service
    from src.infrastructure.graphql.authentication.authentication import (
        UserRole,
    )
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


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestCacheIntegration:
    """Test cache integration with federation."""

    @pytest.mark.asyncio
    async def test_query_caching(self, federation_gateway):
        """Test GraphQL query caching."""
        if not federation_gateway.cache:
            pytest.skip("Cache not available")

        # Mock cache hit
        federation_gateway.cache.get_with_fallback = AsyncMock(
            return_value={"data": {"child": {"name": "Cached Child"}}}
        )

        query = 'query { child(id: "123") { name } }'
        result = await federation_gateway._execute_federated_query(query, {})

        assert result["data"]["child"]["name"] == "Cached Child"

    @pytest.mark.asyncio
    async def test_authentication_caching(self, auth_service):
        """Test authentication token caching."""
        if not auth_service.cache:
            pytest.skip("Cache not available")

        import secrets

        test_password4 = secrets.token_urlsafe(16)
        user = await auth_service.create_user(
            "cacheuser", "cache@example.com", test_password4, UserRole.PARENT
        )

        token = await auth_service.create_access_token(user)

        # First verification should cache the result
        verified_user = await auth_service.verify_token(token)
        assert verified_user.id == user.id

        # Second verification should use cache
        verified_user = await auth_service.verify_token(token)
        assert verified_user.id == user.id
