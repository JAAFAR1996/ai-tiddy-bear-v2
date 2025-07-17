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


@dataclass(frozen=True)
class ChildAge:
    """A value object representing a child's age."""
    value: int
    
    def __post_init__(self):
        if not (1 <= self.value <= 12):
            raise ValueError("Child age must be between 1 and 12 years.")