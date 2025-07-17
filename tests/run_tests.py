#!/usr/bin/env python3
"""
Test Runner for AI Teddy Bear
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# Test suite configurations
TEST_SUITES = {
    "unit": {
        "name": "Unit Tests",
        "markers": "unit",
        "coverage": True,
        "min_coverage": 80,
    },
    "integration": {
        "name": "Integration Tests",
        "markers": "integration",
        "coverage": True,
        "min_coverage": 70,
    },
    "e2e": {"name": "End-to-End Tests", "markers": "e2e", "coverage": False},
    "security": {
        "name": "Security Tests",
        "markers": "security",
        "coverage": True,
        "min_coverage": 90,
    },
    "child_safety": {
        "name": "Child Safety Tests",
        "markers": "child_safety",
        "coverage": True,
        "min_coverage": 95,
    },
    "performance": {
        "name": "Performance Tests",
        "markers": "slow",
        "coverage": False,
    },
    "all": {
        "name": "All Tests",
        "markers": None,
        "coverage": True,
        "min_coverage": 80,
    },
}


class TestRunner:
    """Test runner with advanced features"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"

    def run_suite(
        self,
        suite_name: str,
        verbose: bool = False,
        quiet: bool = False,
        failfast: bool = False,
        parallel: Optional[int] = None,
    ) -> int:
        """Run a specific test suite"""
        if suite_name not in TEST_SUITES:
            print(f"Unknown test suite: {suite_name}")
            print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
            return 1

        suite = TEST_SUITES[suite_name]
        print(f"\n{'='*60}")
        print(f"Running {suite['name']}")
        print(f"{'='*60}\n")

        # Build pytest command
        cmd = ["python", "-m", "pytest"]

        # Add markers
        if suite["markers"]:
            cmd.extend(["-m", suite["markers"]])

        # Add verbosity
        if verbose:
            cmd.append("-vv")
        elif quiet:
            cmd.append("-q")
        else:
            cmd.append("-v")

        # Add failfast
        if failfast:
            cmd.append("-x")

        # Add parallel execution
        if parallel:
            cmd.extend(["-n", str(parallel)])

        # Add coverage if enabled
        if suite.get("coverage"):
            cmd.extend(
                [
                    "--cov=src",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                    f"--cov-fail-under={suite.get('min_coverage', 0)}",
                ]
            )

        # Add test directory
        cmd.append(str(self.tests_dir))

        # Run tests
        result = subprocess.run(cmd, cwd=self.project_root)

        return result.returncode

    def run_specific_tests(
        self,
        test_paths: List[str],
        verbose: bool = False,
        coverage: bool = True,
    ) -> int:
        """Run specific test files or patterns"""
        cmd = ["python", "-m", "pytest"]

        if verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")

        if coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])

        # Add test paths
        cmd.extend(test_paths)

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode

    def run_security_scan(self) -> int:
        """Run security-focused tests and checks"""
        print("\n🔒 Running Security Scan...")

        # Run security tests
        security_result = self.run_suite("security", quiet=True)

        # Run bandit security linter
        print("\n🔍 Running Bandit security linter...")
        bandit_result = subprocess.run(
            ["python", "-m", "bandit", "-r", "src", "-ll"],
            cwd=self.project_root,
        ).returncode

        # Check for hardcoded secrets
        print("\n🔑 Checking for hardcoded secrets...")
        secrets_result = self._check_secrets()

        return max(security_result, bandit_result, secrets_result)

    def run_child_safety_validation(self) -> int:
        """Run child safety validation tests"""
        print("\n👶 Running Child Safety Validation...")

        # Run child safety tests with strict coverage
        result = self.run_suite("child_safety", verbose=True)

        # Additional COPPA compliance checks
        print("\n📋 Checking COPPA compliance...")
        coppa_result = self._check_coppa_compliance()

        return max(result, coppa_result)

    def _check_secrets(self) -> int:
        """Check for hardcoded secrets in code"""
        patterns = [
            r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
            r"secret[_-]?key\s*=\s*[\"'][^\"']+[\"']",
            r"password\s*=\s*[\"'][^\"']+[\"']",
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API key pattern
        ]

        cmd = [
            "grep",
            "-r",
            "-E",
            "|".join(patterns),
            "src/",
            "--exclude-dir=__pycache__",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            print("⚠️  Potential secrets found:")
            print(result.stdout)
            return 1

        print("✅ No hardcoded secrets found")
        return 0

    def _check_coppa_compliance(self) -> int:
        """Check COPPA compliance requirements"""
        checks_passed = True

        # Check for age verification
        print("Checking age verification implementation...")
        age_check = subprocess.run(
            ["grep", "-r", "age.*verification", "src/", "--include=*.py"],
            capture_output=True,
        )
        if not age_check.stdout:
            print("⚠️  Age verification not found")
            checks_passed = False

        # Check for parental consent
        print("Checking parental consent implementation...")
        consent_check = subprocess.run(
            ["grep", "-r", "parental.*consent", "src/", "--include=*.py"],
            capture_output=True,
        )
        if not consent_check.stdout:
            print("⚠️  Parental consent not found")
            checks_passed = False

        # Check for data retention policy
        print("Checking data retention policy...")
        retention_check = subprocess.run(
            ["grep", "-r", "data.*retention", "src/", "--include=*.py"],
            capture_output=True,
        )
        if not retention_check.stdout:
            print("⚠️  Data retention policy not found")
            checks_passed = False

        if checks_passed:
            print("✅ COPPA compliance checks passed")
            return 0
        else:
            return 1

    def generate_coverage_report(self) -> int:
        """Generate detailed coverage report"""
        print("\n📊 Generating Coverage Report...")

        cmd = [
            "python",
            "-m",
            "pytest",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=xml",
            str(self.tests_dir),
        ]

        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode == 0:
            print(
                f"\n✅ Coverage report generated in: {self.project_root}/htmlcov/index.html"
            )

        return result.returncode


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Teddy Bear Test Runner")
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=list(TEST_SUITES.keys())
        + ["security-scan", "child-safety-validation", "coverage"],
        help="Test suite to run",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet output"
    )
    parser.add_argument(
        "-x", "--failfast", action="store_true", help="Stop on first failure"
    )
    parser.add_argument(
        "-n", "--parallel", type=int, help="Number of parallel workers"
    )
    parser.add_argument("-k", "--keyword", help="Run tests matching keyword")
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage"
    )

    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)

    # Handle special commands
    if args.suite == "security-scan":
        return runner.run_security_scan()
    elif args.suite == "child-safety-validation":
        return runner.run_child_safety_validation()
    elif args.suite == "coverage":
        return runner.generate_coverage_report()

    # Handle keyword filtering
    if args.keyword:
        cmd = ["python", "-m", "pytest", "-k", args.keyword]
        if args.verbose:
            cmd.append("-vv")
        if not args.no_coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
        cmd.append(str(runner.tests_dir))

        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode

    # Run regular test suite
    return runner.run_suite(
        args.suite,
        verbose=args.verbose,
        quiet=args.quiet,
        failfast=args.failfast,
        parallel=args.parallel,
    )


if __name__ == "__main__":
    sys.exit(main())
