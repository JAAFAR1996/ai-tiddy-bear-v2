"""Child Safety Input Validation Service

Provides COPPA-compliant validation specifically focused on child safety,
including age validation, content filtering, and PII protection.
"""

import re
from typing import Any
from src.domain.schemas import ValidationResult
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="validation")


class ChildSafetyValidator:
    """
    Provides validation for inputs related to child safety, including:
    - Age checks (COPPA compliance)
    - Content safety (offensive/inappropriate language)
    - PII detection (personally identifiable information)
    """

    def __init__(self, min_age: int = 3, max_age: int = 16):
        self.min_age = min_age
        self.max_age = max_age
        # قائمة الكلمات الممنوعة (يجب ضبطها من مصادر إنتاجية أو إعدادات)
        self.banned_words = {"badword1", "badword2"}
        # نمط ايميل/هاتف للكشف عن PII البسيطة
        self.email_pattern = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
        self.phone_pattern = re.compile(r"\b(\+?\d{1,3})?[-. (]*\d{3}[-. )]*\d{3,4}[-. ]*\d{4}\b")

    def validate_age(self, age: Any) -> ValidationResult:
        try:
            age_int = int(age)
        except (ValueError, TypeError):
            return ValidationResult(False, errors=["Invalid age value"])
        if not (self.min_age <= age_int <= self.max_age):
            return ValidationResult(
                False,
                errors=[f"Age {age_int} is out of allowed range [{self.min_age}, {self.max_age}]"]
            )
        return ValidationResult(True)

    def validate_content(self, text: str) -> ValidationResult:
        found_banned = [w for w in self.banned_words if w in text.lower()]
        if found_banned:
            return ValidationResult(
                False,
                errors=[f"Inappropriate content: {', '.join(found_banned)}"]
            )
        return ValidationResult(True)

    def detect_pii(self, text: str) -> ValidationResult:
        emails = self.email_pattern.findall(text)
        phones = self.phone_pattern.findall(text)
        errors = []
        if emails:
            errors.append(f"PII: emails detected {emails}")
        if phones:
            errors.append(f"PII: phone numbers detected {phones}")
        is_valid = not bool(errors)
        return ValidationResult(is_valid, errors=errors)

    def validate_child_input(self, input_data: dict[str, Any]) -> ValidationResult:
        # مثال: توقع وجود age و message في الدكتشنري
        errors = []
        result = self.validate_age(input_data.get("age"))
        if not result.is_valid:
            errors.extend(result.errors)
        result = self.validate_content(input_data.get("message", ""))
        if not result.is_valid:
            errors.extend(result.errors)
        result = self.detect_pii(input_data.get("message", ""))
        if not result.is_valid:
            errors.extend(result.errors)
        return ValidationResult(is_valid=not errors, errors=errors)
