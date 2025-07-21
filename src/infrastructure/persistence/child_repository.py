from abc import ABC, abstractmethod

from src.domain.entities.child import Child


class ChildRepository(ABC):
    @abstractmethod
    async def add(self, child: Child) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, child_id: str) -> Child | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Child]:
        pass

    @abstractmethod
    async def update(self, child: Child) -> None:
        pass

    @abstractmethod
    async def delete(self, child_id: str) -> None:
        pass
