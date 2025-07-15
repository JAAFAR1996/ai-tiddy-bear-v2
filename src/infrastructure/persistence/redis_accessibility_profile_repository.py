import json
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from redis.asyncio import Redis

from src.domain.interfaces.accessibility_profile_repository import IAccessibilityProfileRepository
from src.domain.value_objects.accessibility import AccessibilityProfile, SpecialNeedType
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="redis_accessibility_repository")


class RedisAccessibilityProfileRepository(IAccessibilityProfileRepository):
    """
    Redis implementation of the accessibility profile repository.
    Serializes and deserializes AccessibilityProfile objects to/from Redis.
    """
    PROFILE_KEY_PREFIX = "accessibility_profile:"

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client
        self.logger = logger

    async def get_profile_by_child_id(self, child_id: UUID) -> Optional[AccessibilityProfile]:
        key = self.PROFILE_KEY_PREFIX + str(child_id)
        try:
            profile_data_json = await self.redis_client.get(key)
            if profile_data_json:
                profile_data_dict = json.loads(profile_data_json)
                # Deserialize SpecialNeedType enum members correctly
                special_needs = [
                    SpecialNeedType[sn.upper()] for sn in profile_data_dict.get("special_needs", [])
                ]
                profile = AccessibilityProfile(
                    child_id=UUID(profile_data_dict["child_id"]),
                    special_needs=special_needs,
                    preferred_interaction_mode=profile_data_dict.get("preferred_interaction_mode", "voice"),
                    voice_speed_adjustment=profile_data_dict.get("voice_speed_adjustment", 1.0),
                    volume_level=profile_data_dict.get("volume_level", 0.8),
                    subtitles_enabled=profile_data_dict.get("subtitles_enabled", False),
                    additional_settings=profile_data_dict.get("additional_settings", {})
                )
                self.logger.debug(f"Retrieved accessibility profile for child {child_id} from Redis.")
                return profile
            self.logger.debug(f"Accessibility profile for child {child_id} not found in Redis.")
            return None
        except Exception as e:
            self.logger.error(f"Error getting accessibility profile for child {child_id} from Redis: {e}", exc_info=True)
            return None

    async def save_profile(self, profile: AccessibilityProfile) -> None:
        key = self.PROFILE_KEY_PREFIX + str(profile.child_id)
        try:
            # Serialize SpecialNeedType enum members to strings
            profile_data_dict = {
                "child_id": str(profile.child_id),
                "special_needs": [sn.value for sn in profile.special_needs],
                "preferred_interaction_mode": profile.preferred_interaction_mode,
                "voice_speed_adjustment": profile.voice_speed_adjustment,
                "volume_level": profile.volume_level,
                "subtitles_enabled": profile.subtitles_enabled,
                "additional_settings": profile.additional_settings
            }
            await self.redis_client.set(key, json.dumps(profile_data_dict))
            self.logger.debug(f"Saved accessibility profile for child {profile.child_id} to Redis.")
        except Exception as e:
            self.logger.error(f"Error saving accessibility profile for child {profile.child_id} to Redis: {e}", exc_info=True)
            raise # Re-raise to ensure calling service handles persistence failure

    async def delete_profile(self, child_id: UUID) -> bool:
        key = self.PROFILE_KEY_PREFIX + str(child_id)
        try:
            result = await self.redis_client.delete(key)
            if result > 0:
                self.logger.debug(f"Deleted accessibility profile for child {child_id} from Redis.")
                return True
            self.logger.debug(f"Accessibility profile for child {child_id} not found for deletion in Redis.")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting accessibility profile for child {child_id} from Redis: {e}", exc_info=True)
            return False

    async def get_all_profiles(self) -> List[AccessibilityProfile]:
        # In a production system, this operation should be avoided or carefully paginated
        # as it can be very resource intensive on large datasets.
        # For now, a placeholder that logs a warning.
        self.logger.warning("Attempted to retrieve all accessibility profiles. This operation is not optimized for large datasets.")
        # A real implementation would involve Redis SCAN or other techniques
        return [] 