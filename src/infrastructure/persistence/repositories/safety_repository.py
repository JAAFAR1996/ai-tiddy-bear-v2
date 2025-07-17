"""Safety Repository.

Handles all safety-related database operations including events, alerts, and scores.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.database_input_validator import (
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
                f"Safety Event {event_id}: Child={child_id}, "
                f"Type={event_type}, Severity={severity}, Details={details}",
            )
            return event_id
        except SecurityError as e:
            logger.error(f"Security error recording safety event: {e}")
            raise ValueError("Invalid data for safety event")
        except Exception as e:
            logger.error(f"Error recording safety event: {e}")
            raise

    @database_input_validation("safety_alerts")
    async def get_safety_alerts(self, child_id: str) -> list[dict[str, Any]]:
        """Get safety alerts for a child.

        Args:
            child_id: Child ID

        Returns:
            List of safety alerts

        """
        # This is a mock implementation
        logger.info(f"Fetching safety alerts for child {child_id}")
        return [
            {
                "alert_id": str(uuid4()),
                "child_id": child_id,
                "alert_type": "inappropriate_language",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "unresolved",
            },
        ]

    @database_input_validation("safety_scores")
    async def get_child_safety_score(self, child_id: str) -> float:
        """Calculate and retrieve a safety score for a child.

        Args:
            child_id: Child ID

        Returns:
            Safety score between 0.0 and 1.0

        """
        # Mock implementation
        logger.info(f"Calculating safety score for child {child_id}")
        return 0.95
