"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.infrastructure.di.fastapi_dependencies import (
"""

Example of simplified dependency injection in endpoints
"""
    get_current_parent,
    get_child_service,
    get_conversation_service,
    get_ai_service,
    verify_child_access)
from src.presentation.api.decorators.rate_limit import moderate_limit, strict_limit

router = APIRouter(prefix="/api/v1", tags=["example"])

# Request/Response Models
class ChatRequest(BaseModel):
    child_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    child_safe: bool
    interaction_id: str

# Example Endpoints
@router.post("/chat", response_model=ChatResponse)
@moderate_limit()  # 30 requests per minute
async def chat_with_teddy(
    request: ChatRequest,
    current_parent: Dict[str, Any] = Depends(get_current_parent),
    conversation_service = Depends(get_conversation_service),
    _: bool = Depends(lambda: verify_child_access(request.child_id))):
    """
    Send a message to AI Teddy Bear.
    """
    try:
        # Process chat message
        result = await conversation_service.process_message(
            child_id=request.child_id,
            message=request.message,
            parent_id=current_parent["user_id"]
        )
        
        return ChatResponse(
            response=result["response"],
            child_safe=result["is_safe"],
            interaction_id=result["interaction_id"]
        )
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/children")
@moderate_limit()
async def get_my_children(
    current_parent: Dict[str, Any] = Depends(get_current_parent),
    child_service = Depends(get_child_service)) -> List[Dict[str, Any]]:
    """
    Get all children for the current parent.
    """
    children = await child_service.get_children_by_parent(
        parent_id=current_parent["user_id"]
    )
    
    return [
        {
            "id": child.id,
            "name": child.name,
            "age": child.age,
            "avatar": child.avatar_url
        }
        for child in children
    ]

@router.post("/children/{child_id}/story")
@strict_limit()  # 5 requests per minute (expensive operation)
async def generate_story(
    child_id: str,
    theme: str,
    current_parent: Dict[str, Any] = Depends(get_current_parent),
    ai_service = Depends(get_ai_service),
    child_service = Depends(get_child_service),
    _: bool = Depends(lambda: verify_child_access(child_id))):
    """
    Generate a personalized story for the child.
    """
    # Get child info
    child = await child_service.get_child(child_id)
    
    # Generate story
    story = await ai_service.generate_story(
        child_name=child.name,
        child_age=child.age,
        theme=theme,
        safety_level="strict"
    )
    
    return {
        "story": story["content"],
        "reading_time": story["estimated_reading_time"],
        "age_appropriate": story["age_appropriate"]
    }

# Example of custom dependency
async def get_child_context(
    child_id: str,
    current_parent: Dict[str, Any] = Depends(get_current_parent),
    child_service = Depends(get_child_service)) -> Dict[str, Any]:
    """
    Custom dependency that provides full child context.
    """
    # Verify access
    await verify_child_access(child_id, current_parent, child_service)
    
    # Get child data
    child = await child_service.get_child(child_id)
    
    # Get recent interactions
    interactions = await child_service.get_recent_interactions(child_id, limit=10)
    
    return {
        "child": child,
        "parent_id": current_parent["user_id"],
        "recent_interactions": interactions,
        "safety_settings": child.safety_settings
    }

@router.get("/children/{child_id}/context")
async def get_child_interaction_context(
    child_id: str,
    context: Dict[str, Any] = Depends(lambda: get_child_context(child_id))):
    """
    Get full context for child interactions.
    """
    return {
        "child_name": context["child"].name,
        "recent_topics": [i.topic for i in context["recent_interactions"]],
        "safety_level": context["safety_settings"]["level"],
        "interaction_limits": context["safety_settings"]["daily_limits"]
    }