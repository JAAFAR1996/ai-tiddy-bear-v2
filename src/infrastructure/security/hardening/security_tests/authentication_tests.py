"""Authentication Security Tests"""
from typing import Dict, List, Any
import logging
import re
from .base_tester import BaseSecurityTester
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class AuthenticationTester(BaseSecurityTester):
    """Tests for authentication security"""

    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication security"""
        issues = []
        auth_patterns = [
            (r'password\s*=\s*".*"', "Hardcoded password"),
            (r'secret\s*=\s*".*"', "Hardcoded secret"),
            (r'jwt\.encode\s*\(.*algorithm\s*=\s*"none"', "JWT with no algorithm"),
            (r'verify\s*=\s*False', "Disabled SSL verification"),
            (r'check_password\s*=\s*False', "Disabled password check"),
            (r'session_cookie_secure\s*=\s*False', "Insecure session cookie")
        ]
        python_files = self.scan_python_files()
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern, description in auth_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append({
                        "file": str(file_path),
                        "issue": description,
                        "severity": "high"
                    })
        recommendations = [
            "Store secrets in environment variables",
            "Use strong JWT algorithms (RS256, ES256)",
            "Implement proper session management",
            "Use secure cookie settings in production",
            "Implement multi-factor authentication"
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations
        )

    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation"""
        issues = []
        # This is a simplified check. Real validation requires more context.
        validation_keywords = ["validate", "sanitize", "escape", "pydantic"]
        python_files = self.scan_python_files()
        files_with_validation = 0
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            if any(keyword in content.lower() for keyword in validation_keywords):
                files_with_validation += 1

        if files_with_validation / len(python_files) < 0.25:  # Arbitrary threshold
            issues.append("Low usage of input validation keywords")

        recommendations = [
            "Use Pydantic for robust input validation",
            "Sanitize all user-provided input",
            "Implement validation at API boundaries"
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=issues,
            recommendations=recommendations
        )

    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test for rate limiting implementation"""
        issues = []
        rate_limit_keywords = ["ratelimit", "throttle", "RateLimiter"]
        python_files = self.scan_python_files()
        has_rate_limiting = False
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            if any(keyword in content for keyword in rate_limit_keywords):
                has_rate_limiting = True
                break

        if not has_rate_limiting:
            issues.append("No rate limiting implementation found")

        recommendations = [
            "Implement rate limiting on all public endpoints",
            "Use a library like `slowapi` for FastAPI",
            "Configure different limits for different user types"
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=issues,
            recommendations=recommendations
        )