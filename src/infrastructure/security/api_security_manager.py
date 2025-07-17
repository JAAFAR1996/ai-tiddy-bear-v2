import html
import logging
import re
import time
from typing import Any, Dict, List

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")


class APISecurityManager:
    """Handles API-level security including rate limiting and input sanitization."""
    
    def __init__(self) -> None:
        self.rate_limit_storage: Dict[str, List[float]] = {}
        self.rate_limit_window = 60  # 1 minute window
        self.rate_limit_max_requests = 100  # max requests per window
        self.blocked_ips: set = set()
        self.max_input_length = 1000
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP address is within rate limits.
        Args:
            ip_address: Client IP address
        Returns:
            bool: True if within limits, False if rate limited
        """
        try:
            current_time = time.time()
            
            # Check if IP is blocked
            if ip_address in self.blocked_ips:
                logger.warning(f"Blocked IP attempted access: {ip_address}")
                return False
            
            # Get or create request history for this IP
            if ip_address not in self.rate_limit_storage:
                self.rate_limit_storage[ip_address] = []
            
            request_times = self.rate_limit_storage[ip_address]
            
            # Remove old requests outside the window
            cutoff_time = current_time - self.rate_limit_window
            request_times = [t for t in request_times if t > cutoff_time]
            self.rate_limit_storage[ip_address] = request_times
            
            # Check if within limit
            if len(request_times) >= self.rate_limit_max_requests:
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return False
            
            # Add current request
            request_times.append(current_time)
            
            logger.debug(
                f"Rate limit check passed for {ip_address}: {len(request_times)}/{self.rate_limit_max_requests}"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error checking rate limit for {ip_address}: {e}")
            # Fail open - allow request if there's an error
            return True
    
    def block_ip(self, ip_address: str) -> None:
        """Block an IP address."""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP address blocked: {ip_address}")
    
    def unblock_ip(self, ip_address: str) -> None:
        """Unblock an IP address."""
        self.blocked_ips.discard(ip_address)
        logger.info(f"IP address unblocked: {ip_address}")
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize user input for security.
        Args:
            input_string: Raw input string
        Returns:
            str: Sanitized input string
        """
        try:
            if not input_string:
                return ""
            
            # Limit input length
            if len(input_string) > self.max_input_length:
                input_string = input_string[: self.max_input_length]
                logger.warning(f"Input truncated to {self.max_input_length} characters")
            
            # HTML escape to prevent XSS
            sanitized = html.escape(input_string)
            
            # Remove null bytes
            sanitized = sanitized.replace("\x00", "")
            
            # Remove control characters except newline and tab
            sanitized = "".join(
                char for char in sanitized if ord(char) >= 32 or char in "\n\t"
            )
            
            # Remove common SQL injection patterns
            sql_patterns = [
                r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+",
                r"[\"\';]",
                r"--",
                r"/\*",
                r"\*/",
                r"xp_",
                r"sp_",
            ]
            for pattern in sql_patterns:
                sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
            
            # Remove script tags and javascript
            script_patterns = [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"onload=",
                r"onerror=",
                r"onclick=",
            ]
            for pattern in script_patterns:
                sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
            
            logger.debug(
                f"Input sanitized: length {len(input_string)} -> {len(sanitized)}"
            )
            
            return sanitized.strip()
        except Exception as e:
            logger.error(f"Error sanitizing input: {e}")
            # Return empty string if sanitization fails
            return ""
    
    def validate_child_input(self, input_text: str) -> Dict[str, Any]:
        """Validate input specifically for child safety.
        Args:
            input_text: Text input from child
        Returns:
            Dict containing validation results
        """
        result = {
            "is_safe": True,
            "sanitized_input": "",
            "warnings": [],
            "blocked_content": [],
        }
        
        try:
            # Basic sanitization
            sanitized = self.sanitize_input(input_text)
            result["sanitized_input"] = sanitized
            
            # Check for inappropriate content patterns
            inappropriate_patterns = [
                r"\b(password|credit\s*card|ssn|social\s*security)\b",
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
                r"\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b",  # Credit card pattern
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                r"\b\d{3}-\d{3}-\d{4}\b",  # Phone number
            ]
            
            for pattern in inappropriate_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    result["is_safe"] = False
                    result["blocked_content"].append(
                        f"Potential sensitive information detected"
                    )
                    break
            
            # Check for excessive caps (shouting)
            if (
                len(sanitized) > 10
                and sum(1 for c in sanitized if c.isupper()) / len(sanitized) > 0.7
            ):
                result["warnings"].append("Input contains excessive capital letters")
            
            # Check for repetitive content
            if (
                len(sanitized) > 20
                and len(set(sanitized.lower())) < len(sanitized) * 0.3
            ):
                result["warnings"].append("Input appears to be repetitive")
            
            logger.debug(
                f"Child input validation: {'SAFE' if result['is_safe'] else 'BLOCKED'}"
            )
            
            return result
        except Exception as e:
            logger.error(f"Error validating child input: {e}")
            result["is_safe"] = False
            result["blocked_content"].append("Validation error occurred")
            return result