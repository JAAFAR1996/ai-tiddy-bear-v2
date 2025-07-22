"""Real database-backed data retention service.

This service provides actual database operations for data retention
management, replacing dummy implementations with production-ready logic.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.child_models import ChildModel
from src.domain.models.conversation_models import ConversationModel
from src.domain.models.consent_models_infra import SafetyEventModel
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)


class DataRetentionService:
    """Real database service for data retention with COPPA compliance."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.default_retention_days = 90  # COPPA default

    async def schedule_data_deletion(
        self, 
        child_id: str, 
        deletion_date: datetime
    ) -> bool:
        """Schedule data deletion for a child profile.
        
        Args:
            child_id: Child identifier
            deletion_date: When to delete the data
            
        Returns:
            True if scheduling successful, False otherwise
        """
        try:
            # Verify child exists
            child = await self.db.scalar(
                select(ChildModel).where(ChildModel.id == child_id)
            )
            if not child:
                logger.warning(f"Child {child_id} not found for deletion scheduling")
                return False

            # Update child record with deletion schedule
            result = await self.db.execute(
                update(ChildModel)
                .where(ChildModel.id == child_id)
                .values(
                    data_retention_expires=deletion_date,
                    updated_at=datetime.now(UTC)
                )
            )
            
            if result.rowcount == 0:
                logger.error(f"Failed to update deletion schedule for child {child_id}")
                return False

            # Log the scheduling in safety events
            safety_event = SafetyEventModel(
                id=str(uuid.uuid4()),
                child_id=child_id,
                event_type="DATA_RETENTION_SCHEDULED",
                severity="INFO",
                description=f"Data deletion scheduled for {deletion_date.isoformat()}",
                metadata={
                    "scheduled_deletion": deletion_date.isoformat(),
                    "retention_policy": "COPPA_90_DAYS",
                    "trigger": "manual_scheduling"
                },
                occurred_at=datetime.now(UTC)
            )
            
            self.db.add(safety_event)
            await self.db.commit()
            
            logger.info(f"Data deletion scheduled for child {child_id} on {deletion_date}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Failed to schedule data deletion for child {child_id}: {e}")
            return False

    async def check_retention_compliance(self, child_id: str) -> dict[str, Any]:
        """Check retention compliance for a child's data.
        
        Args:
            child_id: Child identifier
            
        Returns:
            Dictionary with compliance status and details
        """
        try:
            # Get child record
            child = await self.db.scalar(
                select(ChildModel).where(ChildModel.id == child_id)
            )
            
            if not child:
                return {
                    "compliant": False,
                    "status": "child_not_found",
                    "child_id": child_id
                }

            now = datetime.now(UTC)
            created_at = child.created_at
            retention_expires = child.data_retention_expires
            
            # Calculate days since creation
            days_since_creation = (now - created_at).days
            
            # Check if retention period is set
            if not retention_expires:
                # Set default retention period if not set
                retention_expires = created_at + timedelta(days=self.default_retention_days)
                await self.db.execute(
                    update(ChildModel)
                    .where(ChildModel.id == child_id)
                    .values(data_retention_expires=retention_expires)
                )
                await self.db.commit()
            
            # Calculate days until expiry
            days_until_expiry = (retention_expires - now).days
            is_expired = retention_expires < now
            is_due_soon = days_until_expiry <= 7 and not is_expired
            
            # Get data counts for compliance report
            conversation_count = await self.db.scalar(
                select(func.count(ConversationModel.id))
                .where(ConversationModel.child_id == child_id)
            )
            
            safety_event_count = await self.db.scalar(
                select(func.count(SafetyEventModel.id))
                .where(SafetyEventModel.child_id == child_id)
            )
            
            compliance_status = {
                "compliant": not is_expired,
                "child_id": child_id,
                "retention_days": self.default_retention_days,
                "days_since_creation": days_since_creation,
                "days_until_expiry": days_until_expiry,
                "next_review": retention_expires.isoformat(),
                "status": "active" if not is_expired else "expired",
                "data_summary": {
                    "conversations": conversation_count or 0,
                    "safety_events": safety_event_count or 0,
                    "total_interactions": child.total_interactions
                },
                "warnings": []
            }
            
            if is_expired:
                compliance_status["warnings"].append("Data retention period has expired")
            elif is_due_soon:
                compliance_status["warnings"].append(f"Data retention expires in {days_until_expiry} days")
                
            return compliance_status
            
        except Exception as e:
            logger.exception(f"Error checking retention compliance for child {child_id}: {e}")
            return {
                "compliant": False,
                "status": "error",
                "child_id": child_id,
                "error": str(e)
            }

    async def execute_data_deletion(self, child_id: str) -> dict[str, Any]:
        """Execute immediate data deletion for a child.
        
        Args:
            child_id: Child identifier
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Start transaction
            deletion_results = {
                "child_id": child_id,
                "deleted_at": datetime.now(UTC).isoformat(),
                "items_deleted": {},
                "success": False
            }
            
            # Delete conversations and messages
            conversations_deleted = await self.db.execute(
                delete(ConversationModel).where(ConversationModel.child_id == child_id)
            )
            deletion_results["items_deleted"]["conversations"] = conversations_deleted.rowcount
            
            # Delete safety events
            safety_events_deleted = await self.db.execute(
                delete(SafetyEventModel).where(SafetyEventModel.child_id == child_id)
            )
            deletion_results["items_deleted"]["safety_events"] = safety_events_deleted.rowcount
            
            # Delete child profile (this will cascade to related data)
            child_deleted = await self.db.execute(
                delete(ChildModel).where(ChildModel.id == child_id)
            )
            deletion_results["items_deleted"]["child_profile"] = child_deleted.rowcount
            
            if child_deleted.rowcount == 0:
                deletion_results["error"] = "Child profile not found"
                return deletion_results
            
            await self.db.commit()
            deletion_results["success"] = True
            
            logger.info(f"Successfully deleted all data for child {child_id}: {deletion_results}")
            return deletion_results
            
        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Failed to delete data for child {child_id}: {e}")
            return {
                "child_id": child_id,
                "success": False,
                "error": str(e),
                "deleted_at": datetime.now(UTC).isoformat()
            }

    async def get_children_due_for_deletion(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """Get list of children whose data is due for deletion.
        
        Args:
            days_ahead: Number of days ahead to look for deletions
            
        Returns:
            List of children due for deletion
        """
        try:
            cutoff_date = datetime.now(UTC) + timedelta(days=days_ahead)
            
            children = await self.db.scalars(
                select(ChildModel)
                .where(
                    and_(
                        ChildModel.data_retention_expires.is_not(None),
                        ChildModel.data_retention_expires <= cutoff_date
                    )
                )
                .order_by(ChildModel.data_retention_expires)
            )
            
            due_for_deletion = []
            for child in children:
                days_until_deletion = (child.data_retention_expires - datetime.now(UTC)).days
                
                due_for_deletion.append({
                    "child_id": child.id,
                    "name_encrypted": child.name_encrypted,
                    "parent_id": child.parent_id,
                    "created_at": child.created_at.isoformat(),
                    "retention_expires": child.data_retention_expires.isoformat(),
                    "days_until_deletion": days_until_deletion,
                    "total_interactions": child.total_interactions,
                    "is_overdue": days_until_deletion < 0
                })
                
            return due_for_deletion
            
        except Exception as e:
            logger.exception(f"Error getting children due for deletion: {e}")
            return []

    async def extend_retention_period(
        self, 
        child_id: str, 
        additional_days: int,
        reason: str = "parental_request"
    ) -> bool:
        """Extend retention period for a child's data.
        
        Args:
            child_id: Child identifier
            additional_days: Number of additional days to extend
            reason: Reason for extension
            
        Returns:
            True if extension successful, False otherwise
        """
        try:
            child = await self.db.scalar(
                select(ChildModel).where(ChildModel.id == child_id)
            )
            
            if not child:
                logger.warning(f"Child {child_id} not found for retention extension")
                return False
            
            # Calculate new expiry date
            current_expiry = child.data_retention_expires or (
                child.created_at + timedelta(days=self.default_retention_days)
            )
            new_expiry = current_expiry + timedelta(days=additional_days)
            
            # Update retention expiry
            await self.db.execute(
                update(ChildModel)
                .where(ChildModel.id == child_id)
                .values(
                    data_retention_expires=new_expiry,
                    updated_at=datetime.now(UTC)
                )
            )
            
            # Log the extension
            safety_event = SafetyEventModel(
                id=str(uuid.uuid4()),
                child_id=child_id,
                event_type="DATA_RETENTION_EXTENDED",
                severity="INFO",
                description=f"Data retention extended by {additional_days} days",
                metadata={
                    "previous_expiry": current_expiry.isoformat(),
                    "new_expiry": new_expiry.isoformat(),
                    "additional_days": additional_days,
                    "reason": reason
                },
                occurred_at=datetime.now(UTC)
            )
            
            self.db.add(safety_event)
            await self.db.commit()
            
            logger.info(f"Extended retention for child {child_id} by {additional_days} days")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Failed to extend retention for child {child_id}: {e}")
            return False
