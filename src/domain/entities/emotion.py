"""
Defines the EmotionType enumeration for representing various emotional states.

This module provides a standardized way to categorize and refer to different
emotions, which can be used throughout the system for emotion analysis,
response generation, and personalization.
"""

from enum import Enum


class EmotionType(Enum):
    """Enumeration for different emotional states."""

    HAPPY = "happy"
    SAD = "sad"
    NEUTRAL = "neutral"
    EXCITED = "excited"
