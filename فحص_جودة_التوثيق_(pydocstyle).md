## فحص جودة التوثيق (pydocstyle)
```bash
pydocstyle src/ --ignore=.venv venv __pycache__ build dist .mypy_cache node_modules .git
```

_Error or No results._
```
WARNING: Error code passed is not a prefix of any known errors: .venv
WARNING: Error in file src/application/interfaces/infrastructure_services.py: Cannot parse file.
WARNING: Error in file src/infrastructure/logging/standards.py: Cannot parse file.
WARNING: Error in file src/infrastructure/persistence/database_service_orchestrator.py: Cannot parse file.
WARNING: Error in file src/infrastructure/persistence/repositories/__init__.py: Cannot parse file.
WARNING: Error in file src/presentation/api/emergency_response/main.py: Cannot parse file.
WARNING: Error in file src/presentation/api/endpoints/chatgpt.py: Cannot parse file.
src/main.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/main.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/main.py:1 at module level:
        D400: First line should end with a period (not ')')
src/main.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/main.py:41 in public function `lifespan`:
        D103: Missing docstring in public function
src/main.py:75 in private function `_setup_app_configurations`:
        D401: First line should be in imperative mood; try rephrasing (found 'Helper')
src/main.py:85 in private function `_validate_system_startup`:
        D401: First line should be in imperative mood; try rephrasing (found 'Helper')
src/main.py:101 in private function `_setup_app_middlewares_and_routes`:
        D401: First line should be in imperative mood; try rephrasing (found 'Helper')
src/main.py:108 in private function `_mount_static_files`:
        D401: First line should be in imperative mood; try rephrasing (found 'Helper')
src/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/api/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/api/endpoints/voice_models.py:1 at module level:
        D100: Missing docstring in public module
src/api/endpoints/voice_models.py:5 in public class `VoiceResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/api/endpoints/voice_models.py:14 in public class `AudioValidationResult`:
        D101: Missing docstring in public class
src/api/endpoints/voice_models.py:21 in public class `SpeechToTextResult`:
        D101: Missing docstring in public class
src/api/endpoints/voice_models.py:31 in public class `TextToSpeechResult`:
        D101: Missing docstring in public class
src/api/endpoints/voice_routes.py:1 at module level:
        D100: Missing docstring in public module
src/api/endpoints/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/exceptions.py:4 in public class `AITeddyError`:
        D203: 1 blank line required before class docstring (found 0)
src/application/exceptions.py:6 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/exceptions.py:20 in public class `ServiceUnavailableError`:
        D203: 1 blank line required before class docstring (found 0)
src/application/exceptions.py:22 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/exceptions.py:31 in public class `InvalidInputError`:
        D203: 1 blank line required before class docstring (found 0)
src/application/exceptions.py:33 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/exceptions.py:42 in public class `TimeoutError`:
        D203: 1 blank line required before class docstring (found 0)
src/application/exceptions.py:44 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/exceptions.py:52 in public class `ConsentError`:
        D203: 1 blank line required before class docstring (found 0)
src/application/exceptions.py:52 in public class `ConsentError`:
        D204: 1 blank line required after class docstring (found 0)
src/application/exceptions.py:52 in public class `ConsentError`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/exceptions.py:52 in public class `ConsentError`:
        D212: Multi-line docstring summary should start at the first line
src/application/exceptions.py:56 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/dto/ai_response.py:1 at module level:
        D100: Missing docstring in public module
src/application/dto/ai_response.py:7 in public class `AIResponse`:
        D101: Missing docstring in public class
src/application/dto/ai_response.py:37 in public method `__post_init__`:
        D105: Missing docstring in magic method
src/application/dto/child_data.py:1 at module level:
        D100: Missing docstring in public module
src/application/dto/child_data.py:32 in public class `ChildData`:
        D203: 1 blank line required before class docstring (found 0)
src/application/dto/child_data.py:32 in public class `ChildData`:
        D213: Multi-line docstring summary should start at the second line
src/application/dto/esp32_request.py:1 at module level:
        D100: Missing docstring in public module
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D203: 1 blank line required before class docstring (found 0)
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D213: Multi-line docstring summary should start at the second line
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D400: First line should end with a period (not 'd')
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D413: Missing blank line after last section ('Attributes')
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D407: Missing dashed underline after section ('Attributes')
src/application/dto/esp32_request.py:7 in public class `ESP32Request`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/application/dto/story_response.py:1 at module level:
        D100: Missing docstring in public module
src/application/dto/story_response.py:12 in public class `StoryResponse`:
        D101: Missing docstring in public class
src/application/dto/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/dto/esp32/esp32_data.py:1 at module level:
        D100: Missing docstring in public module
src/application/dto/esp32/esp32_data.py:7 in public class `ESP32SensorReadingDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/esp32_data.py:16 in public class `ESP32VoiceCommandDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/esp32_data.py:23 in public class `ESP32GestureEventDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/esp32_data.py:31 in public class `ESP32FirmwareUpdateStatusDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/esp32_data.py:40 in public class `ESP32DeviceStatusDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/esp32_data.py:50 in public class `ESP32EdgeAIResultDTO`:
        D101: Missing docstring in public class
src/application/dto/esp32/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/event_handlers/child_profile_event_handlers.py:1 at module level:
        D100: Missing docstring in public module
src/application/event_handlers/child_profile_event_handlers.py:28 in public class `ChildProfileEventHandlers`:
        D203: 1 blank line required before class docstring (found 0)
src/application/event_handlers/child_profile_event_handlers.py:28 in public class `ChildProfileEventHandlers`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/event_handlers/child_profile_event_handlers.py:28 in public class `ChildProfileEventHandlers`:
        D213: Multi-line docstring summary should start at the second line
src/application/event_handlers/child_profile_event_handlers.py:33 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/event_handlers/child_profile_event_handlers.py:37 in public method `handle_child_registered`:
        D213: Multi-line docstring summary should start at the second line
src/application/event_handlers/child_profile_event_handlers.py:37 in public method `handle_child_registered`:
        D407: Missing dashed underline after section ('Args')
src/application/event_handlers/child_profile_event_handlers.py:64 in public method `handle_child_profile_updated`:
        D213: Multi-line docstring summary should start at the second line
src/application/event_handlers/child_profile_event_handlers.py:64 in public method `handle_child_profile_updated`:
        D407: Missing dashed underline after section ('Args')
src/application/event_handlers/child_profile_event_handlers.py:111 in private method `_async_save`:
        D213: Multi-line docstring summary should start at the second line
src/application/event_handlers/child_profile_event_handlers.py:111 in private method `_async_save`:
        D407: Missing dashed underline after section ('Args')
src/application/event_handlers/child_profile_event_handlers.py:125 in private method `_async_get_by_id`:
        D213: Multi-line docstring summary should start at the second line
src/application/event_handlers/child_profile_event_handlers.py:125 in private method `_async_get_by_id`:
        D407: Missing dashed underline after section ('Returns')
src/application/event_handlers/child_profile_event_handlers.py:125 in private method `_async_get_by_id`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/event_handlers/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/interfaces/ai_provider.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/ai_provider.py:8 in public class `AIProvider`:
        D203: 1 blank line required before class docstring (found 0)
src/application/interfaces/ai_provider.py:10 in public method `generate_response`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:18 in public method `analyze_sentiment`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:20 in public method `analyze_emotion`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:22 in public method `analyze_toxicity`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:24 in public method `analyze_personality`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:29 in public method `supports_asr_model`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:31 in public method `transcribe_audio`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:33 in public method `evaluate_educational_value`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:35 in public method `determine_activity_type`:
        D102: Missing docstring in public method
src/application/interfaces/ai_provider.py:42 in public method `generate_personalized_content`:
        D102: Missing docstring in public method
src/application/interfaces/read_model_interfaces.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/read_model_interfaces.py:12 in public class `IChildProfileReadModel`:
        D203: 1 blank line required before class docstring (found 0)
src/application/interfaces/read_model_interfaces.py:36 in public class `IChildProfileReadModelStore`:
        D203: 1 blank line required before class docstring (found 0)
src/application/interfaces/read_model_interfaces.py:85 in public function `create_child_profile_read_model`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/interfaces/read_model_interfaces.py:85 in public function `create_child_profile_read_model`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/read_model_interfaces.py:85 in public function `create_child_profile_read_model`:
        D400: First line should end with a period (not 's')
src/application/interfaces/read_model_interfaces.py:85 in public function `create_child_profile_read_model`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/interfaces/read_model_interfaces.py:85 in public function `create_child_profile_read_model`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/interfaces/read_model_interfaces.py:93 in public function `get_read_model_store`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/interfaces/read_model_interfaces.py:93 in public function `get_read_model_store`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/read_model_interfaces.py:93 in public function `get_read_model_store`:
        D400: First line should end with a period (not 'e')
src/application/interfaces/read_model_interfaces.py:93 in public function `get_read_model_store`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/interfaces/read_model_interfaces.py:93 in public function `get_read_model_store`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/interfaces/read_model_interfaces.py:101 in public function `get_event_bus`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/interfaces/read_model_interfaces.py:101 in public function `get_event_bus`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/read_model_interfaces.py:101 in public function `get_event_bus`:
        D400: First line should end with a period (not 's')
src/application/interfaces/read_model_interfaces.py:101 in public function `get_event_bus`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/interfaces/read_model_interfaces.py:101 in public function `get_event_bus`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/interfaces/read_model_interfaces.py:109 in public function `get_external_api_client`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/interfaces/read_model_interfaces.py:109 in public function `get_external_api_client`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/read_model_interfaces.py:109 in public function `get_external_api_client`:
        D400: First line should end with a period (not 't')
src/application/interfaces/read_model_interfaces.py:109 in public function `get_external_api_client`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/application/interfaces/read_model_interfaces.py:109 in public function `get_external_api_client`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/interfaces/read_model_interfaces.py:117 in public function `get_settings_provider`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/interfaces/read_model_interfaces.py:117 in public function `get_settings_provider`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/read_model_interfaces.py:117 in public function `get_settings_provider`:
        D400: First line should end with a period (not 'r')
src/application/interfaces/read_model_interfaces.py:117 in public function `get_settings_provider`:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/application/interfaces/read_model_interfaces.py:117 in public function `get_settings_provider`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/interfaces/safety_monitor.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/safety_monitor.py:8 in public class `SafetyMonitor`:
        D101: Missing docstring in public class
src/application/interfaces/safety_monitor.py:16 in public method `check_content_safety`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/application/interfaces/speech_processor.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/speech_processor.py:4 in public class `SpeechProcessor`:
        D101: Missing docstring in public class
src/application/interfaces/speech_processor.py:5 in public method `speech_to_text`:
        D102: Missing docstring in public method
src/application/interfaces/speech_processor.py:7 in public method `text_to_speech`:
        D102: Missing docstring in public method
src/application/interfaces/text_to_speech_service.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/text_to_speech_service.py:5 in public class `TextToSpeechService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/interfaces/text_to_speech_service.py:5 in public class `TextToSpeechService`:
        D400: First line should end with a period (not 's')
src/application/interfaces/text_to_speech_service.py:5 in public class `TextToSpeechService`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D400: First line should end with a period (not 't')
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D413: Missing blank line after last section ('Returns')
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D407: Missing dashed underline after section ('Returns')
src/application/interfaces/text_to_speech_service.py:14 in public method `generate_speech`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D400: First line should end with a period (not 's')
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D413: Missing blank line after last section ('Returns')
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D407: Missing dashed underline after section ('Returns')
src/application/interfaces/text_to_speech_service.py:27 in public method `list_voices`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D213: Multi-line docstring summary should start at the second line
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D400: First line should end with a period (not 'y')
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D413: Missing blank line after last section ('Returns')
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D407: Missing dashed underline after section ('Returns')
src/application/interfaces/text_to_speech_service.py:35 in public method `health_check`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/interfaces/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/interfaces/security/encryption_interfaces.py:1 at module level:
        D100: Missing docstring in public module
src/application/interfaces/security/encryption_interfaces.py:7 in public class `HomomorphicEncryptionService`:
        D101: Missing docstring in public class
src/application/interfaces/security/encryption_interfaces.py:18 in public method `add`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/application/interfaces/security/encryption_interfaces.py:22 in public method `multiply`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/application/interfaces/security/encryption_interfaces.py:25 in public class `ZeroKnowledgeProofService`:
        D101: Missing docstring in public class
src/application/interfaces/security/encryption_interfaces.py:32 in public method `generate_proof`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/interfaces/security/encryption_interfaces.py:36 in public method `verify_proof`:
        D401: First line should be in imperative mood (perhaps 'Verify', not 'Verifies')
src/application/interfaces/security/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/services/accessibility_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:27 in public class `AccessibilityService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/accessibility_service.py:35 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:35 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/accessibility_service.py:35 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/accessibility_service.py:52 in public method `create_accessibility_profile`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:52 in public method `create_accessibility_profile`:
        D401: First line should be in imperative mood (perhaps 'Create', not 'Creates')
src/application/services/accessibility_service.py:52 in public method `create_accessibility_profile`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/accessibility_service.py:52 in public method `create_accessibility_profile`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/accessibility_service.py:82 in public method `get_accessibility_profile`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:82 in public method `get_accessibility_profile`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/accessibility_service.py:82 in public method `get_accessibility_profile`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/accessibility_service.py:82 in public method `get_accessibility_profile`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/accessibility_service.py:102 in private method `_get_adaptations`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:102 in private method `_get_adaptations`:
        D401: First line should be in imperative mood (perhaps 'Get', not 'Gets')
src/application/services/accessibility_service.py:102 in private method `_get_adaptations`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/accessibility_service.py:102 in private method `_get_adaptations`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/accessibility_service.py:123 in private method `_get_accessibility_settings`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/accessibility_service.py:123 in private method `_get_accessibility_settings`:
        D401: First line should be in imperative mood (perhaps 'Get', not 'Gets')
src/application/services/accessibility_service.py:123 in private method `_get_accessibility_settings`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/accessibility_service.py:123 in private method `_get_accessibility_settings`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_personalization_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:28 in public class `AdvancedPersonalizationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/advanced_personalization_service.py:36 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:36 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/advanced_personalization_service.py:36 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/advanced_personalization_service.py:54 in public method `create_personality_profile`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:54 in public method `create_personality_profile`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_personalization_service.py:54 in public method `create_personality_profile`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_personalization_service.py:71 in public method `get_personality_profile`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:71 in public method `get_personality_profile`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/advanced_personalization_service.py:71 in public method `get_personality_profile`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_personalization_service.py:71 in public method `get_personality_profile`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_personalization_service.py:91 in public method `get_personalized_content`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:91 in public method `get_personalized_content`:
        D401: First line should be in imperative mood (perhaps 'Get', not 'Gets')
src/application/services/advanced_personalization_service.py:91 in public method `get_personalized_content`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_personalization_service.py:91 in public method `get_personalized_content`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_personalization_service.py:140 in private method `_analyze_interactions`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_personalization_service.py:140 in private method `_analyze_interactions`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_personalization_service.py:140 in private method `_analyze_interactions`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_progress_analyzer.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_progress_analyzer.py:19 in public class `ProgressMetrics`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/advanced_progress_analyzer.py:28 in public class `AdvancedProgressAnalyzer`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/advanced_progress_analyzer.py:31 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/advanced_progress_analyzer.py:40 in public method `analyze_progress`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_progress_analyzer.py:40 in public method `analyze_progress`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_progress_analyzer.py:40 in public method `analyze_progress`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_progress_analyzer.py:67 in public method `get_progress_report`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_progress_analyzer.py:67 in public method `get_progress_report`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/advanced_progress_analyzer.py:67 in public method `get_progress_report`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_progress_analyzer.py:67 in public method `get_progress_report`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/advanced_progress_analyzer.py:96 in private method `_calculate_metrics`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/advanced_progress_analyzer.py:96 in private method `_calculate_metrics`:
        D401: First line should be in imperative mood (perhaps 'Calculate', not 'Calculates')
src/application/services/advanced_progress_analyzer.py:96 in private method `_calculate_metrics`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/advanced_progress_analyzer.py:96 in private method `_calculate_metrics`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/ai_orchestration_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai_orchestration_service.py:32 in public class `AIOrchestrationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai_orchestration_service.py:41 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai_orchestration_service.py:41 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/ai_orchestration_service.py:41 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/ai_orchestration_service.py:63 in public method `get_ai_response`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai_orchestration_service.py:63 in public method `get_ai_response`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/ai_orchestration_service.py:63 in public method `get_ai_response`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/ai_orchestration_service.py:63 in public method `get_ai_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/audio_processing_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audio_processing_service.py:20 in public class `AudioProcessingService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/audio_processing_service.py:28 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audio_processing_service.py:28 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/audio_processing_service.py:28 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/audio_processing_service.py:45 in public method `process_audio_input`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audio_processing_service.py:45 in public method `process_audio_input`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/audio_processing_service.py:45 in public method `process_audio_input`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/audio_processing_service.py:45 in public method `process_audio_input`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/audio_processing_service.py:60 in public method `generate_audio_response`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audio_processing_service.py:60 in public method `generate_audio_response`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/audio_processing_service.py:60 in public method `generate_audio_response`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/audio_processing_service.py:60 in public method `generate_audio_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/audit_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audit_service.py:17 in public class `AuditService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/audit_service.py:23 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/audit_service.py:40 in public method `create_audit_log`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audit_service.py:40 in public method `create_audit_log`:
        D401: First line should be in imperative mood (perhaps 'Create', not 'Creates')
src/application/services/audit_service.py:40 in public method `create_audit_log`:
        D407: Missing dashed underline after section ('Args')
src/application/services/audit_service.py:76 in public method `get_audit_logs`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/audit_service.py:76 in public method `get_audit_logs`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/audit_service.py:76 in public method `get_audit_logs`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/audit_service.py:76 in public method `get_audit_logs`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/base_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:17 in public class `BaseService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/base_service.py:20 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/base_service.py:25 in public method `initialize`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:25 in public method `initialize`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/base_service.py:33 in public method `cleanup`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:33 in public method `cleanup`:
        D401: First line should be in imperative mood (perhaps 'Clean', not 'Cleans')
src/application/services/base_service.py:40 in public method `log_info`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:40 in public method `log_info`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/application/services/base_service.py:40 in public method `log_info`:
        D407: Missing dashed underline after section ('Args')
src/application/services/base_service.py:50 in public method `log_error`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:50 in public method `log_error`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/application/services/base_service.py:50 in public method `log_error`:
        D407: Missing dashed underline after section ('Args')
src/application/services/base_service.py:60 in public method `validate_input`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/base_service.py:60 in public method `validate_input`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/application/services/base_service.py:60 in public method `validate_input`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/base_service.py:60 in public method `validate_input`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/cleanup_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/cleanup_service.py:19 in public class `CleanupService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/cleanup_service.py:25 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/cleanup_service.py:39 in private method `_is_safe_path`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/cleanup_service.py:39 in private method `_is_safe_path`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/application/services/cleanup_service.py:59 in public method `cleanup_old_data`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/cleanup_service.py:59 in public method `cleanup_old_data`:
        D401: First line should be in imperative mood (perhaps 'Clean', not 'Cleans')
src/application/services/cleanup_service.py:59 in public method `cleanup_old_data`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/cleanup_service.py:59 in public method `cleanup_old_data`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/cleanup_service.py:110 in private method `_cleanup_data_type`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/cleanup_service.py:110 in private method `_cleanup_data_type`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/application/services/cleanup_service.py:110 in private method `_cleanup_data_type`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/cleanup_service.py:110 in private method `_cleanup_data_type`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/cleanup_service.py:150 in private method `_simulate_data_cleanup`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/cleanup_service.py:150 in private method `_simulate_data_cleanup`:
        D401: First line should be in imperative mood (perhaps 'Simulate', not 'Simulates')
src/application/services/cleanup_service.py:150 in private method `_simulate_data_cleanup`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/cleanup_service.py:150 in private method `_simulate_data_cleanup`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/content_filter_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/content_filter_service.py:19 in public class `ContentFilterService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/content_filter_service.py:26 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/content_filter_service.py:26 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/content_filter_service.py:26 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D400: First line should end with a period (not 'e')
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D401: First line should be in imperative mood (perhaps 'Filter', not 'Filters')
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/content_filter_service.py:38 in public method `filter_content`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:20 in public class `ConversationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/conversation_service.py:27 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:27 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/conversation_service.py:27 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/conversation_service.py:42 in public method `start_new_conversation`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:42 in public method `start_new_conversation`:
        D401: First line should be in imperative mood (perhaps 'Start', not 'Starts')
src/application/services/conversation_service.py:42 in public method `start_new_conversation`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:42 in public method `start_new_conversation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:59 in public method `get_conversation_history`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:59 in public method `get_conversation_history`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/conversation_service.py:59 in public method `get_conversation_history`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:59 in public method `get_conversation_history`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D407: Missing dashed underline after section ('Raises')
src/application/services/conversation_service.py:71 in private method `_get_conversation_by_id`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/application/services/conversation_service.py:94 in public method `update_conversation_analysis`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:94 in public method `update_conversation_analysis`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/application/services/conversation_service.py:94 in public method `update_conversation_analysis`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:94 in public method `update_conversation_analysis`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:115 in public method `update_conversation_summary`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:115 in public method `update_conversation_summary`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/application/services/conversation_service.py:115 in public method `update_conversation_summary`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:115 in public method `update_conversation_summary`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/conversation_service.py:136 in public method `add_interaction`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/conversation_service.py:136 in public method `add_interaction`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/application/services/conversation_service.py:136 in public method `add_interaction`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/conversation_service.py:136 in public method `add_interaction`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/data_export_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:30 in public class `DataExportService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export_service.py:37 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:37 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/data_export_service.py:37 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/data_export_service.py:53 in private method `_sanitize_data_for_export`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:53 in private method `_sanitize_data_for_export`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/data_export_service.py:53 in private method `_sanitize_data_for_export`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/data_export_service.py:90 in public method `request_export`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:90 in public method `request_export`:
        D401: First line should be in imperative mood (perhaps 'Request', not 'Requests')
src/application/services/data_export_service.py:90 in public method `request_export`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/data_export_service.py:90 in public method `request_export`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/data_export_service.py:126 in public method `get_export_status`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:126 in public method `get_export_status`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/data_export_service.py:126 in public method `get_export_status`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/data_export_service.py:126 in public method `get_export_status`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/data_export_service.py:138 in private method `_validate_export_request`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:138 in private method `_validate_export_request`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/application/services/data_export_service.py:138 in private method `_validate_export_request`:
        D407: Missing dashed underline after section ('Raises')
src/application/services/data_export_service.py:138 in private method `_validate_export_request`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/application/services/data_export_service.py:163 in private method `_simulate_export`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export_service.py:163 in private method `_simulate_export`:
        D401: First line should be in imperative mood (perhaps 'Simulate', not 'Simulates')
src/application/services/data_export_service.py:163 in private method `_simulate_export`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/data_export_service.py:163 in private method `_simulate_export`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/dynamic_content_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_content_service.py:25 in public class `DynamicContentService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/dynamic_content_service.py:32 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_content_service.py:32 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/dynamic_content_service.py:32 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/dynamic_content_service.py:50 in public method `generate_personalized_story`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_content_service.py:50 in public method `generate_personalized_story`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/dynamic_content_service.py:50 in public method `generate_personalized_story`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/dynamic_content_service.py:50 in public method `generate_personalized_story`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/dynamic_content_service.py:101 in public method `generate_educational_content`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_content_service.py:101 in public method `generate_educational_content`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/dynamic_content_service.py:101 in public method `generate_educational_content`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/dynamic_content_service.py:101 in public method `generate_educational_content`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/dynamic_content_service.py:149 in public method `get_interactive_activity`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_content_service.py:149 in public method `get_interactive_activity`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/dynamic_content_service.py:149 in public method `get_interactive_activity`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/dynamic_content_service.py:149 in public method `get_interactive_activity`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/dynamic_story_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_story_service.py:13 in public class `DynamicStoryService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/dynamic_story_service.py:16 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_story_service.py:16 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/dynamic_story_service.py:16 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/dynamic_story_service.py:32 in public method `generate_story`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/dynamic_story_service.py:32 in public method `generate_story`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/application/services/dynamic_story_service.py:32 in public method `generate_story`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/dynamic_story_service.py:32 in public method `generate_story`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/esp32_device_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:28 in public class `ESP32DeviceService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/esp32_device_service.py:35 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:35 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/esp32_device_service.py:35 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:47 in public method `process_sensor_reading`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:47 in public method `process_sensor_reading`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:47 in public method `process_sensor_reading`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:72 in public method `process_voice_command`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:72 in public method `process_voice_command`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:72 in public method `process_voice_command`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:97 in public method `process_gesture_event`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:97 in public method `process_gesture_event`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:97 in public method `process_gesture_event`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:125 in public method `process_firmware_update_status`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:125 in public method `process_firmware_update_status`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:125 in public method `process_firmware_update_status`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:147 in public method `process_device_status`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:147 in public method `process_device_status`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:147 in public method `process_device_status`:
        D407: Missing dashed underline after section ('Args')
src/application/services/esp32_device_service.py:169 in public method `process_edge_ai_result`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/esp32_device_service.py:169 in public method `process_edge_ai_result`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/esp32_device_service.py:169 in public method `process_edge_ai_result`:
        D407: Missing dashed underline after section ('Args')
src/application/services/feature_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/feature_service.py:19 in public class `FeatureType`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/feature_service.py:30 in public class `FeatureService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/feature_service.py:33 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/feature_service.py:58 in public method `enable_feature`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/feature_service.py:58 in public method `enable_feature`:
        D401: First line should be in imperative mood (perhaps 'Enable', not 'Enables')
src/application/services/feature_service.py:58 in public method `enable_feature`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/feature_service.py:58 in public method `enable_feature`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/feature_service.py:115 in public method `disable_feature`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/feature_service.py:115 in public method `disable_feature`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/feature_service.py:115 in public method `disable_feature`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/feature_service.py:148 in public method `get_feature_status`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/feature_service.py:148 in public method `get_feature_status`:
        D401: First line should be in imperative mood (perhaps 'Get', not 'Gets')
src/application/services/feature_service.py:148 in public method `get_feature_status`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/feature_service.py:148 in public method `get_feature_status`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/federated_learning_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:22 in public class `FederatedLearningService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/federated_learning_service.py:29 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:29 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/federated_learning_service.py:29 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/federated_learning_service.py:44 in private method `_validate_model_update_for_privacy`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:44 in private method `_validate_model_update_for_privacy`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/application/services/federated_learning_service.py:44 in private method `_validate_model_update_for_privacy`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/federated_learning_service.py:44 in private method `_validate_model_update_for_privacy`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/federated_learning_service.py:77 in private method `_initialize_global_model`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:77 in private method `_initialize_global_model`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/federated_learning_service.py:77 in private method `_initialize_global_model`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/federated_learning_service.py:77 in private method `_initialize_global_model`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/federated_learning_service.py:94 in public method `process_local_model_update`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:94 in public method `process_local_model_update`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/federated_learning_service.py:94 in public method `process_local_model_update`:
        D407: Missing dashed underline after section ('Args')
src/application/services/federated_learning_service.py:120 in private method `_aggregate_model_update`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:120 in private method `_aggregate_model_update`:
        D401: First line should be in imperative mood (perhaps 'Aggregate', not 'Aggregates')
src/application/services/federated_learning_service.py:120 in private method `_aggregate_model_update`:
        D407: Missing dashed underline after section ('Args')
