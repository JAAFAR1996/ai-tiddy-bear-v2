"""Centralized Data Retention Service for COPPA Compliance
Ensures consistent data retention policies across the AI Teddy Bear system.
"""

from datetime import datetime, timedelta
from typing import Any

from src.domain.interfaces.logging_interface import (
    DomainLoggerInterface,
    NullDomainLogger,
)
from src.domain.models.data_retention_models import DataType, RetentionPolicy
from src.domain.services.coppa_age_validation import (
    AgeValidationResult,
    COPPAAgeValidator,
)


class COPPADataRetentionService:
    """Centralized data retention service with COPPA compliance."""

    def __init__(self, logger: DomainLoggerInterface = None) -> None:
        self._logger = logger or NullDomainLogger()
        self.policies = self._initialize_retention_policies()

    def _initialize_retention_policies(
        self,
    ) -> dict[str, dict[DataType, RetentionPolicy]]:
        """Initialize retention policies by age group and data type."""
        policies = {
            # Children under 13 (COPPA applies)
            "valid_child": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA,
                    30,
                    "valid_child",
                    True,
                    True,
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS,
                    7,
                    "valid_child",
                    True,
                    True,
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS,
                    60,
                    "valid_child",
                    True,
                    True,
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA,
                    90,
                    "valid_child",
                    True,
                    True,
                ),
                DataType.SAFETY_LOGS: RetentionPolicy(
                    DataType.SAFETY_LOGS,
                    365,
                    "valid_child",
                    False,
                    True,  # Keep for safety
                ),
                DataType.CONSENT_RECORDS: RetentionPolicy(
                    DataType.CONSENT_RECORDS,
                    2555,
                    "valid_child",
                    False,
                    False,  # 7 years
                ),
                DataType.AUDIT_LOGS: RetentionPolicy(
                    DataType.AUDIT_LOGS,
                    2555,
                    "valid_child",
                    False,
                    False,  # 7 years
                ),
                DataType.PROFILE_DATA: RetentionPolicy(
                    DataType.PROFILE_DATA,
                    90,
                    "valid_child",
                    True,
                    True,
                ),
            },
            # Teens 13-17 (Modified requirements)
            "valid_teen": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA,
                    90,
                    "valid_teen",
                    True,
                    True,
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS,
                    30,
                    "valid_teen",
                    True,
                    True,
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS,
                    180,
                    "valid_teen",
                    True,
                    True,
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA,
                    365,
                    "valid_teen",
                    True,
                    True,
                ),
                DataType.SAFETY_LOGS: RetentionPolicy(
                    DataType.SAFETY_LOGS,
                    730,
                    "valid_teen",
                    False,
                    True,  # 2 years
                ),
                DataType.CONSENT_RECORDS: RetentionPolicy(
                    DataType.CONSENT_RECORDS,
                    2555,
                    "valid_teen",
                    False,
                    False,  # 7 years
                ),
                DataType.AUDIT_LOGS: RetentionPolicy(
                    DataType.AUDIT_LOGS,
                    2555,
                    "valid_teen",
                    False,
                    False,  # 7 years
                ),
                DataType.PROFILE_DATA: RetentionPolicy(
                    DataType.PROFILE_DATA,
                    365,
                    "valid_teen",
                    True,
                    True,
                ),
            },
            # Adults 18+ (Standard requirements)
            "valid_adult": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA,
                    365,
                    "valid_adult",
                    True,
                    False,
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS,
                    90,
                    "valid_adult",
                    True,
                    False,
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS,
                    365,
                    "valid_adult",
                    True,
                    False,
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA,
                    730,
                    "valid_adult",
                    True,
                    False,  # 2 years
                ),
                DataType.SAFETY_LOGS: RetentionPolicy(
                    DataType.SAFETY_LOGS,
                    1095,
                    "valid_adult",
                    False,
                    False,  # 3 years
                ),
                DataType.CONSENT_RECORDS: RetentionPolicy(
                    DataType.CONSENT_RECORDS,
                    2555,
                    "valid_adult",
                    False,
                    False,  # 7 years
                ),
                DataType.AUDIT_LOGS: RetentionPolicy(
                    DataType.AUDIT_LOGS,
                    2555,
                    "valid_adult",
                    False,
                    False,  # 7 years
                ),
                DataType.PROFILE_DATA: RetentionPolicy(
                    DataType.PROFILE_DATA,
                    1095,
                    "valid_adult",
                    True,
                    False,  # 3 years
                ),
            },
        }
        return policies

    def get_retention_policy(
        self,
        child_age: int,
        data_type: DataType,
    ) -> RetentionPolicy | None:
        """Get retention policy for specific child age and data type.

        Args:
            child_age: Child's age in years
            data_type: Type of data
        Returns:
            RetentionPolicy for the age group and data type

        """
        age_validation = COPPAAgeValidator.validate_age(child_age)
        if age_validation == AgeValidationResult.VALID_CHILD:
            age_group = "valid_child"
        elif age_validation == AgeValidationResult.VALID_TEEN:
            age_group = "valid_teen"
        elif age_validation == AgeValidationResult.VALID_ADULT:
            age_group = "valid_adult"
        else:
            # For invalid ages, use most restrictive policy
            age_group = "valid_child"
        return self.policies.get(age_group, {}).get(
            data_type,
            90,
        )  # Default 90 days for COPPA compliance

    def calculate_deletion_date(
        self,
        child_age: int,
        data_type: DataType,
        created_at: datetime,
    ) -> datetime:
        """Calculate when data should be deleted based on retention policy.

        Args:
            child_age: Child's age in years
            data_type: Type of data
            created_at: When the data was created
        Returns:
            Datetime when data should be deleted

        """
        policy = self.get_retention_policy(child_age, data_type)
        if not policy:
            # Default to most restrictive (30 days) for unknown policies
            retention_days = 30
        else:
            retention_days = policy.retention_days
        return created_at + timedelta(days=retention_days)

    def should_delete_data(
        self,
        child_age: int,
        data_type: DataType,
        created_at: datetime,
    ) -> bool:
        """Check if data should be deleted based on retention policy.

        Args:
            child_age: Child's age in years
            data_type: Type of data
            created_at: When the data was created
        Returns:
            True if data should be deleted

        """
        deletion_date = self.calculate_deletion_date(
            child_age, data_type, created_at
        )
        return datetime.utcnow() >= deletion_date

    def get_retention_summary(self, child_age: int) -> dict[str, Any]:
        """Get retention policy summary for a child's age.

        Args:
            child_age: Child's age in years
        Returns:
            Dictionary with retention policy summary

        """
        age_validation = COPPAAgeValidator.validate_age(child_age)
        if age_validation == AgeValidationResult.VALID_CHILD:
            age_group = "valid_child"
        elif age_validation == AgeValidationResult.VALID_TEEN:
            age_group = "valid_teen"
        elif age_validation == AgeValidationResult.VALID_ADULT:
            age_group = "valid_adult"
        else:
            age_group = "valid_child"  # Most restrictive
        policies = self.policies.get(age_group, {})
        summary = {
            "child_age": child_age,
            "age_group": age_group,
            "coppa_applicable": COPPAAgeValidator.is_coppa_applicable(
                child_age
            ),
            "policies": {},
        }
        for data_type, policy in policies.items():
            summary["policies"][data_type.value] = {
                "retention_days": policy.retention_days,
                "auto_delete": policy.auto_delete,
                "requires_consent": policy.requires_consent,
                "retention_period_human": self._format_retention_period(
                    policy.retention_days,
                ),
            }
        return summary

    def _format_retention_period(self, days: int) -> str:
        """Format retention period in human-readable format."""
        if days < 30:
            return f"{days} days"
        if days < 365:
            months = round(days / 30)
            return f"{months} month{'s' if months != 1 else ''}"
        years = round(days / 365)
        return f"{years} year{'s' if years != 1 else ''}"

    def validate_retention_compliance(self, child_age: int) -> dict[str, Any]:
        """Validate that retention policies comply with regulations.

        Args:
            child_age: Child's age in years
        Returns:
            Validation results

        """
        is_coppa_applicable = COPPAAgeValidator.is_coppa_applicable(child_age)
        retention_summary = self.get_retention_summary(child_age)
        compliance_issues = []
        # Check COPPA compliance for children under 13
        if is_coppa_applicable:
            conversation_policy = self.get_retention_policy(
                child_age,
                DataType.CONVERSATION_DATA,
            )
            voice_policy = self.get_retention_policy(
                child_age,
                DataType.VOICE_RECORDINGS,
            )
            if conversation_policy and conversation_policy.retention_days > 90:
                compliance_issues.append(
                    "Conversation data retention exceeds recommended 90 days for COPPA",
                )
            if voice_policy and voice_policy.retention_days > 30:
                compliance_issues.append(
                    "Voice recording retention exceeds recommended 30 days for COPPA",
                )
        return {
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "recommendations": self._get_compliance_recommendations(child_age),
            "retention_summary": retention_summary,
        }

    def _get_compliance_recommendations(self, child_age: int) -> list[str]:
        """Get compliance recommendations based on child age."""
        recommendations = []
        if COPPAAgeValidator.is_coppa_applicable(child_age):
            recommendations.extend(
                [
                    "Implement automatic data deletion for children under 13",
                    "Obtain verifiable parental consent before data collection",
                    "Minimize data collection to what is necessary for service",
                    "Provide clear data deletion mechanisms for parents",
                    "Maintain audit logs of all data operations",
                ],
            )
        return recommendations
