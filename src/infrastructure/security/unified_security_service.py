"""Unified Security Service - Centralized security management."""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.audit.child_safe_audit_logger import (
    get_child_safe_audit_logger,
)

logger = get_logger(__name__, component="unified_security")
child_safe_audit = get_child_safe_audit_logger()


@dataclass
class SecurityConfig:
    """Configuration for unified security service."""

    max_login_attempts: int = 3
    lockout_duration: timedelta = timedelta(minutes=15)
    dangerous_patterns: list[str] | None = None

    def __post_init__(self):
        if self.dangerous_patterns is None:
            self.dangerous_patterns = [
                "<script>",
                "drop table",
                r"exec\(",
                "'; drop",
                "union select",
                "insert into",
                "delete from",
                "update ",
                "exec sp_",
                "xp_cmdshell",
                "javascript:",
                "vbscript:",
                "<iframe",
                "<object",
                "<embed",
            ]


class UnifiedSecurityService:
    """Unified security service providing comprehensive security features."""

    def __init__(self, config: SecurityConfig = None):
        """Initialize the unified security service."""
        self.config = config or SecurityConfig()
        self.blocked_ips: dict[str, datetime] = {}
        self.failed_login_attempts: dict[str, list[datetime]] = {}

        # Store patterns as strings for simple string matching
        self.dangerous_patterns = self.config.dangerous_patterns

        logger.info("Unified security service initialized")

    async def analyze_threat(self, content: str, ip_address: str) -> dict[str, Any]:
        """Analyze content for security threats.

        Args:
            content: Content to analyze
            ip_address: Source IP address

        Returns:
            Threat analysis result
        """
        result = {
            "threat_detected": False,
            "threat_types": [],
            "severity": "low",
            "action_taken": "none",
            "ip_address": ip_address,
            "timestamp": datetime.utcnow(),
        }

        # Check for dangerous patterns
        detected_patterns = []
        content_lower = content.lower()
        for pattern in self.dangerous_patterns:
            if pattern.lower() in content_lower:
                detected_patterns.append(f"Dangerous pattern: {pattern}")

        if detected_patterns:
            result["threat_detected"] = True
            result["threat_types"].extend(detected_patterns)

            # Determine severity based on pattern type
            critical_patterns = ["drop table", "'; drop", "union select", "exec("]
            high_patterns = ["<script>", "javascript:", "vbscript:"]

            is_critical = any(cp.lower() in content_lower for cp in critical_patterns)
            is_high = any(hp.lower() in content_lower for hp in high_patterns)

            if is_critical:
                result["severity"] = "critical"
                result["action_taken"] = "blocked"
                # Block IP for critical threats
                self.blocked_ips[ip_address] = datetime.utcnow() + timedelta(hours=24)
            elif is_high:
                result["severity"] = "high"
                result["action_taken"] = "flagged"
            else:
                result["severity"] = "medium"
                result["action_taken"] = "logged"

        # Check for SQL injection attempts
        sql_injection_patterns = [
            "'; drop",
            "union select",
            "insert into",
            "delete from",
            "--",
        ]

        for pattern in sql_injection_patterns:
            if pattern.lower() in content_lower:
                result["threat_detected"] = True
                result["threat_types"].append("SQL injection attempt")
                result["severity"] = "critical"
                result["action_taken"] = "blocked"
                # Block IP for SQL injection
                self.blocked_ips[ip_address] = datetime.utcnow() + timedelta(hours=24)
                break

        logger.info(
            f"Threat analysis completed for IP {ip_address}: {result['severity']}"
        )
        return result

    async def validate_login_attempt(
        self, username: str, ip_address: str
    ) -> dict[str, Any]:
        """Validate if login attempt should be allowed.

        Args:
            username: Username attempting login
            ip_address: Source IP address

        Returns:
            Validation result
        """
        result = {
            "allowed": True,
            "reason": None,
            "remaining_attempts": None,
            "block_until": None,
        }

        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            block_until = self.blocked_ips[ip_address]
            if datetime.utcnow() < block_until:
                result["allowed"] = False
                result["reason"] = "IP temporarily blocked"
                result["block_until"] = block_until
                return result
            else:
                # Block expired, remove it
                del self.blocked_ips[ip_address]

        # Check failed login attempts
        now = datetime.utcnow()
        cutoff = now - self.config.lockout_duration

        # Clean old attempts
        if username in self.failed_login_attempts:
            self.failed_login_attempts[username] = [
                attempt
                for attempt in self.failed_login_attempts[username]
                if attempt > cutoff
            ]

        # Check current attempts count
        attempts = len(self.failed_login_attempts.get(username, []))
        if attempts >= self.config.max_login_attempts:
            result["allowed"] = False
            result["reason"] = "Too many failed attempts"
            result["remaining_attempts"] = 0
            # Calculate block until time
            if username in self.failed_login_attempts:
                last_attempt = max(self.failed_login_attempts[username])
                result["block_until"] = last_attempt + self.config.lockout_duration
        else:
            result["remaining_attempts"] = self.config.max_login_attempts - attempts

        return result

    async def record_login_failure(self, username: str, ip_address: str) -> None:
        """Record a failed login attempt."""
        now = datetime.utcnow()

        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []

        self.failed_login_attempts[username].append(now)

        # Auto-block after max attempts
        if len(self.failed_login_attempts[username]) >= self.config.max_login_attempts:
            logger.warning(
                f"User {username} exceeded login attempts, blocking IP {ip_address}"
            )

    async def clear_login_failures(self, username: str) -> None:
        """Clear failed login attempts for successful login."""
        if username in self.failed_login_attempts:
            del self.failed_login_attempts[username]

    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is currently blocked."""
        if ip_address not in self.blocked_ips:
            return False

        if datetime.utcnow() >= self.blocked_ips[ip_address]:
            # Block expired
            del self.blocked_ips[ip_address]
            return False

        return True

    async def block_ip(
        self, ip_address: str, duration: timedelta | None = None
    ) -> None:
        """Manually block an IP address."""
        if duration is None:
            duration = timedelta(hours=1)

        self.blocked_ips[ip_address] = datetime.utcnow() + duration
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
        child_safe_audit.log_security_event(
            event_type="ip_manually_blocked",
            threat_level="high",
            input_data="IP manually blocked by administrator",
            context={"ip_hash": ip_hash, "duration": str(duration)},
        )

    async def unblock_ip(self, ip_address: str) -> None:
        """Manually unblock an IP address."""
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            logger.info("IP address manually unblocked")

    async def get_security_status(self) -> dict[str, Any]:
        """Get current security status."""
        now = datetime.utcnow()

        # Clean expired blocks
        expired_ips = [ip for ip, until in self.blocked_ips.items() if now >= until]
        for ip in expired_ips:
            del self.blocked_ips[ip]

        return {
            "blocked_ips": len(self.blocked_ips),
            "failed_login_users": len(self.failed_login_attempts),
            "total_patterns": len(self.config.dangerous_patterns),
            "last_updated": now,
        }


# Convenience function for dependency injection
def get_unified_security_service(
    config: SecurityConfig = None,
) -> UnifiedSecurityService:
    """Get unified security service instance."""
    return UnifiedSecurityService(config)
