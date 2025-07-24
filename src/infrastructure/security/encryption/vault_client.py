import asyncio
from functools import lru_cache
from typing import Any, Optional

from pydantic import SecretStr

from src.infrastructure.config.settings import get_settings

try:
    import hvac  # type: ignore

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False
    hvac = None

"""HashiCorp Vault client for enterprise-grade secret management.
Implements 2025 security standards for the AI Teddy Bear system.
NOTE: This integration is optional and requires the 'hvac' package.
To enable Vault integration:
  1. Install hvac: pip install hvac
  2. Set VAULT_URL and VAULT_TOKEN environment variables
  3. Configure Vault with appropriate policies and secrets
If Vault is not configured, the system will use environment variables instead.
"""


class VaultClient:
    """Enterprise-grade secrets management using HashiCorp Vault."""

    def __init__(self, vault_url: str, vault_token: SecretStr) -> None:
        self.vault_url = vault_url
        self.vault_token = vault_token
        self.client = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Vault client connection."""
        if self._initialized:
            return
        try:
            # Run in thread pool to avoid blocking
            self.client = await asyncio.get_event_loop().run_in_executor(
                None,
                self._init_client,
            )
            self._initialized = True
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Vault client: {e}")

    def _init_client(self) -> Any:
        if not VAULT_AVAILABLE:
            raise ImportError(
                "hvac package not installed. Install with: pip install hvac",
            )
        """Initialize the HVAC client (synchronous operation)."""
        client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token.get_secret_value(),
        )
        if not client.is_authenticated():
            raise ConnectionError("Vault authentication failed")
        return client

    async def get_secret(
        self,
        secret_path: str,
        mount_point: str = "secret",
    ) -> dict[str, Any]:
        """Retrieve a secret from Vault.

        Args:
            secret_path: Path to the secret in Vault
            mount_point: Vault mount point (default: "secret")

        Returns:
            Dictionary containing the secret data

        """
        if not self._initialized:
            await self.initialize()
        if not self.client:
            raise ValueError("Vault client not initialized.")
        try:
            # Run in thread pool to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.secrets.kv.v2.read_secret_version,
                secret_path,
                mount_point,
            )
            return response["data"]["data"]
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret '{secret_path}': {e}")

    async def put_secret(
        self,
        secret_path: str,
        secret_data: dict[str, Any],
        mount_point: str = "secret",
    ) -> None:
        """Store a secret in Vault.

        Args:
            secret_path: Path to store the secret
            secret_data: Dictionary containing the secret data
            mount_point: Vault mount point (default: "secret")

        """
        if not self._initialized:
            await self.initialize()
        if not self.client:
            raise ValueError("Vault client not initialized.")
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.secrets.kv.v2.create_or_update_secret,
                secret_path,
                secret_data,
                mount_point,
            )
        except Exception as e:
            raise ValueError(f"Failed to store secret '{secret_path}': {e}")


@lru_cache
async def get_vault_client() -> Optional[VaultClient]:
    """Get a configured Vault client instance."""
    if not VAULT_AVAILABLE:
        return None
    settings = get_settings()
    if not settings.security.VAULT_URL or not settings.security.VAULT_TOKEN:
        return None
    client = VaultClient(
        str(settings.security.VAULT_URL),
        settings.security.VAULT_TOKEN,
    )
    await client.initialize()
    return client
