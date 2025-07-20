from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.child import Child

T = TypeVar("T")


class BatchLoader:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._cache: dict[str, Any] = {}

    async def load(
        self,
        key: str,
        loader_func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Any:
        if key not in self._cache:
            self._cache[key] = await loader_func()
        return self._cache[key]

    async def load_many(
        self,
        keys: list[str],
        loader_func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> dict[str, Any]:
        results = {}
        for key in keys:
            results[key] = await self.load(key, lambda: loader_func(key))
        return results


async def get_child_batch_loader(
    db: AsyncSession,
    child_ids: list[str],
) -> dict[str, Child]:
    children = await Child.get_by_ids(db, child_ids)
    return {child.id: child for child in children}
