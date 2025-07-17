
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List
import base64
import hashlib
import json
import logging
import os
import secrets



from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    max_login_attempts: int = 5
    lockout_duration: timedelta = timedelta(minutes=30)
    session_timeout: timedelta = timedelta(hours=24)
    token_expiry: timedelta = timedelta(hours=1)
    encryption_key_size: int = 32
    salt_size: int = 32

class EnhancedSecurityService:
    """Enhanced security service with comprehensive protection"""
    def __init__(self, config: SecurityConfig = None) -> None:
        self.config = config or SecurityConfig()
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self._initialize_security()

    def _initialize_security(self) -> None:
        """Initialize security components"""
        try:
            # Ensure secure random number generation
            if not hasattr(secrets, 'token_bytes'):
                raise SecurityError("Secure random number generation not available")
            # Validate environment variables
            self._validate_environment()
            logger.info("Enhanced security service initialized")
        except Exception as e:
            logger.error(f"Security initialization failed: {e}")
            raise SecurityError(f"Failed to initialize security: {e}")

    def _validate_environment(self) -> None:
        """Validate security - related environment variables"""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'ENCRYPTION_KEY'
        ]
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        if missing_vars:
            logger.warning(f"Missing security environment variables: {missing_vars}")
            # Generate temporary keys for development
            for var in missing_vars:
                temp_key = self.generate_secure_key()
                os.environ[var] = temp_key
                logger.warning(f"Generated temporary {var} for development")

    def generate_secure_key(self, length: int = 32) -> str:
        """Generate a cryptographically secure random key"""
        return secrets.token_urlsafe(length)

    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure password meeting all requirements"""
        if length < self.config.password_min_length:
            length = self.config.password_min_length
        
        # Character sets
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        numbers = "0123456789"
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each required set
        password = []
        if self.config.password_require_uppercase:
            password.append(secrets.choice(uppercase))
        if self.config.password_require_lowercase:
            password.append(secrets.choice(lowercase))
        if self.config.password_require_numbers:
            password.append(secrets.choice(numbers))
        if self.config.password_require_special:
            password.append(secrets.choice(special))
        
        # Fill remaining length with random characters
        all_chars = ""
        if self.config.password_require_uppercase:
            all_chars += uppercase
        if self.config.password_require_lowercase:
            all_chars += lowercase
        if self.config.password_require_numbers:
            all_chars += numbers
        if self.config.password_require_special:
            all_chars += special
        
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength against security requirements"""
        result = {
            "valid": True,
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # Length check
        if len(password) < self.config.password_min_length:
            result["valid"] = False
            result["issues"].append(f"Password must be at least {self.config.password_min_length} characters")
            result["suggestions"].append(f"Use at least {self.config.password_min_length} characters")
        else:
            result["score"] += 25
        
        # Character requirements
        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            result["valid"] = False
            result["issues"].append("Password must contain uppercase letters")
            result["suggestions"].append("Add uppercase letters (A-Z)")
        elif self.config.password_require_uppercase:
            result["score"] += 20
        
        if self.config.password_require_lowercase and not any(c.islower() for c in password):
            result["valid"] = False
            result["issues"].append("Password must contain lowercase letters")
            result["suggestions"].append("Add lowercase letters (a-z)")
        elif self.config.password_require_lowercase:
            result["score"] += 20
        
        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            result["valid"] = False
            result["issues"].append("Password must contain numbers")
            result["suggestions"].append("Add numbers (0-9)")
        elif self.config.password_require_numbers:
            result["score"] += 20
        
        if self.config.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result["valid"] = False
            result["issues"].append("Password must contain special characters")
            result["suggestions"].append("Add special characters (!@#$%^&*)")
        elif self.config.password_require_special:
            result["score"] += 15
        
        # Common password checks
        common_passwords = [
            "password", "123456", "qwerty", "abc123", "admin", "user",
            "welcome", "login", "secret", "pass", "root", "guest"
        ]
        if password.lower() in common_passwords:
            result["valid"] = False
            result["issues"].append("Password is too common")
            result["suggestions"].append("Use a unique password")
        
        return result

    def check_rate_limit(self, identifier: str, max_attempts: int = None) -> bool:
        """Check if an identifier has exceeded rate limits"""
        if max_attempts is None:
            max_attempts = self.config.max_login_attempts
        
        now = datetime.now()
        
        # Clean old attempts
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if now - attempt < self.config.lockout_duration
            ]
        
        # Check if blocked
        if identifier in self.blocked_ips:
            if now - self.blocked_ips[identifier] < self.config.lockout_duration:
                logger.warning(f"Rate limit exceeded for {identifier}")
                return False
            else:
                # Unblock after timeout
                del self.blocked_ips[identifier]
        
        # Check attempt count
        attempts = len(self.failed_attempts.get(identifier, []))
        if attempts >= max_attempts:
            self.blocked_ips[identifier] = now
            logger.warning(f"IP {identifier} blocked due to excessive attempts")
            return False
        
        return True

    def record_failed_attempt(self, identifier: str) -> None:
        """Record a failed authentication attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        self.failed_attempts[identifier].append(datetime.now())
        logger.warning(f"Failed authentication attempt from {identifier}")

    def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed attempts for successful authentication"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.blocked_ips:
            del self.blocked_ips[identifier]

    def create_audit_log(self, action: str, user_id: str, details: Dict[str, Any]) -> None:
        """Create security audit log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details,
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent"),
            "success": details.get("success", True)
        }
        
        # Log to structured logger
        logger.info(f"Security audit: {action}", extra=log_entry)
        
        # Also log to file for compliance
        try:
            audit_file = os.getenv("SECURITY_AUDIT_FILE", "security_audit.log")
            with open(audit_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def sanitize_input(self, input_data: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks.
        This method will raise a ValueError if SQL injection patterns are detected.
        """
        if not input_data:
            return ""
        
        # Truncate if too long
        if len(input_data) > max_length:
            input_data = input_data[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '']
        
        for char in dangerous_chars:
            input_data = input_data.replace(char, '')
        
        # Check for SQL injection patterns and raise an error
        sql_patterns = [
            'union', 'select', 'insert', 'update', 'delete', 'drop', 'create',
            'alter', 'exec', 'execute', '--', '/*', '*/', 'xp_'
        ]
        
        input_lower = input_data.lower()
        for pattern in sql_patterns:
            if pattern in input_lower:
                logger.error(f"SQL injection pattern detected in input: {pattern}")
                raise ValueError("Potentially malicious input detected.")
        
        return input_data.strip()

    def generate_csrf_token(self) -> str:
        """Generate CSRF token for form protection"""
        return secrets.token_urlsafe(32)

    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, session_token)

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
        }

    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data for logging"""
        if not data:
            return ""
        if len(data) <= visible_chars:
            return "*" * len(data)
        visible_part = data[:visible_chars]
        masked_part = "*" * (len(data) - visible_chars)
        return f"{visible_part}{masked_part}"

class SecurityError(Exception):
    """Custom security exception"""
    pass

class SecurityMiddleware:
    """Security middleware for FastAPI"""
    def __init__(self, security_service: EnhancedSecurityService) -> None:
        self.security_service = security_service

    async def __call__(self, request, call_next):
        """Process security checks for each request"""
        try:
            # Get client IP
            client_ip = request.client.host
            
            # Rate limiting
            if not self.security_service.check_rate_limit(client_ip):
                return {"error": "Rate limit exceeded"}, 429
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_service.get_security_headers().items():
                response.headers[header] = value
            
            return response
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return {"error": "Security check failed"}, 500

def create_security_service() -> EnhancedSecurityService:
    """Factory function to create security service"""
    return EnhancedSecurityService()

def create_security_middleware(security_service: EnhancedSecurityService) -> SecurityMiddleware:
    """Factory function to create security middleware"""
    return SecurityMiddleware(security_service)