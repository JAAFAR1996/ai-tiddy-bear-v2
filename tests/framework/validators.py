"""
Content Safety Validators - أدوات التحقق من أمان المحتوى
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from faker import Faker

fake = Faker()


@dataclass
class ContentValidationResult:
    """نتيجة التحقق من المحتوى"""

    is_safe: bool
    confidence: float
    violation_type: Optional[str] = None
    reason: Optional[str] = None
    suggested_alternative: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ContentSafetyValidator:
    """التحقق من أمان المحتوى للأطفال"""

    def __init__(self):
        # Unsafe patterns by category
        self.unsafe_patterns = {
            "violence": [
                r"\b(kill|hurt|fight|weapon|gun|knife|blood|die|death)\b",
                r"\b(punch|kick|hit|attack|destroy)\b",
            ],
            "inappropriate_language": [
                r"\b(damn|hell|stupid|hate|ugly|dumb|idiot)\b",
                r"\b(shut up|go away)\b",
            ],
            "adult_content": [
                r"\b(sex|kiss|date|boyfriend|girlfriend|love|marry)\b",
                r"\b(pregnant|baby|romance)\b",
            ],
            "personal_info": [
                r"(my|your) (address|phone|email|school|parent)",
                r"(where|what) (do you live|is your address|school do you go)",
                r"(tell me|what is) your (name|age|birthday)",
            ],
            "dangerous_requests": [
                r"don't tell (your )?(mom|dad|parents)",
                r"keep (this|it) (a )?secret",
                r"meet me (at|in)",
                r"send me (a )?(photo|picture)",
                r"come (to|with) me",
            ],
            "scary_content": [
                r"\b(ghost|monster|demon|witch|zombie|vampire)\b",
                r"\b(scary|frightening|horror|nightmare)\b",
            ],
        }

        # Age-appropriate content guidelines
        self.age_guidelines = {
            (3, 5): {
                "allowed_topics": [
                    "colors",
                    "shapes",
                    "animals",
                    "family",
                    "simple_stories",
                ],
                "max_complexity": "simple",
                "forbidden": ["violence", "scary_content", "complex_emotions"],
            },
            (6, 8): {
                "allowed_topics": ["education", "friendship", "adventure", "nature"],
                "max_complexity": "moderate",
                "forbidden": ["violence", "adult_content", "dangerous_requests"],
            },
            (9, 12): {
                "allowed_topics": ["science", "history", "sports", "hobbies"],
                "max_complexity": "complex",
                "forbidden": ["adult_content", "dangerous_requests", "personal_info"],
            },
        }

    def validate(self, content: str, age: int) -> ContentValidationResult:
        """التحقق من أمان المحتوى"""
        content_lower = content.lower()

        # Check for unsafe patterns
        for violation_type, patterns in self.unsafe_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    return ContentValidationResult(
                        is_safe=False,
                        confidence=0.95,
                        violation_type=violation_type,
                        reason=f"Content contains {violation_type} related terms",
                        suggested_alternative=self._generate_safe_alternative(
                            violation_type, age
                        ),
                    )

        # Check age appropriateness
        age_group = self._get_age_group(age)
        if age_group:
            forbidden = age_group.get("forbidden", [])
            for forbidden_type in forbidden:
                if forbidden_type in content_lower:
                    return ContentValidationResult(
                        is_safe=False,
                        confidence=0.90,
                        violation_type="age_inappropriate",
                        reason=f"Content not suitable for age {age}",
                        suggested_alternative=self._generate_age_appropriate_alternative(
                            age
                        ),
                    )

        # Content is safe
        return ContentValidationResult(
            is_safe=True,
            confidence=0.98,
            metadata={"age": age, "content_length": len(content)},
        )

    def _get_age_group(self, age: int) -> Optional[Dict[str, Any]]:
        """Get age group guidelines"""
        for (min_age, max_age), guidelines in self.age_guidelines.items():
            if min_age <= age <= max_age:
                return guidelines
        return None

    def _generate_safe_alternative(self, violation_type: str, age: int) -> str:
        """Generate safe alternative content"""
        alternatives = {
            "violence": "Let's talk about friendship and kindness instead!",
            "inappropriate_language": "Let's use nice words to express ourselves!",
            "adult_content": "Let's explore fun topics like animals or space!",
            "personal_info": "Remember to keep personal information private!",
            "dangerous_requests": "Let's talk to a trusted adult about this!",
            "scary_content": "How about a happy story instead?",
        }
        return alternatives.get(
            violation_type, "Let's talk about something fun and safe!"
        )


class AgeAppropriateContentGenerator:
    """Generator for age-appropriate test content"""

    def __init__(self):
        self.content_templates = {
            3: {
                "educational": [
                    "Let's count to {number}!",
                    "What color is the {object}?",
                    "The {animal} says {sound}!",
                ],
                "stories": [
                    "Once upon a time, there was a happy {animal}",
                    "The little {object} went on an adventure",
                ],
                "games": ["Let's play peek-a-boo!", "Can you jump like a {animal}?"],
            },
            5: {
                "educational": [
                    "Let's learn about {topic}!",
                    "Can you spell {word}?",
                    "What shape has {number} sides?",
                ],
                "stories": [
                    "The brave {character} helped their friend",
                    "In the magical forest, there lived a {creature}",
                ],
                "games": ["Let's play a rhyming game!", "I spy with my little eye..."],
            },
            8: {
                "educational": [
                    "Did you know that {fact}?",
                    "Let's explore how {process} works",
                    "In science, we learn about {topic}",
                ],
                "stories": [
                    "The adventurers discovered a {discovery}",
                    "Together, they solved the mystery of {mystery}",
                ],
                "games": [
                    "Let's solve this puzzle together",
                    "Can you guess the riddle?",
                ],
            },
            12: {
                "educational": [
                    "Let's discuss the importance of {concept}",
                    "In history, we learn about {event}",
                    "The scientific method helps us understand {phenomenon}",
                ],
                "stories": [
                    "The young hero faced challenges with courage",
                    "Through teamwork, they achieved {goal}",
                ],
                "games": [
                    "Let's play a strategy game",
                    "Can you solve this logic puzzle?",
                ],
            },
        }

        self.safe_placeholders = {
            "number": ["5", "10", "3", "7"],
            "object": ["ball", "toy", "book", "star"],
            "animal": ["cat", "dog", "bunny", "bird"],
            "sound": ["meow", "woof", "hop", "tweet"],
            "topic": ["nature", "space", "ocean", "seasons"],
            "word": ["cat", "sun", "tree", "happy"],
            "character": ["knight", "princess", "explorer", "scientist"],
            "creature": ["unicorn", "dragon", "fairy", "talking animal"],
            "fact": ["butterflies taste with their feet", "the sun is a star"],
            "process": ["rain", "plant growth", "day and night"],
            "discovery": ["hidden treasure", "new planet", "ancient map"],
            "mystery": ["the missing toy", "the secret garden"],
            "concept": ["friendship", "teamwork", "perseverance"],
            "event": ["ancient Egypt", "space exploration"],
            "phenomenon": ["gravity", "photosynthesis", "magnetism"],
            "goal": ["their dream", "saving the day", "helping others"],
        }

    def generate(self, age: int, topic: str = "general") -> str:
        """Generate age-appropriate content"""
        # Find closest age group
        age_key = min(self.content_templates.keys(), key=lambda x: abs(x - age))

        # Get templates for age and topic
        templates = self.content_templates[age_key].get(
            topic, self.content_templates[age_key]["educational"]
        )

        # Select random template
        template = fake.random_element(templates)

        # Fill placeholders
        content = template
        for placeholder, values in self.safe_placeholders.items():
            if f"{{{placeholder}}}" in content:
                value = fake.random_element(values)
                content = content.replace(f"{{{placeholder}}}", value)

        return content


class COPPAComplianceChecker:
    """COPPA (Children's Online Privacy Protection Act) compliance checker"""

    def __init__(self):
        self.personal_info_patterns = {
            "full_name": r"(my name is|i am) [A-Z][a-z]+ [A-Z][a-z]+",
            "address": r"(live at|address is|home is) .{5,}",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "school": r"(go to|attend|study at) .{3,} (school|academy)",
            "birthdate": r"(born on|birthday is) .{5,}",
        }

        self.allowed_data_fields = {
            "child_id",
            "age_group",  # Not exact age
            "interaction_count",
            "preferences",
            "learning_progress",
            "last_interaction_timestamp",
        }

    def check_data_collection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if data collection is COPPA compliant"""
        violations = []

        # Check for personal information
        for field, value in data.items():
            if field not in self.allowed_data_fields:
                if self._contains_personal_info(str(value)):
                    violations.append(
                        {"field": field, "type": "personal_info", "severity": "high"}
                    )

        # Check for exact age storage (should be age groups)
        if "age" in data and isinstance(data["age"], int):
            if data["age"] < 13:
                violations.append(
                    {
                        "field": "age",
                        "type": "exact_age_storage",
                        "severity": "medium",
                        "recommendation": "Store age groups instead of exact age",
                    }
                )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "checked_at": datetime.utcnow(),
        }

    def _contains_personal_info(self, text: str) -> bool:
        """Check if text contains personal information"""
        for info_type, pattern in self.personal_info_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def check_parental_consent(self, consent_data: Dict[str, Any]) -> bool:
        """Verify parental consent is properly obtained"""
        required_fields = [
            "parent_id",
            "child_id",
            "consent_timestamp",
            "consent_type",
            "verification_method",
        ]

        # Check all required fields present
        for field in required_fields:
            if field not in consent_data:
                return False

        # Check verification method is strong enough
        valid_methods = ["credit_card", "government_id", "signed_form", "video_call"]
        if consent_data.get("verification_method") not in valid_methods:
            return False

        # Check consent is not expired (90 days)
        consent_date = consent_data.get("consent_timestamp")
        if isinstance(consent_date, datetime):
            days_old = (datetime.utcnow() - consent_date).days
            if days_old > 90:
                return False

        return True
