"""
AI Service Models - Response models for AI service operations
"""

from typing import List
from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """AI response model with safety validation"""

    content: str
    safety_score: float = Field(ge=0.0, le=1.0)
    age_appropriate: bool
    sentiment: str
    topics: List[str] = Field(default_factory=list)
    processing_time: float
    cached: bool = False
    moderation_flags: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration"""

        validate_assignment = True
        frozen = False
