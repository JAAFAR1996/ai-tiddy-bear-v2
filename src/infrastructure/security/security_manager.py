"""Security Manager - Import wrapper for existing CoreSecurityManager."""

# Import existing implementation and alias it to match test expectations
from src.infrastructure.security.child_safety.security_manager import (
    CoreSecurityManager as SecurityManager,
    security_manager,
)

__all__ = ['SecurityManager', 'security_manager']
