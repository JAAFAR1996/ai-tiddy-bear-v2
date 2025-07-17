from typing import Any, Dict, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.application.dto.child_data import ChildData
from src.application.dto.story_response import StoryResponse
from src.application.use_cases.generate_dynamic_story import (
    GenerateDynamicStoryUseCase,
)
from src.application.use_cases.manage_child_profile import (
    ManageChildProfileUseCase,
)
from src.infrastructure.dependencies import (
    get_generate_dynamic_story_use_case,
    get_manage_child_profile_use_case,
)
from src.infrastructure.security.coppa import get_consent_manager
from src.infrastructure.security.error_handler import get_secure_error_handler
from src.infrastructure.security.real_auth_service import (
    UserInfo,
    get_current_parent,
)

router = APIRouter()

# --- Pydantic Models ---


class CreateChildRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z\s\u0600-\u06FF]+$",
        description="Child's name (letters and spaces only, Arabic/English)",
    )
    age: int = Field(
        ...,
        ge=3,
        le=13,
        description="Child's age (COPPA compliance: 3-13 years)",
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Child preferences (validated dictionary)",
    )


class UpdateChildRequest(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z\s\u0600-\u06FF]+$",
        description="Updated child's name (optional)",
    )
    age: Optional[int] = Field(
        None,
        ge=3,
        le=13,
        description="Updated child's age (COPPA compliance: 3-13 years)",
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="Updated child preferences (optional)"
    )


class ConsentRequest(BaseModel):
    consent_types: List[str] = Field(
        ...,
        description="List of consent types to grant",
        example=["data_collection", "voice_recording", "usage_analytics"],
    )
    verification_method: str = Field(
        "email",
        pattern="^(email|sms|phone)$",
        description="Method used for verification",
    )
    verification_code: str = Field(
        ...,
        min_length=6,
        max_length=10,
        description="Verification code received via chosen method",
    )
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")


class ConsentStatusResponse(BaseModel):
    child_id: str
    data_collection: bool = False
    voice_recording: bool = False
    usage_analytics: bool = False
    safety_monitoring: bool = False
    last_updated: Optional[str] = None
    consent_valid: bool = False


# --- API Endpoints ---


@router.post(
    "/children", response_model=ChildData, status_code=status.HTTP_201_CREATED
)
async def create_child_profile_endpoint(
    request: CreateChildRequest,
    use_case: ManageChildProfileUseCase = Depends(
        get_manage_child_profile_use_case
    ),
) -> ChildData:
    try:
        child_data = await use_case.create_child_profile(
            request.name, request.age, request.preferences
        )
        return child_data
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to create child profile",
        )


@router.get("/children/{child_id}", response_model=ChildData)
async def get_child_profile_endpoint(
    child_id: UUID,
    use_case: ManageChildProfileUseCase = Depends(
        get_manage_child_profile_use_case
    ),
) -> ChildData:
    child_data = await use_case.get_child_profile(child_id)
    if not child_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child not found"
        )
    return child_data


@router.put("/children/{child_id}", response_model=ChildData)
async def update_child_profile_endpoint(
    child_id: UUID,
    request: UpdateChildRequest,
    use_case: ManageChildProfileUseCase = Depends(
        get_manage_child_profile_use_case
    ),
) -> ChildData:
    updated_child = await use_case.update_child_profile(
        child_id, request.name, request.age, request.preferences
    )
    if not updated_child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child not found"
        )
    return updated_child


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child_profile_endpoint(
    child_id: UUID,
    use_case: ManageChildProfileUseCase = Depends(
        get_manage_child_profile_use_case
    ),
) -> None:
    success = await use_case.delete_child_profile(child_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Child not found"
        )
    return


@router.post("/children/{child_id}/story", response_model=StoryResponse)
async def generate_child_story_endpoint(
    child_id: UUID,
    theme: str = "adventure",
    length: str = "short",
    use_case: GenerateDynamicStoryUseCase = Depends(
        get_generate_dynamic_story_use_case
    ),
) -> StoryResponse:
    try:
        story_response = await use_case.execute(child_id, theme, length)
        return story_response
    except ValueError as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_404_NOT_FOUND,
            "Story not found or invalid parameters",
        )
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to generate story",
        )


@router.post("/children/{child_id}/consent/request")
async def request_consent_verification(
    child_id: UUID,
    consent_types: List[str],
    verification_method: str = "email",
    current_user: UserInfo = Depends(get_current_parent),
) -> Dict[str, Any]:
    try:
        consent_manager = get_consent_manager()
        parent_id = current_user.id
        consent_request = await consent_manager.request_parental_consent(
            parent_id=parent_id,
            child_id=str(child_id),
            consent_types=consent_types,
            verification_method=verification_method,
        )
        return {
            "status": "consent_request_sent",
            "request_id": consent_request["request_id"],
            "verification_method": verification_method,
            "message": f"Verification {verification_method} sent to parent",
        }
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to request parental consent",
        )


@router.post("/children/{child_id}/consent/grant")
async def grant_parental_consent(
    child_id: UUID,
    request: ConsentRequest,
    current_user: UserInfo = Depends(get_current_parent),
) -> Dict[str, Any]:
    try:
        consent_manager = get_consent_manager()
        parent_id = current_user.id
        verification_data = {
            "method": request.verification_method,
            "verification_code": request.verification_code,
            "ip_address": request.ip_address,
            "user_agent": request.user_agent,
        }
        granted_consents = []
        for consent_type in request.consent_types:
            consent = await consent_manager.grant_consent(
                parent_id=parent_id,
                child_id=str(child_id),
                consent_type=consent_type,
                verification_data=verification_data,
            )
            granted_consents.append(
                {
                    "consent_id": consent.consent_id,
                    "consent_type": consent_type,
                    "expires_at": consent.expires_at.isoformat(),
                }
            )
        return {
            "status": "consent_granted",
            "child_id": str(child_id),
            "granted_consents": granted_consents,
            "message": "Parental consent successfully granted",
        }
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e, status.HTTP_400_BAD_REQUEST, "Failed to grant parental consent"
        )


@router.get(
    "/children/{child_id}/consent/status", response_model=ConsentStatusResponse
)
async def get_consent_status(child_id: UUID) -> ConsentStatusResponse:
    try:
        consent_manager = get_consent_manager()
        consent_status = await consent_manager.get_child_consent_status(
            str(child_id)
        )
        return ConsentStatusResponse(
            child_id=str(child_id),
            data_collection=consent_status.get("data_collection", False),
            voice_recording=consent_status.get("voice_recording", False),
            usage_analytics=consent_status.get("usage_analytics", False),
            safety_monitoring=consent_status.get("safety_monitoring", False),
            last_updated=consent_status.get("last_updated"),
            consent_valid=consent_status.get("consent_valid", False),
        )
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to retrieve consent status",
        )


@router.delete("/children/{child_id}/consent/{consent_type}")
async def revoke_consent(
    child_id: UUID,
    consent_type: str,
    current_user: UserInfo = Depends(get_current_parent),
) -> Dict[str, Any]:
    try:
        consent_manager = get_consent_manager()
        parent_id = current_user.id
        success = await consent_manager.revoke_consent(
            parent_id=parent_id,
            child_id=str(child_id),
            consent_type=consent_type,
        )
        if success:
            return {
                "status": "consent_revoked",
                "child_id": str(child_id),
                "consent_type": consent_type,
                "message": f"Consent for {consent_type} has been revoked",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consent for {consent_type} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        error_handler = get_secure_error_handler()
        raise error_handler.create_safe_error_response(
            e,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to revoke consent",
        )
