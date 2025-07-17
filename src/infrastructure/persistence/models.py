"""
from src.infrastructure.persistence.models import (
    """
    SQLAlchemy Models - LEGACY COMPATIBILITY FILE
    Enterprise - grade database models for AI Teddy Bear system
    NOTE: This file maintains backward compatibility while new modular structure
    is in src / infrastructure / persistence / models / package
    """
    # Import all models from the new modular structure for backward compatibility
    Base,
    ParentModel,
    ChildModel,
    ConversationModel,
    MessageModel,
    ConsentModel,
    SafetyEventModel,
    ConsentType,
    SafetyEventType
)
# Export all models for backward compatibility
__all__ = [
    "Base",
    "ParentModel",
    "ChildModel",
    "ConversationModel",
    "MessageModel",
    "ConsentModel",
    "SafetyEventModel",
    "ConsentType",
    "SafetyEventType"
]