src/application/services/federated_learning_service.py:138 in public method `get_global_model`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/federated_learning_service.py:138 in public method `get_global_model`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/federated_learning_service.py:138 in public method `get_global_model`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/federated_learning_service.py:138 in public method `get_global_model`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/incident_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/incident_service.py:14 in public class `IncidentService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/incident_service.py:17 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/incident_service.py:21 in public method `report_incident`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/incident_service.py:21 in public method `report_incident`:
        D401: First line should be in imperative mood (perhaps 'Report', not 'Reports')
src/application/services/incident_service.py:21 in public method `report_incident`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/incident_service.py:21 in public method `report_incident`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/incident_service.py:41 in public method `get_incident`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/incident_service.py:41 in public method `get_incident`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/incident_service.py:41 in public method `get_incident`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/incident_service.py:41 in public method `get_incident`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/incident_service.py:60 in public method `resolve_incident`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/incident_service.py:60 in public method `resolve_incident`:
        D401: First line should be in imperative mood (perhaps 'Resolve', not 'Resolves')
src/application/services/incident_service.py:60 in public method `resolve_incident`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/incident_service.py:60 in public method `resolve_incident`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/interaction_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:30 in public class `InteractionService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/interaction_service.py:40 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:40 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/interaction_service.py:40 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/interaction_service.py:57 in public method `process`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:57 in public method `process`:
        D401: First line should be in imperative mood (perhaps 'Process', not 'Processes')
src/application/services/interaction_service.py:57 in public method `process`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/interaction_service.py:57 in public method `process`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/interaction_service.py:57 in public method `process`:
        D407: Missing dashed underline after section ('Raises')
src/application/services/interaction_service.py:57 in public method `process`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D400: First line should end with a period (not 's')
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/interaction_service.py:154 in private method `_sanitize_message`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/interaction_service.py:170 in private method `_check_content_safety`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:170 in private method `_check_content_safety`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/application/services/interaction_service.py:170 in private method `_check_content_safety`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/interaction_service.py:170 in private method `_check_content_safety`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/interaction_service.py:189 in private method `_check_child_age`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/interaction_service.py:189 in private method `_check_child_age`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/interaction_service.py:189 in private method `_check_child_age`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/interaction_service.py:189 in private method `_check_child_age`:
        D407: Missing dashed underline after section ('Raises')
src/application/services/interaction_service.py:189 in private method `_check_child_age`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/application/services/notification_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/notification_service.py:41 in public class `NotificationType`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/notification_service.py:50 in public class `NotificationChannel`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/notification_service.py:59 in public class `NotificationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/notification_service.py:72 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/notification_service.py:72 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/notification_service.py:72 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/notification_service.py:102 in public method `send_notification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/notification_service.py:102 in public method `send_notification`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/application/services/notification_service.py:102 in public method `send_notification`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/notification_service.py:102 in public method `send_notification`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/notification_service.py:209 in private method `_send_by_channel`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/notification_service.py:209 in private method `_send_by_channel`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/application/services/notification_service.py:209 in private method `_send_by_channel`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/notification_service.py:209 in private method `_send_by_channel`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/notification_service.py:269 in public method `get_notification_history`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/notification_service.py:269 in public method `get_notification_history`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/notification_service.py:269 in public method `get_notification_history`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/notification_service.py:269 in public method `get_notification_history`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/parent_child_verification_service.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/parent_child_verification_service.py:25 in private function `get_verification_service`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/parent_child_verification_service.py:25 in private function `get_verification_service`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/services/parent_child_verification_service.py:25 in private function `get_verification_service`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/parent_child_verification_service.py:25 in private function `get_verification_service`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/parent_child_verification_service.py:35 in private function `get_relationship_manager`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/parent_child_verification_service.py:35 in private function `get_relationship_manager`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/application/services/parent_child_verification_service.py:35 in private function `get_relationship_manager`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/parent_child_verification_service.py:35 in private function `get_relationship_manager`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/safety.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:33 in public class `SafetyService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/safety.py:41 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:41 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/safety.py:41 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:56 in private method `_analyze_harmful_content`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:56 in private method `_analyze_harmful_content`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:124 in private method `_analyze_toxicity`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:124 in private method `_analyze_toxicity`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:161 in private method `_analyze_emotional_impact`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:161 in private method `_analyze_emotional_impact`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:200 in private method `_analyze_educational_value`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:200 in private method `_analyze_educational_value`:
        D401: First line should be in imperative mood (perhaps 'Evaluate', not 'Evaluates')
src/application/services/safety.py:200 in private method `_analyze_educational_value`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:240 in private method `_analyze_context`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:240 in private method `_analyze_context`:
        D407: Missing dashed underline after section ('Args')
src/application/services/safety.py:275 in public method `analyze_content`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:275 in public method `analyze_content`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/application/services/safety.py:275 in public method `analyze_content`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/safety.py:275 in public method `analyze_content`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/safety.py:308 in public method `get_metrics`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/safety.py:308 in public method `get_metrics`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/safety.py:308 in public method `get_metrics`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/application/services/safety.py:308 in public method `get_metrics`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/safety.py:308 in public method `get_metrics`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/transcription_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/transcription_models.py:16 in public class `TranscriptionResult`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/voice_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:25 in public class `VoiceService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/voice_service.py:25 in public class `VoiceService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:32 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:32 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/application/services/voice_service.py:32 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/voice_service.py:47 in public method `validate_audio_file`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:47 in public method `validate_audio_file`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/voice_service.py:47 in public method `validate_audio_file`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/voice_service.py:87 in public method `speech_to_text`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:87 in public method `speech_to_text`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/voice_service.py:87 in public method `speech_to_text`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/voice_service.py:159 in public method `text_to_speech`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/voice_service.py:159 in public method `text_to_speech`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/voice_service.py:159 in public method `text_to_speech`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/main_service.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/ai/main_service.py:25 in public class `AITeddyBearService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai/main_service.py:25 in public class `AITeddyBearService`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/ai/main_service.py:25 in public class `AITeddyBearService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/main_service.py:35 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/services/ai/main_service.py:232 in private method `_analyze_sentiment`:
        D401: First line should be in imperative mood; try rephrasing (found 'Simple')
src/application/services/ai/models.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/ai/utils.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/ai/utils.py:2 in public class `AIServiceUtils`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai/utils.py:40 in public method `check_age_appropriateness`:
        D401: First line should be in imperative mood; try rephrasing (found 'Simple')
src/application/services/ai/utils.py:51 in public method `analyze_sentiment`:
        D401: First line should be in imperative mood; try rephrasing (found 'Dummy')
src/application/services/ai/utils.py:82 in public method `clean_content`:
        D401: First line should be in imperative mood; try rephrasing (found 'Basic')
src/application/services/ai/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/services/ai/modules/response_generator.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/ai/modules/response_generator.py:23 in public class `ResponseType`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai/modules/response_generator.py:32 in public class `ResponseGenerator`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai/modules/response_generator.py:32 in public class `ResponseGenerator`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/ai/modules/response_generator.py:32 in public class `ResponseGenerator`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/modules/response_generator.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/services/ai/modules/response_generator.py:93 in public method `generate_response`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/ai/modules/response_generator.py:93 in public method `generate_response`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/modules/transcription_service.py:1 at module level:
        D100: Missing docstring in public module
src/application/services/ai/modules/transcription_service.py:34 in public class `TranscriptionService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/ai/modules/transcription_service.py:34 in public class `TranscriptionService`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/ai/modules/transcription_service.py:34 in public class `TranscriptionService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/modules/transcription_service.py:38 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/services/ai/modules/transcription_service.py:87 in public method `transcribe_audio`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/ai/modules/transcription_service.py:87 in public method `transcribe_audio`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/ai/modules/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/services/audio/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/application/services/consent/consent_models.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/consent/consent_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_models.py:1 at module level:
        D400: First line should end with a period (not 's')
src/application/services/consent/consent_models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/consent/consent_models.py:11 in public class `VerificationMethod`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/consent/consent_models.py:22 in public class `VerificationStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/consent/consent_models.py:33 in public class `VerificationAttempt`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/consent/consent_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/consent/consent_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:19 in public class `ConsentService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/consent/consent_service.py:19 in public class `ConsentService`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/consent/consent_service.py:19 in public class `ConsentService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:19 in public class `ConsentService`:
        D404: First word of the docstring should not be `This`
src/application/services/consent/consent_service.py:42 in public method `request_consent`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:42 in public method `request_consent`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:42 in public method `request_consent`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:68 in public method `grant_consent`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:68 in public method `grant_consent`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:68 in public method `grant_consent`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:85 in public method `revoke_consent`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:85 in public method `revoke_consent`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:85 in public method `revoke_consent`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:100 in public method `check_consent_status`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:100 in public method `check_consent_status`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:100 in public method `check_consent_status`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:126 in public method `verify_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:126 in public method `verify_parental_consent`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:126 in public method `verify_parental_consent`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:150 in public method `initiate_email_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:150 in public method `initiate_email_verification`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:150 in public method `initiate_email_verification`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:165 in public method `initiate_sms_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:165 in public method `initiate_sms_verification`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:165 in public method `initiate_sms_verification`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:177 in public method `complete_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:177 in public method `complete_verification`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:177 in public method `complete_verification`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/consent_service.py:189 in public method `get_consent_audit_trail`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/consent_service.py:189 in public method `get_consent_audit_trail`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/consent_service.py:189 in public method `get_consent_audit_trail`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/verification_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/consent/verification_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/verification_service.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/application/services/consent/verification_service.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/services/consent/verification_service.py:23 in public class `VerificationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/consent/verification_service.py:33 in public method `send_email_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/verification_service.py:33 in public method `send_email_verification`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/verification_service.py:33 in public method `send_email_verification`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/verification_service.py:67 in public method `send_sms_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/verification_service.py:67 in public method `send_sms_verification`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/verification_service.py:67 in public method `send_sms_verification`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/verification_service.py:95 in public method `verify_code`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/verification_service.py:95 in public method `verify_code`:
        D413: Missing blank line after last section ('Args')
src/application/services/consent/verification_service.py:95 in public method `verify_code`:
        D407: Missing dashed underline after section ('Args')
src/application/services/consent/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/consent/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/consent/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/application/services/consent/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/services/coppa/coppa_compliance_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:29 in public class `COPPAComplianceService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/coppa/coppa_compliance_service.py:29 in public class `COPPAComplianceService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:44 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:44 in public method `__init__`:
        D413: Missing blank line after last section ('Args')
src/application/services/coppa/coppa_compliance_service.py:44 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/services/coppa/coppa_compliance_service.py:57 in public method `validate_child_age`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:57 in public method `validate_child_age`:
        D413: Missing blank line after last section ('Returns')
src/application/services/coppa/coppa_compliance_service.py:57 in public method `validate_child_age`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/coppa/coppa_compliance_service.py:57 in public method `validate_child_age`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/coppa/coppa_compliance_service.py:103 in private method `_convert_validation_result`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:225 in public method `create_consent_record`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/coppa/coppa_compliance_service.py:225 in public method `create_consent_record`:
        D413: Missing blank line after last section ('Returns')
src/application/services/coppa/coppa_compliance_service.py:225 in public method `create_consent_record`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/coppa/coppa_compliance_service.py:225 in public method `create_consent_record`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/data_export/formatters.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/data_export/formatters.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export/formatters.py:1 at module level:
        D400: First line should end with a period (not 's')
src/application/services/data_export/formatters.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/data_export/formatters.py:21 in public class `BaseFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/formatters.py:41 in public class `JSONFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/formatters.py:67 in private method `_json_serializer`:
        D401: First line should be in imperative mood; try rephrasing (found 'Custom')
src/application/services/data_export/formatters.py:72 in public method `get_file_extension`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:75 in public method `get_mime_type`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:80 in public class `CSVFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/formatters.py:140 in public method `get_file_extension`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:143 in public method `get_mime_type`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:148 in public class `XMLFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/formatters.py:226 in public method `get_file_extension`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:229 in public method `get_mime_type`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:234 in public class `ArchiveFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/formatters.py:300 in public method `get_file_extension`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:303 in public method `get_mime_type`:
        D102: Missing docstring in public method
src/application/services/data_export/formatters.py:308 in public class `FormatterFactory`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/data_export/types.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/data_export/types.py:1 at module level:
        D400: First line should end with a period (not 's')
src/application/services/data_export/types.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/data_export/types.py:11 in public class `ExportFormat`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:21 in public class `DataCategory`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:34 in public class `ExportStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:45 in public class `ExportRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:61 in public class `ExportResult`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/data_export/types.py:77 in public class `ExportMetadata`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_manager.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/session_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:19 in public class `AsyncSessionManager`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_manager.py:19 in public class `AsyncSessionManager`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/session_manager.py:19 in public class `AsyncSessionManager`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:54 in public method `create_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:54 in public method `create_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_manager.py:74 in public method `get_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:74 in public method `get_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_manager.py:103 in public method `update_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:103 in public method `update_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_manager.py:133 in public method `end_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:133 in public method `end_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_manager.py:152 in public method `get_child_sessions`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:152 in public method `get_child_sessions`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_manager.py:173 in public method `get_session_stats`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:173 in public method `get_session_stats`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/session/session_manager.py:173 in public method `get_session_stats`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/session/session_manager.py:197 in public method `cleanup_expired_sessions`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_manager.py:197 in public method `cleanup_expired_sessions`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/session/session_manager.py:197 in public method `cleanup_expired_sessions`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/session/session_models.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/session_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_models.py:1 at module level:
        D400: First line should end with a period (not 's')
src/application/services/session/session_models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/session/session_models.py:13 in public class `SessionStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_models.py:23 in public class `AsyncSessionData`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_models.py:23 in public class `AsyncSessionData`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/session_models.py:23 in public class `AsyncSessionData`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_models.py:23 in public class `AsyncSessionData`:
        D400: First line should end with a period (not ':')
src/application/services/session/session_models.py:23 in public class `AsyncSessionData`:
        D415: First line should end with a period, question mark, or exclamation point (not ':')
src/application/services/session/session_models.py:74 in public class `SessionStats`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_storage.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/session_storage.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/application/services/session/session_storage.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/application/services/session/session_storage.py:15 in public class `SessionStorage`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/session/session_storage.py:24 in public method `store_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:24 in public method `store_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_storage.py:46 in public method `retrieve_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:46 in public method `retrieve_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_storage.py:58 in public method `remove_session`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:58 in public method `remove_session`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_storage.py:87 in public method `get_child_sessions`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:87 in public method `get_child_sessions`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_storage.py:107 in public method `cleanup_expired_sessions`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:107 in public method `cleanup_expired_sessions`:
        D407: Missing dashed underline after section ('Args')
src/application/services/session/session_storage.py:135 in public method `get_session_count`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:135 in public method `get_session_count`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/session/session_storage.py:135 in public method `get_session_count`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/session/session_storage.py:145 in public method `get_active_session_count`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/session_storage.py:145 in public method `get_active_session_count`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/session/session_storage.py:145 in public method `get_active_session_count`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/session/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/session/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/session/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/application/services/session/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/services/verification/relationship_manager.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/relationship_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/application/services/verification/relationship_manager.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/application/services/verification/relationship_manager.py:22 in public class `RelationshipManager`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/relationship_manager.py:36 in public method `create_relationship`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:36 in public method `create_relationship`:
        D413: Missing blank line after last section ('Args')
src/application/services/verification/relationship_manager.py:36 in public method `create_relationship`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/relationship_manager.py:73 in public method `verify_relationship`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:73 in public method `verify_relationship`:
        D413: Missing blank line after last section ('Args')
src/application/services/verification/relationship_manager.py:73 in public method `verify_relationship`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/relationship_manager.py:117 in public method `check_relationship_validity`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:117 in public method `check_relationship_validity`:
        D413: Missing blank line after last section ('Args')
src/application/services/verification/relationship_manager.py:117 in public method `check_relationship_validity`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/relationship_manager.py:144 in public method `get_parent_children`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:144 in public method `get_parent_children`:
        D413: Missing blank line after last section ('Args')
src/application/services/verification/relationship_manager.py:144 in public method `get_parent_children`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/relationship_manager.py:163 in public method `get_child_parents`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/relationship_manager.py:163 in public method `get_child_parents`:
        D413: Missing blank line after last section ('Args')
src/application/services/verification/relationship_manager.py:163 in public method `get_child_parents`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_models.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/verification_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_models.py:1 at module level:
        D400: First line should end with a period (not 's')
src/application/services/verification/verification_models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/services/verification/verification_models.py:11 in public class `RelationshipStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/verification_models.py:21 in public class `RelationshipType`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/verification_models.py:32 in public class `VerificationRecord`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/verification_models.py:47 in public class `RelationshipRecord`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/verification_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/verification_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:18 in public class `ParentChildVerificationService`:
        D203: 1 blank line required before class docstring (found 0)
src/application/services/verification/verification_service.py:18 in public class `ParentChildVerificationService`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/verification_service.py:18 in public class `ParentChildVerificationService`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:44 in public method `establish_relationship`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:44 in public method `establish_relationship`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_service.py:85 in public method `verify_parent_child_relationship`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:85 in public method `verify_parent_child_relationship`:
        D407: Missing dashed underline after section ('Returns')
src/application/services/verification/verification_service.py:85 in public method `verify_parent_child_relationship`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/services/verification/verification_service.py:122 in private method `_perform_strong_verification`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/verification_service.py:122 in private method `_perform_strong_verification`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:122 in private method `_perform_strong_verification`:
        D401: First line should be in imperative mood (perhaps 'Simulate', not 'Simulates')
src/application/services/verification/verification_service.py:134 in public method `get_parent_children`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:134 in public method `get_parent_children`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_service.py:149 in public method `get_child_guardians`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:149 in public method `get_child_guardians`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_service.py:169 in public method `approve_relationship`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:169 in public method `approve_relationship`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_service.py:198 in private method `_log_access_attempt`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:198 in private method `_log_access_attempt`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/verification_service.py:232 in public method `get_access_audit_trail`:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/verification_service.py:232 in public method `get_access_audit_trail`:
        D407: Missing dashed underline after section ('Args')
src/application/services/verification/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/services/verification/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/services/verification/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/application/services/verification/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/use_cases/generate_ai_response.py:1 at module level:
        D100: Missing docstring in public module
src/application/use_cases/generate_ai_response.py:12 in public class `GenerateAIResponseUseCase`:
        D203: 1 blank line required before class docstring (found 0)
src/application/use_cases/generate_ai_response.py:12 in public class `GenerateAIResponseUseCase`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/use_cases/generate_ai_response.py:12 in public class `GenerateAIResponseUseCase`:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/generate_ai_response.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/use_cases/generate_ai_response.py:28 in public method `execute`:
        D102: Missing docstring in public method
src/application/use_cases/generate_dynamic_story.py:1 at module level:
        D100: Missing docstring in public module
src/application/use_cases/generate_dynamic_story.py:8 in public class `GenerateDynamicStoryUseCase`:
        D203: 1 blank line required before class docstring (found 0)
src/application/use_cases/generate_dynamic_story.py:10 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/use_cases/generate_dynamic_story.py:19 in public method `execute`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/use_cases/generate_dynamic_story.py:19 in public method `execute`:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/generate_dynamic_story.py:19 in public method `execute`:
        D400: First line should end with a period (not 's')
src/application/use_cases/generate_dynamic_story.py:19 in public method `execute`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/application/use_cases/manage_child_profile.py:1 at module level:
        D100: Missing docstring in public module
src/application/use_cases/manage_child_profile.py:13 in public class `ManageChildProfileUseCase`:
        D101: Missing docstring in public class
src/application/use_cases/manage_child_profile.py:14 in public method `__init__`:
        D107: Missing docstring in __init__
src/application/use_cases/manage_child_profile.py:24 in public method `create_child_profile`:
        D102: Missing docstring in public method
src/application/use_cases/manage_child_profile.py:41 in public method `get_child_profile`:
        D102: Missing docstring in public method
src/application/use_cases/manage_child_profile.py:52 in public method `update_child_profile`:
        D102: Missing docstring in public method
src/application/use_cases/manage_child_profile.py:71 in public method `delete_child_profile`:
        D102: Missing docstring in public method
src/application/use_cases/process_esp32_audio.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/application/use_cases/process_esp32_audio.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/process_esp32_audio.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/application/use_cases/process_esp32_audio.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/application/use_cases/process_esp32_audio.py:21 in public class `ProcessESP32AudioUseCase`:
        D203: 1 blank line required before class docstring (found 0)
src/application/use_cases/process_esp32_audio.py:21 in public class `ProcessESP32AudioUseCase`:
        D205: 1 blank line required between summary line and description (found 0)
src/application/use_cases/process_esp32_audio.py:21 in public class `ProcessESP32AudioUseCase`:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/process_esp32_audio.py:21 in public class `ProcessESP32AudioUseCase`:
        D407: Missing dashed underline after section ('Attributes')
src/application/use_cases/process_esp32_audio.py:21 in public class `ProcessESP32AudioUseCase`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/application/use_cases/process_esp32_audio.py:46 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/process_esp32_audio.py:46 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/application/use_cases/process_esp32_audio.py:61 in public method `execute`:
        D213: Multi-line docstring summary should start at the second line
src/application/use_cases/process_esp32_audio.py:61 in public method `execute`:
        D407: Missing dashed underline after section ('Returns')
src/application/use_cases/process_esp32_audio.py:61 in public method `execute`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/application/use_cases/process_esp32_audio.py:61 in public method `execute`:
        D407: Missing dashed underline after section ('Raises')
src/application/use_cases/process_esp32_audio.py:61 in public method `execute`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/application/use_cases/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/common/constants.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/common/constants.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/common/constants.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/common/constants.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/common/constants.py:120 in public class `EventStoreType`:
        D101: Missing docstring in public class
src/common/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/common/exceptions/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/common/utils/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/analytics.py:1 at module level:
        D100: Missing docstring in public module
src/domain/analytics.py:25 in public class `ChildAnalytics`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/analytics.py:33 in public method `calculate_emotion_stability`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/analytics.py:33 in public method `calculate_emotion_stability`:
        D213: Multi-line docstring summary should start at the second line
src/domain/analytics.py:33 in public method `calculate_emotion_stability`:
        D400: First line should end with a period (not ')')
src/domain/analytics.py:33 in public method `calculate_emotion_stability`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/domain/analytics.py:69 in public method `get_speech_concerns`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/analytics.py:69 in public method `get_speech_concerns`:
        D213: Multi-line docstring summary should start at the second line
src/domain/analytics.py:69 in public method `get_speech_concerns`:
        D400: First line should end with a period (not 's')
src/domain/analytics.py:69 in public method `get_speech_concerns`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/domain/constants.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/constants.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/contracts.py:1 at module level:
        D100: Missing docstring in public module
src/domain/contracts.py:6 in public class `ContractTest`:
        D101: Missing docstring in public class
src/domain/contracts.py:15 in public class `ContractResult`:
        D101: Missing docstring in public class
src/domain/schemas.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/schemas.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/schemas.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/schemas.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/schemas.py:13 in public class `COPPAViolationType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/schemas.py:23 in public class `ValidationResult`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/schemas.py:25 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/schemas.py:58 in public function `validate_against_schema`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/schemas.py:58 in public function `validate_against_schema`:
        D213: Multi-line docstring summary should start at the second line
src/domain/schemas.py:301 in private class `ValidationSeverity`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/audio_session.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/audio_session.py:16 in public class `AudioSession`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/audio_session.py:28 in public method `create_new`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/audio_session.py:28 in public method `create_new`:
        D401: First line should be in imperative mood (perhaps 'Create', not 'Creates')
src/domain/entities/audio_session.py:28 in public method `create_new`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/audio_session.py:28 in public method `create_new`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/audio_session.py:50 in public method `mark_processed`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/audio_session.py:50 in public method `mark_processed`:
        D401: First line should be in imperative mood (perhaps 'Mark', not 'Marks')
src/domain/entities/audio_session.py:50 in public method `mark_processed`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/child.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:17 in public class `Child`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/child.py:17 in public class `Child`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:17 in public class `Child`:
        D407: Missing dashed underline after section ('Attributes')
src/domain/entities/child.py:17 in public class `Child`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/domain/entities/child.py:81 in public method `create_new`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:81 in public method `create_new`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/domain/entities/child.py:81 in public method `create_new`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/child.py:81 in public method `create_new`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/child.py:102 in public method `update_interaction_time`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:102 in public method `update_interaction_time`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/child.py:102 in public method `update_interaction_time`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/child.py:112 in public method `is_interaction_time_exceeded`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:112 in public method `is_interaction_time_exceeded`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/domain/entities/child.py:112 in public method `is_interaction_time_exceeded`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/child.py:112 in public method `is_interaction_time_exceeded`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/child.py:123 in public method `add_allowed_topic`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:123 in public method `add_allowed_topic`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/child.py:123 in public method `add_allowed_topic`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/child.py:133 in public method `add_restricted_topic`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:133 in public method `add_restricted_topic`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/child.py:133 in public method `add_restricted_topic`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/child.py:143 in public method `update_parental_controls`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child.py:143 in public method `update_parental_controls`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/child.py:143 in public method `update_parental_controls`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/child_profile.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child_profile.py:22 in public class `ChildProfile`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/child_profile.py:36 in public method `create`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child_profile.py:36 in public method `create`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/domain/entities/child_profile.py:36 in public method `create`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/child_profile.py:36 in public method `create`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/child_profile.py:81 in public method `get_uncommitted_events`:
        D401: First line should be in imperative mood (perhaps 'Return', not 'Returns')
src/domain/entities/child_profile.py:85 in public method `clear_uncommitted_events`:
        D401: First line should be in imperative mood (perhaps 'Clear', not 'Clears')
src/domain/entities/child_profile.py:89 in private method `_record_event`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/child_profile.py:89 in private method `_record_event`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/child_profile.py:89 in private method `_record_event`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/conversation.py:1 at module level:
        D100: Missing docstring in public module
src/domain/entities/conversation.py:17 in public class `InteractionType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/conversation.py:25 in public class `Conversation`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/conversation.py:43 in public method `create_new`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:43 in public method `create_new`:
        D401: First line should be in imperative mood (perhaps 'Create', not 'Creates')
src/domain/entities/conversation.py:43 in public method `create_new`:
        D413: Missing blank line after last section ('Returns')
src/domain/entities/conversation.py:43 in public method `create_new`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/conversation.py:43 in public method `create_new`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/conversation.py:67 in public method `end_conversation`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:67 in public method `end_conversation`:
        D401: First line should be in imperative mood (perhaps 'End', not 'Ends')
src/domain/entities/conversation.py:67 in public method `end_conversation`:
        D413: Missing blank line after last section ('Args')
src/domain/entities/conversation.py:67 in public method `end_conversation`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/conversation.py:80 in public method `is_active`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:80 in public method `is_active`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/domain/entities/conversation.py:80 in public method `is_active`:
        D413: Missing blank line after last section ('Returns')
src/domain/entities/conversation.py:80 in public method `is_active`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/conversation.py:80 in public method `is_active`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/conversation.py:88 in public method `duration_minutes`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:88 in public method `duration_minutes`:
        D401: First line should be in imperative mood (perhaps 'Get', not 'Gets')
src/domain/entities/conversation.py:88 in public method `duration_minutes`:
        D413: Missing blank line after last section ('Returns')
src/domain/entities/conversation.py:88 in public method `duration_minutes`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/conversation.py:88 in public method `duration_minutes`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/conversation.py:99 in public method `update_summary`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:99 in public method `update_summary`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/conversation.py:99 in public method `update_summary`:
        D413: Missing blank line after last section ('Args')
src/domain/entities/conversation.py:99 in public method `update_summary`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/conversation.py:107 in public method `update_analysis`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:107 in public method `update_analysis`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/conversation.py:107 in public method `update_analysis`:
        D413: Missing blank line after last section ('Args')
src/domain/entities/conversation.py:107 in public method `update_analysis`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/conversation.py:117 in public method `add_interaction`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/conversation.py:117 in public method `add_interaction`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/conversation.py:117 in public method `add_interaction`:
        D413: Missing blank line after last section ('Args')
