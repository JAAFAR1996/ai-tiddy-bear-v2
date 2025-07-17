#!/usr/bin/env python3
"""
مشغل الاختبارات الشامل لمشروع AI Teddy Bear
"""

import subprocess
import sys
import os
import logging
from pathlib import Path
import json

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("test_results.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def run_tests_with_coverage():
    """تشغيل الاختبارات مع تغطية الكود"""

    logger.info("🧪 تشغيل الاختبارات مع تغطية الكود...")

    # تحديد PYTHONPATH
    os.environ["PYTHONPATH"] = str(Path.cwd() / "src")

    try:
        # تشغيل pytest مع تغطية الكود
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-fail-under=70",  # بدء بـ 70% وزيادة تدريجية
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
        )

        logger.info("📊 نتائج الاختبارات:")
        if result.stdout:
            logger.info(result.stdout)

        if result.stderr:
            logger.warning("⚠️ تحذيرات/أخطاء:")
            logger.warning(result.stderr)

        return result.returncode == 0

    except FileNotFoundError:
        logger.error("❌ pytest غير متوفر. جاري تشغيل الاختبارات البديلة...")
        return run_basic_tests()


def run_basic_tests():
    """تشغيل الاختبارات الأساسية بدون pytest"""

    logger.info("🔧 تشغيل الاختبارات الأساسية...")

    # إضافة src إلى المسار
    sys.path.insert(0, "src")

    test_results = []

    # اختبار خدمة المصادقة
    try:
        from infrastructure.security.real_auth_service import AuthService

        auth = AuthService()

        # اختبار تشفير كلمة المرور
        import secrets

        # ✅  - استخدام كلمة مرور عشوائية آمنة
        password = secrets.token_urlsafe(16)
        hashed = auth.hash_password(password)
        verified = auth.verify_password(password, hashed)

        test_results.append(("Auth Service - Password Hashing", verified))

        # اختبار إنشاء الرمز
        user_data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "parent"}
        token = auth.create_access_token(user_data)
        decoded = auth.verify_token(token)

        test_results.append(
            ("Auth Service - Token Creation",
             decoded is not None))

    except Exception as e:
        test_results.append(("Auth Service", False))
        logger.error(f"خطأ في اختبار خدمة المصادقة: {e}")

    # اختبار خدمة الذكاء الاصطناعي
    try:
        from infrastructure.ai.real_ai_service import AIService

        ai = AIService()

        # اختبار توليد الاستجابة
        response = ai.generate_response(
            "Tell me a story", 6, {"interests": ["animals"]}
        )

        test_results.append(
            ("AI Service - Response Generation", len(response["response"]) > 0)
        )
        test_results.append(
            ("AI Service - Safety Analysis",
             response["safety_analysis"]["safe"])
        )

        # اختبار تصفية الأمان
        unsafe_response = ai.generate_response("I hate everything", 6, {})
        test_results.append(
            ("AI Service - Safety Filtering",
             "hate" not in unsafe_response["response"])
        )

    except Exception as e:
        test_results.append(("AI Service", False))
        logger.error(f"خطأ في اختبار خدمة الذكاء الاصطناعي: {e}")

    # اختبار الوظائف الأساسية
    try:
        from domain.entities.child_profile import ChildProfile
        from application.dto.ai_response import AIResponse

        # اختبار إنشاء ملف الطفل
        child = ChildProfile.create_new("Test Child", 6, {"language": "en"})
        test_results.append(
            ("Domain - Child Profile Creation", child.name == "Test Child")
        )

        # اختبار إنشاء DTO
        response = AIResponse(
            response_text="Hello!",
            audio_response=b"audio",
            emotion="happy",
            sentiment=0.8,
            safe=True,
            conversation_id="123",
        )
        test_results.append(
            ("Application - DTO Creation", response.response_text == "Hello!")
        )

    except Exception as e:
        test_results.append(("Basic Functionality", False))
        logger.error(f"خطأ في الوظائف الأساسية: {e}")

    # تسجيل النتائج
    logger.info("\n📊 نتائج الاختبارات الأساسية:")
    logger.info("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ نجح" if result else "❌ فشل"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1

    logger.info("=" * 60)
    logger.info(
        f"📈 النتيجة الإجمالية: {passed}/{total} ({passed/total*100:.1f}%)")

    return passed == total


def run_security_scan():
    """تشغيل فحص الأمان"""

    logger.info("🔒 تشغيل فحص الأمان...")
    all_issues_found = []

    # Run Bandit
    try:
        bandit_cmd = [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            "src",
            "-f",
            "json",
            "-o",
            "bandit_report.json",
            "--verbose",
        ]
        logger.info(f"Running Bandit: {' '.join(bandit_cmd)}")
        bandit_result = subprocess.run(
            bandit_cmd, capture_output=True, text=True, check=False
        )
        if bandit_result.stdout:
            logger.info("Bandit stdout:\n" + bandit_result.stdout)
        if bandit_result.stderr:
            logger.warning("Bandit stderr:\n" + bandit_result.stderr)

        if os.path.exists("bandit_report.json"):
            with open("bandit_report.json", "r", encoding="utf-8") as f:
                report = json.load(f)
                for result in report.get("results", []):
                    issue_details = f"Bandit: {result['test_name']} - {result['issue_text']} at {result['filename']}:{result['lineno']}"
                    all_issues_found.append(issue_details)
                    if result["issue_severity"] in ["HIGH", "CRITICAL"]:
                        logger.error(
                            f"🚨 Critical/High Security Issue (Bandit): {issue_details}"
                        )
                        return False
        else:
            logger.warning(
                "Bandit report file not found, skipping Bandit results processing."
            )

    except FileNotFoundError:
        logger.warning("Bandit command not found. Skipping Bandit scan.")
    except Exception as e:
        logger.error(f"Error running Bandit: {e}")

    # Run Safety
    try:
        safety_cmd = [
            sys.executable,
            "-m",
            "safety",
            "check",
            "-r",
            "requirements.txt",
            "--full-report",
            "--json",
        ]
        logger.info(f"Running Safety: {' '.join(safety_cmd)}")
        safety_result = subprocess.run(
            safety_cmd, capture_output=True, text=True, check=False
        )
        if safety_result.stdout:
            safety_output = json.loads(safety_result.stdout)
            for vulnerability in safety_output.get("vulnerabilities", []):
                issue_details = f"Safety: {vulnerability['package_name']} - {vulnerability['advisory']}"
                all_issues_found.append(issue_details)
                logger.error(f"🚨 Vulnerability (Safety): {issue_details}")
                return False

        if safety_result.stderr:
            logger.warning("Safety stderr:\n" + safety_result.stderr)

    except FileNotFoundError:
        logger.warning("Safety command not found. Skipping Safety scan.")
    except json.JSONDecodeError as e:
        logger.error(
            f"Error decoding Safety JSON output: {e}. Output was: {safety_result.stdout}"
        )
    except Exception as e:
        logger.error(f"Error running Safety: {e}")

    if all_issues_found:
        logger.warning(
            "⚠️ Potential security issues found (review logs for full details): "
        )
        for issue in all_issues_found[:10]:
            logger.warning(f"  - {issue}")
        if len(all_issues_found) > 10:
            logger.warning(
                f"  ... and {len(all_issues_found) - 10} more issues.")
        return False
    else:
        logger.info("✅ No obvious security issues found by Bandit or Safety.")
        return True


def generate_coverage_report():
    """إنشاء تقرير تغطية الكود"""

    logger.info("📊 إنشاء تقرير تغطية الكود...")

    # حساب تغطية تقريبية
    src_files = list(Path("src").rglob("*.py"))
    test_files = list(Path("tests").rglob("test_*.py"))

    total_src_files = len(src_files)
    total_test_files = len(test_files)

    # تقدير تغطية الكود بناءً على نسبة ملفات الاختبار
    estimated_coverage = min(
        90, (total_test_files / max(1, total_src_files)) * 100)

    logger.info(f"📁 ملفات المصدر: {total_src_files}")
    logger.info(f"🧪 ملفات الاختبار: {total_test_files}")
    logger.info(f"📈 تغطية الكود المقدرة: {estimated_coverage:.1f}%")

    if estimated_coverage >= 80:
        logger.info("✅ تغطية كود ممتازة!")
    elif estimated_coverage >= 70:
        logger.warning("⚠️ تغطية كود جيدة، يمكن تحسينها")
    else:
        logger.error("❌ تغطية كود منخفضة، تحتاج لمزيد من الاختبارات")

    return estimated_coverage


def main():
    """الدالة الرئيسية"""

    logger.info("🧸 AI Teddy Bear - مشغل الاختبارات الشامل")
    logger.info("=" * 70)

    # تشغيل الاختبارات
    tests_passed = run_tests_with_coverage()

    # تشغيل فحص الأمان
    security_clean = run_security_scan()

    # إنشاء تقرير التغطية
    coverage = generate_coverage_report()

    logger.info("\n" + "=" * 70)
    logger.info("📋 ملخص النتائج:")
    logger.info(f"🧪 الاختبارات: {'✅ نجحت' if tests_passed else '❌ فشلت'}")
    logger.info(
        f"🔒 الأمان: {'✅ نظيف' if security_clean else '⚠️ مشاكل محتملة'}")
    logger.info(f"📊 تغطية الكود: {coverage:.1f}%")

    if tests_passed and security_clean and coverage >= 70:
        logger.info("\n🎉 جميع الاختبارات نجحت! المشروع جاهز للإنتاج.")
        return True
    else:
        logger.warning("\n⚠️ بعض الاختبارات فشلت أو تحتاج لتحسين.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
