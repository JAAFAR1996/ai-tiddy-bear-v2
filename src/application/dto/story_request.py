from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

try:
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError("Pydantic is required for production validation - install with: pip install pydantic") from e

@dataclass
class StoryRequest:
    child_id: UUID
    theme: Optional[str] = None
    characters: Optional[List[str]] = None
    setting: Optional[str] = None
    moral_lesson: Optional[str] = None
    story_length: Optional[str] = "medium"