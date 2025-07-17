from dataclasses import dataclass
from uuid import UUID

try:
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(
        "Pydantic is required for production validation - install with: pip install pydantic",
    ) from e


@dataclass
class StoryRequest:
    child_id: UUID
    theme: str | None = None
    characters: list[str] | None = None
    setting: str | None = None
    moral_lesson: str | None = None
    story_length: str | None = "medium"
