"""Secrets Management Module.

Production-ready secrets management for AI Teddy Bear.
Provides secure storage, rotation, and access to sensitive configuration.
"""

from .config import SecretConfig, SecretProvider, SecretType
from .providers import EnvironmentProvider, LocalEncryptedProvider, VaultProvider
from .secrets_manager import SecretsManager, create_secrets_manager

__all__ = [
    "EnvironmentProvider",
    "LocalEncryptedProvider",
    "SecretConfig",
    "SecretProvider",
    "SecretType",
    "SecretsManager",
    "VaultProvider",
    "create_secrets_manager",
]
