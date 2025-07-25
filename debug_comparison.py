#!/usr/bin/env python3
"""Debug script to compare installed vs lock file packages"""

import re
import importlib.metadata
from pathlib import Path

def debug_package_comparison():
    """Debug package comparison between installed and lock file"""
    project_root = Path(__file__).parent
    requirements_lock = project_root / "requirements-lock.txt"
    
    # Parse lock file (using the fixed algorithm)
    content = requirements_lock.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    lock_file_packages = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line or line.startswith("#"):
            i += 1
            continue
        
        if "==" in line and not line.startswith(" "):
            current_line = line
            
            while current_line.endswith("\\"):
                i += 1
                if i < len(lines):
                    current_line = current_line[:-1].strip()
                    next_line = lines[i].strip()
                    if next_line.startswith("--hash=") or next_line.startswith(" "):
                        continue
                else:
                    break
            
            clean_line = current_line.rstrip(" \\").strip()
            
            match = re.match(
                r"^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)==([^\s\\]+)", clean_line
            )
            if match:
                package_name = match.group(1).lower()
                version = match.group(2)
                clean_name = re.sub(r"\[.*\]", "", package_name)
                lock_file_packages[clean_name] = version
        
        i += 1
    
    # Get installed packages
    installed_packages = {}
    try:
        for dist_name in importlib.metadata.distributions():
            installed_packages[dist_name.metadata['name'].lower()] = dist_name.version
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        return
    
    print(f"Lock file packages: {len(lock_file_packages)}")
    print(f"Installed packages: {len(installed_packages)}")
    
    # Find packages in lock file but not installed
    missing_packages = []
    for name in lock_file_packages:
        if name not in installed_packages:
            missing_packages.append((name, lock_file_packages[name]))
    
    # Find packages installed but not in lock file
    extra_packages = []
    for name in installed_packages:
        if name not in lock_file_packages and name not in ["pip", "setuptools", "wheel"]:
            extra_packages.append((name, installed_packages[name]))
    
    # Find version mismatches
    version_mismatches = []
    for name in lock_file_packages:
        if name in installed_packages:
            if installed_packages[name] != lock_file_packages[name]:
                version_mismatches.append((name, installed_packages[name], lock_file_packages[name]))
    
    print(f"\n=== MISSING PACKAGES (in lock file, not installed): {len(missing_packages)} ===")
    for name, version in missing_packages[:10]:  # Show first 10
        print(f"  {name} == {version}")
    if len(missing_packages) > 10:
        print(f"  ... and {len(missing_packages) - 10} more")
    
    print(f"\n=== EXTRA PACKAGES (installed, not in lock file): {len(extra_packages)} ===")
    for name, version in extra_packages[:10]:  # Show first 10
        print(f"  {name} == {version}")
    if len(extra_packages) > 10:
        print(f"  ... and {len(extra_packages) - 10} more")
    
    print(f"\n=== VERSION MISMATCHES: {len(version_mismatches)} ===")
    for name, installed_ver, lock_ver in version_mismatches[:10]:  # Show first 10
        print(f"  {name}: installed={installed_ver}, lock={lock_ver}")
    if len(version_mismatches) > 10:
        print(f"  ... and {len(version_mismatches) - 10} more")
    
    # Check specific examples
    test_packages = ["aiofiles", "fastapi", "jinja2", "requests", "starlette"]
    print(f"\n=== SPECIFIC PACKAGE CHECK ===")
    for pkg in test_packages:
        lock_version = lock_file_packages.get(pkg, "NOT FOUND")
        installed_version = installed_packages.get(pkg, "NOT FOUND")
        print(f"  {pkg}: lock={lock_version}, installed={installed_version}")

if __name__ == "__main__":
    debug_package_comparison()