src/domain/entities/conversation.py:117 in public method `add_interaction`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/emotion.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/emotion.py:12 in public class `EmotionType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/encrypted_child.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:19 in public class `EncryptedChild`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/encrypted_child.py:53 in public method `set_emergency_contacts`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:53 in public method `set_emergency_contacts`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/encrypted_child.py:70 in public method `get_emergency_contacts`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:70 in public method `get_emergency_contacts`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/encrypted_child.py:70 in public method `get_emergency_contacts`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/encrypted_child.py:84 in public method `set_medical_notes`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:84 in public method `set_medical_notes`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/encrypted_child.py:95 in public method `get_medical_notes`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:95 in public method `get_medical_notes`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/encrypted_child.py:95 in public method `get_medical_notes`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/encrypted_child.py:109 in public method `update_interaction_time`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:109 in public method `update_interaction_time`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/encrypted_child.py:109 in public method `update_interaction_time`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/encrypted_child.py:120 in public method `is_interaction_time_exceeded`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:120 in public method `is_interaction_time_exceeded`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/domain/entities/encrypted_child.py:120 in public method `is_interaction_time_exceeded`:
        D407: Missing dashed underline after section ('Returns')
src/domain/entities/encrypted_child.py:120 in public method `is_interaction_time_exceeded`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/entities/encrypted_child.py:133 in public method `add_allowed_topic`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:133 in public method `add_allowed_topic`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/encrypted_child.py:133 in public method `add_allowed_topic`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/encrypted_child.py:144 in public method `add_restricted_topic`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:144 in public method `add_restricted_topic`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/domain/entities/encrypted_child.py:144 in public method `add_restricted_topic`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/encrypted_child.py:155 in public method `update_parental_controls`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/encrypted_child.py:155 in public method `update_parental_controls`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/domain/entities/encrypted_child.py:155 in public method `update_parental_controls`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/user.py:1 at module level:
        D100: Missing docstring in public module
src/domain/entities/user.py:4 in public class `User`:
        D101: Missing docstring in public class
src/domain/entities/user.py:5 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/entities/user.py:23 in public method `__repr__`:
        D105: Missing docstring in magic method
src/domain/entities/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/entities/parent_profile/entities.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/domain/entities/parent_profile/entities.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/domain/entities/parent_profile/entities.py:11 in public class `Parent`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/parent_profile/entities.py:11 in public class `Parent`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/entities/parent_profile/entities.py:11 in public class `Parent`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/parent_profile/entities.py:53 in public method `get_full_name`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/entities/parent_profile/entities.py:53 in public method `get_full_name`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/parent_profile/entities.py:90 in public method `add_child`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/parent_profile/entities.py:90 in public method `add_child`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/parent_profile/entities.py:107 in public method `remove_child`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/parent_profile/entities.py:107 in public method `remove_child`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/parent_profile/entities.py:121 in public method `update_preference`:
        D213: Multi-line docstring summary should start at the second line
src/domain/entities/parent_profile/entities.py:121 in public method `update_preference`:
        D407: Missing dashed underline after section ('Args')
src/domain/entities/parent_profile/entities.py:201 in public method `__str__`:
        D401: First line should be in imperative mood; try rephrasing (found 'String')
src/domain/entities/parent_profile/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/entities/voice_games/voice_games_engine.py:1 at module level:
        D100: Missing docstring in public module
src/domain/entities/voice_games/voice_games_engine.py:18 in public class `GameType`:
        D101: Missing docstring in public class
src/domain/entities/voice_games/voice_games_engine.py:25 in public class `GameSession`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/voice_games/voice_games_engine.py:27 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/entities/voice_games/voice_games_engine.py:39 in public class `VoiceGameEngine`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/entities/voice_games/voice_games_engine.py:41 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/entities/voice_games/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/esp32/models.py:1 at module level:
        D100: Missing docstring in public module
src/domain/esp32/models.py:7 in public class `ESP32SensorReading`:
        D101: Missing docstring in public class
src/domain/esp32/models.py:17 in public class `ESP32VoiceCommand`:
        D101: Missing docstring in public class
src/domain/esp32/models.py:25 in public class `ESP32GestureEvent`:
        D101: Missing docstring in public class
src/domain/esp32/models.py:34 in public class `ESP32FirmwareUpdateStatus`:
        D101: Missing docstring in public class
src/domain/esp32/models.py:44 in public class `ESP32DeviceStatus`:
        D101: Missing docstring in public class
src/domain/esp32/models.py:55 in public class `ESP32EdgeAIResult`:
        D101: Missing docstring in public class
src/domain/esp32/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/events/child_profile_updated.py:1 at module level:
        D100: Missing docstring in public module
src/domain/events/child_profile_updated.py:9 in public class `ChildProfileUpdated`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/events/child_registered.py:1 at module level:
        D100: Missing docstring in public module
src/domain/events/child_registered.py:9 in public class `ChildRegistered`:
        D101: Missing docstring in public class
src/domain/events/child_registered.py:16 in public method `create`:
        D102: Missing docstring in public method
src/domain/events/conversation_started.py:12 in public class `ConversationStarted`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/events/conversation_started.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/events/conversation_updated.py:1 at module level:
        D100: Missing docstring in public module
src/domain/events/conversation_updated.py:8 in public class `ConversationUpdatedEvent`:
        D101: Missing docstring in public class
src/domain/events/domain_events.py:1 at module level:
        D100: Missing docstring in public module
src/domain/events/domain_events.py:7 in public class `DomainEvent`:
        D101: Missing docstring in public class
src/domain/events/domain_events.py:11 in public method `__post_init__`:
        D105: Missing docstring in magic method
src/domain/events/domain_events.py:19 in public method `new_event`:
        D102: Missing docstring in public method
src/domain/events/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/exceptions/base.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:1 at module level:
        D400: First line should end with a period (not 's')
src/domain/exceptions/base.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/domain/exceptions/base.py:13 in public class `TeddyBearException`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base.py:13 in public class `TeddyBearException`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base.py:13 in public class `TeddyBearException`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:25 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:25 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/domain/exceptions/base.py:58 in public class `ParentalConsentRequiredException`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base.py:58 in public class `ParentalConsentRequiredException`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base.py:58 in public class `ParentalConsentRequiredException`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:69 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:69 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/domain/exceptions/base.py:96 in public class `CircuitBreakerOpenException`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base.py:96 in public class `CircuitBreakerOpenException`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base.py:96 in public class `CircuitBreakerOpenException`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:101 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:101 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/domain/exceptions/base.py:127 in public class `StartupValidationException`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base.py:127 in public class `StartupValidationException`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base.py:127 in public class `StartupValidationException`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base.py:133 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/base_exceptions.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base_exceptions.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base_exceptions.py:10 in public class `DomainException`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base_exceptions.py:10 in public class `DomainException`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/base_exceptions.py:10 in public class `DomainException`:
        D213: Multi-line docstring summary should start at the second line
src/domain/exceptions/base_exceptions.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/base_exceptions.py:37 in public class `ValidationError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base_exceptions.py:39 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/base_exceptions.py:57 in public class `AuthorizationError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base_exceptions.py:59 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/base_exceptions.py:77 in public class `NotFoundError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base_exceptions.py:79 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/base_exceptions.py:97 in public class `ConflictError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/base_exceptions.py:99 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/exceptions/child_exceptions.py:7 in public class `ChildNotFoundError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/child_exceptions.py:7 in public class `ChildNotFoundError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/child_exceptions.py:12 in public class `ChildCreationError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/child_exceptions.py:12 in public class `ChildCreationError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/child_exceptions.py:17 in public class `ChildAccessDeniedError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/child_exceptions.py:17 in public class `ChildAccessDeniedError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/child_exceptions.py:22 in public class `InvalidChildAgeError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/child_exceptions.py:22 in public class `InvalidChildAgeError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/security_exceptions.py:7 in public class `SecurityValidationError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/security_exceptions.py:7 in public class `SecurityValidationError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/security_exceptions.py:12 in public class `AuthenticationError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/security_exceptions.py:12 in public class `AuthenticationError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/security_exceptions.py:17 in public class `PermissionDeniedError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/security_exceptions.py:17 in public class `PermissionDeniedError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/security_exceptions.py:22 in public class `ContentSafetyError`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/exceptions/security_exceptions.py:22 in public class `ContentSafetyError`:
        D204: 1 blank line required after class docstring (found 0)
src/domain/exceptions/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/exceptions/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/accessibility_profile_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/accessibility_profile_repository.py:8 in public class `IAccessibilityProfileRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/accessibility_profile_repository.py:15 in public method `get_profile_by_child_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/accessibility_profile_repository.py:19 in public method `save_profile`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/accessibility_profile_repository.py:23 in public method `delete_profile`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/accessibility_profile_repository.py:27 in public method `get_all_profiles`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/ai_service_interface.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/ai_service_interface.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/ai_service_interface.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/interfaces/ai_service_interface.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/interfaces/ai_service_interface.py:11 in public class `AIServiceInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/ai_service_interface.py:20 in public method `generate_response`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/ai_service_interface.py:20 in public method `generate_response`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/ai_service_interface.py:20 in public method `generate_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/ai_service_interface.py:34 in public method `assess_content_safety`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/ai_service_interface.py:34 in public method `assess_content_safety`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/ai_service_interface.py:34 in public method `assess_content_safety`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/child_profile_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/child_profile_repository.py:10 in public class `IChildProfileRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/child_profile_repository.py:14 in public method `get_profile_by_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/child_profile_repository.py:18 in public method `save_profile`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/child_profile_repository.py:22 in public method `delete_profile`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/child_profile_repository.py:26 in public method `get_child_age`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/config_interface.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/config_interface.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/config_interface.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/interfaces/config_interface.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/interfaces/config_interface.py:10 in public class `ConfigInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/conversation_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/conversation_repository.py:8 in public class `IConversationRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/conversation_repository.py:12 in public method `save`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/conversation_repository.py:16 in public method `find_by_child_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/conversation_repository.py:20 in public method `get_by_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/device_authenticator.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/device_authenticator.py:5 in public class `IDeviceAuthenticator`:
        D101: Missing docstring in public class
src/domain/interfaces/device_authenticator.py:8 in public method `authenticate_device`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/device_authenticator.py:8 in public method `authenticate_device`:
        D401: First line should be in imperative mood (perhaps 'Authenticate', not 'Authenticates')
src/domain/interfaces/device_authenticator.py:8 in public method `authenticate_device`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/device_authenticator.py:8 in public method `authenticate_device`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/encryption_interface.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/domain/interfaces/encryption_interface.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/domain/interfaces/encryption_interface.py:13 in public class `EncryptionServiceInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/encryption_interface.py:13 in public class `EncryptionServiceInterface`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/encryption_interface.py:13 in public class `EncryptionServiceInterface`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:20 in public method `encrypt`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:20 in public method `encrypt`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:20 in public method `encrypt`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:32 in public method `decrypt`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:32 in public method `decrypt`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:32 in public method `decrypt`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:44 in public method `is_available`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:44 in public method `is_available`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:44 in public method `is_available`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:53 in public class `SecureFieldInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/encryption_interface.py:53 in public class `SecureFieldInterface`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/encryption_interface.py:53 in public class `SecureFieldInterface`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:60 in public method `get_value`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:60 in public method `get_value`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:60 in public method `get_value`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:69 in public method `is_encrypted`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:69 in public method `is_encrypted`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:69 in public method `is_encrypted`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:78 in public method `get_encrypted_representation`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:78 in public method `get_encrypted_representation`:
        D407: Missing dashed underline after section ('Returns')
src/domain/interfaces/encryption_interface.py:78 in public method `get_encrypted_representation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/interfaces/encryption_interface.py:87 in public class `NullEncryptionService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/encryption_interface.py:87 in public class `NullEncryptionService`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/encryption_interface.py:87 in public class `NullEncryptionService`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:101 in public method `is_available`:
        D401: First line should be in imperative mood; try rephrasing (found 'Always')
src/domain/interfaces/encryption_interface.py:106 in public class `SecureString`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/encryption_interface.py:106 in public class `SecureString`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/encryption_interface.py:106 in public class `SecureString`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:112 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/encryption_interface.py:112 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/domain/interfaces/event_bus_interface.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/event_bus_interface.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/event_bus_interface.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/interfaces/event_bus_interface.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/interfaces/event_bus_interface.py:11 in public class `EventBusInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/external_service_interfaces.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/external_service_interfaces.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/external_service_interfaces.py:12 in public class `IAIService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/external_service_interfaces.py:30 in public class `INotificationService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/logging_interface.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/logging_interface.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/logging_interface.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/domain/interfaces/logging_interface.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/domain/interfaces/logging_interface.py:13 in public class `LogLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/logging_interface.py:23 in public class `DomainLoggerInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/logging_interface.py:23 in public class `DomainLoggerInterface`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/logging_interface.py:23 in public class `DomainLoggerInterface`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/logging_interface.py:36 in public method `log_domain_event`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/logging_interface.py:36 in public method `log_domain_event`:
        D407: Missing dashed underline after section ('Args')
src/domain/interfaces/logging_interface.py:53 in public method `log_business_rule_violation`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/logging_interface.py:53 in public method `log_business_rule_violation`:
        D407: Missing dashed underline after section ('Args')
src/domain/interfaces/logging_interface.py:70 in public method `log_child_safety_event`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/logging_interface.py:70 in public method `log_child_safety_event`:
        D407: Missing dashed underline after section ('Args')
src/domain/interfaces/logging_interface.py:82 in public class `NullDomainLogger`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/logging_interface.py:82 in public class `NullDomainLogger`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/logging_interface.py:82 in public class `NullDomainLogger`:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/notification_clients.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/notification_clients.py:5 in public class `IEmailClient`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/notification_clients.py:8 in public method `send_email`:
        D102: Missing docstring in public method
src/domain/interfaces/notification_clients.py:12 in public class `ISMSClient`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/notification_clients.py:15 in public method `send_sms`:
        D102: Missing docstring in public method
src/domain/interfaces/notification_clients.py:19 in public class `IInAppNotifier`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/notification_clients.py:22 in public method `send_in_app_notification`:
        D102: Missing docstring in public method
src/domain/interfaces/notification_clients.py:31 in public class `IPushNotifier`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/notification_clients.py:34 in public method `send_push_notification`:
        D102: Missing docstring in public method
src/domain/interfaces/notification_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/notification_repository.py:8 in public class `INotificationRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/notification_repository.py:12 in public method `save_notification`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/notification_repository.py:19 in public method `get_notification_by_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/notification_repository.py:26 in public method `get_notifications_for_recipient`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/notification_repository.py:30 in public method `delete_notification`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/personality_profile_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/personality_profile_repository.py:10 in public class `IPersonalityProfileRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/personality_profile_repository.py:14 in public method `get_profile_by_child_id`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/personality_profile_repository.py:18 in public method `save_profile`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/personality_profile_repository.py:22 in public method `delete_profile`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/personality_profile_repository.py:26 in public method `get_all_profiles`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/repository_interfaces.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/repository_interfaces.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/repository_interfaces.py:15 in public class `IChildRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/repository_interfaces.py:39 in public class `IUserRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/sanitization_service.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/sanitization_service.py:5 in public class `ISanitizationService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/sanitization_service.py:8 in public method `sanitize_text`:
        D102: Missing docstring in public method
src/domain/interfaces/sanitization_service.py:11 in public method `detect_pii`:
        D102: Missing docstring in public method
src/domain/interfaces/security_interfaces.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/security_interfaces.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/interfaces/security_interfaces.py:12 in public class `IEncryptionService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/security_interfaces.py:32 in public class `ISecurityService`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/session_repository.py:1 at module level:
        D100: Missing docstring in public module
src/domain/interfaces/session_repository.py:9 in public class `ISessionRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/interfaces/session_repository.py:13 in public method `get`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/domain/interfaces/session_repository.py:17 in public method `save`:
        D401: First line should be in imperative mood (perhaps 'Save', not 'Saves')
src/domain/interfaces/session_repository.py:21 in public method `delete`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/session_repository.py:25 in public method `delete_expired`:
        D401: First line should be in imperative mood (perhaps 'Delete', not 'Deletes')
src/domain/interfaces/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/interfaces/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/models/consent_models.py:1 at module level:
        D100: Missing docstring in public module
src/domain/models/consent_models.py:7 in public class `ConsentType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/models/consent_models.py:22 in public class `ConsentStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/models/consent_models.py:33 in public class `ConsentRecord`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/models/consent_models.py:35 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/models/data_retention_models.py:1 at module level:
        D100: Missing docstring in public module
src/domain/models/data_retention_models.py:5 in public class `DataType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/models/data_retention_models.py:18 in public class `RetentionPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/models/data_retention_models.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/repositories/event_store.py:9 in public class `EventStore`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/repositories/event_store.py:33 in public class `InMemoryEventStore`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/repositories/event_store.py:35 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/repositories/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/safety/models.py:13 in public class `RiskLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:24 in public class `ContentCategory`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:39 in public class `ToxicityResult`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:50 in public class `EmotionalImpact`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:62 in public class `EducationalValue`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:73 in public class `ContextAnalysis`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:90 in public class `ContentModification`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:104 in public class `BiasAnalysis`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:117 in public class `SafetyAnalysisResult`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:157 in public class `SafetyConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:199 in private method `_load_safety_patterns`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:199 in private method `_load_safety_patterns`:
        D407: Missing dashed underline after section ('Returns')
src/domain/safety/models.py:199 in private method `_load_safety_patterns`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/safety/models.py:222 in private method `_load_age_restrictions`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:222 in private method `_load_age_restrictions`:
        D407: Missing dashed underline after section ('Returns')
src/domain/safety/models.py:222 in private method `_load_age_restrictions`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/safety/models.py:326 in private method `_get_age_limits`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:326 in private method `_get_age_limits`:
        D407: Missing dashed underline after section ('Args')
src/domain/safety/models.py:340 in private method `_calculate_risk_score`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:340 in private method `_calculate_risk_score`:
        D407: Missing dashed underline after section ('Args')
src/domain/safety/models.py:360 in private method `_score_to_risk_level`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:360 in private method `_score_to_risk_level`:
        D407: Missing dashed underline after section ('Args')
src/domain/safety/models.py:376 in public class `ProfanityRule`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/safety/models.py:378 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/safety/models.py:404 in public method `check_content`:
        D213: Multi-line docstring summary should start at the second line
src/domain/safety/models.py:404 in public method `check_content`:
        D407: Missing dashed underline after section ('Args')
src/domain/safety/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/safety/bias_detector/bias_detector.py:1 at module level:
        D100: Missing docstring in public module
src/domain/safety/bias_detector/bias_detector.py:8 in public class `AIBiasDetector`:
        D101: Missing docstring in public class
src/domain/safety/bias_detector/bias_detector.py:9 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/safety/bias_detector/bias_detector.py:22 in public method `detect_bias`:
        D102: Missing docstring in public method
src/domain/safety/bias_detector/bias_detector.py:102 in public method `batch_analyze_bias`:
        D102: Missing docstring in public method
src/domain/safety/bias_detector/bias_detector.py:115 in public method `get_bias_statistics`:
        D102: Missing docstring in public method
src/domain/safety/bias_detector/bias_detector.py:118 in public method `generate_bias_report`:
        D102: Missing docstring in public method
src/domain/safety/bias_detector/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/safety/bias_models/bias_models.py:1 at module level:
        D100: Missing docstring in public module
src/domain/safety/bias_models/bias_models.py:5 in public class `ConversationContext`:
        D101: Missing docstring in public class
src/domain/safety/bias_models/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/services/age_filter.py:1 at module level:
        D100: Missing docstring in public module
src/domain/services/age_filter.py:7 in public class `AgeFilter`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/age_filter.py:10 in public method `filter_content`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/age_filter.py:10 in public method `filter_content`:
        D413: Missing blank line after last section ('Returns')
src/domain/services/age_filter.py:10 in public method `filter_content`:
        D407: Missing dashed underline after section ('Returns')
src/domain/services/age_filter.py:10 in public method `filter_content`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/services/age_filter.py:22 in public method `is_age_appropriate`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/age_filter.py:22 in public method `is_age_appropriate`:
        D413: Missing blank line after last section ('Returns')
src/domain/services/age_filter.py:22 in public method `is_age_appropriate`:
        D407: Missing dashed underline after section ('Returns')
src/domain/services/age_filter.py:22 in public method `is_age_appropriate`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/services/coppa_age_validation.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/services/coppa_age_validation.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/domain/services/coppa_age_validation.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/domain/services/coppa_age_validation.py:11 in public class `AgeValidationResult`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/coppa_age_validation.py:22 in public class `COPPAAgeValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/coppa_age_validation.py:30 in public method `validate_age`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:30 in public method `validate_age`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:52 in public method `validate_birthdate`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:52 in public method `validate_birthdate`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:77 in public method `get_age_from_birthdate`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:77 in public method `get_age_from_birthdate`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:94 in public method `requires_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:94 in public method `requires_parental_consent`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:110 in public method `is_coppa_applicable`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:110 in public method `is_coppa_applicable`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:123 in public method `get_validation_details`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:123 in public method `get_validation_details`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:182 in public function `validate_child_age`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:182 in public function `validate_child_age`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/domain/services/coppa_age_validation.py:182 in public function `validate_child_age`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/coppa_age_validation.py:194 in public function `is_age_coppa_compliant`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/coppa_age_validation.py:194 in public function `is_age_coppa_compliant`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/emotion_analyzer.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/services/emotion_analyzer.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/services/emotion_analyzer.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/services/emotion_analyzer.py:12 in public class `EmotionResult`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/emotion_analyzer.py:31 in public class `EmotionAnalyzer`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/emotion_analyzer.py:52 in public method `analyze_text`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:52 in public method `analyze_text`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/emotion_analyzer.py:112 in public method `analyze_voice`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:112 in public method `analyze_voice`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/emotion_analyzer.py:161 in public method `get_child_appropriate_emotions`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:161 in public method `get_child_appropriate_emotions`:
        D407: Missing dashed underline after section ('Returns')
src/domain/services/emotion_analyzer.py:161 in public method `get_child_appropriate_emotions`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/domain/services/emotion_analyzer.py:181 in public method `is_emotion_positive`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:181 in public method `is_emotion_positive`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/emotion_analyzer.py:192 in public method `requires_attention`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/emotion_analyzer.py:192 in public method `requires_attention`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/parental_consent_enforcer.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/services/parental_consent_enforcer.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/parental_consent_enforcer.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/domain/services/parental_consent_enforcer.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/domain/services/parental_consent_enforcer.py:24 in public class `ParentalConsentEnforcer`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/services/parental_consent_enforcer.py:26 in public method `__init__`:
        D107: Missing docstring in __init__
src/domain/services/parental_consent_enforcer.py:60 in public method `get_required_consents`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/parental_consent_enforcer.py:60 in public method `get_required_consents`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/parental_consent_enforcer.py:87 in public method `validate_consent_for_operation`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/parental_consent_enforcer.py:87 in public method `validate_consent_for_operation`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/parental_consent_enforcer.py:142 in public method `validate_all_required_consents`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/parental_consent_enforcer.py:142 in public method `validate_all_required_consents`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/parental_consent_enforcer.py:247 in public method `get_consent_requirements_summary`:
        D213: Multi-line docstring summary should start at the second line
src/domain/services/parental_consent_enforcer.py:247 in public method `get_consent_requirements_summary`:
        D407: Missing dashed underline after section ('Args')
src/domain/services/safety_validator.py:1 at module level:
        D100: Missing docstring in public module
src/domain/services/safety_validator.py:6 in public class `SafetyValidator`:
        D101: Missing docstring in public class
src/domain/services/safety_validator.py:7 in public method `validate_text`:
        D102: Missing docstring in public method
src/domain/services/safety_validator.py:9 in public method `validate_audio`:
        D102: Missing docstring in public method
src/domain/services/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/domain/value_objects/accessibility.py:1 at module level:
        D100: Missing docstring in public module
src/domain/value_objects/accessibility.py:7 in public class `SpecialNeedType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/accessibility.py:20 in public class `AccessibilityProfile`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/accessibility.py:20 in public class `AccessibilityProfile`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/accessibility.py:20 in public class `AccessibilityProfile`:
        D407: Missing dashed underline after section ('Attributes')
src/domain/value_objects/accessibility.py:20 in public class `AccessibilityProfile`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/domain/value_objects/child_age.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/child_age.py:12 in public class `AgeCategory`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/child_age.py:23 in public class `ChildAge`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/child_age.py:23 in public class `ChildAge`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/value_objects/child_age.py:23 in public class `ChildAge`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/child_age.py:23 in public class `ChildAge`:
        D400: First line should end with a period (not 't')
src/domain/value_objects/child_age.py:23 in public class `ChildAge`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/domain/value_objects/child_age.py:173 in public method `__str__`:
        D105: Missing docstring in magic method
src/domain/value_objects/child_age.py:178 in public method `__repr__`:
        D105: Missing docstring in magic method
src/domain/value_objects/child_name.py:8 in public class `ChildName`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/child_name.py:12 in public method `__post_init__`:
        D105: Missing docstring in magic method
src/domain/value_objects/child_preferences.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/value_objects/child_preferences.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/child_preferences.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/domain/value_objects/child_preferences.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/domain/value_objects/child_preferences.py:13 in public class `AgeGroup`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/child_preferences.py:40 in public class `ChildPreferences`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/encrypted_field.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/value_objects/encrypted_field.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/domain/value_objects/encrypted_field.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/domain/value_objects/encrypted_field.py:16 in public class `EncryptedField`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/encrypted_field.py:16 in public class `EncryptedField`:
        D205: 1 blank line required between summary line and description (found 0)
src/domain/value_objects/encrypted_field.py:16 in public class `EncryptedField`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:26 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:26 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/domain/value_objects/encrypted_field.py:39 in private method `_serialize_and_encrypt`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:39 in private method `_serialize_and_encrypt`:
        D407: Missing dashed underline after section ('Args')
src/domain/value_objects/encrypted_field.py:76 in private method `_deserialize_value`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:76 in private method `_deserialize_value`:
        D407: Missing dashed underline after section ('Args')
src/domain/value_objects/encrypted_field.py:105 in public method `from_encrypted_data`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/encrypted_field.py:105 in public method `from_encrypted_data`:
        D407: Missing dashed underline after section ('Args')
src/domain/value_objects/language.py:1 at module level:
        D100: Missing docstring in public module
src/domain/value_objects/language.py:4 in public class `Language`:
        D101: Missing docstring in public class
src/domain/value_objects/language.py:13 in public method `from_code`:
        D102: Missing docstring in public method
src/domain/value_objects/notification.py:1 at module level:
        D100: Missing docstring in public module
src/domain/value_objects/notification.py:9 in public class `NotificationStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/notification.py:21 in public class `NotificationRecord`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/personality.py:1 at module level:
        D100: Missing docstring in public module
src/domain/value_objects/personality.py:9 in public class `PersonalityType`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/personality.py:22 in public class `ChildPersonality`:
        D203: 1 blank line required before class docstring (found 0)
src/domain/value_objects/personality.py:22 in public class `ChildPersonality`:
        D213: Multi-line docstring summary should start at the second line
src/domain/value_objects/personality.py:22 in public class `ChildPersonality`:
        D407: Missing dashed underline after section ('Attributes')
src/domain/value_objects/personality.py:22 in public class `ChildPersonality`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/domain/value_objects/safety_level.py:1 at module level:
        D100: Missing docstring in public module
src/domain/value_objects/safety_level.py:3 in public class `SafetyLevel`:
        D101: Missing docstring in public class
src/domain/value_objects/safety_level.py:13 in public method `create_safe_level`:
        D102: Missing docstring in public method
src/domain/value_objects/safety_level.py:17 in public method `is_safe`:
        D102: Missing docstring in public method
src/domain/value_objects/safety_level.py:22 in public method `level`:
        D102: Missing docstring in public method
src/domain/value_objects/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/app_initializer.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/app_initializer.py:7 in public class `AppInitializer`:
        D101: Missing docstring in public class
