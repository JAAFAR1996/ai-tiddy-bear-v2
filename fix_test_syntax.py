#!/usr/bin/env python3
"""Quick syntax fixes for test files"""

import re
from pathlib import Path

# Files that need syntax fixes based on the pre-commit output
broken_files = [
    "tests/backend_components/test_ai_service.py",
    "tests/backend_components/test_conversation_service.py",
    "tests/backend_components/test_emotion_service.py",
    "tests/backend_components/test_encryption_service.py",
    "tests/backend_components/test_error_handling_and_recovery.py",
    "tests/backend_components/test_esp32_integration.py",
    "tests/backend_components/test_performance_and_scaling.py",
    "tests/backend_components/test_report_generation.py",
    "tests/backend_components/test_safety_and_moderation.py",
    "tests/e2e/test_full_journey.py",
    "tests/e2e/test_mobile_experience.py",
    "tests/frontend_components/test_authentication.py",
    "tests/frontend_components/test_child_profile.py",
    "tests/frontend_components/test_conversations.py",
    "tests/frontend_components/test_dashboard.py",
    "tests/frontend_components/test_emergency_alerts.py",
    "tests/frontend_components/test_error_handling.py",
    "tests/frontend_components/test_integration.py",
    "tests/frontend_components/test_performance.py",
    "tests/frontend_components/test_reports.py",
    "tests/frontend_components/test_websocket.py",
    "tests/unit/conversation_repository_tests/test_aggregation.py",
    "tests/unit/conversation_repository_tests/test_analytics.py",
    "tests/unit/conversation_repository_tests/test_basic_operations.py",
    "tests/unit/conversation_repository_tests/test_error_handling.py",
    "tests/unit/conversation_repository_tests/test_integration.py",
    "tests/unit/conversation_repository_tests/test_maintenance.py",
    "tests/unit/conversation_repository_tests/test_messaging.py",
    "tests/unit/conversation_repository_tests/test_search.py",
]


def fix_syntax_issues():
    """Fix common syntax issues in test files"""
    fixed_count = 0

    for file_path in broken_files:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"File not found: {file_path}")
            continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix incomplete function definitions
            content = re.sub(
                r"def fixture\(self, \*args, \*\*kwargs\):\s*\n\s*class",
                r"def fixture(self, *args, **kwargs):\n            pass\n\n        class",
                content,
            )

            # Fix incomplete decorator definitions
            content = re.sub(
                r"def decorator\(func\):\s*\n\s*return",
                r"def decorator(func):\n                return",
                content,
            )

            # Fix incomplete except blocks
            content = re.sub(
                r"except.*:\s*\n\s*class MockPytest:",
                r"except ImportError:\n        pass\n\n    class MockPytest:",
                content,
            )

            # Fix missing pass statements
            content = re.sub(
                r"(\s+def \w+\([^)]*\):\s*\n)(\s+)(class|\w+)",
                r"\1\2pass\n\n\2\3",
                content,
            )

            if content != original_content:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed syntax in: {file_path}")
                fixed_count += 1
            else:
                print(f"No fixes needed: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    fix_syntax_issues()
