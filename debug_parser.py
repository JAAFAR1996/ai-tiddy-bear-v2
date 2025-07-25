#!/usr/bin/env python3
"""Debug script to test the lock file parsing"""

import re
from pathlib import Path


def debug_parse_lock_file():
    """Debug the lock file parsing"""
    project_root = Path(__file__).parent
    requirements_lock = project_root / "requirements-lock.txt"

    content = requirements_lock.read_text(encoding="utf-8")
    lines = content.split("\n")

    lock_file_packages = {}

    # Parse requirements file format with proper multi-line handling
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            i += 1
            continue

        # Look for package definition lines (contain == and may end with \)
        if "==" in line and not line.startswith(" "):
            # This is a package definition line
            current_line = line
            print(f"DEBUG: Found package line: {current_line}")

            # Handle multi-line entries with backslash continuation
            while current_line.endswith("\\"):
                i += 1
                if i < len(lines):
                    # Remove the backslash and add the next line (ignoring hash lines)
                    current_line = current_line[:-1].strip()
                    next_line = lines[i].strip()
                    print(f"DEBUG: Processing continuation line: {next_line}")
                    # Skip hash lines and other continuation content
                    if next_line.startswith("--hash=") or next_line.startswith(" "):
                        continue
                else:
                    break

            # Extract package name and version from the complete line
            # Remove any trailing backslash or whitespace
            clean_line = current_line.rstrip(" \\").strip()
            print(f"DEBUG: Clean line: {clean_line}")

            # Match package name and version
            match = re.match(
                r"^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)==([^\s\\]+)", clean_line
            )
            if match:
                package_name = match.group(1).lower()
                version = match.group(2)
                # Remove extras specification for comparison
                clean_name = re.sub(r"\[.*\]", "", package_name)
                lock_file_packages[clean_name] = version
                print(f"DEBUG: Added package: {clean_name} == {version}")
            else:
                print(f"DEBUG: No match for line: {clean_line}")

        i += 1

    print(f"\nDEBUG: Total packages parsed: {len(lock_file_packages)}")
    print("DEBUG: All packages:")
    for name, version in sorted(lock_file_packages.items()):
        print(f"  {name} == {version}")


if __name__ == "__main__":
    debug_parse_lock_file()