src/infrastructure/app_initializer.py:8 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/app_initializer.py:13 in public method `get_settings`:
        D102: Missing docstring in public method
src/infrastructure/app_initializer.py:18 in public method `get_container`:
        D102: Missing docstring in public method
src/infrastructure/app_initializer.py:23 in public method `wire_container`:
        D102: Missing docstring in public method
src/infrastructure/app_initializer.py:26 in public method `get_logger`:
        D102: Missing docstring in public method
src/infrastructure/dependencies.py:12 in public function `Depends`:
        D103: Missing docstring in public function
src/infrastructure/dependencies.py:22 in public function `get_event_store`:
        D103: Missing docstring in public function
src/infrastructure/dependencies.py:27 in public function `get_child_repository`:
        D103: Missing docstring in public function
src/infrastructure/dependencies.py:35 in public class `MockManageChildProfileUseCase`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/dependencies.py:37 in public method `create_child_profile`:
        D102: Missing docstring in public method
src/infrastructure/dependencies.py:50 in public method `get_child_profile`:
        D102: Missing docstring in public method
src/infrastructure/dependencies.py:58 in public method `update_child_profile`:
        D102: Missing docstring in public method
src/infrastructure/dependencies.py:72 in public method `delete_child_profile`:
        D102: Missing docstring in public method
src/infrastructure/dependencies.py:77 in public class `MockGenerateDynamicStoryUseCase`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/dependencies.py:79 in public method `generate_story`:
        D102: Missing docstring in public method
src/infrastructure/exceptions.py:1 at module level:
        D400: First line should end with a period (not 'm')
src/infrastructure/exceptions.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/infrastructure/exceptions.py:13 in public class `ErrorCode`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/exceptions.py:13 in public class `ErrorCode`:
        D400: First line should end with a period (not 's')
src/infrastructure/exceptions.py:13 in public class `ErrorCode`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/exceptions.py:48 in public class `BaseApplicationException`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/exceptions.py:50 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:73 in public class `AuthenticationException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:74 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:83 in public class `ChildSafetyException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:84 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:93 in public class `DataValidationException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:94 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:103 in public class `ResourceNotFoundException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:104 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:109 in public class `SystemException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:110 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exceptions.py:119 in public class `ExternalServiceException`:
        D101: Missing docstring in public class
src/infrastructure/exceptions.py:120 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/logging_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:51 in public function `configure_logging`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/logging_config.py:51 in public function `configure_logging`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:51 in public function `configure_logging`:
        D401: First line should be in imperative mood (perhaps 'Configure', not 'Configures')
src/infrastructure/logging_config.py:51 in public function `configure_logging`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/logging_config.py:145 in public function `get_logger`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:145 in public function `get_logger`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/infrastructure/logging_config.py:145 in public function `get_logger`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/logging_config.py:145 in public function `get_logger`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/logging_config.py:172 in public function `log_security_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:172 in public function `log_security_event`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/infrastructure/logging_config.py:172 in public function `log_security_event`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/logging_config.py:197 in public class `ChildSafetyFilter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/logging_config.py:197 in public class `ChildSafetyFilter`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/logging_config.py:197 in public class `ChildSafetyFilter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:203 in public method `filter`:
        D102: Missing docstring in public method
src/infrastructure/logging_config.py:251 in public class `ProductionFormatter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/logging_config.py:251 in public class `ProductionFormatter`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/logging_config.py:251 in public class `ProductionFormatter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:258 in public method `format`:
        D102: Missing docstring in public method
src/infrastructure/logging_config.py:280 in public function `log_child_interaction`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/logging_config.py:280 in public function `log_child_interaction`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/logging_config.py:280 in public function `log_child_interaction`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/infrastructure/logging_config.py:280 in public function `log_child_interaction`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/adapters/encryption_adapter.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/adapters/encryption_adapter.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/adapters/encryption_adapter.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/adapters/encryption_adapter.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/adapters/encryption_adapter.py:12 in public class `InfrastructureEncryptionAdapter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/adapters/encryption_adapter.py:12 in public class `InfrastructureEncryptionAdapter`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/adapters/encryption_adapter.py:12 in public class `InfrastructureEncryptionAdapter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/ai/models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/ai/models.py:4 in public class `ConversationContext`:
        D101: Missing docstring in public class
src/infrastructure/ai/prompt_builder.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/ai/prompt_builder.py:5 in public class `PromptBuilder`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/prompt_builder.py:13 in public method `build_child_safe_prompt`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/ai/prompt_builder.py:13 in public method `build_child_safe_prompt`:
        D401: First line should be in imperative mood (perhaps 'Construct', not 'Constructs')
