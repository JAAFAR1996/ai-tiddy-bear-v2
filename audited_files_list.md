# Audited Files List

This file contains all unique file paths that were mentioned or analyzed in the security audit reports.

## Total Files Audited: 258

### Third-party Library Files (13 files)
- attr/__init__.py
- attr/_cmp.py
- attr/_compat.py
- attr/_config.py
- attr/_funcs.py
- attr/_make.py
- attr/_next_gen.py
- attr/_version_info.py
- attr/converters.py
- attr/exceptions.py
- attr/filters.py
- attr/setters.py
- attr/validators.py

### Build & Configuration Files (6 files)
- .env
- Dockerfile
- pyproject.toml
- pytest.ini
- requirements-dev.txt
- requirements.txt

### Database Migration Files (2 files)
- migrations/env.py
- migrations/versions/20250111_1500_001_initial_production_schema.py

### Development Scripts (5 files)
- scripts/development/generators/__init__.py
- scripts/development/generators/auth_generator.py
- scripts/development/generators/children_generator.py
- scripts/development/generators/conversations_generator.py
- scripts/development/generators/main_generator.py

### Core Application Files (5 files)
- src/__init__.py
- src/common/constants.py
- src/common/container.py
- src/main.py
- src/presentation/routing.py

### Application Services (30 files)
- src/application/services/accessibility_service.py
- src/application/services/advanced_personalization_service.py
- src/application/services/advanced_progress_analyzer.py
- src/application/services/ai_orchestration_service.py
- src/application/services/async_session_manager.py
- src/application/services/audio_processing_service.py
- src/application/services/audio_service.py
- src/application/services/audit_service.py
- src/application/services/base_service.py
- src/application/services/cleanup_service.py
- src/application/services/consent_service.py
- src/application/services/content_filter_service.py
- src/application/services/conversation_service.py
- src/application/services/data_export_service.py
- src/application/services/data_retention_service.py
- src/application/services/dynamic_content_service.py
- src/application/services/emotion_analyzer.py
- src/application/services/esp32_device_service.py
- src/application/services/feature_service.py
- src/application/services/federated_learning_service.py
- src/application/services/interaction_service.py
- src/application/services/notification_service.py
- src/application/services/parent_child_verification_service.py
- src/application/services/response_generator.py
- src/application/services/safety.py
- src/application/services/session_manager.py
- src/application/services/transcription_models.py
- src/application/services/transcription_service.py
- src/application/services/voice_service.py

### Use Cases (2 files)
- src/application/use_cases/generate_ai_response.py
- src/application/use_cases/manage_child_profile.py

### Domain Layer (24 files)
- src/domain/analytics.py
- src/domain/constants.py
- src/domain/contracts.py
- src/domain/entities/audio_session.py
- src/domain/entities/child.py
- src/domain/entities/child_profile.py
- src/domain/entities/conversation.py
- src/domain/entities/emotion.py
- src/domain/entities/encrypted_child.py
- src/domain/interfaces/accessibility_profile_repository.py
- src/domain/interfaces/ai_service_interface.py
- src/domain/interfaces/child_profile_repository.py
- src/domain/interfaces/config_interface.py
- src/domain/interfaces/conversation_repository.py
- src/domain/interfaces/event_bus_interface.py
- src/domain/interfaces/external_service_interfaces.py
- src/domain/schemas.py
- src/domain/value_objects.py
- src/domain/value_objects/accessibility.py
- src/domain/value_objects/age_group.py
- src/domain/value_objects/child_age.py
- src/domain/value_objects/child_preferences.py
- src/domain/value_objects/encrypted_field.py
- src/domain/value_objects/language.py
- src/domain/value_objects/notification.py
- src/domain/value_objects/personality.py
- src/domain/value_objects/safety_level.py

### Infrastructure Layer (134 files)

#### AI Infrastructure (10 files)
- src/infrastructure/ai/chatgpt/client.py
- src/infrastructure/ai/chatgpt/fallback_responses.py
- src/infrastructure/ai/chatgpt/response_enhancer.py
- src/infrastructure/ai/chatgpt/safety_filter.py
- src/infrastructure/ai/models.py
- src/infrastructure/ai/production_ai_service.py
- src/infrastructure/ai/prompt_builder.py
- src/infrastructure/ai/real_ai_service.py
- src/infrastructure/ai/safety_analyzer.py

#### Caching (3 files)
- src/infrastructure/cache/redis_cache.py
- src/infrastructure/caching/cache_config.py
- src/infrastructure/caching/redis_cache_manager.py

