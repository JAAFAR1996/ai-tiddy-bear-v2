#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Teddy Bear
Enterprise-grade testing with detailed reporting and 100% improvement focus
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

# Setup logging
# Configure root logger directly to ensure all messages are handled consistently.
# For StreamHandler, let the default system encoding be used or set PYTHONIOENCODING globally.
# For FileHandler, explicitly use UTF-8.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout) # Removed encoding, relying on PYTHONIOENCODING or system default
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Enterprise-grade test runner with detailed reporting"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            "execution_start": datetime.now().isoformat(),
            "execution_end": None,
            "total_duration": None,
            "overall_status": "PENDING",
            "test_categories": {},
            "coverage_report": {},
            "security_analysis": {},
            "quality_metrics": {},
            "recommendations": []
        }
        
    def setup_environment(self):
        """Setup test environment"""
        logger.info("🔧 Setting up test environment...")
        
        # Add project root to Python path
        sys.path.insert(0, str(self.project_root / "src"))
        
        # Set environment variables for testing
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["USE_MOCK_SERVICES"] = "true"
        os.environ["LOG_LEVEL"] = "INFO"
        os.environ["DATABASE_URL"] = "sqlite:///test_ai_teddy.db"
        os.environ["PYTHONIOENCODING"] = "UTF-8" # Ensure consistent encoding for subprocesses
        
        # Generate test security keys
        import secrets
        os.environ["SECRET_KEY"] = secrets.token_urlsafe(32)
        os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(32)
        os.environ["ENCRYPTION_KEY"] = secrets.token_urlsafe(32)
        
        logger.info("✅ Test environment setup complete")
    
    def install_dependencies(self):
        """Install all required dependencies"""
        logger.info("📦 Installing dependencies...")
        
        try:
            # Install production dependencies with upgrade
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"
            ], capture_output=True, timeout=300, env=os.environ.copy())

            if result.returncode != 0:
                logger.warning(f"Some production dependencies failed to install or upgrade: {result.stderr.decode('utf-8', errors='ignore')}")

            # Install development dependencies with upgrade
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements-dev.txt"
            ], capture_output=True, timeout=300, env=os.environ.copy())

            if result.returncode != 0:
                logger.warning(f"Some dev dependencies failed to install: {result.stderr.decode('utf-8', errors='ignore')}")

            # Install essential testing packages
            essential_packages = [
                "pytest>=8.0.0",
                "pytest-asyncio>=0.23.0", 
                "pytest-cov>=5.0.0",
                "pytest-mock>=3.11.0"
            ]

            for package in essential_packages:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], capture_output=True, timeout=60, env=os.environ.copy())
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout installing {package}")

            logger.info("✅ Dependencies installation complete")

        except Exception as e:
            logger.error(f"❌ Dependency installation failed: {e}")

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage"""
        logger.info("🧪 Running unit tests...")

        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/unit/",
                "-v",
                "--tb=short",
                "--cov=src",
                "--cov-report=json:coverage_unit.json",
                "--cov-report=term-missing",
                "--json-report",
                "--json-report-file=unit_test_results.json"
            ]

            # Pass encoding to subprocess for consistent output decoding
            result = subprocess.run(cmd, capture_output=True, timeout=300, env=os.environ.copy())

            # Parse results
            test_report = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": (result.stdout or b"").decode('utf-8', errors='ignore'),
                "stderr": (result.stderr or b"").decode('utf-8', errors='ignore'),
                "tests_found": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "coverage_percentage": 0
            }

            # Extract test counts from output
            if "passed" in test_report["stdout"]:
                import re
                passed_match = re.search(r'(\d+) passed', test_report["stdout"])
                if passed_match:
                    test_report["tests_passed"] = int(passed_match.group(1))

                failed_match = re.search(r'(\d+) failed', test_report["stdout"])
                if failed_match:
                    test_report["tests_failed"] = int(failed_match.group(1))

            test_report["tests_found"] = test_report["tests_passed"] + test_report["tests_failed"]

            # Extract coverage info
            try:
                if os.path.exists("coverage_unit.json"):
                    with open("coverage_unit.json", "r", encoding='utf-8') as f: # Added encoding
                        coverage_data = json.load(f)
                        test_report["coverage_percentage"] = coverage_data.get("totals", {}).get("percent_covered", 0)
            except (IOError, json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Could not read coverage data: {e}")
                pass

            logger.info(f"Unit tests: {test_report['status']} - {test_report['tests_passed']} passed, {test_report['tests_failed']} failed")
            return test_report

        except subprocess.TimeoutExpired:
            logger.error("❌ Unit tests timed out")
            return {"status": "TIMEOUT", "error": "Tests timed out after 5 minutes"}
        except Exception as e:
            logger.error(f"❌ Unit test execution failed: {e}")
            return {"status": "ERROR", "error": str(e)}

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("🔗 Running integration tests...")

        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/integration/",
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=integration_test_results.json"
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=300, env=os.environ.copy())

            test_report = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": (result.stdout or b"").decode('utf-8', errors='ignore'),
                "stderr": (result.stderr or b"").decode('utf-8', errors='ignore'),
                "tests_found": 0,
                "tests_passed": 0,
                "tests_failed": 0
            }

            # Extract test counts
            if "passed" in test_report["stdout"]:
                import re
                passed_match = re.search(r'(\d+) passed', test_report["stdout"])
                if passed_match:
                    test_report["tests_passed"] = int(passed_match.group(1))

                failed_match = re.search(r'(\d+) failed', test_report["stdout"])
                if failed_match:
                    test_report["tests_failed"] = int(failed_match.group(1))

            test_report["tests_found"] = test_report["tests_passed"] + test_report["tests_failed"]

            logger.info(f"Integration tests: {test_report['status']} - {test_report['tests_passed']} passed, {test_report['tests_failed']} failed")
            return test_report

        except subprocess.TimeoutExpired:
            logger.error("❌ Integration tests timed out")
            return {"status": "TIMEOUT", "error": "Tests timed out after 5 minutes"}
        except Exception as e:
            logger.error(f"❌ Integration test execution failed: {e}")
            return {"status": "ERROR", "error": str(e)}

    def run_security_tests(self) -> Dict[str, Any]:
        """Run comprehensive security tests"""
        logger.info("🔒 Running security tests...")

        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/security/",
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=security_test_results.json"
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=300, env=os.environ.copy())

            test_report = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "stdout": (result.stdout or b"").decode('utf-8', errors='ignore'),
                "stderr": (result.stderr or b"").decode('utf-8', errors='ignore'),
                "tests_found": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "security_issues_found": 0
            }

            # Extract test counts
            if "passed" in test_report["stdout"]:
                import re
                passed_match = re.search(r'(\d+) passed', test_report["stdout"])
                if passed_match:
                    test_report["tests_passed"] = int(passed_match.group(1))

                failed_match = re.search(r'(\d+) failed', test_report["stdout"])
                if failed_match:
                    test_report["tests_failed"] = int(failed_match.group(1))

            test_report["tests_found"] = test_report["tests_passed"] + test_report["tests_failed"]
            test_report["security_issues_found"] = test_report["tests_failed"]

            logger.info(f"Security tests: {test_report['status']} - {test_report['security_issues_found']} issues found")
            return test_report

        except subprocess.TimeoutExpired:
            logger.error("❌ Security tests timed out")
            return {"status": "TIMEOUT", "error": "Tests timed out after 5 minutes"}
        except Exception as e:
            logger.error(f"❌ Security test execution failed: {e}")
            return {"status": "ERROR", "error": str(e)}

    def run_code_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks"""
        logger.info("🏗️ Running code quality checks...")

        quality_results = {
            "linting": {"status": "PENDING"},
            "type_checking": {"status": "PENDING"},
            "security_scanning": {"status": "PENDING"},
            "overall_score": 0
        }

        # Run Black formatting check
        try:
            result = subprocess.run([
                sys.executable, "-m", "black", "--check", "src/", "--diff"
            ], capture_output=True, timeout=60, env=os.environ.copy())

            quality_results["formatting"] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "issues": (result.stdout or b"").decode('utf-8', errors='ignore').count("--- ") if result.returncode != 0 else 0
            }
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            quality_results["formatting"] = {"status": "SKIPPED", "error": f"Black not available: {e}"}

        # Run flake8 linting
        try:
            result = subprocess.run([
                sys.executable, "-m", "flake8", "src/", "--count", "--statistics"
            ], capture_output=True, timeout=60, env=os.environ.copy())

            quality_results["linting"] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED", 
                "issues": len((result.stdout or b"").decode('utf-8', errors='ignore').split('\n')) if result.returncode != 0 else 0,
                "details": (result.stdout or b"").decode('utf-8', errors='ignore')
            }
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            quality_results["linting"] = {"status": "SKIPPED", "error": f"Flake8 not available: {e}"}

        # Run mypy type checking
        try:
            result = subprocess.run([
                sys.executable, "-m", "mypy", "src/", "--ignore-missing-imports"
            ], capture_output=True, timeout=120, env=os.environ.copy())

            quality_results["type_checking"] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "issues": (result.stdout or b"").decode('utf-8', errors='ignore').count("error:") if result.returncode != 0 else 0,
                "details": (result.stdout or b"").decode('utf-8', errors='ignore')
            }
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            quality_results["type_checking"] = {"status": "SKIPPED", "error": f"Mypy not available: {e}"}

        # Run bandit security scanning
        try:
            result = subprocess.run([
                sys.executable, "-m", "bandit", "-r", "src/", "-f", "json"
            ], capture_output=True, timeout=60, env=os.environ.copy())

            if result.stdout:
                # Attempt to decode, then load JSON. Use default empty dict if decoding fails.
                decoded_stdout = (result.stdout or b"").decode('utf-8', errors='ignore')
                try:
                    bandit_results = json.loads(decoded_stdout or "{}") # Ensure it's not None or empty string before loading
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode Bandit JSON: {decoded_stdout}")
                    bandit_results = {}

                quality_results["security_scanning"] = {
                    "status": "PASSED" if len(bandit_results.get("results", [])) == 0 else "FAILED",
                    "issues": len(bandit_results.get("results", [])),
                    "high_severity": len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "HIGH"]),
                    "medium_severity": len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "MEDIUM"])
                }
            else:
                quality_results["security_scanning"] = {"status": "PASSED", "issues": 0, "details": (result.stderr or b"").decode('utf-8', errors='ignore') or "No output from Bandit"}
        except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
            quality_results["security_scanning"] = {"status": "SKIPPED", "error": f"Bandit not available: {e}"}
        except Exception as e: # Catch any other unexpected errors during Bandit processing
            logger.error(f"An unexpected error occurred during Bandit scan: {e}")
            quality_results["security_scanning"] = {"status": "ERROR", "error": str(e)}

        # Calculate overall quality score
        passed_checks = sum(1 for check in quality_results.values() 
                          if isinstance(check, dict) and check.get("status") == "PASSED")
        total_checks = len([check for check in quality_results.values() 
                          if isinstance(check, dict) and check.get("status") != "SKIPPED"])

        quality_results["overall_score"] = (passed_checks / max(total_checks, 1)) * 100

        logger.info(f"Code quality: {quality_results['overall_score']:.1f}% score")
        return quality_results

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        logger.info("⚡ Running performance tests...")

        try:
            # Simple performance test
            start_time = time.time()

            # Test imports and basic functionality
            # Ensure `src` is in `sys.path` for this sub-process as well
            current_env = os.environ.copy()
            if str(self.project_root / "src") not in current_env.get("PYTHONPATH", ""):
                current_env["PYTHONPATH"] = str(self.project_root / "src") + os.pathsep + current_env.get("PYTHONPATH", "")

            # Running a subprocess to isolate the mock service import and execution
            # This avoids potential conflicts with the main test runner's environment
            performance_test_script = Path(__file__).parent / "_run_single_performance_test.py"
            with open(performance_test_script, "w", encoding="utf-8") as f:
                f.write("""
import asyncio
import os
import sys
from pathlib import Path
# The PYTHONPATH is set by the parent process, no need for complex path manipulation here

from src.infrastructure.mocks.comprehensive_mock_services import MockServiceManager

async def main():
    mock_manager = MockServiceManager()
    health = await mock_manager.health_check()
    print(health)

if __name__ == "__main__":
    asyncio.run(main())
""")

            # Execute the temporary script as a separate process
            result = subprocess.run(
                [sys.executable, str(performance_test_script)],
                capture_output=True, 
                timeout=30, # Shorter timeout for individual script
                env=current_env
            )
            
            # Clean up temporary script
            os.remove(performance_test_script)

            if result.returncode != 0:
                raise Exception(f"Performance test script failed: {result.stderr.decode('utf-8', errors='ignore')}")

            # Parse health result from stdout
            health_output = (result.stdout or b"").decode('utf-8', errors='ignore').strip()
            try:
                health_result = json.loads(health_output)
            except json.JSONDecodeError:
                health_result = {"overall_status": "error", "details": "Failed to parse health check output"}
                logger.warning(f"Could not parse performance test health result: {health_output}")
            
            end_time = time.time()
            
            return {
                "status": "PASSED" if health_result.get("overall_status") == "healthy" else "FAILED",
                "execution_time": round(end_time - start_time, 3),
                "service_health": health_result.get("overall_status", "unknown"),
                "memory_usage": "Not measured",
                "recommendations": [
                    "Consider implementing proper performance monitoring",
                    "Add load testing for production readiness"
                ]
            }
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Performance test script timed out")
            return {"status": "TIMEOUT", "error": "Performance test script timed out after 30 seconds"}
        except Exception as e:
            logger.error(f"❌ Performance tests failed: {e}", exc_info=True) # Log full traceback
            return {"status": "ERROR", "error": str(e)}
    
    def generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations based on test results"""
        recommendations = []
        
        # Coverage recommendations
        coverage = self.test_results["test_categories"].get("unit", {}).get("coverage_percentage", 0)
        if coverage < 80:
            recommendations.append(f"📈 Increase test coverage from {coverage:.1f}% to at least 80%")
        
        # Security recommendations
        security_issues = self.test_results["test_categories"].get("security", {}).get("security_issues_found", 0)
        if security_issues > 0:
            recommendations.append(f"🔒 Fix {security_issues} security issues identified in tests")
        
        # Quality recommendations
        quality_score = self.test_results["quality_metrics"].get("overall_score", 0)
        if quality_score < 90:
            recommendations.append(f"🏗️ Improve code quality from {quality_score:.1f}% to at least 90%")
        
        # Performance recommendations
        if "performance" in self.test_results["test_categories"]:
            recommendations.append("⚡ Implement comprehensive performance monitoring")
        
        # General recommendations for 100% improvement
        recommendations.extend([
            "🧪 Add more comprehensive integration tests",
            "🔍 Implement automated security scanning in CI/CD",
            "📊 Add metrics and monitoring for production deployment",
            "🚀 Optimize application startup time and memory usage",
            "📝 Enhance API documentation with OpenAPI 3.0",
            "🔄 Implement automated dependency updates",
            "🌐 Add multi-language support for international users",
            "♿ Ensure full accessibility compliance",
            "🎯 Add A/B testing framework for feature validation"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        logger.info("📊 Generating final test report...")
        
        # Calculate overall status
        test_categories = self.test_results["test_categories"]
        failed_categories = [name for name, results in test_categories.items() 
                           if results.get("status") == "FAILED"]
        
        if not failed_categories:
            self.test_results["overall_status"] = "PASSED"
        elif len(failed_categories) <= 2:
            self.test_results["overall_status"] = "PARTIAL"
        else:
            self.test_results["overall_status"] = "FAILED"
        
        # Add recommendations
        self.test_results["recommendations"] = self.generate_recommendations()
        
        # Finalize timing
        self.test_results["execution_end"] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(self.test_results["execution_start"])
        end_time = datetime.fromisoformat(self.test_results["execution_end"])
        self.test_results["total_duration"] = str(end_time - start_time)
        
        # Save detailed report
        with open("comprehensive_test_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("🧸 AI TEDDY BEAR - COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"📅 Execution Time: {self.test_results['total_duration']}")
        print(f"🎯 Overall Status: {self.test_results['overall_status']}")
        print()
        
        # Print category results
        for category, results in test_categories.items():
            status_emoji = "✅" if results.get("status") == "PASSED" else "❌"
            print(f"{status_emoji} {category.upper()}: {results.get('status', 'UNKNOWN')}")
            
            if "tests_passed" in results and "tests_failed" in results:
                print(f"   📊 Tests: {results['tests_passed']} passed, {results['tests_failed']} failed")
            
            if "coverage_percentage" in results:
                print(f"   📈 Coverage: {results['coverage_percentage']:.1f}%")
            
            if "security_issues_found" in results:
                print(f"   🔒 Security Issues: {results['security_issues_found']}")
        
        # Print quality metrics
        if "quality_metrics" in self.test_results:
            print(f"\n🏗️ Code Quality Score: {self.test_results['quality_metrics'].get('overall_score', 0):.1f}%")
        
        # Print top recommendations
        print("\n🎯 TOP RECOMMENDATIONS FOR 100% IMPROVEMENT:")
        for i, recommendation in enumerate(self.test_results["recommendations"][:5], 1):
            print(f"   {i}. {recommendation}")
        
        print("\n📄 Full report saved to: comprehensive_test_report.json")
        print("="*80)
    
    def run_all_tests(self):
        """Run all test categories"""
        logger.info("🚀 Starting comprehensive test execution...")
        
        # Setup
        self.setup_environment()
        # Commenting out dependency installation to avoid build issues. Please ensure dependencies are installed manually.
        # self.install_dependencies()
        
        # Run test categories
        test_categories = [
            ("unit", self.run_unit_tests),
            ("integration", self.run_integration_tests),
            ("security", self.run_security_tests),
            ("performance", self.run_performance_tests)
        ]
        
        for category_name, test_function in test_categories:
            logger.info(f"🔄 Running {category_name} tests...")
            try:
                results = test_function()
                self.test_results["test_categories"][category_name] = results
                logger.info(f"✅ {category_name} tests completed: {results.get('status', 'UNKNOWN')}")
            except Exception as e:
                logger.error(f"❌ {category_name} tests failed: {e}")
                self.test_results["test_categories"][category_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Run quality checks
        try:
            quality_results = self.run_code_quality_checks()
            self.test_results["quality_metrics"] = quality_results
        except Exception as e:
            logger.error(f"❌ Quality checks failed: {e}")
            self.test_results["quality_metrics"] = {"error": str(e)}
        
        # Generate final report
        self.generate_final_report()


if __name__ == "__main__":
    print("🧸 AI Teddy Bear - Comprehensive Test Runner")
    print("=============================================")
    print("Running enterprise-grade tests with 100% improvement focus...")
    print()
    
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()