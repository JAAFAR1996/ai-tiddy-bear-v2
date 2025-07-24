"""Pydantic models for children endpoints.

This module defines the request/response models used by the children API endpoints.
These models provide validation, serialization, and API documentation through
FastAPI and Pydantic integration.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ChildCreateRequest(BaseModel):
    """Request model for creating a new child profile."""

    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    age: int = Field(..., ge=0, le=17, description="Child's age (0-17 years)")
    preferences: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Child preferences and settings"
    )
    parental_consent: bool = Field(
        ...,
        description="Confirmation of parental consent (required for COPPA compliance)",
    )

    @validator("name")
    def validate_name(cls, v):
        """Validate name contains only letters, spaces, and common punctuation."""
        if not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip()

    @validator("parental_consent")
    def validate_consent(cls, v):
        """Ensure parental consent is explicitly given."""
        if not v:
            raise ValueError("Parental consent is required for child account creation")
        return v


class ChildUpdateRequest(BaseModel):
    """Request model for updating an existing child profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=17)
    preferences: Optional[dict[str, Any]] = None

    @validator("name")
    def validate_name(cls, v):
        """Validate name if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or only whitespace")
        return v.strip() if v else v


class ChildResponse(BaseModel):
    """Response model for child profile operations."""

    child_id: UUID = Field(..., description="Unique child identifier")
    name: str = Field(..., description="Child's name")
    age: int = Field(..., description="Child's age")
    preferences: dict[str, Any] = Field(
        default_factory=dict, description="Child preferences and settings"
    )
    is_active: bool = Field(True, description="Whether the profile is active")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ChildDeleteResponse(BaseModel):
    """Response model for child profile deletion."""

    child_id: UUID = Field(..., description="ID of deleted child profile")
    message: str = Field(..., description="Deletion confirmation message")
    deleted_at: datetime = Field(..., description="Deletion timestamp")


class ChildSafetySummary(BaseModel):
    """Safety summary for a child profile."""

    child_id: UUID = Field(..., description="Child identifier")
    safety_score: float = Field(
        ..., ge=0.0, le=100.0, description="Overall safety score"
    )
    recent_interactions: int = Field(
        ..., ge=0, description="Number of recent interactions"
    )
    flagged_content_count: int = Field(
        ..., ge=0, description="Number of flagged content items"
    )
    last_safety_check: Optional[datetime] = Field(
        None, description="Last safety evaluation"
    )
    safety_alerts: list[str] = Field(
        default_factory=list, description="Active safety alerts"
    )
    compliance_status: str = Field(..., description="COPPA compliance status")

    @classmethod
    def from_safety_events(
        cls, child_id: UUID, safety_events: list[dict]
    ) -> "ChildSafetySummary":
        """Create safety summary from safety events data."""
        # Calculate safety metrics from events
        total_events = len(safety_events)
        flagged_events = [e for e in safety_events if e.get("flagged", False)]

        # Calculate safety score (simple implementation)
        if total_events == 0:
            safety_score = 100.0
        else:
            safety_score = max(0.0, 100.0 - (len(flagged_events) / total_events * 50))

        # Extract alerts
        alerts = [
            e.get("alert_message", "") for e in flagged_events if e.get("alert_message")
        ]

        # Find most recent event
        last_check = None
        if safety_events:
            timestamps = [
                e.get("timestamp") for e in safety_events if e.get("timestamp")
            ]
            if timestamps:
                last_check = max(timestamps)

        return cls(
            child_id=child_id,
            safety_score=safety_score,
            recent_interactions=total_events,
            flagged_content_count=len(flagged_events),
            last_safety_check=last_check,
            safety_alerts=alerts,
            compliance_status="compliant" if safety_score >= 80.0 else "needs_review",
        )


class ChildProfileModel(BaseModel):
    """Comprehensive child profile model with all details."""

    child_id: UUID = Field(..., description="Unique child identifier")
    name: str = Field(..., description="Child's name")
    age: int = Field(..., description="Child's age")
    preferences: dict[str, Any] = Field(default_factory=dict)
    personality_traits: list[str] = Field(default_factory=list)
    learning_preferences: dict[str, float] = Field(default_factory=dict)
    communication_style: Optional[str] = None
    max_daily_interaction_time: Optional[int] = Field(
        None, description="Maximum daily interaction time in seconds"
    )
    allowed_topics: list[str] = Field(default_factory=list)
    restricted_topics: list[str] = Field(default_factory=list)
    language_preference: str = Field(
        default="en", description="Preferred language code"
    )
    cultural_background: Optional[str] = None
    parental_controls: dict[str, Any] = Field(default_factory=dict)
    educational_level: Optional[str] = None
    special_needs: list[str] = Field(default_factory=list)
    is_active: bool = Field(True, description="Whether profile is active")
    privacy_settings: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(..., description="Profile creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class InteractionModel(BaseModel):
    """Model representing a child-AI interaction."""

    interaction_id: UUID = Field(..., description="Unique interaction identifier")
    child_id: UUID = Field(..., description="Child who participated")
    conversation_id: Optional[UUID] = Field(None, description="Associated conversation")
    interaction_type: str = Field(..., description="Type of interaction")
    content_summary: str = Field(..., description="Summary of interaction content")
    duration_seconds: Optional[int] = Field(None, description="Interaction duration")
    safety_flags: list[str] = Field(default_factory=list, description="Safety concerns")
    emotional_context: Optional[dict[str, Any]] = Field(
        None, description="Emotional analysis data"
    )
    learning_outcomes: list[str] = Field(
        default_factory=list, description="Educational outcomes achieved"
    )
    timestamp: datetime = Field(..., description="When interaction occurred")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class SafetyConfigModel(BaseModel):
    """Model for child safety configuration settings."""

    config_id: UUID = Field(..., description="Unique configuration identifier")
    child_id: UUID = Field(..., description="Associated child profile")
    content_filters: dict[str, bool] = Field(
        default_factory=dict, description="Content filtering settings"
    )
    interaction_limits: dict[str, int] = Field(
        default_factory=dict, description="Time and frequency limits"
    )
    allowed_topics: list[str] = Field(
        default_factory=list, description="Topics child can discuss"
    )
    restricted_topics: list[str] = Field(
        default_factory=list, description="Topics to avoid"
    )
    emergency_contacts: list[dict[str, str]] = Field(
        default_factory=list, description="Emergency contact information"
    )
    monitoring_level: str = Field(
        default="standard", description="Level of safety monitoring"
    )
    alert_thresholds: dict[str, float] = Field(
        default_factory=dict, description="Thresholds for safety alerts"
    )
    auto_escalation: bool = Field(
        True, description="Whether to auto-escalate safety concerns"
    )
    last_updated: datetime = Field(..., description="Last configuration update")

    @validator("monitoring_level")
    def validate_monitoring_level(cls, v):
        """Validate monitoring level is recognized."""
        valid_levels = ["minimal", "standard", "enhanced", "strict"]
        if v not in valid_levels:
            raise ValueError(f"Monitoring level must be one of: {valid_levels}")
        return v

    class Config:
        """Pydantic configuration."""

        from_attributes = True
