from domain.value_objects.safety_level import SafetyLevel
from domain.value_objects.language import Language
from domain.value_objects.child_preferences import ChildPreferences
from domain.value_objects.age_group import AgeGroup
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for domain value objects."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestAgeGroup:
    """Test AgeGroup value object."""

    def test_age_group_creation(self):
        """Test creating AgeGroup instances."""
        toddler = AgeGroup.TODDLER
        preschool = AgeGroup.PRESCHOOL
        school_age = AgeGroup.SCHOOL_AGE
        preteen = AgeGroup.PRETEEN

        assert toddler == AgeGroup.TODDLER
        assert preschool == AgeGroup.PRESCHOOL
        assert school_age == AgeGroup.SCHOOL_AGE
        assert preteen == AgeGroup.PRETEEN

    def test_age_group_from_age_toddler(self):
        """Test determining age group for toddlers."""
        assert AgeGroup.from_age(1) == AgeGroup.TODDLER
        assert AgeGroup.from_age(2) == AgeGroup.TODDLER
        assert AgeGroup.from_age(3) == AgeGroup.TODDLER

    def test_age_group_from_age_preschool(self):
        """Test determining age group for preschoolers."""
        assert AgeGroup.from_age(4) == AgeGroup.PRESCHOOL
        assert AgeGroup.from_age(5) == AgeGroup.PRESCHOOL

    def test_age_group_from_age_school_age(self):
        """Test determining age group for school age children."""
        assert AgeGroup.from_age(6) == AgeGroup.SCHOOL_AGE
        assert AgeGroup.from_age(7) == AgeGroup.SCHOOL_AGE
        assert AgeGroup.from_age(8) == AgeGroup.SCHOOL_AGE
        assert AgeGroup.from_age(9) == AgeGroup.SCHOOL_AGE
        assert AgeGroup.from_age(10) == AgeGroup.SCHOOL_AGE

    def test_age_group_from_age_preteen(self):
        """Test determining age group for preteens."""
        assert AgeGroup.from_age(11) == AgeGroup.PRETEEN
        assert AgeGroup.from_age(12) == AgeGroup.PRETEEN

    def test_age_group_edge_cases(self):
        """Test age group edge cases."""
        # Test boundary cases
        assert AgeGroup.from_age(0) == AgeGroup.TODDLER  # Newborn
        assert AgeGroup.from_age(13) == AgeGroup.PRETEEN  # Early teen
        assert AgeGroup.from_age(15) == AgeGroup.PRETEEN  # Older teen

    def test_age_group_invalid_age(self):
        """Test age group with invalid ages."""
        with pytest.raises(ValueError):
            AgeGroup.from_age(-1)

        with pytest.raises(ValueError):
            AgeGroup.from_age(100)  # Too old for system

    def test_age_group_string_representation(self):
        """Test string representation of age groups."""
        assert str(AgeGroup.TODDLER) == "AgeGroup.TODDLER"
        assert str(AgeGroup.PRESCHOOL) == "AgeGroup.PRESCHOOL"
        assert str(AgeGroup.SCHOOL_AGE) == "AgeGroup.SCHOOL_AGE"
        assert str(AgeGroup.PRETEEN) == "AgeGroup.PRETEEN"

    def test_age_group_comparison(self):
        """Test age group comparison."""
        assert AgeGroup.TODDLER != AgeGroup.PRESCHOOL
        assert AgeGroup.SCHOOL_AGE == AgeGroup.SCHOOL_AGE

    def test_age_group_content_appropriateness(self):
        """Test age-appropriate content suggestions."""
        toddler_content = AgeGroup.TODDLER.get_appropriate_content_types()
        assert "simple_words" in toddler_content
        assert "basic_colors" in toddler_content
        assert "animal_sounds" in toddler_content

        school_age_content = (
            AgeGroup.SCHOOL_AGE.get_appropriate_content_types()
        )
        assert "educational_games" in school_age_content
        assert "reading_comprehension" in school_age_content
        assert "science_facts" in school_age_content


