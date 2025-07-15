from datetime import datetime
from typing import Any, Dict, List

from src.presentation.api.endpoints.children.models import ChildResponse


def create_mock_child_response(
    child_id: str, name: str = "Mock Child", age: int = 7
) -> ChildResponse:
    """Create mock child response for testing purposes."""
    return ChildResponse(
        id=child_id,
        name=name,
        age=age,
        preferences={"favorite_color": "blue"},
        interests=["reading", "drawing"],
        language="en",
        created_at=datetime.now().isoformat(),
        parent_id="mock_parent",
    )


def create_mock_children_list(parent_id: str = "mock_parent") -> List[ChildResponse]:
    """Create mock children list for testing purposes."""
    return [
        ChildResponse(
            id="mock_child_1",
            name="Alice",
            age=6,
            preferences={"favorite_color": "blue"},
            interests=["animals", "stories"],
            language="en",
            created_at=datetime.now().isoformat(),
            parent_id=parent_id,
        ),
        ChildResponse(
            id="mock_child_2",
            name="Bob",
            age=8,
            preferences={"favorite_animal": "dog"},
            interests=["games", "music"],
            language="en",
            created_at=datetime.now().isoformat(),
            parent_id=parent_id,
        ),
    ]
