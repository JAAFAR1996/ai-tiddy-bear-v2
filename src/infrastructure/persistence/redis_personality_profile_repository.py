import json
from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from src.domain.interfaces.personality_profile_repository import (
    IPersonalityProfileRepository,
)
from src.domain.value_objects.personality import ChildPersonality, PersonalityType
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="redis_personality_repository")


class RedisPersonalityProfileRepository(IPersonalityProfileRepository):
    """Redis implementation of the personality profile repository.
    Serializes and deserializes ChildPersonality objects to/from Redis.
    """

    PROFILE_KEY_PREFIX = "personality_profile:"

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client
        self.logger = logger

    async def get_profile_by_child_id(self, child_id: UUID) -> ChildPersonality | None:
        key = self.PROFILE_KEY_PREFIX + str(child_id)
        try:
            profile_data_json = await self.redis_client.get(key)
            if profile_data_json:
                profile_data_dict = json.loads(profile_data_json)
                # Deserialize PersonalityType enum member and datetime
                personality_type = PersonalityType[
                    profile_data_dict.get("personality_type", "OTHER").upper()
                ]
                last_updated = datetime.fromisoformat(profile_data_dict["last_updated"])
                profile = ChildPersonality(
                    child_id=UUID(profile_data_dict["child_id"]),
                    personality_type=personality_type,
                    traits=profile_data_dict.get("traits", {}),
                    learning_style=profile_data_dict.get("learning_style", []),
                    interests=profile_data_dict.get("interests", []),
                    last_updated=last_updated,
                    metadata=profile_data_dict.get("metadata", {}),
                )
                self.logger.debug(
                    f"Retrieved personality profile for child {child_id} from Redis.",
                )
                return profile
            self.logger.debug(
                f"Personality profile for child {child_id} not found in Redis.",
            )
            return None
        except (ValueError, TypeError):
            self.logger.exception("Error getting personality profile from Redis")
            raise
        except Exception as e:
            self.logger.exception(
                "Critical error getting personality profile from Redis"
            )
            raise RuntimeError(
                f"Failed to get personality profile for child {child_id} from Redis"
            ) from e

    async def save_profile(self, profile: ChildPersonality) -> None:
        key = self.PROFILE_KEY_PREFIX + str(profile.child_id)
        try:
            # Serialize PersonalityType enum member to string and datetime to ISO format
            profile_data_dict = {
                "child_id": str(profile.child_id),
                "personality_type": profile.personality_type.value,
                "traits": profile.traits,
                "learning_style": profile.learning_style,
                "interests": profile.interests,
                "last_updated": profile.last_updated.isoformat(),
                "metadata": profile.metadata,
            }
            await self.redis_client.set(key, json.dumps(profile_data_dict))
            self.logger.debug(
                f"Saved personality profile for child {profile.child_id} to Redis.",
            )
        except (ValueError, TypeError):
            self.logger.exception("Error saving personality profile to Redis")
            raise
        except Exception as e:
            self.logger.exception("Critical error saving personality profile to Redis")
            raise RuntimeError(
                f"Failed to save personality profile for child {profile.child_id} to Redis"
            ) from e

    async def delete_profile(self, child_id: UUID) -> bool:
        key = self.PROFILE_KEY_PREFIX + str(child_id)
        try:
            result = await self.redis_client.delete(key)
            if result > 0:
                self.logger.debug(
                    f"Deleted personality profile for child {child_id} from Redis.",
                )
                return True
            self.logger.debug(
                f"Personality profile for child {child_id} not found for deletion in Redis.",
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Error deleting personality profile for child {child_id} from Redis: {e}",
                exc_info=True,
            )
            return False

    async def get_all_profiles(
        self, batch_size: int = 100, cursor: int = 0, max_profiles: int | None = None
    ) -> list[ChildPersonality]:
        """Retrieves all personality profiles using Redis SCAN for efficient pagination.

        PRODUCTION IMPLEMENTATION using Redis SCAN to avoid memory issues.

        Args:
            batch_size: Number of keys to process per SCAN iteration (default: 100)
            cursor: Starting cursor for pagination (default: 0 for beginning)
            max_profiles: Maximum number of profiles to return (default: None for all)

        Returns:
            List of ChildPersonality objects from Redis

        Performance Notes:
            - Uses Redis SCAN to avoid blocking and memory issues
            - Processes keys in batches to limit memory usage
            - Suitable for datasets with 10,000+ profiles
            - Time complexity: O(N) where N is total keys in Redis
            - Memory complexity: O(batch_size) during iteration

        Limitations:
            - SCAN may return duplicate keys in concurrent modification scenarios
            - Results are not sorted
            - Performance depends on Redis memory and network latency

        Best Practices:
            - Use batch_size=100-1000 for optimal performance
            - Consider max_profiles for pagination in API endpoints
            - Monitor Redis memory usage during large scans
            - Use during low-traffic periods for full scans
        """
        profiles: list[ChildPersonality] = []
        total_scanned = 0
        total_found = 0
        scan_cursor = cursor
        pattern = f"{self.PROFILE_KEY_PREFIX}*"

        self.logger.info(
            f"Starting personality profiles scan with batch_size={batch_size}, "
            f"max_profiles={max_profiles}, pattern='{pattern}'"
        )

        try:
            while True:
                # Use Redis SCAN for memory-efficient iteration
                scan_cursor, keys = await self.redis_client.scan(
                    cursor=scan_cursor, match=pattern, count=batch_size
                )

                total_scanned += len(keys)

                # Process each key in the current batch
                for key in keys:
                    try:
                        # Check if we've reached the maximum
                        if max_profiles and len(profiles) >= max_profiles:
                            self.logger.info(
                                f"Reached max_profiles limit: {max_profiles}"
                            )
                            return profiles

                        profile_data_json = await self.redis_client.get(key)
                        if profile_data_json:
                            profile_data_dict = json.loads(profile_data_json)

                            # Deserialize PersonalityType enum and datetime
                            personality_type = PersonalityType[
                                profile_data_dict.get(
                                    "personality_type", "OTHER"
                                ).upper()
                            ]
                            created_at = datetime.fromisoformat(
                                profile_data_dict["created_at"]
                            )

                            profile = ChildPersonality(
                                child_id=UUID(profile_data_dict["child_id"]),
                                personality_type=personality_type,
                                traits=profile_data_dict.get("traits", []),
                                preferences=profile_data_dict.get("preferences", {}),
                                created_at=created_at,
                            )
                            profiles.append(profile)
                            total_found += 1

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        self.logger.warning(
                            f"Failed to deserialize personality profile from key {key}: {e}"
                        )
                        continue
                    except Exception as e:
                        self.logger.error(f"Unexpected error processing key {key}: {e}")
                        continue

                # Check if scan is complete
                if scan_cursor == 0:
                    break

                # Log progress for large scans
                if total_scanned % 1000 == 0:
                    self.logger.debug(
                        f"Scan progress: {total_scanned} keys scanned, "
                        f"{total_found} profiles found"
                    )

            self.logger.info(
                f"Completed personality profiles scan: {total_scanned} keys scanned, "
                f"{total_found} valid profiles found, {len(profiles)} profiles returned"
            )

            return profiles

        except Exception as e:
            self.logger.error(f"Critical error during personality profiles scan: {e}")
            raise RuntimeError(
                f"Failed to retrieve personality profiles from Redis"
            ) from e
