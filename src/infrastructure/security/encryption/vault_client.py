import asyncio
import base64
import os
import time
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import SecretStr
from retrying import retry

from src.infrastructure.logging_config import get_logger

try:
    import hvac  # type: ignore

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False
    hvac = None

logger = get_logger(__name__, component="security")

"""Production-grade HashiCorp Vault client for enterprise secret management.
Implements 2025 security standards for the AI Teddy Bear system.

CRITICAL REQUIREMENTS:
- Production systems MUST use HashiCorp Vault for all secrets
- NO fallback to environment variables in production
- System MUST fail fast if Vault is unavailable
- All operations MUST be audited (without exposing secret values)
- Key rotation support is MANDATORY
- Health checks are REQUIRED for monitoring

Environment Variables Required:
- VAULT_URL: https://vault.company.com:8200
- VAULT_TOKEN: Authentication token for Vault
- VAULT_NAMESPACE: (Optional) Vault Enterprise namespace
"""


class VaultConnectionError(Exception):
    """Raised when Vault connection fails."""


class VaultAuthenticationError(Exception):
    """Raised when Vault authentication fails."""


class VaultSecretNotFoundError(Exception):
    """Raised when a secret is not found in Vault."""


class VaultClient:
    """Production-grade secrets management using HashiCorp Vault.

    Features:
    - Reliable connection with retry logic
    - Secure secret storage and retrieval
    - Key rotation support
    - Comprehensive audit logging (NO secret values logged)
    - Health monitoring
    - Fail-fast behavior in production
    """

    def __init__(
        self,
        vault_url: str,
        vault_token: Union[str, SecretStr],
        vault_namespace: Optional[str] = None,
        mount_point: str = "secret",
    ) -> None:
        if not vault_url:
            raise ValueError("VAULT_URL is required and cannot be empty")

        # Handle both string and SecretStr tokens
        if isinstance(vault_token, str):
            if not vault_token:
                raise ValueError("VAULT_TOKEN is required and cannot be empty")
            self.vault_token = SecretStr(vault_token)
        elif isinstance(vault_token, SecretStr):
            if not vault_token.get_secret_value():
                raise ValueError("VAULT_TOKEN is required and cannot be empty")
            self.vault_token = vault_token
        else:
            raise ValueError("VAULT_TOKEN must be either str or SecretStr")

        self.vault_url = vault_url
        self.vault_namespace = vault_namespace
        self.mount_point = mount_point
        self.client = None
        self._initialized = False
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes

        logger.info(
            f"VaultClient configured: URL={vault_url}, Namespace={vault_namespace}, Mount={mount_point}"
        )

    @retry(
        stop_max_attempt_number=3,
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        retry_on_exception=lambda ex: isinstance(
            ex, (ConnectionError, VaultConnectionError)
        ),
    )
    async def initialize(self) -> None:
        """Initialize the Vault client connection with retry logic."""
        if self._initialized:
            return

        try:
            logger.info("Initializing Vault client connection...")

            # Run in thread pool to avoid blocking
            self.client = await asyncio.get_event_loop().run_in_executor(
                None,
                self._init_client,
            )

            # Test connection and authentication
            await self._verify_connection()

            self._initialized = True
            logger.info("Vault client successfully initialized and authenticated")

        except Exception as e:
            logger.critical(f"Failed to initialize Vault client: {e}")
            self._initialized = False
            raise VaultConnectionError(f"Vault initialization failed: {e}") from e

    def _init_client(self) -> Any:
        """Initialize the HVAC client (synchronous operation)."""
        if not VAULT_AVAILABLE:
            raise ImportError(
                "hvac package not installed. Install with: pip install hvac"
            )

        try:
            client = hvac.Client(
                url=self.vault_url,
                token=self.vault_token.get_secret_value(),
                namespace=self.vault_namespace,
                verify=True,  # Always verify SSL in production
                timeout=30,  # 30 second timeout
            )

            # Verify authentication
            if not client.is_authenticated():
                raise VaultAuthenticationError("Vault authentication failed")

            logger.debug("HVAC client created and authenticated successfully")
            return client

        except Exception as e:
            logger.error(f"Failed to create HVAC client: {e}")
            raise

    async def _verify_connection(self) -> None:
        """Verify Vault connection and basic functionality."""
        try:
            # Test basic connectivity
            health_status = await asyncio.get_event_loop().run_in_executor(
                None, self.client.sys.read_health_status
            )

            if not health_status.get("initialized", False):
                raise VaultConnectionError("Vault is not initialized")

            if health_status.get("sealed", True):
                raise VaultConnectionError("Vault is sealed")

            logger.debug("Vault health check passed")

        except Exception as e:
            logger.error(f"Vault connection verification failed: {e}")
            raise VaultConnectionError(f"Vault connectivity test failed: {e}") from e

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of Vault connection.

        Returns:
            Dictionary containing health status information
        """
        current_time = time.time()

        # Skip frequent health checks
        if current_time - self._last_health_check < self._health_check_interval:
            return {
                "status": "healthy",
                "cached": True,
                "last_check": self._last_health_check,
            }

        try:
            if not self._initialized:
                await self.initialize()

            # Get Vault health status
            health_status = await asyncio.get_event_loop().run_in_executor(
                None, self.client.sys.read_health_status
            )

            # Check authentication
            is_authenticated = await asyncio.get_event_loop().run_in_executor(
                None, self.client.is_authenticated
            )

            self._last_health_check = current_time

            result = {
                "status": "healthy"
                if is_authenticated and not health_status.get("sealed", True)
                else "unhealthy",
                "vault_initialized": health_status.get("initialized", False),
                "vault_sealed": health_status.get("sealed", True),
                "authenticated": is_authenticated,
                "cluster_name": health_status.get("cluster_name"),
                "version": health_status.get("version"),
                "last_check": current_time,
                "url": self.vault_url,
                "namespace": self.vault_namespace,
            }

            if result["status"] == "healthy":
                logger.debug("Vault health check: HEALTHY")
            else:
                logger.warning(f"Vault health check: UNHEALTHY - {result}")

            return result

        except Exception as e:
            logger.error(f"Vault health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": current_time,
                "url": self.vault_url,
            }

    async def get_secret(
        self,
        secret_path: str,
        version: Optional[int] = None,
        mount_point: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve a secret from Vault.

        Args:
            secret_path: Path to the secret in Vault
            version: Specific version of the secret (None for latest)
            mount_point: Vault mount point (defaults to self.mount_point)

        Returns:
            Dictionary containing the secret data

        Raises:
            VaultSecretNotFoundError: If secret is not found
            VaultConnectionError: If Vault is not accessible
        """
        if not self._initialized:
            await self.initialize()

        if not self.client:
            raise VaultConnectionError("Vault client not initialized")

        mount_point = mount_point or self.mount_point

        try:
            logger.debug(f"Retrieving secret: {secret_path} from mount: {mount_point}")

            # Run in thread pool to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._get_secret_sync, secret_path, mount_point, version
            )

            if not response or "data" not in response:
                raise VaultSecretNotFoundError(f"Secret not found: {secret_path}")

            secret_data = response["data"]["data"]

            # Audit log (NO secret values)
            logger.info(
                f"Secret retrieved successfully: path={secret_path}, "
                f"mount={mount_point}, keys={list(secret_data.keys()) if secret_data else []}"
            )

            return secret_data

        except VaultSecretNotFoundError:
            logger.warning(f"Secret not found: {secret_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_path}': {e}")
            raise VaultConnectionError(
                f"Failed to retrieve secret '{secret_path}': {e}"
            ) from e

    def _get_secret_sync(
        self, secret_path: str, mount_point: str, version: Optional[int]
    ) -> Dict[str, Any]:
        """Synchronous secret retrieval for use in thread pool."""
        if version:
            return self.client.secrets.kv.v2.read_secret_version(
                path=secret_path, version=version, mount_point=mount_point
            )
        else:
            return self.client.secrets.kv.v2.read_secret_version(
                path=secret_path, mount_point=mount_point
            )

    async def put_secret(
        self,
        secret_path: str,
        secret_data: Dict[str, Any],
        mount_point: Optional[str] = None,
        cas: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Store a secret in Vault.

        Args:
            secret_path: Path to store the secret
            secret_data: Dictionary containing the secret data
            mount_point: Vault mount point (defaults to self.mount_point)
            cas: Check-and-Set parameter for version control

        Returns:
            Dictionary containing the response metadata
        """
        if not self._initialized:
            await self.initialize()

        if not self.client:
            raise VaultConnectionError("Vault client not initialized")

        mount_point = mount_point or self.mount_point

        try:
            logger.debug(f"Storing secret: {secret_path} in mount: {mount_point}")

            # Validate secret data
            if not secret_data or not isinstance(secret_data, dict):
                raise ValueError("Secret data must be a non-empty dictionary")

            # Run in thread pool to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._put_secret_sync, secret_path, secret_data, mount_point, cas
            )

            # Audit log (NO secret values)
            logger.info(
                f"Secret stored successfully: path={secret_path}, "
                f"mount={mount_point}, keys={list(secret_data.keys())}, "
                f"version={response['data']['version'] if response and 'data' in response else 'unknown'}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to store secret '{secret_path}': {e}")
            raise VaultConnectionError(
                f"Failed to store secret '{secret_path}': {e}"
            ) from e

    def _put_secret_sync(
        self,
        secret_path: str,
        secret_data: Dict[str, Any],
        mount_point: str,
        cas: Optional[int],
    ) -> Dict[str, Any]:
        """Synchronous secret storage for use in thread pool."""
        return self.client.secrets.kv.v2.create_or_update_secret(
            path=secret_path, secret=secret_data, mount_point=mount_point, cas=cas
        )

    async def delete_secret(
        self,
        secret_path: str,
        versions: Optional[List[int]] = None,
        mount_point: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete a secret from Vault.

        Args:
            secret_path: Path to the secret
            versions: Specific versions to delete (None deletes latest)
            mount_point: Vault mount point (defaults to self.mount_point)

        Returns:
            Dictionary containing the response metadata
        """
        if not self._initialized:
            await self.initialize()

        if not self.client:
            raise VaultConnectionError("Vault client not initialized")

        mount_point = mount_point or self.mount_point

        try:
            logger.debug(f"Deleting secret: {secret_path} from mount: {mount_point}")

            # Run in thread pool to avoid blocking
            if versions:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.client.secrets.kv.v2.delete_secret_versions,
                    secret_path,
                    versions,
                    mount_point,
                )
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.client.secrets.kv.v2.delete_latest_version_of_secret,
                    secret_path,
                    mount_point,
                )

            # Audit log
            logger.info(
                f"Secret deleted successfully: path={secret_path}, "
                f"mount={mount_point}, versions={versions or 'latest'}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_path}': {e}")
            raise VaultConnectionError(
                f"Failed to delete secret '{secret_path}': {e}"
            ) from e

    async def list_secrets(
        self,
        path: str = "",
        mount_point: Optional[str] = None,
    ) -> List[str]:
        """List secrets at a given path.

        Args:
            path: Path to list secrets from
            mount_point: Vault mount point (defaults to self.mount_point)

        Returns:
            List of secret names
        """
        if not self._initialized:
            await self.initialize()

        if not self.client:
            raise VaultConnectionError("Vault client not initialized")

        mount_point = mount_point or self.mount_point

        try:
            logger.debug(f"Listing secrets: {path} from mount: {mount_point}")

            # Run in thread pool to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.client.secrets.kv.v2.list_secrets, path, mount_point
            )

            secrets = response.get("data", {}).get("keys", [])

            logger.debug(f"Listed {len(secrets)} secrets at path: {path}")

            return secrets

        except Exception as e:
            logger.error(f"Failed to list secrets at '{path}': {e}")
            raise VaultConnectionError(
                f"Failed to list secrets at '{path}': {e}"
            ) from e

    async def rotate_secret(
        self,
        secret_path: str,
        new_secret_data: Dict[str, Any],
        mount_point: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rotate a secret by creating a new version.

        Args:
            secret_path: Path to the secret
            new_secret_data: New secret data
            mount_point: Vault mount point (defaults to self.mount_point)

        Returns:
            Dictionary containing the response metadata
        """
        try:
            # Get current version for CAS
            current_secret = await self.get_secret(secret_path, mount_point=mount_point)

            # Store new version
            response = await self.put_secret(
                secret_path, new_secret_data, mount_point=mount_point
            )

            logger.info(
                f"Secret rotated successfully: path={secret_path}, "
                f"new_version={response['data']['version'] if response and 'data' in response else 'unknown'}"
            )

            return response

        except Exception as e:
            logger.error(f"Failed to rotate secret '{secret_path}': {e}")
            raise VaultConnectionError(
                f"Failed to rotate secret '{secret_path}': {e}"
            ) from e

    async def get_encryption_key(
        self,
        key_name: str,
        purpose: str = "default",
        key_length: int = 32,
    ) -> bytes:
        """Get or generate an encryption key from Vault.

        Args:
            key_name: Name of the encryption key
            purpose: Purpose of the key (for audit trail)
            key_length: Length of the key in bytes

        Returns:
            Raw encryption key bytes

        Raises:
            VaultSecretNotFoundError: If key is not found and auto-generation is disabled
        """
        full_key_path = f"encryption_keys/{key_name}"

        try:
            # Try to get existing key
            secret_data = await self.get_secret(full_key_path)
            key_b64 = secret_data.get("key")

            if not key_b64:
                raise VaultSecretNotFoundError(
                    f"Encryption key data missing for: {key_name}"
                )

            key_bytes = base64.b64decode(key_b64)

            logger.info(f"Encryption key retrieved: name={key_name}, purpose={purpose}")
            return key_bytes

        except VaultSecretNotFoundError:
            logger.critical(
                f"Encryption key '{key_name}' not found in Vault. "
                f"Keys must be manually provisioned by security team."
            )
            raise

    async def store_encryption_key(
        self,
        key_name: str,
        key_data: bytes,
        purpose: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store an encryption key in Vault.

        Args:
            key_name: Name of the encryption key
            key_data: Raw key bytes
            purpose: Purpose of the key
            metadata: Additional metadata

        Returns:
            Dictionary containing the response metadata
        """
        full_key_path = f"encryption_keys/{key_name}"

        secret_data = {
            "key": base64.b64encode(key_data).decode("utf-8"),
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "key_length": len(key_data),
            **(metadata or {}),
        }

        response = await self.put_secret(full_key_path, secret_data)

        logger.info(
            f"Encryption key stored: name={key_name}, purpose={purpose}, length={len(key_data)}"
        )
        return response

    async def validate_required_secrets(
        self, required_secrets: List[str]
    ) -> Dict[str, bool]:
        """Validate that all required secrets exist in Vault.

        Args:
            required_secrets: List of secret paths that must exist

        Returns:
            Dictionary mapping secret names to their existence status
        """
        results = {}
        missing_secrets = []

        for secret_path in required_secrets:
            try:
                await self.get_secret(secret_path)
                results[secret_path] = True
            except VaultSecretNotFoundError:
                results[secret_path] = False
                missing_secrets.append(secret_path)
            except Exception as e:
                logger.error(f"Error checking secret '{secret_path}': {e}")
                results[secret_path] = False
                missing_secrets.append(secret_path)

        if missing_secrets:
            logger.critical(f"Missing required secrets in Vault: {missing_secrets}")
        else:
            logger.info(f"All {len(required_secrets)} required secrets found in Vault")

        return results


@lru_cache
def get_vault_client() -> VaultClient:
    """Get a configured Vault client instance.

    Environment Variables Required:
    - VAULT_URL: HashiCorp Vault server URL
    - VAULT_TOKEN: Authentication token
    - VAULT_NAMESPACE: (Optional) Vault Enterprise namespace

    Raises:
        ValueError: If required environment variables are missing
        ImportError: If hvac package is not installed
    """
    if not VAULT_AVAILABLE:
        raise ImportError(
            "HashiCorp Vault integration requires 'hvac' package. "
            "Install with: pip install hvac"
        )

    vault_url = os.getenv("VAULT_URL")
    vault_token = os.getenv("VAULT_TOKEN")
    vault_namespace = os.getenv("VAULT_NAMESPACE")

    if not vault_url:
        raise ValueError(
            "VAULT_URL environment variable is required for production. "
            "Example: https://vault.company.com:8200"
        )

    if not vault_token:
        raise ValueError(
            "VAULT_TOKEN environment variable is required for production. "
            "This should be a valid Vault authentication token."
        )

    logger.info(f"Creating Vault client for URL: {vault_url}")

    return VaultClient(
        vault_url=vault_url,
        vault_token=SecretStr(vault_token),
        vault_namespace=vault_namespace,
    )


async def get_vault_client_async() -> VaultClient:
    """Get and initialize a Vault client asynchronously."""
    client = get_vault_client()
    await client.initialize()
    return client