#### Chaos Engineering (14 files)
- src/infrastructure/chaos/actions/ai_model_recovery_testing.py
- src/infrastructure/chaos/actions/bias_detection_testing.py
- src/infrastructure/chaos/actions/hallucination_testing.py
- src/infrastructure/chaos/actions/load_testing.py
- src/infrastructure/chaos/actions/response_consistency_testing.py
- src/infrastructure/chaos/infrastructure/chaos_injector.py
- src/infrastructure/chaos/infrastructure/chaos_monitor.py
- src/infrastructure/chaos/infrastructure/chaos_orchestrator.py
- src/infrastructure/chaos/infrastructure/chaos_reporter.py
- src/infrastructure/chaos/monitoring/chaos_metrics.py
- src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py
- src/infrastructure/chaos/monitoring/chaos_metrics/metrics_collector.py

#### Configuration (20 files)
- src/infrastructure/config/accessibility_config.py
- src/infrastructure/config/ai_settings.py
- src/infrastructure/config/application_settings.py
- src/infrastructure/config/base_settings.py
- src/infrastructure/config/coppa_config.py
- src/infrastructure/config/database_settings.py
- src/infrastructure/config/env_security.py
- src/infrastructure/config/fix.md
- src/infrastructure/config/infrastructure_settings.py
- src/infrastructure/config/interaction_config.py
- src/infrastructure/config/models.py
- src/infrastructure/config/notification_config.py
- src/infrastructure/config/production_check.py
- src/infrastructure/config/production_settings.py
- src/infrastructure/config/prometheus_settings.py
- src/infrastructure/config/redis_settings.py
- src/infrastructure/config/secure_settings.py
- src/infrastructure/config/session_config.py
- src/infrastructure/config/settings.py
- src/infrastructure/config/startup_validator.py
- src/infrastructure/config/validators.py
- src/infrastructure/config/voice_settings.py

#### Core Infrastructure (8 files)
- src/infrastructure/app_initializer.py
- src/infrastructure/dependencies.py
- src/infrastructure/di/container.py
- src/infrastructure/exceptions.py
- src/infrastructure/lifespan.py
- src/infrastructure/logging_config.py
- src/infrastructure/middleware.py

#### Error Handling (10 files)
- src/infrastructure/error_handling/decorators.py
- src/infrastructure/error_handling/error_handlers.py
- src/infrastructure/error_handling/exceptions.py
- src/infrastructure/error_handling/handlers.py
- src/infrastructure/error_handling/messages.py
- src/infrastructure/exception_handling/circuit_breaker.py
- src/infrastructure/exception_handling/enterprise_exception_handler.py
- src/infrastructure/exception_handling/global_exception_handler.py

#### External APIs (6 files)
- src/infrastructure/external_apis/azure_speech_client.py
- src/infrastructure/external_apis/chatgpt_client.py
- src/infrastructure/external_apis/chatgpt_service.py
- src/infrastructure/external_apis/elevenlabs_client.py
- src/infrastructure/external_apis/openai_client.py
- src/infrastructure/external_apis/whisper_client.py

#### External Services (3 files)
- src/infrastructure/external_services/dummy_notification_clients.py
- src/infrastructure/external_services/dummy_sanitization_service.py
- src/infrastructure/external_services/speech_analysis_base.py

#### Logging (2 files)
- src/infrastructure/logging/audit_logger.py
- src/infrastructure/logging/standards.py

#### Monitoring (4 files)
- src/infrastructure/monitoring/components/child_safety_monitor.py
- src/infrastructure/monitoring/components/monitoring_service.py
- src/infrastructure/monitoring/comprehensive_monitoring.py
- src/infrastructure/monitoring/performance_monitor.py

#### Persistence (7 files)
- src/infrastructure/persistence/database.py
- src/infrastructure/persistence/models.py
- src/infrastructure/persistence/models/child_model.py
- src/infrastructure/persistence/models/conversation_model.py
- src/infrastructure/persistence/models/user_model.py
- src/infrastructure/persistence/repositories.py
- src/infrastructure/persistence/repositories/child_repository.py

#### Resilience (2 files)
- src/infrastructure/resilience/circuit_breaker.py
- src/infrastructure/resilience/retry_decorator.py

