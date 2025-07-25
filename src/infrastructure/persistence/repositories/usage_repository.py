"""Usage Repository.

Handles all usage statistics and analytics database operations.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.validators.security.database_input_validator import (
    SecurityError,
    database_input_validation,
    validate_database_operation,
)

logger = get_logger(__name__, component="persistence")


class UsageRepository:
    """Repository for usage statistics and analytics operations."""

    def __init__(self, database: Database) -> None:
        """Initialize usage repository.

        Args:
            database: Database instance

        """
        self.database = database
        logger.info("UsageRepository initialized")

    @database_input_validation("usage_statistics")
    async def record_usage(self, usage_record: dict[str, Any]) -> str:
        """Record usage statistics for a child.

        Args:
            usage_record: Usage data including child_id, activity_type, duration

        Returns:
            Usage record ID

        """
        try:
            required_fields = ["child_id", "activity_type", "duration"]
            for field in required_fields:
                if field not in usage_record:
                    raise ValueError(f"Missing required field: {field}")

            if usage_record["duration"] < 0:
                raise ValueError(
                    f"Duration cannot be negative: {usage_record['duration']}",
                )

            validated_operation = validate_database_operation(
                "INSERT",
                "usage_statistics",
                usage_record,
            )
            validated_data = validated_operation["data"]
            usage_id = str(uuid4())

            # Create complete usage record
            complete_record = {
                "usage_id": usage_id,
                "child_id": validated_data["child_id"],
                "activity_type": validated_data["activity_type"],
                "duration": validated_data["duration"],
                "timestamp": datetime.utcnow(),
            }

            # In a real implementation, this would be saved to a database
            logger.info(f"Usage recorded: {complete_record}")
            return usage_id
        except (ValueError, SecurityError) as e:
            logger.error(f"Error recording usage: {e}")
            raise ValueError(f"Invalid usage data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error recording usage: {e}")
            raise

    @database_input_validation("usage_statistics")
    async def get_usage_summary(self, child_id: str, days: int = 30) -> dict[str, Any]:
        """Get usage summary for a child over a period (production implementation).

        Args:
            child_id: Child ID
            days: Number of days to summarize

        Returns:
            Dictionary with usage summary
        """
        try:
            # استعلام فعلي من قاعدة البيانات لجلب سجلات الاستخدام
            query = (
                "SELECT activity_type, SUM(duration) as total_duration "
                "FROM usage_statistics "
                "WHERE child_id = :child_id AND timestamp >= :since "
                "GROUP BY activity_type"
            )
            since = datetime.utcnow() - timedelta(days=days)
            params = {"child_id": child_id, "since": since}
            result = await self.database.fetch_all(query, params)
            if not result:
                return {
                    "child_id": child_id,
                    "total_duration_minutes": 0,
                    "most_common_activity": None,
                    "period_days": days,
                }
            total_duration = sum(row["total_duration"] for row in result)
            most_common_activity = max(
                result, key=lambda r: r["total_duration"]
            )["activity_type"]
        except (ValueError, TypeError):
            logger.exception("Error fetching usage summary")
            raise
        else:
            return {
                "child_id": child_id,
                "total_duration_minutes": total_duration,
                "most_common_activity": most_common_activity,
                "period_days": days,
            }
