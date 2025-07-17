"""Core security manager for handling passwords, tokens, and other security-critical operations."""

import hashlib
import hmac
import secrets

import bcrypt


class SecurityManager:
    """Provides centralized security functions for the application."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password using bcrypt, the industry standard for password storage.

        Args:
            password: The plaintext password.

        Returns:
            The hashed password as a string.

        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plaintext password against a stored bcrypt hash.

        Args:
            plain_password: The plaintext password to verify.
            hashed_password: The stored hashed password.

        Returns:
            True if the password is correct, False otherwise.

        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generates a cryptographically secure, URL-safe token.

        Args:
            length: The desired length of the token in bytes.

        Returns:
            A hex-encoded secure token.

        """
        return secrets.token_hex(length)

    @staticmethod
    def secure_compare(a: str | bytes, b: str | bytes) -> bool:
        """Performs a constant-time comparison to mitigate timing attacks.

        Args:
            a: The first string or bytes object.
            b: The second string or bytes object.

        Returns:
            True if the inputs are equal, False otherwise.

        """
        return hmac.compare_digest(a, b)

    @staticmethod
    def generate_file_signature(file_content: bytes, secret_key: str) -> str:
        """Generates a HMAC-SHA256 signature for file content to ensure integrity.

        Args:
            file_content: The content of the file in bytes.
            secret_key: A secret key to use for generating the signature.

        Returns:
            The hex-encoded HMAC signature.

        """
        return hmac.new(
            secret_key.encode("utf-8"),
            file_content,
            hashlib.sha256,
        ).hexdigest()


# Example of a global instance, though dependency injection is preferred
security_manager = SecurityManager()
