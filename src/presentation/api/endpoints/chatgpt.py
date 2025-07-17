"""ChatGPT API endpoints للمحادثة مع الأطفال"""
from datetime import datetime
from typing import Dict, Any, Optional
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# Production imports - fail fast with proper exceptions
try:
    from pydantic import BaseModel
    from fastapi import APIRouter, HTTPException, Depends, status
except ImportError as e:
    logger.error(f"CRITICAL ERROR: Core dependencies missing: {e}")
    logger.error("Install required dependencies: pip install pydantic fastapi")
    raise ImportError(f"Missing core dependencies: {e}") from e

# Import services with proper error handling
try:
    from src.infrastructure.ai.real_ai_service import ProductionAIService
from src.application.services.ai_orchestration_service import AIOrchestrationService
from src.infrastructure.di.container import container

# Request/Response Models
class ChatRequest(BaseModel):
    child_id: str
    message: str
    child_profile: Dict[str, Any]

class StoryRequest(BaseModel):
    child_id: str
    theme: str
    child_profile: Dict[str, Any]

class QuestionRequest(BaseModel):
    child_id: str
    question: str
    child_profile: Dict[str, Any]

class ChatResponse(BaseModel):
    response: str
    emotion: str
    safe: bool
    compliant: bool
    timestamp: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, ai_orchestration_service: AIOrchestrationService = Depends(container.ai_orchestration_service)):
    """دردشة مع AI مع ضمانات الأمان"""
    try:
        # Extract child info from profile
        child_name = request.child_profile.get("name", "Child")
        child_age = request.child_profile.get("age", 7)
        preferences = request.child_profile.get("preferences", {})
        
        # Generate AI response
        ai_response = await ai_orchestration_service.generate_response(
            user_message=request.message,
            child_age=child_age,
            child_name=child_name,
            preferences=preferences
        )
        
        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service temporarily unavailable"
        )

@router.post("/story", response_model=ChatResponse)
async def generate_story(request: StoryRequest, ai_orchestration_service: AIOrchestrationService = Depends(container.ai_orchestration_service)):
    """توليد قصة مخصصة للطفل"""
    try:
        # Extract child info from profile
        child_name = request.child_profile.get("name", "Child")
        child_age = request.child_profile.get("age", 7)
        preferences = request.child_profile.get("preferences", {})
        
        # Create story prompt
        story_prompt = f"Tell me a story about {request.theme}"
        
        # Generate AI story
        ai_response = await ai_orchestration_service.generate_response(
            user_message=story_prompt,
            child_age=child_age,
            child_name=child_name,
            preferences=preferences
        )
        
        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Story generation service temporarily unavailable"
        )

@router.post("/question", response_model=ChatResponse)
async def answer_question(request: QuestionRequest, ai_orchestration_service: AIOrchestrationService = Depends(container.ai_orchestration_service)):
    """الإجابة على أسئلة الطفل"""
    try:
        # Extract child info from profile
        child_name = request.child_profile.get("name", "Child")
        child_age = request.child_profile.get("age", 7)
        preferences = request.child_profile.get("preferences", {})
        
        # Generate AI answer
        ai_response = await ai_orchestration_service.generate_response(
            user_message=request.question,
            child_age=child_age,
            child_name=child_name,
            preferences=preferences
        )
        
        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question answering service temporarily unavailable"
        )

@router.get("/suggestions/{child_id}")
async def get_conversation_suggestions(child_id: str, child_age: int = 6):
    """اقتراحات محادثة مناسبة للعمر"""
    age_suggestions = {
        3: [
            "Tell me about your favorite animal",
            "What color do you like most?",
            "Do you want to hear a story?",
            "Let's count to ten together!"
        ],
        4: [
            "What's your favorite toy?",
            "Do you like to draw pictures?",
            "Tell me about your family",
            "What sounds do animals make?"
        ],
        5: [
            "What did you learn at school today?",
            "Do you have a best friend?",
            "What's your favorite book?",
            "Let's talk about shapes and colors!"
        ],
        6: [
            "What do you want to be when you grow up?",
            "Tell me about your favorite game",
            "Do you like nature and animals?",
            "What makes you happy?"
        ]
    }
    
    suggestions = age_suggestions.get(child_age, age_suggestions[6])
    
    return {
        "suggestions": suggestions,
        "age_appropriate": True,
        "timestamp": datetime.now().isoformat()
    }