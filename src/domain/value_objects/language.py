from enum import Enum


class Language(Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"

    @staticmethod
    def from_code(code: str) -> "Language":
        for lang in Language:
            if lang.value == code.lower():
                return lang
        raise ValueError(f"Unsupported language code: {code}")
