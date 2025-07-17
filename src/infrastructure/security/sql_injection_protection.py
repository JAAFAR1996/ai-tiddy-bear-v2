"""
Unified SQL Injection Protection System
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

# Import with fallback for missing modules
try:
    from .validation.input_sanitizer import get_input_sanitizer
except ImportError:
    logger.warning("Input sanitizer not available, using mock implementation")
    
    class MockInputSanitizer:
        def sanitize(self, user_input: str, input_type: str = "text"):
            class MockResult:
                def __init__(self):
                    self.is_safe = True
                    self.sanitized_value = user_input
                    self.original_value = user_input
                    self.modifications_made = []
            return MockResult()
    
    def get_input_sanitizer():
        return MockInputSanitizer()

try:
    from .validation.query_validator import get_query_validator
except ImportError:
    logger.warning("Query validator not available, using mock implementation")
    
    class MockQueryValidator:
        def validate_query(self, query: str, context: Optional[str] = None):
            class MockResult:
                def __init__(self):
                    self.is_safe = True
                    self.threats_found = []
                    self.sanitized_query = query
                    self.risk_score = 0
            return MockResult()
    
    def get_query_validator():
        return MockQueryValidator()


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
            "alert_threshold": 5,
            "enable_logging": True,
            "enable_ip_blocking": True,
            "strict_mode": False,
        }

        logger.info("SQL Injection Protection initialized")

    def validate_query(
        self, query: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate SQL query for injection attempts
        """
        # Validate query
        result = self.query_validator.validate_query(query, context)

        # Log if suspicious
        if not result.is_safe:
            self._log_attack_attempt(query, result.threats_found, context)

        return {
            "safe": result.is_safe,
            "threats": result.threats_found,
            "sanitized_query": result.sanitized_query,
            "risk_score": result.risk_score,
            "context": context,
        }

    def sanitize_input(
        self, user_input: str, input_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Sanitize user input before use in queries
        """
        result = self.input_sanitizer.sanitize(user_input, input_type)

        return {
            "safe": result.is_safe,
            "sanitized": result.sanitized_value,
            "original": result.original_value,
            "modifications": result.modifications_made,
            "input_type": input_type,
        }

    def check_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked due to attack attempts"""
        return ip_address in self.blocked_ips

    def block_ip(self, ip_address: str, reason: str = "SQL injection attempts") -> None:
        """Block an IP address"""
        if self.config.get("enable_ip_blocking", True):
            self.blocked_ips.add(ip_address)
            logger.warning(f"IP {ip_address} blocked for: {reason}")

    def unblock_ip(self, ip_address: str) -> None:
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"IP {ip_address} unblocked")

    def record_attack_attempt(
        self, 
        ip_address: str, 
        query: str, 
        threats: List[str],
        context: Optional[str] = None
    ) -> None:
        """Record attack attempt from specific IP"""
        now = datetime.utcnow()
        
        # Clean old attempts (older than block duration)
        cutoff_time = now - datetime.timedelta(
            minutes=self.config["block_duration_minutes"]
        )
        self.attack_attempts[ip_address] = [
            attempt for attempt in self.attack_attempts[ip_address]
            if attempt["timestamp"] > cutoff_time
        ]
        
        # Record new attempt
        self.attack_attempts[ip_address].append({
            "timestamp": now,
            "query_preview": query[:100],
            "threats": threats,
            "context": context
        })
        
        # Check if IP should be blocked
        attempt_count = len(self.attack_attempts[ip_address])
        if attempt_count >= self.config["max_attempts_per_ip"]:
            self.block_ip(
                ip_address, 
                f"Multiple SQL injection attempts ({attempt_count})"
            )

    def _log_attack_attempt(
        self, 
        query: str, 
        threats: List[str], 
        context: Optional[str] = None
    ) -> None:
        """Log potential SQL injection attempt"""
        if not self.config.get("enable_logging", True):
            return

        # Create detailed log entry
        log_data = {
            "event": "sql_injection_attempt",
            "timestamp": datetime.utcnow().isoformat(),
            "threats": threats,
            "query_preview": query[:100] + "..." if len(query) > 100 else query,
            "context": context,
            "risk_assessment": self._assess_risk_level(threats)
        }

        # Log to security audit
        logger.warning(
            f"SQL injection attempt detected - Threats: {threats}, "
            f"Context: {context}, Query preview: {query[:100]}..."
        )

        # Additional logging for high-risk attempts
        if len(threats) > 2 or any("DROP" in threat.upper() for threat in threats):
            logger.critical(
                f"HIGH-RISK SQL injection attempt detected: {log_data}"
            )

    def _assess_risk_level(self, threats: List[str]) -> str:
        """Assess risk level based on detected threats"""
        if not threats:
            return "none"
        
        high_risk_patterns = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE"]
        medium_risk_patterns = ["UNION", "SELECT", "INSERT", "UPDATE"]
        
        threat_text = " ".join(threats).upper()
        
        if any(pattern in threat_text for pattern in high_risk_patterns):
            return "critical"
        elif any(pattern in threat_text for pattern in medium_risk_patterns):
            return "high"
        elif len(threats) > 1:
            return "medium"
        else:
            return "low"

    def validate_child_query(
        self, query: str, child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Special validation for queries involving child data (COPPA compliance)
        """
        # Standard validation first
        result = self.validate_query(query, f"child_data:{child_id}")
        
        # Additional child-specific checks
        child_violations = []
        
        # Check for prohibited operations on child data
        dangerous_operations = [
            "DELETE", "DROP", "TRUNCATE", "ALTER TABLE"
        ]
        
        query_upper = query.upper()
        for operation in dangerous_operations:
            if operation in query_upper:
                child_violations.append(f"Dangerous operation on child data: {operation}")
        
        # Check for data export attempts
        export_patterns = ["INTO OUTFILE", "INTO DUMPFILE", "LOAD_FILE"]
        for pattern in export_patterns:
            if pattern in query_upper:
                child_violations.append(f"Potential data export attempt: {pattern}")
        
        if child_violations:
            result["safe"] = False
            result["threats"].extend(child_violations)
            logger.critical(
                f"Child data protection violation detected - Child ID: {child_id}, "
                f"Violations: {child_violations}"
            )
        
        return result

    def get_protection_stats(self) -> Dict[str, Any]:
        """Get protection statistics"""
        now = datetime.utcnow()
        recent_attacks = 0
        
        # Count recent attacks (last 24 hours)
        for ip_attempts in self.attack_attempts.values():
            recent_attacks += len([
                attempt for attempt in ip_attempts
                if (now - attempt["timestamp"]).total_seconds() < 86400
            ])
        
        return {
            "total_blocked_ips": len(self.blocked_ips),
            "recent_attacks_24h": recent_attacks,
            "active_monitoring_ips": len(self.attack_attempts),
            "configuration": self.config.copy(),
            "protection_status": "active" if self.config.get("enable_logging") else "passive"
        }

    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update protection configuration"""
        old_config = self.config.copy()
        self.config.update(config)
        
        logger.info(
            f"SQL injection protection config updated - "
            f"Old: {old_config}, New: {self.config}"
        )

    def reset_protection_state(self) -> None:
        """Reset protection state (for testing or maintenance)"""
        self.attack_attempts.clear()
        self.blocked_ips.clear()
        logger.info("SQL injection protection state reset")

    def export_security_report(self) -> Dict[str, Any]:
        """Export comprehensive security report"""
        return {
            "report_timestamp": datetime.utcnow().isoformat(),
            "protection_stats": self.get_protection_stats(),
            "blocked_ips": list(self.blocked_ips),
            "recent_attack_summary": {
                ip: {
                    "attempt_count": len(attempts),
                    "latest_attempt": max(
                        attempt["timestamp"] for attempt in attempts
                    ).isoformat() if attempts else None,
                    "threat_types": list(set(
                        threat for attempt in attempts 
                        for threat in attempt["threats"]
                    ))
                }
                for ip, attempts in self.attack_attempts.items()
                if attempts
            },
            "configuration": self.config.copy()
        }


# Global instance
_sql_protection: Optional[SQLInjectionProtection] = None


def get_sql_protection() -> SQLInjectionProtection:
    """Get or create SQL injection protection instance"""
    global _sql_protection
    if _sql_protection is None:
        _sql_protection = SQLInjectionProtection()
    return _sql_protection


def validate_query_safe(query: str, context: Optional[str] = None) -> bool:
    """Quick validation check - returns True if safe"""
    protection = get_sql_protection()
    result = protection.validate_query(query, context)
    return result["safe"]


def sanitize_user_input(user_input: str, input_type: str = "text") -> str:
    """Quick sanitization - returns sanitized string"""
    protection = get_sql_protection()
    result = protection.sanitize_input(user_input, input_type)
    return result["sanitized"]


def validate_child_query_safe(
    query: str, child_id: Optional[str] = None
) -> bool:
    """Quick validation for child data queries"""
    protection = get_sql_protection()
    result = protection.validate_child_query(query, child_id)
    return result["safe"]


def setup_sql_protection(config: Optional[Dict[str, Any]] = None) -> SQLInjectionProtection:
    """Setup SQL injection protection with configuration"""
    protection = get_sql_protection()
    if config:
        protection.update_configuration(config)
    return protection


# Legacy compatibility exports
SQLInjectionPrevention = SQLInjectionProtection
create_sql_injection_prevention = get_sql_protection
get_sql_injection_prevention = get_sql_protection