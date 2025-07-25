#!/usr/bin/env python3
"""Debug script to test UUID + freezegun interaction"""

import sys
import uuid

print(f"Python version: {sys.version}")

# Test 1: UUID before freezegun
print("\n=== BEFORE FREEZEGUN ===")
print(f"UUID module location: {uuid.__file__}")
print(f"Has _load_system_functions: {hasattr(uuid, '_load_system_functions')}")
print(f"UUID attributes: {[attr for attr in dir(uuid) if not attr.startswith('__')]}")

# Test 2: Import freezegun
print("\n=== IMPORTING FREEZEGUN ===")
try:
    from freezegun import freeze_time

    print("Freezegun imported successfully")
except Exception as e:
    print(f"Error importing freezegun: {e}")

# Test 3: UUID after freezegun import
print("\n=== AFTER FREEZEGUN IMPORT ===")
print(f"Has _load_system_functions: {hasattr(uuid, '_load_system_functions')}")
print(f"UUID attributes: {[attr for attr in dir(uuid) if not attr.startswith('__')]}")

# Test 4: Using freeze_time decorator
print("\n=== TESTING FREEZE_TIME USAGE ===")
try:

    @freeze_time("2023-01-01")
    def test_function():
        return "success"

    result = test_function()
    print(f"freeze_time decorator works: {result}")
except Exception as e:
    print(f"Error with freeze_time: {e}")

print("\n=== FINAL UUID STATE ===")
print(f"Has _load_system_functions: {hasattr(uuid, '_load_system_functions')}")
