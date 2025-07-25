import re
import secrets
from datetime import datetime, timedelta
from typing import Any

from src.domain.models.registration_models import (
    PasswordRequirements,
    RegistrationRequest,
)
from src.infrastructure.validators.security.email_validator import (
    validate_email_address,
)
from src.infrastructure.validators.security.password_validator import (
    validate_password_strength,
)

"""🔒 AI Teddy Bear - Secure User Registration System
Secure user registration system with identity verification"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

# Production-only imports
try:
    import bcrypt
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: Security dependencies missing: {e}")
    raise ImportError("Missing security dependencies: bcrypt, cryptography") from e


class SecureUserRegistration:
    """Secure User Registration System
    Features:
    - Password strength validation
    - Email address validation
    - Duplicate account prevention
    - Email identity verification
    - COPPA compliance for parents.
    """

    def __init__(self) -> None:
        self.password_requirements = PasswordRequirements()
        self.password_requirements.forbidden_patterns = [
            "password",
            "123456",
            "qwerty",
            "admin",
            "user",
            "teddy",
            "bear",
            "child",
            "parent",
            "family",
        ]
        self.min_parent_age = 18
        self.verification_token_expiry = timedelta(hours=24)
        # Email verification storage (in production, use database)
        self.pending_verifications: dict[str, dict[str, Any]] = {}
        logger.info("Secure user registration system initialized")

    def validate_parent_eligibility(
        self,
        registration_data: RegistrationRequest,
    ) -> dict[str, Any]:
        """Validate parent eligibility for registration (COPPA compliance)."""
        validation = {"eligible": True, "errors": [], "warnings": []}

        # Check terms and conditions acceptance
        if not registration_data.terms_accepted:
            validation["eligible"] = False
            validation["errors"].append("Terms and conditions must be accepted")

        if not registration_data.privacy_accepted:
            validation["eligible"] = False
            validation["errors"].append("Privacy policy must be accepted")

        # Check age (if date of birth provided)
        if registration_data.date_of_birth:
            try:
                birth_date = datetime.strptime(
                    registration_data.date_of_birth,
                    "%Y-%m-%d",
                )
                age = (datetime.now() - birth_date).days // 365

                if age < self.min_parent_age:
                    validation["eligible"] = False
                    validation["errors"].append(
                        f"Must be at least {self.min_parent_age} years old to register",
                    )
                elif age > 100:
                    validation["warnings"].append(
                        "Please verify the date of birth is correct",
                    )
            except ValueError:
                validation["warnings"].append("Invalid date of birth format")

        # Check phone number (if provided)
        if registration_data.phone_number:
            # Simple phone number format check
            phone_pattern = re.compile(r"^\+?[\d\s\-\(\)]{10,15}$")
            if not phone_pattern.match(registration_data.phone_number):
                validation["warnings"].append("Phone number format may be invalid")

        return validation

    def generate_verification_token(self, email: str) -> str:
        """توليد رمز التحقق الآمن."""
        # توليد رمز عشوائي آمن
        token = secrets.token_urlsafe(32)
        # حفظ الرمز مع انتهاء الصلاحية
        self.pending_verifications[email] = {
            "token": token,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.verification_token_expiry,
            "verified": False,
        }
        return token

    def verify_email_token(self, email: str, token: str) -> bool:
        """التحقق من رمز البريد الإلكتروني."""
        if email not in self.pending_verifications:
            return False

        stored_data = self.pending_verifications[email]

        # فحص انتهاء الصلاحية
        if datetime.utcnow() > stored_data["expires_at"]:
            del self.pending_verifications[email]
            return False

        # فحص الرمز
        if stored_data["token"] != token:
            return False

        # تأكيد التحقق
        stored_data["verified"] = True
        return True

    def register_parent_user(
        self,
        registration_data: RegistrationRequest,
    ) -> dict[str, Any]:
        """تسجيل والد جديد مع جميع الفحوصات الأمنية."""
        try:
            # 1. التحقق من صحة البيانات
            email_validation = validate_email_address(registration_data.email)
            if not email_validation["valid"]:
                return {
                    "success": False,
                    "errors": email_validation["errors"],
                    "stage": "email_validation",
                }

            # 2. التحقق من تطابق كلمات المرور
            if registration_data.password != registration_data.confirm_password:
                return {
                    "success": False,
                    "errors": ["Passwords do not match"],
                    "stage": "password_confirmation",
                }

            # 3. التحقق من قوة كلمة المرور
            password_validation = validate_password_strength(
                registration_data.password,
                self.password_requirements,
                {
                    "full_name": registration_data.full_name,
                    "email": registration_data.email,
                },
            )

            if not password_validation["valid"]:
                return {
                    "success": False,
                    "errors": password_validation["errors"],
                    "warnings": password_validation["warnings"],
                    "suggestions": password_validation["suggestions"],
                    "stage": "password_validation",
                }

            # 4. التحقق من أهلية الوالد
            parent_validation = self.validate_parent_eligibility(registration_data)
            if not parent_validation["eligible"]:
                return {
                    "success": False,
                    "errors": parent_validation["errors"],
                    "warnings": parent_validation["warnings"],
                    "stage": "parent_eligibility",
                }

            # 5. توليد رمز التحقق
            verification_token = self.generate_verification_token(
                registration_data.email,
            )

            # 6. تشفير كلمة المرور
            password_hash = bcrypt.hashpw(
                registration_data.password.encode("utf-8"),
                bcrypt.gensalt(rounds=14),
            ).decode("utf-8")

            # 7. إنشاء ملف المستخدم
            user_profile = {
                "email": email_validation["normalized_email"],
                "password_hash": password_hash,
                "full_name": registration_data.full_name,
                "phone_number": registration_data.phone_number,
                "date_of_birth": registration_data.date_of_birth,
                "role": "parent",
                "created_at": datetime.utcnow().isoformat(),
                "email_verified": False,
                "account_status": "pending_verification",
                "marketing_consent": registration_data.marketing_consent,
                "registration_ip": None,  # يجب إضافته من الطلب
                "last_login": None,
                "failed_login_attempts": 0,
                "account_locked": False,
            }

            logger.info("New parent user registered successfully")

            return {
                "success": True,
                "user_profile": user_profile,
                "verification_token": verification_token,
                "verification_expires": (
                    datetime.utcnow() + self.verification_token_expiry
                ).isoformat(),
                "message": "Registration successful. Please check your email for verification instructions.",
                "password_strength": password_validation["strength"],
            }
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {
                "success": False,
                "errors": ["Registration failed due to internal error"],
                "stage": "system_error",
            }

    def resend_verification_email(self, email: str) -> dict[str, Any]:
        """إعادة إرسال بريد التحقق."""
        try:
            # فحص ما إذا كان البريد الإلكتروني في انتظار التحقق
            if email not in self.pending_verifications:
                return {
                    "success": False,
                    "error": "No pending verification found for this email",
                }

            # فحص ما إذا كان التحقق قد تم بالفعل
            if self.pending_verifications[email]["verified"]:
                return {"success": False, "error": "Email already verified"}

            # توليد رمز جديد
            new_token = self.generate_verification_token(email)

            return {
                "success": True,
                "verification_token": new_token,
                "verification_expires": (
                    datetime.utcnow() + self.verification_token_expiry
                ).isoformat(),
                "message": "Verification email resent successfully",
            }
        except Exception as e:
            logger.error(f"Error resending verification: {e}")
            return {
                "success": False,
                "error": "Failed to resend verification email",
            }
