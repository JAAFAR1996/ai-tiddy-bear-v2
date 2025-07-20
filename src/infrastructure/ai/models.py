from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    previous_messages: list[str] = Field(default_factory=list)
    child_preferences: dict = Field(default_factory=dict)
