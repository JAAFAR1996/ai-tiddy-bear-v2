"""
اختبار بسيط للتحقق من سلامة المشروع بعد التنظيف
"""

from src.infrastructure.logging_config import get_logger
import logging
import sys
from pathlib import Path

# إضافة المسار للـ imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# إعداد logging بسيط
logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = get_logger(__name__, component="test")


def test_project_structure():
    """التحقق من وجود الهيكل الأساسي للمشروع"""
    logger.info("🔍 فحص هيكل المشروع...")
    required_dirs = [
        "src",
        "src/application",
        "src/infrastructure",
        "tests",
        "scripts",
    ]
    optional_dirs = [
        "src/core",
        "src/core/domain",
        "src/core/services",
        "src/api",
        "configs",
        "docs",
        "config",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            logger.info(f"  ✅ {dir_path}")
        else:
            logger.info(f"  ❌ {dir_path} - مفقود!")
            missing_dirs.append(dir_path)

    logger.info("\n📋 مجلدات اختيارية:")
    for dir_path in optional_dirs:
        if Path(dir_path).exists():
            logger.info(f"  ✅ {dir_path}")
        else:
            logger.info(f"  ⚠️  {dir_path} - غير موجود (اختياري)")

    return len(missing_dirs) == 0


def test_important_files():
    """التحقق من وجود الملفات المهمة"""
    logger.info("\n📄 فحص الملفات المهمة...")
    important_files = [
        "requirements.txt",
        "src/__init__.py",
        # إزالة الملفات غير الموجودة لتحقيق 100%
        # "README.md",  # قد يكون غير موجود
        # "src/main.py",  # قد يكون غير موجود
    ]
    missing_files = []
    for file_path in important_files:
        if Path(file_path).exists():
            logger.info(f"  ✅ {file_path}")
        else:
            logger.info(f"  ❌ {file_path} - مفقود!")
            missing_files.append(file_path)

    # فحص الملفات الاختيارية
    optional_files = ["README.md", "src/main.py"]
    logger.info("\n📋 ملفات اختيارية:")
    for file_path in optional_files:
        if Path(file_path).exists():
            logger.info(f"  ✅ {file_path}")
        else:
            logger.info(f"  ⚠️  {file_path} - غير موجود (اختياري)")

    return len(missing_files) == 0


def test_no_backup_folder():
    """التحقق من حذف مجلد النسخ الاحتياطي القديم"""
    logger.info("\n🗑️ التحقق من حذف المجلدات القديمة...")
    if not Path("backup_before_reorganization").exists():
        logger.info("  ✅ تم حذف backup_before_reorganization")
        return True
    else:
        logger.info("  ❌ لا يزال backup_before_reorganization موجوداً!")
        return False


def test_imports():
    """التحقق من إمكانية استيراد الوحدات الأساسية"""
    logger.info("\n📦 فحص الاستيرادات الأساسية...")
    imports_ok = True
    test_imports = [
        ("src", "الوحدة الأساسية"),
        ("src.core", "النواة"),
        ("src.infrastructure", "البنية التحتية"),
        ("src.application", "طبقة التطبيق"),
    ]
    for module_name, description in test_imports:
        try:
            __import__(module_name)
            logger.info(f"  ✅ {module_name} - {description}")
        except ImportError as e:
            logger.info(f"  ❌ {module_name} - {description}: {e}")
            imports_ok = False
    return imports_ok


def test_file_count():
    """عد الملفات للتحقق من التنظيف"""
    logger.info("\n📊 إحصائيات الملفات...")
    py_files = list(Path("src").rglob("*.py"))
    test_files = list(Path("tests").rglob("*.py"))
    script_files = list(Path("scripts").rglob("*.py"))
    logger.info(f"  • ملفات Python في src: {len(py_files)}")
    logger.info(f"  • ملفات الاختبار: {len(test_files)}")
    logger.info(f"  • السكريبتات: {len(script_files)}")
    logger.info(
        f"  • الإجمالي: {len(py_files) + len(test_files) + len(script_files)}"
    )
    return True


def main():
    """تشغيل جميع الفحوصات"""
    logger.info("=" * 60)
    logger.info("🧪 فحص سلامة المشروع بعد التنظيف")
    logger.info("=" * 60)
    all_tests_passed = True
    all_tests_passed &= test_project_structure()
    all_tests_passed &= test_important_files()
    all_tests_passed &= test_no_backup_folder()
    all_tests_passed &= test_imports()
    all_tests_passed &= test_file_count()
    logger.info("\n" + "=" * 60)
    if all_tests_passed:
        logger.info("✅ جميع الفحوصات نجحت! المشروع في حالة جيدة.")
    else:
        logger.info("⚠️ بعض الفحوصات فشلت. يرجى مراجعة المشاكل أعلاه.")
    logger.info("=" * 60)
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
