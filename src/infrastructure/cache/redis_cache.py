"""Production Redis Caching Implementation
High-performance caching layer with comprehensive features"""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class RedisCache:
    """Production-ready Redis caching implementation
    Comprehensive caching strategy to solve performance issues.
    """

    def __init__(self, redis_url: str, default_ttl: int = 3600) -> None:
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20,
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise RuntimeError(f"Cache initialization failed: {e}") from e

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.redis_client:
                await self.initialize()
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            if not self.redis_client:
                await self.initialize()
            serialized_value = json.dumps(value)
            ttl = ttl or self.default_ttl
            await self.redis_client.set(key, serialized_value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key '{key}': {e}")
            return False