src/infrastructure/ai/prompt_builder.py:13 in public method `build_child_safe_prompt`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/ai/prompt_builder.py:13 in public method `build_child_safe_prompt`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/ai/real_ai_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/ai/real_ai_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/ai/real_ai_service.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/ai/real_ai_service.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/ai/real_ai_service.py:26 in public class `ProductionAIService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/real_ai_service.py:26 in public class `ProductionAIService`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/ai/real_ai_service.py:26 in public class `ProductionAIService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/ai/real_ai_service.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/safety_analyzer.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/ai/safety_analyzer.py:9 in public class `SafetyAnalyzer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/safety_analyzer.py:11 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/safety_analyzer.py:48 in public method `analyze_safety`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/ai/safety_analyzer.py:48 in public method `analyze_safety`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/infrastructure/ai/safety_analyzer.py:48 in public method `analyze_safety`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/ai/safety_analyzer.py:48 in public method `analyze_safety`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/ai/chatgpt/client.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/ai/chatgpt/client.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/ai/chatgpt/client.py:35 in public class `ChatGPTClient`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/chatgpt/client.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/chatgpt/fallback_responses.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/ai/chatgpt/fallback_responses.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/ai/chatgpt/fallback_responses.py:13 in public class `FallbackResponseGenerator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/chatgpt/fallback_responses.py:13 in public class `FallbackResponseGenerator`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:13 in public class `FallbackResponseGenerator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/chatgpt/fallback_responses.py:111 in public method `generate_fallback_response`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:111 in public method `generate_fallback_response`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:144 in public method `generate_safety_redirect_response`:
        D400: First line should end with a period (not 'ن')
src/infrastructure/ai/chatgpt/fallback_responses.py:144 in public method `generate_safety_redirect_response`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ن')
src/infrastructure/ai/chatgpt/fallback_responses.py:177 in public method `generate_encouragement_response`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:177 in public method `generate_encouragement_response`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:191 in public method `generate_learning_suggestion`:
        D400: First line should end with a period (not 'ي')
src/infrastructure/ai/chatgpt/fallback_responses.py:191 in public method `generate_learning_suggestion`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ي')
src/infrastructure/ai/chatgpt/fallback_responses.py:207 in public method `get_conversation_starter`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/fallback_responses.py:207 in public method `get_conversation_starter`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:1 at module level:
        D400: First line should end with a period (not 't')
src/infrastructure/ai/chatgpt/response_enhancer.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/ai/chatgpt/response_enhancer.py:18 in public class `ResponseEnhancer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/chatgpt/response_enhancer.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/chatgpt/response_enhancer.py:80 in private method `_apply_age_specific_enhancements`:
        D400: First line should end with a period (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:80 in private method `_apply_age_specific_enhancements`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:94 in private method `_simplify_language`:
        D400: First line should end with a period (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:94 in private method `_simplify_language`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:130 in private method `_add_repetition`:
        D400: First line should end with a period (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:130 in private method `_add_repetition`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ر')
src/infrastructure/ai/chatgpt/response_enhancer.py:145 in private method `_add_sound_effects`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/ai/chatgpt/response_enhancer.py:145 in private method `_add_sound_effects`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/ai/chatgpt/response_enhancer.py:162 in private method `_add_educational_elements`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:162 in private method `_add_educational_elements`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:180 in private method `_add_interactive_elements`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:180 in private method `_add_interactive_elements`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:188 in private method `_add_encouragement`:
        D400: First line should end with a period (not 'ع')
src/infrastructure/ai/chatgpt/response_enhancer.py:188 in private method `_add_encouragement`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ع')
src/infrastructure/ai/chatgpt/response_enhancer.py:196 in private method `_add_follow_up_question`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:196 in private method `_add_follow_up_question`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:206 in private method `_apply_child_preferences`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/ai/chatgpt/response_enhancer.py:206 in private method `_apply_child_preferences`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/ai/chatgpt/response_enhancer.py:228 in public method `detect_emotion`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/ai/chatgpt/response_enhancer.py:228 in public method `detect_emotion`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/ai/chatgpt/safety_filter.py:1 at module level:
        D400: First line should end with a period (not 'g')
src/infrastructure/ai/chatgpt/safety_filter.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/infrastructure/ai/chatgpt/safety_filter.py:18 in public class `SafetyFilter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/ai/chatgpt/safety_filter.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/ai/chatgpt/__init__.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/ai/chatgpt/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/caching/cache_config.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/caching/cache_config.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/caching/cache_config.py:5 in public class `CacheConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/caching/redis_cache.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/caching/redis_cache.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/caching/redis_cache.py:14 in public class `RedisCacheManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/caching/redis_cache.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/caching/__init__.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/caching/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/caching/strategies/invalidation_strategy.py:13 in public class `CacheInvalidationStrategy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/caching/strategies/invalidation_strategy.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/chaos/actions/ai.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/ai.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/ai.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/chaos/actions/ai.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/chaos/actions/ai.py:20 in public class `AIChaosActions`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/actions/ai_model_recovery_testing.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/ai_model_recovery_testing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/ai_model_recovery_testing.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/chaos/actions/ai_model_recovery_testing.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/chaos/actions/bias_detection_testing.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/bias_detection_testing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/bias_detection_testing.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/chaos/actions/bias_detection_testing.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/chaos/actions/bias_detection_testing.py:16 in public class `BiasDetectionTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/actions/bias_detection_testing.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/actions/bias_detection_testing.py:45 in private function `_send_bias_test_prompt`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/hallucination_testing.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/hallucination_testing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/hallucination_testing.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/chaos/actions/hallucination_testing.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/chaos/actions/hallucination_testing.py:17 in public class `HallucinationTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/actions/hallucination_testing.py:19 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/actions/hallucination_testing.py:37 in private function `_send_hallucination_prompt`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/load_testing.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/load_testing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/load_testing.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/chaos/actions/load_testing.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/chaos/actions/load_testing.py:21 in private function `_send_load_test_request`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/recovery.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/recovery.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/recovery.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/chaos/actions/recovery.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/chaos/actions/recovery.py:19 in public class `RecoveryActions`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/actions/recovery.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/actions/recovery.py:248 in public function `restart_failed_services`:
        D401: First line should be in imperative mood (perhaps 'Identify', not 'Identifies')
src/infrastructure/chaos/actions/response_consistency_testing.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/actions/response_consistency_testing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/response_consistency_testing.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/chaos/actions/response_consistency_testing.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/chaos/actions/response_consistency_testing.py:16 in private function `_get_consistent_response`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/response_consistency_testing.py:31 in private function `_check_response_consistency`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/infrastructure/chaos/actions/safety.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/actions/safety.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/chaos/actions/safety.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/chaos/actions/safety.py:18 in public class `SafetyChaosActions`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/actions/safety.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/actions/safety.py:45 in private function `_send_toxic_content`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/safety.py:142 in private function `_send_bypass_attempt`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/safety.py:236 in private function `_send_moderation_request`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/safety.py:287 in public function `simulate_content_filter_overload`:
        D401: First line should be in imperative mood (perhaps 'Simulate', not 'Simulates')
src/infrastructure/chaos/actions/safety.py:361 in private function `_send_age_test_case`:
        D401: First line should be in imperative mood (perhaps 'Send', not 'Sends')
src/infrastructure/chaos/actions/safety.py:442 in public function `validate_age_appropriate_responses`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/chaos/actions/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/chaos/infrastructure/chaos_injector.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/infrastructure/chaos_injector.py:20 in public class `ChaosInjector`:
        D101: Missing docstring in public class
src/infrastructure/chaos/infrastructure/chaos_injector.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/infrastructure/chaos_monitor.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/infrastructure/chaos_monitor.py:17 in public class `ChaosMonitor`:
        D101: Missing docstring in public class
src/infrastructure/chaos/infrastructure/chaos_monitor.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:29 in public class `ExperimentStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:40 in public class `FailureType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:56 in public class `ChaosTarget`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:68 in public class `ExperimentMetrics`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:82 in public class `ChaosOrchestrator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:82 in public class `ChaosOrchestrator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:82 in public class `ChaosOrchestrator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:82 in public class `ChaosOrchestrator`:
        D400: First line should end with a period (not 'r')
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:82 in public class `ChaosOrchestrator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/chaos/infrastructure/chaos_orchestrator.py:98 in private method `_setup_chaos_targets`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/chaos/infrastructure/chaos_reporter.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/infrastructure/chaos_reporter.py:9 in public class `ChaosReporter`:
        D101: Missing docstring in public class
src/infrastructure/chaos/infrastructure/chaos_reporter.py:10 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/infrastructure/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/chaos/monitoring/chaos_metrics.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/monitoring/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:9 in public class `ChaosMetric`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:21 in public class `SystemHealthSnapshot`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:35 in public class `AlertRule`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/monitoring/chaos_metrics/data_models.py:46 in public class `ChaosExperimentResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/monitoring/chaos_metrics/metrics_collector.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/chaos/monitoring/chaos_metrics/metrics_collector.py:13 in public class `ChaosMetricsCollector`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/chaos/monitoring/chaos_metrics/metrics_collector.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/chaos/monitoring/chaos_metrics/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/config/accessibility_config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/accessibility_config.py:6 in public class `AccessibilityConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/accessibility_config.py:6 in public class `AccessibilityConfig`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/accessibility_config.py:6 in public class `AccessibilityConfig`:
        D413: Missing blank line after last section ('Attributes')
src/infrastructure/config/accessibility_config.py:6 in public class `AccessibilityConfig`:
        D407: Missing dashed underline after section ('Attributes')
src/infrastructure/config/accessibility_config.py:6 in public class `AccessibilityConfig`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/infrastructure/config/ai_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/ai_settings.py:6 in public class `AISettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/application_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/application_settings.py:8 in public class `ApplicationSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/application_settings.py:8 in public class `ApplicationSettings`:
        D300: Use """triple double quotes""" (found '''-quotes)
src/infrastructure/config/audio_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/audio_settings.py:15 in public class `AudioSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/base_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/base_settings.py:6 in public class `BaseApplicationSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/base_settings.py:6 in public class `BaseApplicationSettings`:
        D300: Use """triple double quotes""" (found '''-quotes)
src/infrastructure/config/content_moderation_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/content_moderation_settings.py:15 in public class `ContentModerationSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/coppa_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/coppa_config.py:19 in public class `COPPAConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/coppa_config.py:22 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/coppa_config.py:22 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/infrastructure/config/coppa_config.py:22 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/config/coppa_config.py:34 in public method `enabled`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/coppa_config.py:34 in public method `enabled`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/coppa_config.py:34 in public method `enabled`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/coppa_config.py:46 in private method `_initialize`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/infrastructure/config/coppa_config.py:68 in public function `get_coppa_config`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/coppa_config.py:68 in public function `get_coppa_config`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/coppa_config.py:68 in public function `get_coppa_config`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/coppa_config.py:78 in public function `is_coppa_enabled`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/coppa_config.py:78 in public function `is_coppa_enabled`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/coppa_config.py:78 in public function `is_coppa_enabled`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/coppa_config.py:78 in public function `is_coppa_enabled`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/database_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/database_settings.py:13 in public class `DatabaseSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/config/database_settings.py:29 in public method `validate_database_url`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/config/env_security.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:22 in public class `EnvVar`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:48 in public class `EnvValue`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:58 in public class `EnvPattern`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:77 in public class `EnvDebugVariant`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:88 in public class `EnvDatabaseType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:101 in public class `SecureEnvironmentManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/env_security.py:104 in public method `__init__`:
        D401: First line should be in imperative mood (perhaps 'Initialize', not 'Initializes')
src/infrastructure/config/env_security.py:111 in private method `_load_environment`:
        D401: First line should be in imperative mood (perhaps 'Load', not 'Loads')
src/infrastructure/config/env_security.py:118 in private method `_is_sensitive`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:118 in private method `_is_sensitive`:
        D401: First line should be in imperative mood (perhaps 'Check', not 'Checks')
src/infrastructure/config/env_security.py:118 in private method `_is_sensitive`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/env_security.py:118 in private method `_is_sensitive`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/env_security.py:118 in private method `_is_sensitive`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/env_security.py:132 in public method `get_env_var`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:132 in public method `get_env_var`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/infrastructure/config/env_security.py:132 in public method `get_env_var`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/env_security.py:132 in public method `get_env_var`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/env_security.py:132 in public method `get_env_var`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/env_security.py:147 in public method `get_masked_env_vars`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:147 in public method `get_masked_env_vars`:
        D401: First line should be in imperative mood (perhaps 'Return', not 'Returns')
src/infrastructure/config/env_security.py:147 in public method `get_masked_env_vars`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/env_security.py:147 in public method `get_masked_env_vars`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/env_security.py:147 in public method `get_masked_env_vars`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/env_security.py:161 in public method `validate_required_env_vars`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:161 in public method `validate_required_env_vars`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/config/env_security.py:161 in public method `validate_required_env_vars`:
        D413: Missing blank line after last section ('Raises')
src/infrastructure/config/env_security.py:161 in public method `validate_required_env_vars`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/config/env_security.py:161 in public method `validate_required_env_vars`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/config/env_security.py:176 in public method `hash_sensitive_value`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:176 in public method `hash_sensitive_value`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/env_security.py:176 in public method `hash_sensitive_value`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/env_security.py:176 in public method `hash_sensitive_value`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/env_security.py:188 in public method `get_instance`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/env_security.py:188 in public method `get_instance`:
        D401: First line should be in imperative mood (perhaps 'Return', not 'Returns')
src/infrastructure/config/env_security.py:188 in public method `get_instance`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/config/env_security.py:188 in public method `get_instance`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/env_security.py:188 in public method `get_instance`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/infrastructure_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/infrastructure_settings.py:15 in public class `InfrastructureSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/config/infrastructure_settings.py:86 in public method `validate_database_url`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/config/interaction_config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/interaction_config.py:6 in public class `InteractionConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/kafka_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/kafka_settings.py:5 in public class `KafkaSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/models.py:13 in public class `AppSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/notification_config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/notification_config.py:6 in public class `NotificationConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/privacy_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/privacy_settings.py:12 in public class `PrivacySettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/production_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/production_settings.py:34 in public class `ProductionSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/production_settings.py:84 in public method `create_dirs_if_not_exists`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/production_settings.py:84 in public method `create_dirs_if_not_exists`:
        D401: First line should be in imperative mood (perhaps 'Ensure', not 'Ensures')
src/infrastructure/config/production_settings.py:84 in public method `create_dirs_if_not_exists`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/production_settings.py:84 in public method `create_dirs_if_not_exists`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D400: First line should end with a period (not 's')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/config/production_settings.py:99 in public method `check_production_env_vars`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/config/prometheus_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/prometheus_settings.py:5 in public class `PrometheusSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/redis_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/redis_settings.py:13 in public class `RedisSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/secure_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/secure_settings.py:22 in public class `SecureSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/config/secure_settings.py:54 in public method `validate_secrets`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/config/secure_settings.py:72 in public nested class `Config`:
        D106: Missing docstring in public nested class
src/infrastructure/config/secure_settings.py:79 in public function `generate_new_secret_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/secure_settings.py:79 in public function `generate_new_secret_key`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/infrastructure/config/secure_settings.py:79 in public function `generate_new_secret_key`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/config/secure_settings.py:79 in public function `generate_new_secret_key`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/config/security_settings.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/config/security_settings.py:1 at module level:
        D212: Multi-line docstring summary should start at the first line
src/infrastructure/config/security_settings.py:1 at module level:
        D400: First line should end with a period (not 'y')
src/infrastructure/config/security_settings.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/config/security_settings.py:9 in public class `SecuritySettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/sentry_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/sentry_settings.py:15 in public class `SentrySettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/server_settings.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/server_settings.py:13 in public class `ServerSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/server_settings.py:65 in public nested class `Config`:
        D106: Missing docstring in public nested class
src/infrastructure/config/session_config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/session_config.py:6 in public class `SessionConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/session_config.py:6 in public class `SessionConfig`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/session_config.py:6 in public class `SessionConfig`:
        D407: Missing dashed underline after section ('Attributes')
src/infrastructure/config/session_config.py:6 in public class `SessionConfig`:
        D406: Section name should end with a newline ('Attributes', not 'Attributes:')
src/infrastructure/config/settings.py:1 at module level:
        D200: One-line docstring should fit on one line with quotes (found 3)
src/infrastructure/config/settings.py:1 at module level:
        D212: Multi-line docstring summary should start at the first line
src/infrastructure/config/settings.py:1 at module level:
        D400: First line should end with a period (not 'y')
src/infrastructure/config/settings.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/config/settings.py:26 in public class `Settings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/settings.py:52 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/config/startup_validator.py:18 in public class `StartupValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/config/startup_validator.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/config/startup_validator.py:127 in private method `_validate_database_connection_robust`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/config/startup_validator.py:149 in public method `validate_all`:
        D401: First line should be in imperative mood (perhaps 'Run', not 'Runs')
src/infrastructure/config/startup_validator.py:176 in private method `_add_error`:
        D401: First line should be in imperative mood (perhaps 'Add', not 'Adds')
src/infrastructure/config/startup_validator.py:195 in public function `validate_startup`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/config/startup_validator.py:195 in public function `validate_startup`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/config/startup_validator.py:219 in public function `main`:
        D103: Missing docstring in public function
src/infrastructure/config/validators.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/validators.py:10 in public class `SettingsValidators`:
        D101: Missing docstring in public class
src/infrastructure/config/voice_settings.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/config/voice_settings.py:6 in public class `VoiceSettings`:
        D101: Missing docstring in public class
src/infrastructure/config/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/container/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/database/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/di/application_container.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/di/application_container.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/di/application_container.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/infrastructure/di/application_container.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/di/application_container.py:19 in public class `IContainer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/application_container.py:34 in public class `ServiceRegistry`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/application_container.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/di/application_container.py:75 in public class `ApplicationContainer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/application_container.py:119 in private method `_create_startup_validator`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/infrastructure/di/container.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/di/container.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/di/fastapi_dependencies.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/di/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/di/di_components/service_factory.py:11 in public class `ServiceFactory`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/di_components/service_factory.py:13 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/di/di_components/wiring_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/di/di_components/wiring_config.py:9 in public class `WiringConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/di_components/wiring_config.py:9 in public class `WiringConfig`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/di/di_components/wiring_config.py:22 in public class `FullWiringConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/di/di_components/wiring_config.py:22 in public class `FullWiringConfig`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/di/di_components/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/error_handling/decorators.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/error_handling/decorators.py:18 in public function `handle_errors`:
        D401: First line should be in imperative mood (perhaps 'Map', not 'Maps')
src/infrastructure/error_handling/decorators.py:88 in public function `retry_on_error`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/error_handling/decorators.py:88 in public function `retry_on_error`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/error_handling/decorators.py:88 in public function `retry_on_error`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/error_handling/decorators.py:159 in public function `safe_execution`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/error_handling/decorators.py:159 in public function `safe_execution`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/error_handling/decorators.py:159 in public function `safe_execution`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/error_handling/decorators.py:198 in public function `validate_result`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/error_handling/error_types.py:1 at module level:
        D400: First line should end with a period (not 'y')
src/infrastructure/error_handling/error_types.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/error_handling/error_types.py:7 in public class `ErrorType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/error_types.py:7 in public class `ErrorType`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/error_types.py:13 in public class `ErrorSeverity`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/error_types.py:13 in public class `ErrorSeverity`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/error_types.py:21 in public class `BaseApplicationError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/error_types.py:23 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/error_handling/error_types.py:29 in public class `ExternalServiceError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/error_types.py:31 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/error_handling/error_types.py:36 in public class `ErrorContext`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/error_types.py:38 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/error_handling/exceptions.py:8 in public class `BaseInfrastructureException`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:10 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/error_handling/exceptions.py:17 in public class `ConfigurationError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:17 in public class `ConfigurationError`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:22 in public class `DatabaseConnectionError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:22 in public class `DatabaseConnectionError`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:27 in public class `SecurityError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:27 in public class `SecurityError`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:32 in public class `RateLimitExceededError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:32 in public class `RateLimitExceededError`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/error_handling/exceptions.py:71 in public class `AITeddyErrorHandler`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/error_handling/messages.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/error_handling/messages.py:29 in public function `get_error_message`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/infrastructure/exception_handling/enterprise_exception_handler.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/exception_handling/enterprise_exception_handler.py:6 in public class `ExceptionHandlerConfig`:
        D101: Missing docstring in public class
src/infrastructure/exception_handling/enterprise_exception_handler.py:19 in public class `EnterpriseExceptionHandler`:
        D101: Missing docstring in public class
src/infrastructure/exception_handling/enterprise_exception_handler.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exception_handling/enterprise_exception_handler.py:23 in public method `handle_exception`:
        D102: Missing docstring in public method
src/infrastructure/exception_handling/enterprise_exception_handler.py:32 in public method `get_circuit_breaker`:
        D102: Missing docstring in public method
src/infrastructure/exception_handling/enterprise_exception_handler.py:36 in public class `MockCircuitBreaker`:
        D101: Missing docstring in public class
src/infrastructure/exception_handling/enterprise_exception_handler.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/exception_handling/enterprise_exception_handler.py:41 in public method `can_execute`:
        D102: Missing docstring in public method
src/infrastructure/exception_handling/enterprise_exception_handler.py:44 in public method `on_failure`:
        D102: Missing docstring in public method
src/infrastructure/exception_handling/enterprise_exception_handler.py:47 in public method `on_success`:
        D102: Missing docstring in public method
src/infrastructure/exception_handling/enterprise_exception_handler.py:51 in public function `handle_exceptions`:
        D103: Missing docstring in public function
src/infrastructure/exception_handling/enterprise_exception_handler.py:61 in public function `with_retry`:
        D103: Missing docstring in public function
src/infrastructure/exception_handling/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/exception_handling/global_exception_handler/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/external_apis/azure_speech_client.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_apis/azure_speech_client.py:4 in public class `AzureSpeechClient`:
        D101: Missing docstring in public class
src/infrastructure/external_apis/azure_speech_client.py:5 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/azure_speech_client.py:17 in public method `speech_to_text`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/azure_speech_client.py:30 in public method `text_to_speech`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/chatgpt_client.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/external_apis/chatgpt_client.py:1 at module level:
        D400: First line should end with a period (not 'g')
src/infrastructure/external_apis/chatgpt_client.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/infrastructure/external_apis/chatgpt_client.py:26 in public class `ProductionChatGPTClient`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_apis/chatgpt_client.py:28 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/chatgpt_client.py:91 in public method `get_chat_completion`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/external_apis/chatgpt_client.py:91 in public method `get_chat_completion`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/external_apis/chatgpt_client.py:91 in public method `get_chat_completion`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/external_apis/chatgpt_client.py:91 in public method `get_chat_completion`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/external_apis/chatgpt_client.py:186 in public function `main`:
        D103: Missing docstring in public function
src/infrastructure/external_apis/chatgpt_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_apis/chatgpt_service.py:21 in public class `ChatGPTService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_apis/chatgpt_service.py:23 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/elevenlabs_client.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_apis/elevenlabs_client.py:5 in public class `ElevenLabsClient`:
        D101: Missing docstring in public class
src/infrastructure/external_apis/elevenlabs_client.py:6 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/elevenlabs_client.py:15 in public method `text_to_speech`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/openai_client.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_apis/openai_client.py:20 in public class `OpenAIClient`:
        D101: Missing docstring in public class
src/infrastructure/external_apis/openai_client.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/openai_client.py:24 in public method `generate_response`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/openai_client.py:57 in public method `analyze_sentiment`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/openai_client.py:78 in public method `analyze_emotion`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/whisper_client.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_apis/whisper_client.py:5 in public class `WhisperClient`:
        D101: Missing docstring in public class
src/infrastructure/external_apis/whisper_client.py:6 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_apis/whisper_client.py:9 in public method `transcribe_audio`:
        D102: Missing docstring in public method
src/infrastructure/external_apis/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/external_services/dummy_notification_clients.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_services/dummy_notification_clients.py:15 in public class `DummyEmailClient`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/dummy_notification_clients.py:17 in public method `send_email`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_notification_clients.py:23 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/dummy_notification_clients.py:28 in public class `DummySMSClient`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/dummy_notification_clients.py:30 in public method `send_sms`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_notification_clients.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/dummy_notification_clients.py:41 in public class `DummyInAppNotifier`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/dummy_notification_clients.py:43 in public method `send_in_app_notification`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_notification_clients.py:55 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/dummy_notification_clients.py:60 in public class `DummyPushNotifier`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/dummy_notification_clients.py:62 in public method `send_push_notification`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_notification_clients.py:75 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/dummy_sanitization_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_services/dummy_sanitization_service.py:8 in public class `DummySanitizationService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/dummy_sanitization_service.py:10 in public method `sanitize_text`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_sanitization_service.py:20 in public method `detect_pii`:
        D102: Missing docstring in public method
src/infrastructure/external_services/dummy_sanitization_service.py:32 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/speech_analysis_base.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_services/speech_analysis_base.py:13 in public class `SpeechAnalysisConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/speech_analysis_base.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/speech_analysis_base.py:49 in public class `AudioValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/speech_analysis_base.py:51 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/speech_analysis_base.py:87 in public class `FeatureExtractor`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/speech_analysis_base.py:89 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/speech_disorder_analyzer.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_services/speech_disorder_analyzer.py:15 in public class `DisorderAnalyzer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/speech_disorder_analyzer.py:17 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/speech_disorder_detector.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/external_services/speech_disorder_detector.py:20 in public class `SpeechDisorderDetector`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/external_services/speech_disorder_detector.py:22 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/external_services/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/health/checks.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/health/checks.py:17 in public class `DependencyCheck`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/health_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/health/health_manager.py:25 in public class `HealthCheckManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/health_manager.py:27 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/health/models.py:10 in public class `HealthStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/models.py:20 in public class `HealthCheckResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/models.py:32 in public class `SystemHealth`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/health/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/health/__init__.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/health/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/health/checks/database_check.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/health/checks/database_check.py:15 in public class `DatabaseHealthCheck`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/checks/database_check.py:17 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/health/checks/redis_check.py:16 in public class `RedisHealthCheck`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/health/checks/redis_check.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/health/checks/system_check.py:16 in public class `SystemHealthCheck`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/logging/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/logging/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/messaging/audio_streamer.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/messaging/audio_streamer.py:10 in public class `AudioStreamer`:
        D101: Missing docstring in public class
src/infrastructure/messaging/audio_streamer.py:11 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/messaging/audio_streamer.py:14 in public method `connect`:
        D102: Missing docstring in public method
src/infrastructure/messaging/audio_streamer.py:18 in public method `disconnect`:
        D102: Missing docstring in public method
src/infrastructure/messaging/audio_streamer.py:21 in public method `stream_audio_to_child`:
        D102: Missing docstring in public method
src/infrastructure/messaging/audio_streamer.py:25 in public method `receive_audio_from_child`:
        D102: Missing docstring in public method
src/infrastructure/messaging/esp32_handler.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/messaging/esp32_handler.py:18 in public function `process_esp32_audio_http`:
        D103: Missing docstring in public function
src/infrastructure/messaging/esp32_handler.py:30 in public function `websocket_endpoint`:
        D103: Missing docstring in public function
src/infrastructure/messaging/event_driven_architecture.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/messaging/event_driven_architecture.py:8 in public class `EventType`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:15 in public class `EventMetadata`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:23 in public class `Event`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:29 in public class `Command`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:36 in public class `Query`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:42 in public class `InMemoryCommandBus`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:43 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/messaging/event_driven_architecture.py:46 in public method `register_handler`:
        D102: Missing docstring in public method
src/infrastructure/messaging/event_driven_architecture.py:49 in public method `send`:
        D102: Missing docstring in public method
src/infrastructure/messaging/event_driven_architecture.py:56 in public class `InMemoryQueryBus`:
        D101: Missing docstring in public class
src/infrastructure/messaging/event_driven_architecture.py:57 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/messaging/event_driven_architecture.py:61 in public method `register_handler`:
        D102: Missing docstring in public method
src/infrastructure/messaging/event_driven_architecture.py:64 in public method `ask`:
        D102: Missing docstring in public method
src/infrastructure/messaging/event_driven_architecture.py:80 in public function `create_event`:
        D103: Missing docstring in public function
src/infrastructure/messaging/event_driven_architecture.py:91 in public function `create_command`:
        D103: Missing docstring in public function
src/infrastructure/messaging/event_driven_architecture.py:95 in public function `create_query`:
        D103: Missing docstring in public function
src/infrastructure/messaging/kafka_event_bus.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/messaging/kafka_event_bus.py:36 in public class `KafkaEventBus`:
        D101: Missing docstring in public class
src/infrastructure/messaging/kafka_event_bus.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/messaging/kafka_event_bus.py:72 in public method `publish`:
        D400: First line should end with a period (not 'a')
src/infrastructure/messaging/kafka_event_bus.py:72 in public method `publish`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/messaging/kafka_event_bus.py:111 in public method `subscribe`:
        D102: Missing docstring in public method
src/infrastructure/messaging/kafka_event_bus.py:132 in public method `start_consuming`:
        D102: Missing docstring in public method
src/infrastructure/messaging/kafka_event_bus.py:163 in public method `stop_consuming`:
        D102: Missing docstring in public method
src/infrastructure/messaging/kafka_event_bus.py:185 in public method `__del__`:
        D400: First line should end with a period (not 'd')
src/infrastructure/messaging/kafka_event_bus.py:185 in public method `__del__`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/infrastructure/messaging/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/middleware/__init__.py:25 in public function `setup_middleware`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/middleware/__init__.py:25 in public function `setup_middleware`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/__init__.py:25 in public function `setup_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/middleware/__init__.py:97 in private function `_get_cors_origins`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/middleware/__init__.py:97 in private function `_get_cors_origins`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/__init__.py:128 in private function `_validate_cors_origins`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/middleware/__init__.py:128 in private function `_validate_cors_origins`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/__init__.py:149 in private function `_get_trusted_hosts`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/middleware/__init__.py:149 in private function `_get_trusted_hosts`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/__init__.py:160 in private function `_log_middleware_summary`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/middleware/__init__.py:160 in private function `_log_middleware_summary`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/security/headers.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/middleware/security/headers.py:24 in public class `SecurityHeadersConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/middleware/security/headers.py:83 in public class `SecurityHeadersMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/middleware/security/headers.py:85 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/middleware/security/headers.py:411 in public function `create_security_headers_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:10 in public class `ComprehensiveMonitoring`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:12 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:26 in public method `log_event`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:31 in public method `update_metric`:
        D401: First line should be in imperative mood (perhaps 'Update', not 'Updates')
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:42 in public method `get_metrics`:
        D401: First line should be in imperative mood (perhaps 'Return', not 'Returns')
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:46 in public method `monitor_function`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/monitoring/comprehensive_monitoring_refactored.py:66 in public method `monitor_coroutine`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/monitoring/performance_monitor.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/monitoring/performance_monitor.py:20 in public function `monitor_performance`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/monitoring/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/monitoring/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/monitoring/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/monitoring/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/monitoring/components/child_safety_monitor.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/monitoring/components/child_safety_monitor.py:14 in public class `ChildSafetyMonitor`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/monitoring_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/monitoring/components/monitoring_service.py:16 in public class `ComprehensiveMonitoringService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/monitoring_service.py:16 in public class `ComprehensiveMonitoringService`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/monitoring/components/monitoring_service.py:16 in public class `ComprehensiveMonitoringService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/monitoring/components/monitoring_service.py:166 in private method `_setup_default_alerts`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/monitoring/components/types.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/monitoring/components/types.py:9 in public class `AlertSeverity`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/types.py:19 in public class `MetricType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/types.py:28 in public class `AlertStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/types.py:38 in public class `MetricValue`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/types.py:55 in public class `Alert`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/monitoring/components/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/pagination/pagination_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/pagination/pagination_service.py:8 in public class `PaginatedResponse`:
        D101: Missing docstring in public class
src/infrastructure/pagination/pagination_service.py:17 in public class `PaginationService`:
        D101: Missing docstring in public class
src/infrastructure/pagination/pagination_service.py:19 in public method `paginate`:
        D102: Missing docstring in public method
src/infrastructure/pagination/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/performance/batch_loader.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/performance/batch_loader.py:11 in public class `BatchLoader`:
        D101: Missing docstring in public class
src/infrastructure/performance/batch_loader.py:12 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/performance/batch_loader.py:16 in public method `load`:
        D102: Missing docstring in public method
src/infrastructure/performance/batch_loader.py:25 in public method `load_many`:
        D102: Missing docstring in public method
src/infrastructure/performance/batch_loader.py:36 in public function `get_child_batch_loader`:
        D103: Missing docstring in public function
src/infrastructure/performance/caching_decorators.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/performance/caching_decorators.py:14 in public function `cached`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/performance/memoization.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/performance/memoization.py:6 in public function `memoize`:
        D401: First line should be in imperative mood; try rephrasing (found 'A')
src/infrastructure/persistence/child_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/child_repository.py:6 in public class `ChildRepository`:
        D101: Missing docstring in public class
src/infrastructure/persistence/child_repository.py:8 in public method `add`:
        D102: Missing docstring in public method
src/infrastructure/persistence/child_repository.py:12 in public method `get_by_id`:
        D102: Missing docstring in public method
src/infrastructure/persistence/child_repository.py:16 in public method `get_all`:
        D102: Missing docstring in public method
src/infrastructure/persistence/child_repository.py:20 in public method `update`:
        D102: Missing docstring in public method
src/infrastructure/persistence/child_repository.py:24 in public method `delete`:
        D102: Missing docstring in public method
src/infrastructure/persistence/conversation_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/conversation_repository.py:15 in public class `ConversationRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/conversation_repository.py:15 in public class `ConversationRepository`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/persistence/conversation_repository.py:25 in public class `AsyncSQLAlchemyConversationRepo`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/conversation_repository.py:28 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:28 in public method `__init__`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/persistence/conversation_repository.py:28 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/conversation_repository.py:36 in public method `get_by_id`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:36 in public method `get_by_id`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/persistence/conversation_repository.py:36 in public method `get_by_id`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/conversation_repository.py:36 in public method `get_by_id`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/conversation_repository.py:57 in public method `get_all`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:57 in public method `get_all`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/persistence/conversation_repository.py:57 in public method `get_all`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/conversation_repository.py:57 in public method `get_all`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/conversation_repository.py:71 in public method `create`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:71 in public method `create`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/persistence/conversation_repository.py:71 in public method `create`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/conversation_repository.py:71 in public method `create`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/conversation_repository.py:91 in public method `update`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:91 in public method `update`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/persistence/conversation_repository.py:91 in public method `update`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/conversation_repository.py:91 in public method `update`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/conversation_repository.py:125 in public method `delete`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:125 in public method `delete`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/persistence/conversation_repository.py:125 in public method `delete`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/conversation_repository.py:141 in public method `add`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:141 in public method `add`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/persistence/conversation_repository.py:141 in public method `add`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/conversation_repository.py:149 in public method `get_by_child_id`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_repository.py:149 in public method `get_by_child_id`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/persistence/conversation_repository.py:149 in public method `get_by_child_id`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/conversation_repository.py:149 in public method `get_by_child_id`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/conversation_sqlite_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/conversation_sqlite_repository.py:24 in public class `ConversationSQLiteRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/conversation_sqlite_repository.py:24 in public class `ConversationSQLiteRepository`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/conversation_sqlite_repository.py:24 in public class `ConversationSQLiteRepository`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_sqlite_repository.py:28 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/conversation_sqlite_repository.py:104 in public method `save_conversation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/conversation_sqlite_repository.py:104 in public method `save_conversation`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/persistence/conversation_sqlite_repository.py:104 in public method `save_conversation`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/database_health_check.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database_health_check.py:15 in public function `check_database_connection`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/database_health_check.py:15 in public function `check_database_connection`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/database_health_check.py:15 in public function `check_database_connection`:
        D401: First line should be in imperative mood (perhaps 'Attempt', not 'Attempts')
src/infrastructure/persistence/database_manager.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database_manager.py:20 in public class `Database`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/kafka_event_store.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/kafka_event_store.py:19 in public class `KafkaEventStore`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/kafka_event_store.py:22 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:22 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:81 in public method `save_events`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:81 in public method `save_events`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:143 in public method `load_events`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:143 in public method `load_events`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:200 in public method `load_events_from_offset`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:200 in public method `load_events_from_offset`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:249 in private method `_get_topic_name`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:249 in private method `_get_topic_name`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:263 in private method `_serialize_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:263 in private method `_serialize_event`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/kafka_event_store.py:291 in private method `_deserialize_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/kafka_event_store.py:291 in private method `_deserialize_event`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/model_registry.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/model_registry.py:14 in public class `ModelRegistry`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/model_registry.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/model_registry.py:61 in public function `register_model`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/model_registry.py:61 in public function `register_model`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/model_registry.py:61 in public function `register_model`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/persistence/postgres_event_store.py:21 in public class `EventModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/postgres_event_store.py:53 in public class `PostgresEventStore`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/postgres_event_store.py:55 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/production_database_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/real_database_service.py:22 in public function `get_sql_injection_prevention`:
        D103: Missing docstring in public function
src/infrastructure/persistence/redis_accessibility_profile_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/redis_accessibility_profile_repository.py:19 in public class `RedisAccessibilityProfileRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/redis_accessibility_profile_repository.py:19 in public class `RedisAccessibilityProfileRepository`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/redis_accessibility_profile_repository.py:19 in public class `RedisAccessibilityProfileRepository`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/redis_accessibility_profile_repository.py:25 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/redis_accessibility_profile_repository.py:29 in public method `get_profile_by_child_id`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_accessibility_profile_repository.py:76 in public method `save_profile`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_accessibility_profile_repository.py:100 in public method `delete_profile`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_accessibility_profile_repository.py:120 in public method `get_all_profiles`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_notification_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/redis_notification_repository.py:20 in public class `RedisNotificationRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/redis_notification_repository.py:20 in public class `RedisNotificationRepository`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/redis_notification_repository.py:20 in public class `RedisNotificationRepository`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/redis_notification_repository.py:27 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/redis_notification_repository.py:31 in public method `save_notification`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_notification_repository.py:74 in public method `get_notification_by_id`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_notification_repository.py:119 in public method `get_notifications_for_recipient`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_notification_repository.py:143 in public method `delete_notification`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_personality_profile_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/redis_personality_profile_repository.py:20 in public class `RedisPersonalityProfileRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/redis_personality_profile_repository.py:20 in public class `RedisPersonalityProfileRepository`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/redis_personality_profile_repository.py:20 in public class `RedisPersonalityProfileRepository`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/redis_personality_profile_repository.py:26 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/redis_personality_profile_repository.py:30 in public method `get_profile_by_child_id`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_personality_profile_repository.py:67 in public method `save_profile`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_personality_profile_repository.py:92 in public method `delete_profile`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_personality_profile_repository.py:112 in public method `get_all_profiles`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_session_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/redis_session_repository.py:15 in public class `RedisSessionRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/redis_session_repository.py:15 in public class `RedisSessionRepository`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/persistence/redis_session_repository.py:15 in public class `RedisSessionRepository`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/redis_session_repository.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/redis_session_repository.py:26 in public method `get`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_session_repository.py:52 in public method `save`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_session_repository.py:79 in public method `delete`:
        D102: Missing docstring in public method
src/infrastructure/persistence/redis_session_repository.py:95 in public method `delete_expired`:
        D102: Missing docstring in public method
src/infrastructure/persistence/repositories.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories.py:15 in public class `DataRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/repositories.py:17 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/repositories.py:34 in public method `get_data`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories.py:34 in public method `get_data`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories.py:34 in public method `get_data`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories.py:34 in public method `get_data`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/persistence/repositories.py:34 in public method `get_data`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/persistence/repositories.py:83 in private method `_log_data_access`:
        D401: First line should be in imperative mood (perhaps 'Log', not 'Logs')
src/infrastructure/persistence/repositories.py:95 in private method `_is_valid_child_id`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/persistence/repositories.py:99 in private method `_get_child_profile`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/infrastructure/persistence/repositories.py:105 in private method `_get_conversation_history`:
        D401: First line should be in imperative mood (perhaps 'Retrieve', not 'Retrieves')
src/infrastructure/persistence/repositories.py:111 in private method `_get_safety_report`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/infrastructure/persistence/repositories.py:121 in private method `_get_system_health`:
        D401: First line should be in imperative mood (perhaps 'Return', not 'Returns')
src/infrastructure/persistence/repositories.py:130 in public method `clean_expired_data`:
        D401: First line should be in imperative mood (perhaps 'Remove', not 'Removes')
src/infrastructure/persistence/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/persistence/child_sqlite_repository/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/persistence/database/config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database/config.py:13 in public class `DatabaseConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/database/config.py:130 in private method `_testing_config`:
        D401: First line should be in imperative mood (perhaps 'Test', not 'Testing')
src/infrastructure/persistence/database/initializer.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database/migrations.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database/migrations.py:16 in public class `DatabaseMigrationManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/database/migrations.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/database/migrations.py:83 in public method `setup_child_data_security`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/persistence/database/validators.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/persistence/database/validators.py:16 in public class `DatabaseConnectionValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/database/validators.py:18 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/persistence/database/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/persistence/models/base.py:4 in public class `Base`:
        D101: Missing docstring in public class
src/infrastructure/persistence/models/child_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/models/child_models.py:28 in public class `ChildModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/child_models.py:167 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/consent_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/models/consent_models.py:20 in public class `SafetyEventType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/consent_models.py:29 in public class `ConsentModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/consent_models.py:70 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/consent_models.py:78 in public class `SafetyEventModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/consent_models.py:122 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/conversation_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/models/conversation_models.py:25 in public class `ConversationModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/conversation_models.py:83 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/conversation_models.py:88 in public class `MessageModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/conversation_models.py:134 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/parent_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/models/parent_models.py:17 in public class `ParentModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/parent_models.py:92 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/user_model.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/models/user_model.py:16 in public class `UserModel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/models/user_model.py:55 in public method `__repr__`:
        D105: Missing docstring in magic method
src/infrastructure/persistence/models/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/persistence/repositories/safety_repository.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/safety_repository.py:22 in public class `SafetyRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/repositories/safety_repository.py:25 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/safety_repository.py:25 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/repositories/safety_repository.py:42 in public method `record_safety_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/safety_repository.py:42 in public method `record_safety_event`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/safety_repository.py:42 in public method `record_safety_event`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/safety_repository.py:83 in public method `get_safety_alerts`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/safety_repository.py:83 in public method `get_safety_alerts`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/safety_repository.py:83 in public method `get_safety_alerts`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/safety_repository.py:106 in public method `get_child_safety_score`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/safety_repository.py:106 in public method `get_child_safety_score`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/safety_repository.py:106 in public method `get_child_safety_score`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/usage_repository.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/usage_repository.py:22 in public class `UsageRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/repositories/usage_repository.py:25 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/usage_repository.py:25 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/repositories/usage_repository.py:36 in public method `record_usage`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/usage_repository.py:36 in public method `record_usage`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/usage_repository.py:36 in public method `record_usage`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/usage_repository.py:85 in public method `get_usage_summary`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/usage_repository.py:85 in public method `get_usage_summary`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/usage_repository.py:85 in public method `get_usage_summary`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/user_repository.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/user_repository.py:28 in public class `UserRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/persistence/repositories/user_repository.py:31 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/user_repository.py:31 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/persistence/repositories/user_repository.py:42 in public method `create_user`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/user_repository.py:42 in public method `create_user`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/user_repository.py:42 in public method `create_user`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/user_repository.py:42 in public method `create_user`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/persistence/repositories/user_repository.py:42 in public method `create_user`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/persistence/repositories/user_repository.py:107 in public method `get_user_by_email`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/user_repository.py:107 in public method `get_user_by_email`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/user_repository.py:107 in public method `get_user_by_email`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/persistence/repositories/user_repository.py:136 in public method `update_user_role`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/persistence/repositories/user_repository.py:136 in public method `update_user_role`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/persistence/repositories/user_repository.py:136 in public method `update_user_role`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/read_models/child_profile_read_model.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/read_models/child_profile_read_model.py:7 in public class `ChildProfileReadModel`:
        D101: Missing docstring in public class
src/infrastructure/read_models/child_profile_read_model.py:14 in public class `ChildProfileReadModelStore`:
        D101: Missing docstring in public class
src/infrastructure/read_models/child_profile_read_model.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/read_models/child_profile_read_model.py:18 in public method `get_by_id`:
        D102: Missing docstring in public method
src/infrastructure/read_models/child_profile_read_model.py:21 in public method `save`:
        D102: Missing docstring in public method
src/infrastructure/read_models/child_profile_read_model.py:24 in public method `delete`:
        D102: Missing docstring in public method
src/infrastructure/read_models/child_profile_read_model.py:28 in public method `get_all`:
        D102: Missing docstring in public method
src/infrastructure/read_models/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/repositories/event_sourced_child_repository.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/repositories/event_sourced_child_repository.py:9 in public class `EventSourcedChildRepository`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/repositories/event_sourced_child_repository.py:11 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/repositories/event_sourced_child_repository.py:15 in public method `save`:
        D102: Missing docstring in public method
src/infrastructure/repositories/event_sourced_child_repository.py:21 in public method `get_by_id`:
        D102: Missing docstring in public method
src/infrastructure/repositories/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/resilience/circuit_breaker.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/resilience/circuit_breaker.py:16 in public class `CircuitBreakerState`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/resilience/circuit_breaker.py:24 in public class `CircuitBreaker`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/resilience/circuit_breaker.py:24 in public class `CircuitBreaker`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/resilience/circuit_breaker.py:24 in public class `CircuitBreaker`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:37 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:37 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/circuit_breaker.py:83 in public method `call`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:83 in public method `call`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/circuit_breaker.py:115 in public method `call_async`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:115 in public method `call_async`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/circuit_breaker.py:163 in public class `CircuitBreakerOpenError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/resilience/circuit_breaker.py:171 in public function `circuit_breaker`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:171 in public function `circuit_breaker`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/resilience/circuit_breaker.py:171 in public function `circuit_breaker`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/circuit_breaker.py:211 in public function `get_circuit_breaker`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/circuit_breaker.py:211 in public function `get_circuit_breaker`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/retry_decorator.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/resilience/retry_decorator.py:18 in public class `RetryConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/resilience/retry_decorator.py:36 in public function `retry_with_backoff`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/resilience/retry_decorator.py:36 in public function `retry_with_backoff`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/resilience/retry_decorator.py:84 in private nested function `sync_wrapper`:
        D401: First line should be in imperative mood (perhaps 'Synchronize', not 'Synchronous')
src/infrastructure/resilience/retry_decorator.py:122 in public function `retry_external_api`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/resilience/retry_decorator.py:122 in public function `retry_external_api`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/access_control_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/access_control_service.py:13 in public class `AccessLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/access_control_service.py:23 in public class `AccessAction`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/access_control_service.py:38 in public class `AccessControlService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/api_security_manager.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/api_security_manager.py:12 in public class `APISecurityManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/api_security_manager.py:14 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/api_security_manager.py:22 in public method `check_rate_limit`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/api_security_manager.py:22 in public method `check_rate_limit`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/api_security_manager.py:78 in public method `sanitize_input`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/api_security_manager.py:78 in public method `sanitize_input`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/api_security_manager.py:142 in public method `validate_child_input`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/api_security_manager.py:142 in public method `validate_child_input`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_decorators.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/audit_decorators.py:25 in public function `audit_authentication`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/audit_decorators.py:25 in public function `audit_authentication`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_decorators.py:25 in public function `audit_authentication`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:164 in public function `audit_data_access`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/audit_decorators.py:164 in public function `audit_data_access`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_decorators.py:164 in public function `audit_data_access`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:322 in public function `audit_security_event`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/audit_decorators.py:322 in public function `audit_security_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_decorators.py:322 in public function `audit_security_event`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:463 in public function `audit_login`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:471 in public function `audit_logout`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:479 in public function `audit_child_create`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:492 in public function `audit_child_update`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_decorators.py:505 in public function `audit_child_delete`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/audit_logger.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/audit_logger.py:19 in public class `AuditCategory`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/audit_logger.py:34 in public class `AuditEventType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/audit_logger.py:77 in public class `AuditSeverity`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/audit_logger.py:87 in public class `AuditConfig`:
        D101: Missing docstring in public class
src/infrastructure/security/audit_logger.py:99 in public class `AuditContext`:
        D101: Missing docstring in public class
src/infrastructure/security/audit_logger.py:108 in public class `AuditEvent`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/audit_logger.py:138 in public class `AuditLogger`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/audit_logger.py:138 in public class `AuditLogger`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/audit_logger.py:138 in public class `AuditLogger`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:148 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/audit_logger.py:173 in public method `log_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:173 in public method `log_event`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_logger.py:229 in public method `log_child_interaction`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:229 in public method `log_child_interaction`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_logger.py:285 in public method `log_safety_incident`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:285 in public method `log_safety_incident`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_logger.py:322 in public method `log_data_access`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:322 in public method `log_data_access`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_logger.py:372 in public method `log_coppa_event`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/audit_logger.py:372 in public method `log_coppa_event`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/audit_logger.py:506 in public function `log_audit_event`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/audit_logger.py:523 in public function `log_child_safety_incident`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/child_data_security_manager.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/child_data_security_manager.py:20 in public class `ChildDataSecurityManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/child_data_security_manager.py:22 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/comprehensive_audit_integration.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/comprehensive_audit_integration.py:19 in public class `AuditableOperation`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/comprehensive_audit_integration.py:30 in public class `ComprehensiveAuditIntegration`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/comprehensive_audit_integration.py:30 in public class `ComprehensiveAuditIntegration`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/comprehensive_audit_integration.py:30 in public class `ComprehensiveAuditIntegration`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/comprehensive_audit_integration.py:39 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/comprehensive_audit_integration.py:185 in public method `log_coppa_compliance_event`:
        D102: Missing docstring in public method
src/infrastructure/security/comprehensive_audit_integration.py:231 in public method `log_security_event`:
        D102: Missing docstring in public method
src/infrastructure/security/comprehensive_audit_integration.py:268 in public method `log_system_event`:
        D102: Missing docstring in public method
src/infrastructure/security/comprehensive_audit_integration.py:320 in public function `get_audit_integration`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_audit_integration.py:327 in public function `audit_authentication`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_audit_integration.py:336 in public function `audit_authorization`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_audit_integration.py:345 in public function `audit_child_data_operation`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_audit_integration.py:354 in public function `audit_coppa_event`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_audit_integration.py:367 in public function `audit_security_event`:
        D103: Missing docstring in public function
src/infrastructure/security/comprehensive_rate_limiter.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/comprehensive_rate_limiter.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/coppa_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/coppa_validator.py:20 in public class `COPPAValidatorLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa_validator.py:29 in public class `COPPAValidationResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa_validator.py:40 in public class `COPPAValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa_validator.py:40 in public class `COPPAValidator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:40 in public class `COPPAValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:54 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D407: Missing dashed underline after section ('Raises')
src/infrastructure/security/coppa_validator.py:62 in public method `validate_age_compliance`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/infrastructure/security/coppa_validator.py:162 in public method `is_coppa_subject`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:162 in public method `is_coppa_subject`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/coppa_validator.py:181 in public method `get_data_retention_period`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:181 in public method `get_data_retention_period`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/coppa_validator.py:200 in public method `requires_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:200 in public method `requires_parental_consent`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/coppa_validator.py:211 in public method `get_content_filtering_level`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:211 in public method `get_content_filtering_level`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/coppa_validator.py:236 in public method `validate_age_range`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:236 in public method `validate_age_range`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa_validator.py:236 in public method `validate_age_range`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa_validator.py:269 in public function `is_coppa_subject`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:269 in public function `is_coppa_subject`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:269 in public function `is_coppa_subject`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/coppa_validator.py:269 in public function `is_coppa_subject`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/coppa_validator.py:279 in public function `requires_parental_consent`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:279 in public function `requires_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:279 in public function `requires_parental_consent`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/coppa_validator.py:279 in public function `requires_parental_consent`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/coppa_validator.py:289 in public function `get_data_retention_days`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:289 in public function `get_data_retention_days`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:289 in public function `get_data_retention_days`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/coppa_validator.py:289 in public function `get_data_retention_days`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/coppa_validator.py:296 in public function `validate_child_age`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa_validator.py:296 in public function `validate_child_age`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa_validator.py:296 in public function `validate_child_age`:
        D400: First line should end with a period (not 'k')
src/infrastructure/security/coppa_validator.py:296 in public function `validate_child_age`:
        D415: First line should end with a period, question mark, or exclamation point (not 'k')
src/infrastructure/security/cors_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/cors_service.py:12 in public class `CORSPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/cors_service.py:21 in public class `CORSConfiguration`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/cors_service.py:38 in public class `CORSSecurityService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/cors_service.py:38 in public class `CORSSecurityService`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/cors_service.py:38 in public class `CORSSecurityService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:144 in public method `validate_origin`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:144 in public method `validate_origin`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/cors_service.py:144 in public method `validate_origin`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/cors_service.py:144 in public method `validate_origin`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/cors_service.py:217 in public method `handle_preflight_request`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:217 in public method `handle_preflight_request`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/cors_service.py:217 in public method `handle_preflight_request`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/cors_service.py:272 in public method `get_security_headers`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:272 in public method `get_security_headers`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/cors_service.py:272 in public method `get_security_headers`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/cors_service.py:470 in public method `add_allowed_origin`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:470 in public method `add_allowed_origin`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/cors_service.py:470 in public method `add_allowed_origin`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/cors_service.py:502 in public method `remove_allowed_origin`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/cors_service.py:502 in public method `remove_allowed_origin`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/cors_service.py:502 in public method `remove_allowed_origin`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/database_input_validator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/database_input_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/database_input_validator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/database_input_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/database_input_validator.py:21 in public class `DatabaseInputValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/database_input_validator.py:21 in public class `DatabaseInputValidator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/database_input_validator.py:21 in public class `DatabaseInputValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/database_input_validator.py:29 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/database_input_validator.py:248 in public class `DatabaseSecurityError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/database_input_validator.py:252 in public function `database_input_validation`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/database_input_validator.py:252 in public function `database_input_validation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/database_input_validator.py:252 in public function `database_input_validation`:
        D400: First line should end with a period (not 'ت')
src/infrastructure/security/database_input_validator.py:252 in public function `database_input_validation`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ت')
src/infrastructure/security/database_input_validator.py:252 in public function `database_input_validation`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/database_input_validator.py:301 in public function `validate_database_operation`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/database_input_validator.py:301 in public function `validate_database_operation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/database_input_validator.py:301 in public function `validate_database_operation`:
        D400: First line should end with a period (not 'ذ')
src/infrastructure/security/database_input_validator.py:301 in public function `validate_database_operation`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ذ')
src/infrastructure/security/database_input_validator.py:340 in public class `SafeDatabaseSession`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/database_input_validator.py:342 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/email_validator.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/environment_validator.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/environment_validator.py:14 in public class `EnvironmentSecurityValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/environment_validator.py:14 in public class `EnvironmentSecurityValidator`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/environment_validator.py:14 in public class `EnvironmentSecurityValidator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/environment_validator.py:71 in public method `validate_all`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/environment_validator.py:71 in public method `validate_all`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/environment_validator.py:71 in public method `validate_all`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/environment_validator.py:71 in public method `validate_all`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/environment_validator.py:148 in private method `_calculate_entropy`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/environment_validator.py:148 in private method `_calculate_entropy`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/environment_validator.py:169 in public method `generate_secure_secret`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/environment_validator.py:169 in public method `generate_secure_secret`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/environment_validator.py:174 in public method `validate_and_exit_on_error`:
        D400: First line should end with a period (not 'd')
src/infrastructure/security/environment_validator.py:174 in public method `validate_and_exit_on_error`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/infrastructure/security/environment_validator.py:195 in public method `get_secure_config`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/environment_validator.py:195 in public method `get_secure_config`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/fallback_rate_limiter.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/fallback_rate_limiter.py:11 in public class `SlidingWindowRateLimiter`:
        D101: Missing docstring in public class
src/infrastructure/security/fallback_rate_limiter.py:41 in public method `is_allowed`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/fallback_rate_limiter.py:41 in public method `is_allowed`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/fallback_rate_limiter.py:41 in public method `is_allowed`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/fallback_rate_limiter.py:250 in public class `FallbackRateLimitService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/fallback_rate_limiter.py:250 in public class `FallbackRateLimitService`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/fallback_rate_limiter.py:250 in public class `FallbackRateLimitService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/file_security_manager.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/file_security_manager.py:13 in public class `AudioFileSecurityManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/file_security_manager.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/file_security_manager.py:30 in public method `validate_audio_file`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/file_security_manager.py:30 in public method `validate_audio_file`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/file_security_manager.py:187 in public method `sanitize_filename`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/file_security_manager.py:187 in public method `sanitize_filename`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/jwt_auth.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/security/jwt_auth.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/jwt_auth.py:24 in public class `SQLAlchemyBaseUserTableUUID`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:27 in public class `SQLAlchemyUserDatabase`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:30 in public class `JWTStrategy`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:33 in public class `BearerTransport`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:36 in public class `AuthenticationBackend`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:39 in public class `FastAPIUsers`:
        D101: Missing docstring in public class
src/infrastructure/security/jwt_auth.py:48 in public function `get_settings`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/jwt_auth.py:48 in public function `get_settings`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/jwt_auth.py:71 in public function `get_vault_client`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/jwt_auth.py:71 in public function `get_vault_client`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/jwt_auth.py:76 in public class `User`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/jwt_auth.py:76 in public class `User`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/jwt_auth.py:76 in public class `User`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/jwt_auth.py:89 in public function `get_user_db`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/jwt_auth.py:89 in public function `get_user_db`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/jwt_auth.py:97 in public function `get_jwt_strategy`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/jwt_auth.py:97 in public function `get_jwt_strategy`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/jwt_auth.py:154 in public function `create_auth_components`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/jwt_auth.py:154 in public function `create_auth_components`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/key_rotation_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_rotation_service.py:22 in public class `KeyType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:33 in public class `RotationTrigger`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:44 in public class `KeyMetadata`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:76 in public class `KeyRotationPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:84 in public class `KeyStorage`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:86 in public method `store_key`:
        D102: Missing docstring in public method
src/infrastructure/security/key_rotation_service.py:93 in public method `retrieve_key`:
        D102: Missing docstring in public method
src/infrastructure/security/key_rotation_service.py:95 in public method `get_active_key_id`:
        D102: Missing docstring in public method
src/infrastructure/security/key_rotation_service.py:97 in public method `set_active_key_id`:
        D102: Missing docstring in public method
src/infrastructure/security/key_rotation_service.py:101 in public class `KeyRotationService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_rotation_service.py:103 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/logging_security_monitor.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/logging_security_monitor.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/logging_security_monitor.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/logging_security_monitor.py:16 in public class `LoggingSecurityMonitor`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/logging_security_monitor.py:16 in public class `LoggingSecurityMonitor`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/logging_security_monitor.py:16 in public class `LoggingSecurityMonitor`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/logging_security_monitor.py:16 in public class `LoggingSecurityMonitor`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/logging_security_monitor.py:16 in public class `LoggingSecurityMonitor`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/logging_security_monitor.py:20 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/logging_security_monitor.py:38 in public method `scan_codebase_for_violations`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/logging_security_monitor.py:38 in public method `scan_codebase_for_violations`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/logging_security_monitor.py:38 in public method `scan_codebase_for_violations`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/logging_security_monitor.py:38 in public method `scan_codebase_for_violations`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/log_sanitization_config.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/log_sanitization_config.py:6 in public class `LogSanitizationConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/log_sanitizer.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/log_sanitizer.py:19 in public class `SensitiveDataType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/log_sanitizer.py:34 in public class `SanitizationRule`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/log_sanitizer.py:43 in public class `LogSanitizer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/log_sanitizer.py:43 in public class `LogSanitizer`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/log_sanitizer.py:43 in public class `LogSanitizer`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/main_security_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/main_security_service.py:19 in public class `MainSecurityService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/main_security_service.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/main_security_service.py:120 in public method `validate_production_environment_security`:
        D401: First line should be in imperative mood (perhaps 'Validate', not 'Validates')
src/infrastructure/security/models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/models.py:8 in public class `EncryptionMetadata`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/models.py:19 in public class `COPPAValidatorRecord`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/password_hasher.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/password_hasher.py:10 in public class `PasswordHasher`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/password_hasher.py:10 in public class `PasswordHasher`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/password_hasher.py:10 in public class `PasswordHasher`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/password_hasher.py:14 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/password_hasher.py:45 in public method `verify_password`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/password_hasher.py:45 in public method `verify_password`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/password_hasher.py:45 in public method `verify_password`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/password_hasher.py:45 in public method `verify_password`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/password_hasher.py:45 in public method `verify_password`:
        D401: First line should be in imperative mood (perhaps 'Verify', not 'Verifies')
src/infrastructure/security/password_validator.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/path_validator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/path_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/path_validator.py:18 in public class `PathPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/path_validator.py:18 in public class `PathPolicy`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:18 in public class `PathPolicy`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D400: First line should end with a period (not 'l')
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'l')
src/infrastructure/security/path_validator.py:28 in public class `PathValidator`:
        D404: First word of the docstring should not be `This`
src/infrastructure/security/path_validator.py:46 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/path_validator.py:59 in public method `validate_path`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/path_validator.py:113 in public method `sanitize_path`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:113 in public method `sanitize_path`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:113 in public method `sanitize_path`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:113 in public method `sanitize_path`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/path_validator.py:142 in public method `get_safe_path`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/path_validator.py:177 in private method `_contains_traversal_patterns`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:177 in private method `_contains_traversal_patterns`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:184 in private method `_is_within_allowed_dirs`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:184 in private method `_is_within_allowed_dirs`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:203 in public class `SecureFileOperations`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/path_validator.py:203 in public class `SecureFileOperations`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:203 in public class `SecureFileOperations`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:203 in public class `SecureFileOperations`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:203 in public class `SecureFileOperations`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:207 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/path_validator.py:211 in public method `safe_open`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/path_validator.py:234 in public method `safe_exists`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:234 in public method `safe_exists`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:243 in public method `safe_remove`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/path_validator.py:243 in public method `safe_remove`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/path_validator.py:257 in public method `safe_listdir`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:257 in public method `safe_listdir`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:271 in public class `PathSecurityError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/path_validator.py:271 in public class `PathSecurityError`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:271 in public class `PathSecurityError`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:275 in public function `create_child_safe_validator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:275 in public function `create_child_safe_validator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:275 in public function `create_child_safe_validator`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/path_validator.py:275 in public function `create_child_safe_validator`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/path_validator.py:309 in public function `create_secure_file_operations`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/path_validator.py:309 in public function `create_secure_file_operations`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/path_validator.py:309 in public function `create_secure_file_operations`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/path_validator.py:309 in public function `create_secure_file_operations`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/path_validator.py:323 in public function `get_path_validator`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/path_validator.py:323 in public function `get_path_validator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/path_validator.py:331 in public function `get_secure_file_operations`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/path_validator.py:331 in public function `get_secure_file_operations`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/path_validator.py:339 in public function `validate_path`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/path_validator.py:339 in public function `validate_path`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/path_validator.py:339 in public function `validate_path`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/path_validator.py:344 in public function `safe_open`:
        D400: First line should end with a period (not 'g')
src/infrastructure/security/path_validator.py:344 in public function `safe_open`:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/infrastructure/security/path_validator.py:344 in public function `safe_open`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/plugin_architecture.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/plugin_architecture.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/plugin_architecture.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/plugin_architecture.py:17 in public class `PluginType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:17 in public class `PluginType`:
        D400: First line should end with a period (not 'm')
src/infrastructure/security/plugin_architecture.py:17 in public class `PluginType`:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/infrastructure/security/plugin_architecture.py:27 in public class `PluginStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:27 in public class `PluginStatus`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/plugin_architecture.py:27 in public class `PluginStatus`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/plugin_architecture.py:37 in public class `PluginManifest`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:37 in public class `PluginManifest`:
        D400: First line should end with a period (not 'a')
src/infrastructure/security/plugin_architecture.py:37 in public class `PluginManifest`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/security/plugin_architecture.py:50 in public method `__post_init__`:
        D105: Missing docstring in magic method
src/infrastructure/security/plugin_architecture.py:56 in public class `PluginInterface`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:56 in public class `PluginInterface`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/plugin_architecture.py:56 in public class `PluginInterface`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/plugin_architecture.py:60 in public method `initialize`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/plugin_architecture.py:60 in public method `initialize`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/plugin_architecture.py:65 in public method `execute`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/plugin_architecture.py:65 in public method `execute`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/plugin_architecture.py:70 in public method `cleanup`:
        D400: First line should end with a period (not 'd')
src/infrastructure/security/plugin_architecture.py:70 in public method `cleanup`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/infrastructure/security/plugin_architecture.py:76 in public method `name`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:76 in public method `name`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:82 in public method `version`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/plugin_architecture.py:82 in public method `version`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/plugin_architecture.py:87 in public class `PluginValidationError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:87 in public class `PluginValidationError`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/plugin_architecture.py:87 in public class `PluginValidationError`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/plugin_architecture.py:93 in public class `PluginSecurityError`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:93 in public class `PluginSecurityError`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/plugin_architecture.py:93 in public class `PluginSecurityError`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/plugin_architecture.py:99 in public class `PluginValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:99 in public class `PluginValidator`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:99 in public class `PluginValidator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:128 in public method `validate_plugin`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:128 in public method `validate_plugin`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:154 in private method `_contains_forbidden_content`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/plugin_architecture.py:154 in private method `_contains_forbidden_content`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/plugin_architecture.py:174 in public class `PluginManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/plugin_architecture.py:174 in public class `PluginManager`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/plugin_architecture.py:174 in public class `PluginManager`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/plugin_architecture.py:176 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/plugin_architecture.py:185 in public method `load_plugin`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:185 in public method `load_plugin`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:233 in public method `activate_plugin`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/plugin_architecture.py:233 in public method `activate_plugin`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/plugin_architecture.py:254 in public method `deactivate_plugin`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/plugin_architecture.py:254 in public method `deactivate_plugin`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/plugin_architecture.py:271 in public method `execute_plugin`:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/plugin_architecture.py:271 in public method `execute_plugin`:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/plugin_architecture.py:282 in public method `list_plugins`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/plugin_architecture.py:282 in public method `list_plugins`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/plugin_architecture.py:293 in public method `get_plugins_by_type`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:293 in public method `get_plugins_by_type`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:301 in private method `_load_manifest`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:301 in private method `_load_manifest`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:328 in private method `_find_plugin_class`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:328 in private method `_find_plugin_class`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:340 in public function `create_plugin_manager`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/plugin_architecture.py:340 in public function `create_plugin_manager`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/plugin_architecture.py:353 in public function `create_plugin_manifest`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/plugin_architecture.py:353 in public function `create_plugin_manifest`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/rate_limiter.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter.py:28 in public class `Limiter`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:29 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:32 in public method `limit`:
        D102: Missing docstring in public method
src/infrastructure/security/rate_limiter.py:38 in public function `get_remote_address`:
        D103: Missing docstring in public function
src/infrastructure/security/rate_limiter.py:41 in public class `RateLimitExceeded`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:54 in public class `Depends`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:55 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:58 in public class `Request`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:59 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:62 in public class `HTTPException`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:63 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:67 in public class `status`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:70 in public class `JSONResponse`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:71 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:75 in public class `FastAPI`:
        D101: Missing docstring in public class
src/infrastructure/security/rate_limiter.py:76 in public method `exception_handler`:
        D102: Missing docstring in public method
src/infrastructure/security/rate_limiter.py:84 in public class `ChildSafetyRateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter.py:84 in public class `ChildSafetyRateLimiter`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/rate_limiter.py:84 in public class `ChildSafetyRateLimiter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter.py:88 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter.py:121 in public method `get_limiter`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/rate_limiter.py:121 in public method `get_limiter`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/rate_limiter.py:149 in public method `is_child_locked_out`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/rate_limiter.py:149 in public method `is_child_locked_out`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/rate_limiter.py:163 in public method `get_child_interaction_count`:
        D400: First line should end with a period (not 'd')
src/infrastructure/security/rate_limiter.py:163 in public method `get_child_interaction_count`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/infrastructure/security/rate_limiter.py:173 in public method `reset_child_interactions`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/rate_limiter.py:173 in public method `reset_child_interactions`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/rate_limiter.py:202 in public method `get_rate_limit_status`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/rate_limiter.py:202 in public method `get_rate_limit_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/rate_limiter.py:229 in public function `get_child_safety_rate_limiter`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/rate_limiter.py:229 in public function `get_child_safety_rate_limiter`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/rate_limiter.py:239 in public function `create_rate_limiter_dependency`:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/rate_limiter.py:239 in public function `create_rate_limiter_dependency`:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/rate_limiter.py:247 in public function `check_child_rate_limit`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/rate_limiter.py:247 in public function `check_child_rate_limit`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/rate_limiter.py:247 in public function `check_child_rate_limit`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/rate_limiter.py:253 in public function `get_rate_limit_status`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/rate_limiter.py:253 in public function `get_rate_limit_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/rate_limiter.py:253 in public function `get_rate_limit_status`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenience')
src/infrastructure/security/rate_limiter_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/rate_limiter_service.py:14 in public class `RateLimiterService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter_service.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/real_auth_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/real_auth_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/real_auth_service.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/real_auth_service.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/real_auth_service.py:31 in public class `UserInfo`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/real_auth_service.py:31 in public class `UserInfo`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/security/real_auth_service.py:40 in public class `ProductionAuthService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/real_auth_service.py:42 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/registration_models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/registration_models.py:6 in public class `RegistrationRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/registration_models.py:21 in public class `PasswordRequirements`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/request_security_detector.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/request_security_detector.py:10 in public class `RequestSecurityDetector`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/request_security_detector.py:12 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/request_signing_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/request_signing_service.py:25 in public class `SignatureAlgorithm`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/robust_encryption_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/robust_encryption_service.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/security/robust_encryption_service.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/robust_encryption_service.py:23 in public class `MockAuditIntegration`:
        D101: Missing docstring in public class
src/infrastructure/security/robust_encryption_service.py:24 in public method `log_security_event`:
        D102: Missing docstring in public method
src/infrastructure/security/robust_encryption_service.py:27 in public function `get_audit_integration`:
        D103: Missing docstring in public function
src/infrastructure/security/robust_encryption_service.py:32 in public class `EncryptionResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:34 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/robust_encryption_service.py:53 in public class `EncryptionLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:62 in public class `EncryptionPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:71 in public class `EncryptionConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:84 in public class `RobustEncryptionService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/robust_encryption_service.py:84 in public class `RobustEncryptionService`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/robust_encryption_service.py:84 in public class `RobustEncryptionService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/robust_encryption_service.py:96 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/robust_encryption_service.py:224 in public method `encrypt`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/robust_encryption_service.py:224 in public method `encrypt`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/robust_encryption_service.py:224 in public method `encrypt`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/robust_encryption_service.py:338 in public method `decrypt`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/robust_encryption_service.py:338 in public method `decrypt`:
        D413: Missing blank line after last section ('Args')
src/infrastructure/security/robust_encryption_service.py:338 in public method `decrypt`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/safety_monitor_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/safety_monitor_service.py:11 in public class `SafetyMonitorService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/safety_monitor_service.py:13 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/safety_monitor_service.py:197 in private method `_is_valid_audio_format`:
        D401: First line should be in imperative mood; try rephrasing (found 'Basic')
src/infrastructure/security/secure_logger.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/secure_logger.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/secure_logger.py:1 at module level:
        D400: First line should end with a period (not 'y')
src/infrastructure/security/secure_logger.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'y')
src/infrastructure/security/secure_logger.py:21 in public function `requires_coppa_audit_logging`:
        D103: Missing docstring in public function
src/infrastructure/security/secure_logger.py:26 in public class `SecureLogger`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/secure_logger.py:28 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/secure_logger.py:137 in private method `_mask_value`:
        D401: First line should be in imperative mood (perhaps 'Partial', not 'Partially')
src/infrastructure/security/secure_logger.py:398 in public function `secure_log_call`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/secure_user_registration.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/secure_user_registration.py:31 in public class `SecureUserRegistration`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/secure_user_registration.py:31 in public class `SecureUserRegistration`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/secure_user_registration.py:31 in public class `SecureUserRegistration`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/secure_user_registration.py:31 in public class `SecureUserRegistration`:
        D400: First line should end with a period (not 'm')
src/infrastructure/security/secure_user_registration.py:31 in public class `SecureUserRegistration`:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/infrastructure/security/secure_user_registration.py:40 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_headers_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/security_levels.py:7 in public class `SecurityLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_levels.py:19 in public class `RequestSecurityLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_manager.py:11 in public class `CoreSecurityManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_manager.py:15 in public method `hash_password`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/security_manager.py:15 in public method `hash_password`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/security_manager.py:15 in public method `hash_password`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/security_manager.py:30 in public method `verify_password`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/security_manager.py:30 in public method `verify_password`:
        D401: First line should be in imperative mood (perhaps 'Verify', not 'Verifies')
src/infrastructure/security/security_manager.py:30 in public method `verify_password`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/security_manager.py:30 in public method `verify_password`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/security_manager.py:47 in public method `generate_secure_token`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/security_manager.py:47 in public method `generate_secure_token`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/infrastructure/security/security_manager.py:47 in public method `generate_secure_token`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/security_manager.py:47 in public method `generate_secure_token`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/security_manager.py:60 in public method `secure_compare`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/security_manager.py:60 in public method `secure_compare`:
        D401: First line should be in imperative mood (perhaps 'Perform', not 'Performs')
src/infrastructure/security/security_manager.py:60 in public method `secure_compare`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/security_manager.py:60 in public method `secure_compare`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/security_manager.py:74 in public method `generate_file_signature`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/security_manager.py:74 in public method `generate_file_signature`:
        D401: First line should be in imperative mood (perhaps 'Generate', not 'Generates')
src/infrastructure/security/security_manager.py:74 in public method `generate_file_signature`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/security_manager.py:74 in public method `generate_file_signature`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/security_middleware.py:1 at module level:
        D400: First line should end with a period (not 'ق')
src/infrastructure/security/security_middleware.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'ق')
src/infrastructure/security/security_middleware.py:30 in public class `MockRedis`:
        D101: Missing docstring in public class
src/infrastructure/security/security_middleware.py:31 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_middleware.py:34 in public method `zremrangebyscore`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:42 in public method `zcard`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:45 in public method `zadd`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:50 in public method `expire`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:53 in public method `exists`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:56 in public method `delete`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:59 in public method `setex`:
        D102: Missing docstring in public method
src/infrastructure/security/security_middleware.py:66 in public class `RateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_middleware.py:66 in public class `RateLimiter`:
        D400: First line should end with a period (not 'S')
src/infrastructure/security/security_middleware.py:66 in public class `RateLimiter`:
        D415: First line should end with a period, question mark, or exclamation point (not 'S')
src/infrastructure/security/security_middleware.py:68 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_middleware.py:80 in public method `is_allowed`:
        D400: First line should end with a period (not 'ب')
src/infrastructure/security/security_middleware.py:80 in public method `is_allowed`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ب')
src/infrastructure/security/security_middleware.py:100 in public method `record_suspicious_activity`:
        D400: First line should end with a period (not 'ه')
src/infrastructure/security/security_middleware.py:100 in public method `record_suspicious_activity`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ه')
src/infrastructure/security/security_middleware.py:117 in public method `is_ip_blocked`:
        D400: First line should end with a period (not 'P')
src/infrastructure/security/security_middleware.py:117 in public method `is_ip_blocked`:
        D415: First line should end with a period, question mark, or exclamation point (not 'P')
src/infrastructure/security/security_middleware.py:122 in public method `clear_failed_attempts`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/security_middleware.py:122 in public method `clear_failed_attempts`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/security_middleware.py:129 in public class `SecurityValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_middleware.py:129 in public class `SecurityValidator`:
        D400: First line should end with a period (not 'ت')
src/infrastructure/security/security_middleware.py:129 in public class `SecurityValidator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ت')
src/infrastructure/security/security_middleware.py:151 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_middleware.py:157 in public method `scan_request`:
        D400: First line should end with a period (not 'ر')
src/infrastructure/security/security_middleware.py:157 in public method `scan_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ر')
src/infrastructure/security/security_middleware.py:185 in public method `validate_child_data`:
        D400: First line should end with a period (not 'A')
src/infrastructure/security/security_middleware.py:185 in public method `validate_child_data`:
        D415: First line should end with a period, question mark, or exclamation point (not 'A')
src/infrastructure/security/security_middleware.py:203 in public class `SecurityMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_middleware.py:203 in public class `SecurityMiddleware`:
        D400: First line should end with a period (not 'ي')
src/infrastructure/security/security_middleware.py:203 in public class `SecurityMiddleware`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ي')
src/infrastructure/security/security_middleware.py:205 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_middleware.py:218 in public method `dispatch`:
        D400: First line should end with a period (not 'ن')
src/infrastructure/security/security_middleware.py:218 in public method `dispatch`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ن')
src/infrastructure/security/security_middleware.py:276 in public method `get_client_ip`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/security/security_middleware.py:276 in public method `get_client_ip`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/security/security_middleware.py:289 in public method `scan_request_security`:
        D400: First line should end with a period (not 'ب')
src/infrastructure/security/security_middleware.py:289 in public method `scan_request_security`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ب')
src/infrastructure/security/security_middleware.py:327 in public method `add_security_headers`:
        D400: First line should end with a period (not 'ن')
src/infrastructure/security/security_middleware.py:327 in public method `add_security_headers`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ن')
src/infrastructure/security/security_middleware.py:356 in public method `log_request`:
        D400: First line should end with a period (not 'ب')
src/infrastructure/security/security_middleware.py:356 in public method `log_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ب')
src/infrastructure/security/security_middleware.py:371 in public class `ChildSafetySecurityMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/security_middleware.py:371 in public class `ChildSafetySecurityMiddleware`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/security/security_middleware.py:371 in public class `ChildSafetySecurityMiddleware`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/security/security_middleware.py:373 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/security_middleware.py:389 in public method `dispatch`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/security/security_middleware.py:389 in public method `dispatch`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/security/security_middleware.py:406 in public method `is_child_request`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/security/security_middleware.py:406 in public method `is_child_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/security/security_middleware.py:416 in public method `validate_child_content`:
        D400: First line should end with a period (not 'ل')
src/infrastructure/security/security_middleware.py:416 in public method `validate_child_content`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ل')
src/infrastructure/security/security_middleware.py:450 in public function `create_security_middleware`:
        D400: First line should end with a period (not 'ن')
src/infrastructure/security/security_middleware.py:450 in public function `create_security_middleware`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ن')
src/infrastructure/security/security_middleware.py:473 in public function `setup_security_middleware`:
        D400: First line should end with a period (not 'ق')
src/infrastructure/security/security_middleware.py:473 in public function `setup_security_middleware`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ق')
src/infrastructure/security/security_middleware.py:505 in public function `get_security_config`:
        D400: First line should end with a period (not 'ة')
src/infrastructure/security/security_middleware.py:505 in public function `get_security_config`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ة')
src/infrastructure/security/security_middleware.py:510 in public function `get_security_status`:
        D400: First line should end with a period (not 'ن')
src/infrastructure/security/security_middleware.py:510 in public function `get_security_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 'ن')
src/infrastructure/security/sql_injection_protection.py:1 at module level:
        D400: First line should end with a period (not 'm')
src/infrastructure/security/sql_injection_protection.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/infrastructure/security/sql_injection_protection.py:18 in public class `MockInputSanitizer`:
        D101: Missing docstring in public class
src/infrastructure/security/sql_injection_protection.py:19 in public method `sanitize`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:29 in public function `get_input_sanitizer`:
        D103: Missing docstring in public function
src/infrastructure/security/sql_injection_protection.py:38 in public class `MockQueryValidator`:
        D101: Missing docstring in public class
src/infrastructure/security/sql_injection_protection.py:39 in public method `validate_query`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:49 in public function `get_query_validator`:
        D103: Missing docstring in public function
src/infrastructure/security/sql_injection_protection.py:54 in public class `SQLInjectionProtection`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/sql_injection_protection.py:54 in public class `SQLInjectionProtection`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/sql_injection_protection.py:54 in public class `SQLInjectionProtection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/sql_injection_protection.py:56 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/sql_injection_protection.py:77 in public method `validate_query`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:77 in public method `validate_query`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:96 in public method `sanitize_input`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:96 in public method `sanitize_input`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:108 in public method `check_ip_blocked`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:108 in public method `check_ip_blocked`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:112 in public method `block_ip`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:112 in public method `block_ip`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:118 in public method `unblock_ip`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:118 in public method `unblock_ip`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:130 in public method `record_attack_attempt`:
        D400: First line should end with a period (not 'P')
src/infrastructure/security/sql_injection_protection.py:130 in public method `record_attack_attempt`:
        D415: First line should end with a period, question mark, or exclamation point (not 'P')
src/infrastructure/security/sql_injection_protection.py:163 in private method `_log_attack_attempt`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/sql_injection_protection.py:163 in private method `_log_attack_attempt`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/sql_injection_protection.py:188 in private method `_assess_risk_level`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:188 in private method `_assess_risk_level`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:208 in public method `validate_child_query`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/sql_injection_protection.py:208 in public method `validate_child_query`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/sql_injection_protection.py:208 in public method `validate_child_query`:
        D401: First line should be in imperative mood; try rephrasing (found 'Special')
src/infrastructure/security/sql_injection_protection.py:242 in public method `get_protection_stats`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:242 in public method `get_protection_stats`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:267 in public method `update_configuration`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/sql_injection_protection.py:267 in public method `update_configuration`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/sql_injection_protection.py:277 in public method `reset_protection_state`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/sql_injection_protection.py:277 in public method `reset_protection_state`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/sql_injection_protection.py:283 in public method `export_security_report`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/sql_injection_protection.py:283 in public method `export_security_report`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/sql_injection_protection.py:316 in public function `get_sql_protection`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/sql_injection_protection.py:316 in public function `get_sql_protection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/sql_injection_protection.py:324 in public function `validate_query_safe`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/sql_injection_protection.py:324 in public function `validate_query_safe`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/sql_injection_protection.py:331 in public function `sanitize_user_input`:
        D400: First line should end with a period (not 'g')
src/infrastructure/security/sql_injection_protection.py:331 in public function `sanitize_user_input`:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/infrastructure/security/sql_injection_protection.py:338 in public function `validate_child_query_safe`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/sql_injection_protection.py:338 in public function `validate_child_query_safe`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/sql_injection_protection.py:347 in public function `setup_sql_protection`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/sql_injection_protection.py:347 in public function `setup_sql_protection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/sql_injection_protection.py:347 in public function `setup_sql_protection`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/security/sql_injection_protection.py:364 in public class `SecureQueryBuilder`:
        D101: Missing docstring in public class
src/infrastructure/security/sql_injection_protection.py:365 in public method `build_insert`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:369 in public method `build_update`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:373 in public method `build_select`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:377 in public function `get_secure_query_builder`:
        D103: Missing docstring in public function
src/infrastructure/security/sql_injection_protection.py:381 in public class `EnhancedSQLProtection`:
        D101: Missing docstring in public class
src/infrastructure/security/sql_injection_protection.py:382 in public method `validate_sql_query`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:385 in public method `validate_column_name`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:388 in public method `validate_table_name`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:391 in public method `sanitize_input`:
        D102: Missing docstring in public method
src/infrastructure/security/sql_injection_protection.py:400 in public method `log_security_event`:
        D102: Missing docstring in public method
src/infrastructure/security/token_service.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/token_service.py:14 in public class `TokenService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/token_service.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/vault_client.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/vault_client.py:30 in public class `VaultClient`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/vault_client.py:32 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/vault_client.py:71 in public method `get_secret`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/vault_client.py:71 in public method `get_secret`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/vault_client.py:71 in public method `get_secret`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/vault_client.py:103 in public method `put_secret`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/vault_client.py:103 in public method `put_secret`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/coppa/consent_manager.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/consent_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/coppa/consent_manager.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/coppa/consent_manager.py:24 in public class `COPPAConsentManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/consent_manager.py:24 in public class `COPPAConsentManager`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:44 in public method `verify_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:44 in public method `verify_parental_consent`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:44 in public method `verify_parental_consent`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:44 in public method `verify_parental_consent`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa/consent_manager.py:79 in public method `request_parental_consent`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:79 in public method `request_parental_consent`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:79 in public method `request_parental_consent`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:79 in public method `request_parental_consent`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa/consent_manager.py:119 in public method `get_child_consent_status`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:119 in public method `get_child_consent_status`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:119 in public method `get_child_consent_status`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:119 in public method `get_child_consent_status`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa/consent_manager.py:163 in public method `revoke_consent`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/consent_manager.py:163 in public method `revoke_consent`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:163 in public method `revoke_consent`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/coppa/consent_manager.py:163 in public method `revoke_consent`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/coppa/consent_manager.py:219 in public method `create_consent_record`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_models.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_models.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/coppa/data_models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/coppa/data_models.py:15 in public class `COPPAChildData`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_models.py:103 in public class `ParentConsent`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_models.py:142 in public class `DataRetentionPolicy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_models.py:167 in public class `AuditLogEntry`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_models.py:216 in public class `DataDeletionRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_retention.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_retention.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_retention.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/coppa/data_retention.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/coppa/data_retention.py:22 in public class `DataRetentionManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/coppa/data_retention.py:22 in public class `DataRetentionManager`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_retention.py:22 in public class `DataRetentionManager`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_retention.py:22 in public class `DataRetentionManager`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/coppa/data_retention.py:22 in public class `DataRetentionManager`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/coppa/data_retention.py:30 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/coppa/data_retention.py:47 in public method `create_retention_policy`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_retention.py:47 in public method `create_retention_policy`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_retention.py:47 in public method `create_retention_policy`:
        D400: First line should end with a period (not 'd')
src/infrastructure/security/coppa/data_retention.py:47 in public method `create_retention_policy`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/infrastructure/security/coppa/data_retention.py:70 in public method `calculate_retention_period`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_retention.py:70 in public method `calculate_retention_period`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_retention.py:70 in public method `calculate_retention_period`:
        D400: First line should end with a period (not 'a')
src/infrastructure/security/coppa/data_retention.py:70 in public method `calculate_retention_period`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/security/coppa/data_retention.py:92 in public method `schedule_automatic_deletion`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/data_retention.py:92 in public method `schedule_automatic_deletion`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/data_retention.py:92 in public method `schedule_automatic_deletion`:
        D400: First line should end with a period (not 'a')
src/infrastructure/security/coppa/data_retention.py:92 in public method `schedule_automatic_deletion`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/security/coppa/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/coppa/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/coppa/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/coppa/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/coppa/__init__.py:16 in public function `get_consent_manager`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/infrastructure/security/hardening/csrf_protection.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/hardening/csrf_protection.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/hardening/csrf_protection.py:20 in public class `CSRFConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/csrf_protection.py:20 in public class `CSRFConfig`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:20 in public class `CSRFConfig`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:30 in public method `__post_init__`:
        D105: Missing docstring in magic method
src/infrastructure/security/hardening/csrf_protection.py:36 in public class `CSRFTokenManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/csrf_protection.py:36 in public class `CSRFTokenManager`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:36 in public class `CSRFTokenManager`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:36 in public class `CSRFTokenManager`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:36 in public class `CSRFTokenManager`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:40 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/csrf_protection.py:47 in public method `generate_token`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:47 in public method `generate_token`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:47 in public method `generate_token`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:47 in public method `generate_token`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:83 in public method `validate_token`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:83 in public method `validate_token`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:83 in public method `validate_token`:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/hardening/csrf_protection.py:83 in public method `validate_token`:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/hardening/csrf_protection.py:118 in public method `invalidate_token`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:118 in public method `invalidate_token`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:118 in public method `invalidate_token`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:118 in public method `invalidate_token`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:133 in public method `invalidate_session_tokens`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:133 in public method `invalidate_session_tokens`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:133 in public method `invalidate_session_tokens`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:133 in public method `invalidate_session_tokens`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:153 in private method `_cleanup_expired_tokens`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:153 in private method `_cleanup_expired_tokens`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:169 in public method `get_token_stats`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/csrf_protection.py:169 in public method `get_token_stats`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/csrf_protection.py:189 in public class `CSRFProtection`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/csrf_protection.py:189 in public class `CSRFProtection`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:189 in public class `CSRFProtection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:191 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/csrf_protection.py:196 in public method `generate_token_for_request`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/hardening/csrf_protection.py:196 in public method `generate_token_for_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/hardening/csrf_protection.py:202 in public method `validate_request`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/csrf_protection.py:202 in public method `validate_request`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/csrf_protection.py:202 in public method `validate_request`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/hardening/csrf_protection.py:202 in public method `validate_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/hardening/csrf_protection.py:235 in public method `set_csrf_cookie`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:235 in public method `set_csrf_cookie`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:249 in private method `_get_session_id`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/hardening/csrf_protection.py:249 in private method `_get_session_id`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/hardening/csrf_protection.py:259 in private method `_get_user_id`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/hardening/csrf_protection.py:259 in private method `_get_user_id`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/hardening/csrf_protection.py:271 in private method `_get_csrf_token_from_request`:
        D400: First line should end with a period (not 'a')
src/infrastructure/security/hardening/csrf_protection.py:271 in private method `_get_csrf_token_from_request`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/security/hardening/csrf_protection.py:289 in public class `CSRFMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/csrf_protection.py:289 in public class `CSRFMiddleware`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:289 in public class `CSRFMiddleware`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:291 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/csrf_protection.py:295 in public method `__call__`:
        D102: Missing docstring in public method
src/infrastructure/security/hardening/csrf_protection.py:317 in public function `get_csrf_protection`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:317 in public function `get_csrf_protection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/hardening/csrf_protection.py:333 in public function `init_csrf_protection`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:333 in public function `init_csrf_protection`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/csrf_protection.py:343 in public function `csrf_protect`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/csrf_protection.py:343 in public function `csrf_protect`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/csrf_protection.py:343 in public function `csrf_protect`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/infrastructure/security/hardening/input_validation.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/hardening/secure_settings.py:23 in public class `SecureAppSettings`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/secure_settings.py:80 in public nested class `Config`:
        D106: Missing docstring in public nested class
src/infrastructure/security/hardening/security_tests.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/security_validator.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/security/hardening/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/hardening/security_tests/authentication_tests.py:14 in public class `AuthenticationTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/base_tester.py:13 in public class `BaseSecurityTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/base_tester.py:15 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/security_tests/compliance_tests.py:14 in public class `ComplianceTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/encryption_tests.py:14 in public class `EncryptionTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/injection_tests.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:14 in public class `InjectionTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/injection_tests.py:14 in public class `InjectionTester`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:14 in public class `InjectionTester`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:17 in public method `test_code_injection`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:17 in public method `test_code_injection`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:54 in public method `test_sql_injection`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:54 in public method `test_sql_injection`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:93 in public method `test_xss_vulnerabilities`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:93 in public method `test_xss_vulnerabilities`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:146 in public method `test_path_traversal`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/security_tests/injection_tests.py:146 in public method `test_path_traversal`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/security_tests/security_tester.py:17 in public class `SecurityTester`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/security_tests/security_tester.py:19 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/validation/sanitizer.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/validation/sanitizer.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/sanitizer.py:1 at module level:
        D400: First line should end with a period (not 'c')
src/infrastructure/security/hardening/validation/sanitizer.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'c')
src/infrastructure/security/hardening/validation/sanitizer.py:20 in public class `ValidationSeverity`:
        D101: Missing docstring in public class
src/infrastructure/security/hardening/validation/sanitizer.py:27 in public class `ValidationRule`:
        D101: Missing docstring in public class
src/infrastructure/security/hardening/validation/sanitizer.py:34 in public class `InputValidationConfig`:
        D101: Missing docstring in public class
src/infrastructure/security/hardening/validation/sanitizer.py:44 in public function `get_default_validation_rules`:
        D103: Missing docstring in public function
src/infrastructure/security/hardening/validation/sanitizer.py:66 in public function `get_profanity_words`:
        D103: Missing docstring in public function
src/infrastructure/security/hardening/validation/sanitizer.py:88 in public class `InputSanitizer`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/validation/sanitizer.py:90 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/hardening/validation/sanitizer.py:119 in public method `sanitize_string`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/hardening/validation/validation_config.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/validation_config.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/validation/validation_config.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/validation/validation_config.py:13 in public class `ValidationSeverity`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:13 in public class `ValidationSeverity`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:22 in public class `ValidationRule`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:22 in public class `ValidationRule`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:30 in public class `InputValidationConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_config.py:30 in public class `InputValidationConfig`:
        D204: 1 blank line required after class docstring (found 0)
src/infrastructure/security/hardening/validation/validation_rules.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/validation/validation_rules.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/validation_rules.py:1 at module level:
        D400: First line should end with a period (not 's')
src/infrastructure/security/hardening/validation/validation_rules.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/hardening/validation/validation_rules.py:73 in public function `get_profanity_words`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/validation/validation_rules.py:73 in public function `get_profanity_words`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/validation_rules.py:73 in public function `get_profanity_words`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/hardening/validation/validation_rules.py:73 in public function `get_profanity_words`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/hardening/validation/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/hardening/validation/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/hardening/validation/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/hardening/validation/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/input_validation/core.py:7 in public class `SecurityThreat`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/core.py:9 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/core.py:26 in public class `InputValidationResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/core.py:28 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/detectors.py:14 in public class `SecurityPatterns`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/detectors.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/detectors.py:84 in public class `ThreatDetectors`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/detectors.py:86 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/middleware.py:20 in public class `MockValidator`:
        D101: Missing docstring in public class
src/infrastructure/security/input_validation/middleware.py:21 in public method `validate_input`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/middleware.py:26 in public function `get_input_validator`:
        D103: Missing docstring in public function
src/infrastructure/security/input_validation/middleware.py:36 in public class `MockAuditIntegration`:
        D101: Missing docstring in public class
src/infrastructure/security/input_validation/middleware.py:37 in public method `log_security_event`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/middleware.py:40 in public function `get_audit_integration`:
        D103: Missing docstring in public function
src/infrastructure/security/input_validation/middleware.py:45 in public class `InputValidationMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/middleware.py:47 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/middleware.py:377 in public function `setup_child_safe_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/security/input_validation/middleware.py:384 in public function `setup_development_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/security/input_validation/middleware.py:391 in public function `setup_production_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/security/input_validation/patterns.py:7 in public class `SecurityPatterns`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/patterns.py:9 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/patterns.py:78 in private method `_setup_child_safety_patterns`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/infrastructure/security/input_validation/validator.py:19 in public class `ThreatDetectors`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/validator.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/validator.py:24 in public method `detect_sql_injection`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:27 in public method `detect_xss`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:30 in public method `detect_path_traversal`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:33 in public method `detect_command_injection`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:36 in public method `detect_ldap_injection`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:39 in public method `detect_template_injection`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:42 in public method `detect_inappropriate_content`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:45 in public method `detect_pii`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:48 in public method `detect_encoding_attacks`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:58 in public class `MockAuditIntegration`:
        D101: Missing docstring in public class
src/infrastructure/security/input_validation/validator.py:59 in public method `log_security_event`:
        D102: Missing docstring in public method
src/infrastructure/security/input_validation/validator.py:62 in public function `get_audit_integration`:
        D103: Missing docstring in public function
src/infrastructure/security/input_validation/validator.py:67 in public class `ComprehensiveInputValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/input_validation/validator.py:67 in public class `ComprehensiveInputValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/input_validation/validator.py:81 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/input_validation/validator.py:91 in public method `validate_input`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/input_validation/validator.py:91 in public method `validate_input`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/security/input_validation/validator.py:91 in public method `validate_input`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/input_validation/validator.py:91 in public method `validate_input`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/input_validation/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/input_validation/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_generator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/key_generator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_generator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/key_management/key_generator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/key_management/key_generator.py:15 in public class `KeyGenerator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/key_generator.py:30 in public method `generate_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_generator.py:30 in public method `generate_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_lifecycle_manager.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/key_lifecycle_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_lifecycle_manager.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/key_management/key_lifecycle_manager.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/key_management/key_lifecycle_manager.py:21 in public class `KeyLifecycleManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/key_lifecycle_manager.py:24 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_lifecycle_manager.py:24 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_lifecycle_manager.py:52 in public method `create_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_lifecycle_manager.py:52 in public method `create_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_lifecycle_manager.py:93 in public method `deactivate_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_lifecycle_manager.py:93 in public method `deactivate_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_lifecycle_manager.py:115 in public method `cleanup_old_keys`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_lifecycle_manager.py:115 in public method `cleanup_old_keys`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/key_rotation_orchestrator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:35 in public class `KeyRotationOrchestrator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/key_rotation_orchestrator.py:35 in public class `KeyRotationOrchestrator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/key_rotation_orchestrator.py:35 in public class `KeyRotationOrchestrator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:41 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:41 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:65 in public method `create_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:65 in public method `create_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:81 in public method `rotate_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:81 in public method `rotate_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:93 in public method `rotate_all_keys`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:93 in public method `rotate_all_keys`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:115 in public method `perform_scheduled_rotation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:115 in public method `perform_scheduled_rotation`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:115 in public method `perform_scheduled_rotation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:127 in public method `emergency_rotation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:127 in public method `emergency_rotation`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:138 in public method `cleanup_old_keys`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:138 in public method `cleanup_old_keys`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:151 in public method `get_rotation_statistics`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:151 in public method `get_rotation_statistics`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:151 in public method `get_rotation_statistics`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:160 in public method `check_rotation_needed`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/key_rotation_orchestrator.py:160 in public method `check_rotation_needed`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/key_rotation_orchestrator.py:160 in public method `check_rotation_needed`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_executor.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/rotation_executor.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_executor.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/key_management/rotation_executor.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/key_management/rotation_executor.py:30 in public class `RotationExecutor`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/rotation_executor.py:39 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_executor.py:39 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_executor.py:60 in public method `rotate_key`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_executor.py:60 in public method `rotate_key`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_executor.py:137 in public method `perform_scheduled_rotation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_executor.py:137 in public method `perform_scheduled_rotation`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/rotation_executor.py:137 in public method `perform_scheduled_rotation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_executor.py:172 in public method `emergency_rotation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_executor.py:172 in public method `emergency_rotation`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_policy_manager.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/rotation_policy_manager.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/security/key_management/rotation_policy_manager.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/security/key_management/rotation_policy_manager.py:18 in public class `RotationPolicyManager`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/rotation_policy_manager.py:21 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:21 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_policy_manager.py:32 in public method `check_rotation_needed`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:32 in public method `check_rotation_needed`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_policy_manager.py:60 in public method `get_keys_needing_rotation`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:60 in public method `get_keys_needing_rotation`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/rotation_policy_manager.py:60 in public method `get_keys_needing_rotation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_policy_manager.py:73 in public method `get_next_rotation_time`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:73 in public method `get_next_rotation_time`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/rotation_policy_manager.py:73 in public method `get_next_rotation_time`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_policy_manager.py:92 in public method `get_affected_services`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_policy_manager.py:92 in public method `get_affected_services`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_statistics.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/rotation_statistics.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/key_management/rotation_statistics.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/key_management/rotation_statistics.py:22 in public class `RotationStatistics`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/key_management/rotation_statistics.py:29 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:29 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_statistics.py:40 in public method `get_rotation_statistics`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:40 in public method `get_rotation_statistics`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/rotation_statistics.py:40 in public method `get_rotation_statistics`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_statistics.py:80 in private method `_calculate_average_age`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:80 in private method `_calculate_average_age`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/rotation_statistics.py:96 in public method `get_key_usage_report`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:96 in public method `get_key_usage_report`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/key_management/rotation_statistics.py:96 in public method `get_key_usage_report`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/key_management/rotation_statistics.py:123 in public method `get_rotation_history`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/rotation_statistics.py:123 in public method `get_rotation_history`:
        D407: Missing dashed underline after section ('Args')
src/infrastructure/security/key_management/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/key_management/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/key_management/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/key_management/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/rate_limiter/child_safety.py:14 in public class `ChildSafetyHandler`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/child_safety.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter/config.py:7 in public class `DefaultConfigurations`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter/core.py:16 in public class `RateLimitType`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:31 in public class `RateLimitStrategy`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:41 in public class `RateLimitConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:69 in public class `RateLimitState`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:82 in public class `RateLimitResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:94 in public class `RedisRateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:94 in public class `RedisRateLimiter`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/rate_limiter/core.py:94 in public class `RedisRateLimiter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter/core.py:94 in public class `RedisRateLimiter`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/rate_limiter/core.py:94 in public class `RedisRateLimiter`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/rate_limiter/core.py:98 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter/core.py:192 in public class `ChildSafetyRateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/core.py:194 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter/service.py:22 in public class `ComprehensiveRateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/service.py:22 in public class `ComprehensiveRateLimiter`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter/service.py:34 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter/service.py:53 in public method `check_rate_limit`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/rate_limiter/service.py:53 in public method `check_rate_limit`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/security/rate_limiter/service.py:53 in public method `check_rate_limit`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/security/rate_limiter/storage.py:14 in public class `RateLimitStorage`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/storage.py:16 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/rate_limiter/strategies.py:14 in public class `RateLimitingStrategies`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/rate_limiter/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/safe_expression_parser/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/security/safe_expression_parser/__init__.py:9 in public class `ExpressionContext`:
        D101: Missing docstring in public class
src/infrastructure/security/safe_expression_parser/__init__.py:13 in public class `SafeExpressionConfig`:
        D101: Missing docstring in public class
src/infrastructure/security/safe_expression_parser/__init__.py:14 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/safe_expression_parser/__init__.py:18 in public class `SafeExpressionParser`:
        D101: Missing docstring in public class
src/infrastructure/security/safe_expression_parser/__init__.py:19 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/safe_expression_parser/__init__.py:22 in public method `evaluate`:
        D102: Missing docstring in public method
src/infrastructure/security/validation/query_validator.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/validation/query_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/validation/query_validator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/validation/query_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/validation/query_validator.py:17 in public class `QueryValidationResult`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/validation/query_validator.py:17 in public class `QueryValidationResult`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:17 in public class `QueryValidationResult`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:27 in public class `SQLQueryValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/security/validation/query_validator.py:27 in public class `SQLQueryValidator`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/validation/query_validator.py:27 in public class `SQLQueryValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/validation/query_validator.py:27 in public class `SQLQueryValidator`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:27 in public class `SQLQueryValidator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/security/validation/query_validator.py:85 in public method `validate_query_parameters`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:85 in public method `validate_query_parameters`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:136 in public method `validate_table_name`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/validation/query_validator.py:136 in public method `validate_table_name`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/validation/query_validator.py:150 in public method `validate_column_name`:
        D400: First line should end with a period (not 't')
src/infrastructure/security/validation/query_validator.py:150 in public method `validate_column_name`:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/infrastructure/security/validation/query_validator.py:181 in public method `create_safe_where_clause`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/validation/query_validator.py:181 in public method `create_safe_where_clause`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/validation/query_validator.py:207 in public method `validate_child_data_query`:
        D400: First line should end with a period (not 'a')
src/infrastructure/security/validation/query_validator.py:207 in public method `validate_child_data_query`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/infrastructure/security/validation/query_validator.py:207 in public method `validate_child_data_query`:
        D401: First line should be in imperative mood; try rephrasing (found 'Special')
src/infrastructure/security/validation/query_validator.py:241 in public method `log_security_event`:
        D400: First line should end with a period (not 'g')
src/infrastructure/security/validation/query_validator.py:241 in public method `log_security_event`:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/infrastructure/security/validation/query_validator.py:260 in public method `sanitize_query_string`:
        D400: First line should end with a period (not ')')
src/infrastructure/security/validation/query_validator.py:260 in public method `sanitize_query_string`:
        D415: First line should end with a period, question mark, or exclamation point (not ')')
src/infrastructure/security/validation/query_validator.py:279 in public method `get_safe_limit_offset`:
        D400: First line should end with a period (not 's')
src/infrastructure/security/validation/query_validator.py:279 in public method `get_safe_limit_offset`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/infrastructure/security/validation/query_validator.py:323 in public function `get_query_validator`:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/validation/query_validator.py:323 in public function `get_query_validator`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/security/validation/query_validator.py:332 in public function `validate_params`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:332 in public function `validate_params`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:338 in public function `is_safe_table`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:338 in public function `is_safe_table`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:344 in public function `is_safe_column`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:344 in public function `is_safe_column`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:350 in public function `create_safe_where`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:350 in public function `create_safe_where`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/query_validator.py:358 in public function `validate_child_query`:
        D400: First line should end with a period (not 'n')
src/infrastructure/security/validation/query_validator.py:358 in public function `validate_child_query`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/security/validation/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/security/validation/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/security/validation/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/security/validation/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/services/data_retention_service.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/services/data_retention_service.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/services/data_retention_service.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/services/data_retention_service.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/services/data_retention_service.py:19 in public class `RetentionStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/services/data_retention_service.py:29 in public class `COPPADataRetentionService`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/services/data_retention_service.py:29 in public class `COPPADataRetentionService`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/services/data_retention_service.py:54 in public method `register_child_data`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/services/data_retention_service.py:54 in public method `register_child_data`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/services/data_retention_service.py:54 in public method `register_child_data`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/services/data_retention_service.py:54 in public method `register_child_data`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/services/data_retention_service.py:102 in public method `schedule_daily_retention_check`:
        D205: 1 blank line required between summary line and description (found 0)
src/infrastructure/services/data_retention_service.py:102 in public method `schedule_daily_retention_check`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/session_manager/session_models.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/session_manager/session_models.py:11 in public class `Session`:
        D101: Missing docstring in public class
src/infrastructure/session_manager/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/state/application_state_manager.py:1 at module level:
        D100: Missing docstring in public module
src/infrastructure/state/application_state_manager.py:6 in public class `StateScope`:
        D101: Missing docstring in public class
src/infrastructure/state/application_state_manager.py:12 in public class `ApplicationStateManager`:
        D101: Missing docstring in public class
src/infrastructure/state/application_state_manager.py:13 in public method `__init__`:
        D107: Missing docstring in __init__
src/infrastructure/state/application_state_manager.py:17 in public method `set_state`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:26 in public method `get_state`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:29 in public method `has_state`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:32 in public method `delete_state`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:36 in public method `async_request_context`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:46 in public method `session_context`:
        D102: Missing docstring in public method
src/infrastructure/state/application_state_manager.py:57 in public function `create_state_manager`:
        D103: Missing docstring in public function
src/infrastructure/state/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/infrastructure/validation/child_safety_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/child_safety_validator.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/infrastructure/validation/child_safety_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/infrastructure/validation/comprehensive_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/validation/comprehensive_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/validation/comprehensive_validator.py:20 in public class `ComprehensiveValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/validation/comprehensive_validator.py:20 in public class `ComprehensiveValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:48 in public method `validate_child_registration`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:48 in public method `validate_child_registration`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:48 in public method `validate_child_registration`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:48 in public method `validate_child_registration`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/comprehensive_validator.py:116 in public method `validate_message_input`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:116 in public method `validate_message_input`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:116 in public method `validate_message_input`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:116 in public method `validate_message_input`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/comprehensive_validator.py:183 in public method `validate_file_upload`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:183 in public method `validate_file_upload`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:183 in public method `validate_file_upload`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:183 in public method `validate_file_upload`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/comprehensive_validator.py:219 in public method `validate_parent_data`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:219 in public method `validate_parent_data`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:219 in public method `validate_parent_data`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:219 in public method `validate_parent_data`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/comprehensive_validator.py:265 in public method `validate_search_query`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/comprehensive_validator.py:265 in public method `validate_search_query`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:265 in public method `validate_search_query`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/comprehensive_validator.py:265 in public method `validate_search_query`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/comprehensive_validator.py:337 in public function `validate_child_registration`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenient')
src/infrastructure/validation/comprehensive_validator.py:343 in public function `validate_message_input`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenient')
src/infrastructure/validation/comprehensive_validator.py:349 in public function `validate_file_upload`:
        D401: First line should be in imperative mood; try rephrasing (found 'Convenient')
src/infrastructure/validation/emergency_contact_validator.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/emergency_contact_validator.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/infrastructure/validation/emergency_contact_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/infrastructure/validation/emergency_contact_validator.py:17 in public class `EmergencyContact`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/validation/emergency_contact_validator.py:28 in public class `EmergencyContactValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/infrastructure/validation/emergency_contact_validator.py:28 in public class `EmergencyContactValidator`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/emergency_contact_validator.py:80 in public method `validate_emergency_contact`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/emergency_contact_validator.py:80 in public method `validate_emergency_contact`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:80 in public method `validate_emergency_contact`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:80 in public method `validate_emergency_contact`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/emergency_contact_validator.py:146 in public method `validate_emergency_contacts_list`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/emergency_contact_validator.py:146 in public method `validate_emergency_contacts_list`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:146 in public method `validate_emergency_contacts_list`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:146 in public method `validate_emergency_contacts_list`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/emergency_contact_validator.py:372 in public method `get_contact_accessibility_score`:
        D213: Multi-line docstring summary should start at the second line
src/infrastructure/validation/emergency_contact_validator.py:372 in public method `get_contact_accessibility_score`:
        D413: Missing blank line after last section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:372 in public method `get_contact_accessibility_score`:
        D407: Missing dashed underline after section ('Returns')
src/infrastructure/validation/emergency_contact_validator.py:372 in public method `get_contact_accessibility_score`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/infrastructure/validation/general_input_validator.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/infrastructure/validation/general_input_validator.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/infrastructure/validation/general_input_validator.py:5 in public class `GeneralInputValidator`:
        D101: Missing docstring in public class
src/infrastructure/validation/general_input_validator.py:6 in public method `validate_text`:
        D102: Missing docstring in public method
src/infrastructure/validation/general_input_validator.py:9 in public method `validate_email`:
        D102: Missing docstring in public method
src/infrastructure/validation/general_input_validator.py:14 in public function `get_general_input_validator`:
        D103: Missing docstring in public function
src/presentation/routing.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/routing.py:44 in public function `setup_routing`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/routing.py:44 in public function `setup_routing`:
        D407: Missing dashed underline after section ('Args')
src/presentation/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/esp32_endpoints.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/esp32_endpoints.py:29 in public function `get_current_user_esp32`:
        D400: First line should end with a period (not 's')
src/presentation/api/esp32_endpoints.py:29 in public function `get_current_user_esp32`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/esp32_endpoints.py:61 in public class `AudioRequest`:
        D101: Missing docstring in public class
src/presentation/api/esp32_endpoints.py:70 in public class `AudioResponse`:
        D101: Missing docstring in public class
src/presentation/api/esp32_endpoints.py:79 in public class `DeviceStatusRequest`:
        D101: Missing docstring in public class
src/presentation/api/esp32_endpoints.py:97 in public function `process_audio`:
        D400: First line should end with a period (not 'e')
src/presentation/api/esp32_endpoints.py:97 in public function `process_audio`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/api/esp32_endpoints.py:177 in public function `update_device_status`:
        D400: First line should end with a period (not 's')
src/presentation/api/esp32_endpoints.py:177 in public function `update_device_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/esp32_endpoints.py:191 in public function `health_check`:
        D400: First line should end with a period (not 'h')
src/presentation/api/esp32_endpoints.py:191 in public function `health_check`:
        D415: First line should end with a period, question mark, or exclamation point (not 'h')
src/presentation/api/esp32_endpoints.py:206 in public function `get_device_config`:
        D400: First line should end with a period (not 'n')
src/presentation/api/esp32_endpoints.py:206 in public function `get_device_config`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/health_endpoints.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/main_router.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/main_router.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/main_router.py:46 in public function `api_info`:
        D401: First line should be in imperative mood; try rephrasing (found 'API')
src/presentation/api/openapi_config.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/parental_dashboard.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/parental_dashboard.py:31 in public class `CreateChildRequest`:
        D101: Missing docstring in public class
src/presentation/api/parental_dashboard.py:51 in public class `UpdateChildRequest`:
        D101: Missing docstring in public class
src/presentation/api/parental_dashboard.py:70 in public class `ParentConsentRequest`:
        D101: Missing docstring in public class
src/presentation/api/parental_dashboard.py:91 in public class `ConsentStatusResponse`:
        D101: Missing docstring in public class
src/presentation/api/parental_dashboard.py:105 in public function `create_child_profile_endpoint`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:124 in public function `get_child_profile_endpoint`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:137 in public function `update_child_profile_endpoint`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:153 in public function `delete_child_profile_endpoint`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:165 in public function `generate_child_story_endpoint`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:193 in public function `request_consent_verification`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:224 in public function `grant_parental_consent`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:267 in public function `get_consent_status`:
        D103: Missing docstring in public function
src/presentation/api/parental_dashboard.py:290 in public function `revoke_consent`:
        D103: Missing docstring in public function
src/presentation/api/validators.py:12 in public class `ChildValidationMixin`:
        D101: Missing docstring in public class
src/presentation/api/validators.py:15 in public method `validate_age`:
        D102: Missing docstring in public method
src/presentation/api/validators.py:24 in public method `validate_name`:
        D102: Missing docstring in public method
src/presentation/api/validators.py:48 in public method `validate_interests`:
        D102: Missing docstring in public method
src/presentation/api/validators.py:75 in public method `validate_language`:
        D102: Missing docstring in public method
src/presentation/api/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/presentation/api/decorators/rate_limit.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/decorators/rate_limit.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/decorators/rate_limit.py:15 in public function `rate_limit`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/decorators/rate_limit.py:15 in public function `rate_limit`:
        D413: Missing blank line after last section ('Args')
src/presentation/api/decorators/rate_limit.py:15 in public function `rate_limit`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/decorators/rate_limit.py:66 in public function `check_child_interaction_limit`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/decorators/rate_limit.py:66 in public function `check_child_interaction_limit`:
        D413: Missing blank line after last section ('Raises')
src/presentation/api/decorators/rate_limit.py:66 in public function `check_child_interaction_limit`:
        D407: Missing dashed underline after section ('Raises')
src/presentation/api/decorators/rate_limit.py:66 in public function `check_child_interaction_limit`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/presentation/api/dependencies/auth.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/dependencies/auth.py:16 in public function `get_authenticated_user`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/dependencies/auth.py:16 in public function `get_authenticated_user`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/dependencies/auth.py:16 in public function `get_authenticated_user`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/dependencies/base.py:9 in public class `ServiceFactory`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/dependencies/base.py:17 in public class `LazyServiceProvider`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/dependencies/base.py:19 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/dependencies/base.py:23 in public method `get`:
        D102: Missing docstring in public method
src/presentation/api/emergency_response/endpoints.py:1 at module level:
        D400: First line should end with a period (not 'm')
src/presentation/api/emergency_response/endpoints.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/presentation/api/emergency_response/endpoints.py:34 in public class `EmergencyEndpoints`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/endpoints.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/emergency_response/models.py:1 at module level:
        D400: First line should end with a period (not 'm')
src/presentation/api/emergency_response/models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'm')
src/presentation/api/emergency_response/models.py:10 in public class `AlertPayload`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:18 in public class `EmergencyAlert`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:31 in public class `SystemStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:41 in public class `HealthResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:51 in public class `NotificationRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:61 in public class `ResponseAction`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:72 in public class `EmergencyContact`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:84 in public class `AlertRule`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:97 in public class `SafetyIncident`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:112 in public class `AlertHistory`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:123 in public class `ParentNotification`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/models.py:138 in public class `SystemConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/services.py:1 at module level:
        D400: First line should end with a period (not 'g')
