"""
Provides content filtering services to ensure child-safe interactions.

This service filters inappropriate words and content based on predefined lists
and age-group specific rules. It is crucial for maintaining COPPA compliance
and providing a safe environment for children using the AI Teddy Bear.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List

from src.domain.interfaces.config_interface import ConfigInterface
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="services")


class ContentFilterService:
    """Service for filtering inappropriate content."""

    def __init__(self, config: ConfigInterface) -> None:
        """
        Initializes the content filter service.

        Args:
            config: Configuration interface to load filtering rules.
        """
        self.logger = get_logger(__name__, component="services")
        self.config = config
        self.inappropriate_words = self._load_inappropriate_words()
        self.age_groups = self._load_age_groups()

    def _load_inappropriate_words(self) -> List[str]:
        """
        Loads inappropriate words from configuration.

        Returns:
            A list of inappropriate words.
        """
        # Enhanced content filtering with 50+ inappropriate words and patterns
        # Default inappropriate words for content filtering
        return self.config.get(
            "content_moderation.inappropriate_words",
            [
                # Violence & harm
                "bad", "stupid", "idiot", "hate", "kill", "die", "weapon",
                "violence", "fight", "hurt", "pain", "scary", "nightmare",
                "monster", "demon", "evil", "angry", "mad", "furious",
                "destroy", "break", "smash", "crash", "explosion",
                "dangerous", "poison", "toxic", "harmful", "unsafe",
                "attack", "murder", "blood", "gore", "torture", "abuse",
                # Adult content
                "adult", "mature", "sexual", "naked", "inappropriate",
                "private parts", "body parts", "bathroom", "toilet",
                # Bullying & negative behavior
                "bully", "mean", "cruel", "tease", "mock", "shame",
                "embarrass", "humiliate", "reject", "exclude",
                # Drugs & substances
                "drug", "alcohol", "smoke", "cigarette", "drunk",
                "marijuana", "cocaine", "heroin", "meth",
                # Personal information
                "address", "phone number", "email", "password",
                "credit card", "social security", "bank account",
                # Fear & anxiety inducing
                "death", "suicide", "depression", "anxiety", "panic",
                "terror", "horror", "traumatic", "disaster", "catastrophe",
                # Discriminatory language
                "racist", "sexist", "homophobic", "discriminatory", "prejudice",
                # Self-harm
                "cut", "harm myself", "end my life",
            ],
        )

    def _load_age_groups(self) -> Dict[str, Any]:
        """
        Loads age group specific content rules from configuration.

        Returns:
            A dictionary of age group rules.
        """
        return self.config.get(
            "content_moderation.age_groups",
            {
                "child": {"max_complexity": 3, "forbidden_topics": ["politics", "religion"]},
                "teen": {"max_complexity": 7, "forbidden_topics": []},
                "adult": {"max_complexity": 10, "forbidden_topics": []},
            },
        )

    def filter_content(self, text: str, age: int = None) -> str:
        """
        Filters inappropriate content from the given text.

        Args:
            text: The input text to filter.
            age: Optional. The age of the user for age-specific filtering.

        Returns:
            The filtered text with inappropriate words replaced.
        """
        filtered_text = text
        for word in self.inappropriate_words:
            # Use regex to replace whole words, case-insensitive
            filtered_text = re.sub(r'\b' + re.escape(word) + r'\b', "[FILTERED]", filtered_text, flags=re.IGNORECASE)

        if age is not None:
            age_group = self._get_age_group(age)
            if age_group:
                rules = self.age_groups.get(age_group)
                if rules and "forbidden_topics" in rules:
                    for topic in rules["forbidden_topics"]:
                        filtered_text = re.sub(r'\b' + re.escape(topic) + r'\b', "[FILTERED]", filtered_text, flags=re.IGNORECASE)

        return filtered_text

    def _get_age_group(self, age: int) -> str:
        """
        Determines the age group based on the given age.

        Args:
            age: The age of the user.

        Returns:
            The age group (e.g., "child", "teen", "adult").
        """
        if age < 13:
            return "child"
        elif 13 <= age < 18:
            return "teen"
        else:
            return "adult"
