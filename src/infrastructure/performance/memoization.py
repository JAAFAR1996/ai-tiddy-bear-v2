from collections.abc import Callable
from typing import Any


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """A simple memoization decorator."""
    cache: dict[Any, Any] = {}

    def wrapper(*args: Any) -> Any:
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return wrapper
