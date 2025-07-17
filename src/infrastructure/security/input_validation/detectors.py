"""
from typing import List
from .core import SecurityThreat
from .patterns import SecurityPatterns
"""

"""Security threat detection logic for input validation."""


class ThreatDetectors(SecurityPatterns):
    """Security threat detection methods."""
    
    async def detect_sql_injection(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect SQL injection attempts."""
        threats = []
        for pattern in self.sql_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(SecurityThreat(
                    "sql_injection", "critical", field, str(match),
                    "Potential SQL injection detected"
                ))
        return threats

    async def detect_xss(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect XSS attempts."""
        threats = []
        for pattern in self.xss_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(SecurityThreat(
                    "xss_attack", "critical", field, str(match),
                    "Potential XSS attack detected"
                ))
        return threats

    async def detect_path_traversal(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect path traversal attempts."""
        threats = []
        for pattern in self.path_traversal_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(SecurityThreat(
                    "path_traversal", "high", field, str(match),
                    "Potential path traversal detected"
                ))
        return threats

    async def detect_command_injection(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect command injection attempts."""
        threats = []
        for pattern in self.command_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(SecurityThreat(
                    "command_injection", "critical", field, str(match),
                    "Potential command injection detected"
                ))
        return threats

    async def detect_ldap_injection(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect LDAP injection attempts."""
        threats = []
        # Only check if it looks like LDAP query
        if any(ldap_keyword in text.lower() for ldap_keyword in ['cn=', 'ou=', 'dc=', 'uid=']):
            for pattern in self.ldap_patterns:
                matches = pattern.findall(text)
                for match in matches:
                    threats.append(SecurityThreat(
                        "ldap_injection", "high", field, str(match),
                        "Potential LDAP injection detected"
                    ))
        return threats

    async def detect_template_injection(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect template injection attempts."""
        threats = []
        for pattern in self.template_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(SecurityThreat(
                    "template_injection", "high", field, str(match),
                    "Potential template injection detected"
                ))
        return threats

    async def detect_inappropriate_content(self, text: str, field: str) -> List[str]:
        """Detect inappropriate content for children."""
        violations = []
        for pattern in self.inappropriate_patterns:
            matches = pattern.findall(text)
            for match in matches:
                violations.append(f"Inappropriate content detected in {field}: {match}")
        return violations

    async def detect_pii(self, text: str, field: str) -> List[str]:
        """Detect personally identifiable information."""
        violations = []
        for pattern in self.pii_patterns:
            matches = pattern.findall(text)
            for match in matches:
                violations.append(f"PII detected in {field}: {type(match).__name__}")
        return violations

    async def detect_encoding_attacks(self, text: str, field: str) -> List[SecurityThreat]:
        """Detect encoding - based attacks."""
        import re
        threats = []
        
        # Check for suspicious unicode characters
        suspicious_unicode = re.finditer(r'[^\x00-\x7F]', text)
        for match in suspicious_unicode:
            char = match.group()
            if ord(char) > 0x1000:  # High unicode ranges often used in attacks
                threats.append(SecurityThreat(
                    "suspicious_encoding", "medium", field, char,
                    "Suspicious unicode character detected"
                ))
        
        # Check for null bytes
        if '\x00' in text:
            threats.append(SecurityThreat(
                "null_byte_injection", "high", field, "\\x00",
                "Null byte injection detected"
            ))
            
        return threats