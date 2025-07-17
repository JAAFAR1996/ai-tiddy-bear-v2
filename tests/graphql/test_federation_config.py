import pytest

try:
    from src.infrastructure.graphql.federation_gateway.federation_gateway import (
        FederationConfig,
        ServiceConfig,
        create_default_federation_config,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.mark.skipif(
    not FEDERATION_AVAILABLE, reason="Federation not available"
)
class TestFederationConfig:
    """Test federation configuration."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = create_default_federation_config()

        assert len(config.services) == 4
        assert config.enable_introspection is True
        assert config.enable_caching is True
        assert config.cors_origins == ["*"]

    def test_custom_config(self):
        """Test custom configuration."""
        services = [
            ServiceConfig("test_service", "http://test:8000", "/schema")
        ]

        config = FederationConfig(
            services=services,
            enable_authentication=False,
            rate_limit_requests=200,
        )

        assert len(config.services) == 1
        assert config.enable_authentication is False
        assert config.rate_limit_requests == 200