class TestLanguage:
    """Test Language value object."""

    def test_language_creation(self):
        """Test creating Language instances."""
        english = Language.ENGLISH
        spanish = Language.SPANISH
        french = Language.FRENCH
        arabic = Language.ARABIC
        mandarin = Language.MANDARIN

        assert english == Language.ENGLISH
        assert spanish == Language.SPANISH
        assert french == Language.FRENCH
        assert arabic == Language.ARABIC
        assert mandarin == Language.MANDARIN

    def test_language_from_code(self):
        """Test creating Language from language codes."""
        assert Language.from_code("en") == Language.ENGLISH
        assert Language.from_code("es") == Language.SPANISH
        assert Language.from_code("fr") == Language.FRENCH
        assert Language.from_code("ar") == Language.ARABIC
        assert Language.from_code("zh") == Language.MANDARIN

    def test_language_from_code_case_insensitive(self):
        """Test language creation is case insensitive."""
        assert Language.from_code("EN") == Language.ENGLISH
        assert Language.from_code("En") == Language.ENGLISH
        assert Language.from_code("eN") == Language.ENGLISH

    def test_language_from_invalid_code(self):
        """Test creating Language from invalid code."""
        with pytest.raises(ValueError):
            Language.from_code("invalid")

        with pytest.raises(ValueError):
            Language.from_code("xx")

    def test_language_to_code(self):
        """Test converting Language to code."""
        assert Language.ENGLISH.to_code() == "en"
        assert Language.SPANISH.to_code() == "es"
        assert Language.FRENCH.to_code() == "fr"
        assert Language.ARABIC.to_code() == "ar"
        assert Language.MANDARIN.to_code() == "zh"

    def test_language_display_name(self):
        """Test language display names."""
        assert Language.ENGLISH.display_name() == "English"
        assert Language.SPANISH.display_name() == "Español"
        assert Language.FRENCH.display_name() == "Français"
        assert Language.ARABIC.display_name() == "العربية"
        assert Language.MANDARIN.display_name() == "中文"

    def test_language_rtl_support(self):
        """Test right-to-left language support."""
        assert Language.ARABIC.is_rtl() is True
        assert Language.ENGLISH.is_rtl() is False
        assert Language.SPANISH.is_rtl() is False
        assert Language.FRENCH.is_rtl() is False
        assert Language.MANDARIN.is_rtl() is False

    def test_language_voice_models(self):
        """Test language-specific voice models."""
        english_voices = Language.ENGLISH.get_available_voices()
        assert "child-en-us" in english_voices
        assert "child-en-uk" in english_voices

        spanish_voices = Language.SPANISH.get_available_voices()
        assert "child-es-es" in spanish_voices
        assert "child-es-mx" in spanish_voices

        arabic_voices = Language.ARABIC.get_available_voices()
        assert "child-ar-standard" in arabic_voices


class TestSafetyLevel:
    """Test SafetyLevel value object."""

    def test_safety_level_creation(self):
        """Test creating SafetyLevel instances."""
        none_level = SafetyLevel.NONE
        low = SafetyLevel.LOW
        moderate = SafetyLevel.MODERATE
        high = SafetyLevel.HIGH
        critical = SafetyLevel.CRITICAL

        assert none_level == SafetyLevel.NONE
        assert low == SafetyLevel.LOW
        assert moderate == SafetyLevel.MODERATE
        assert high == SafetyLevel.HIGH
        assert critical == SafetyLevel.CRITICAL

    def test_safety_level_values(self):
        """Test SafetyLevel enum values."""
        assert SafetyLevel.NONE.value == "none"
        assert SafetyLevel.LOW.value == "low"
        assert SafetyLevel.MODERATE.value == "moderate"
        assert SafetyLevel.HIGH.value == "high"
        assert SafetyLevel.CRITICAL.value == "critical"

    def test_safety_level_string_representation(self):
        """Test SafetyLevel string representation."""
        assert str(SafetyLevel.NONE) == "SafetyLevel.NONE"
        assert str(SafetyLevel.LOW) == "SafetyLevel.LOW"
        assert str(SafetyLevel.MODERATE) == "SafetyLevel.MODERATE"
        assert str(SafetyLevel.HIGH) == "SafetyLevel.HIGH"
        assert str(SafetyLevel.CRITICAL) == "SafetyLevel.CRITICAL"

    def test_safety_level_comparison(self):
        """Test SafetyLevel comparison."""
        assert SafetyLevel.NONE != SafetyLevel.LOW
        assert SafetyLevel.HIGH == SafetyLevel.HIGH
        assert SafetyLevel.CRITICAL != SafetyLevel.MODERATE


