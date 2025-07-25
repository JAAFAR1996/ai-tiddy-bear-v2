from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.application.interfaces.read_model_interfaces import (
    IChildProfileReadModel,
    IChildProfileReadModelStore,
)


@dataclass
class ChildProfileReadModel(IChildProfileReadModel):
    """Concrete implementation of child profile read model."""

    _id: UUID
    _name: str
    _age: int
    _preferences: dict[str, Any]

    @property
    def id(self) -> str:
        """Child identifier."""
        return str(self._id)

    @property
    def name(self) -> str:
        """Child name."""
        return self._name

    @property
    def age(self) -> int:
        """Child age."""
        return self._age

    @property
    def preferences(self) -> dict[str, Any]:
        """Child preferences."""
        return self._preferences


class ChildProfileReadModelStore(IChildProfileReadModelStore):
    """Concrete implementation of child profile read model store."""

    def __init__(self) -> None:
        self._store: dict[UUID, ChildProfileReadModel] = {}

    async def get_by_id(self, child_id: str) -> IChildProfileReadModel | None:
        """Get child profile by ID."""
        try:
            uuid_id = UUID(child_id)
            return self._store.get(uuid_id)
        except ValueError:
            return None

    async def save(self, model: IChildProfileReadModel) -> None:
        """Save child profile read model."""
        if isinstance(model, ChildProfileReadModel):
            self._store[model._id] = model
        else:
            # Convert interface to concrete implementation
            concrete_model = ChildProfileReadModel(
                _id=UUID(model.id),
                _name=model.name,
                _age=model.age,
                _preferences=model.preferences,
            )
            self._store[concrete_model._id] = concrete_model

    async def delete_by_id(self, child_id: str) -> bool:
        """Delete child profile by ID."""
        try:
            uuid_id = UUID(child_id)
            if uuid_id in self._store:
                del self._store[uuid_id]
                return True
            return False
        except ValueError:
            return False

    async def update(self, child_id: str, updates: dict[str, Any]) -> bool:
        """Update child profile."""
        try:
            uuid_id = UUID(child_id)
            if uuid_id in self._store:
                profile = self._store[uuid_id]
                # Update preferences or other mutable fields
                if "preferences" in updates:
                    profile._preferences.update(updates["preferences"])
                if "name" in updates:
                    profile._name = updates["name"]
                if "age" in updates:
                    profile._age = updates["age"]
                return True
            return False
        except ValueError:
            return False

    def get_all(self) -> list[ChildProfileReadModel]:
        """Get all child profiles (convenience method)."""
        return list(self._store.values())
