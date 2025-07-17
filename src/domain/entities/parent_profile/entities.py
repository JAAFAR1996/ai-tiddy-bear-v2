"""from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
import re.
"""

"""Parent entity with comprehensive profile management and validation"""


@dataclass
class Parent:
    """Parent entity representing a parent / guardian in the AI Teddy Bear system.
    Handles parent profile information with comprehensive validation and privacy controls.
    """

    id: Optional[str] = None
    name: str = ""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    child_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    email_verified: bool = False
    phone_verified: bool = False

    def __post_init__(self):
        """Post - initialization validation and setup."""
        # Set creation timestamp if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        # Validate and parse name if first_name/last_name not provided
        if self.name and not (self.first_name or self.last_name):
            self._parse_full_name()

        # Validate email format if provided
        if self.email:
            self._validate_email()

        # Initialize default preferences
        if not self.preferences:
            self.preferences = {
                "language": "ar",
                "notifications_enabled": True,
                "child_safety_level": "strict",
                "session_timeout_minutes": 30,
            }

    def get_full_name(self) -> str:
        """Get the full name of the parent with proper formatting.
        Returns: str: The formatted full name of the parent
        Examples:
            >>> parent = Parent(first_name="Ahmed", last_name="Ali")
            >>> parent.get_full_name()
            "Ahmed Ali"
            >>> parent = Parent(name="Sarah Mohamed")
            >>> parent.get_full_name()
            "Sarah Mohamed".
        """
        # Use first_name and last_name if available
        if self.first_name or self.last_name:
            first = (self.first_name or "").strip()
            last = (self.last_name or "").strip()
            if first and last:
                return f"{first} {last}"
            if first:
                return first
            if last:
                return last

        # Fallback to the name field
        if self.name:
            return self.name.strip()

        # Return a default if no name is available
        return "Anonymous User"

    def get_display_name(self) -> str:
        """Get a display - friendly version of the parent's name."""
        full_name = self.get_full_name()
        # If it's the default name, return something more friendly
        if full_name == "Anonymous User":
            return f"Parent #{self.id[:8] if self.id else 'new'}"
        return full_name

    def add_child(self, child_id: str) -> bool:
        """Add a child ID to this parent's profile.

        Args:
            child_id: The unique identifier of the child
        Returns:
            bool: True if child was added, False if already exists

        """
        if not child_id or not isinstance(child_id, str):
            raise ValueError("Valid child_id required")

        if child_id not in self.child_ids:
            self.child_ids.append(child_id)
            return True
        return False

    def remove_child(self, child_id: str) -> bool:
        """Remove a child ID from this parent's profile.

        Args:
            child_id: The unique identifier of the child to remove
        Returns:
            bool: True if child was removed, False if not found

        """
        if child_id in self.child_ids:
            self.child_ids.remove(child_id)
            return True
        return False

    def update_preference(self, key: str, value: Any) -> None:
        """Update a parent preference with validation.

        Args:
            key: The preference key
            value: The preference value
        Raises:
            ValueError: If key or value is invalid

        """
        if not key or not isinstance(key, str):
            raise ValueError("Valid preference key required")

        # Validate specific preference values
        if key == "language" and value not in ["ar", "en", "fr", "es"]:
            raise ValueError("Unsupported language")
        if key == "child_safety_level" and value not in [
            "strict",
            "moderate",
            "relaxed",
        ]:
            raise ValueError("Invalid safety level")
        if key == "session_timeout_minutes" and (
            not isinstance(value, int) or value < 5 or value > 480
        ):
            raise ValueError("Session timeout must be between 5 and 480 minutes")

        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a parent preference with optional default."""
        return self.preferences.get(key, default)

    def is_verified(self) -> bool:
        """Check if parent account is fully verified."""
        return self.email_verified and self.phone_verified

    def can_manage_children(self) -> bool:
        """Check if parent can manage children (must be verified and active)."""
        return self.is_active and self.email_verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert parent entity to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.get_full_name(),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
            "child_count": len(self.child_ids),
            "is_active": self.is_active,
            "is_verified": self.is_verified(),
            "can_manage_children": self.can_manage_children(),
        }

    def _parse_full_name(self) -> None:
        """Parse the full name into first_name and last_name components."""
        if not self.name:
            return

        parts = self.name.strip().split()
        if len(parts) >= 2:
            self.first_name = parts[0]
            self.last_name = " ".join(parts[1:])
        elif len(parts) == 1:
            self.first_name = parts[0]

    def _validate_email(self) -> None:
        """Validate email format."""
        if not self.email:
            return

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.email):
            raise ValueError(f"Invalid email format: {self.email}")

    def __str__(self) -> str:
        """String representation of parent."""
        return f"Parent(id={self.id}, name='{self.get_full_name()}', children={len(self.child_ids)})"

    def __repr__(self) -> str:
        """Developer representation of parent."""
        return (
            f"Parent(id='{self.id}', name='{self.get_full_name()}', "
            f"email='{self.email}', children={len(self.child_ids)}, "
            f"verified={self.is_verified()})"
        )
