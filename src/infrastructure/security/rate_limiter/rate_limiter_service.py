import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.child_safe_audit_logger import (
    get_child_safe_audit_logger,
)

logger = get_logger(__name__, component="security")
child_safe_audit = get_child_safe_audit_logger()


class RateLimiterService:
    """Service for managing rate limiting and account lockouts."""

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.settings = settings
        self.max_login_attempts = self.settings.security.MAX_LOGIN_ATTEMPTS
        self.lockout_duration = timedelta(
            seconds=self.settings.security.LOCKOUT_DURATION_SECONDS,
        )
        # Rate limiting storage
        self.login_attempts = defaultdict(list)
        self.locked_accounts = {}

    async def check_rate_limit(
        self,
        email: str,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        """Enhanced rate limiting with IP tracking and progressive delays."""
        now = datetime.utcnow()

        # Check if account is locked
        if email in self.locked_accounts:
            lock_time = self.locked_accounts[email]
            if now - lock_time < self.lockout_duration:
                remaining_time = (
                    lock_time + self.lockout_duration - now
                ).total_seconds()
                return {
                    "allowed": False,
                    "reason": "account_locked",
                    "retry_after": int(remaining_time),
                    "message": f"Account locked. Try again in {int(remaining_time / 60)} minutes.",
                }
            # Unlock account
            del self.locked_accounts[email]
            self.login_attempts[email] = []
            logger.info(
                f"Account unlocked after lockout period: {email[:3]}***@{email.split('@')[1] if '@' in email else 'domain'}",
            )

        # Clean old attempts (older than 1 hour)
        hour_ago = now - timedelta(hours=1)
        self.login_attempts[email] = [
            t for t in self.login_attempts[email] if t > hour_ago
        ]

        # Check attempts from this email
        if len(self.login_attempts[email]) >= self.max_login_attempts:
            self.locked_accounts[email] = now
            email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
            child_safe_audit.log_security_event(
                event_type="account_locked",
                threat_level="high",
                input_data="Account locked due to too many failed attempts",
                context={
                    "email_hash": email_hash,
                    "attempts": len(self.login_attempts[email]),
                },
            )
            return {
                "allowed": False,
                "reason": "account_locked",
                "retry_after": self.lockout_duration.total_seconds(),
                "message": "Account locked due to too many failed login attempts.",
            }

        return {"allowed": True}

    async def record_failed_login(
        self, email: str, ip_address: str | None = None
    ) -> None:
        """Record a failed login attempt."""
        self.login_attempts[email].append(datetime.utcnow())
        logger.info("Failed login attempt recorded for user")

    async def reset_login_attempts(self, email: str) -> None:
        """Reset login attempts for a user."""
        if email in self.login_attempts:
            del self.login_attempts[email]
        if email in self.locked_accounts:
            del self.locked_accounts[email]
        logger.info("Login attempts reset for user")
