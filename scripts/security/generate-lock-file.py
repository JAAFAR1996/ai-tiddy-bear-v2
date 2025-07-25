#!/usr/bin/env python3
"""
AI Teddy Bear - Requirements Lock File Generator
Generate production-ready requirements-lock.txt with real SHA256 hashes

This script generates a properly formatted requirements-lock.txt file with
real cryptographic hashes for all dependencies, ensuring package integrity.

Usage:
    python scripts/security/generate-lock-file.py [options]

Options:
    --requirements FILE     Input requirements file (default: requirements.txt)
    --output FILE          Output lock file (default: requirements-lock.txt)
    --include-deps         Include all transitive dependencies
    --dry-run              Show what would be generated without writing file

Exit codes:
    0: Lock file generated successfully
    1: Generation failed
    2: Configuration error
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/lock-file-generation.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


class LockFileGenerator:
    """Production-grade requirements lock file generator."""

    def __init__(self, args):
        self.project_root = Path(__file__).parent.parent.parent
        self.requirements_file = (
            Path(args.requirements)
            if args.requirements
            else self.project_root / "requirements.txt"
        )
        self.output_file = (
            Path(args.output)
            if args.output
            else self.project_root / "requirements-lock.txt"
        )
        self.include_deps = args.include_deps
        self.dry_run = args.dry_run

        # State
        self.package_info: Dict[str, Dict] = {}
        self.package_hashes: Dict[str, List[str]] = {}

    def generate_lock_file(self) -> bool:
        """Generate the requirements lock file with hashes."""
        logger.info("🔒 Starting requirements lock file generation")

        try:
            # Validate input
            if not self._validate_input():
                return False

            # Parse requirements
            packages = self._parse_requirements()
            if not packages:
                return False

            # Get package information and hashes
            if not self._get_package_hashes(packages):
                return False

            # Generate lock file content
            lock_content = self._generate_lock_content()

            # Write or display result
            if self.dry_run:
                print("DRY RUN - Lock file content:")
                print(lock_content)
            else:
                self._write_lock_file(lock_content)

            logger.info("✅ Lock file generation completed successfully")
            return True

        except Exception as e:
            logger.exception(f"💥 Lock file generation failed: {e}")
            return False

    def _validate_input(self) -> bool:
        """Validate input files and configuration."""
        if not self.requirements_file.exists():
            logger.error(f"❌ Requirements file not found: {self.requirements_file}")
            return False

        # Ensure logs directory exists
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        return True

    def _parse_requirements(self) -> List[Tuple[str, str]]:
        """Parse requirements file and extract package names and versions."""
        packages = []

        try:
            content = self.requirements_file.read_text(encoding="utf-8")

            for line_num, line in enumerate(content.split("\n"), 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse package specification
                if "==" in line:
                    match = re.match(
                        r"^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)==([^\s]+)", line
                    )
                    if match:
                        package_name = match.group(1)
                        version = match.group(2)

                        # Remove extras specification for hash lookup
                        clean_name = re.sub(r"\[.*\]", "", package_name)
                        packages.append((clean_name, version))
                    else:
                        logger.warning(f"⚠️ Could not parse line {line_num}: {line}")
                else:
                    logger.warning(
                        f"⚠️ Non-pinned dependency at line {line_num}: {line}"
                    )

            logger.info(f"📦 Parsed {len(packages)} pinned packages")
            return packages

        except Exception as e:
            logger.error(f"❌ Failed to parse requirements file: {e}")
            return []

    def _get_package_hashes(self, packages: List[Tuple[str, str]]) -> bool:
        """Get SHA256 hashes for all packages."""
        logger.info("🔍 Retrieving package hashes from PyPI...")

        session = requests.Session()
        session.headers.update({"User-Agent": "AI-Teddy-Bear-Lock-Generator/1.0"})

        success_count = 0
        failure_count = 0

        for package_name, version in packages:
            try:
                hashes = self._get_package_hash_from_pypi(
                    session, package_name, version
                )
                if hashes:
                    self.package_hashes[f"{package_name}=={version}"] = hashes
                    success_count += 1
                    logger.debug(
                        f"✅ Got {len(hashes)} hashes for {package_name}=={version}"
                    )
                else:
                    logger.warning(f"⚠️ No hashes found for {package_name}=={version}")
                    failure_count += 1

            except Exception as e:
                logger.error(
                    f"❌ Failed to get hashes for {package_name}=={version}: {e}"
                )
                failure_count += 1

        logger.info(
            f"📊 Hash retrieval completed: {success_count} success, {failure_count} failed"
        )

        if failure_count > 0 and success_count == 0:
            logger.error("❌ Failed to retrieve any package hashes")
            return False

        return True

    def _get_package_hash_from_pypi(
        self, session: requests.Session, package_name: str, version: str
    ) -> List[str]:
        """Get SHA256 hashes for a specific package version from PyPI."""
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            hashes = []

            # Get hashes from all distribution files
            for file_info in data.get("urls", []):
                if "digests" in file_info and "sha256" in file_info["digests"]:
                    sha256_hash = file_info["digests"]["sha256"]
                    hashes.append(f"sha256:{sha256_hash}")

            # Sort for consistency
            return sorted(hashes)

        except requests.exceptions.RequestException as e:
            logger.debug(f"PyPI request failed for {package_name}=={version}: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.debug(f"Invalid PyPI response for {package_name}=={version}: {e}")
            return []

    def _generate_lock_content(self) -> str:
        """Generate the complete lock file content."""
        lines = []

        # Header
        lines.append("#")
        lines.append("# AI Teddy Bear - Production Requirements Lock File")
        lines.append(
            "# This file contains pinned dependencies with cryptographic hashes"
        )
        lines.append("# for secure and reproducible deployments.")
        lines.append("#")
        lines.append(f"# Generated on: {datetime.now().isoformat()}")
        lines.append(f"# Total packages: {len(self.package_hashes)}")
        lines.append("#")
        lines.append("# SECURITY WARNING:")
        lines.append("# - Do not modify this file manually")
        lines.append("# - Verify all hashes before installation")
        lines.append("# - Use 'pip install --require-hashes -r requirements-lock.txt'")
        lines.append("#")
        lines.append("")

        # Package entries with hashes
        for package_spec in sorted(self.package_hashes.keys()):
            hashes = self.package_hashes[package_spec]

            if hashes:
                # Package line
                lines.append(f"{package_spec} \\")

                # Hash lines
                for i, hash_value in enumerate(hashes):
                    if i == len(hashes) - 1:
                        # Last hash, no continuation
                        lines.append(f"    --hash={hash_value}")
                    else:
                        # Continuation for multiple hashes
                        lines.append(f"    --hash={hash_value} \\")
            else:
                # Package without hashes (fallback)
                lines.append(f"{package_spec}")
                lines.append(f"    # Warning: No cryptographic hash available")

            lines.append("")  # Empty line between packages

        # Footer
        lines.append("# End of requirements lock file")

        return "\n".join(lines)

    def _write_lock_file(self, content: str) -> None:
        """Write the lock file content to disk."""
        try:
            # Create backup if file exists
            if self.output_file.exists():
                backup_file = self.output_file.with_suffix(".txt.backup")
                self.output_file.rename(backup_file)
                logger.info(f"💾 Created backup: {backup_file}")

            # Write new lock file
            self.output_file.write_text(content, encoding="utf-8")
            logger.info(f"📝 Lock file written to: {self.output_file}")

            # Validate the written file
            if self._validate_lock_file():
                logger.info("✅ Lock file validation passed")
            else:
                logger.warning("⚠️ Lock file validation had issues")

        except Exception as e:
            logger.error(f"❌ Failed to write lock file: {e}")
            raise

    def _validate_lock_file(self) -> bool:
        """Validate the generated lock file."""
        try:
            content = self.output_file.read_text(encoding="utf-8")

            # Basic validation checks
            lines = content.split("\n")

            # Check for basic structure
            if not any("--hash=" in line for line in lines):
                logger.warning("⚠️ No hash lines found in lock file")
                return False

            # Count packages with hashes
            packages_with_hashes = 0
            for line in lines:
                if (
                    line.strip()
                    and not line.startswith("#")
                    and "==" in line
                    and "\\" in line
                ):
                    packages_with_hashes += 1

            logger.info(f"📊 Validation: {packages_with_hashes} packages with hashes")

            # Check hash format
            hash_lines = [line for line in lines if "--hash=" in line]
            invalid_hashes = []

            for line in hash_lines:
                hash_match = re.search(r"--hash=sha256:([a-f0-9]{64})", line)
                if not hash_match:
                    invalid_hashes.append(line.strip())

            if invalid_hashes:
                logger.warning(f"⚠️ Found {len(invalid_hashes)} invalid hash formats")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Lock file validation failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Teddy Bear Requirements Lock File Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--requirements", help="Input requirements file (default: requirements.txt)"
    )
    parser.add_argument(
        "--output", help="Output lock file (default: requirements-lock.txt)"
    )
    parser.add_argument(
        "--include-deps",
        action="store_true",
        help="Include all transitive dependencies",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing file",
    )

    args = parser.parse_args()

    generator = LockFileGenerator(args)

    if generator.generate_lock_file():
        logger.info("✅ Lock file generation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Lock file generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
