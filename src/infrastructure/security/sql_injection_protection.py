"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging
import re
from .validation.input_sanitizer import InputSanitizer, get_input_sanitizer
from .validation.query_validator import SQLQueryValidator, get_query_validator
"""

Unified SQL Injection Protection System
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="security")

class SQLInjectionProtection:
    """
    Unified SQL injection protection combining prevention, monitoring, and configuration
    """
    def __init__(self) -> None:
        self.query_validator = get_query_validator()
        self.input_sanitizer = get_input_sanitizer()
        
        # Attack patterns monitoring
        self.attack_attempts = defaultdict(list)
        self.blocked_ips = set()
        
        # Configuration
        self.config = {
            "max_attempts_per_ip": 10,
            "block_duration_minutes": 60,
            "alert_threshold": 5
        }
        
        logger.info("SQL Injection Protection initialized")

    def validate_query(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate SQL query for injection attempts
        """
        # Validate query
        result = self.query_validator.validate_query(query, context)
        
        # Log if suspicious
        if not result.is_safe:
            self._log_attack_attempt(query, result.threats_found)
        
        return {
            "safe": result.is_safe,
            "threats": result.threats_found,
            "sanitized_query": result.sanitized_query,
            "risk_score": result.risk_score
        }

    def sanitize_input(self, user_input: str, input_type: str = "text") -> Dict[str, Any]:
        """
        Sanitize user input before use in queries
        """
        result = self.input_sanitizer.sanitize(user_input, input_type)
        
        return {
            "safe": result.is_safe,
            "sanitized": result.sanitized_value,
            "original": result.original_value,
            "modifications": result.modifications_made
        }

    def check_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked due to attack attempts"""
        return ip_address in self.blocked_ips

    def _log_attack_attempt(self, query: str, threats: List[str]) -> None:
        """Log potential SQL injection attempt"""
        timestamp = datetime.utcnow()
        
        # Log to security audit
        logger.warning(
            f"SQL injection attempt detected - Threats: {threats}, "
            f"Query preview: {query[:100]}..."
        )
        
        # IP tracking requires request context which is not available at this layer
        # Proper implementation would be in the middleware layer where we have access to:
        # - request.client.host for direct IP
        # - request.headers.get("X-Forwarded-For") for proxy scenarios
        #
        # This is intentionally left unimplemented here to maintain clean architecture
        # The middleware layer should call this method with IP information

    def get_protection_stats(self) -> Dict[str, Any]:
        """Get protection statistics"""
        return {
            "total_blocked_ips": len(self.blocked_ips),
            "recent_attacks": sum(len(attempts) for attempts in self.attack_attempts.values()),
            "configuration": self.config
        }

    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update protection configuration"""
        self.config.update(config)
        logger.info(f"SQL injection protection config updated: {config}")

# Global instance
_sql_protection: Optional[SQLInjectionProtection] = None

def get_sql_protection() -> SQLInjectionProtection:
    """Get or create SQL injection protection instance"""
    global _sql_protection
    if _sql_protection is None:
        _sql_protection = SQLInjectionProtection()
    return _sql_protection

# Legacy compatibility exports
SQLInjectionPrevention = SQLInjectionProtection
create_sql_injection_prevention = get_sql_protection
get_sql_injection_prevention = get_sql_protection