from datetime import datetime
from typing import Any
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from src.application.services.ai_orchestration_service import AIOrchestrationService
from src.application.services.conversation_service import ConversationService
from src.application.use_cases.manage_child_profile import ManageChildProfileUseCase
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.real_auth_service import ProductionAuthService
from src.infrastructure.security.safety_monitor_service import SafetyMonitorService

logger = get_logger(__name__, component="api")

router = APIRouter(prefix="/conversations", tags=["Conversations"])
security = HTTPBearer()


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: ProductionAuthService = Depends(container.auth_service),
) -> dict[str, Any]:
    """Verify authentication for child conversation access - COPPA compliance required.

    Returns:
        Dict containing authenticated user data including parent verification

    Raises:
        HTTPException: If authentication fails or user not authorized for child data

    """
    try:
        token = credentials.credentials
        payload = await auth_service.verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = payload.get("role", "")
        if user_role not in ["parent", "guardian", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Only parents/guardians can access child conversation data",
            )

        return {
            "user_id": payload.get("sub"),
            "role": user_role,
            "permissions": payload.get("permissions", []),
            "child_ids": payload.get("child_ids", []),  # Children this user can access
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ConversationRequest(BaseModel):
    child_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Child's message",
    )
    message_type: str = Field(default="text", pattern=r"^(text|audio|story_request)$")
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")

    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"

    @field_validator("message")
    def validate_message_content(self, v):
        """Validate message content for child safety."""
        forbidden_words = {"password", "credit card", "address", "phone", "email"}
        if any(word in v.lower() for word in forbidden_words):
            raise ValueError("Message contains inappropriate content")
        return v


class ConversationResponse(BaseModel):
    conversation_id: str
    child_id: str
    response: str
    emotion: str
    safe: bool
    response_type: str
    timestamp: str
    safety_analysis: dict[str, Any]


class ConversationHistory(BaseModel):
    conversation_id: str
    child_id: str
    messages: list[dict[str, Any]]
    started_at: str
    last_message_at: str
    message_count: int
    safety_events: int


@router.post("/", response_model=ConversationResponse)
@inject
async def create_conversation(
    request: ConversationRequest,
    current_user: dict[str, Any] = Depends(get_authenticated_user),
    ai_orchestration_service: AIOrchestrationService = Depends(
        Provide[container.ai_orchestration_service],
    ),
    conversation_service: ConversationService = Depends(
        Provide[container.conversation_service],
    ),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
    safety_monitor: SafetyMonitorService = Depends(Provide[container.safety_monitor]),
):
    """Create a new conversation with the child."""
    try:
        # Validate child access
        child = await manage_child_profile_use_case.get_child(request.child_id)
        if not child or child.parent_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's profile",
            )

        ai_response = await ai_orchestration_service.generate_response(
            user_message=request.message,
            child_age=child.age,
            child_name=child.name,
            preferences=child.preferences.dict() if child.preferences else {},
        )

        # Generate conversation ID with UUID
        conversation_id = str(uuid4())

        # Save conversation to history
        await conversation_service.add_message_to_conversation(
            conversation_id=conversation_id,
            child_id=request.child_id,
            user_message=request.message,
            ai_response=ai_response.content,
            message_type=request.message_type,
            language=request.language,
            safety_analysis=ai_response.safety_analysis,
        )

        # Record safety event
        await safety_monitor.record_safety_event(
            child_id=request.child_id,
            event_type="conversation_message",
            details={
                "conversation_id": conversation_id,
                "message_type": request.message_type,
                "safe": ai_response.age_appropriate,
                "safety_score": ai_response.safety_score,
            },
            severity="info" if ai_response.age_appropriate else "warning",
        )

        return ConversationResponse(
            conversation_id=conversation_id,
            child_id=request.child_id,
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            response_type=ai_response.response_type,
            timestamp=datetime.now().isoformat(),
            safety_analysis={
                "safe": ai_response.age_appropriate,
                "safety_score": ai_response.safety_score,
                "moderation_flags": ai_response.moderation_flags,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation. Please try again.",
        )


@router.get("/{child_id}/history", response_model=list[ConversationHistory])
@inject
async def get_conversation_history(
    child_id: str,
    limit: int = 10,
    current_user: dict[str, Any] = Depends(get_authenticated_user),
    conversation_service: ConversationService = Depends(
        Provide[container.conversation_service],
    ),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
):
    """Get conversation history for the child."""
    try:
        # Validate child access
        child = await manage_child_profile_use_case.get_child(child_id)
        if not child or child.parent_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's profile",
            )

        history = await conversation_service.get_conversation_history(child_id, limit)

        return [
            ConversationHistory(
                conversation_id=h.conversation_id,
                child_id=h.child_id,
                messages=h.messages,
                started_at=h.started_at,
                last_message_at=h.last_message_at,
                message_count=h.message_count,
                safety_events=h.safety_events,
            )
            for h in history
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history. Please try again.",
        )


