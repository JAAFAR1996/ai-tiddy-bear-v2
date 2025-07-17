"""Injection Security Tests"""

import re
from typing import Any, Dict

from src.infrastructure.logging_config import get_logger

from .base_tester import BaseSecurityTester

logger = get_logger(__name__, component="security")


class InjectionTester(BaseSecurityTester):
    """Tests for various injection vulnerabilities"""

    def test_code_injection(self) -> Dict[str, Any]:
        """Test for code injection vulnerabilities"""
        issues = []
        dangerous_patterns = [
            (r"\beval\s*\(", "eval() function found"),
            (r"\bexec\s*\(", "exec() function found"),
            (r"__import__\s*\(", "__import__() function found"),
            (r"compile\s*\(", "compile() function found"),
            (r"subprocess\.call\s*\(", "subprocess.call() without validation"),
            (r"os\.system\s*\(", "os.system() without validation"),
        ]
        python_files = self.scan_python_files()
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern, description in dangerous_patterns:
                if re.search(pattern, content):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "high",
                        }
                    )
        recommendations = [
            "Replace eval() with ast.literal_eval() for safe evaluation",
            "Use parameterized queries instead of string formatting",
            "Implement input validation and sanitization",
            "Use allowlists instead of denylists for validation",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )

    def test_sql_injection(self) -> Dict[str, Any]:
        """Test for SQL injection vulnerabilities"""
        issues = []
        sql_patterns = [
            # Detect f-strings in execute calls containing SELECT (basic heuristic)
            (r"execute\s*\(.*f['\"].*SELECT.*", "f-string in SQL query"),
            # Detect %-formatting in execute calls containing SELECT
            (
                r"execute\s*\(.*['\"].*SELECT.*%s.*",
                "%-formatting in SQL query",
            ),
            # Detect .format() usage in execute calls containing SELECT
            (r"execute\s*\(.*['\"].*SELECT.*\{\}.*", ".format() in SQL query"),
        ]
        python_files = self.scan_python_files()
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern, description in sql_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "critical",
                        }
                    )
        recommendations = [
            "Use parameterized queries with your database driver",
            "Use an ORM like SQLAlchemy to prevent SQL injection",
            "Sanitize all input that is used in database queries",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )

    def test_xss_vulnerabilities(self) -> Dict[str, Any]:
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        issues = []
        xss_patterns = [
            (r"mark_safe\s*\(", "mark_safe() usage in Django/Jinja2"),
            (
                r"dangerouslySetInnerHTML",
                "dangerouslySetInnerHTML usage in React (if applicable)",
            ),
            (r"innerHTML\s*=", "Direct assignment to innerHTML"),
        ]
        # Scan HTML/template files as well
        template_files = list(self.base_path.rglob("*.html")) + list(
            self.base_path.rglob("*.jinja2")
        )
        for file_path in template_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            if (
                "{{ content|safe }}" in content
                or "{{ content|escape|safe }}" in content
            ):
                issues.append(
                    {
                        "file": str(file_path),
                        "issue": "Unescaped variable with |safe filter",
                        "severity": "high",
                    }
                )

            # Additionally check for unsafe patterns in templates
            for pattern, description in xss_patterns:
                if re.search(pattern, content):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "high",
                        }
                    )

        recommendations = [
            "Use auto-escaping template engines (e.g., Jinja2, Django templates)",
            "Avoid using `mark_safe` or equivalent functions",
            "Sanitize user-generated content before rendering",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )

    def test_path_traversal(self) -> Dict[str, Any]:
        """Test for path traversal vulnerabilities"""
        issues = []
        path_patterns = [
            (
                r"os\.path\.join\s*\(.*request\.args.*",
                "Path joining with user input",
            ),
            (r"open\s*\(.*request\.args.*", "File open with user input"),
        ]
        python_files = self.scan_python_files()
        for file_path in python_files:
            content = self.read_file_safely(file_path)
            if not content:
                continue
            for pattern, description in path_patterns:
                if re.search(pattern, content):
                    issues.append(
                        {
                            "file": str(file_path),
                            "issue": description,
                            "severity": "high",
                        }
                    )

        recommendations = [
            "Never use user-provided input directly in file paths",
            "Use a secure method to serve files, ensuring the path is within a safe directory",
            "Validate and sanitize all file path inputs",
        ]
        return self.create_test_result(
            passed=len(issues) == 0,
            issues=[f"{issue['file']}: {issue['issue']}" for issue in issues],
            recommendations=recommendations,
        )
