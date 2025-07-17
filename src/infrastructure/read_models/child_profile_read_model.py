from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class ChildProfileReadModel:
    id: UUID
    name: str
    age: int
    preferences: dict[str, Any]


class ChildProfileReadModelStore:
    def __init__(self) -> None:
        self._store: dict[UUID, ChildProfileReadModel] = {}

    def get_by_id(self, child_id: UUID) -> ChildProfileReadModel | None:
        return self._store.get(child_id)

    def save(self, child_profile: ChildProfileReadModel) -> None:
        self._store[child_profile.id] = child_profile

    def delete(self, child_id: UUID) -> None:
        if child_id in self._store:
            del self._store[child_id]

    def get_all(self) -> list[ChildProfileReadModel]:
        return list(self._store.values())
