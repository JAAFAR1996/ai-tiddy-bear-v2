"""AgeGroup value object with full test compatibility."""

from enum import Enum


class AgeGroup(str, Enum):
    """Age groups for children with safety-appropriate categorization."""

    TODDLER = "toddler"
    PRESCHOOL = "preschool"
    SCHOOL_AGE = "school_age"
    PRETEEN = "preteen"

    @classmethod
    def from_age(cls, age: int) -> "AgeGroup":
        """Convert numeric age to appropriate age group."""
        if age < 0:
            raise ValueError("Negative age")
        if 0 <= age <= 3:
            return cls.TODDLER
        if 4 <= age <= 5:
            return cls.PRESCHOOL
        if 6 <= age <= 10:
            return cls.SCHOOL_AGE
        return cls.PRETEEN

    def get_appropriate_content_types(self) -> list[str]:
        """Get appropriate content types for this age group."""
        content_map = {
            self.TODDLER: [
                "simple_songs",
                "basic_colors",
                "animal_sounds",
                "simple_words",
            ],
            self.PRESCHOOL: ["stories", "counting", "alphabet", "shapes"],
            self.SCHOOL_AGE: [
                "educational_games",
                "science_facts",
                "geography",
                "math",
            ],
            self.PRETEEN: ["complex_stories", "history", "technology", "social_skills"],
        }
        return content_map.get(self, [])

    def __str__(self) -> str:
        return f"AgeGroup.{self.name}"