src/presentation/api/emergency_response/services.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'g')
src/presentation/api/emergency_response/services.py:20 in public class `EmergencyResponseService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/services.py:22 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/emergency_response/services.py:183 in public class `SystemMonitorService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/services.py:185 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/emergency_response/services.py:283 in public class `EmergencyNotificationService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/emergency_response/services.py:285 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/emergency_response/__init__.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/emergency_response/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/audio.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/auth.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/children_legacy.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children_legacy.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children_legacy.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/presentation/api/endpoints/children_legacy.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/api/endpoints/conversations.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/conversations.py:34 in public function `get_authenticated_user`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/conversations.py:34 in public function `get_authenticated_user`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/endpoints/conversations.py:34 in public function `get_authenticated_user`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/endpoints/conversations.py:34 in public function `get_authenticated_user`:
        D407: Missing dashed underline after section ('Raises')
src/presentation/api/endpoints/conversations.py:34 in public function `get_authenticated_user`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/presentation/api/endpoints/conversations_paginated.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/conversations_paginated.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/conversations_paginated.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/conversations_paginated.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/conversations_paginated.py:62 in public class `ConversationPaginationService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/coppa_notices.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/coppa_notices.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/coppa_notices.py:23 in public class `COPPANoticeResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/coppa_notices.py:34 in public class `COPPAValidatorStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/coppa_notices.py:43 in public function `get_coppa_status`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:43 in public function `get_coppa_status`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:43 in public function `get_coppa_status`:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/coppa_notices.py:43 in public function `get_coppa_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/coppa_notices.py:67 in public function `get_coppa_notice`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:67 in public function `get_coppa_notice`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:67 in public function `get_coppa_notice`:
        D400: First line should end with a period (not 'e')
src/presentation/api/endpoints/coppa_notices.py:67 in public function `get_coppa_notice`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/api/endpoints/coppa_notices.py:117 in public function `get_child_privacy_settings`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:117 in public function `get_child_privacy_settings`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:117 in public function `get_child_privacy_settings`:
        D400: First line should end with a period (not 'd')
src/presentation/api/endpoints/coppa_notices.py:117 in public function `get_child_privacy_settings`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/presentation/api/endpoints/coppa_notices.py:168 in public function `request_coppa_consent`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:168 in public function `request_coppa_consent`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:168 in public function `request_coppa_consent`:
        D400: First line should end with a period (not 'd')
src/presentation/api/endpoints/coppa_notices.py:168 in public function `request_coppa_consent`:
        D415: First line should end with a period, question mark, or exclamation point (not 'd')
src/presentation/api/endpoints/coppa_notices.py:220 in public function `request_data_deletion`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/coppa_notices.py:220 in public function `request_data_deletion`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/coppa_notices.py:220 in public function `request_data_deletion`:
        D400: First line should end with a period (not 'a')
src/presentation/api/endpoints/coppa_notices.py:220 in public function `request_data_deletion`:
        D415: First line should end with a period, question mark, or exclamation point (not 'a')
src/presentation/api/endpoints/dashboard.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/dashboard.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/dashboard.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/dashboard.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/dashboard.py:99 in public function `get_child_stats`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/dashboard.py:185 in public function `get_devices_status`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/dashboard.py:299 in public function `get_system_health`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/device.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/device.py:25 in public class `DeviceRegistration`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/device.py:25 in public class `DeviceRegistration`:
        D400: First line should end with a period (not 'n')
src/presentation/api/endpoints/device.py:25 in public class `DeviceRegistration`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/endpoints/device.py:61 in public class `DeviceStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/device.py:61 in public class `DeviceStatus`:
        D400: First line should end with a period (not 'n')
