import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine

from cachetools import TTLCache

# A simple in-memory cache with a TTL of 5 minutes
_cache = TTLCache(maxsize=1024, ttl=300)


def cached(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator to cache the result of an async function."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(kwargs)
        if key in _cache:
            return _cache[key]

        result = await func(*args, **kwargs)
        _cache[key] = result
        return result

    return wrapper