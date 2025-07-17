from typing import Protocol, List, Optional
from uuid import UUID
from src.domain.entities.child_profile import ChildProfile


class ChildRepository(Protocol):
    async def save(self, child: ChildProfile) -> None:
        ...
    
    async def get_by_id(self, child_id: UUID) -> Optional[ChildProfile]:
        ...
    
    async def get_all(self) -> List[ChildProfile]:
        ...
    
    async def delete(self, child_id: UUID) -> None:
        ...