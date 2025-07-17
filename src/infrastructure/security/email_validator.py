from typing import Any, Dict
from email_validator import EmailNotValidError, validate_email

def validate_email_address(email: str) -> Dict[str, Any]:
    """التحقق من صحة عنوان البريد الإلكتروني"""
    validation_result = {
        "valid": False,
        "email": email,
        "errors": [],
        "normalized_email": None,
    }
    try:
        # استخدام مكتبة التحقق من البريد الإلكتروني
        validated_email = validate_email(email)
        validation_result["valid"] = True
        validation_result["normalized_email"] = validated_email.email
        
        # فحوصات إضافية
        domain = validated_email.domain
        
        # منع النطاقات المؤقتة المعروفة
        disposable_domains = [
            "10minutemail.com",
            "tempmail.org",
            "guerrillamail.com",
            "mailinator.com",
            "throwaway.email",
        ]
        
        if domain.lower() in disposable_domains:
            validation_result["valid"] = False
            validation_result["errors"].append(
                "Disposable email addresses are not allowed"
            )
        
        # التحقق من طول البريد الإلكتروني
        if len(email) > 254:
            validation_result["valid"] = False
            validation_result["errors"].append("Email address too long")
    
    except EmailNotValidError as e:
        validation_result["errors"].append(str(e))
    except Exception as e:
        validation_result["errors"].append(f"Email validation error: {e}")
    
    return validation_result