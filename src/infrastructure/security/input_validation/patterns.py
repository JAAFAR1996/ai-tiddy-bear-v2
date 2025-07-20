"""Security threat detection patterns for input validation."""

import re


class SecurityPatterns:
    """Compiled security threat detection patterns."""

    def __init__(self):
        self._compile_security_patterns()
        self._setup_child_safety_patterns()

    def _compile_security_patterns(self) -> None:
        """Compile security threat detection patterns."""
        # SQL Injection patterns
        self.sql_patterns = [
            re.compile(
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                re.IGNORECASE,
            ),
            re.compile(r"(--|#|/\*|\*/)", re.IGNORECASE),
            re.compile(r"(\b(OR|AND)\s+\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"('\s*(OR|AND)\s*'\w*'\s*=\s*'\w*)", re.IGNORECASE),
            re.compile(r"(\b(EXEC|EXECUTE)\s*\()", re.IGNORECASE),
            re.compile(r"(\b(sp_|xp_)\w+)", re.IGNORECASE),
        ]

        # XSS patterns
        self.xss_patterns = [
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"<iframe[^>]*>", re.IGNORECASE),
            re.compile(r"<object[^>]*>", re.IGNORECASE),
            re.compile(r"<embed[^>]*>", re.IGNORECASE),
            re.compile(r"<link[^>]*>", re.IGNORECASE),
            re.compile(r"<meta[^>]*>", re.IGNORECASE),
            re.compile(r"document\.(write|cookie|location)", re.IGNORECASE),
            re.compile(r"window\.(location|open)", re.IGNORECASE),
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            re.compile(r"\.\.[\\\/]", re.IGNORECASE),
            re.compile(r"\.\\.%2f", re.IGNORECASE),
            re.compile(r"\.\\.%5c", re.IGNORECASE),
            re.compile(r"%2e%2e[\\\/]", re.IGNORECASE),
            re.compile(r"\.\.[/\\]", re.IGNORECASE),
        ]

        # Command injection patterns
        self.command_patterns = [
            re.compile(r"[;&|`$()]", re.IGNORECASE),
            re.compile(
                r"\b(cat|ls|ps|kill|rm|cp|mv|chmod|chown|sudo|su)\b",
                re.IGNORECASE,
            ),
            re.compile(r"\\x[0-9a-fA-F]{2}", re.IGNORECASE),
            re.compile(r"%(0[0-9a-fA-F]|[2-9a-fA-F][0-9a-fA-F])", re.IGNORECASE),
        ]

        # LDAP injection patterns
        self.ldap_patterns = [
            re.compile(r"[()&|!]", re.IGNORECASE),
            re.compile(r"\*", re.IGNORECASE),
            re.compile(r"\\[0-9a-fA-F]{2}", re.IGNORECASE),
        ]

        # Template injection patterns
        self.template_patterns = [
            re.compile(r"\{\{.*?\}\}", re.IGNORECASE),
            re.compile(r"\{%.*?%\}", re.IGNORECASE),
            re.compile(r"\$\{.*?\}", re.IGNORECASE),
            re.compile(r"<%.*?%>", re.IGNORECASE),
        ]

    def _setup_child_safety_patterns(self) -> None:
        """Setup patterns for child safety content detection."""
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            re.compile(
                r"\b(violence|blood|kill|death|murder|weapon|gun|knife)\b",
                re.IGNORECASE,
            ),
            re.compile(r"\b(drug|alcohol|cigarette|smoke|beer|wine)\b", re.IGNORECASE),
            re.compile(r"\b(sex|sexual|porn|naked|nude)\b", re.IGNORECASE),
            re.compile(r"\b(hate|racist|discrimination)\b", re.IGNORECASE),
            re.compile(r"\b(scary|horror|nightmare|terrifying)\b", re.IGNORECASE),
        ]

        # Personal information patterns (PII)
        self.pii_patterns = [
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
            re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),  # Credit card
            re.compile(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b"),  # Phone number
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
            re.compile(
                r"\b\d{1,5}\s+([A-Za-z]+\s+){1,3}(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b",
                re.IGNORECASE,
            ),  # Address
        ]

    def get_all_patterns(self) -> dict:
        """Get all compiled patterns for inspection."""
        return {
            "sql_patterns": self.sql_patterns,
            "xss_patterns": self.xss_patterns,
            "path_traversal_patterns": self.path_traversal_patterns,
            "command_patterns": self.command_patterns,
            "ldap_patterns": self.ldap_patterns,
            "template_patterns": self.template_patterns,
            "inappropriate_patterns": self.inappropriate_patterns,
            "pii_patterns": self.pii_patterns,
        }

    def test_pattern_group(self, text: str, pattern_group: str) -> list[str]:
        """Test text against a specific pattern group."""
        patterns = getattr(self, f"{pattern_group}_patterns", [])
        matches = []
        for pattern in patterns:
            found = pattern.findall(text)
            matches.extend([str(match) for match in found])
        return matches

    def is_safe_for_children(self, text: str) -> bool:
        """Quick check if text is safe for children."""
        for pattern in self.inappropriate_patterns:
            if pattern.search(text):
                return False
        return True

    def contains_pii(self, text: str) -> bool:
        """Quick check if text contains PII."""
        for pattern in self.pii_patterns:
            if pattern.search(text):
                return True
        return False


# Global patterns instance
_security_patterns = None


def get_security_patterns() -> SecurityPatterns:
    """Get global security patterns instance."""
    global _security_patterns
    if _security_patterns is None:
        _security_patterns = SecurityPatterns()
    return _security_patterns


# Convenience functions for quick pattern testing
def test_sql_injection(text: str) -> list[str]:
    """Test text for SQL injection patterns."""
    patterns = get_security_patterns()
    return patterns.test_pattern_group(text, "sql")


def test_xss_attack(text: str) -> list[str]:
    """Test text for XSS attack patterns."""
    patterns = get_security_patterns()
    return patterns.test_pattern_group(text, "xss")


def test_path_traversal(text: str) -> list[str]:
    """Test text for path traversal patterns."""
    patterns = get_security_patterns()
    return patterns.test_pattern_group(text, "path_traversal")


def test_command_injection(text: str) -> list[str]:
    """Test text for command injection patterns."""
    patterns = get_security_patterns()
    return patterns.test_pattern_group(text, "command")


def is_child_safe(text: str) -> bool:
    """Quick check if text is safe for children."""
    patterns = get_security_patterns()
    return patterns.is_safe_for_children(text)


def has_pii(text: str) -> bool:
    """Quick check if text contains personally identifiable information."""
    patterns = get_security_patterns()
    return patterns.contains_pii(text)
