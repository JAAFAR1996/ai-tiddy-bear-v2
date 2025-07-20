## التحقق من تنسيق الكود (Black)
```bash
black --check src/ --exclude .venv|venv|__pycache__|build|dist|.mypy_cache|node_modules|.git
```

_Error or No results._
```
/bin/sh: 1: venv: not found
/bin/sh: 1: __pycache__: Permission denied
/bin/sh: 1: build: not found
/bin/sh: 1: /bin/sh: 1: dist: not found.mypy_cache: not found

/bin/sh: 1: .git: not found
/bin/sh: 1: node_modules: Permission denied
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/interfaces/infrastructure_services.py: Cannot parse: 5:0:     @abstractmethod
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/exceptions/child_exceptions.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/exceptions/security_exceptions.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/services/consent/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/services/parent_child_verification_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/entities/user.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/interfaces/read_model_interfaces.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/exceptions.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/base_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/dto/ai_response.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/interfaces/repository_interfaces.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/ai_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/value_objects/safety_level.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/kafka_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/application_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/prometheus_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/redis_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/exceptions/base.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/models.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/privacy_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/repositories/event_store.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/database_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/coppa_config.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/value_objects/child_preferences.py
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/logging/standards.py: Cannot parse: 11:0:     """Standard log categories for the system."""
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/error_handling/error_types.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/production_check.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/di/di_components/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/di/container.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/error_handling/__init__.py
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/database_service_orchestrator.py: Cannot parse: 13:125: from src.infrastructure.persistence.conversation_repository import AsyncSQLAlchemyConversationRepo as ConversationRepository import (
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/monitoring/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/server_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/database/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/models/base.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/error_handling/exceptions.py
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/repositories/__init__.py: Cannot parse: 9:125: from src.infrastructure.persistence.conversation_repository import AsyncSQLAlchemyConversationRepo as ConversationRepository import (
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/real_database_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/security_settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/config/settings.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/coppa/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/di/application_container.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/conversation_repository.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/middleware/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/child_data_security_manager.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/postgres_event_store.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/hardening/security_validator.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/hardening/validation/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/services/coppa/coppa_compliance_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/hardening/validation/validation_config.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/models/child_models.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/domain/schemas.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/request_signing_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/application/services/ai/modules/response_generator.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/persistence/database_manager.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/security_headers_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/security_levels.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/coppa/consent_manager.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/validation/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/validation/child_safety_validator.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/validation/general_input_validator.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/session_manager/session_models.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/dependencies/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/dependencies/base.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/dependencies/providers.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/endpoints/audio.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/endpoints/auth.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/real_auth_service.py
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/emergency_response/main.py: Cannot parse: 65:11:     global (
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/health_endpoints.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/token_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/main_security_service.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/middleware/__init__.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/rate_limiter/core.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/endpoints/conversations.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/middleware/security/headers.py
error: cannot format /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/endpoints/chatgpt.py: Cannot parse: 261:8:         ],
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/main.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/endpoints/children/compliance.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/middleware/error_handling.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/sql_injection_protection.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/infrastructure/security/secure_logger.py
would reformat /mnt/c/Users/jaafa/Desktop/5555/ai-teddy/ai-tiddy-bear--main/src/presentation/api/models/validation_models.py

Oh no! 💥 💔 💥
77 files would be reformatted, 399 files would be left unchanged, 6 files would fail to reformat.

```

⏱️ الوقت المستغرق: 47.24 ثانية


---

