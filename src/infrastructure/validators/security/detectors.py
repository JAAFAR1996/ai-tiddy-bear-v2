import re

from .security_patterns import SecurityPatterns
from .security_types import SecurityThreat


class ThreatDetectors(SecurityPatterns):
    async def detect_sql_injection(self, text, field):
        threats = []
        for pattern in self.SQLI_PATTERNS:
            if re.search(pattern, text):
                threats.append(
                    SecurityThreat(
                        threat_type="sql_injection",
                        severity="high",
                        field_name=field,
                        value=text,
                        description=f"Pattern matched: {pattern}",
                    )
                )
        return threats

    async def detect_xss(self, text, field):
        threats = []
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text):
                threats.append(
                    SecurityThreat(
                        threat_type="xss",
                        severity="high",
                        field_name=field,
                        value=text,
                        description=f"Pattern matched: {pattern}",
                    )
                )
        return threats

    async def detect_path_traversal(self, text, field):
        return []

    async def detect_command_injection(self, text, field):
        return []

    async def detect_ldap_injection(self, text, field):
        return []

    async def detect_template_injection(self, text, field):
        return []

    async def detect_inappropriate_content(self, text, field):
        return []

    async def detect_pii(self, text, field):
        return []

    async def detect_encoding_attacks(self, text, field):
        return []
