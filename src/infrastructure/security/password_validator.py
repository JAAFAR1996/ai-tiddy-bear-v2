import re
from typing import Any

from src.infrastructure.security.registration_models import (
    PasswordRequirements,
)


def validate_password_strength(
    password: str,
    requirements: PasswordRequirements,
    user_info: dict[str, str] | None = None,
) -> dict[str, Any]:
    """التحقق من قوة كلمة المرور."""
    req = requirements
    validation = {
        "valid": True,
        "strength_score": 0,
        "errors": [],
        "warnings": [],
        "suggestions": [],
    }

    # فحص الطول
    if len(password) < req.min_length:
        validation["valid"] = False
        validation["errors"].append(
            f"Password must be at least {req.min_length} characters long",
        )
    else:
        validation["strength_score"] += 20

    # فحص الأحرف الكبيرة
    if req.require_uppercase and not re.search(r"[A-Z]", password):
        validation["valid"] = False
        validation["errors"].append(
            "Password must contain at least one uppercase letter",
        )
    elif re.search(r"[A-Z]", password):
        validation["strength_score"] += 15

    # فحص الأحرف الصغيرة
    if req.require_lowercase and not re.search(r"[a-z]", password):
        validation["valid"] = False
        validation["errors"].append(
            "Password must contain at least one lowercase letter",
        )
    elif re.search(r"[a-z]", password):
        validation["strength_score"] += 15

    # فحص الأرقام
    if req.require_numbers and not re.search(r"\d", password):
        validation["valid"] = False
        validation["errors"].append(
            "Password must contain at least one number"
        )
    elif re.search(r"\d", password):
        validation["strength_score"] += 15

    # فحص الرموز الخاصة
    if req.require_special_chars and not re.search(
        r'[!@#$%^&*()_+\-=\[\]{};:\'"\\\|,.<>?]',
        password,
    ):
        validation["valid"] = False
        validation["errors"].append(
            "Password must contain at least one special character",
        )
    elif re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\\|,.<>?]', password):
        validation["strength_score"] += 15

    # فحص الأنماط المحظورة
    password_lower = password.lower()
    if requirements.forbidden_patterns:
        for pattern in requirements.forbidden_patterns:
            if pattern in password_lower:
                validation["valid"] = False
                validation["errors"].append(
                    f"Password cannot contain common words like '{pattern}'",
                )

    # فحص التكرار
    if len(set(password)) < len(password) * 0.6:
        validation["warnings"].append(
            "Password has too many repeated characters"
        )
        validation["strength_score"] -= 10

    # فحص التسلسل
    sequences = ["123", "abc", "qwe", "asd", "zxc"]
    for seq in sequences:
        if seq in password_lower:
            validation["warnings"].append(
                "Avoid sequential characters in password"
            )
            validation["strength_score"] -= 5

    # فحص المعلومات الشخصية
    if user_info:
        name_parts = user_info.get("full_name", "").lower().split()
        email_local = user_info.get("email", "").split("@")[0].lower()
        for part in [*name_parts, email_local]:
            if part and len(part) > 2 and part in password_lower:
                validation["valid"] = False
                validation["errors"].append(
                    "Password cannot contain personal information",
                )

    # تقييم القوة النهائية
    if validation["strength_score"] >= 80:
        validation["strength"] = "STRONG"
    elif validation["strength_score"] >= 60:
        validation["strength"] = "MEDIUM"
    else:
        validation["strength"] = "WEAK"
        if validation["valid"]:
            validation["warnings"].append("Consider using a stronger password")

    # اقتراحات التحسين
    if validation["strength_score"] < 80:
        validation["suggestions"].extend(
            [
                "Use a mix of uppercase and lowercase letters",
                "Include numbers and special characters",
                "Avoid common words and personal information",
                "Consider using a passphrase with multiple words",
            ],
        )

    return validation