@router.get("/{conversation_id}", response_model=ConversationHistory)
@inject
async def get_conversation(
    conversation_id: str,
    current_user: dict[str, Any] = Depends(get_authenticated_user),
    conversation_service: ConversationService = Depends(
        Provide[container.conversation_service],
    ),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
):
    """Get a specific conversation."""
    try:
        # Validate child access (assuming conversation_id implies child_id)
        # In a real app, you'd get child_id from the conversation record
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        child = await manage_child_profile_use_case.get_child(conversation.child_id)
        if not child or child.parent_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        return ConversationHistory(
            conversation_id=conversation.conversation_id,
            child_id=conversation.child_id,
            messages=conversation.messages,
            started_at=conversation.started_at,
            last_message_at=conversation.last_message_at,
            message_count=conversation.message_count,
            safety_events=conversation.safety_events,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation. Please try again.",
        )


@router.post("/story-request", response_model=ConversationResponse)
@inject
async def request_story(
    request: ConversationRequest,
    current_user: dict[str, Any] = Depends(get_authenticated_user),
    ai_orchestration_service: AIOrchestrationService = Depends(
        Provide[container.ai_orchestration_service],
    ),
    conversation_service: ConversationService = Depends(
        Provide[container.conversation_service],
    ),
    manage_child_profile_use_case: ManageChildProfileUseCase = Depends(
        Provide[container.manage_child_profile_use_case],
    ),
    safety_monitor: SafetyMonitorService = Depends(Provide[container.safety_monitor]),
):
    """Request a custom story for the child."""
    try:
        # Validate child access
        child = await manage_child_profile_use_case.get_child(request.child_id)
        if not child or child.parent_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child's profile",
            )

        story_prompt = f"Tell me a story about {request.message}"
        ai_response = await ai_orchestration_service.generate_response(
            user_message=story_prompt,
            child_age=child.age,
            child_name=child.name,
            preferences=child.preferences.dict() if child.preferences else {},
        )

        # Generate conversation ID with UUID
        conversation_id = str(uuid4())

        # Save story request to history
        await conversation_service.add_message_to_conversation(
            conversation_id=conversation_id,
            child_id=request.child_id,
            user_message=story_prompt,
            ai_response=ai_response.content,
            message_type="story_request",
            language=request.language,
            safety_analysis=ai_response.safety_analysis,
        )

        # Record safety event
        await safety_monitor.record_safety_event(
            child_id=request.child_id,
            event_type="story_request",
            details={
                "conversation_id": conversation_id,
                "message_type": "story_request",
                "safe": ai_response.age_appropriate,
                "safety_score": ai_response.safety_score,
            },
            severity="info" if ai_response.age_appropriate else "warning",
        )

        return ConversationResponse(
            conversation_id=conversation_id,
            child_id=request.child_id,
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            response_type="story",
            timestamp=datetime.now().isoformat(),
            safety_analysis={
                "safe": ai_orchestration_service.age_appropriate,
                "safety_score": ai_orchestration_service.safety_score,
                "moderation_flags": ai_orchestration_service.moderation_flags,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate story. Please try again.",
        )
