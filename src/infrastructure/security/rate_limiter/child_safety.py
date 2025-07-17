"""Child safety specific rate limiting features."""

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.comprehensive_audit_integration import (
    get_audit_integration,
)

from .core import RateLimitConfig, RateLimitState

logger = get_logger(__name__, component="security")


class ChildSafetyHandler:
    """Handler for child safety related rate limiting features."""

    def __init__(self):
        self.audit_integration = get_audit_integration()

    async def handle_child_safety_violation(
        self,
        config: RateLimitConfig,
        key: str,
        user_id: str | None,
        child_id: str | None,
        ip_address: str | None,
    ) -> None:
        """Handle rate limit violations that trigger child safety protocols."""
        # Log as security incident
        await self.audit_integration.log_security_event(
            event_type="child_safety_rate_limit_violation",
            severity="warning",
            description=f"Child safety rate limit exceeded for key: {key}",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "rate_limit_config": config.limit_type.value,
                "child_id": child_id,
                "key": key,
                "safety_action": "rate_limit_enforced",
            },
        )
        # Additional child safety measures could be implemented here
        # (e.g., notify parents, escalate to safety team, etc.)

    def should_block_key(self, config: RateLimitConfig, state: RateLimitState) -> bool:
        """Determine if a key should be blocked based on child safety behavior."""
        # Always block if it's a child safety config
        if config.child_safe_mode:
            return True

        # Block if there have been too many recent denials
        import time

        recent_time = time.time() - 300  # Last 5 minutes
        recent_requests = len([r for r in state.requests if r > recent_time])
        # Block if more than 3 rate limit denials in the last 5 minutes
        if recent_requests > config.max_requests * 3:
            logger.warning(
                f"Suspicious activity detected for key {state.key}, blocking.",
            )
            return True

        return False
