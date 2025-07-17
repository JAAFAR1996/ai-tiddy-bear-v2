"""from typing import Dict, Any"""
"""Cache configuration and constants"""


class CacheConfig:
    """Cache configuration settings"""

    # Default TTL values (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    SESSION_TTL = 1800  # 30 minutes
    CHILD_DATA_TTL = 7200  # 2 hours
    AI_RESPONSE_TTL = 300  # 5 minutes
    SAFETY_CHECK_TTL = 60  # 1 minute

    # Cache key prefixes
    SESSION_PREFIX = "session:"
    CHILD_PREFIX = "child:"
    AI_RESPONSE_PREFIX = "ai_response:"
    SAFETY_PREFIX = "safety:"
    RATE_LIMIT_PREFIX = "rate_limit:"

    # Rate limiting defaults
    DEFAULT_RATE_LIMIT_WINDOW = 60  # 1 minute
    DEFAULT_RATE_LIMIT_MAX_REQUESTS = 60

    # Cache invalidation patterns
    INVALIDATION_PATTERNS = {
        "child_update": ["child:*", "safety:*"],
        "session_logout": ["session:*"],
        "safety_event": ["safety:*", "ai_response:*"],
    }


def get_cache_key(prefix: str, identifier: str) -> str:
    """Generate cache key with prefix"""
    return f"{prefix}{identifier}"


def parse_cache_key(key: str) -> Dict[str, str]:
    """Parse cache key into components"""
    parts = key.split(":", 1)
    if len(parts) == 2:
        return {"prefix": parts[0] + ":", "identifier": parts[1]}
    return {"prefix": "", "identifier": key}