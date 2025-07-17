from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from src.domain.repositories.child_repository import ChildRepository
    from src.domain.repositories.event_store import EventStore

try:
    from fastapi import Depends
except ImportError:
    # Mock FastAPI Depends when not available
    def Depends(*args, **kwargs):
        return lambda func: func


from src.domain.repositories.event_store import EventStore, InMemoryEventStore
from src.infrastructure.repositories.event_sourced_child_repository import (
    EventSourcedChildRepository,
)


def get_event_store() -> "EventStore":
    # In a real application, this would be a singleton or managed by a DI container
    return InMemoryEventStore()


def get_child_repository(
    event_store: "EventStore" = Depends(get_event_store),
) -> "ChildRepository":
    return EventSourcedChildRepository(event_store)


# Mock implementations for missing dependencies
class MockManageChildProfileUseCase:
    """Mock manage child profile use case."""
    
    async def create_child_profile(
        self,
        name: str,
        age: int,
        preferences: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "id": "mock-id",
            "name": name,
            "age": age,
            "preferences": preferences,
        }

    async def get_child_profile(self, child_id: str) -> Dict[str, Any]:
        return {
            "id": str(child_id),
            "name": "Mock Child",
            "age": 5,
            "preferences": {},
        }

    async def update_child_profile(
        self,
        child_id: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "id": str(child_id),
            "name": name or "Mock Child",
            "age": age or 5,
            "preferences": preferences or {},
        }

    async def delete_child_profile(self, child_id: str) -> bool:
        return True


class MockGenerateDynamicStoryUseCase:
    """Mock generate dynamic story use case."""
    
    async def generate_story(self, child_id: str, prompt: str) -> Dict[str, Any]:
        return {
            "story_id": "story-123",
            "title": "The Mock Adventure",
            "content": f"A story about {prompt}",
        }


def get_manage_child_profile_use_case() -> MockManageChildProfileUseCase:
    """Get mock manage child profile use case."""
    return MockManageChildProfileUseCase()


def get_generate_dynamic_story_use_case() -> MockGenerateDynamicStoryUseCase:
    """Get mock generate dynamic story use case."""
    return MockGenerateDynamicStoryUseCase()