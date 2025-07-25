"""Base Security Tester Class."""

from datetime import datetime
from pathlib import Path
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class BaseSecurityTester:
    """Base class for security testers."""

    def __init__(self, base_path: str = ".") -> None:
        self.base_path = Path(base_path)
        self.test_results = []

    def create_test_result(
        self,
        passed: bool,
        issues: list[str],
        recommendations: list[str],
    ) -> dict[str, Any]:
        """Create standardized test result."""
        return {
            "passed": passed,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    def scan_python_files(self) -> list[Path]:
        """Get all Python files in the project."""
        return list(self.base_path.rglob("*.py"))

    def read_file_safely(self, file_path: Path) -> str:
        """Read file content safely with error handling."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return ""
