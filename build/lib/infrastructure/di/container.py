"""Dependency Injection Container for Hexagonal Architecture.

This module configures and provides all the necessary services and dependencies for the application,
following the principles of Dependency Injection and Inversion of Control. It uses the
`dependency-injector` library to manage object creation and wiring.

Key Responsibilities:
- Configure providers for all services, repositories, and use cases.
- Manage the lifecycle of singletons and factory providers.
- Wire dependencies into the application's API endpoints and other modules.
- Provide a centralized and predictable way to manage application dependencies.

Design Principles:
- **Separation of Concerns**: The container is responsible for object creation, not business logic.
- **Loose Coupling**: Components are decoupled from the concrete implementations of their dependencies.
- **Testability**: Dependencies can be easily mocked or replaced for testing purposes.
"""
import logging
import sys
from typing import Any

from dependency_injector import containers, providers

# Settings
from src.infrastructure.config.settings import get_settings

# Container components
from .di_components.service_factory import ServiceFactory
from .di_components.wiring_config import FullWiringConfig

# Infrastructure Services
from src.infrastructure.caching.redis_cache import RedisCache
from src.infrastructure.logging_config import get_logger
from src.infrastructure.messaging.kafka_event_bus import KafkaEventBus
from src.infrastructure.pagination import PaginationService
from src.infrastructure.persistence.conversation_repository import (
    AsyncSQLAlchemyConversationRepo,
)
from src.domain.interfaces.conversation_repository import IConversationRepository # Import the interface
from src.infrastructure.persistence.kafka_event_store import KafkaEventStore
from src.infrastructure.persistence.postgres_event_store import PostgresEventStore
from src.infrastructure.read_models.child_profile_read_model import (
    ChildProfileReadModelStore,
)
from src.infrastructure.repositories.event_sourced_child_repository import (
    EventSourcedChildRepository,
)
from src.infrastructure.security.hardening.coppa_compliance import (
    ProductionCOPPACompliance,
)
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.security.rate_limiter_service import RateLimiterService
from src.infrastructure.security.safety_monitor_service import SafetyMonitorService
from src.infrastructure.security.token_service import TokenService
from src.infrastructure.config.startup_validator import StartupValidator
from src.common.constants import EventStoreType # Import the new Enum

# Application Services
from src.application.event_handlers.child_profile_event_handlers import (
    ChildProfileEventHandlers,
)
from src.application.services.ai_orchestration_service import AIOrchestrationService
from src.application.services.audio_processing_service import AudioProcessingService
from src.application.services.conversation_service import ConversationService
from src.application.services.dynamic_content_service import DynamicContentService
from src.application.services.dynamic_story_service import DynamicStoryService
from src.application.services.esp32_device_service import ESP32DeviceService
from src.application.services.federated_learning_service import FederatedLearningService
from src.application.interfaces.ai_provider import AIProvider # Import the AIProvider interface

# Use Cases
from src.application.use_cases.generate_ai_response import GenerateAIResponseUseCase
from src.application.use_cases.generate_dynamic_story import GenerateDynamicStoryUseCase
from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.application.use_cases.process_esp32_audio import ProcessESP32AudioUseCase

# Domain Events
from src.domain.events.child_profile_updated import ChildProfileUpdated
from src.domain.events.child_registered import ChildRegistered

# Presentation Layer Components
from src.presentation.api.endpoints.children.compliance import (
    COPPAIntegration,
    ComplianceValidator,
    DataRetentionManager,
    ParentalConsentManager,
)
from src.presentation.api.endpoints.children.operations import (
    ChildDataTransformer,
    ChildOperations,
    ChildValidationService,
)

