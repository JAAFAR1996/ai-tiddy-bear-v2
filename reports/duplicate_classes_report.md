=== تقرير الكلاسات المكررة ===
تاريخ التقرير: Sun Jul 20 09:35:21 +03 2025

عدد الكلاسات المكررة: 19

## التفاصيل:

### AlertRule
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:34:class AlertRule:
src/presentation/api/emergency_response/models.py:83:class AlertRule(BaseModel):

### ChildData
src/application/dto/child_data.py:31:class ChildData:
src/infrastructure/security/child_data_security_manager.py:19:class ChildDataSecurityManager:
src/infrastructure/security/coppa/data_models.py:14:class ChildData(BaseModel):
src/presentation/api/endpoints/children/operations.py:255:class ChildDataTransformer:

### ChildPreferences
src/domain/value_objects/child_preferences.py:39:class ChildPreferences:
src/presentation/api/endpoints/children/models.py:18:class ChildPreferences(BaseModel):

### ChildSafetyRateLimiter
src/infrastructure/security/rate_limiter/core.py:191:class ChildSafetyRateLimiter(RedisRateLimiter):
src/infrastructure/security/rate_limiter.py:83:class ChildSafetyRateLimiter:

### ConsentRequest
src/presentation/api/endpoints/children/compliance.py:22:class ConsentRequest(BaseModel):
src/presentation/api/parental_dashboard.py:70:class ConsentRequest(BaseModel):

### ConsentType
src/domain/models/consent_models.py:6:class ConsentType(Enum):
src/infrastructure/persistence/models/consent_models.py:18:class ConsentType(enum.Enum):

### ConversationContext
src/domain/safety/bias_models/bias_models.py:5:class ConversationContext:
src/infrastructure/ai/models.py:4:class ConversationContext(BaseModel):

### ConversationRepository
src/domain/repositories/conversation_repository.py:7:class ConversationRepository(Protocol):
src/infrastructure/persistence/conversation_repository.py:13:class ConversationRepository(ABC):

### DataRetentionManager
src/infrastructure/security/coppa/data_retention.py:21:class DataRetentionManager:
src/presentation/api/endpoints/children/compliance.py:67:class DataRetentionManager:

### EmergencyContact
src/infrastructure/validation/emergency_contact_validator.py:16:class EmergencyContact:
src/infrastructure/validation/emergency_contact_validator.py:27:class EmergencyContactValidator:
src/presentation/api/emergency_response/models.py:71:class EmergencyContact(BaseModel):
src/presentation/api/models/validation_models.py:231:class EmergencyContactRequest(BaseModel):

### ErrorContext
src/domain/exceptions/base.py:22:class ErrorContext:
src/infrastructure/error_handling/error_types.py:35:class ErrorContext:

### ErrorSeverity
src/domain/exceptions/base.py:11:class ErrorSeverity(Enum):
src/infrastructure/error_handling/error_types.py:12:class ErrorSeverity(Enum):

### HealthStatus
src/infrastructure/health/models.py:9:class HealthStatus(str, Enum):
src/presentation/api/endpoints/health.py:54:class HealthStatus(BaseModel):

### QueryValidationResult
src/infrastructure/security/sql_injection_protection.py:363:class QueryValidationResult:
src/infrastructure/security/validation/query_validator.py:16:class QueryValidationResult:

### ServiceFactory
src/infrastructure/di/di_components/service_factory.py:10:class ServiceFactory:
src/presentation/api/dependencies/base.py:8:class ServiceFactory(ABC):

### SessionStatus
src/application/services/session/session_models.py:12:class SessionStatus(str, Enum):
src/infrastructure/session_manager/session_models.py:10:class SessionStatus(Enum):

### StoryRequest
src/application/dto/story_request.py:6:class StoryRequest:
src/presentation/api/endpoints/chatgpt.py:28:class StoryRequest(BaseModel):

### User
src/domain/entities/user.py:4:class User:
src/infrastructure/persistence/models/user_model.py:15:class UserModel(Base):
src/infrastructure/persistence/repositories/user_repository.py:27:class UserRepository:
src/infrastructure/security/jwt_auth.py:75:class User(SQLAlchemyBaseUserTableUUID, Base):
src/infrastructure/security/real_auth_service.py:30:class UserInfo(BaseModel):

### ValidationSeverity
src/domain/schemas.py:300:class ValidationSeverity(Enum):
src/infrastructure/security/hardening/validation/validation_config.py:12:class ValidationSeverity(Enum):
