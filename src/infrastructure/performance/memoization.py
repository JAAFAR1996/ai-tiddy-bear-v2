from typing import Any, Callable, Dict


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """A simple memoization decorator."""
    cache: Dict[Any, Any] = {}

    def wrapper(*args: Any) -> Any:
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return wrapper