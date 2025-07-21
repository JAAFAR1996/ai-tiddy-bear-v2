"""Emergency Response Main Module - Simplified main application"""

from datetime import datetime
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

from .endpoints import EmergencyEndpoints
from .services import (
    EmergencyResponseService,
    NotificationService,
    SystemMonitorService
)
from src.infrastructure.logging_config import get_logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = get_logger(__name__, component="api")

# متغيرات البيئة - محسّنة للإنتاج
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# إعداد قاعدة البيانات الآمنة - PostgreSQL فقط للإنتاج
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.critical(
        "DATABASE_URL environment variable is required for emergency response",
    )
    raise RuntimeError(
        "CRITICAL: DATABASE_URL must be set for emergency response system",
    )

# منع استخدام SQLite في نظام الطوارئ الحرج
if DATABASE_URL.startswith("sqlite"):
    logger.critical(
        "SQLite detected in emergency response system - SECURITY VIOLATION"
    )
    raise RuntimeError(
        "CRITICAL: SQLite is not allowed for emergency response systems. "
        "Use PostgreSQL for data integrity and COPPA compliance.",
    )

# متغيرات عامة
redis_client = None
db_session = None
emergency_service = None
monitor_service = None
notification_service = None
endpoints = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق."""
    global redis_client, db_session, emergency_service, monitor_service, notification_service, endpoints

    logger.info("🚨 Starting Emergency Response System...")
    try:
        # إعداد Redis
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()
        logger.info("✅ Redis connected")

        # إعداد قاعدة البيانات
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession)
        db_session = async_session()
        logger.info("✅ Database connected")

        # إعداد الخدمات
        emergency_service = EmergencyResponseService(redis_client, db_session)
        monitor_service = SystemMonitorService(redis_client)
        notification_service = NotificationService(redis_client)

        # إعداد النقاط النهائية
        endpoints = EmergencyEndpoints(
            emergency_service,
            monitor_service,
            notification_service,
        )
        logger.info("🚨 Emergency Response System started successfully")
    except Exception as e:
        logger.error(f"Failed to start Emergency Response System: {e}")
        raise

    yield

    # تنظيف الموارد
    logger.info("🚨 Shutting down Emergency Response System...")
    if redis_client:
        await redis_client.close()
    if db_session:
        await db_session.close()
    logger.info("🚨 Emergency Response System shutdown complete")


def create_app() -> FastAPI:
    """إنشاء تطبيق FastAPI."""
    app = FastAPI(
        title="🚨 AI Teddy Bear - Emergency Response",
        description="نظام الاستجابة الطارئة للتنبيهات الأمنية",
        version="1.0.0",
        lifespan=lifespan,
    )

    # إعداد CORS آمن
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://yourdomain.com",  # إضافة نطاقات الإنتاج
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # تسجيل المسارات
    @app.post("/webhook/alerts")
    async def webhook_alerts(request, payload, background_tasks):
        """استلام التنبيهات من أنظمة المراقبة الخارجية."""
        return await endpoints.webhook_alerts(
            request, payload, background_tasks
        )

    @app.get("/health")
    async def health_check():
        """فحص صحة نظام الاستجابة الطارئة."""
        return await endpoints.health_check()

    @app.get("/alerts")
    async def get_alerts(credentials):
        """الحصول على قائمة التنبيهات النشطة."""
        return await endpoints.get_alerts(credentials)

    @app.post("/notifications")
    async def send_notification(request, credentials):
        """إرسال إشعارات طارئة."""
        return await endpoints.send_notification(request, credentials)

    @app.get("/system/status")
    async def system_status(credentials):
        """الحصول على حالة النظام الشاملة."""
        return await endpoints.system_status(credentials)

    @app.post("/emergency-contact/{child_id}")
    async def emergency_contact_alert(child_id: str, alert_type: str,
                                      message: str, credentials):
        """إرسال تنبيه لجهات الاتصال الطارئة لطفل محدد."""
        return await endpoints.emergency_contact_alert(
            child_id, alert_type, message, credentials
        )

    @app.get("/logs/emergency")
    async def get_emergency_logs(child_id: str = None, limit: int = 50,
                                 credentials=None):
        """الحصول على سجلات الطوارئ."""
        return await endpoints.get_emergency_logs(child_id, limit, credentials)

    # إضافة معلومات إضافية للتطبيق
    @app.get("/info")
    async def app_info():
        """معلومات عن نظام الاستجابة الطارئة."""
        return {
            "name": "AI Teddy Bear Emergency Response",
            "version": "1.0.0",
            "description": "نظام الاستجابة الطارئة للتنبيهات الأمنية",
            "features": [
                "مراقبة الأطفال في الوقت الفعلي",
                "تنبيهات فورية لجهات الاتصال الطارئة",
                "تتبع الأحداث الأمنية",
                "تكامل مع أنظمة المراقبة",
                "امتثال COPPA",
            ],
            "endpoints": {
                "webhook": "/webhook/alerts",
                "health": "/health",
                "alerts": "/alerts",
                "notifications": "/notifications",
                "status": "/system/status",
                "emergency_contact": "/emergency-contact/{child_id}",
                "logs": "/logs/emergency",
            },
            "timestamp": datetime.now().isoformat(),
        }

    return app


# نقطة الدخول
if __name__ == "__main__":
    import uvicorn

    API_PORT = int(os.getenv("API_PORT", 8080))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")

    logger.info(f"🚨 Starting Emergency Response Server on {API_HOST}:{API_PORT}")

    app = create_app()
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )
