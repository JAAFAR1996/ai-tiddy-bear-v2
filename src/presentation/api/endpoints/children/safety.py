from .models import ChildSafetySummary
from src.infrastructure.logging_config import get_logger
from typing import Any
from datetime import datetime


class DatabaseNotAvailableError(Exception):
    """Raised when the database service is not available in production."""
    pass


"""Security operations and safety summary for children."""


logger = get_logger(__name__, component="api")

# Import FastAPI dependencies
try:
    from fastapi import HTTPException, status

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail

    class status:
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500


# Import services
try:
    from infrastructure.persistence.real_database_service import (
        get_database_service,
    )

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.critical("Database service is not available. This is a production-blocking error. All safety features require a real database connection.")


class SafetyEventTypes:
    """Types of safety events."""

    CONTENT_FILTER = "content_filter"
    INAPPROPRIATE_LANGUAGE = "inappropriate_language"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PRIVACY_VIOLATION = "privacy_violation"
    EXCESSIVE_USAGE = "excessive_usage"
    UNSAFE_INTERACTION = "unsafe_interaction"


class ChildSafetyManager:
    """Child safety manager."""

    @staticmethod
    async def get_safety_summary(child_id: str) -> ChildSafetySummary:
        """Get child safety summary."""
        try:
            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot get child safety summary. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for get_safety_summary.")

            db_service = get_database_service()
            safety_events = await db_service.get_safety_events(child_id)
            return ChildSafetySummary.from_safety_events(child_id, safety_events)
        except Exception as e:
            logger.error(f"Error getting safety summary for child {child_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to get safety summary: {e!s}",
            )

    @staticmethod
    async def record_safety_event(
        child_id: str,
        event_type: str,
        event_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Record safety event."""
        try:
            event_record = {
                "child_id": child_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.now().isoformat(),
                "severity": event_data.get("severity", "medium"),
            }

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot record safety event. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for record_safety_event.")

            # Log event in database
            db_service = get_database_service()
            event_id = await db_service.record_safety_event(
                child_id=child_id,
                event_type=event_type,
                details=str(event_data),
                severity=event_record["severity"],
            )

            event_record["event_id"] = event_id

            # Update safety score
            await ChildSafetyManager.update_safety_score(child_id, event_type)

            return event_record
        except Exception as e:
            logger.error(f"Error recording safety event: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record safety event: {e!s}",
            )

    @staticmethod
    async def update_safety_score(child_id: str, event_type: str) -> int:
        """Update safety score based on event type."""
        try:
            # Deduction points for each event type
            score_deductions = {
                SafetyEventTypes.CONTENT_FILTER: 5,
                SafetyEventTypes.INAPPROPRIATE_LANGUAGE: 10,
                SafetyEventTypes.SUSPICIOUS_ACTIVITY: 15,
                SafetyEventTypes.PRIVACY_VIOLATION: 20,
                SafetyEventTypes.EXCESSIVE_USAGE: 3,
                SafetyEventTypes.UNSAFE_INTERACTION: 25,
            }

            deduction = score_deductions.get(event_type, 5)

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot update safety score. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for update_safety_score.")

            # Get current safety score from database
            db_service = get_database_service()
            try:
                # جلب score حقيقي من قاعدة البيانات
                current_score = await db_service.get_safety_score(child_id=child_id)
                if current_score is None:
                    logger.critical(f"No safety score found for child {child_id}. Cannot update score.")
                    raise RuntimeError("No safety score found in database.")
                new_score = max(0, current_score - deduction)

                success = await db_service.update_safety_score(
                    child_id=child_id,
                    new_score=new_score,
                    reason=f"Safety event: {event_type}",
                )

                if not success:
                    logger.error(f"Failed to update safety score for child {child_id}")
                    raise RuntimeError("Safety score update failed")
            except Exception as e:
                logger.error(f"Error updating safety score for child {child_id}: {e}")
                raise

            # Send alert if score drops significantly
            if new_score < 70:
                await ChildSafetyManager.send_safety_alert(
                    child_id,
                    new_score,
                    event_type,
                )

            return new_score
        except Exception as e:
            logger.error(f"Error updating safety score: {e}")
            return 100

    @staticmethod
    async def send_safety_alert(
        child_id: str,
        safety_score: int,
        event_type: str,
    ) -> None:
        """Send safety alert to parents."""
        try:
            alert_data = {
                "child_id": child_id,
                "safety_score": safety_score,
                "event_type": event_type,
                "alert_level": "high" if safety_score < 50 else "medium",
                "timestamp": datetime.now().isoformat(),
                "message": f"Safety score dropped to {safety_score}% due to {event_type}",
            }

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot send safety alert. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for send_safety_alert.")

            # Send alert (can be implemented via email, push notification, etc)
            db_service = get_database_service()
            await db_service.send_safety_alert(alert_data)
        except Exception as e:
            logger.error(f"Error sending safety alert: {e}")

    @staticmethod
    async def get_safety_events(child_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get safety events for child."""
        try:

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot get safety events. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for get_safety_events.")

            db_service = get_database_service()
            return await db_service.get_safety_events(child_id, limit)
        except Exception as e:
            logger.error(f"Error getting safety events: {e}")
            return []


class ContentSafetyFilter:
    """Content safety filter."""

    @staticmethod
    def filter_text_content(text: str, child_age: int) -> dict[str, Any]:
        """Filter text content."""
        try:
            # Inappropriate words (can be improved using ML)
            inappropriate_words = [
                "bad_word1",
                "bad_word2",
                "inappropriate_term",
            ]

            filtered_text = text
            violations = []

            for word in inappropriate_words:
                if word.lower() in text.lower():
                    filtered_text = filtered_text.replace(word, "***")
                    violations.append(word)

            return {
                "original_text": text,
                "filtered_text": filtered_text,
                "violations": violations,
                "is_safe": len(violations) == 0,
                "age_appropriate": child_age >= 8,  # Age appropriateness check
            }
        except Exception as e:
            logger.error(f"Error filtering text content: {e}")
            return {
                "original_text": text,
                "filtered_text": text,
                "violations": [],
                "is_safe": True,
                "age_appropriate": True,
            }

    @staticmethod
    def validate_interaction_safety(
        interaction_data: dict[str, Any],
        child_age: int,
    ) -> dict[str, Any]:
        """Validate interaction safety."""
        try:
            safety_checks = {
                "content_appropriate": True,
                "duration_acceptable": True,
                "frequency_normal": True,
                "privacy_protected": True,
            }

            violations = []

            if "text" in interaction_data:
                content_filter = ContentSafetyFilter.filter_text_content(
                    interaction_data["text"],
                    child_age,
                )
                if not content_filter["is_safe"]:
                    safety_checks["content_appropriate"] = False
                    violations.extend(content_filter["violations"])

            # Check interaction duration
            if "duration" in interaction_data:
                max_duration = 30 * 60  # 30 minutes
                if interaction_data["duration"] > max_duration:
                    safety_checks["duration_acceptable"] = False
                    violations.append("excessive_duration")

            # Check interaction frequency
            if "daily_interactions" in interaction_data:
                max_interactions = 20 if child_age < 8 else 30
                if interaction_data["daily_interactions"] > max_interactions:
                    safety_checks["frequency_normal"] = False
                    violations.append("excessive_frequency")

            return {
                "safety_checks": safety_checks,
                "violations": violations,
                "is_safe": len(violations) == 0,
                "safety_score": max(0, 100 - len(violations) * 10),
            }
        except Exception as e:
            logger.error(f"Error validating interaction safety: {e}")
            return {
                "safety_checks": {},
                "violations": [],
                "is_safe": True,
                "safety_score": 100,
            }


class PrivacyProtectionManager:
    """Privacy protection manager."""

    @staticmethod
    def validate_data_sharing(data: dict[str, Any], child_age: int) -> dict[str, Any]:
        """Validate data sharing safety."""
        try:
            sensitive_fields = [
                "full_name",
                "address",
                "phone",
                "email",
                "school",
                "location",
                "personal_info",
            ]

            violations = []
            protected_data = {}

            for field, value in data.items():
                if field in sensitive_fields:
                    if child_age < 13:
                        violations.append(f"sharing_{field}_under_13")
                        protected_data[field] = "PROTECTED"
                    else:
                        protected_data[field] = value
                else:
                    protected_data[field] = value

            return {
                "protected_data": protected_data,
                "violations": violations,
                "sharing_allowed": len(violations) == 0,
                "coppa_compliant": child_age >= 13 or len(violations) == 0,
            }
        except Exception as e:
            logger.error(f"Error validating data sharing: {e}")
            return {
                "protected_data": data,
                "violations": [],
                "sharing_allowed": True,
                "coppa_compliant": True,
            }

    @staticmethod
    def anonymize_child_data(data: dict[str, Any]) -> dict[str, Any]:
        """Anonymize child data."""
        try:
            anonymized = data.copy()

            # Hide sensitive fields
            sensitive_fields = [
                "name",
                "full_name",
                "address",
                "phone",
                "email",
            ]
            for field in sensitive_fields:
                if field in anonymized:
                    anonymized[field] = f"ANONYMIZED_{field.upper()}"

            # Add anonymous identifier
            anonymized["anonymous_id"] = f"anon_{hash(str(data))}"
            anonymized["anonymized_at"] = datetime.now().isoformat()

            return anonymized
        except Exception as e:
            logger.error(f"Error anonymizing child data: {e}")
            return data


class UsageMonitor:
    """Usage monitor."""

    @staticmethod
    async def track_usage(
        child_id: str,
        activity_type: str,
        duration: int,
    ) -> dict[str, Any]:
        """Track child usage."""
        try:
            usage_record = {
                "child_id": child_id,
                "activity_type": activity_type,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot track usage. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for track_usage.")

            # Record usage in database
            db_service = get_database_service()
            await db_service.record_usage(usage_record)

            # Check usage limits
            daily_usage = await db_service.get_daily_usage(child_id)
            if daily_usage > 120:  # More than 2 hours
                await ChildSafetyManager.record_safety_event(
                    child_id,
                    SafetyEventTypes.EXCESSIVE_USAGE,
                    {"daily_usage": daily_usage, "limit": 120},
                )

            return usage_record
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_usage_statistics(child_id: str, days: int = 7) -> dict[str, Any]:
        """Get usage statistics."""
        try:

            if not DATABASE_AVAILABLE:
                logger.critical("Database service is not available. Cannot get usage statistics. This is a production-blocking error.")
                raise DatabaseNotAvailableError("Database connection not established for get_usage_statistics.")

            db_service = get_database_service()
            usage_stats = await db_service.get_usage_statistics(child_id, days)
            return usage_stats
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {"error": str(e)}


# Public interfaces for security operations
async def get_child_safety_summary(child_id: str) -> ChildSafetySummary:
    """Get child safety summary."""
    return await ChildSafetyManager.get_safety_summary(child_id)


async def record_safety_event(
    child_id: str,
    event_type: str,
    event_data: dict[str, Any],
) -> dict[str, Any]:
    """Record safety event."""
    return await ChildSafetyManager.record_safety_event(
        child_id,
        event_type,
        event_data,
    )


async def validate_interaction_safety(
    interaction_data: dict[str, Any],
    child_age: int,
) -> dict[str, Any]:
    """Validate interaction safety."""
    return ContentSafetyFilter.validate_interaction_safety(interaction_data, child_age)


async def track_child_usage(
    child_id: str,
    activity_type: str,
    duration: int,
) -> dict[str, Any]:
    """Track child usage."""
    return await UsageMonitor.track_usage(child_id, activity_type, duration)
