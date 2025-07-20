=== تقرير الدوال المكررة ===
تاريخ التقرير: Sat Jul 19 23:25:45 +03 2025

### configure_openapi
src/presentation/api/openapi_config.py:64:def configure_openapi(app: FastAPI) -> None:
src/presentation/api/openapi_docs.py:415:def configure_openapi(app) -> None:

### create_app
src/main.py:144:def create_app() -> FastAPI:
src/presentation/api/emergency_response/main.py:113:def create_app() -> FastAPI:

### create_input_validation_middleware
src/infrastructure/security/hardening/validation/middleware.py:124:def create_input_validation_middleware(
src/infrastructure/security/input_validation/middleware.py:366:def create_input_validation_middleware(

### create_safe_database_session
src/infrastructure/persistence/real_database_service.py:46:def create_safe_database_session(session):
src/infrastructure/security/database_input_validator.py:435:def create_safe_database_session(database_session) -> SafeDatabaseSession:

### create_security_middleware
src/infrastructure/middleware/security/headers.py:440:def create_security_middleware(app, environment: str = "production") -> SecurityHeadersMiddleware:
src/infrastructure/security/security_middleware.py:446:def create_security_middleware(

### database_input_validation
src/infrastructure/persistence/real_database_service.py:35:def database_input_validation(table):
src/infrastructure/security/database_input_validator.py:251:def database_input_validation(table_name: str):

### enforce_production_safety
src/infrastructure/config/production_check.py:69:def enforce_production_safety() -> None:
src/infrastructure/config/production_check.py:78:def enforce_production_safety() -> None:

### get_auth_service
src/infrastructure/di/fastapi_dependencies.py:70:def get_auth_service(
src/infrastructure/security/real_auth_service.py:145:def get_auth_service() -> ProductionAuthService:

### get_compliance_validator
src/presentation/api/dependencies/__init__.py:24:def get_compliance_validator():
src/presentation/api/endpoints/children/compliance.py:108:def get_compliance_validator(

### get_consent_manager
src/application/interfaces/read_model_interfaces.py:124:def get_consent_manager() -> IConsentManager:
src/infrastructure/security/coppa/__init__.py:15:def get_consent_manager() -> COPPAConsentManager:
src/presentation/api/endpoints/children/compliance.py:114:def get_consent_manager() -> ParentalConsentManager:

### get_data_retention_days
src/infrastructure/config/coppa_config.py:87:def get_data_retention_days() -> int:
src/infrastructure/security/coppa_validator.py:288:def get_data_retention_days(age: int) -> int:

### get_rate_limiter
src/infrastructure/security/rate_limiter/core.py:217:def get_rate_limiter():
src/infrastructure/security/rate_limiter/service.py:129:def get_rate_limiter(redis_client=None) -> ComprehensiveRateLimiter:

### get_retention_manager
src/infrastructure/security/coppa/data_retention.py:426:def get_retention_manager() -> DataRetentionManager:
src/presentation/api/endpoints/children/compliance.py:119:def get_retention_manager() -> DataRetentionManager:

### validate_child_age
src/domain/services/coppa_age_validation.py:181:def validate_child_age(age: int | None) -> dict[str, Any]:
src/infrastructure/security/coppa_validator.py:295:def validate_child_age(age: int) -> COPPAValidationResult:

### validate_database_operation
src/infrastructure/persistence/real_database_service.py:42:def validate_database_operation(*args, **kwargs):
src/infrastructure/security/database_input_validator.py:295:def validate_database_operation(

### ملخص:
عدد الدوال المكررة: 15
