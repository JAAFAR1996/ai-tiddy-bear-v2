=== تقرير استخدامات الكلاسات المكررة ===
تاريخ التقرير: Sun Jul 20 09:37:36 +03 2025

## ConsentType
### المواقع:
src/domain/models/consent_models.py:6:class ConsentType(Enum):
src/infrastructure/persistence/models/consent_models.py:18:class ConsentType(enum.Enum):

### الاستخدامات:
src/application/services/coppa/coppa_compliance_service.py:13:from src.domain.models.consent_models import ConsentType, ConsentStatus, ConsentRecord
src/application/services/coppa/coppa_compliance_service.py:330:    def _determine_required_consents(self, age: int) -> List[ConsentType]:
src/application/services/coppa/coppa_compliance_service.py:334:                ConsentType.DATA_COLLECTION,
src/application/services/coppa/coppa_compliance_service.py:335:                ConsentType.VOICE_RECORDING,
src/application/services/coppa/coppa_compliance_service.py:336:                ConsentType.INTERACTION_LOGGING,
src/application/services/coppa/coppa_compliance_service.py:337:                ConsentType.SAFETY_MONITORING,
src/application/services/coppa/coppa_compliance_service.py:338:                ConsentType.PROFILE_CREATION
src/application/services/coppa/coppa_compliance_service.py:342:    def _generate_consent_text(self, consent_type: ConsentType, data: Dict[str, Any]) -> str:
src/application/services/coppa/coppa_compliance_service.py:345:            ConsentType.DATA_COLLECTION: (
src/application/services/coppa/coppa_compliance_service.py:349:            ConsentType.VOICE_RECORDING: (

## ErrorSeverity
### المواقع:
src/domain/exceptions/base.py:11:class ErrorSeverity(Enum):
src/infrastructure/error_handling/error_types.py:12:class ErrorSeverity(Enum):

### الاستخدامات:
src/domain/exceptions/base.py:11:class ErrorSeverity(Enum):
src/domain/exceptions/base.py:72:        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
src/domain/exceptions/base.py:92:        if self.severity == ErrorSeverity.CRITICAL:
src/domain/exceptions/base.py:96:        if self.severity == ErrorSeverity.HIGH:
src/domain/exceptions/base.py:140:            severity=ErrorSeverity.CRITICAL,
src/domain/exceptions/base.py:171:            severity=ErrorSeverity.HIGH,
src/domain/exceptions/base.py:192:            severity=ErrorSeverity.CRITICAL,
src/infrastructure/error_handling/error_types.py:12:class ErrorSeverity(Enum):
src/infrastructure/error_handling/error_types.py:38:    def __init__(self, error_type: ErrorType, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
src/infrastructure/error_handling/__init__.py:25:    ErrorSeverity,

## ValidationSeverity
### المواقع:
src/domain/schemas.py:300:class ValidationSeverity(Enum):
src/infrastructure/security/hardening/validation/validation_config.py:12:class ValidationSeverity(Enum):

### الاستخدامات:
src/domain/schemas.py:300:class ValidationSeverity(Enum):
src/infrastructure/security/hardening/input_validation.py:8:    ValidationSeverity,
src/infrastructure/security/hardening/input_validation.py:18:    "ValidationSeverity",
src/infrastructure/security/hardening/validation/sanitizer.py:13:    from .validation_config import InputValidationConfig, ValidationSeverity
src/infrastructure/security/hardening/validation/sanitizer.py:20:    class ValidationSeverity(Enum):
src/infrastructure/security/hardening/validation/sanitizer.py:30:        severity: ValidationSeverity
src/infrastructure/security/hardening/validation/sanitizer.py:49:                severity=ValidationSeverity.HIGH,
src/infrastructure/security/hardening/validation/sanitizer.py:55:                severity=ValidationSeverity.HIGH,
src/infrastructure/security/hardening/validation/sanitizer.py:61:                severity=ValidationSeverity.CRITICAL,
src/infrastructure/security/hardening/validation/sanitizer.py:185:                            ValidationSeverity.CRITICAL,

## ChildData
### المواقع:
src/application/dto/child_data.py:31:class ChildData:
src/infrastructure/security/child_data_security_manager.py:19:class ChildDataSecurityManager:
src/infrastructure/security/coppa/data_models.py:14:class ChildData(BaseModel):
src/presentation/api/endpoints/children/operations.py:255:class ChildDataTransformer:

### الاستخدامات:
src/application/dto/child_data.py:14: ChildData: COPPA-compliant child data representation
src/application/dto/child_data.py:31:class ChildData:
src/application/use_cases/manage_child_profile.py:4:from src.application.dto.child_data import ChildData
src/application/use_cases/manage_child_profile.py:29:    ) -> ChildData:
src/application/use_cases/manage_child_profile.py:34:        return ChildData(
src/application/use_cases/manage_child_profile.py:41:    async def get_child_profile(self, child_id: UUID) -> ChildData | None:
src/application/use_cases/manage_child_profile.py:44:            return ChildData(
src/application/use_cases/manage_child_profile.py:58:    ) -> ChildData | None:
src/infrastructure/security/coppa/data_models.py:14:class ChildData(BaseModel):
src/infrastructure/security/coppa/data_models.py:266:    "ChildData",

## ConversationRepository
### المواقع:
src/domain/repositories/conversation_repository.py:7:class ConversationRepository(Protocol):
src/infrastructure/persistence/conversation_repository.py:13:class ConversationRepository(ABC):

### الاستخدامات:
src/application/services/conversation_service.py:5:summaries. It interacts with the `ConversationRepository` to persist and
src/application/services/conversation_service.py:14:    ConversationRepository,
src/application/services/conversation_service.py:26:        conversation_repo: ConversationRepository,
src/domain/repositories/conversation_repository.py:7:class ConversationRepository(Protocol):
src/infrastructure/persistence/conversation_repository.py:13:class ConversationRepository(ABC):
src/infrastructure/persistence/conversation_repository.py:35:class AsyncSQLAlchemyConversationRepo(ConversationRepository):
src/infrastructure/persistence/conversation_repository.py:36:    """Async SQLAlchemy implementation of ConversationRepository."""
src/infrastructure/persistence/conversation_repository.py:150:    # Implement the abstract methods from ConversationRepository
src/infrastructure/persistence/database_service_orchestrator.py:13:from src.infrastructure.persistence.conversation_repository import AsyncSQLAlchemyConversationRepo as ConversationRepository import (
src/infrastructure/persistence/database_service_orchestrator.py:14:    ConversationRepository,
