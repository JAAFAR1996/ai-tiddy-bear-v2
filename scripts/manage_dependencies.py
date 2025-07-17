#!/usr/bin/env python3
"""
AI Teddy Bear - Dependency Management Script
Standardized dependency management and environment setup.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str],
                check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def install_dependencies(env: str = "dev") -> None:
    """Install dependencies based on environment."""
    print(f"Installing dependencies for {env} environment...")

    if env == "prod":
        requirements_file = "requirements.txt"
    elif env == "dev":
        requirements_file = "requirements-dev.txt"
    else:
        raise ValueError(f"Unknown environment: {env}")

    # Check if we're in a virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("WARNING: No virtual environment detected. Consider using:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # Linux/Mac")
        print("  venv\\Scripts\\activate     # Windows")
        print()

    # Upgrade pip first
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Install dependencies
    run_command([sys.executable, "-m", "pip",
                "install", "-r", requirements_file])

    print(f"✅ Dependencies installed successfully for {env} environment")


def check_security() -> None:
    """Run security checks on dependencies."""
    print("Running security checks...")

    try:
        # Check for known vulnerabilities
        run_command([sys.executable, "-m", "safety", "check"])
        print("✅ No known security vulnerabilities found")
    except subprocess.CalledProcessError:
        print("⚠️  Security vulnerabilities found. Review the output above.")

    try:
        # Audit dependencies
        run_command([sys.executable, "-m", "pip_audit"])
        print("✅ Dependency audit completed")
    except subprocess.CalledProcessError:
        print("⚠️  Issues found in dependency audit. Review the output above.")


def generate_lock_file() -> None:
    """Generate a lock file with exact versions."""
    print("Generating dependency lock file...")

    result = run_command([sys.executable, "-m", "pip", "freeze"], check=False)

    if result.returncode == 0:
        with open("requirements.lock", "w") as f:
            f.write("# AI Teddy Bear - Dependency Lock File\n")
            f.write("# Generated automatically - DO NOT EDIT\n")
            f.write("# Use: pip install -r requirements.lock\n\n")
            f.write(result.stdout)
        print("✅ Lock file generated: requirements.lock")
    else:
        print("❌ Failed to generate lock file")


def check_compatibility() -> None:
    """Check Python version compatibility."""
    print("Checking Python compatibility...")

    python_version = sys.version_info
    required_major, required_minor = 3, 11

    if python_version.major != required_major or python_version.minor < required_minor:
        print(
            f"❌ Python {required_major}.{required_minor}+ required, got {python_version.major}.{python_version.minor}"
        )
        sys.exit(1)
    else:
        print(
            f"✅ Python {python_version.major}.{python_version.minor} is compatible")


def clean_dependencies() -> None:
    """Clean up pip cache and temporary files."""
    print("Cleaning dependency cache...")

    run_command([sys.executable, "-m", "pip", "cache", "purge"], check=False)
    print("✅ Dependency cache cleaned")


def validate_environment() -> None:
    """Validate that required environment variables are set."""
    print("Validating environment configuration...")

    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "OPENAI_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Create a .env file or set these variables in your environment")
        print("   See .env.example for guidance")
    else:
        print("✅ All required environment variables are set")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Teddy Bear Dependency Manager")
    parser.add_argument(
        "command",
        choices=[
            "install",
            "security",
            "lock",
            "check",
            "clean",
            "validate",
            "all"],
        help="Command to run",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        default="dev",
        help="Environment (dev or prod)",
    )

    args = parser.parse_args()

    # Change to script directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)

    print(f"🧸 AI Teddy Bear Dependency Manager")
    print(f"Working directory: {os.getcwd()}")
    print()

    try:
        if args.command == "install":
            check_compatibility()
            install_dependencies(args.env)
        elif args.command == "security":
            check_security()
        elif args.command == "lock":
            generate_lock_file()
        elif args.command == "check":
            check_compatibility()
        elif args.command == "clean":
            clean_dependencies()
        elif args.command == "validate":
            validate_environment()
        elif args.command == "all":
            check_compatibility()
            install_dependencies(args.env)
            check_security()
            generate_lock_file()
            validate_environment()
            print("\n🎉 All dependency management tasks completed!")

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
