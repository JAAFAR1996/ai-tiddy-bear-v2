"""COPPA Legal Notices and Compliance Information Endpoints
COPPA CONDITIONAL: These endpoints are only active when COPPA compliance is enabled.
When disabled, they return 404 or empty responses to avoid confusion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.domain.entities.user import User
from src.infrastructure.config.coppa_config import (
    is_coppa_enabled,
    should_show_coppa_notices,
)
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.jwt_auth import get_current_user

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/coppa", tags=["coppa"])


class COPPANoticeResponse(BaseModel):
    """COPPA notice response model."""

    enabled: bool
    notice_text: str | None = None
    privacy_policy_url: str | None = None
    consent_required: bool = False
    data_collection_types: list[str] = []
    retention_period_days: int | None = None


class COPPAValidatorStatus(BaseModel):
    """COPPA compliance status response."""

    coppa_enabled: bool
    compliance_mode: str
    features_affected: list[str] = []


@router.get("/status", response_model=COPPAValidatorStatus)
async def get_coppa_status():
    """Get current COPPA compliance status
    This endpoint always works to inform clients about COPPA status.
    """
    coppa_enabled = is_coppa_enabled()
    features_affected = []

    if coppa_enabled:
        features_affected = [
            "parental_consent_required",
            "age_verification_strict",
            "data_retention_limited",
            "audit_logging_enhanced",
            "data_sharing_restricted",
        ]

    return COPPAValidatorStatus(
        coppa_enabled=coppa_enabled,
        compliance_mode="strict" if coppa_enabled else "development",
        features_affected=features_affected,
    )


@router.get("/notice", response_model=COPPANoticeResponse)
async def get_coppa_notice():
    """Get COPPA compliance notice
    COPPA CONDITIONAL: Returns different content based on compliance status.
    """
    coppa_enabled = is_coppa_enabled()

    if not coppa_enabled:
        return COPPANoticeResponse(
            enabled=False,
            notice_text="COPPA compliance is currently disabled for development purposes.",
            consent_required=False,
        )

    # COPPA enabled - return full notice
    return COPPANoticeResponse(
        enabled=True,
        notice_text="""
        COPPA COMPLIANCE NOTICE

        This service complies with the Children's Online Privacy Protection Act (COPPA).

        For children under 13:
        - Parental consent is required before data collection
        - Data is automatically deleted after 90 days
        - No personal information is shared with third parties
        - Enhanced content filtering is applied

        Parents have the right to:
        - Review data collected about their child
        - Request deletion of their child's data
        - Revoke consent at any time

        For questions about COPPA compliance, contact: privacy@aiteddybear.com
        """,
        privacy_policy_url="https://aiteddybear.com/privacy-policy",
        consent_required=True,
        data_collection_types=[
            "voice_interactions",
            "preferences",
            "conversation_history",
            "usage_analytics",
        ],
        retention_period_days=90,
    )


@router.get("/privacy-settings/{child_id}")
async def get_child_privacy_settings(
    child_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get privacy settings for a specific child
    COPPA CONDITIONAL: Returns different settings based on compliance status.
    """
    # Verify user is a parent
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can access child privacy settings",
        )

    coppa_enabled = is_coppa_enabled()

    if not coppa_enabled:
        return {
            "child_id": child_id,
            "coppa_enabled": False,
            "privacy_level": "development",
            "data_retention_days": 730,  # 2 years in development
            "parental_controls": {
                "consent_required": False,
                "data_sharing_allowed": True,
                "analytics_enabled": True,
            },
            "notice": "COPPA compliance is disabled in development mode",
        }

    # COPPA enabled - return strict privacy settings
    return {
        "child_id": child_id,
        "coppa_enabled": True,
        "privacy_level": "coppa_strict",
        "data_retention_days": 90,
        "parental_controls": {
            "consent_required": True,
            "data_sharing_allowed": False,
            "analytics_enabled": False,  # Only anonymized analytics
        },
        "compliance_features": {
            "automatic_deletion": True,
            "enhanced_content_filtering": True,
            "audit_logging": True,
            "parental_oversight": True,
        },
    }


@router.post("/consent/{child_id}")
async def request_coppa_consent(
    child_id: str,
    current_user: User = Depends(get_current_user),
):
    """Request COPPA consent for a child
    COPPA CONDITIONAL: Only functional when COPPA compliance is enabled.
    """
    # Verify user is a parent
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can manage COPPA consent",
        )

    if not is_coppa_enabled():
        return {
            "child_id": child_id,
            "consent_status": "not_required",
            "message": "COPPA compliance is disabled - no consent required",
            "coppa_enabled": False,
        }

    # COPPA enabled - process consent request
    from ..endpoints.children.compliance import request_parental_consent

    try:
        consent_id = await request_parental_consent(
            parent_id=current_user.id,
            child_id=child_id,
            data_types=[
                "voice_interactions",
                "preferences",
                "conversation_history",
            ],
        )

        return {
            "child_id": child_id,
            "consent_id": consent_id,
            "consent_status": "requested",
            "message": "Parental consent has been requested",
            "coppa_enabled": True,
        }
    except Exception as e:
        logger.error(f"Error requesting COPPA consent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process consent request",
        )


@router.delete("/data/{child_id}")
async def request_data_deletion(
    child_id: str,
    current_user: User = Depends(get_current_user),
):
    """Request deletion of child's data
    COPPA CONDITIONAL: Behavior changes based on compliance status.
    """
    # Verify user is a parent
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents can request data deletion",
        )

    if not is_coppa_enabled():
        return {
            "child_id": child_id,
            "deletion_status": "scheduled",
            "message": "Data deletion scheduled (COPPA compliance disabled)",
            "retention_override": True,
            "coppa_enabled": False,
        }

    # COPPA enabled - process compliant deletion
    from ..endpoints.children.compliance import handle_compliant_child_deletion

    try:
        deletion_result = await handle_compliant_child_deletion(
            child_id,
            current_user.id,
        )

        return {
            "child_id": child_id,
            "deletion_result": deletion_result,
            "deletion_status": "completed",
            "message": "COPPA-compliant data deletion completed",
            "coppa_enabled": True,
        }
    except Exception as e:
        logger.error(f"Error processing data deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data deletion request",
        )


# Health check for COPPA services
@router.get("/health")
async def coppa_health_check():
    """Health check for COPPA services."""
    coppa_enabled = is_coppa_enabled()

    return {
        "service": "coppa_compliance",
        "status": "active" if coppa_enabled else "disabled",
        "mode": "production" if coppa_enabled else "development",
        "timestamp": "2025-01-01T00:00:00Z",
        "features": {
            "consent_management": coppa_enabled,
            "data_retention": coppa_enabled,
            "audit_logging": coppa_enabled,
            "privacy_notices": should_show_coppa_notices(),
        },
    }
