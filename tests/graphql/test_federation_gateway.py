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
                name="child_service", url="http://localhost:8001", schema_path="/schema"
            ),
            ServiceConfig(
                name="ai_service", url="http://localhost:8002", schema_path="/schema"
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
class TestGraphQLFederationGateway:
    """Test GraphQL Federation Gateway."""

    @pytest.mark.asyncio
    async def test_gateway_initialization(self, federation_config):
        """Test gateway initialization."""
        gateway = GraphQLFederationGateway(federation_config)

        # Mock dependencies
        gateway.http_client = AsyncMock()
        gateway.http_client.get.return_value.__aenter__.return_value.status_code = 200

        result = await gateway.initialize()
        assert result is True

        await gateway.cleanup()

    @pytest.mark.asyncio
    async def test_service_health_check(self, federation_gateway):
        """Test service health checking."""
        # Mock successful health check
        federation_gateway.http_client.get.return_value.__aenter__.return_value.status_code = (
            200
        )

        config = federation_gateway.services["child_service"]
        healthy = await federation_gateway._check_single_service_health(config)

        assert healthy is True

    @pytest.mark.asyncio
    async def test_query_service_analysis(self, federation_gateway):
        """Test query service analysis."""
        # Test child service detection
        query = 'query { child(id: "123") { name age } }'
        services = federation_gateway._analyze_query_services(query)
        assert "child_service" in services

        # Test AI service detection
        query = 'query { child(id: "123") { aiProfile { personalityTraits } } }'
        services = federation_gateway._analyze_query_services(query)
        assert "ai_service" in services

    @pytest.mark.asyncio
    async def test_federated_query_execution(self, federation_gateway):
        """Test federated query execution."""
        # Mock service responses
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = (
            200
        )
        federation_gateway.http_client.post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"data": {"child": {"name": "Test Child", "age": 7}}}
        )

        query = 'query { child(id: "123") { name age } }'
        result = await federation_gateway._execute_federated_query(query, {})

        assert "data" in result
        assert result["data"] is not None
