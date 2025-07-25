"""Configuration for secrets management."""

from dataclasses import dataclass
from enum import Enum


class SecretProvider(str, Enum):
    """Available secret providers."""

    ENVIRONMENT = "environment"
    LOCAL_ENCRYPTED = "local_encrypted"
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"


class SecretType(str, Enum):
    """Types of secrets."""

    API_KEY = "api_key"
    DATABASE_URL = "database_url"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = "jwt_secret"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"


@dataclass
class SecretConfig:
    """Configuration for secrets management."""

    default_provider: SecretProvider = SecretProvider.ENVIRONMENT
    auto_rotation_enabled: bool = False
    rotation_check_interval_hours: int = 24
    cache_ttl_seconds: int = 300  # 5 minutes
    audit_enabled: bool = True
    secure_delete_enabled: bool = True
    encryption_algorithm: str = "AES256"

    # Provider-specific configurations
    vault_url: str | None = None
    vault_token: str | None = None
    vault_mount_point: str = "secret"

    aws_region: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    azure_vault_url: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: str | None = None
    azure_tenant_id: str | None = None

    gcp_project_id: str | None = None
    gcp_credentials_path: str | None = None

    # Local storage configuration
    local_secrets_dir: str = "/var/secrets"
    local_encryption_key_path: str = "/var/keys/secret_encryption_key"

    # Security settings
    require_encrypted_storage: bool = True
    allow_fallback_to_env: bool = False  # For production, should be False
    max_secret_age_days: int = 90

    # Audit settings
    audit_log_path: str = "/var/log/secrets_audit.log"
    audit_log_max_size_mb: int = 100
    audit_log_retention_days: int = 365
