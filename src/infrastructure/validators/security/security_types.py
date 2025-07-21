from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

class ThreatSeverity(str):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class SecurityThreat:
    threat_type: str
    severity: str  # Use ThreatSeverity constants for consistency
    field_name: str
    value: Optional[str] = None
    description: Optional[str] = ""
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self):
        return (
            f"[{self.severity.upper()}] {self.threat_type} in {self.field_name} "
            f"value={self.value!r}: {self.description}"
        )

@dataclass
class InputValidationResult:
    is_valid: bool
    threats: List[SecurityThreat] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    child_safety_violations: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add_threat(self, threat: SecurityThreat):
        self.threats.append(threat)
        if threat.severity in ("critical", "high"):
            self.is_valid = False

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_child_safety_violation(self, violation: str):
        self.child_safety_violations.append(violation)
        self.is_valid = False

    @property
    def threat_types(self):
        return [t.threat_type for t in self.threats]

    @property
    def max_severity(self):
        severities = [t.severity for t in self.threats]
        if "critical" in severities:
            return "critical"
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        if "low" in severities:
            return "low"
        return "none"

# Shortcuts for backward compatibility if needed
ValidationResult = InputValidationResult
