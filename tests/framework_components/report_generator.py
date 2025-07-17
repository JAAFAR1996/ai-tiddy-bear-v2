from datetime import datetime
from typing import Any, Dict, List

from .models import TestSuite


def _calculate_average_coverage(test_suites: Dict[str, TestSuite]) -> float:
    """Calculate the average test coverage across all suites."""
    total_coverage = 0.0
    for suite in test_suites.values():
        if suite.test_results:
            avg_coverage = sum(
                r.coverage_percent or 0 for r in suite.test_results
            ) / len(suite.test_results)
            total_coverage += avg_coverage
    return total_coverage


def _calculate_average_security_score(
    test_suites: Dict[str, TestSuite],
) -> float:
    """Calculate the average security score across all suites."""
    total_security_score = 0.0
    for suite in test_suites.values():
        security_results = [
            r for r in suite.test_results if r.security_score is not None
        ]
        if security_results:
            avg_security = sum(
                r.security_score for r in security_results
            ) / len(security_results)
            total_security_score += avg_security
    return total_security_score


def _calculate_average_child_safety_score(
    test_suites: Dict[str, TestSuite],
) -> float:
    """Calculate the average child safety score across all suites."""
    total_child_safety_score = 0.0
    for suite in test_suites.values():
        safety_results = [
            r for r in suite.test_results if r.child_safety_score is not None
        ]
        if safety_results:
            avg_safety = sum(
                r.child_safety_score for r in safety_results
            ) / len(safety_results)
            total_child_safety_score += avg_safety
    return total_child_safety_score


def _check_quality_gates(framework) -> Dict[str, bool]:
    """فحص بوابات الجودة"""
    gates = {
        "coverage_95_percent": framework.overall_results["coverage_percent"]
        >= framework.config.min_coverage,
        "zero_critical_vulnerabilities": framework.overall_results[
            "security_score"
        ]
        >= 0.95,
        "performance_benchmarks_pass": framework.overall_results[
            "performance_score"
        ]
        >= 90.0,
        "all_tests_pass": framework.overall_results["failed_tests"] == 0,
        "child_safety_compliance": framework.overall_results[
            "child_safety_score"
        ]
        >= 0.95,
    }

    return gates


def _generate_recommendations(framework) -> List[str]:
    """توليد التوصيات"""
    recommendations = []

    if (
        framework.overall_results["coverage_percent"]
        < framework.config.min_coverage
    ):
        recommendations.append("📈 زيادة تغطية الاختبارات لتصل إلى 95%+")

    if framework.overall_results["security_score"] < 0.95:
        recommendations.append("🔒 تحسين إجراءات الأمان")

    if framework.overall_results["child_safety_score"] < 0.95:
        recommendations.append("👶 تعزيز حماية الأطفال")

    recommendations.extend(
        [
            "🚀 إعداد CI/CD pipeline مع بوابات الجودة",
            "📊 مراقبة الأداء المستمر",
            "🔍 فحص الأمان الدوري",
            "📝 تحديث التوثيق",
        ]
    )

    return recommendations


def generate_comprehensive_report(
    framework, execution_time: float
) -> Dict[str, Any]:
    """توليد تقرير شامل"""
    return {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 3: Testing & Quality Assurance",
        "execution_time_seconds": execution_time,
        "overall_results": framework.overall_results,
        "test_suites": {
            name: {
                "name": suite.name,
                "description": suite.description,
                "total_tests": suite.total_tests,
                "passed_tests": suite.passed_tests,
                "failed_tests": suite.failed_tests,
                "coverage_percent": (
                    sum(r.coverage_percent or 0 for r in suite.test_results)
                    / len(suite.test_results)
                    if suite.test_results
                    else 0.0
                ),
            }
            for name, suite in framework.test_suites.items()
        },
        "quality_gates_status": _check_quality_gates(framework),
        "recommendations": _generate_recommendations(framework),
    }
