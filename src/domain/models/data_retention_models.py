from enum import Enum


class DataType(Enum):
    """Types of data with different retention requirements."""

    CONVERSATION_DATA = "conversation_data"
    VOICE_RECORDINGS = "voice_recordings"
    INTERACTION_LOGS = "interaction_logs"
    ANALYTICS_DATA = "analytics_data"
    SAFETY_LOGS = "safety_logs"
    CONSENT_RECORDS = "consent_records"
    AUDIT_LOGS = "audit_logs"
    PROFILE_DATA = "profile_data"


class RetentionPolicy:
    """Data retention policy configuration."""

    def __init__(
        self,
        data_type: DataType,
        retention_days: int,
        child_age_group: str,
        auto_delete: bool = True,
        requires_consent: bool = True,
    ) -> None:
        self.data_type = data_type
        self.retention_days = retention_days
        self.child_age_group = child_age_group
        self.auto_delete = auto_delete
        self.requires_consent = requires_consent
