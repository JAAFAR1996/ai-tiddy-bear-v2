from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoryRequest:
    child_id: UUID
    theme: str | None = None
    characters: list[str] | None = None
    setting: str | None = None
    moral_lesson: str | None = None
    story_length: str | None = "medium"
