from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.logging_config import get_logger
from src.presentation.api.validators import ChildValidationMixin

logger = get_logger(__name__, component="api")

"""Data models for child API endpoints.
This module defines Pydantic models for child profile creation, updates,
and responses with comprehensive validation and COPPA compliance."""

DEFAULT_LANGUAGE = "en"


class ChildPreferences(BaseModel):
    """Model for child-specific preferences, ensuring structured data."""

    favorite_color: str | None = Field(None, max_length=50)
    favorite_animal: str | None = Field(None, max_length=50)
    story_preferences: list[str] | None = Field(None, max_items=10)
    model_config = ConfigDict(from_attributes=True)


class ChildCreateRequest(ChildValidationMixin, BaseModel):
    """Request model for creating a new child profile."""

    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=1, le=13)
    preferences: ChildPreferences = Field(default_factory=ChildPreferences)
    interests: list[str] = Field(default_factory=list)
    language: str = Field(default=DEFAULT_LANGUAGE)


class ChildUpdateRequest(ChildValidationMixin, BaseModel):
    """Request model for updating child profile data."""

    model_config = ConfigDict(from_attributes=True)
    name: str | None = Field(None, min_length=1, max_length=50)
    age: int | None = Field(None, ge=1, le=13)
    preferences: ChildPreferences | None = None
    interests: list[str] | None = None
    language: str | None = None


class ChildResponse(BaseModel):
    """Response model for child profile data."""

    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    age: int
    preferences: ChildPreferences
    interests: list[str]
    language: str
    created_at: datetime  # Use datetime object directly
    parent_id: str


class ChildSafetySummary(BaseModel):
    """Model for child safety summary data."""

    child_id: str
    safety_events: int
    content_filtered: int
    last_interaction: str
    safety_score: int
    recent_events: list[dict[str, Any]] | None = None

    @classmethod
    def create_mock(cls, child_id: str) -> "ChildSafetySummary":
        """Create mock safety summary for testing purposes."""
        return cls(
            child_id=child_id,
            safety_events=0,
            content_filtered=2,
            last_interaction=datetime.now().isoformat(),
            safety_score=95,
            recent_events=[],
        )

    @classmethod
    def from_safety_events(
        cls,
        child_id: str,
        safety_events: list[dict[str, Any]],
    ) -> "ChildSafetySummary":
        """Create safety summary from safety events data."""
        safety_score = max(0, 100 - len(safety_events) * 5)
        content_filtered = len(
            [
                e
                for e in safety_events
                if e.get("event_type") == "content_filter"
            ],
        )
        return cls(
            child_id=child_id,
            safety_events=len(safety_events),
            content_filtered=content_filtered,
            last_interaction=datetime.now().isoformat(),
            safety_score=safety_score,
            recent_events=safety_events[:5],  # Latest 5 events
        )


class ChildDeleteResponse(BaseModel):
    """Response model for child deletion operations."""

    message: str
    child_id: str
    deleted_at: str

    @classmethod
    def create_success(cls, child_id: str) -> "ChildDeleteResponse":
        """Create successful deletion response."""
        return cls(
            message="Child and all associated data deleted successfully",
            child_id=child_id,
            deleted_at=datetime.now().isoformat(),
        )
