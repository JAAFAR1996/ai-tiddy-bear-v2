from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class PaginationService:
    @staticmethod
    def paginate(
        items: list[T],
        page: int,
        size: int,
        total: int | None = None,
    ) -> PaginatedResponse[T]:
        if total is None:
            total = len(items)

        start = (page - 1) * size
        end = start + size
        paginated_items = items[start:end]

        return PaginatedResponse(
            items=paginated_items,
            total=total,
            page=page,
            size=size,
            has_next=end < total,
            has_prev=page > 1,
        )
