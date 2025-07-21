import os
import re
import secrets
import sys
from pathlib import Path

from src.domain.constants import COPPA_MAX_RETENTION_DAYS
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class EnvironmentSecurityValidator:
    """Validates environment configuration for security compliance"""

    # Minimum entropy bits for secrets
    MIN_SECRET_ENTROPY = 256

    # Required environment variables with validation rules
    REQUIRED_SECRETS = {
        "DATABASE_URL": {
            "min_length": 20,
            "pattern": r"^postgresql://",
            "no_defaults": ["CHANGE_ME", "password", "admin", "root", "test"],
            "description": "PostgreSQL connection string",
        },
        "JWT_SECRET": {
            "min_length": 64,
            "pattern": None,
            "no_defaults": ["REQUIRED", "CHANGE", "SECRET", "your_secret"],
            "description": "JWT signing secret",
        },
        "ENCRYPTION_KEY": {
            "min_length": 64,
            "pattern": None,
            "no_defaults": ["REQUIRED", "CHANGE", "SECRET"],
            "description": "Data encryption key",
        },
        "SESSION_SECRET": {
            "min_length": 64,
            "pattern": None,
            "no_defaults": ["REQUIRED", "CHANGE", "SECRET"],
            "description": "Session encryption secret",
        },
        "OPENAI_API_KEY": {
            "min_length": 40,
            "pattern": r"^sk-",
            "no_defaults": ["REQUIRED", "your_api_key"],
            "description": "OpenAI API key",
        },
    }

    # Optional but recommended secrets
    RECOMMENDED_SECRETS = {
        "VAULT_TOKEN": {
            "min_length": 20,
            "description": "HashiCorp Vault token",
        },
        "SENTRY_DSN": {
            "min_length": 20,
            "description": "Sentry error tracking",
        },
        "PARENT_VERIFICATION_API_KEY": {
            "min_length": 32,
            "description": "Parent verification service",
        },
    }

    @classmethod
    def validate_all(cls) -> tuple[bool, list[str]]:
        """Validate all environment variables
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        warnings = []

        if os.getenv("ENVIRONMENT") == "production" and Path(".env").exists():
            errors.append("CRITICAL: .env file found in production environment!")

        # Validate required secrets
        for var_name, rules in cls.REQUIRED_SECRETS.items():
            value = os.getenv(var_name)
            if not value:
                errors.append(
                    f"Missing required secret: {var_name} ({rules['description']})"
                )
                continue

            # Check minimum length
            if len(value) < rules["min_length"]:
                errors.append(
                    f"{var_name} too short: {len(value)} chars "
                    f"(minimum: {rules['min_length']})"
                )

            # Check pattern if specified
            if rules.get("pattern") and not re.match(rules["pattern"], value):
                errors.append(
                    f"{var_name} invalid format: must match {rules['pattern']}"
                )

            # Check for default/weak values
            for default in rules.get("no_defaults", []):
                if default.lower() in value.lower():
                    errors.append(
                        f"{var_name} contains default/weak value: '{default}'"
                    )

            if var_name in ["JWT_SECRET", "ENCRYPTION_KEY", "SESSION_SECRET"]:
                entropy = cls._calculate_entropy(value)
                if entropy < cls.MIN_SECRET_ENTROPY:
                    errors.append(
                        f"{var_name} has insufficient entropy: {entropy:.1f} bits "
                        f"(minimum: {cls.MIN_SECRET_ENTROPY})"
                    )

        # Check recommended secrets
        for var_name, rules in cls.RECOMMENDED_SECRETS.items():
            value = os.getenv(var_name)
            if not value and os.getenv("ENVIRONMENT") == "production":
                warnings.append(
                    f"Recommended secret missing: {var_name} ({rules['description']})"
                )

        if os.getenv("COPPA_ENABLED", "true").lower() != "true":
            errors.append("COPPA_ENABLED must be 'true' for child safety")

        if os.getenv("PARENTAL_CONSENT_REQUIRED", "true").lower() != "true":
            errors.append("PARENTAL_CONSENT_REQUIRED must be 'true'")

        retention_days = os.getenv("DATA_RETENTION_DAYS", str(COPPA_MAX_RETENTION_DAYS))
        try:
            if int(retention_days) > COPPA_MAX_RETENTION_DAYS:
                errors.append(
                    f"DATA_RETENTION_DAYS ({retention_days}) exceeds COPPA limit of {COPPA_MAX_RETENTION_DAYS}"
                )
        except ValueError:
            errors.append("DATA_RETENTION_DAYS must be a valid integer")

        # Print warnings
        for warning in warnings:
            logger.warning(f"Security Warning: {warning}")

        return len(errors) == 0, errors

    @staticmethod
    def _calculate_entropy(value: str) -> float:
        """Calculate Shannon entropy of a string in bits"""
        if not value:
            return 0.0

        # Count character frequencies
        freq = {}
        for char in value:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        total = len(value)
        for count in freq.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * (probability).bit_length()

        return entropy * len(value)

    @classmethod
    def generate_secure_secret(cls, length: int = 64) -> str:
        """Generate a cryptographically secure secret"""
        return secrets.token_urlsafe(length)

    @classmethod
    def validate_and_exit_on_error(cls) -> None:
        """Validate environment and exit if errors found"""
        is_valid, errors = cls.validate_all()
        if not is_valid:
            logger.error("=" * 60)
            logger.error("SECURITY VALIDATION FAILED")
            logger.error("=" * 60)
            for error in errors:
                logger.error(f"❌ {error}")
            logger.error("=" * 60)
            logger.error("Fix these security issues before starting the application")
            logger.error("Generate secure secrets with:")
            logger.error(
                '  python -c "from src.infrastructure.validators.security.environment_validator '
                "import EnvironmentSecurityValidator; "
                'EnvironmentSecurityValidator.generate_secure_secret()"'
            )
            sys.exit(1)
        logger.info("✅ Environment security validation passed")

    @classmethod
    def get_secure_config(cls) -> dict[str, str]:
        """Get validated configuration with defaults for development only"""
        config = {}

        # Only provide defaults in development
        is_development = os.getenv("ENVIRONMENT", "development") == "development"
        if is_development:
            for var_name in cls.REQUIRED_SECRETS:
                value = os.getenv(var_name)
                if not value or any(
                    d in value
                    for d in cls.REQUIRED_SECRETS[var_name].get("no_defaults", [])
                ):
                    if var_name == "DATABASE_URL":
                        config[var_name] = (
                            "postgresql://dev:dev@localhost:5432/ai_teddy_dev"
                        )
                    elif var_name == "OPENAI_API_KEY":
                        config[var_name] = (
                            logger.error("No real development key available - environment key not configured.")
                            raise NotImplementedError("No real development key available - environment key not configured.")
                        )
                    else:
                        config[var_name] = cls.generate_secure_secret()
                    logger.warning(f"Generated development secret for {var_name}")
                else:
                    config[var_name] = value
        else:
            # Production: no defaults allowed
            for var_name in cls.REQUIRED_SECRETS:
                config[var_name] = os.getenv(var_name)

        return config


if os.getenv("ENVIRONMENT") == "production":
    EnvironmentSecurityValidator.validate_and_exit_on_error()
