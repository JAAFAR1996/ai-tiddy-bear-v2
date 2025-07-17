from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class ConsentType(Enum):
    """Types of parental consent required."""
    DATA_COLLECTION = "data_collection"
    VOICE_RECORDING = "voice_recording"
    INTERACTION_LOGGING = "interaction_logging"
    ANALYTICS_COLLECTION = "analytics_collection"
    PROFILE_CREATION = "profile_creation"
    AUDIO_PROCESSING = "audio_processing"
    CONVERSATION_STORAGE = "conversation_storage"
    SAFETY_MONITORING = "safety_monitoring"
    THIRD_PARTY_SHARING = "third_party_sharing"
    MARKETING_COMMUNICATIONS = "marketing_communications"


class ConsentStatus(Enum):
    """Status of parental consent."""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    NOT_REQUIRED = "not_required"


class ConsentRecord:
    """Record of parental consent."""
    
    def __init__(
        self,
        consent_id: str,
        child_id: str,
        parent_id: str,
        consent_type: ConsentType,
        status: ConsentStatus,
        granted_at: Optional[datetime]=None,
        expires_at: Optional[datetime]=None,
        verification_method: str="email",
        consent_text: str="",
        metadata: Optional[Dict[str, Any]]=None,
    ) -> None:
        self.consent_id = consent_id
        self.child_id = child_id
        self.parent_id = parent_id
        self.consent_type = consent_type
        self.status = status
        self.granted_at = granted_at or datetime.utcnow()
        self.expires_at = expires_at
        self.verification_method = verification_method
        self.consent_text = consent_text
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()