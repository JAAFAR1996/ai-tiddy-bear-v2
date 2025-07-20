"""Security threat detection logic for input validation."""

import re

from .core import SecurityThreat

try:
    from .patterns import SecurityPatterns
except ImportError:
    # Fallback implementation if patterns module is not available
    import re

    class SecurityPatterns:
        """Fallback security patterns for threat detection."""

        def __init__(self):
            # SQL injection patterns
            self.sql_patterns = [
                re.compile(
                    r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b",
                    re.IGNORECASE,
                ),
                re.compile(r"(\'\s*(OR|AND)\s*\')", re.IGNORECASE),
                re.compile(r"(1\s*=\s*1|0\s*=\s*0)", re.IGNORECASE),
                re.compile(r"(\bUNION\s+SELECT\b)", re.IGNORECASE),
            ]

            # XSS patterns
            self.xss_patterns = [
                re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
                re.compile(r"javascript:", re.IGNORECASE),
                re.compile(r"on\w+\s*=", re.IGNORECASE),
                re.compile(r"<iframe[^>]*>", re.IGNORECASE),
            ]

            # Path traversal patterns
            self.path_traversal_patterns = [
                re.compile(r"\.\./", re.IGNORECASE),
                re.compile(r"\.\.\\", re.IGNORECASE),
                re.compile(r"%2e%2e%2f", re.IGNORECASE),
                re.compile(r"%2e%2e\\", re.IGNORECASE),
            ]

            # Command injection patterns
            self.command_patterns = [
                re.compile(r"[;&|`$()]", re.IGNORECASE),
                re.compile(r"\b(ls|cat|grep|wget|curl|rm|mv|cp)\b", re.IGNORECASE),
                re.compile(r"(\|\s*\w+)", re.IGNORECASE),
            ]

            # LDAP injection patterns
            self.ldap_patterns = [
                re.compile(r"[()&|!]", re.IGNORECASE),
                re.compile(r"\*\s*\)", re.IGNORECASE),
            ]

            # Template injection patterns
            self.template_patterns = [
                re.compile(r"\{\{.*?\}\}", re.IGNORECASE),
                re.compile(r"\$\{.*?\}", re.IGNORECASE),
                re.compile(r"<%.*?%>", re.IGNORECASE),
            ]

            # Inappropriate content patterns (basic examples)
            self.inappropriate_patterns = [
                re.compile(r"\b(hate|violence|weapon|drug|alcohol)\b", re.IGNORECASE),
                re.compile(r"\b(kill|die|murder|suicide)\b", re.IGNORECASE),
            ]

            # PII patterns
            self.pii_patterns = [
                re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
                re.compile(
                    r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"
                ),  # Credit card
                re.compile(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                ),  # Email
                re.compile(r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b"),  # Phone number
            ]


class ThreatDetectors(SecurityPatterns):
    """Security threat detection methods."""

    def __init__(self):
        super().__init__()

    async def detect_sql_injection(self, text: str, field: str) -> list[SecurityThreat]:
        """Detect SQL injection attempts."""
        threats = []
        for pattern in self.sql_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(
                    SecurityThreat(
                        "sql_injection",
                        "critical",
                        field,
                        str(match),
                        "Potential SQL injection detected",
                    ),
                )
        return threats

    async def detect_xss(self, text: str, field: str) -> list[SecurityThreat]:
        """Detect XSS attempts."""
        threats = []
        for pattern in self.xss_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(
                    SecurityThreat(
                        "xss_attack",
                        "critical",
                        field,
                        str(match),
                        "Potential XSS attack detected",
                    ),
                )
        return threats

    async def detect_path_traversal(
        self,
        text: str,
        field: str,
    ) -> list[SecurityThreat]:
        """Detect path traversal attempts."""
        threats = []
        for pattern in self.path_traversal_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(
                    SecurityThreat(
                        "path_traversal",
                        "high",
                        field,
                        str(match),
                        "Potential path traversal detected",
                    ),
                )
        return threats

    async def detect_command_injection(
        self,
        text: str,
        field: str,
    ) -> list[SecurityThreat]:
        """Detect command injection attempts."""
        threats = []
        for pattern in self.command_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(
                    SecurityThreat(
                        "command_injection",
                        "critical",
                        field,
                        str(match),
                        "Potential command injection detected",
                    ),
                )
        return threats

    async def detect_ldap_injection(
        self,
        text: str,
        field: str,
    ) -> list[SecurityThreat]:
        """Detect LDAP injection attempts."""
        threats = []
        # Only check if it looks like LDAP query
        if any(
            ldap_keyword in text.lower()
            for ldap_keyword in ["cn=", "ou=", "dc=", "uid="]
        ):
            for pattern in self.ldap_patterns:
                matches = pattern.findall(text)
                for match in matches:
                    threats.append(
                        SecurityThreat(
                            "ldap_injection",
                            "high",
                            field,
                            str(match),
                            "Potential LDAP injection detected",
                        ),
                    )
        return threats

    async def detect_template_injection(
        self,
        text: str,
        field: str,
    ) -> list[SecurityThreat]:
        """Detect template injection attempts."""
        threats = []
        for pattern in self.template_patterns:
            matches = pattern.findall(text)
            for match in matches:
                threats.append(
                    SecurityThreat(
                        "template_injection",
                        "high",
                        field,
                        str(match),
                        "Potential template injection detected",
                    ),
                )
        return threats

    async def detect_inappropriate_content(self, text: str, field: str) -> list[str]:
        """Detect inappropriate content for children."""
        violations = []
        for pattern in self.inappropriate_patterns:
            matches = pattern.findall(text)
            for match in matches:
                violations.append(f"Inappropriate content detected in {field}: {match}")
        return violations

    async def detect_pii(self, text: str, field: str) -> list[str]:
        """Detect personally identifiable information."""
        violations = []
        for pattern in self.pii_patterns:
            matches = pattern.findall(text)
            for match in matches:
                violations.append(f"PII detected in {field}: {type(match).__name__}")
        return violations

    async def detect_encoding_attacks(
        self,
        text: str,
        field: str,
    ) -> list[SecurityThreat]:
        """Detect encoding-based attacks."""
        threats = []

        # Check for suspicious unicode characters
        suspicious_unicode = re.finditer(r"[^\x00-\x7F]", text)
        for match in suspicious_unicode:
            char = match.group()
            if ord(char) > 0x1000:  # High unicode ranges often used in attacks
                threats.append(
                    SecurityThreat(
                        "suspicious_encoding",
                        "medium",
                        field,
                        char,
                        "Suspicious unicode character detected",
                    ),
                )

        # Check for null bytes
        if "\x00" in text:
            threats.append(
                SecurityThreat(
                    "null_byte_injection",
                    "high",
                    field,
                    "\\x00",
                    "Null byte injection detected",
                ),
            )

        return threats


# Global detector instance
_threat_detector = None


def get_threat_detector() -> ThreatDetectors:
    """Get global threat detector instance."""
    global _threat_detector
    if _threat_detector is None:
        _threat_detector = ThreatDetectors()
    return _threat_detector


# Convenience functions for quick threat detection
async def detect_all_threats(text: str, field: str = "input") -> list[SecurityThreat]:
    """Detect all types of security threats in text."""
    detector = get_threat_detector()
    all_threats = []

    # Run all detection methods
    all_threats.extend(await detector.detect_sql_injection(text, field))
    all_threats.extend(await detector.detect_xss(text, field))
    all_threats.extend(await detector.detect_path_traversal(text, field))
    all_threats.extend(await detector.detect_command_injection(text, field))
    all_threats.extend(await detector.detect_ldap_injection(text, field))
    all_threats.extend(await detector.detect_template_injection(text, field))
    all_threats.extend(await detector.detect_encoding_attacks(text, field))

    return all_threats


async def is_text_safe(text: str) -> bool:
    """Quick check if text is safe from security threats."""
    threats = await detect_all_threats(text)
    return len(threats) == 0
