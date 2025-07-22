import json
from datetime import datetime
from uuid import UUID

from redis.asyncio import Redis

from src.domain.interfaces.personality_profile_repository import (
    IPersonalityProfileRepository,
)
from src.domain.value_objects.personality import (
    ChildPersonality,
    PersonalityType,
)
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
        except (ValueError, TypeError) as err:
            self.logger.exception("Error getting personality profile from Redis")
            raise
        except Exception as err:
            self.logger.exception("Critical error getting personality profile from Redis")
            raise RuntimeError(f"Failed to get personality profile for child {child_id} from Redis") from err

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
        except (ValueError, TypeError) as err:
            self.logger.exception("Error saving personality profile to Redis")
            raise
        except Exception as err:
            self.logger.exception("Critical error saving personality profile to Redis")
            raise RuntimeError(f"Failed to save personality profile for child {profile.child_id} to Redis") from err

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

    async def get_all_profiles(self) -> list[ChildPersonality]:
        # In a production system, this operation should be avoided or carefully paginated
        # as it can be very resource intensive on large datasets.
        # For now, a placeholder that logs a warning.
        self.logger.warning(
            "Attempted to retrieve all personality profiles. This operation is not optimized for large datasets.",
        )
        # A real implementation would involve Redis SCAN or other techniques
        return []
