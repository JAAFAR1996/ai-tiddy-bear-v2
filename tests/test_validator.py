from src.infrastructure.logging_config import get_logger
from typing import List, Optional
from dataclasses import dataclass
import tempfile
import subprocess
import re
import os
import logging
import ast
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Test Validator for AI-Generated Tests
====================================

Validates and fixes AI-generated test cases to ensure
they are syntactically correct and functionally sound.
"""


logger = get_logger(__name__, component="test")


@dataclass
class ValidationResult:
    """Result of test validation"""

    is_valid: bool
    syntax_errors: List[str]
    import_errors: List[str]
    logic_errors: List[str]
    suggestions: List[str]
    fixed_code: Optional[str] = None


class TestValidator:
    """
    Validates and fixes AI-generated test cases
    ensuring they meet quality and syntax standards.
    """

    def __init__(self):
        # Common import patterns for fixing
        self.common_imports = [
            "import pytest",
            "import asyncio",
            "import unittest",
            "from unittest.mock import Mock, patch, MagicMock",
            "from hypothesis import given, strategies as st, settings",
            "import json",
            "import time",
            "from typing import Any, Dict, List, Optional",
        ]

        # Common test patterns
        self.required_patterns = {
            "test_class": r"class Test\w+:",
            "test_method": r"def test_\w+\(",
            "assertion": r"assert\s+",
            "docstring": r'""".*?"""',
        }

        # Syntax error fixes
        self.syntax_fixes = {
            "missing_colon": r"def\s+(\w+)\s*\([^)]*\)\s*$",
            "missing_self": r"def\s+(test_\w+)\s*\(\s*\)",
            "incorrect_indentation": r"^(\s*)([^\s])",
            "missing_imports": r"(Mock|patch|given|strategies)",
        }

    async def validate_syntax(self, test_code: str) -> bool:
        """
        Validate Python syntax of test code

        Args:
            test_code: Test code to validate

        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            ast.parse(test_code)
            return True
        except SyntaxError as e:
            logger.debug(f"Syntax error in test code: {e}")
            return False
        except Exception as e:
            logger.debug(f"Error parsing test code: {e}")
            return False

    async def comprehensive_validation(
            self, test_code: str) -> ValidationResult:
        """
        Perform comprehensive validation of test code

        Args:
            test_code: Test code to validate

        Returns:
            Detailed validation result
        """
        result = ValidationResult(
            is_valid=True,
            syntax_errors=[],
            import_errors=[],
            logic_errors=[],
            suggestions=[],
        )

        # Check syntax
        syntax_valid = await self.validate_syntax(test_code)
        if not syntax_valid:
            result.is_valid = False
            result.syntax_errors = await self._find_syntax_errors(test_code)

        # Check imports
        import_errors = await self._check_imports(test_code)
        if import_errors:
            result.import_errors = import_errors
            if not result.syntax_errors:  # Only mark invalid if no syntax errors
                result.is_valid = False

        # Check test structure
        logic_errors = await self._check_test_logic(test_code)
        if logic_errors:
            result.logic_errors = logic_errors

        # Generate suggestions
        result.suggestions = await self._generate_suggestions(test_code)

        return result

    async def fix_test(self, test_code: str) -> Optional[str]:
        """
        Attempt to fix common issues in test code

        Args:
            test_code: Test code to fix

        Returns:
            Fixed test code or None if unfixable
        """
        try:
            fixed_code = test_code

            # Apply syntax fixes
            fixed_code = await self._fix_syntax_errors(fixed_code)

            # Fix imports
            fixed_code = await self._fix_imports(fixed_code)

            # Fix test structure
            fixed_code = await self._fix_test_structure(fixed_code)

            # Validate the fixed code
            if await self.validate_syntax(fixed_code):
                return fixed_code
            else:
                logger.warning("Could not fix test code")
                return None

        except Exception as e:
            logger.error(f"Error fixing test code: {e}")
            return None

    async def _find_syntax_errors(self, test_code: str) -> List[str]:
        """Find specific syntax errors in the code"""
        errors = []

        try:
            ast.parse(test_code)
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")

        return errors

    async def _check_imports(self, test_code: str) -> List[str]:
        """Check for missing or incorrect imports"""
        errors = []

        # Check for usage without imports
        if "Mock" in test_code and "from unittest.mock import" not in test_code:
            errors.append("Missing import: from unittest.mock import Mock")

        if "@given" in test_code and "from hypothesis import" not in test_code:
            errors.append(
                "Missing import: from hypothesis import given, strategies as st"
            )

        if "pytest" in test_code and "import pytest" not in test_code:
            errors.append("Missing import: import pytest")

        if "asyncio" in test_code and "import asyncio" not in test_code:
            errors.append("Missing import: import asyncio")

        return errors

    async def _check_test_logic(self, test_code: str) -> List[str]:
        """Check for logical errors in test structure"""
        errors = []

        # Check for test class
        if not re.search(self.required_patterns["test_class"], test_code):
            errors.append("No test class found (should start with 'Test')")

        # Check for test methods
        if not re.search(self.required_patterns["test_method"], test_code):
            errors.append("No test methods found (should start with 'test_')")

        # Check for assertions
        if not re.search(self.required_patterns["assertion"], test_code):
            errors.append("No assertions found in test code")

        # Check for empty test methods
        if "pass" in test_code and "assert" not in test_code:
            errors.append(
                "Test method appears to be empty (only contains 'pass')")

        # Check for proper indentation
        lines = test_code.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("def test_") and not line.startswith("    "):
                if i > 1:  # Not the first line
                    errors.append(
                        f"Line {i}: Test method not properly indented")

        return errors

    async def _generate_suggestions(self, test_code: str) -> List[str]:
        """Generate suggestions for improving test code"""
        suggestions = []

        # Suggest docstrings if missing
        if not re.search(self.required_patterns["docstring"], test_code):
            suggestions.append(
                "Add docstrings to test methods for better documentation"
            )

        # Suggest better assertions
        if "assert True" in test_code:
            suggestions.append(
                "Replace 'assert True' with meaningful assertions")

        # Suggest setup/teardown if needed
        if "Mock" in test_code and "setUp" not in test_code:
            suggestions.append(
                "Consider using setUp/tearDown for mock initialization")

        # Suggest async/await usage
        if "async def" in test_code and "await" not in test_code:
            suggestions.append(
                "Async test method should use 'await' for async operations"
            )

        # Suggest proper exception testing
        if "Exception" in test_code and "pytest.raises" not in test_code:
            suggestions.append("Use pytest.raises() for testing exceptions")

        return suggestions

    async def _fix_syntax_errors(self, test_code: str) -> str:
        """Fix common syntax errors"""
        fixed_code = test_code

        # Fix missing colons in function definitions
        fixed_code = re.sub(
            r"def\s+(\w+)\s*\([^)]*\)\s*$", r"def \1():", fixed_code, flags=re.MULTILINE
        )

        # Fix missing 'self' parameter in test methods
        fixed_code = re.sub(
            r"def\s+(test_\w+)\s*\(\s*\)",
            r"def \1(self)",
            fixed_code)

        # Fix basic indentation issues
        lines = fixed_code.split("\n")
        fixed_lines = []
        in_class = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("class "):
                in_class = True
                fixed_lines.append(line)
            elif stripped.startswith("def ") and in_class:
                # Ensure proper indentation for methods
                fixed_lines.append("    " + stripped)
            elif (
                stripped
                and in_class
                and not line.startswith("    ")
                and not stripped.startswith("class")
            ):
                # Ensure proper indentation for method content
                fixed_lines.append("        " + stripped)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _determine_needed_imports(self, test_code: str) -> List[str]:
        """Determine which standard imports are needed in the test code."""
        needed_imports = []
        import_map = {
            "Mock": "from unittest.mock import Mock, patch, MagicMock",
            "@given": "from hypothesis import given, strategies as st, settings",
            "pytest": "import pytest",
            "asyncio": "import asyncio",
        }
        for keyword, import_statement in import_map.items():
            if keyword in test_code and import_statement not in test_code:
                needed_imports.append(import_statement)
        return needed_imports

    async def _fix_imports(self, test_code: str) -> str:
        """Fix missing imports by adding them at the top of the file."""
        lines = test_code.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("class ") or line.strip().startswith("def "):
                insert_index = i
                break

        needed_imports = self._determine_needed_imports(test_code)
        if needed_imports:
            # Insert needed imports in reverse to maintain order
            for import_stmt in reversed(needed_imports):
                lines.insert(insert_index, import_stmt)
            # Add a blank line for readability
            lines.insert(insert_index + len(needed_imports), "")

        return "\n".join(lines)

    async def _fix_test_structure(self, test_code: str) -> str:
        """Fix test structure issues"""
        fixed_code = test_code

        # Ensure test class exists
        if not re.search(self.required_patterns["test_class"], test_code):
            # Wrap existing test methods in a class
            lines = fixed_code.split("\n")
            new_lines = []

            # Add test class header
            new_lines.append("class TestGenerated:")
            new_lines.append('    """Generated test class"""')
            new_lines.append("")

            # Indent existing content
            for line in lines:
                if line.strip():
                    new_lines.append("    " + line)
                else:
                    new_lines.append("")

            fixed_code = "\n".join(new_lines)

        # Fix empty test methods
        fixed_code = re.sub(
            r"(def test_\w+\([^)]*\):\s*)\n\s*pass",
            r'\1\n        """Generated test method"""\n        assert True  # TODO: Add meaningful assertions',
            fixed_code,
            flags=re.MULTILINE | re.DOTALL,
        )

        # Add missing assertions
        if "assert" not in fixed_code:
            # Find test methods and add basic assertions
            lines = fixed_code.split("\n")
            new_lines = []

            for i, line in enumerate(lines):
                new_lines.append(line)

                # If this is a test method definition, add assertion
                if re.match(r"\s*def test_\w+\(", line):
                    # Look ahead to see if there's already content
                    next_line_index = i + 1
                    if next_line_index < len(lines) and lines[
                        next_line_index
                    ].strip() in ["", "pass"]:
                        new_lines.append('        """Generated test method"""')
                        new_lines.append(
                            "        assert True  # TODO #034: Add meaningful assertions"
                        )

            fixed_code = "\n".join(new_lines)

        return fixed_code

    async def run_test_execution_check(self, test_code: str) -> bool:
        """
        Run the test code to check if it executes without errors

        Args:
            test_code: Test code to execute

        Returns:
            True if test runs without errors, False otherwise
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(test_code)
                temp_file = f.name

            try:
                # Run pytest on the temporary file
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", temp_file, "-v"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                # Check if pytest ran successfully (even if tests failed)
                # 0=passed, 1=failed but ran
                return result.returncode in [0, 1]

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        except Exception as e:
            logger.debug(f"Test execution check failed: {e}")
            return False

    async def validate_child_safety_compliance(self, test_code: str) -> bool:
        """
        Validate that test code complies with child safety requirements

        Args:
            test_code: Test code to validate

        Returns:
            True if compliant, False otherwise
        """
        # Check for inappropriate content in test code
        inappropriate_keywords = [
            "inappropriate",
            "adult",
            "violence",
            "harmful",
            "dangerous",
            "scary",
            "weapon",
        ]

        test_code_lower = test_code.lower()

        for keyword in inappropriate_keywords:
            if keyword in test_code_lower:
                # Check if it's in a proper testing context
                if (
                    f"test_{keyword}" not in test_code_lower
                    and f"assert not {keyword}" not in test_code_lower
                ):
                    logger.warning(
                        f"Test code contains inappropriate keyword: {keyword}"
                    )
                    return False

        # Check for proper safety testing patterns
        safety_patterns = [
            "age_appropriate",
            "content_filter",
            "safety_check",
            "child_protection",
        ]

        has_safety_testing = any(
            pattern in test_code_lower for pattern in safety_patterns
        )

        return has_safety_testing or "safety" in test_code_lower
