from typing import Protocol
from uuid import UUID

from src.domain.entities.child_profile import ChildProfile


class ChildRepository(Protocol):
    async def save(self, child: ChildProfile) -> None: ...

    async def get_by_id(self, child_id: UUID) -> ChildProfile | None: ...

    async def get_all(self) -> list[ChildProfile]: ...

    async def delete(self, child_id: UUID) -> None: ...