src/presentation/api/endpoints/device.py:61 in public class `DeviceStatus`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/endpoints/device.py:83 in public function `register_device`:
        D400: First line should end with a period (not 'e')
src/presentation/api/endpoints/device.py:83 in public function `register_device`:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/api/endpoints/device.py:131 in public function `get_device_status`:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/device.py:131 in public function `get_device_status`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/device.py:159 in public class `AudioUploadRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/device.py:159 in public class `AudioUploadRequest`:
        D400: First line should end with a period (not 'n')
src/presentation/api/endpoints/device.py:159 in public class `AudioUploadRequest`:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/endpoints/device.py:194 in public function `upload_audio`:
        D400: First line should end with a period (not '2')
src/presentation/api/endpoints/device.py:194 in public function `upload_audio`:
        D415: First line should end with a period, question mark, or exclamation point (not '2')
src/presentation/api/endpoints/device.py:229 in public class `DeviceConfig`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/device.py:229 in public class `DeviceConfig`:
        D400: First line should end with a period (not 'l')
src/presentation/api/endpoints/device.py:229 in public class `DeviceConfig`:
        D415: First line should end with a period, question mark, or exclamation point (not 'l')
src/presentation/api/endpoints/device.py:250 in public function `get_device_config`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/device.py:250 in public function `get_device_config`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/health.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/health.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/health.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/health.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/health.py:55 in public class `HealthStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/health.py:123 in public function `basic_health_check`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/health.py:123 in public function `basic_health_check`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/health.py:123 in public function `basic_health_check`:
        D401: First line should be in imperative mood; try rephrasing (found 'Basic')
