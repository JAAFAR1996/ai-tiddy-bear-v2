from enum import Enum


class Language(Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    MANDARIN = "zh"  # Alias for Chinese

    @staticmethod
    def from_code(code: str) -> "Language":
        for lang in Language:
            if lang.value == code.lower():
                return lang
        raise ValueError(f"Unsupported language code: {code}")

    def to_code(self) -> str:
        """Get the language code."""
        return self.value

    def display_name(self) -> str:
        """Get the display name of the language."""
        display_names = {
            "ar": "Arabic",
            "en": "English",
            "es": "Español",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
        }
        return display_names.get(self.value, self.name.title())

    def is_rtl(self) -> bool:
        """Check if language is right-to-left."""
        return self.value in ["ar", "he", "fa"]

    def get_available_voices(self) -> list[str]:
        """Get available voice models for this language."""
        voice_models = {
            "en": ["female_adult", "male_adult", "child_friendly", "child-en-us"],
            "es": ["female_adult", "male_adult"],
            "fr": ["female_adult", "male_adult"],
            "de": ["female_adult", "male_adult"],
            "zh": ["female_adult", "male_adult"],
            "ar": ["female_adult", "male_adult"],
        }
        return voice_models.get(self.value, ["default"])
