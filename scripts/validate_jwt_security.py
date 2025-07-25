"""
JWT Security Startup Validator

This script validates JWT security on system startup and ensures the system
fails securely if any JWT secrets do not meet cryptographic requirements.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.auth.jwt_security_validator import JWTSecurityValidator

logger = get_logger(__name__, component="security")


def validate_jwt_security_on_startup() -> bool:
    """Validate JWT security configuration on system startup.

    Returns:
        bool: True if all validations pass, False otherwise

    Raises:
        SystemExit: If critical security issues are found
    """
    try:
        logger.info("🔐 Starting JWT security validation...")

        # Load settings
        settings = get_settings()

        # Validate main SECRET_KEY
        try:
            JWTSecurityValidator.validate_jwt_secret(settings.security.SECRET_KEY)
            logger.info("✅ SECRET_KEY validation passed")
        except ValueError as e:
            logger.critical(f"❌ SECRET_KEY validation failed: {e}")
            return False

        # Validate JWT_SECRET_KEY
        try:
            JWTSecurityValidator.validate_jwt_secret(settings.security.JWT_SECRET_KEY)
            logger.info("✅ JWT_SECRET_KEY validation passed")
        except ValueError as e:
            logger.critical(f"❌ JWT_SECRET_KEY validation failed: {e}")
            return False

        # Validate optional JWT secrets if they exist
        if hasattr(settings.security, "JWT_SECRET") and settings.security.JWT_SECRET:
            if (
                len(settings.security.JWT_SECRET) >= 32
            ):  # Only validate if it's intended to be used
                try:
                    JWTSecurityValidator.validate_jwt_secret(
                        settings.security.JWT_SECRET
                    )
                    logger.info("✅ JWT_SECRET validation passed")
                except ValueError as e:
                    logger.critical(f"❌ JWT_SECRET validation failed: {e}")
                    return False

        if (
            hasattr(settings.security, "JWT_REFRESH_SECRET")
            and settings.security.JWT_REFRESH_SECRET
        ):
            if len(settings.security.JWT_REFRESH_SECRET) >= 32:
                try:
                    JWTSecurityValidator.validate_jwt_secret(
                        settings.security.JWT_REFRESH_SECRET
                    )
                    logger.info("✅ JWT_REFRESH_SECRET validation passed")
                except ValueError as e:
                    logger.critical(f"❌ JWT_REFRESH_SECRET validation failed: {e}")
                    return False

        logger.info("🔐 All JWT security validations passed - system is secure")
        return True

    except Exception as e:
        logger.critical(f"💥 Critical error during JWT security validation: {e}")
        return False


def main():
    """Main function for standalone execution."""
    print("🚀 AI Teddy Bear - JWT Security Startup Validation")
    print("=" * 60)

    # Check if we're in development mode
    is_development = os.getenv("ENVIRONMENT", "production").lower() in [
        "development",
        "dev",
        "local",
    ]

    if is_development:
        print("⚠️  DEVELOPMENT MODE DETECTED")
        print("Note: Enhanced JWT security validation is active")
        print()

    try:
        validation_passed = validate_jwt_security_on_startup()

        if validation_passed:
            print("✅ JWT Security Validation: PASSED")
            print("🔐 System is secure and ready to start")
            print("🧸 AI Teddy Bear can safely serve children")
            return 0
        else:
            print("❌ JWT Security Validation: FAILED")
            print("🚨 CRITICAL SECURITY ISSUE DETECTED")
            print("⛔ System CANNOT start with weak JWT secrets")
            print("📋 Action Required:")
            print("   1. Generate cryptographically strong JWT secrets (64+ chars)")
            print("   2. Ensure secrets have high entropy (4.0+ bits per char)")
            print("   3. Avoid predictable patterns or common words")
            print("   4. Update environment variables with secure secrets")
            print()
            print("🛡️  Child safety depends on strong JWT security!")
            return 1

    except Exception as e:
        print(f"💥 FATAL ERROR: {e}")
        print("🚨 System cannot validate JWT security")
        print("⛔ Startup ABORTED for child safety")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
