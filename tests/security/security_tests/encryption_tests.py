"""Encryption Security Tests."""

import re
from typing import Any

from src.infrastructure.logging_config import get_logger

from .base_tester import BaseSecurityTester

logger = get_logger(__name__, component="security")


class EncryptionTester(BaseSecurityTester):
    """Tests for encryption security."""

    def test_encryption(self) -> dict[str, Any]:
        """Test encryption implementation."""
        issues = []
        encryption_patterns = [
            (r"md5\s*\(", "MD5 hash usage (weak)"),
            (r"sha1\s*\(", "SHA1 hash usage (weak)"),
            (r"DES\s*\(", "DES encryption (weak)"),
            (r"RC4\s*\(", "RC4 encryption (weak)"),
            (r'algorithm\s*=\s*"md5"', "MD5 algorithm specified"),
            (r'algorithm\s*=\s*"sha1"', "SHA1 algorithm specified"),
            (r"ssl_version\s*=\s*ssl\.PROTOCOL_TLSv1", "TLS 1.0 usage (weak)"),
            (r"ssl_version\s*=\s*ssl\.PROTOCOL_SSLv", "SSL usage (weak)"),
        ]
        strong_encryption_indicators = [
            "AES",
            "sha256",
            "sha512",
            "RSA",
            "ECDSA",
            "bcrypt",
            "scrypt",
            "pbkdf2",
            "TLSv1_2",
            "TLSv1_3",
        ]
        python_files = self.scan_python_files()
        has_strong_encryption = False
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            # Check for weak encryption
            for pattern, description in encryption_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "high",
                        },
                    )
            # Check for strong encryption
            for indicator in strong_encryption_indicators:
                if indicator in content:
                    has_strong_encryption = True
                    break

        if not has_strong_encryption:
            issues.append(
                {
                    "file": "N/A",
                    "issue": "No strong encryption indicators found",
                    "severity": "medium",
                },
            )

        recommendations = [
            "Use AES-256 for symmetric encryption",
            "Use SHA-256 or stronger for hashing",
            "Use bcrypt or scrypt for password hashing",
            "Configure TLS 1.2 or 1.3 for all connections",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )

    def test_secrets_exposure(self) -> dict[str, Any]:
        """Test for secrets exposure."""
        issues = []
        secret_patterns = [
            (r'api_key\s*=\s*".*"', "Hardcoded API key"),
            (r'secret_key\s*=\s*".*"', "Hardcoded secret key"),
            (r'password\s*=\s*".*"', "Hardcoded password"),
            (r'private_key\s*=\s*".*"', "Hardcoded private key"),
        ]
        python_files = self.scan_python_files()
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern, description in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "critical",
                        },
                    )

        recommendations = [
            "Store secrets in environment variables or a secret management system (e.g., HashiCorp Vault)",
            "Use a library like `pydantic-settings` to manage secrets",
            "Rotate secrets regularly",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )
