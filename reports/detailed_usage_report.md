=== تقرير مفصل لاستخدامات الدوال المكررة ===
تاريخ التقرير: Sat Jul 19 23:29:47 +03 2025

## 1. validate_child_age
### المواقع:
src/domain/services/coppa_age_validation.py:181:def validate_child_age(age: int | None) -> dict[str, Any]:
src/infrastructure/security/coppa_validator.py:295:def validate_child_age(age: int) -> COPPAValidationResult:

### الاستخدامات:
src/domain/services/coppa_age_validation.py:181:def validate_child_age(age: int | None) -> dict[str, Any]:
src/infrastructure/security/coppa_validator.py:295:def validate_child_age(age: int) -> COPPAValidationResult:
src/infrastructure/validation/comprehensive_validator.py:82:        age_result = self.child_safety.validate_child_age(child_data["age"])
src/presentation/api/endpoints/children/routes_di.py:38:        age_validation = await coppa_service.validate_child_age(request.age)
src/presentation/api/endpoints/children/routes_di.py:211:            age_validation = await coppa_service.validate_child_age(request.age)

## 2. configure_openapi
### المواقع:
src/presentation/api/openapi_config.py:64:def configure_openapi(app: FastAPI) -> None:
src/presentation/api/openapi_docs.py:415:def configure_openapi(app) -> None:

### الاستخدامات:
src/main.py:32:from src.presentation.api.openapi_config import configure_openapi
src/main.py:104:    configure_openapi(fast_app)
src/presentation/api/openapi_config.py:64:def configure_openapi(app: FastAPI) -> None:
src/presentation/api/openapi_docs.py:415:def configure_openapi(app) -> None:
src/presentation/api/openapi_docs.py:467:    "configure_openapi",
