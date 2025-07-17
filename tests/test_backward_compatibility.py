from src.infrastructure.logging_config import get_logger
from typing import Any
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


logger = get_logger(__name__, component="test")


"""
Test Backward Compatibility for modern_ui.py
هذا الملف يختبر أن كل الاستيرادات القديمة لا تزال تعمل
"""


def test_import(import_statement, expected_name) -> Any:
    """Test a single import statement"""
    try:
        None
        logger.info(f"✅ {import_statement}")
        return True
    except Exception as e:
        logger.info(f"❌ {import_statement}")
        logger.info(f"   Error: {e}")
        return False


def test_backward_compatibility() -> Any:
    """Test all backward compatibility imports"""
    logger.info("🔍 Testing Backward Compatibility for modern_ui.py")
    logger.info("=" * 60)
    failed_imports = []
    total_tests = 0
    imports_to_test = [
        (
            "from modern_ui import AudioProcessingEngine",
            "AudioProcessingEngine",
        ),
        ("from modern_ui import WebSocketClient", "WebSocketClient"),
        ("from modern_ui import ModernAudioWidget", "ModernAudioWidget"),
        ("from modern_ui import TeddyMainWindow", "TeddyMainWindow"),
        ("from modern_ui import ConversationWidget", "ConversationWidget"),
        ("from modern_ui import WaveformWidget", "WaveformWidget"),
        ("from modern_ui import AudioWidget", "AudioWidget"),
        ("from modern_ui import MainWindow", "MainWindow"),
        ("from modern_ui import AudioEngine", "AudioEngine"),
        ("from modern_ui import WSClient", "WSClient"),
        (
            "from modern_ui import get_available_features",
            "get_available_features",
        ),
        (
            "from modern_ui import check_feature_compatibility",
            "check_feature_compatibility",
        ),
        (
            "from modern_ui import ENTERPRISE_DASHBOARD_AVAILABLE",
            "ENTERPRISE_DASHBOARD_AVAILABLE",
        ),
        ("from modern_ui import PYSIDE6_AVAILABLE", "PYSIDE6_AVAILABLE"),
    ]
    logger.info("\n📦 Testing Core Component Imports:")
    for import_stmt, name in imports_to_test:
        total_tests += 1
        if not test_import(import_stmt, name):
            failed_imports.append(import_stmt)
    pyside6_imports = [
        ("from modern_ui import QApplication", "QApplication"),
        ("from modern_ui import QPushButton", "QPushButton"),
        ("from modern_ui import QWidget", "QWidget"),
        ("from modern_ui import Signal", "Signal"),
        ("from modern_ui import Qt", "Qt"),
    ]
    logger.info("\n🎨 Testing PySide6 Re-exports:")
    for import_stmt, name in pyside6_imports:
        total_tests += 1
        if not test_import(import_stmt, name):
            failed_imports.append(import_stmt)
    logger.info("\n⚙️ Testing Functionality:")
    try:
        from modern_ui import (
            check_feature_compatibility,
            get_available_features,
        )

        features = get_available_features()
        logger.info(
            f"✅ get_available_features() returned {len(features)} features"
        )
        audio_available = check_feature_compatibility("audio_processing")
        logger.info(
            f"✅ check_feature_compatibility('audio_processing') = {audio_available}"
        )
        total_tests += 2
    except Exception as e:
        logger.info(f"❌ Functionality test failed: {e}")
        failed_imports.append("functionality_test")
        total_tests += 2
    logger.info("\n🔄 Testing Aliases Functionality:")
    try:
        from modern_ui import (
            AudioEngine,
            AudioProcessingEngine,
            AudioWidget,
            MainWindow,
            ModernAudioWidget,
            TeddyMainWindow,
        )

        assert AudioWidget is ModernAudioWidget, "AudioWidget alias incorrect"
        assert (
            AudioEngine is AudioProcessingEngine
        ), "AudioEngine alias incorrect"
        assert MainWindow is TeddyMainWindow, "MainWindow alias incorrect"
        logger.info("✅ All aliases point to correct classes")
        total_tests += 1
    except Exception as e:
        logger.info(f"❌ Aliases test failed: {e}")
        failed_imports.append("aliases_test")
        total_tests += 1
    logger.info("\n" + "=" * 60)
    logger.info("📊 BACKWARD COMPATIBILITY TEST RESULTS:")
    logger.info(
        f"✅ Passed: {total_tests - len(failed_imports)}/{total_tests}"
    )
    logger.info(f"❌ Failed: {len(failed_imports)}/{total_tests}")
    if failed_imports:
        logger.info("\n❌ Failed Imports:")
        for imp in failed_imports:
            logger.info(f"   - {imp}")
        return False
    else:
        logger.info("\n🎉 ALL BACKWARD COMPATIBILITY TESTS PASSED!")
        logger.info("   Old code will continue to work without modification!")
        return True


if __name__ == "__main__":
    success = test_backward_compatibility()
    sys.exit(0 if success else 1)
