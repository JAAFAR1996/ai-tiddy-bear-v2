"""Test cases for Parent entity."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.domain.entities.parent_profile.entities import Parent


class TestParentEntity:
    """Test suite for Parent entity."""

    def test_basic_parent_creation(self):
        """Test creating a basic parent entity."""
        parent = Parent(name="John Doe", email="john@example.com")

        assert parent.name == "John Doe"
        assert parent.email == "john@example.com"
        assert parent.is_active is True
        assert parent.email_verified is False
        assert parent.phone_verified is False
        assert isinstance(parent.created_at, datetime)
        assert len(parent.child_ids) == 0

    def test_post_init_name_parsing(self):
        """Test automatic name parsing in post_init."""
        parent = Parent(name="Sarah Mohamed")

        assert parent.first_name == "Sarah"
        assert parent.last_name == "Mohamed"
        assert parent.get_full_name() == "Sarah Mohamed"

    def test_name_parsing_single_name(self):
        """Test name parsing with single name."""
        parent = Parent(name="Ahmed")

        assert parent.first_name == "Ahmed"
        assert parent.last_name is None
        assert parent.get_full_name() == "Ahmed"

    def test_name_parsing_multiple_parts(self):
        """Test name parsing with multiple name parts."""
        parent = Parent(name="Ahmed Ali Hassan")

        assert parent.first_name == "Ahmed"
        assert parent.last_name == "Ali Hassan"
        assert parent.get_full_name() == "Ahmed Ali Hassan"

    def test_email_validation(self):
        """Test email format validation."""
        # Valid email
        parent = Parent(name="John", email="john@example.com")
        assert parent.email == "john@example.com"

        # Invalid email formats
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user@.com",
            "user@domain",
            "user space@domain.com",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Parent(name="Test", email=invalid_email)

    def test_default_preferences(self):
        """Test default preferences initialization."""
        parent = Parent(name="John")

        expected_preferences = {
            "language": "ar",
            "notifications_enabled": True,
            "child_safety_level": "strict",
            "session_timeout_minutes": 30,
        }

        assert parent.preferences == expected_preferences

    def test_custom_preferences(self):
        """Test parent with custom preferences."""
        custom_prefs = {"language": "en", "theme": "dark"}

        parent = Parent(name="John", preferences=custom_prefs)

        # Custom preferences should be preserved
        assert parent.preferences["language"] == "en"
        assert parent.preferences["theme"] == "dark"

    def test_get_full_name_combinations(self):
        """Test get_full_name with different name combinations."""
        # First and last name provided
        parent1 = Parent(first_name="Ahmed", last_name="Ali")
        assert parent1.get_full_name() == "Ahmed Ali"

        # Only first name
        parent2 = Parent(first_name="Sarah")
        assert parent2.get_full_name() == "Sarah"

        # Only last name
        parent3 = Parent(last_name="Mohamed")
        assert parent3.get_full_name() == "Mohamed"

        # Name field takes precedence
        parent4 = Parent(
            name="Full Name",
            first_name="First",
            last_name="Last")
        assert parent4.get_full_name() == "First Last"

        # No name provided
        parent5 = Parent()
        assert parent5.get_full_name() == "Anonymous User"

    def test_get_display_name(self):
        """Test display name generation."""
        # With name
        parent1 = Parent(
            name="John Doe",
            id="12345678-1234-5678-1234-567812345678")
        assert parent1.get_display_name() == "John Doe"

        # Anonymous user
        parent2 = Parent(id="abcdef12-3456-7890-abcd-ef1234567890")
        assert parent2.get_display_name() == "Parent #abcdef12"

        # No ID
        parent3 = Parent()
        assert parent3.get_display_name() == "Parent #new"

    def test_add_child(self):
        """Test adding children to parent profile."""
        parent = Parent(name="John")

        # Add first child
        assert parent.add_child("child_123") is True
        assert "child_123" in parent.child_ids
        assert len(parent.child_ids) == 1

        # Add second child
        assert parent.add_child("child_456") is True
        assert len(parent.child_ids) == 2

        # Try to add duplicate
        assert parent.add_child("child_123") is False
        assert len(parent.child_ids) == 2

        # Invalid child IDs
        with pytest.raises(ValueError, match="Valid child_id required"):
            parent.add_child("")

        with pytest.raises(ValueError, match="Valid child_id required"):
            parent.add_child(None)

    def test_remove_child(self):
        """Test removing children from parent profile."""
        parent = Parent(name="John", child_ids=["child_123", "child_456"])

        # Remove existing child
        assert parent.remove_child("child_123") is True
        assert "child_123" not in parent.child_ids
        assert len(parent.child_ids) == 1

        # Try to remove non-existent child
        assert parent.remove_child("child_789") is False
        assert len(parent.child_ids) == 1

        # Remove last child
        assert parent.remove_child("child_456") is True
        assert len(parent.child_ids) == 0

    def test_update_preference(self):
        """Test updating parent preferences."""
        parent = Parent(name="John")

        # Update language
        parent.update_preference("language", "en")
        assert parent.preferences["language"] == "en"

        # Invalid language
        with pytest.raises(ValueError, match="Unsupported language"):
            parent.update_preference("language", "xyz")

        # Update safety level
        parent.update_preference("child_safety_level", "moderate")
        assert parent.preferences["child_safety_level"] == "moderate"

        # Invalid safety level
        with pytest.raises(ValueError, match="Invalid safety level"):
            parent.update_preference("child_safety_level", "extreme")

        # Update session timeout
        parent.update_preference("session_timeout_minutes", 60)
        assert parent.preferences["session_timeout_minutes"] == 60

        # Invalid session timeout
        with pytest.raises(ValueError, match="Session timeout must be between"):
            parent.update_preference("session_timeout_minutes", 500)

        with pytest.raises(ValueError, match="Session timeout must be between"):
            parent.update_preference("session_timeout_minutes", 2)

        # Invalid key
        with pytest.raises(ValueError, match="Valid preference key required"):
            parent.update_preference("", "value")

    def test_get_preference(self):
        """Test getting parent preferences."""
        parent = Parent(name="John")

        # Existing preference
        assert parent.get_preference("language") == "ar"

        # Non-existent preference with default
        assert parent.get_preference("theme", "light") == "light"

        # Non-existent preference without default
        assert parent.get_preference("non_existent") is None

    def test_is_verified(self):
        """Test verification status check."""
        parent = Parent(name="John")

        # Not verified
        assert parent.is_verified() is False

        # Email verified only
        parent.email_verified = True
        assert parent.is_verified() is False

        # Both verified
        parent.phone_verified = True
        assert parent.is_verified() is True

    def test_can_manage_children(self):
        """Test child management permission check."""
        parent = Parent(name="John")

        # Not active, not verified
        assert parent.can_manage_children() is False

        # Active but not verified
        parent.is_active = True
        assert parent.can_manage_children() is False

        # Active and email verified
        parent.email_verified = True
        assert parent.can_manage_children() is True

        # Inactive but verified
        parent.is_active = False
        assert parent.can_manage_children() is False

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        parent = Parent(
            id="parent_123",
            name="John Doe",
            email="john@example.com",
            phone_number="+1234567890",
            child_ids=["child_1", "child_2"],
            email_verified=True,
            phone_verified=True,
        )
        parent.last_login = datetime.utcnow()

        result = parent.to_dict()

        assert result["id"] == "parent_123"
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["phone_number"] == "+1234567890"
        assert result["child_count"] == 2
        assert result["is_active"] is True
        assert result["is_verified"] is True
        assert result["can_manage_children"] is True
        assert "created_at" in result
        assert "last_login" in result

    def test_str_representation(self):
        """Test string representation."""
        parent = Parent(
            id="parent_123", name="John Doe", child_ids=["child_1", "child_2"]
        )

        str_repr = str(parent)
        assert "Parent(id=parent_123" in str_repr
        assert "name='John Doe'" in str_repr
        assert "children=2" in str_repr

    def test_repr_representation(self):
        """Test developer representation."""
        parent = Parent(
            id="parent_123",
            name="John Doe",
            email="john@example.com",
            child_ids=["child_1"],
            email_verified=True,
        )

        repr_str = repr(parent)
        assert "Parent(id='parent_123'" in repr_str
        assert "name='John Doe'" in repr_str
        assert "email='john@example.com'" in repr_str
        assert "children=1" in repr_str
        assert "verified=False" in repr_str  # Phone not verified

    def test_supported_languages(self):
        """Test all supported languages."""
        parent = Parent(name="John")

        supported_languages = ["ar", "en", "fr", "es"]

        for lang in supported_languages:
            parent.update_preference("language", lang)
            assert parent.preferences["language"] == lang

    def test_empty_name_handling(self):
        """Test handling of empty name."""
        parent = Parent(name="")

        assert parent.first_name is None
        assert parent.last_name is None
        assert parent.get_full_name() == "Anonymous User"

    def test_whitespace_name_handling(self):
        """Test handling of whitespace in names."""
        parent = Parent(name="  John   Doe  ")

        assert parent.first_name == "John"
        assert parent.last_name == "Doe"
        assert parent.get_full_name() == "John Doe"

    def test_last_login_tracking(self):
        """Test last login timestamp."""
        parent = Parent(name="John")

        assert parent.last_login is None

        # Set last login
        login_time = datetime.utcnow()
        parent.last_login = login_time

        assert parent.last_login == login_time
