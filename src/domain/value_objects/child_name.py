"""Value objects for the domain layer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChildName:
    """A value object representing a child's name."""

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Child name cannot be empty.")
        if len(self.value) > 100:
            raise ValueError("Child name is too long.")
