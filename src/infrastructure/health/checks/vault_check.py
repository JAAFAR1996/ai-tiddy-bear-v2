"""HashiCorp Vault Health Check
Production-grade Vault connectivity and performance monitoring
"""

import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class VaultHealthCheck:
    """Production Vault health monitoring with comprehensive diagnostics."""

    def __init__(self, vault_client=None):
        """Initialize Vault health checker.

        Args:
            vault_client: VaultClient instance for health checks
        """
        self.vault_client = vault_client
        self.check_name = "vault"

    async def check_health(self) -> Dict[str, Any]:
        """Comprehensive Vault health check with performance metrics.

        Returns:
            Health check result with status, timing, and diagnostics
        """
        start_time = time.time()

        if not self.vault_client:
            return {
                "status": "disabled",
                "response_time_ms": 0,
                "details": {"note": "Vault client not configured"},
                "error": None,
            }

        try:
            # Test Vault connectivity and performance
            health_result = await self.vault_client.health_check()
            response_time = (time.time() - start_time) * 1000

            # Determine overall status
            if health_result.get("is_healthy", False):
                status = "healthy"
                error = None
            else:
                status = "unhealthy"
                error = health_result.get("error", "Unknown Vault error")

            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "details": {
                    "vault_url": health_result.get("vault_url", "unknown"),
                    "is_authenticated": health_result.get("is_authenticated", False),
                    "is_sealed": health_result.get("is_sealed", True),
                    "version": health_result.get("version", "unknown"),
                    "cluster_id": health_result.get("cluster_id", "unknown"),
                    "performance_standby": health_result.get(
                        "performance_standby", False
                    ),
                },
                "error": error,
            }

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Vault health check failed: {e}")

            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "details": {"note": "Vault connection failed"},
                "error": str(e),
            }


async def check_vault_health(vault_client=None) -> Dict[str, Any]:
    """Standalone Vault health check function.

    Args:
        vault_client: Optional VaultClient instance

    Returns:
        Vault health check result
    """
    checker = VaultHealthCheck(vault_client)
    return await checker.check_health()
