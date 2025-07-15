"""
Manages data retention policies to ensure compliance with regulations.

This service defines and enforces data retention policies based on age groups
and data types, with a strong focus on COPPA compliance. It provides
functionalities to determine the retention period for various data categories
and to check if specific data should be retained or deleted.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.domain.interfaces.logging_interface import (
    DomainLoggerInterface,
    NullDomainLogger,
)
from src.domain.models.data_retention_models import DataType, RetentionPolicy
from src.domain.services.coppa_age_validation import (
    AgeValidationResult,
    COPPAAgeValidator,
)


class DataRetentionService:
    """Centralized data retention service with COPPA compliance."""

    def __init__(self, logger: DomainLoggerInterface = None) -> None:
        """Initializes the data retention service."""
        self._logger = logger or NullDomainLogger()
        self.policies = self._initialize_retention_policies()

    def _initialize_retention_policies(
        self,
    ) -> Dict[str, Dict[DataType, RetentionPolicy]]:
        """Initializes retention policies by age group and data type."""
        policies = {
            # Children under 13 (COPPA applies)
            "valid_child": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA, 30, "valid_child", True, True
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS, 7, "valid_child", True, True
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS, 60, "valid_child", True, True
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA, 90, "valid_child", True, True
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
            },
            # Teens 13-17
            "valid_teen": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA, 90, "valid_teen", False, True
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS, 30, "valid_teen", False, True
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS, 180, "valid_teen", False, True
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA, 365, "valid_teen", False, True
                ),
                DataType.SAFETY_LOGS: RetentionPolicy(
                    DataType.SAFETY_LOGS, 365, "valid_teen", False, True
                ),
                DataType.CONSENT_RECORDS: RetentionPolicy(
                    DataType.CONSENT_RECORDS, 2555, "valid_teen", False, False
                ),
            },
            # Adults 18+
            "valid_adult": {
                DataType.CONVERSATION_DATA: RetentionPolicy(
                    DataType.CONVERSATION_DATA, 365, "valid_adult", False, False
                ),
                DataType.VOICE_RECORDINGS: RetentionPolicy(
                    DataType.VOICE_RECORDINGS, 90, "valid_adult", False, False
                ),
                DataType.INTERACTION_LOGS: RetentionPolicy(
                    DataType.INTERACTION_LOGS, 730, "valid_adult", False, False
                ),
                DataType.ANALYTICS_DATA: RetentionPolicy(
                    DataType.ANALYTICS_DATA, 730, "valid_adult", False, False
                ),
                DataType.SAFETY_LOGS: RetentionPolicy(
                    DataType.SAFETY_LOGS, 365, "valid_adult", False, True
                ),
                DataType.CONSENT_RECORDS: RetentionPolicy(
                    DataType.CONSENT_RECORDS, 2555, "valid_adult", False, False
                ),
            },
        }
        return policies

    def get_retention_policy(
        self, child_age: int, data_type: DataType
    ) -> Optional[RetentionPolicy]:
        """
        Retrieves the retention policy for a specific data type and child age.

        Args:
            child_age: The age of the child.
            data_type: The type of data.

        Returns:
            The matching RetentionPolicy, or None if not found.
        """
        age_validation = COPPAAgeValidator.validate_age(child_age)
        if age_validation == AgeValidationResult.CHILD:
            age_group = "valid_child"
        elif age_validation == AgeValidationResult.TEEN:
            age_group = "valid_teen"
        elif age_validation == AgeValidationResult.ADULT:
            age_group = "valid_adult"
        else:
            self._logger.warning(f"Invalid child age: {child_age}")
            return None

        return self.policies.get(age_group, {}).get(data_type)

    def check_data_retention(
        self, child_age: int, data_type: DataType, data_timestamp: datetime
    ) -> bool:
        """
        Checks if a piece of data should be retained based on its age and type.

        Args:
            child_age: The age of the child associated with the data.
            data_type: The type of data.
            data_timestamp: The timestamp when the data was created.

        Returns:
            True if the data should be retained, False otherwise.
        """
        policy = self.get_retention_policy(child_age, data_type)
        if not policy:
            return False  # No policy, default to not retaining

        if policy.indefinite_retention:
            return True

        age_of_data = datetime.now() - data_timestamp
        return age_of_data.days <= policy.retention_days

    def get_data_for_deletion(
        self, child_age: int, data_type: DataType, all_data: List[Any]
    ) -> List[Any]:
        """
        Identifies data items that are past their retention period and should be deleted.

        Args:
            child_age: The age of the child associated with the data.
            data_type: The type of data.
            all_data: A list of all data items of the specified type.

        Returns:
            A list of data items that should be deleted.
        """
        policy = self.get_retention_policy(child_age, data_type)
        if not policy or policy.indefinite_retention:
            return []

        data_to_delete = []
        for item in all_data:
            # Assuming each item has a 'timestamp' attribute
            if hasattr(item, "timestamp") and isinstance(item.timestamp, datetime):
                if (datetime.now() - item.timestamp).days > policy.retention_days:
                    data_to_delete.append(item)
            else:
                self._logger.warning(
                    f"Data item of type {data_type} missing 'timestamp' attribute or it's not a datetime object."
                )
        return data_to_delete
