from dataclasses import dataclass


@dataclass
class RegistrationRequest:
    """طلب تسجيل مستخدم جديد."""

    email: str
    password: str
    confirm_password: str
    full_name: str
    phone_number: str | None = None
    date_of_birth: str | None = None
    terms_accepted: bool = False
    privacy_accepted: bool = False
    marketing_consent: bool = False


@dataclass
class PasswordRequirements:
    """متطلبات كلمة المرور."""

    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    forbidden_patterns: list[str] = None
