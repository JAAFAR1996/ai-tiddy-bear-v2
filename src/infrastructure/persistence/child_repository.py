from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.child import Child


class ChildRepository(ABC):
    @abstractmethod
    async def add(self, child: Child) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, child_id: str) -> Optional[Child]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Child]:
        pass

    @abstractmethod
    async def update(self, child: Child) -> None:
        pass

    @abstractmethod
    async def delete(self, child_id: str) -> None:
        pass