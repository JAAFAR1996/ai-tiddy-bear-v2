"""Shared security level definitions for AI Teddy Bear v5."""

from enum import Enum


class SecurityLevel(Enum):
    """Unified security levels for all security components."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CHILD_STRICT = "child_strict"
    CHILD_SAFETY_ENHANCED = "child_safety_enhanced"
    PARENT_MODERATE = "parent_moderate"
    ADMIN_STRICT = "admin_strict"


class RequestSecurityLevel(Enum):
    """Security levels for request signing."""

    CHILD_INTERACTION = "child_interaction"
    PARENT_ACCESS = "parent_access"
    ADMIN_ACCESS = "admin_access"
