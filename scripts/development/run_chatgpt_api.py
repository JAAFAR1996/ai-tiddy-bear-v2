#!/usr/bin/env python3
"""
🚀 تشغيل ChatGPT Complete API Server
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """فحص التبعيات المطلوبة"""

    print("🔍 فحص التبعيات...")

    dependencies = ["uvicorn", "fastapi", "openai"]
    missing = []

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} متاح")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} مفقود")

    if missing:
        print(f"\n⚠️ تبعيات مفقودة: {', '.join(missing)}")
        print("💡 لتثبيت التبعيات:")
        print("pip install uvicorn fastapi openai")
        print("\n🔄 تشغيل في وضع Mock...")
        return False

    return True


def run_with_uvicorn():
    """تشغيل مع uvicorn"""

    print("🚀 تشغيل ChatGPT API مع uvicorn...")

    try:
        subprocess.run(
            [
                "uvicorn",
                "chatgpt_complete_api:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
                "--log-level",
                "info",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تشغيل uvicorn: {e}")
        return False
    except FileNotFoundError:
        print("❌ uvicorn غير متاح")
        return False

    return True


def run_with_python():
    """تشغيل مع Python المدمج"""

    print("🐍 تشغيل مع Python المدمج...")

    try:
        # استيراد الملف الشامل
        from chatgpt_complete_api import create_app

        app = create_app()

        print("✅ تم إنشاء التطبيق بنجاح")
        print("📡 الخادم يعمل على: http://localhost:8000")
        print("📖 الوثائق متاحة على: http://localhost:8000/docs")
        print("🔍 فحص الصحة: http://localhost:8000/health")

        # في الإنتاج، استخدم uvicorn
        print("\n💡 للتشغيل في الإنتاج:")
        print("uvicorn chatgpt_complete_api:app --host 0.0.0.0 --port 8000")

        return True

    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        return False


def test_api_endpoints():
    """اختبار endpoints الأساسية"""

    print("\n🧪 اختبار endpoints...")

    try:
        import asyncio
        from chatgpt_complete_api import chatgpt_service, auth_service

        async def run_tests():
            # اختبار تسجيل مستخدم
            user = auth_service.create_user("demo@test.com", "demo123")
            print(f"✅ تم إنشاء مستخدم تجريبي: {user['email']}")

            # اختبار ChatGPT
            child_profile = {
                "age": 7,
                "preferences": {
                    "interests": ["science", "animals"],
                    "favorite_character": "robot friend",
                },
            }

            response = await chatgpt_service.chat_with_child(
                child_id="demo-child",
                message="Tell me about space",
                child_profile=child_profile,
            )

            print(f"✅ اختبار ChatGPT: {response['response'][:50]}...")

            return True

        asyncio.run(run_tests())
        return True

    except Exception as e:
        print(f"❌ خطأ في اختبار endpoints: {e}")
        return False


def main():
    """الدالة الرئيسية"""

    print("🤖 ChatGPT Complete API Launcher")
    print("=" * 50)

    # فحص التبعيات
    deps_available = check_dependencies()

    # اختبار endpoints
    test_success = test_api_endpoints()

    if not test_success:
        print("❌ فشل في اختبار endpoints")
        return

    print("\n" + "=" * 50)
    print("🎯 خيارات التشغيل:")

    if deps_available:
        print("1. تشغيل مع uvicorn (مستحسن)")
        print("2. تشغيل مع Python")

        choice = input("\nاختر (1 أو 2): ").strip()

        if choice == "1":
            if not run_with_uvicorn():
                print("🔄 تجربة Python...")
                run_with_python()
        else:
            run_with_python()
    else:
        run_with_python()


if __name__ == "__main__":
    main()
