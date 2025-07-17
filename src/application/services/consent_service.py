"""Manages parental consent for data collection and processing.

This service ensures compliance with regulations like COPPA by enforcing
parental consent requirements for various operations involving child data.
It provides functionalities to record, check, and revoke consent, and to
retrieve the current consent status for a child.
"""

from datetime import datetime

from src.domain.interfaces.logging_interface import (
    DomainLoggerInterface,
    NullDomainLogger,
)
from src.domain.models.consent_models import (
    ConsentRecord,
    ConsentStatus,
    ConsentType,
)
from src.domain.services.coppa_age_validation import (
    AgeValidationResult,
    COPPAAgeValidator,
)


class ConsentService:
    """Service for enforcing and managing parental consent."""

    def __init__(self, logger: DomainLoggerInterface = None) -> None:
        """Initializes the consent service."""
        self._logger = logger or NullDomainLogger()
        self.required_consents = self._initialize_consent_requirements()
        self.consent_cache: dict[str, dict[ConsentType, ConsentRecord]] = {}

    def _initialize_consent_requirements(self) -> dict[str, set[ConsentType]]:
        """Initializes consent requirements by age group."""
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
        """Gets the set of consent types required for a given child's age.

        Args:
            child_age: The age of the child.

        Returns:
            A set of required consent types.

        """
        age_validation = COPPAAgeValidator.validate_age(child_age)
        if age_validation == AgeValidationResult.CHILD:
            return self.required_consents["valid_child"]
        if age_validation == AgeValidationResult.TEEN:
            return self.required_consents["valid_teen"]
        if age_validation == AgeValidationResult.ADULT:
            return self.required_consents["valid_adult"]
        return set()  # Invalid age, no consents required

    def record_consent(
        self,
        child_id: str,
        consent_type: ConsentType,
        parent_id: str,
    ) -> ConsentRecord:
        """Records a parental consent for a specific child and consent type.

        Args:
            child_id: The ID of the child.
            consent_type: The type of consent being granted.
            parent_id: The ID of the parent granting consent.

        Returns:
            The recorded consent record.

        """
        record = ConsentRecord(
            child_id=child_id,
            parent_id=parent_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            timestamp=datetime.now(),
        )
        if child_id not in self.consent_cache:
            self.consent_cache[child_id] = {}
        self.consent_cache[child_id][consent_type] = record
        self._logger.info(
            f"Consent recorded: child_id={child_id}, consent_type={consent_type.value}",
        )
        return record

    def check_consent(self, child_id: str, consent_type: ConsentType) -> bool:
        """Checks if a specific consent has been granted for a child.

        Args:
            child_id: The ID of the child.
            consent_type: The type of consent to check.

        Returns:
            True if consent is granted, False otherwise.

        """
        consent_record = self.consent_cache.get(child_id, {}).get(consent_type)
        return (
            consent_record and consent_record.status == ConsentStatus.GRANTED
        )

    def revoke_consent(
        self,
        child_id: str,
        consent_type: ConsentType,
    ) -> ConsentRecord | None:
        """Revokes a previously granted consent for a child.

        Args:
            child_id: The ID of the child.
            consent_type: The type of consent to revoke.

        Returns:
            The revoked consent record, or None if not found.

        """
        if (
            child_id in self.consent_cache
            and consent_type in self.consent_cache[child_id]
        ):
            record = self.consent_cache[child_id][consent_type]
            record.status = ConsentStatus.REVOKED
            record.timestamp = datetime.now()
            self._logger.info(
                f"Consent revoked: child_id={child_id}, consent_type={consent_type.value}",
            )
            return record
        return None

    def get_consent_status(
        self, child_id: str
    ) -> dict[ConsentType, ConsentStatus]:
        """Retrieves the current consent status for all consent types for a child.

        Args:
            child_id: The ID of the child.

        Returns:
            A dictionary mapping consent types to their current status.

        """
        status = {}
        for consent_type in ConsentType:
            record = self.consent_cache.get(child_id, {}).get(consent_type)
            status[consent_type] = (
                record.status if record else ConsentStatus.NOT_GRANTED
            )
        return status
