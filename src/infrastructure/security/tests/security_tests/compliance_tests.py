"""Compliance Security Tests."""

import re
from typing import Any

from src.infrastructure.logging_config import get_logger

from .base_tester import BaseSecurityTester

logger = get_logger(__name__, component="security")


class ComplianceTester(BaseSecurityTester):
    """Tests for compliance requirements."""

    def test_coppa_compliance(self) -> dict[str, Any]:
        """Test COPPA compliance."""
        issues = []
        coppa_requirements = [
            ("parental_consent", "Parental consent mechanism"),
            ("age_verification", "Age verification system"),
            ("data_encryption", "Child data encryption"),
            ("coppa_compliance", "COPPA compliance flag"),
            ("child_safety", "Child safety measures"),
        ]
        python_files = self.scan_python_files()
        compliance_score = 0
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for requirement, _description in coppa_requirements:
                if requirement in content.lower():
                    compliance_score += 1
                    break

        if compliance_score < len(coppa_requirements):
            missing_requirements = len(coppa_requirements) - compliance_score
            issues.append(
                f"Missing {missing_requirements} COPPA compliance requirements",
            )

        # Check for age restrictions
        age_patterns = [
            r"age\s*[<>=]\s*13",
            r"min_age\s*=\s*13",
            r"COPPA_AGE_LIMIT",
        ]
        has_age_restrictions = False
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern in age_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    has_age_restrictions = True
                    break
        if not has_age_restrictions:
            issues.append("No age verification restrictions found")

        recommendations = [
            "Implement clear parental consent flow",
            "Verify user age before collecting personal information",
            "Encrypt all personally identifiable information (PII)",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=issues,
            recommendations=recommendations,
        )

    def test_gdpr_compliance(self) -> dict[str, Any]:
        """Test GDPR compliance."""
        issues = []
        gdpr_keywords = [
            "GDPR",
            "data protection",
            "right to be forgotten",
            "data portability",
        ]
        python_files = self.scan_python_files()
        has_gdpr_references = False
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            if any(keyword in content.lower() for keyword in gdpr_keywords):
                has_gdpr_references = True
                break

        if not has_gdpr_references:
            issues.append("No GDPR compliance references found")

        recommendations = [
            "Ensure a lawful basis for data processing",
            "Implement mechanisms for data subject rights (access, rectification, erasure)",
            "Provide clear privacy notices",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=issues,
            recommendations=recommendations,
        )
