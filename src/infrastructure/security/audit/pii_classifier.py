"""
PII Classification Module for Child Safety Compliance
====================================================

This module provides comprehensive PII (Personally Identifiable Information)
detection and classification specifically designed for COPPA compliance in
child-safe applications.

🛡️ CRITICAL: This classifier must NEVER log actual PII content.
Only classifications, risk levels, and non-reversible hashes are logged.
"""

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class PIIRiskLevel(Enum):
    """Risk levels for PII detection."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PIIType(Enum):
    """Types of PII that can be detected."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    IP_ADDRESS = "ip_address"
    CHILD_NAME = "child_name"
    PARENT_NAME = "parent_name"
    SCHOOL_NAME = "school_name"
    CHILD_AGE = "child_age"
    LOCATION = "location"
    VOICE_DATA = "voice_data"
    BIOMETRIC = "biometric"


@dataclass
class PIIDetectionResult:
    """Result of PII detection analysis."""

    contains_pii: bool
    risk_level: PIIRiskLevel
    detected_types: List[PIIType]
    confidence_score: float
    input_length: int
    input_hash: str
    child_specific_pii: bool


class PIIClassifier:
    """
    Advanced PII classifier with specific focus on child safety and COPPA compliance.

    🚨 SECURITY CRITICAL: This class NEVER stores or logs actual PII content.
    All analysis results contain only metadata, classifications, and hashes.
    """

    def __init__(self):
        """Initialize the PII classifier with comprehensive patterns."""
        self._init_detection_patterns()
        self._init_child_specific_patterns()
        self._init_risk_weights()

    def _init_detection_patterns(self) -> None:
        """Initialize regex patterns for PII detection."""
        self.patterns = {
            PIIType.EMAIL: [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"],
            PIIType.PHONE: [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                r"\(\d{3}\)\s*\d{3}[-.]?\d{4}",
                r"\+1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}",
            ],
            PIIType.SSN: [r"\b\d{3}-\d{2}-\d{4}\b", r"\b\d{9}\b"],
            PIIType.CREDIT_CARD: [r"\b(?:\d{4}[ -]?){3}\d{4}\b"],
            PIIType.IP_ADDRESS: [
                r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b",
            ],
            PIIType.DATE_OF_BIRTH: [
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                r"\b\d{2,4}[/-]\d{1,2}[/-]\d{1,2}\b",
            ],
        }

    def _init_child_specific_patterns(self) -> None:
        """Initialize patterns specific to child PII detection."""
        self.child_patterns = {
            PIIType.CHILD_NAME: [
                r"\bmy name is\s+([A-Z][a-z]+)\b",
                r"\bi am\s+([A-Z][a-z]+)\b",
                r"\bcall me\s+([A-Z][a-z]+)\b",
            ],
            PIIType.CHILD_AGE: [
                r"\bi am\s+(\d{1,2})\s+years?\s+old\b",
                r"\bmy age is\s+(\d{1,2})\b",
                r"\bi\'m\s+(\d{1,2})\b",
            ],
            PIIType.SCHOOL_NAME: [
                r"\bi go to\s+([A-Z][a-z\s]+school)\b",
                r"\bmy school is\s+([A-Z][a-z\s]+)\b",
            ],
            PIIType.LOCATION: [
                r"\bi live in\s+([A-Z][a-z\s,]+)\b",
                r"\bmy address is\s+([A-Z0-9][a-z0-9\s,]+)\b",
            ],
        }

    def _init_risk_weights(self) -> None:
        """Initialize risk weights for different PII types."""
        self.risk_weights = {
            PIIType.EMAIL: 0.8,
            PIIType.PHONE: 0.9,
            PIIType.SSN: 1.0,
            PIIType.CREDIT_CARD: 1.0,
            PIIType.NAME: 0.6,
            PIIType.ADDRESS: 0.9,
            PIIType.DATE_OF_BIRTH: 0.8,
            PIIType.IP_ADDRESS: 0.4,
            PIIType.CHILD_NAME: 1.0,  # CRITICAL for COPPA
            PIIType.PARENT_NAME: 0.9,
            PIIType.SCHOOL_NAME: 0.8,
            PIIType.CHILD_AGE: 0.9,  # CRITICAL for COPPA
            PIIType.LOCATION: 0.7,
            PIIType.VOICE_DATA: 1.0,  # CRITICAL for COPPA
            PIIType.BIOMETRIC: 1.0,  # CRITICAL for COPPA
        }

    def classify_input(self, input_data: str) -> PIIDetectionResult:
        """
        Classify input data for PII content and risk level.

        🛡️ SECURITY: This method NEVER stores or logs the actual input content.
        Only metadata and classifications are returned.

        Args:
            input_data: The input string to analyze

        Returns:
            PIIDetectionResult with classification metadata only
        """
        detected_types = []
        confidence_scores = []
        child_specific_detected = False

        # Analyze general PII patterns
        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    detected_types.append(pii_type)
                    confidence_scores.append(self.risk_weights[pii_type])

        # Analyze child-specific patterns (COPPA critical)
        for pii_type, patterns in self.child_patterns.items():
            for pattern in patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    detected_types.append(pii_type)
                    confidence_scores.append(self.risk_weights[pii_type])
                    child_specific_detected = True

        # Calculate overall risk level
        contains_pii = len(detected_types) > 0
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        risk_level = self._calculate_risk_level(avg_confidence, child_specific_detected)

        # Create non-reversible hash of input for audit purposes
        input_hash = hashlib.sha256(input_data.encode()).hexdigest()[:16]

        return PIIDetectionResult(
            contains_pii=contains_pii,
            risk_level=risk_level,
            detected_types=detected_types,
            confidence_score=avg_confidence,
            input_length=len(input_data),
            input_hash=input_hash,
            child_specific_pii=child_specific_detected,
        )

    def _calculate_risk_level(
        self, confidence: float, child_specific: bool
    ) -> PIIRiskLevel:
        """Calculate risk level based on confidence and child-specific detection."""
        if child_specific:
            return PIIRiskLevel.CRITICAL
        elif confidence >= 0.9:
            return PIIRiskLevel.HIGH
        elif confidence >= 0.7:
            return PIIRiskLevel.MEDIUM
        elif confidence >= 0.3:
            return PIIRiskLevel.LOW
        else:
            return PIIRiskLevel.NONE

    def contains_child_pii(self, input_data: str) -> bool:
        """Quick check if input contains child-specific PII."""
        result = self.classify_input(input_data)
        return result.child_specific_pii

    def get_safe_summary(self, input_data: str) -> Dict[str, any]:
        """
        Get a safe summary of input analysis that can be logged.

        🛡️ SECURITY: This method returns ONLY safe metadata.
        No actual input content is included in the result.
        """
        result = self.classify_input(input_data)

        return {
            "input_length": result.input_length,
            "input_hash": result.input_hash,
            "contains_pii": result.contains_pii,
            "risk_level": result.risk_level.value,
            "detected_pii_types": [t.value for t in result.detected_types],
            "confidence_score": round(result.confidence_score, 3),
            "child_specific_pii": result.child_specific_pii,
            "coppa_risk": result.child_specific_pii
            or result.risk_level in [PIIRiskLevel.HIGH, PIIRiskLevel.CRITICAL],
        }
