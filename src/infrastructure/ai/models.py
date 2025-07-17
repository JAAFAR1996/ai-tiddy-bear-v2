from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    content: str
    safety_score: float
    age_appropriate: bool
    sentiment: str
    topics: list[str]
    processing_time: float
    cached: bool
    moderation_flags: list[str]
    response_type: str
    emotion: str


class ConversationContext(BaseModel):
    previous_messages: list[str] = Field(default_factory=list)
    child_preferences: dict = Field(default_factory=dict)
