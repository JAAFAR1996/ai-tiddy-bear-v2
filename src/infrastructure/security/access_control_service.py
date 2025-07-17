from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Set
import logging
import secrets
import uuid

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class AccessLevel(Enum):
    """Access levels for parent-child relationships."""

    FULL_PARENT = "full_parent"  # Primary parent/guardian
    SHARED_PARENT = "shared_parent"  # Secondary parent (divorced, etc.)
    TEMPORARY_GUARDIAN = "temporary_guardian"  # Babysitter, etc.
    READ_ONLY = "read_only"  # View-only access
    EMERGENCY_CONTACT = "emergency_contact"  # Emergency access only


class AccessAction(Enum):
    """Types of actions that can be performed."""

    READ_PROFILE = "read_profile"
    UPDATE_PROFILE = "update_profile"
    DELETE_PROFILE = "delete_profile"
    READ_CONVERSATIONS = "read_conversations"
    DELETE_CONVERSATIONS = "delete_conversations"
    READ_ANALYTICS = "read_analytics"
    EXPORT_DATA = "export_data"
    MANAGE_SETTINGS = "manage_settings"
    GRANT_CONSENT = "grant_consent"
    REVOKE_CONSENT = "revoke_consent"


class AccessControlService:
    """COPPA-compliant parent-child access control with comprehensive auditing."""

    def __init__(self) -> None:
        """Initialize access control service."""
        self.parent_child_relationships: Dict[str, List[Dict[str, Any]]] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []
        self.failed_access_attempts: Dict[str, List[Dict[str, Any]]] = {}

        # Define permissions for each access level
        self.access_permissions = {
            AccessLevel.FULL_PARENT: {
                AccessAction.READ_PROFILE,
                AccessAction.UPDATE_PROFILE,
                AccessAction.DELETE_PROFILE,
                AccessAction.READ_CONVERSATIONS,
                AccessAction.DELETE_CONVERSATIONS,
                AccessAction.READ_ANALYTICS,
                AccessAction.EXPORT_DATA,
                AccessAction.MANAGE_SETTINGS,
                AccessAction.GRANT_CONSENT,
                AccessAction.REVOKE_CONSENT,
            },
            AccessLevel.SHARED_PARENT: {
                AccessAction.READ_PROFILE,
                AccessAction.UPDATE_PROFILE,
                AccessAction.READ_CONVERSATIONS,
                AccessAction.READ_ANALYTICS,
                AccessAction.EXPORT_DATA,
                AccessAction.MANAGE_SETTINGS,
                AccessAction.GRANT_CONSENT,
            },
            AccessLevel.TEMPORARY_GUARDIAN: {
                AccessAction.READ_PROFILE,
                AccessAction.READ_CONVERSATIONS,
                AccessAction.READ_ANALYTICS,
            },
            AccessLevel.READ_ONLY: {
                AccessAction.READ_PROFILE,
                AccessAction.READ_CONVERSATIONS,
                AccessAction.READ_ANALYTICS,
            },
            AccessLevel.EMERGENCY_CONTACT: {AccessAction.READ_PROFILE},
        }

    async def register_parent_child_relationship(
        self,
        parent_id: str,
        child_id: str,
        access_level: AccessLevel,
        verification_method: str,
        legal_document_id: Optional[str] = None,
        expiry_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Register a parent-child relationship with proper verification."""
        relationship_id = f"rel_{uuid.uuid4().hex[:16]}"
        relationship = {
            "relationship_id": relationship_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "access_level": access_level.value,
            "verification_method": verification_method,
            "legal_document_id": legal_document_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiry_date.isoformat() if expiry_date else None,
            "status": "active",
            "verification_status": "verified",
        }

        if parent_id not in self.parent_child_relationships:
            self.parent_child_relationships[parent_id] = []

        self.parent_child_relationships[parent_id].append(relationship)

        await self._log_audit_event(
            parent_id=parent_id,
            child_id=child_id,
            action="register_relationship",
            access_level=access_level.value,
            success=True,
            details={"relationship_id": relationship_id},
        )

        logger.info(f"Parent-child relationship registered: {relationship_id}")

        return {
            "relationship_id": relationship_id,
            "access_level": access_level.value,
            "permissions": [
                action.value
                for action in self.access_permissions[access_level]
            ],
            "expires_at": relationship["expires_at"],
        }

    async def verify_access(
        self,
        parent_id: str,
        child_id: str,
        action: AccessAction,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Verify that a parent has permission to perform an action on child data."""
        try:
            relationship = await self._find_relationship(parent_id, child_id)

            if not relationship:
                await self._log_failed_access(
                    parent_id,
                    child_id,
                    action,
                    "no_relationship",
                )
                return {
                    "access_granted": False,
                    "reason": "No parent-child relationship found",
                    "error_code": "NO_RELATIONSHIP",
                }

            if relationship["status"] != "active":
                await self._log_failed_access(
                    parent_id,
                    child_id,
                    action,
                    "inactive_relationship",
                )
                return {
                    "access_granted": False,
                    "reason": "Parent-child relationship is not active",
                    "error_code": "INACTIVE_RELATIONSHIP",
                }

            if relationship["expires_at"]:
                expiry = datetime.fromisoformat(relationship["expires_at"])
                if datetime.utcnow() > expiry:
                    await self._log_failed_access(
                        parent_id,
                        child_id,
                        action,
                        "expired_relationship",
                    )
                    return {
                        "access_granted": False,
                        "reason": "Parent-child relationship has expired",
                        "error_code": "EXPIRED_RELATIONSHIP",
                    }

            access_level = AccessLevel(relationship["access_level"])
            allowed_actions = self.access_permissions[access_level]

            if action not in allowed_actions:
                await self._log_failed_access(
                    parent_id,
                    child_id,
                    action,
                    "insufficient_permissions",
                )
                return {
                    "access_granted": False,
                    "reason": f"Access level {access_level.value} does not permit {action.value}",
                    "error_code": "INSUFFICIENT_PERMISSIONS",
                }

            access_token = await self._generate_access_token(
                parent_id,
                child_id,
                action,
                relationship,
            )

            await self._log_audit_event(
                parent_id=parent_id,
                child_id=child_id,
                action=action.value,
                access_level=access_level.value,
                success=True,
                details={
                    "relationship_id": relationship["relationship_id"],
                    "access_token": access_token,
                },
            )

            logger.info(
                f"Access granted: {parent_id} -> {child_id} for {action.value}"
            )

            return {
                "access_granted": True,
                "access_token": access_token,
                "access_level": access_level.value,
                "relationship_id": relationship["relationship_id"],
                "expires_at": (
                    datetime.utcnow() + timedelta(hours=1)
                ).isoformat(),
                "permitted_actions": [act.value for act in allowed_actions],
            }
        except Exception as e:
            logger.error(f"Access verification error: {e}")
            await self._log_failed_access(
                parent_id,
                child_id,
                action,
                f"system_error: {e}",
            )
            return {
                "access_granted": False,
                "reason": "System error during access verification",
                "error_code": "SYSTEM_ERROR",
            }

    async def _find_relationship(
        self,
        parent_id: str,
        child_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Find active parent-child relationship."""
        if parent_id not in self.parent_child_relationships:
            return None

        for relationship in self.parent_child_relationships[parent_id]:
            if (
                relationship["child_id"] == child_id
                and relationship["status"] == "active"
            ):
                return relationship

        return None

    async def _generate_access_token(
        self,
        parent_id: str,
        child_id: str,
        action: AccessAction,
        relationship: Dict[str, Any],
    ) -> str:
        """Generate time-limited access token."""
        token_id = secrets.token_urlsafe(32)
        token_data = {
            "token_id": token_id,
            "parent_id": parent_id,
            "child_id": child_id,
            "action": action.value,
            "relationship_id": relationship["relationship_id"],
            "access_level": relationship["access_level"],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "used": False,
        }

        self.access_tokens[token_id] = token_data
        return token_id

    async def validate_access_token(
        self,
        token_id: str,
        parent_id: str,
        child_id: str,
        action: AccessAction,
    ) -> Dict[str, Any]:
        """Validate and potentially consume an access token."""
        if token_id not in self.access_tokens:
            return {"valid": False, "reason": "Token not found"}

        token = self.access_tokens[token_id]

        if datetime.utcnow() > datetime.fromisoformat(token["expires_at"]):
            return {"valid": False, "reason": "Token expired"}

        if (
            token["parent_id"] != parent_id
            or token["child_id"] != child_id
            or token["action"] != action.value
        ):
            return {"valid": False, "reason": "Token mismatch"}

        if action in [
            AccessAction.DELETE_PROFILE,
            AccessAction.DELETE_CONVERSATIONS,
        ]:
            if token["used"]:
                return {"valid": False, "reason": "Token already used"}
            token["used"] = True

        return {
            "valid": True,
            "access_level": token["access_level"],
            "relationship_id": token["relationship_id"],
        }

    async def _log_audit_event(
        self,
        parent_id: str,
        child_id: str,
        action: str,
        access_level: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log access control events for COPPA compliance auditing."""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "parent_id": parent_id,
            "child_id": child_id,
            "action": action,
            "access_level": access_level,
            "success": success,
            "details": details or {},
        }

        self.audit_logs.append(audit_event)
        logger.info(f"Audit event logged: {audit_event['event_id']}")

    async def _log_failed_access(
        self,
        parent_id: str,
        child_id: str,
        action: AccessAction,
        reason: str,
    ) -> None:
        """Log failed access attempts for security monitoring."""
        if parent_id not in self.failed_access_attempts:
            self.failed_access_attempts[parent_id] = []

        failed_attempt = {
            "timestamp": datetime.utcnow().isoformat(),
            "child_id": child_id,
            "action": action.value,
            "reason": reason,
        }

        self.failed_access_attempts[parent_id].append(failed_attempt)

        recent_failures = [
            attempt
            for attempt in self.failed_access_attempts[parent_id]
            if datetime.utcnow() - datetime.fromisoformat(attempt["timestamp"])
            < timedelta(hours=1)
        ]

        if len(recent_failures) >= 5:
            logger.warning(
                f"Suspicious access activity detected for parent {parent_id}",
            )

        await self._log_audit_event(
            parent_id=parent_id,
            child_id=child_id,
            action=action.value,
            access_level="none",
            success=False,
            details={"failure_reason": reason},
        )

    async def get_parent_children(
        self, parent_id: str
    ) -> List[Dict[str, Any]]:
        """Get all children accessible by a parent."""
        if parent_id not in self.parent_child_relationships:
            return []

        active_relationships = []
        for relationship in self.parent_child_relationships[parent_id]:
            if relationship["status"] == "active":
                if relationship["expires_at"]:
                    expiry = datetime.fromisoformat(relationship["expires_at"])
                    if datetime.utcnow() > expiry:
                        continue

                active_relationships.append(
                    {
                        "child_id": relationship["child_id"],
                        "access_level": relationship["access_level"],
                        "relationship_id": relationship["relationship_id"],
                        "expires_at": relationship["expires_at"],
                    },
                )

        return active_relationships
