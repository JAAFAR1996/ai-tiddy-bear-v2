#!/usr/bin/env python3
"""🧪 اختبار مبسط ومباشر لنظام الحماية المحسن من SQL Injection

هذا الاختبار المبسط يتحقق من النقاط الأساسية دون الاعتماد على imports معقدة.
"""

import sys
import traceback
from datetime import datetime

# Test results tracker
test_results = {"passed": 0, "failed": 0, "errors": []}


def log_test(test_name: str, success: bool, details: str = ""):
    """تسجيل نتائج الاختبار"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"    💡 {details}")

    if success:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(f"{test_name}: {details}")
    print()


def test_basic_sql_injection_protection():
    """🔒 اختبار الحماية الأساسية من SQL Injection"""
    try:
        # Import direct module to test
        sys.path.insert(0, "src")
        from infrastructure.security.validation.sql_injection_protection import (
            SQLInjectionPrevention,
        )

        # Create validator instance
        validator = SQLInjectionPrevention()

        # Test safe inputs
        safe_inputs = [
            "John Doe",
            "user@example.com",
            "12345",
            "Hello World",
            None,
            "",
            123,
            True,
        ]

        safe_count = 0
        for input_val in safe_inputs:
            try:
                result = validator.validate(input_val)
                if result:  # Should be True for safe inputs
                    safe_count += 1
            except Exception as e:
                print(f"    خطأ في اختبار إدخال آمن '{input_val}': {e}")

        # Test dangerous inputs
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
            "admin'/**/OR/**/1=1/**/--",
            "'; DELETE FROM children; --",
            "1' OR '1'='1",
            "'; EXEC xp_cmdshell('dir'); --",
        ]

        blocked_count = 0
        for dangerous_input in dangerous_inputs:
            try:
                result = validator.validate(dangerous_input)
                if not result:  # Should be False (blocked)
                    blocked_count += 1
            except Exception as e:
                print(f"    خطأ في اختبار إدخال خطير '{dangerous_input}': {e}")

        if (
            safe_count >= len(safe_inputs) * 0.8
            and blocked_count >= len(dangerous_inputs) * 0.8
        ):
            log_test(
                "الحماية الأساسية من SQL Injection",
                True,
                f"إدخالات آمنة مقبولة: {safe_count}/{len(safe_inputs)}, هجمات محظورة: {blocked_count}/{len(dangerous_inputs)}",
            )
        else:
            log_test(
                "الحماية الأساسية من SQL Injection",
                False,
                f"إدخالات آمنة مقبولة: {safe_count}/{len(safe_inputs)}, هجمات محظورة: {blocked_count}/{len(dangerous_inputs)}",
            )

    except Exception as e:
        log_test(
            "الحماية الأساسية من SQL Injection",
            False,
            f"خطأ في الاستيراد أو التشغيل: {str(e)}",
        )


def test_enhanced_patterns():
    """🎯 اختبار الأنماط المحسنة للحماية"""
    try:
        sys.path.insert(0, "src")
        from infrastructure.security.validation.sql_injection_protection import (
            SQLInjectionPrevention,
        )

        validator = SQLInjectionPrevention()

        # Test enhanced attack patterns
        advanced_attacks = [
            "0x756e696f6e2073656c656374",  # Hex encoded: union select
            "/**/UNION/**/SELECT/**/",  # Comment-based evasion
            "'; WAITFOR DELAY '00:00:05'; --",  # Time-based attack
            "' AND (SELECT COUNT(*) FROM users) > 0 --",  # Subquery injection
            "1'; CREATE TABLE hacked (id INT); --",  # DDL injection
            "'/**/OR/**/1=1/**/--",  # Comment obfuscation
        ]

        blocked_count = 0
        for attack in advanced_attacks:
            try:
                result = validator.validate(attack)
                if not result:
                    blocked_count += 1
            except Exception:
                pass  # Continue testing

        if blocked_count >= len(advanced_attacks) * 0.7:  # 70% detection rate
            log_test(
                "الأنماط المحسنة للحماية",
                True,
                f"تم اكتشاف {blocked_count}/{len(advanced_attacks)} نمط متقدم",
            )
        else:
            log_test(
                "الأنماط المحسنة للحماية",
                False,
                f"تم اكتشاف {blocked_count}/{len(advanced_attacks)} نمط متقدم فقط",
            )

    except Exception as e:
        log_test("الأنماط المحسنة للحماية", False, f"خطأ: {str(e)}")


def test_child_data_specific_protection():
    """👶 اختبار الحماية المخصصة لبيانات الأطفال"""
    try:
        sys.path.insert(0, "src")
        from infrastructure.security.validation.sql_injection_protection import (
            SQLInjectionPrevention,
        )

        validator = SQLInjectionPrevention()

        # Test child-targeting attacks
        child_attacks = [
            "child_name'; DROP TABLE children; --",
            "age=5 OR 1=1",
            "parent_email'; DELETE FROM safety_events; --",
            "birth_date UNION SELECT password FROM users",
            "student_id'; TRUNCATE TABLE conversations; --",
        ]

        blocked_count = 0
        for attack in child_attacks:
            try:
                result = validator.validate(attack)
                if not result:
                    blocked_count += 1
            except Exception:
                pass

        # Test that child table names are recognized
        child_tables = ["children", "conversations", "safety_events", "parent_consent"]
        table_protection_count = 0

        for table in child_tables:
            if (
                hasattr(validator, "allowed_child_tables")
                and table in validator.allowed_child_tables
            ):
                table_protection_count += 1

        if (
            blocked_count >= len(child_attacks) * 0.8
            and table_protection_count >= len(child_tables) * 0.8
        ):
            log_test(
                "الحماية المخصصة لبيانات الأطفال",
                True,
                f"هجمات محظورة: {blocked_count}/{len(child_attacks)}, جداول محمية: {table_protection_count}/{len(child_tables)}",
            )
        else:
            log_test(
                "الحماية المخصصة لبيانات الأطفال",
                False,
                f"هجمات محظورة: {blocked_count}/{len(child_attacks)}, جداول محمية: {table_protection_count}/{len(child_tables)}",
            )

    except Exception as e:
        log_test("الحماية المخصصة لبيانات الأطفال", False, f"خطأ: {str(e)}")


def test_backward_compatibility():
    """🔄 اختبار التوافق مع الكود الموجود"""
    try:
        sys.path.insert(0, "src")
        from infrastructure.security.validation.sql_injection_protection import (
            get_sql_injection_prevention,
        )

        # Test that the main function works
        validator = get_sql_injection_prevention()

        if validator and hasattr(validator, "validate"):
            # Test basic validation
            safe_result = validator.validate("Hello World")
            dangerous_result = validator.validate("'; DROP TABLE users; --")

            if safe_result == True and dangerous_result == False:
                log_test(
                    "التوافق مع الكود الموجود",
                    True,
                    "وظيفة get_sql_injection_prevention() تعمل بصورة صحيحة",
                )
            else:
                log_test(
                    "التوافق مع الكود الموجود",
                    False,
                    f"نتائج غير متوقعة: آمن={safe_result}, خطير={dangerous_result}",
                )
        else:
            log_test("التوافق مع الكود الموجود", False, "فشل في الحصول على مُدقق صالح")

    except Exception as e:
        log_test("التوافق مع الكود الموجود", False, f"خطأ: {str(e)}")


def test_enhanced_features():
    """⚡ اختبار الميزات المحسنة"""
    try:
        sys.path.insert(0, "src")
        from infrastructure.security.validation.sql_injection_protection import (
            SQLInjectionPrevention,
        )

        validator = SQLInjectionPrevention()

        # Test enhanced features
        features_found = 0

        # Check for enhanced patterns
        if (
            hasattr(validator, "critical_patterns")
            and len(validator.critical_patterns) >= 20
        ):
            features_found += 1

        if (
            hasattr(validator, "high_risk_patterns")
            and len(validator.high_risk_patterns) >= 15
        ):
            features_found += 1

        # Check for child protection
        if (
            hasattr(validator, "allowed_child_tables")
            and len(validator.allowed_child_tables) >= 5
        ):
            features_found += 1

        # Check for enhanced methods
        if hasattr(validator, "validate_table_access"):
            features_found += 1

        if hasattr(validator, "_log_blocked_attempt"):
            features_found += 1

        if features_found >= 4:
            log_test(
                "الميزات المحسنة", True, f"تم العثور على {features_found}/5 ميزات محسنة"
            )
        else:
            log_test(
                "الميزات المحسنة",
                False,
                f"تم العثور على {features_found}/5 ميزات محسنة فقط",
            )

    except Exception as e:
        log_test("الميزات المحسنة", False, f"خطأ: {str(e)}")


def test_sql_file_security():
    """🗄️ اختبار أمان ملفات قاعدة البيانات"""
    try:
        # Check production SQL file for security issues
        sql_file_path = "sql/init-production.sql"

        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Check for dangerous default passwords
        dangerous_patterns = [
            "change_me",
            "changeme",
            "password123",
            "default",
            "admin",
        ]

        security_issues = 0
        for pattern in dangerous_patterns:
            if pattern in sql_content.lower():
                security_issues += 1

        # Check for environment variable usage
        env_var_usage = sql_content.count(
            ":'"
        )  # PostgreSQL environment variable syntax

        if security_issues == 0 and env_var_usage >= 1:
            log_test(
                "أمان ملفات قاعدة البيانات",
                True,
                f"لا توجد كلمات مرور افتراضية خطيرة، {env_var_usage} متغير بيئة مستخدم",
            )
        else:
            log_test(
                "أمان ملفات قاعدة البيانات",
                False,
                f"مشاكل أمنية: {security_issues}, متغيرات بيئة: {env_var_usage}",
            )

    except Exception as e:
        log_test("أمان ملفات قاعدة البيانات", False, f"خطأ: {str(e)}")


def run_simplified_test():
    """🧪 تشغيل الاختبار المبسط"""
    print("=" * 80)
    print("🧪 اختبار مبسط لنظام الحماية المحسن من SQL Injection")
    print("=" * 80)
    print(f"⏰ وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # تشغيل جميع الاختبارات
    test_basic_sql_injection_protection()
    test_enhanced_patterns()
    test_child_data_specific_protection()
    test_backward_compatibility()
    test_enhanced_features()
    test_sql_file_security()

    # تقرير النتائج النهائي
    print("=" * 80)
    print("📊 تقرير النتائج النهائي")
    print("=" * 80)

    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (
        (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    )

    print(f"✅ اختبارات ناجحة: {test_results['passed']}")
    print(f"❌ اختبارات فاشلة: {test_results['failed']}")
    print(f"📈 معدل النجاح: {success_rate:.1f}%")
    print()

    if test_results["failed"] > 0:
        print("❌ الأخطاء المكتشفة:")
        for error in test_results["errors"]:
            print(f"   • {error}")
        print()

    # تقييم النتيجة الإجمالية
    if success_rate >= 90:
        print("🎉 تقييم: ممتاز - النظام يعمل بصورة مثالية!")
        print("✅ جاهز للإنتاج")
        print("🚀 جميع الميزات المحسنة تعمل بصورة صحيحة")
    elif success_rate >= 75:
        print("✅ تقييم: جيد جداً - النظام يعمل بصورة صحيحة")
        print("⚠️ يحتاج إلى تحسينات طفيفة")
        print("📈 معظم الميزات تعمل بشكل جيد")
    elif success_rate >= 50:
        print("⚠️ تقييم: مقبول - النظام يعمل مع بعض المشاكل")
        print("🔧 يحتاج إلى إصلاحات")
        print("📋 بعض الميزات تحتاج إلى تطوير")
    else:
        print("❌ تقييم: غير مقبول - النظام يحتاج إلى إصلاحات عاجلة")
        print("🚨 لا يجب استخدامه في الإنتاج")
        print("⚡ الميزات الأساسية لا تعمل")

    print(f"⏰ وقت الانتهاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        run_simplified_test()
    except Exception as e:
        print(f"❌ خطأ في تشغيل الاختبارات: {str(e)}")
        print("📋 تفاصيل الخطأ:")
        traceback.print_exc()