logger = get_logger(__name__, component="DI_Container")
class Container(containers.DeclarativeContainer):
    """Dependency injection container following Hexagonal Architecture principles."""
    # Configuration
    settings = providers.Singleton(get_settings)
    wiring_config = containers.WiringConfiguration(modules=FullWiringConfig.modules)
    # Startup Validator
    startup_validator = providers.Singleton(StartupValidator, settings=settings)
    # Infrastructure: Core Services (Singletons)
    # These services are instantiated once and shared across the application, suitable for stateless or globally shared resources.
    service_factory = providers.Singleton(ServiceFactory, settings=settings)

    # Database session factory
    # We use providers.Factory to ensure a new session is created each time it's called,
    # ensuring thread safety and proper resource management per request.
    database_manager = providers.Singleton(service_factory.provided.create_database, settings=settings)
    db_session_factory = providers.Factory(database_manager.provided.get_session)

    redis_cache = providers.Singleton(
        RedisCache, redis_url=settings.provided.redis.REDIS_URL
    )
    event_bus = providers.Singleton(
        KafkaEventBus,
        bootstrap_servers=settings.provided.kafka.KAFKA_BOOTSTRAP_SERVERS,
        schema_registry_url=settings.provided.kafka.SCHEMA_REGISTRY_URL,
    )
    event_store = providers.Selector(
        lambda settings_instance: (
            EventStoreType.KAFKA if settings_instance.kafka.KAFKA_ENABLED else EventStoreType.POSTGRES
        ),
        settings_instance=settings,
        kafka=providers.Singleton(KafkaEventStore, settings=settings),
        postgres=providers.Singleton(
            PostgresEventStore, db_session_factory=db_session_factory
        ),
    )

    # Infrastructure: Security Services (Singletons)
    # Security services are typically stateless or manage global state (e.g., rate limits),
    # making Singleton suitable for efficiency and consistent policy enforcement.
    password_hasher = providers.Singleton(
        PasswordHasher, settings=settings.provided.security
    )
    token_service = providers.Singleton(
        TokenService, settings=settings.provided.security
    )
    rate_limiter = providers.Singleton(
        RateLimiterService, settings=settings.provided.security
    )
    safety_monitor = providers.Singleton(SafetyMonitorService)

    # Infrastructure: Repositories (Factories)
    # Repositories interact with database sessions and should be created per request
    # to ensure isolated transactions and prevent state leakage across requests.
    child_repository = providers.Factory(
        EventSourcedChildRepository,
        event_store=event_store,
    )
    conversation_repository: providers.Factory[IConversationRepository] = providers.Factory(
        AsyncSQLAlchemyConversationRepo, # Concrete implementation
        session=db_session_factory,
    )

    # Infrastructure: Read Models (Singletons)
    # Read models typically hold cached or aggregated data and can be shared globally for performance.
    child_profile_read_model_store = providers.Singleton(ChildProfileReadModelStore)

    # Application: Event Handlers (Factories)
    # Event handlers process specific events and might have internal state tied to the event context,
    # making Factory suitable to ensure independent processing of each event.
    child_profile_event_handlers = providers.Factory(
        ChildProfileEventHandlers,
        read_model_store=child_profile_read_model_store,
    )

    # Application: Core Services (Factories)
    # These services contain business logic that might operate on request-specific data or interact
    # with other Factory-provided dependencies, thus requiring a new instance per request.
    audio_processing_service = providers.Factory(
        AudioProcessingService,
        speech_processor=service_factory.provided.create_speech_processor,
        safety_monitor=safety_monitor,
        tts_service=service_factory.provided.create_tts_service,
    )
    conversation_service = providers.Factory(
        ConversationService,
        conversation_repo=conversation_repository,
    )
    ai_orchestration_service: providers.Factory[AIOrchestrationService] = providers.Factory(
        AIOrchestrationService,
        ai_provider=providers.Factory(service_factory.provided.create_openai_client), # Concrete implementation via factory
        safety_monitor=safety_monitor,
        conversation_service=conversation_service,
        tts_service=service_factory.provided.create_tts_service,
    )
    dynamic_content_service: providers.Factory[DynamicContentService] = providers.Factory(
        DynamicContentService,
        openai_client=providers.Factory(service_factory.provided.create_openai_client), # Concrete implementation via factory
    )
    dynamic_story_service: providers.Factory[DynamicStoryService] = providers.Factory(
        DynamicStoryService,
        ai_provider=providers.Factory(service_factory.provided.create_openai_client), # Concrete implementation via factory
    )
    esp32_device_service = providers.Factory(
        ESP32DeviceService,
        event_bus=event_bus,
    )
    # Federated learning service could be Singleton if its state is globally aggregated,
    # or Factory if it processes data per-request/per-batch. Assuming global aggregation.
    federated_learning_service = providers.Singleton(
        FederatedLearningService,
        event_bus=event_bus,
    )

    # Application: Use Cases (Factories)
    # Use cases orchestrate application services and often encapsulate a single business operation,
    # making Factory suitable to ensure each operation is independent.
    process_esp32_audio_use_case = providers.Factory(
        ProcessESP32AudioUseCase,
        audio_processing_service=audio_processing_service,
        ai_orchestration_service=ai_orchestration_service,
        conversation_service=conversation_service,
        child_repository=child_repository,
    )
    manage_child_profile_use_case = providers.Factory(
        ManageChildProfileUseCase,
        child_repository=child_repository,
        child_profile_read_model_store=child_profile_read_model_store,
        event_bus=event_bus,
    )
    generate_ai_response_use_case = providers.Factory(
        GenerateAIResponseUseCase,
        ai_orchestration_service=ai_orchestration_service,
        audio_processing_service=audio_processing_service,
    )
    generate_dynamic_story_use_case = providers.Factory(
        GenerateDynamicStoryUseCase,
        dynamic_story_service=dynamic_story_service,
        child_repository=child_repository,
    )

    # Presentation: API Endpoint Services (Singletons)
    # These services typically handle presentation logic, often stateless or managing UI-related global state,
    # making Singleton appropriate for shared utility and efficiency.
    pagination_service = providers.Singleton(PaginationService)
    coppa_compliance_service = providers.Singleton(
        ProductionCOPPACompliance, settings=settings.provided.privacy
    )
    coppa_integration_service = providers.Singleton(
        COPPAIntegration,
        coppa_compliance_service=coppa_compliance_service,
        settings=settings.provided.privacy,
    )
    parental_consent_manager_service = providers.Singleton(
        ParentalConsentManager,
        coppa_compliance_service=coppa_compliance_service,
    )
    data_retention_manager_service = providers.Singleton(
        DataRetentionManager,
        coppa_compliance_service=coppa_compliance_service,
    )
    compliance_validator_service = providers.Singleton(
        ComplianceValidator,
        settings=settings.provided.application,
    )
    child_operations_service = providers.Singleton(
        ChildOperations,
        manage_child_profile_use_case=manage_child_profile_use_case,
        coppa_compliance_service=coppa_compliance_service,
        pagination_service=pagination_service,
    )
    child_validation_service = providers.Singleton(
        ChildValidationService,
        coppa_compliance_service=coppa_compliance_service,
    )
    child_data_transformer_service = providers.Singleton(ChildDataTransformer)
    # Initialization Logic
    init_event_subscriptions = providers.Callable(
        lambda bus, handlers: _setup_event_subscriptions(bus, handlers),
        bus=event_bus,
        handlers=child_profile_event_handlers,
    )
