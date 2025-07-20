"""Test cases for EncryptedChild entity."""

from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from src.domain.entities.encrypted_child import EncryptedChild


class TestEncryptedChild:
    """Test suite for EncryptedChild entity."""

    def test_basic_child_creation(self):
        """Test creating a basic child entity."""
        child = EncryptedChild(name="Alice", age=5)

        assert child.name == "Alice"
        assert child.age == 5
        assert isinstance(child.id, UUID)
        assert child.is_active is True
        assert child.language_preference == "en"
        assert isinstance(child.created_at, datetime)
        assert isinstance(child.updated_at, datetime)

    def test_coppa_compliance_validation(self):
        """Test COPPA compliance age validation."""
        # Test child under 2 years
        with pytest.raises(
            ValueError, match="Children under 2 years are not supported"
        ):
            EncryptedChild(name="Baby", age=1)

        # Test child 13 or older
        with pytest.raises(ValueError, match="COPPA Compliance"):
            EncryptedChild(name="Teen", age=13)

        # Test valid ages
        for age in range(2, 13):
            child = EncryptedChild(name=f"Child{age}", age=age)
            assert child.age == age

    def test_age_consistency_with_date_of_birth(self):
        """Test age validation with date of birth."""
        # Consistent age and DOB
        today = date.today()
        dob = date(today.year - 5, today.month, today.day)
        child = EncryptedChild(name="Alice", age=5, date_of_birth=dob)
        assert child.age == 5

        # Inconsistent age and DOB
        with pytest.raises(ValueError, match="Age inconsistency"):
            EncryptedChild(name="Bob", age=5, date_of_birth=date(2010, 1, 1))

    def test_data_retention_date_setting(self):
        """Test automatic data retention date setting."""
        child = EncryptedChild(name="Alice", age=5)

        assert child.data_retention_date is not None
        expected_retention = child.created_at + timedelta(days=90)
        # Allow small time difference for test execution
        assert abs((child.data_retention_date - expected_retention).total_seconds()) < 1

    @patch("src.domain.value_objects.encrypted_field.EncryptedField")
    def test_emergency_contacts_encryption(self, mock_encrypted_field):
        """Test emergency contacts encryption."""
        mock_instance = Mock()
        mock_encrypted_field.return_value = mock_instance
        mock_instance.decrypt.return_value = [
            {"name": "Parent", "phone": "123-456-7890"}
        ]

        child = EncryptedChild(name="Alice", age=5)

        # Set emergency contacts
        contacts = [{"name": "Parent", "phone": "123-456-7890"}]
        child.emergency_contacts = contacts

        # Verify encryption was called
        mock_encrypted_field.assert_called_with(contacts)
        assert child._encrypted_emergency_contacts == mock_instance

        # Get emergency contacts
        retrieved_contacts = child.emergency_contacts
        assert retrieved_contacts == contacts

    @patch("src.domain.value_objects.encrypted_field.EncryptedField")
    def test_medical_notes_encryption(self, mock_encrypted_field):
        """Test medical notes encryption."""
        mock_instance = Mock()
        mock_encrypted_field.return_value = mock_instance
        mock_instance.decrypt.return_value = "Allergic to peanuts"

        child = EncryptedChild(name="Alice", age=5)

        # Set medical notes
        notes = "Allergic to peanuts"
        child.medical_notes = notes

        # Verify encryption was called
        mock_encrypted_field.assert_called_with(notes)
        assert child._encrypted_medical_notes == mock_instance

        # Get medical notes
        retrieved_notes = child.medical_notes
        assert retrieved_notes == notes

    def test_record_access_tracking(self):
        """Test access tracking functionality."""
        child = EncryptedChild(name="Alice", age=5)

        assert child.access_count == 0
        assert child.last_access_by is None

        # Record access
        child.record_access("parent_123")

        assert child.access_count == 1
        assert child.last_access_by == "parent_123"

        # Record another access
        child.record_access("admin_456")

        assert child.access_count == 2
        assert child.last_access_by == "admin_456"

    def test_is_due_for_deletion(self):
        """Test data deletion check."""
        child = EncryptedChild(name="Alice", age=5)

        # Not due yet
        assert child.is_due_for_deletion() is False

        # Set retention date to past
        child.data_retention_date = datetime.utcnow() - timedelta(days=1)
        assert child.is_due_for_deletion() is True

        # No retention date
        child.data_retention_date = None
        assert child.is_due_for_deletion() is False

    def test_extend_retention(self):
        """Test extending data retention period."""
        child = EncryptedChild(name="Alice", age=5)
        original_retention = child.data_retention_date

        # Extend by 30 days
        child.extend_retention(30)

        expected_retention = original_retention + timedelta(days=30)
        assert abs((child.data_retention_date - expected_retention).total_seconds()) < 1

    def test_coppa_protection_check(self):
        """Test COPPA protection status."""
        # Under 13
        child = EncryptedChild(name="Alice", age=5)
        assert child.is_coppa_protected is True
        assert child.requires_enhanced_privacy is True

        # 12 years old (still protected)
        child2 = EncryptedChild(name="Bob", age=12)
        assert child2.is_coppa_protected is True
        assert child2.requires_enhanced_privacy is True

    def test_update_interaction_time(self):
        """Test interaction time tracking."""
        child = EncryptedChild(name="Alice", age=5)

        assert child.total_interaction_time == 0
        assert child.last_interaction is None

        # Update interaction
        child.update_interaction_time(300)  # 5 minutes

        assert child.total_interaction_time == 300
        assert child.last_interaction is not None
        assert isinstance(child.last_interaction, datetime)

    def test_topic_restrictions(self):
        """Test topic restriction checking."""
        child = EncryptedChild(
            name="Alice",
            age=5,
            allowed_topics=["animals", "colors", "numbers"],
            restricted_topics=["violence", "scary"],
        )

        # Allowed topics
        assert child.is_topic_allowed("animals") is True
        assert child.is_topic_allowed("ANIMALS") is True  # Case insensitive

        # Restricted topics
        assert child.is_topic_allowed("violence") is False
        assert child.is_topic_allowed("SCARY") is False  # Case insensitive

        # Topic not in allowed list (when allowed list exists)
        assert child.is_topic_allowed("space") is False

        # No restrictions
        child2 = EncryptedChild(name="Bob", age=6)
        assert child2.is_topic_allowed("anything") is True

    def test_age_group_classification(self):
        """Test age group classification."""
        test_cases = [
            (2, "toddler"),
            (3, "toddler"),
            (4, "preschool"),
            (5, "preschool"),
            (6, "early_elementary"),
            (7, "early_elementary"),
            (8, "elementary"),
            (10, "elementary"),
            (11, "preteen"),
            (12, "preteen"),
        ]

        for age, expected_group in test_cases:
            child = EncryptedChild(name="Test", age=age)
            assert child.get_age_group() == expected_group

    def test_daily_interaction_limits(self):
        """Test daily interaction limit checking."""
        # No limit set
        child = EncryptedChild(name="Alice", age=5)
        assert child.can_interact_today() is True

        # With limit, no previous interaction
        child.max_daily_interaction_time = 3600  # 1 hour
        assert child.can_interact_today() is True

        # With limit, interaction today but under limit
        child.last_interaction = datetime.utcnow()
        child.total_interaction_time = 1800  # 30 minutes
        assert child.can_interact_today() is True

        # With limit, interaction today at limit
        child.total_interaction_time = 3600  # 1 hour
        assert child.can_interact_today() is False

        # With limit, interaction yesterday
        child.last_interaction = datetime.utcnow() - timedelta(days=1)
        assert child.can_interact_today() is True

    def test_to_dict_serialization(self):
        """Test entity serialization to dictionary."""
        child = EncryptedChild(
            name="Alice",
            age=5,
            personality_traits=["friendly", "curious"],
            learning_preferences={"visual": 0.8, "auditory": 0.2},
        )

        # Without encrypted fields
        result = child.to_dict(include_encrypted=False)

        assert result["name"] == "Alice"
        assert result["age"] == 5
        assert result["personality_traits"] == ["friendly", "curious"]
        assert result["learning_preferences"] == {
            "visual": 0.8,
            "auditory": 0.2,
        }
        assert "emergency_contacts" not in result
        assert "medical_notes" not in result

        # With encrypted fields
        result_with_encrypted = child.to_dict(include_encrypted=True)
        assert "emergency_contacts" in result_with_encrypted
        assert "medical_notes" in result_with_encrypted

    def test_from_dict_deserialization(self):
        """Test entity deserialization from dictionary."""
        data = {
            "id": str(uuid4()),
            "name": "Alice",
            "age": 5,
            "date_of_birth": date(2019, 1, 1).isoformat(),
            "personality_traits": ["friendly"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "emergency_contacts": [{"name": "Parent", "phone": "123-456"}],
            "medical_notes": "No allergies",
        }

        child = EncryptedChild.from_dict(data)

        assert child.name == "Alice"
        assert child.age == 5
        assert isinstance(child.id, UUID)
        assert isinstance(child.date_of_birth, date)
        assert child.personality_traits == ["friendly"]

    def test_special_needs_handling(self):
        """Test special needs field handling."""
        child = EncryptedChild(name="Alice", age=5, special_needs=["ADHD", "Dyslexia"])

        assert child.special_needs == ["ADHD", "Dyslexia"]
        assert len(child.special_needs) == 2

    def test_custom_settings(self):
        """Test custom settings storage."""
        custom = {
            "favorite_color": "blue",
            "preferred_voice": "female",
            "volume_level": 0.7,
        }

        child = EncryptedChild(name="Alice", age=5, custom_settings=custom)

        assert child.custom_settings == custom
        assert child.custom_settings["favorite_color"] == "blue"

    def test_cultural_background(self):
        """Test cultural background field."""
        child = EncryptedChild(
            name="Alice",
            age=5,
            cultural_background="Middle Eastern",
            language_preference="ar",
        )

        assert child.cultural_background == "Middle Eastern"
        assert child.language_preference == "ar"

    def test_parental_controls(self):
        """Test parental controls dictionary."""
        controls = {
            "content_filter": "strict",
            "time_limits": True,
            "require_approval": True,
        }

        child = EncryptedChild(name="Alice", age=5, parental_controls=controls)

        assert child.parental_controls == controls
        assert child.parental_controls["content_filter"] == "strict"
