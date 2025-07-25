"""Emergency Response Services - Core business logic for emergency handling"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

import httpx
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.logging_config import get_logger

from .models import EmergencyAlert, NotificationRequest, ResponseAction, SystemStatus

logger = get_logger(__name__, component="api")


class EmergencyResponseService:
    """خدمة الاستجابة الطارئة."""

    def __init__(self, redis_client: redis.Redis, db_session: AsyncSession) -> None:
        self.redis = redis_client
        self.db = db_session
        self.alert_handlers = {
            "CHILD_SAFETY": self._handle_child_safety_alert,
            "SYSTEM_FAILURE": self._handle_system_failure_alert,
            "SECURITY_BREACH": self._handle_security_breach_alert,
            "CONTENT_VIOLATION": self._handle_content_violation_alert,
        }

    async def process_alert(self, alert_data: dict[str, Any]) -> EmergencyAlert:
        """معالجة تنبيه طارئ."""
        alert = EmergencyAlert(**alert_data)
        # حفظ التنبيه في Redis للمعالجة السريعة
        await self.redis.setex(
            f"alert:{alert.id}",
            3600,  # انتهاء الصلاحية خلال ساعة
            json.dumps(alert.dict(), default=str),
        )
        # تحديد نوع المعالج المطلوب
        handler = self.alert_handlers.get(alert.severity, self._handle_default_alert)
        # تنفيذ المعالجة
        await handler(alert)
        logger.info(f"Alert {alert.id} processed successfully")
        return alert

    async def _handle_child_safety_alert(self, alert: EmergencyAlert):
        """معالجة تنبيهات أمان الطفل."""
        logger.critical(f"CHILD SAFETY ALERT: {alert.description}")
        actions = [
            ResponseAction(
                action_type="IMMEDIATE_STOP",
                target="ai_service",
                parameters={"child_id": alert.child_id},
            ),
            ResponseAction(
                action_type="NOTIFY_PARENTS",
                target="notification_service",
                parameters={
                    "child_id": alert.child_id,
                    "priority": "critical",
                },
            ),
            ResponseAction(
                action_type="LOG_INCIDENT",
                target="audit_service",
                parameters={"alert_id": alert.id, "type": "child_safety"},
            ),
        ]
        await self._execute_actions(actions)

    async def _handle_system_failure_alert(self, alert: EmergencyAlert):
        """معالجة تنبيهات فشل النظام."""
        logger.error(f"SYSTEM FAILURE ALERT: {alert.description}")
        actions = [
            ResponseAction(
                action_type="HEALTH_CHECK",
                target="all_services",
                parameters={},
            ),
            ResponseAction(
                action_type="RESTART_SERVICE",
                target=alert.source,
                parameters={"force": True},
            ),
        ]
        await self._execute_actions(actions)

    async def _handle_security_breach_alert(self, alert: EmergencyAlert):
        """معالجة تنبيهات الاختراق الأمني."""
        logger.critical(f"SECURITY BREACH ALERT: {alert.description}")
        actions = [
            ResponseAction(
                action_type="ISOLATE_SYSTEM",
                target="network_service",
                parameters={"source_ip": alert.metadata.get("source_ip")},
            ),
            ResponseAction(
                action_type="ENABLE_LOCKDOWN",
                target="security_service",
                parameters={"level": "high"},
            ),
            ResponseAction(
                action_type="NOTIFY_ADMIN",
                target="notification_service",
                parameters={"priority": "critical", "type": "security"},
            ),
        ]
        await self._execute_actions(actions)

    async def _handle_content_violation_alert(self, alert: EmergencyAlert):
        """معالجة تنبيهات انتهاك المحتوى."""
        logger.warning(f"CONTENT VIOLATION ALERT: {alert.description}")
        actions = [
            ResponseAction(
                action_type="BLOCK_CONTENT",
                target="content_filter",
                parameters={"content_id": alert.metadata.get("content_id")},
            ),
            ResponseAction(
                action_type="UPDATE_FILTER",
                target="ai_service",
                parameters={"pattern": alert.metadata.get("violation_pattern")},
            ),
        ]
        await self._execute_actions(actions)

    async def _handle_default_alert(self, alert: EmergencyAlert):
        """معالج افتراضي للتنبيهات."""
        logger.info(f"Default handler for alert: {alert.id}")
        action = ResponseAction(
            action_type="LOG_ALERT",
            target="logging_service",
            parameters={"alert_data": alert.dict()},
        )
        await self._execute_actions([action])

    async def _execute_actions(self, actions: list[ResponseAction]):
        """تنفيذ قائمة الإجراءات."""
        for action in actions:
            try:
                action.executed_at = datetime.now(UTC)
                # هنا يتم تنفيذ الإجراء الفعلي
                await self._execute_single_action(action)
                action.success = True
                logger.info(f"Action {action.action_type} executed successfully")
            except Exception as e:
                action.success = False
                action.error_message = str(e)
                logger.error(f"Action {action.action_type} failed: {e}")

    async def _execute_single_action(self, action: ResponseAction):
        """تنفيذ إجراء واحد."""
        # تنفيذ مؤقت - في الواقع سيتم استدعاء الخدمات المناسبة
        await asyncio.sleep(0.1)  # محاكاة وقت التنفيذ

    async def get_emergency_logs(
        self, child_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """الحصول على سجلات الطوارئ."""
        try:
            # هذا مجرد مثال - في التطبيق الحقيقي سيتم استعلام قاعدة البيانات
            logs = []
            # محاكاة بعض السجلات
            for i in range(min(limit, 10)):
                log_entry = {
                    "id": f"log_{i}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "type": "safety_check",
                    "child_id": child_id or f"child_{i}",
                    "message": f"Emergency log entry {i}",
                    "severity": "info",
                }
                logs.append(log_entry)
            return logs
        except Exception as e:
            logger.error(f"Error fetching emergency logs: {e}")
            return []


class SystemMonitorService:
    """خدمة مراقبة النظام."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client
        self.services = [
            "ai-service:8000",
            "content-filter:8001",
            "auth-service:8002",
            "notification-service:8003",
        ]

    async def check_system_health(self) -> list[SystemStatus]:
        """فحص صحة جميع خدمات النظام."""
        statuses = []
        async with httpx.AsyncClient() as client:
            tasks = [
                self._check_service_health(client, service) for service in self.services
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    status = SystemStatus(
                        service_name=self.services[i],
                        status="error",
                        last_check=datetime.now(UTC),
                        response_time_ms=0.0,
                        error_message=str(result),
                    )
                else:
                    status = result
                statuses.append(status)
        return statuses

    async def _check_service_health(
        self,
        client: httpx.AsyncClient,
        service: str,
    ) -> SystemStatus:
        """فحص صحة خدمة واحدة."""
        start_time = datetime.now(UTC)
        try:
            response = await client.get(f"http://{service}/health", timeout=5.0)
            end_time = datetime.now(UTC)
            response_time = (end_time - start_time).total_seconds() * 1000
            return SystemStatus(
                service_name=service,
                status=("healthy" if response.status_code == 200 else "unhealthy"),
                last_check=end_time,
                response_time_ms=response_time,
                error_message=(
                    None
                    if response.status_code == 200
                    else f"HTTP {response.status_code}"
                ),
            )
        except Exception as e:
            end_time = datetime.now(UTC)
            return SystemStatus(
                service_name=service,
                status="error",
                last_check=end_time,
                response_time_ms=0.0,
                error_message=str(e),
            )

    async def get_system_metrics(self) -> dict[str, Any]:
        """الحصول على مقاييس النظام."""
        try:
            metrics = {
                "timestamp": datetime.now(UTC).isoformat(),
                "services_count": len(self.services),
                "redis_info": {},
                "alerts_count": 0,
            }

            # الحصول على معلومات Redis
            try:
                redis_info = await self.redis.info()
                metrics["redis_info"] = {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0),
                }
            except Exception as e:
                logger.error(f"Error getting Redis info: {e}")

            # عدد التنبيهات النشطة
            try:
                alert_keys = await self.redis.keys("alert:*")
                metrics["alerts_count"] = len(alert_keys)
            except Exception as e:
                logger.error(f"Error counting alerts: {e}")

            return metrics
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}