#### Security (45 files)
- src/infrastructure/security/access_control_service.py
- src/infrastructure/security/api_security_manager.py
- src/infrastructure/security/audit_decorators.py
- src/infrastructure/security/audit_logger.py
- src/infrastructure/security/child_data_encryption.py
- src/infrastructure/security/child_data_security_manager.py
- src/infrastructure/security/comprehensive_audit_integration.py
- src/infrastructure/security/comprehensive_input_validation_middleware.py
- src/infrastructure/security/comprehensive_rate_limiter.py
- src/infrastructure/security/comprehensive_security_service.py
- src/infrastructure/security/coppa/consent_manager.py
- src/infrastructure/security/coppa/data_models.py
- src/infrastructure/security/coppa/data_retention.py
- src/infrastructure/security/coppa_validator.py
- src/infrastructure/security/cors_service.py
- src/infrastructure/security/database_input_validator.py
- src/infrastructure/security/email_validator.py
- src/infrastructure/security/encryption_service.py
- src/infrastructure/security/enhanced_security.py
- src/infrastructure/security/environment_validator.py
- src/infrastructure/security/error_handler.py
- src/infrastructure/security/fallback_rate_limiter.py
- src/infrastructure/security/file_security_manager.py
- src/infrastructure/security/hardening/coppa_compliance.py
- src/infrastructure/security/hardening/csrf_protection.py
- src/infrastructure/security/hardening/input_validation.py
- src/infrastructure/security/hardening/rate_limiter.py
- src/infrastructure/security/hardening/secure_settings.py
- src/infrastructure/security/hardening/security_headers.py
- src/infrastructure/security/hardening/security_tests.py
- src/infrastructure/security/https_middleware.py
- src/infrastructure/security/input_validation/core.py
- src/infrastructure/security/input_validation/middleware.py
- src/infrastructure/security/input_validation/patterns.py
- src/infrastructure/security/jwt_auth.py
- src/infrastructure/security/key_management/key_generator.py
- src/infrastructure/security/key_rotation.py
- src/infrastructure/security/key_rotation_service.py
- src/infrastructure/security/log_sanitization_config.py
- src/infrastructure/security/log_sanitizer.py
- src/infrastructure/security/logging_security_monitor.py
- src/infrastructure/security/main_security_service.py
- src/infrastructure/security/models.py
- src/infrastructure/security/password_hasher.py
- src/infrastructure/security/password_validator.py
- src/infrastructure/security/path_validator.py
- src/infrastructure/security/plugin_architecture.py
- src/infrastructure/security/rate_limiter_service.py
- src/infrastructure/security/token_service.py

### Presentation Layer (25 files)

#### API Endpoints (13 files)
- src/presentation/api/endpoints/audio.py
- src/presentation/api/endpoints/auth.py
- src/presentation/api/endpoints/chatgpt.py
- src/presentation/api/endpoints/children/compliance.py
- src/presentation/api/endpoints/children/models.py
- src/presentation/api/endpoints/children/operations.py
- src/presentation/api/endpoints/children/routes.py
- src/presentation/api/endpoints/children_legacy.py
- src/presentation/api/endpoints/conversations.py
- src/presentation/api/endpoints/coppa_notices.py
- src/presentation/api/endpoints/dashboard.py
- src/presentation/api/endpoints/device.py
- src/presentation/api/endpoints/health.py
- src/presentation/api/endpoints/monitoring_dashboard.py

#### Middleware (8 files)
- src/presentation/api/middleware/child_safe_rate_limiter.py
- src/presentation/api/middleware/comprehensive_security_headers.py
- src/presentation/api/middleware/consent_verification.py
- src/presentation/api/middleware/error_handling.py
- src/presentation/api/middleware/exception_handler.py
- src/presentation/api/middleware/rate_limit_middleware.py
- src/presentation/api/middleware/request_logging.py
- src/presentation/api/middleware/security_headers.py

#### Models (2 files)
- src/presentation/api/models/standard_responses.py
- src/presentation/api/models/validation_models.py

#### Configuration (1 file)
- src/presentation/api/openapi_config.py

### Utility Files (5 files)
- src/utils/comment_formatter.py
- src/utils/file_validators.py
- src/utils/find_long_functions.py
- src/utils/import_organizer.py
- src/utils/type_annotation_fixer.py

### Test Files (5 files)
- tests/ai_test_generator.py
- tests/comprehensive_testing_framework.py
- tests/conftest.py
- tests/contract_tests.py
- tests/final_test.py

---

## Summary by Category

| Category | Count |
|----------|-------|
| Infrastructure Layer | 134 |
| Application Services | 30 |
| Presentation Layer | 25 |
| Domain Layer | 24 |
| Third-party Library Files | 13 |
| Build & Configuration Files | 6 |
| Utility Files | 5 |
| Test Files | 5 |
| Core Application Files | 5 |
| Development Scripts | 5 |
| Database Migration Files | 2 |
| **Total** | **258** |

All files listed above were analyzed in the security audit reports and had one or more security issues identified.