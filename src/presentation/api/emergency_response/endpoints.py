"""Emergency Response Endpoints - API routes for emergency system"""

import os
from datetime import UTC, datetime

from fastapi import BackgroundTasks, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.logging_config import get_logger

from .models import AlertPayload, EmergencyAlert, HealthResponse, NotificationRequest
from .services import (
    EmergencyResponseService,
    NotificationService,
    SystemMonitorService,
)

logger = get_logger(__name__, component="api")

security = HTTPBearer()

# متغيرات البيئة - أمان محسّن بدون قيم افتراضية خطيرة
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.critical("JWT_SECRET environment variable is required but not set")
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: JWT_SECRET must be set in environment variables",
    )

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class EmergencyEndpoints:
    """Emergency Response API Endpoints."""

    def __init__(
        self,
        emergency_service: EmergencyResponseService,
        monitor_service: SystemMonitorService,
        notification_service: NotificationService,
    ):
        self.emergency_service = emergency_service
        self.monitor_service = monitor_service
        self.notification_service = notification_service

    async def webhook_alerts(
        self,
        request: Request,
        payload: AlertPayload,
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        """استلام التنبيهات من Prometheus / Alertmanager."""
        client_ip = request.client.host
        logger.info(f"Received alert webhook from {client_ip}")
        try:
            # معالجة كل تنبيه في الخلفية
            for alert_data in payload.alerts:
                background_tasks.add_task(
                    self._process_single_alert,
                    alert_data,
                    payload.receiver,
                )
            return {
                "status": "accepted",
                "message": f"تم استلام {len(payload.alerts)} تنبيه للمعالجة",
            }
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _process_single_alert(self, alert_data: dict, receiver: str):
        """معالجة تنبيه واحد."""
        try:
            # تحويل البيانات إلى نموذج التنبيه
            emergency_alert = EmergencyAlert(
                id=f"alert_{datetime.now().timestamp()}",
                severity=alert_data.get("labels", {}).get("severity", "unknown"),
                description=alert_data.get("annotations", {}).get(
                    "summary",
                    "No description",
                ),
                source=alert_data.get("labels", {}).get("instance", "unknown"),
                timestamp=datetime.now(UTC),
                child_id=alert_data.get("labels", {}).get("child_id"),
                action_required=True,
                metadata=alert_data,
            )
            await self.emergency_service.process_alert(emergency_alert.dict())
        except Exception as e:
            logger.error(f"Error processing single alert: {e}")

    async def health_check(self) -> HealthResponse:
        """فحص صحة خدمة الاستجابة الطارئة."""
        try:
            # فحص الاتصال بالخدمات المطلوبة
            system_status = await self.monitor_service.check_system_health()
            dependencies = {}
            for status in system_status:
                dependencies[status.service_name] = status.status
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now(UTC),
                version="1.0.0",
                uptime_seconds=0.0,  # سيتم حسابه لاحقاً
                dependencies=dependencies,
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Service unhealthy")

    async def get_alerts(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> list[dict]:
        """الحصول على قائمة التنبيهات النشطة."""
        # التحقق من صحة التوكن
        if not self._verify_token(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            # الحصول على التنبيهات من Redis
            # هذا مجرد مثال - سيتم تنفيذه بالكامل لاحقاً
            return []
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def send_notification(
        self,
        request: NotificationRequest,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict[str, str]:
        """إرسال إشعار طارئ."""
        # التحقق من صحة التوكن
        if not self._verify_token(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            success = await self.notification_service.send_notification(request)
            if success:
                return {"status": "sent", "message": "تم إرسال الإشعار بنجاح"}
            raise HTTPException(status_code=500, detail="فشل في إرسال الإشعار")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def system_status(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> list[dict]:
        """الحصول على حالة النظام."""
        # التحقق من صحة التوكن
        if not self._verify_token(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid token")
        try:
            statuses = await self.monitor_service.check_system_health()
            return [status.dict() for status in statuses]
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def _verify_token(self, token: str) -> bool:
        """التحقق من صحة التوكن."""
        if ENVIRONMENT == "development":
            return True  # تجاهل التحقق في بيئة التطوير
        # في الإنتاج، سيتم التحقق من JWT token
        return token == JWT_SECRET  # مؤقت - سيتم تحسينه

    async def emergency_contact_alert(
        self,
        child_id: str,
        alert_type: str,
        message: str,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict[str, str]:
        """إرسال تنبيه لجهات الاتصال الطارئة."""
        if not self._verify_token(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid token")

        try:
            # إنشاء تنبيه طارئ
            emergency_alert = EmergencyAlert(
                id=f"emergency_{datetime.now().timestamp()}",
                severity="critical",
                description=message,
                source="emergency_contact_system",
                timestamp=datetime.now(UTC),
                child_id=child_id,
                action_required=True,
                metadata={"alert_type": alert_type},
            )

            # معالجة التنبيه
            await self.emergency_service.process_alert(emergency_alert.dict())

            return {
                "status": "sent",
                "message": "تم إرسال التنبيه الطارئ بنجاح",
                "alert_id": emergency_alert.id,
            }
        except Exception as e:
            logger.error(f"Error sending emergency contact alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_emergency_logs(
        self,
        child_id: str = None,
        limit: int = 50,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> list[dict]:
        """الحصول على سجلات الطوارئ."""
        if not self._verify_token(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid token")

        try:
            # الحصول على السجلات من قاعدة البيانات
            # هذا مجرد مثال - سيتم تنفيذه بالكامل لاحقاً
            logs = await self.emergency_service.get_emergency_logs(
                child_id=child_id, limit=limit
            )
            return logs
        except Exception as e:
            logger.error(f"Error fetching emergency logs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
