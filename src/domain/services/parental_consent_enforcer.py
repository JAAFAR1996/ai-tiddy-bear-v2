"""Parental Consent Enforcement Service
Ensures parental consent is properly validated for all child operations.
"""

from datetime import datetime
from typing import Any

from src.domain.interfaces.logging_interface import (
    DomainLoggerInterface,
    NullDomainLogger,
)
from src.domain.models.consent_models import ConsentRecord, ConsentStatus, ConsentType
from src.domain.services.coppa_age_validation import (
    AgeValidationResult,
    COPPAAgeValidator,
)


class ParentalConsentEnforcer:
    """Enforces parental consent requirements across all operations."""

    def __init__(self, logger: DomainLoggerInterface = None) -> None:
        self._logger = logger or NullDomainLogger()
        self.required_consents = self._initialize_consent_requirements()
        self.consent_cache: dict[str, dict[ConsentType, ConsentRecord]] = {}

    def _initialize_consent_requirements(self) -> dict[str, set[ConsentType]]:
        """Initialize consent requirements by age group."""
        return {
            # Children under 13 (COPPA applies) - Strict requirements
            "valid_child": {
                ConsentType.DATA_COLLECTION,
                ConsentType.VOICE_RECORDING,
                ConsentType.INTERACTION_LOGGING,
                ConsentType.ANALYTICS_COLLECTION,
                ConsentType.PROFILE_CREATION,
                ConsentType.AUDIO_PROCESSING,
                ConsentType.CONVERSATION_STORAGE,
                ConsentType.SAFETY_MONITORING,
                ConsentType.THIRD_PARTY_SHARING,
                ConsentType.MARKETING_COMMUNICATIONS,
            },
            # Teens 13-17 - Modified requirements
            "valid_teen": {
                ConsentType.DATA_COLLECTION,
                ConsentType.VOICE_RECORDING,
                ConsentType.PROFILE_CREATION,
                ConsentType.THIRD_PARTY_SHARING,
                ConsentType.MARKETING_COMMUNICATIONS,
            },
            # Adults 18+ - Minimal requirements
            "valid_adult": set(),  # No parental consent required
        }

    def get_required_consents(self, child_age: int) -> set[ConsentType]:
        """Get required consents for a child's age.

        Args:
            child_age: Child's age in years
        Returns:
            Set of required consent types

        """
        age_validation = COPPAAgeValidator.validate_age(child_age)
        if age_validation == AgeValidationResult.VALID_CHILD:
            age_group = "valid_child"
        elif age_validation == AgeValidationResult.VALID_TEEN:
            age_group = "valid_teen"
        elif age_validation == AgeValidationResult.VALID_ADULT:
            age_group = "valid_adult"
        else:
            # For invalid ages, use most restrictive requirements
            age_group = "valid_child"
        return self.required_consents.get(age_group, set())

    def validate_consent_for_operation(
        self,
        child_id: str,
        child_age: int,
        operation_type: ConsentType,
        consent_records: list[ConsentRecord],
    ) -> dict[str, Any]:
        """Validate if parental consent exists for a specific operation.

        Args:
            child_id: Child identifier
            child_age: Child's age in years
            operation_type: Type of operation requiring consent
            consent_records: Available consent records
        Returns:
            Validation result with consent status

        """
        required_consents = self.get_required_consents(child_age)
        # Check if consent is required for this age group
        if operation_type not in required_consents:
            return {
                "consent_required": False,
                "consent_status": ConsentStatus.NOT_REQUIRED.value,
                "can_proceed": True,
                "message": "Parental consent not required for this age group",
            }
        # Find relevant consent record
        consent_record = self._find_consent_record(consent_records, operation_type)
        if not consent_record:
            return {
                "consent_required": True,
                "consent_status": ConsentStatus.PENDING.value,
                "can_proceed": False,
                "message": f"Parental consent required for {operation_type.value}",
                "required_action": "obtain_parental_consent",
            }
        # Check consent status and expiration
        consent_valid = self._is_consent_valid(consent_record)
        if not consent_valid:
            return {
                "consent_required": True,
                "consent_status": consent_record.status.value,
                "can_proceed": False,
                "message": f"Parental consent for {operation_type.value} is {consent_record.status.value}",
                "consent_record": self._consent_record_to_dict(consent_record),
                "required_action": "renew_parental_consent",
            }
        return {
            "consent_required": True,
            "consent_status": ConsentStatus.GRANTED.value,
            "can_proceed": True,
            "message": f"Valid parental consent found for {operation_type.value}",
            "consent_record": self._consent_record_to_dict(consent_record),
        }

    def validate_all_required_consents(
        self,
        child_id: str,
        child_age: int,
        consent_records: list[ConsentRecord],
    ) -> dict[str, Any]:
        """Validate all required consents for a child.

        Args:
            child_id: Child identifier
            child_age: Child's age in years
            consent_records: Available consent records
        Returns:
            Complete validation results

        """
        required_consents = self.get_required_consents(child_age)
        if not required_consents:
            return {
                "all_consents_valid": True,
                "missing_consents": [],
                "expired_consents": [],
                "valid_consents": [],
                "can_interact": True,
                "message": "No parental consent required for this age group",
            }
        validation_results = {}
        valid_consents = []
        missing_consents = []
        expired_consents = []
        for consent_type in required_consents:
            result = self.validate_consent_for_operation(
                child_id,
                child_age,
                consent_type,
                consent_records,
            )
            validation_results[consent_type.value] = result
            if result["can_proceed"]:
                valid_consents.append(consent_type.value)
            elif result["consent_status"] == ConsentStatus.PENDING.value:
                missing_consents.append(consent_type.value)
            else:
                expired_consents.append(consent_type.value)
        all_valid = len(missing_consents) == 0 and len(expired_consents) == 0
        return {
            "all_consents_valid": all_valid,
            "missing_consents": missing_consents,
            "expired_consents": expired_consents,
            "valid_consents": valid_consents,
            "can_interact": all_valid,
            "detailed_results": validation_results,
            "coppa_applicable": COPPAAgeValidator.is_coppa_applicable(child_age),
            "message": self._generate_consent_message(
                all_valid,
                missing_consents,
                expired_consents,
            ),
        }

    def _find_consent_record(
        self,
        consent_records: list[ConsentRecord],
        consent_type: ConsentType,
    ) -> ConsentRecord | None:
        """Find consent record for specific type."""
        for record in consent_records:
            if record.consent_type == consent_type:
                return record
        return None

    def _is_consent_valid(self, consent_record: ConsentRecord) -> bool:
        """Check if consent record is valid and not expired."""
        if consent_record.status != ConsentStatus.GRANTED:
            return False
        return not (consent_record.expires_at and datetime.utcnow() > consent_record.expires_at)

    def _consent_record_to_dict(self, record: ConsentRecord) -> dict[str, Any]:
        """Convert consent record to dictionary."""
        return {
            "consent_id": record.consent_id,
            "consent_type": record.consent_type.value,
            "status": record.status.value,
            "granted_at": record.granted_at.isoformat() if record.granted_at else None,
            "expires_at": record.expires_at.isoformat() if record.expires_at else None,
            "verification_method": record.verification_method,
        }

    def _generate_consent_message(
        self,
        all_valid: bool,
        missing_consents: list[str],
        expired_consents: list[str],
    ) -> str:
        """Generate human-readable consent status message."""
        if all_valid:
            return "All required parental consents are valid"
        messages = []
        if missing_consents:
            messages.append(f"Missing consent for: {', '.join(missing_consents)}")
        if expired_consents:
            messages.append(f"Expired consent for: {', '.join(expired_consents)}")
        return "; ".join(messages)

    def get_consent_requirements_summary(self, child_age: int) -> dict[str, Any]:
        """Get summary of consent requirements for a child's age.

        Args:
            child_age: Child's age in years
        Returns:
            Summary of consent requirements

        """
        required_consents = self.get_required_consents(child_age)
        age_validation = COPPAAgeValidator.validate_age(child_age)
        return {
            "child_age": child_age,
            "age_validation": age_validation.value,
            "coppa_applicable": COPPAAgeValidator.is_coppa_applicable(child_age),
            "consent_required": len(required_consents) > 0,
            "required_consent_types": [consent.value for consent in required_consents],
            "total_required_consents": len(required_consents),
            "compliance_level": self._get_compliance_level(age_validation),
            "recommendations": self._get_consent_recommendations(child_age),
        }

    def _get_compliance_level(self, age_validation: AgeValidationResult) -> str:
        """Get compliance level based on age validation."""
        if age_validation == AgeValidationResult.VALID_CHILD:
            return "strict_coppa_compliance"
        if age_validation == AgeValidationResult.VALID_TEEN:
            return "moderate_parental_oversight"
        if age_validation == AgeValidationResult.VALID_ADULT:
            return "standard_privacy_protection"
        return "blocked_interaction"

    def _get_consent_recommendations(self, child_age: int) -> list[str]:
        """Get recommendations for consent management."""
        recommendations = []
        if COPPAAgeValidator.is_coppa_applicable(child_age):
            recommendations.extend(
                [
                    "Obtain verifiable parental consent before any data collection",
                    "Implement consent expiration and renewal processes",
                    "Provide easy consent withdrawal mechanisms for parents",
                    "Maintain detailed audit logs of all consent activities",
                    "Use secure verification methods (email + additional verification)",
                ],
            )
        elif child_age < 18:
            recommendations.extend(
                [
                    "Consider obtaining parental consent for enhanced protection",
                    "Implement privacy-by-design for teen users",
                    "Provide parental visibility into teen's interactions",
                ],
            )
        return recommendations
