import pytest

try:
    from src.infrastructure.graphql.federation_gateway.federation_gateway import (
        ServiceConfig,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestServiceConfig:
    """Test service configuration."""

    def test_service_config_creation(self):
        """Test service configuration creation."""
        config = ServiceConfig(
            name="test_service",
            url="http://localhost:8000",
            schema_path="/graphql",
            timeout=60,
            retry_attempts=5,
        )

        assert config.name == "test_service"
        assert config.url == "http://localhost:8000"
        assert config.timeout == 60
        assert config.retry_attempts == 5
