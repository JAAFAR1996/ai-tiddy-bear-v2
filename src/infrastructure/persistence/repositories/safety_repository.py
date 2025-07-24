"""Safety Repository.

Handles all safety-related database operations including events, alerts, and scores.
"""

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


class SafetyRepository:
    """Repository for safety-related database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize safety repository.

        Args:
            database: Database instance

        """
        self.database = database
        logger.info("SafetyRepository initialized")

    @database_input_validation("safety_events")
    async def record_safety_event(
        self,
        child_id: str,
        event_type: str,
        details: str,
        severity: str = "low",
    ) -> str:
        """Record a safety event in the database.

        Args:
            child_id: Child ID
            event_type: Type of safety event
            details: Event details
            severity: Event severity (low, medium, high)

        Returns:
            Event ID

        """
        try:
            event_data = {
                "child_id": child_id,
                "event_type": event_type,
                "details": details,
                "severity": severity,
            }
            validated_operation = validate_database_operation(
                "INSERT",
                "safety_events",
                event_data,
            )
            validated_operation["data"]
            event_id = str(uuid4())
            # In production, this would insert into safety_events table
            logger.warning(
                "Safety Event %s: Child=%s, Type=%s, Severity=%s, Details=%s",
                event_id,
                child_id,
                event_type,
                severity,
                details,
            )
        except SecurityError as err:
            logger.exception("Security error recording safety event")
            raise ValueError("Invalid data for safety event") from err
        except Exception as err:
            logger.exception("Error recording safety event")
            raise
        else:
            return event_id

    @database_input_validation("safety_alerts")
    async def get_safety_alerts(self, child_id: str) -> list[dict[str, Any]]:
        """Get safety alerts for a child (production implementation).

        Args:
            child_id: Child ID

        Returns:
            List of safety alerts
        """
        try:
            query = (
                "SELECT alert_id, child_id, alert_type, timestamp, status "
                "FROM safety_alerts "
                "WHERE child_id = :child_id "
                "ORDER BY timestamp DESC"
            )
            params = {"child_id": child_id}
            result = await self.database.fetch_all(query, params)
            return [dict(row) for row in result] if result else []
        except (ValueError, TypeError):
            logger.exception("Error fetching safety alerts")
            raise

    @database_input_validation("safety_scores")
    async def get_child_safety_score(self, child_id: str) -> float:
        """Calculate and retrieve a safety score for a child (production implementation).

        Args:
            child_id: Child ID

        Returns:
            Safety score between 0.0 and 1.0

        Raises:
            ValueError: If no score is found for the child.
        """
        try:
            query = "SELECT score FROM safety_scores WHERE child_id = :child_id ORDER BY timestamp DESC LIMIT 1"
            params = {"child_id": child_id}
            result = await self.database.fetch_one(query, params)
            if result and "score" in result:
                score = float(result["score"])
                logger.info(f"Fetched safety score for child {child_id}: {score}")
                return score
            else:
                logger.warning(f"No safety score found for child {child_id}")
                raise ValueError(f"No safety score found for child {child_id}")
        except Exception as e:
            logger.exception(f"Error fetching safety score for child {child_id}: {e}")
            raise
