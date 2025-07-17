"""Logging Security Monitor

This module monitors and enforces secure logging practices
throughout the AI Teddy Bear application to prevent data leaks.
"""

import re
import warnings
from pathlib import Path
from typing import Any, Dict, List

from .log_sanitizer import LogSanitizer


class LoggingSecurityMonitor:
    """
    Ensures all log messages are sanitized and COPPA-compliant
    before being written to log files.
    """

    def __init__(self) -> None:
        self.sanitizer = LogSanitizer()
        self.violations_found: List[Dict[str, Any]] = []
        # Patterns to detect potential sensitive data in logs
        self.sensitive_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\+?[\d\s\-\(\)]{10,}\b",
            "child_id": r'\bchild_id["\s]*[:=]["\s]*[A-Za-z0-9\-_]+',
            "parent_id": r'\bparent_id["\s]*[:=]["\s]*[A-Za-z0-9\-_]+',
            "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
            "credit_card": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "api_key": r"\b[A-Za-z0-9]{32,}\b",
            "password": r'password["\s]*[:=]["\s]*[^\s"\']+',
            "token": r'token["\s]*[:=]["\s]*[A-Za-z0-9\-_\.]+',
        }

    def scan_codebase_for_violations(self, source_dir: str) -> Dict[str, Any]:
        """
        Scan the codebase for potential logging security violations
        Args: source_dir: Root directory to scan
        Returns: Report of findings and violations
        """
        violations = []
        files_scanned = 0
        source_path = Path(source_dir)
        for py_file in source_path.rglob("*.py"):
            files_scanned += 1
            file_violations = self._scan_file_for_violations(py_file)
            violations.extend(file_violations)
        return {
            "files_scanned": files_scanned,
            "violations_found": len(violations),
            "violations": violations,
        }

    def _scan_file_for_violations(
        self, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Scan a single file for logging violations."""
        violations = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if "logger." in line or "logging." in line:
                        # Check if the log message is sanitized
                        if "sanitizer.sanitize" not in line:
                            for (
                                data_type,
                                pattern,
                            ) in self.sensitive_patterns.items():
                                if re.search(pattern, line, re.IGNORECASE):
                                    violations.append(
                                        {
                                            "file": str(file_path),
                                            "line": line_num,
                                            "violation": f"Unsanitized log message containing potential {data_type}",
                                            "code": line.strip(),
                                        }
                                    )
        except Exception as e:
            warnings.warn(f"Could not scan file {file_path}: {e}")
        return violations
