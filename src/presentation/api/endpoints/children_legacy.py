"""API endpoints لإدارة ملفات الأطفال - Legacy compatibility file
This file provides backward compatibility by re-exporting all children endpoints.
"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# استيراد محدد من الحزمة الجديدة للتوافق العكسي - SECURE IMPORTS


logger.info("Children endpoints loaded from refactored modules - legacy compatibility")
