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


@pytest.mark.integration
@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestFederationIntegration:
    """Integration tests for federation system."""

    @pytest.mark.asyncio
    async def test_full_query_flow(self, federation_gateway):
        """Test complete query flow through federation."""
        # Mock all service responses
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = (
            200
        )
        federation_gateway.http_client.post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "data": {
                    "child": {
                        "id": "123",
                        "name": "Test Child",
                        "age": 7,
                        "aiProfile": {
                            "personalityTraits": [{"name": "Curious", "score": 0.85}]
                        },
                    }
                }
            }
        )

        # Execute federated query
        query = """
        query {
            child(id: "123") {
                id
                name
                age
                aiProfile {
                    personalityTraits {
                        name
                        score
                    }
                }
            }
        }
        """

        result = await federation_gateway._execute_federated_query(query, {})

        assert "data" in result
        assert result["data"]["child"]["name"] == "Test Child"