def _setup_event_subscriptions(
    event_bus: KafkaEventBus, event_handlers: ChildProfileEventHandlers
) -> None:
    """
    Subscribes event handlers to corresponding events on the event bus.
    This function centralizes event subscription logic and provides robust error handling.
    """
    subscriptions = {
        ChildRegistered: event_handlers.handle_child_registered,
        ChildProfileUpdated: event_handlers.handle_child_profile_updated,
    }
    for event, handler in subscriptions.items():
        try:
            event_bus.subscribe(event, handler)
            logger.info(f"Successfully subscribed handler to {event.__name__}")
        except AttributeError as e:
            logger.error(
                f"Failed to subscribe to {event.__name__}: Handler method not found.",
                exc_info=True,
            )
            raise RuntimeError(
                f"Event subscription setup failed for {event.__name__}"
            ) from e
        except ConnectionError as e:
            logger.error(
                f"Failed to connect to event bus for {event.__name__} subscription.",
                exc_info=True,
            )
            raise RuntimeError(
                "Event bus connection failed during subscription."
            ) from e
        except Exception as e: # Catch any other unexpected errors
            logger.critical(
                f"An unexpected error occurred while subscribing to {event.__name__}: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Unhandled exception during event subscription for {event.__name__}"
            ) from e
    logger.info("All event subscriptions initialized successfully.")
# Singleton container instance for application-wide use
container = Container()
# Export for easy import
__all__ = ["Container", "container"]