class EmergencyNotificationService:
    """خدمة الإشعارات."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    async def send_notification(self, request: NotificationRequest) -> bool:
        """إرسال إشعار."""
        try:
            # حفظ الإشعار في قائمة الانتظار
            notification_data = {
                "alert_id": request.alert_id,
                "child_id": request.child_id,
                "contacts": request.parent_contacts,
                "message": request.message,
                "priority": request.priority,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await self.redis.lpush("notification_queue", json.dumps(notification_data))
            logger.info(f"Notification queued for alert {request.alert_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue notification: {e}")
            return False

    async def get_notification_history(
        self, child_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """الحصول على تاريخ الإشعارات."""
        try:
            # محاكاة البيانات - في التطبيق الحقيقي سيتم استعلام قاعدة البيانات
            notifications = []
            for i in range(min(limit, 10)):
                notification = {
                    "id": f"notification_{i}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "child_id": child_id or f"child_{i}",
                    "message": f"Notification message {i}",
                    "priority": "medium",
                    "sent": True,
                    "delivered": True,
                }
                notifications.append(notification)
            return notifications
        except Exception as e:
            logger.error(f"Error fetching notification history: {e}")
            return []

    async def send_emergency_sms(
        self, phone_numbers: list[str], message: str, child_id: str | None = None
    ) -> bool:
        """إرسال رسائل SMS طارئة."""
        try:
            # محاكاة إرسال SMS - في التطبيق الحقيقي سيتم تكامل مع خدمة SMS
            sms_data = {
                "phone_numbers": phone_numbers,
                "message": message,
                "child_id": child_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "type": "emergency_sms",
            }

            await self.redis.lpush("sms_queue", json.dumps(sms_data))

            logger.critical("Emergency SMS queued for multiple recipients")
            return True
        except Exception as e:
            logger.error(f"Failed to queue emergency SMS: {e}")
            return False
