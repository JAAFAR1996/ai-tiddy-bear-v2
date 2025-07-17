from typing import Any, Dict, List

from .models import ContractTestSuite


def _calculate_overall_results(
    test_suites: Dict[str, ContractTestSuite],
) -> Dict[str, Any]:
    """حساب النتائج الإجمالية"""
    total_tests = sum(suite.total_tests for suite in test_suites.values())
    passed_tests = sum(suite.passed_tests for suite in test_suites.values())
    failed_tests = sum(suite.failed_tests for suite in test_suites.values())
    error_tests = sum(suite.error_tests for suite in test_suites.values())

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "error_tests": error_tests,
        "success_rate": success_rate,
        "services_tested": len(test_suites),
    }


def _generate_recommendations(framework) -> List[str]:
    """توليد توصيات لتحسين العقود"""
    recommendations = []

    overall_results = _calculate_overall_results(framework.test_suites)

    if overall_results["success_rate"] < 90:
        recommendations.append("🔴 معدل نجاح العقود منخفض - راجع تعريفات APIs")

    if overall_results["error_tests"] > 0:
        recommendations.append("🟡 بعض الاختبارات فشلت - تحقق من توفر الخدمات")

    for service_name, suite in framework.test_suites.items():
        if suite.failed_tests > 0:
            recommendations.append(
                f"🔴 {service_name}: {suite.failed_tests} اختبارات فشلت"
            )

    if not recommendations:
        recommendations.append("✅ جميع العقود تعمل بشكل صحيح")

    return recommendations