class TestChildPreferences:
    """Test ChildPreferences value object."""

    def test_child_preferences_creation(self):
        """Test creating ChildPreferences with default values."""
        preferences = ChildPreferences.create_default()

        assert preferences.language == Language.ENGLISH
        assert preferences.age_group == AgeGroup.PRESCHOOL
        assert preferences.interests == []
        assert preferences.safety_level == SafetyLevel.HIGH
        assert preferences.voice_preference == "child-default"

    def test_child_preferences_with_custom_values(self):
        """Test creating ChildPreferences with custom values."""
        preferences = ChildPreferences(
            language=Language.SPANISH,
            age_group=AgeGroup.SCHOOL_AGE,
            interests=["animals", "space", "music"],
            safety_level=SafetyLevel.MODERATE,
            voice_preference="child-es-mx",
            learning_style="visual",
            difficulty_level="intermediate",
        )

        assert preferences.language == Language.SPANISH
        assert preferences.age_group == AgeGroup.SCHOOL_AGE
        assert "animals" in preferences.interests
        assert "space" in preferences.interests
        assert "music" in preferences.interests
        assert preferences.safety_level == SafetyLevel.MODERATE
        assert preferences.voice_preference == "child-es-mx"
        assert preferences.learning_style == "visual"
        assert preferences.difficulty_level == "intermediate"

    def test_child_preferences_add_interest(self):
        """Test adding interests to child preferences."""
        preferences = ChildPreferences.create_default()

        preferences.add_interest("dinosaurs")
        assert "dinosaurs" in preferences.interests

        preferences.add_interest("robots")
        assert "robots" in preferences.interests
        assert len(preferences.interests) == 2

    def test_child_preferences_add_duplicate_interest(self):
        """Test adding duplicate interests."""
        preferences = ChildPreferences.create_default()

        preferences.add_interest("cars")
        preferences.add_interest("cars")  # Duplicate

        assert preferences.interests.count("cars") == 1

    def test_child_preferences_remove_interest(self):
        """Test removing interests from child preferences."""
        preferences = ChildPreferences(
            language=Language.ENGLISH,
            age_group=AgeGroup.SCHOOL_AGE,
            interests=["animals", "space", "music"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-default",
        )

        preferences.remove_interest("space")
        assert "space" not in preferences.interests
        assert "animals" in preferences.interests
        assert "music" in preferences.interests

    def test_child_preferences_update_language(self):
        """Test updating language preference."""
        preferences = ChildPreferences.create_default()

        preferences.update_language(Language.FRENCH)
        assert preferences.language == Language.FRENCH

        # Voice preference should update automatically
        assert "fr" in preferences.voice_preference.lower()

    def test_child_preferences_update_age_group(self):
        """Test updating age group."""
        preferences = ChildPreferences.create_default()

        preferences.update_age_group(AgeGroup.SCHOOL_AGE)
        assert preferences.age_group == AgeGroup.SCHOOL_AGE

    def test_child_preferences_safety_adjustment(self):
        """Test safety level adjustments."""
        preferences = ChildPreferences.create_default()

        preferences.adjust_safety_level(SafetyLevel.WARNING)
        assert preferences.safety_level == SafetyLevel.WARNING

    def test_child_preferences_to_dict(self):
        """Test converting preferences to dictionary."""
        preferences = ChildPreferences(
            language=Language.SPANISH,
            age_group=AgeGroup.PRESCHOOL,
            interests=["stories", "animals"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-es",
        )

        prefs_dict = preferences.to_dict()

        assert prefs_dict["language"] == "es"
        assert prefs_dict["age_group"] == "PRESCHOOL"
        assert prefs_dict["interests"] == ["stories", "animals"]
        assert prefs_dict["safety_level"] == "SAFE"
        assert prefs_dict["voice_preference"] == "child-es"

    def test_child_preferences_from_dict(self):
        """Test creating preferences from dictionary."""
        prefs_dict = {
            "language": "fr",
            "age_group": "SCHOOL_AGE",
            "interests": ["science", "art"],
            "safety_level": "CAUTION",
            "voice_preference": "child-fr",
            "learning_style": "auditory",
            "difficulty_level": "advanced",
        }

        preferences = ChildPreferences.from_dict(prefs_dict)

        assert preferences.language == Language.FRENCH
        assert preferences.age_group == AgeGroup.SCHOOL_AGE
        assert "science" in preferences.interests
        assert "art" in preferences.interests
        assert preferences.safety_level == SafetyLevel.MODERATE
        assert preferences.voice_preference == "child-fr"
        assert preferences.learning_style == "auditory"
        assert preferences.difficulty_level == "advanced"

    def test_child_preferences_validation(self):
        """Test preferences validation."""
        preferences = ChildPreferences.create_default()

        # Test valid interests
        valid_interests = [
            "animals",
            "space",
            "music",
            "art",
            "science",
            "sports",
        ]
        for interest in valid_interests:
            preferences.add_interest(interest)

        assert preferences.validate() is True

    def test_child_preferences_invalid_interests(self):
        """Test handling invalid interests."""
        preferences = ChildPreferences.create_default()

        with pytest.raises(ValueError):
            preferences.add_interest("inappropriate_content")

        with pytest.raises(ValueError):
            preferences.add_interest("")  # Empty interest

    def test_child_preferences_equality(self):
        """Test preferences equality."""
        prefs1 = ChildPreferences(
            language=Language.ENGLISH,
            age_group=AgeGroup.PRESCHOOL,
            interests=["animals"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-en",
        )

        prefs2 = ChildPreferences(
            language=Language.ENGLISH,
            age_group=AgeGroup.PRESCHOOL,
            interests=["animals"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-en",
        )

        prefs3 = ChildPreferences(
            language=Language.SPANISH,
            age_group=AgeGroup.PRESCHOOL,
            interests=["animals"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-es",
        )

        assert prefs1 == prefs2
        assert prefs1 != prefs3

    def test_child_preferences_copy(self):
        """Test copying preferences."""
        original = ChildPreferences(
            language=Language.MANDARIN,
            age_group=AgeGroup.TODDLER,
            interests=["colors", "shapes"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-zh",
        )

        copy = original.copy()

        assert copy == original
        assert copy is not original
        assert copy.interests is not original.interests

    def test_child_preferences_merge(self):
        """Test merging preferences."""
        base_prefs = ChildPreferences(
            language=Language.ENGLISH,
            age_group=AgeGroup.PRESCHOOL,
            interests=["animals"],
            safety_level=SafetyLevel.HIGH,
            voice_preference="child-en",
        )

        update_prefs = ChildPreferences(
            language=Language.SPANISH,
            age_group=AgeGroup.SCHOOL_AGE,
            interests=["space", "robots"],
            safety_level=SafetyLevel.MODERATE,
            voice_preference="child-es",
        )

        merged = base_prefs.merge(update_prefs)

        assert merged.language == Language.SPANISH
        assert merged.age_group == AgeGroup.SCHOOL_AGE
        assert set(merged.interests) == {"animals", "space", "robots"}
        assert merged.safety_level == SafetyLevel.MODERATE
        assert merged.voice_preference == "child-es"
