from typing import Protocol

from src.domain.value_objects.child_preferences import AgeGroup


class AgeFilter(Protocol):
    """Protocol for age-based content filtering services."""

    def filter_content(self, content: str, age_group: AgeGroup) -> str:
        """Filter content based on age group.

        Args:
            content: The content to filter
            age_group: The target age group

        Returns:
            Filtered content appropriate for the age group
        """
        ...

    def is_age_appropriate(self, content: str, age_group: AgeGroup) -> bool:
        """Check if content is appropriate for the given age group.

        Args:
            content: The content to check
            age_group: The target age group

        Returns:
            True if content is appropriate, False otherwise
        """
        ...