src/presentation/api/endpoints/health.py:208 in public function `readiness_check`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/health.py:208 in public function `readiness_check`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/health.py:255 in public function `liveness_check`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/health.py:255 in public function `liveness_check`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/monitoring_dashboard.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/monitoring_dashboard.py:36 in public class `MonitoringDashboardService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/auth/routes_di.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/children/compliance.py:23 in public class `ConsentRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:23 in public class `ConsentRequest`:
        D204: 1 blank line required after class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:29 in public class `ConsentResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:29 in public class `ConsentResponse`:
        D204: 1 blank line required after class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:35 in public class `ComplianceValidator`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/compliance.py:68 in public class `DataRetentionManager`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:70 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/compliance.py:122 in public class `COPPAIntegration`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/compliance.py:122 in public class `COPPAIntegration`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/compliance.py:129 in public method `__init__`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/compliance.py:129 in public method `__init__`:
        D413: Missing blank line after last section ('Args')
src/presentation/api/endpoints/children/compliance.py:129 in public method `__init__`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/endpoints/children/compliance.py:143 in public method `validate_child_creation`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/compliance.py:143 in public method `validate_child_creation`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/endpoints/children/compliance.py:143 in public method `validate_child_creation`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/endpoints/children/compliance.py:143 in public method `validate_child_creation`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/endpoints/children/compliance.py:163 in public method `get_compliance_requirements`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/compliance.py:163 in public method `get_compliance_requirements`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/endpoints/children/compliance.py:163 in public method `get_compliance_requirements`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/endpoints/children/compliance.py:163 in public method `get_compliance_requirements`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/endpoints/children/create_child.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/create_child.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/create_child.py:1 at module level:
        D400: First line should end with a period (not 't')
src/presentation/api/endpoints/children/create_child.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/presentation/api/endpoints/children/get_children.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/get_children.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/get_children.py:1 at module level:
        D400: First line should end with a period (not 't')
src/presentation/api/endpoints/children/get_children.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 't')
src/presentation/api/endpoints/children/models.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/children/models.py:19 in public class `ChildPreferences`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/models.py:28 in public class `ChildCreateRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/models.py:39 in public class `ChildUpdateRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/models.py:50 in public class `ChildResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/models.py:64 in public class `ChildSafetySummary`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/models.py:107 in public class `ChildDeleteResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/operations.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/operations.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/operations.py:34 in public class `ChildOperations`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/operations.py:36 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/operations.py:185 in public class `ChildValidationService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/operations.py:187 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/operations.py:256 in public class `ChildDataTransformer`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/operations.py:304 in public class `ChildSearchService`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/operations.py:306 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/routes.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/endpoints/children/routes.py:29 in private function `_setup_create_child_route`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:45 in private function `_setup_get_children_route`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:60 in private function `_setup_get_child_route`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:76 in private function `_setup_update_child_route`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:97 in private function `_setup_delete_child_route`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:113 in private function `_setup_safety_routes`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:132 in private function `_setup_monitoring_routes`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes.py:182 in public function `setup_routes`:
        D401: First line should be in imperative mood; try rephrasing (found 'Setup')
src/presentation/api/endpoints/children/routes_refactored.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/routes_refactored.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/routes_refactored.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/endpoints/children/routes_refactored.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/endpoints/children/routes_refactored.py:109 in public function `create_children_router`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/presentation/api/endpoints/children/routes_refactored.py:126 in public function `create_extended_children_router`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/presentation/api/endpoints/children/routes_refactored.py:225 in public function `create_complete_children_router`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/presentation/api/endpoints/children/route_handlers.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/route_handlers.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/route_handlers.py:34 in public class `ChildRouteHandlers`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/route_handlers.py:37 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D407: Missing dashed underline after section ('Raises')
src/presentation/api/endpoints/children/route_handlers.py:60 in public method `create_child_handler`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D407: Missing dashed underline after section ('Raises')
src/presentation/api/endpoints/children/route_handlers.py:129 in public method `get_children_handler`:
        D406: Section name should end with a newline ('Raises', not 'Raises:')
src/presentation/api/endpoints/children/safety.py:20 in public class `HTTPException`:
        D101: Missing docstring in public class
src/presentation/api/endpoints/children/safety.py:21 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/endpoints/children/safety.py:25 in public class `status`:
        D101: Missing docstring in public class
src/presentation/api/endpoints/children/safety.py:43 in public class `SafetyEventTypes`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/safety.py:54 in public class `ChildSafetyManager`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/safety.py:220 in public class `ContentSafetyFilter`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/safety.py:314 in public class `PrivacyProtectionManager`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/safety.py:387 in public class `UsageMonitor`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/endpoints/children/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/endpoints/children/__init__.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/presentation/api/endpoints/children/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/middleware/child_safe_rate_limiter.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/middleware/child_safe_rate_limiter.py:10 in public class `ChildSafeRateLimiter`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/child_safe_rate_limiter.py:12 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/consent_verification.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/consent_verification.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/consent_verification.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/presentation/api/middleware/consent_verification.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/api/middleware/consent_verification.py:19 in public class `ConsentVerificationRoute`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/consent_verification.py:19 in public class `ConsentVerificationRoute`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/consent_verification.py:19 in public class `ConsentVerificationRoute`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/consent_verification.py:19 in public class `ConsentVerificationRoute`:
        D400: First line should end with a period (not 's')
src/presentation/api/middleware/consent_verification.py:19 in public class `ConsentVerificationRoute`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/middleware/consent_verification.py:23 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/consent_verification.py:34 in public method `get_route_handler`:
        D102: Missing docstring in public method
src/presentation/api/middleware/consent_verification.py:176 in public function `require_consent`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/consent_verification.py:176 in public function `require_consent`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/consent_verification.py:176 in public function `require_consent`:
        D400: First line should end with a period (not 's')
src/presentation/api/middleware/consent_verification.py:176 in public function `require_consent`:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/middleware/consent_verification.py:176 in public function `require_consent`:
        D401: First line should be in imperative mood (perhaps 'Decorate', not 'Decorator')
src/presentation/api/middleware/consent_verification.py:191 in public class `ConsentVerificationMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/consent_verification.py:193 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/consent_verification.py:205 in public method `__call__`:
        D102: Missing docstring in public method
src/presentation/api/middleware/error_handling.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/error_handling.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/error_handling.py:1 at module level:
        D400: First line should end with a period (not 'r')
src/presentation/api/middleware/error_handling.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'r')
src/presentation/api/middleware/error_handling.py:22 in public class `ErrorHandlingMiddleware`:
        D200: One-line docstring should fit on one line with quotes (found 3)
src/presentation/api/middleware/error_handling.py:22 in public class `ErrorHandlingMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/error_handling.py:22 in public class `ErrorHandlingMiddleware`:
        D212: Multi-line docstring summary should start at the first line
src/presentation/api/middleware/error_handling.py:26 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/rate_limit_middleware.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/middleware/rate_limit_middleware.py:16 in public class `RateLimitMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/rate_limit_middleware.py:16 in public class `RateLimitMiddleware`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/rate_limit_middleware.py:16 in public class `RateLimitMiddleware`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/rate_limit_middleware.py:25 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/rate_limit_middleware.py:285 in public function `create_rate_limit_middleware`:
        D401: First line should be in imperative mood; try rephrasing (found 'Factory')
src/presentation/api/middleware/request_logging.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/api/middleware/request_logging.py:25 in public class `RequestLoggingMiddleware`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/middleware/request_logging.py:25 in public class `RequestLoggingMiddleware`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/middleware/request_logging.py:25 in public class `RequestLoggingMiddleware`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/request_logging.py:33 in public method `__init__`:
        D107: Missing docstring in __init__
src/presentation/api/middleware/request_logging.py:79 in public method `dispatch`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/request_logging.py:79 in public method `dispatch`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/middleware/request_logging.py:141 in private method `_extract_request_info`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/request_logging.py:141 in private method `_extract_request_info`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/middleware/request_logging.py:193 in private method `_extract_response_info`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/request_logging.py:193 in private method `_extract_response_info`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/middleware/request_logging.py:210 in private method `_sanitize_data`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/middleware/request_logging.py:210 in private method `_sanitize_data`:
        D407: Missing dashed underline after section ('Args')
src/presentation/api/middleware/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/presentation/api/models/standard_responses.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/models/standard_responses.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:1 at module level:
        D400: First line should end with a period (not 's')
src/presentation/api/models/standard_responses.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 's')
src/presentation/api/models/standard_responses.py:13 in public class `ResponseStatus`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:22 in public class `ResponseCode`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:39 in public class `StandardAPIResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:39 in public class `StandardAPIResponse`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/models/standard_responses.py:39 in public class `StandardAPIResponse`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:67 in public nested class `Config`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:74 in public class `SuccessResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:81 in public class `ErrorResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:88 in public class `ChildSafetyResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:88 in public class `ChildSafetyResponse`:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/models/standard_responses.py:88 in public class `ChildSafetyResponse`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:108 in public class `TeddyBearResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:125 in public class `AuthenticationResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:136 in public class `PaginatedResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:147 in public class `HealthCheckResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:168 in public class `ValidationErrorDetail`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:180 in public class `ValidationErrorResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:188 in public class `VoiceProcessingResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:203 in public class `ConversationResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/standard_responses.py:221 in public function `create_success_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:221 in public function `create_success_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:221 in public function `create_success_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:221 in public function `create_success_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:247 in public function `create_error_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:247 in public function `create_error_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:247 in public function `create_error_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:247 in public function `create_error_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:277 in public function `create_child_safety_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:277 in public function `create_child_safety_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:277 in public function `create_child_safety_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:277 in public function `create_child_safety_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:314 in public function `create_teddy_bear_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:314 in public function `create_teddy_bear_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:314 in public function `create_teddy_bear_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:314 in public function `create_teddy_bear_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:353 in public function `create_paginated_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:353 in public function `create_paginated_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:353 in public function `create_paginated_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:353 in public function `create_paginated_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:392 in public function `create_voice_processing_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:392 in public function `create_voice_processing_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:392 in public function `create_voice_processing_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:392 in public function `create_voice_processing_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/standard_responses.py:430 in public function `create_conversation_response`:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/standard_responses.py:430 in public function `create_conversation_response`:
        D413: Missing blank line after last section ('Returns')
src/presentation/api/models/standard_responses.py:430 in public function `create_conversation_response`:
        D407: Missing dashed underline after section ('Returns')
src/presentation/api/models/standard_responses.py:430 in public function `create_conversation_response`:
        D406: Section name should end with a newline ('Returns', not 'Returns:')
src/presentation/api/models/validation_models.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/models/validation_models.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/validation_models.py:1 at module level:
        D400: First line should end with a period (not 'n')
src/presentation/api/models/validation_models.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'n')
src/presentation/api/models/validation_models.py:18 in public class `ChildAgeGroup`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:27 in public class `LanguageCode`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:36 in public class `ContentSafetyLevel`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:44 in public class `MessageRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:101 in public class `ChildRegistrationRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:189 in public class `AudioMessageRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:232 in public class `EmergencyContactRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:272 in public class `ParentConsentRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:320 in public class `HealthCheckRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:336 in public class `PaginationRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:377 in public class `FileUploadRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:445 in public class `ConversationRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:471 in public class `APIResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:483 in public class `LoginRequest`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:483 in public class `LoginRequest`:
        D204: 1 blank line required after class docstring (found 0)
src/presentation/api/models/validation_models.py:489 in public class `LoginResponse`:
        D203: 1 blank line required before class docstring (found 0)
src/presentation/api/models/validation_models.py:489 in public class `LoginResponse`:
        D204: 1 blank line required after class docstring (found 0)
src/presentation/api/models/__init__.py:1 at module level:
        D205: 1 blank line required between summary line and description (found 0)
src/presentation/api/models/__init__.py:1 at module level:
        D213: Multi-line docstring summary should start at the second line
src/presentation/api/models/__init__.py:1 at module level:
        D400: First line should end with a period (not '(')
src/presentation/api/models/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not '(')
src/presentation/api/websocket/__init__.py:1 at module level:
        D400: First line should end with a period (not 'e')
src/presentation/api/websocket/__init__.py:1 at module level:
        D415: First line should end with a period, question mark, or exclamation point (not 'e')
src/presentation/dependencies/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/presentation/schemas/esp32_schemas.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/schemas/esp32_schemas.py:6 in public class `ESP32AudioRequestSchema`:
        D101: Missing docstring in public class
src/presentation/schemas/esp32_schemas.py:13 in public class `ESP32TextResponseSchema`:
        D101: Missing docstring in public class
src/presentation/schemas/parent_schemas.py:1 at module level:
        D100: Missing docstring in public module
src/presentation/schemas/parent_schemas.py:6 in public class `ChildProfileCreateSchema`:
        D101: Missing docstring in public class
src/presentation/schemas/parent_schemas.py:12 in public class `ChildProfileUpdateSchema`:
        D101: Missing docstring in public class
src/presentation/schemas/parent_schemas.py:17 in public class `ChildProfileResponseSchema`:
        D101: Missing docstring in public class
src/presentation/schemas/parent_schemas.py:23 in public nested class `Config`:
        D106: Missing docstring in public nested class
src/presentation/schemas/__init__.py:1 at module level:
        D104: Missing docstring in public package
src/presentation/websocket/__init__.py:1 at module level:
        D104: Missing docstring in public package

```

⏱️ الوقت المستغرق: 32.63 ثانية


---

