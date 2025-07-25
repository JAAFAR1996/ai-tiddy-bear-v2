"""Database Service for AI Teddy Bear."""

from datetime import date, datetime, timedelta
from uuid import uuid4

from sqlalchemy.future import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.models.child_models import ChildModel

from .session_manager import get_async_session

logger = get_logger(__name__, component="persistence")


# -------- REAL DATABASE SERVICE IMPLEMENTATION --------


class RealDatabaseService:
    def __init__(self):
        pass

    async def get_safety_events(self, child_id: str, limit: int = 10):
        async with get_async_session() as session:
            result = await session.execute(
                select(ChildModel.safety_events).where(ChildModel.child_id == child_id)
            )
            row = result.first()
            if row and row[0]:
                return row[0][-limit:]
            return []

    async def record_safety_event(
        self, child_id: str, event_type: str, details: str, severity: str
    ):
        async with get_async_session() as session:
            child = await session.get(ChildModel, child_id)
            if not child:
                raise ValueError("Child not found")
            event_id = str(uuid4())
            event = {
                "event_id": event_id,
                "event_type": event_type,
                "details": details,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
            }
            if not hasattr(child, "safety_events") or child.safety_events is None:
                child.safety_events = []
            child.safety_events.append(event)
            await session.commit()
            return event_id

    async def get_safety_score(self, child_id: str):
        async with get_async_session() as session:
            child = await session.get(ChildModel, child_id)
            if child and hasattr(child, "safety_score"):
                return child.safety_score
            return None

    async def update_safety_score(self, child_id: str, new_score: int, reason: str):
        async with get_async_session() as session:
            child = await session.get(ChildModel, child_id)
            if not child:
                return False
            child.safety_score = new_score
            if (
                not hasattr(child, "safety_score_history")
                or child.safety_score_history is None
            ):
                child.safety_score_history = []
            child.safety_score_history.append(
                {
                    "score": new_score,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            await session.commit()
            return True

    async def send_safety_alert(self, alert_data: dict):
        # مثال: إضافة alert إلى جدول أو إرسال إشعار خارجي
        logger.warning("SAFETY ALERT: %s", alert_data)
        # يمكن ربطها بخدمة إشعارات حقيقية هنا
        return True

    async def record_usage(self, usage_record: dict):
        async with get_async_session() as session:
            child = await session.get(ChildModel, usage_record["child_id"])
            if not child:
                raise ValueError("Child not found")
            if not hasattr(child, "usage_records") or child.usage_records is None:
                child.usage_records = []
            child.usage_records.append(usage_record)
            await session.commit()
            return True

    async def get_daily_usage(self, child_id: str):
        async with get_async_session() as session:
            child = await session.get(ChildModel, child_id)
            if (
                not child
                or not hasattr(child, "usage_records")
                or not child.usage_records
            ):
                return 0
            today = date.today().isoformat()
            return sum(
                rec["duration"]
                for rec in child.usage_records
                if rec["timestamp"].startswith(today)
            )

    async def get_usage_statistics(self, child_id: str, days: int = 7):
        async with get_async_session() as session:
            child = await session.get(ChildModel, child_id)
            if (
                not child
                or not hasattr(child, "usage_records")
                or not child.usage_records
            ):
                return {}
            now = datetime.now()
            stats = {}
            for i in range(days):
                day = (now - timedelta(days=i)).date().isoformat()
                stats[day] = sum(
                    rec["duration"]
                    for rec in child.usage_records
                    if rec["timestamp"].startswith(day)
                )
            return stats


# Singleton accessor
_real_db_service = RealDatabaseService()


def get_database_service():
    return _real_db_service


def reset_database_service():
    """Reset database service for testing purposes."""
    global _real_db_service
    _real_db_service = RealDatabaseService()
    logger.info("Database service reset for testing")
