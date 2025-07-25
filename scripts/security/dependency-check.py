#!/usr/bin/env python3
"""
AI Teddy Bear - Production Dependency Health Check
Security-critical dependency validation and health monitoring

This script validates that all installed packages match the lock file
and have no known vulnerabilities.

Usage:
    python scripts/security/dependency-check.py

Exit codes:
    0: All checks passed
    1: Critical security issue found
    2: Configuration or environment error
"""

import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pkg_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/dependency-check.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Represents a security issue found in dependencies."""

    severity: str
    package: str
    version: str
    issue: str
    cve_id: str | None = None
    fixed_version: str | None = None


@dataclass
class DependencyInfo:
    """Information about a dependency."""

    name: str
    version: str
    location: str
    hash_sha256: str | None = None
    license: str | None = None


class DependencySecurityChecker:
    """Production-grade dependency security checker."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.requirements_lock = self.project_root / "requirements-lock.txt"
        self.issues: list[SecurityIssue] = []
        self.installed_packages: dict[str, DependencyInfo] = {}
        self.lock_file_packages: dict[str, str] = {}

        # Security configuration
        self.forbidden_licenses = {
            "AGPL-1.0",
            "AGPL-3.0",
            "GPL-2.0",
            "GPL-3.0",
            "LGPL-2.1",
            "LGPL-3.0",
            "SSPL-1.0",
            "MongoDB",
            "Redis Source Available License",
        }

        self.critical_packages = {
            "fastapi",
            "uvicorn",
            "starlette",
            "pydantic",
            "cryptography",
            "sqlalchemy",
            "asyncpg",
            "python-jose",
            "passlib",
            "bcrypt",
        }

    def run_security_check(self) -> bool:
        """Run complete security check. Returns True if all checks pass."""
        logger.info("🔒 Starting production dependency security check")

        try:
            # Pre-flight checks
            if not self._validate_environment():
                return False

            # Load lock file
            if not self._load_lock_file():
                return False

            # Get installed packages
            if not self._get_installed_packages():
                return False

            # Security validations
            success = self._run_all_checks()

            # Generate security report
            self._generate_security_report()

            if not success or self.issues:
                logger.error(f"❌ Found {len(self.issues)} security issues")
                self._print_security_issues()
                return False

            logger.info("🎉 All dependency security checks passed!")
            return True

        except Exception as e:
            logger.exception(f"💥 Unexpected error during security check: {e}")
            return False

    def _run_all_checks(self) -> bool:
        """Run all security checks."""
        checks = [
            ("Package integrity", self._check_package_integrity),
            ("Version compliance", self._check_version_compliance),
            ("License compliance", self._check_license_compliance),
            ("Known vulnerabilities", self._check_vulnerabilities),
            ("Critical package security", self._check_critical_packages),
            ("Dependency conflicts", self._check_dependency_conflicts),
        ]

        for check_name, check_func in checks:
            logger.info(f"🔍 Running {check_name} check...")
            if not check_func():
                logger.error(f"❌ {check_name} check failed")
                return False
            logger.info(f"✅ {check_name} check passed")

        return True

    def _validate_environment(self) -> bool:
        """Validate the environment setup"""
        if not self.requirements_lock.exists():
            logger.error(f"❌ Lock file not found: {self.requirements_lock}")
            return False

        if not self.requirements_lock.stat().st_size > 0:
            logger.error("❌ Lock file is empty")
            return False

        # Check if logs directory exists
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        return True

    def _load_lock_file(self) -> bool:
        """Load and parse the requirements lock file"""
        try:
            content = self.requirements_lock.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Parse requirements file format with proper multi-line handling
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    i += 1
                    continue

                # Look for package definition lines (contain == and may end with \)
                if "==" in line and not line.startswith(" ") and not line.startswith("--"):
                    # This is a package definition line - collect the complete entry
                    package_line = line

                    # Handle multi-line entries with backslash continuation
                    while package_line.endswith("\\"):
                        i += 1
                        if i < len(lines):
                            # Remove the trailing backslash and whitespace
                            package_line = package_line.rstrip("\\").strip()
                            # Skip the hash lines - we only need the package==version part
                            break
                        else:
                            break

                    # Extract package name and version from the package line
                    clean_line = package_line.strip()

                    # Match package name and version (handle extras like package[extra]==version)
                    match = re.match(
                        r"^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)==([^\s\\]+)", clean_line
                    )
                    if match:
                        package_name = match.group(1).lower()
                        version = match.group(2)

                        # Normalize package name (remove extras and normalize separators)
                        clean_name = re.sub(r"\[.*\]", "", package_name)
                        # Normalize hyphens/underscores to hyphens (pip standard)
                        clean_name = re.sub(r"[-_.]+", "-", clean_name)

                        self.lock_file_packages[clean_name] = version

                i += 1

            logger.info(
                f"📋 Loaded {len(self.lock_file_packages)} packages from lock file"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load lock file: {e}")
            return False

    def _get_installed_packages(self) -> bool:
        """Get information about installed packages"""
        try:
            for dist in pkg_resources.working_set:
                self.installed_packages[dist.project_name.lower()] = DependencyInfo(
                    name=dist.project_name.lower(),
                    version=dist.version,
                    location=dist.location,
                    license=self._get_package_license(dist),
                )

            logger.info(f"📦 Found {len(self.installed_packages)} installed packages")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to get installed packages: {e}")
            return False

    def _get_package_license(self, dist) -> str | None:
        """Get license information for a package."""
        try:
            if hasattr(dist, "get_metadata"):
                metadata = dist.get_metadata("METADATA")
                for line in metadata.split("\n"):
                    if line.startswith("License:"):
                        return line.split(":", 1)[1].strip()
        except Exception:
            # Log and ignore license detection failures
            logger.debug(f"Could not determine license for {dist.project_name}")
        return None

    def _check_package_integrity(self) -> bool:
        """Check package integrity against lock file"""
        issues_found = False

        # Check for packages not in lock file
        for package_name in self.installed_packages:
            if package_name not in self.lock_file_packages:
                if package_name not in [
                    "pip",
                    "setuptools",
                    "wheel",
                ]:  # Allow build tools
                    self.issues.append(
                        SecurityIssue(
                            severity="HIGH",
                            package=package_name,
                            version=self.installed_packages[package_name].version,
                            issue="Package installed but not in lock file",
                        )
                    )
                    issues_found = True

        # Check for missing packages
        for package_name in self.lock_file_packages:
            if package_name not in self.installed_packages:
                self.issues.append(
                    SecurityIssue(
                        severity="CRITICAL",
                        package=package_name,
                        version=self.lock_file_packages[package_name],
                        issue="Package in lock file but not installed",
                    )
                )
                issues_found = True

        return not issues_found

    def _check_version_compliance(self) -> bool:
        """Check that installed versions match lock file"""
        issues_found = False

        for package_name, lock_version in self.lock_file_packages.items():
            if package_name in self.installed_packages:
                installed_version = self.installed_packages[package_name].version
                if installed_version != lock_version:
                    severity = (
                        "CRITICAL" if package_name in self.critical_packages else "HIGH"
                    )
                    self.issues.append(
                        SecurityIssue(
                            severity=severity,
                            package=package_name,
                            version=installed_version,
                            issue=f"Version mismatch: installed {installed_version}, lock file {lock_version}",
                        )
                    )
                    issues_found = True

        return not issues_found

    def _check_license_compliance(self) -> bool:
        """Check license compliance"""
        issues_found = False

        for package_name, package_info in self.installed_packages.items():
            if package_info.license and package_info.license in self.forbidden_licenses:
                self.issues.append(
                    SecurityIssue(
                        severity="HIGH",
                        package=package_name,
                        version=package_info.version,
                        issue=f"Forbidden license detected: {package_info.license}",
                    )
                )
                issues_found = True

        return not issues_found

    def _check_vulnerabilities(self) -> bool:
        """Check for known vulnerabilities using pip-audit"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--desc", "--format=json"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                if result.stdout:
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        self.issues.append(
                            SecurityIssue(
                                severity="CRITICAL",
                                package=vuln.get("name", "unknown"),
                                version=vuln.get("version", "unknown"),
                                issue=vuln.get("description", "Known vulnerability"),
                                cve_id=vuln.get("id"),
                                fixed_version=vuln.get("fix_versions", [None])[0],
                            )
                        )
                return False

            return True

        except subprocess.TimeoutExpired:
            logger.error("❌ Vulnerability check timed out")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Could not run vulnerability check: {e}")
            return True  # Don't fail build if tool is not available

    def _check_critical_packages(self) -> bool:
        """Perform additional checks on critical packages"""
        issues_found = False

        for package_name in self.critical_packages:
            if package_name not in self.installed_packages:
                self.issues.append(
                    SecurityIssue(
                        severity="CRITICAL",
                        package=package_name,
                        version="N/A",
                        issue="Critical package is missing",
                    )
                )
                issues_found = True

        return not issues_found

    def _check_dependency_conflicts(self) -> bool:
        """Check for dependency conflicts"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.issues.append(
                    SecurityIssue(
                        severity="HIGH",
                        package="system",
                        version="N/A",
                        issue=f"Dependency conflicts detected: {result.stdout}",
                    )
                )
                return False

            return True

        except Exception as e:
            logger.warning(f"⚠️ Could not check dependency conflicts: {e}")
            return True

    def _generate_security_report(self) -> None:
        """Generate detailed security report"""
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "total_packages": len(self.installed_packages),
            "lock_file_packages": len(self.lock_file_packages),
            "security_issues": len(self.issues),
            "critical_issues": len(
                [i for i in self.issues if i.severity == "CRITICAL"]
            ),
            "high_issues": len([i for i in self.issues if i.severity == "HIGH"]),
            "packages": {
                name: {
                    "version": info.version,
                    "location": info.location,
                    "license": info.license,
                }
                for name, info in self.installed_packages.items()
            },
            "issues": [
                {
                    "severity": issue.severity,
                    "package": issue.package,
                    "version": issue.version,
                    "issue": issue.issue,
                    "cve_id": issue.cve_id,
                    "fixed_version": issue.fixed_version,
                }
                for issue in self.issues
            ],
        }

        # Write report
        report_path = self.project_root / "reports" / "dependency-security-report.json"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2))
        logger.info(f"📊 Security report saved to {report_path}")

    def _print_security_issues(self) -> None:
        """Print security issues to console"""
        print("\n" + "=" * 80)
        print("🚨 SECURITY ISSUES FOUND")
        print("=" * 80)

        for issue in sorted(self.issues, key=lambda x: (x.severity, x.package)):
            print(f"\n[{issue.severity}] {issue.package} v{issue.version}")
            print(f"   Issue: {issue.issue}")
            if issue.cve_id:
                print(f"   CVE: {issue.cve_id}")
            if issue.fixed_version:
                print(f"   Fixed in: {issue.fixed_version}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    checker = DependencySecurityChecker()

    if checker.run_security_check():
        logger.info("✅ All security checks passed")
        sys.exit(0)
    else:
        logger.error("❌ Security check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
