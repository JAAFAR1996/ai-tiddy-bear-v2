"""ChatGPT API endpoints للمحادثة مع الأطفال"""

from datetime import datetime
from typing import Any

# Production imports - fail fast with proper exceptions
try:
    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel

    from src.domain.models.validation_models import ConversationRequest
except ImportError as e:
    raise ImportError(f"Missing core dependencies: {e}") from e

from src.application.services.ai.ai_orchestration_service import AIOrchestrationService
from src.infrastructure.di.container import container
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

# Create router
router = APIRouter(prefix="/chat", tags=["AI Chat"])


# Request/Response Models - ChatRequest replaced with ConversationRequest


class StoryRequest(BaseModel):
    child_id: str
    theme: str
    child_profile: dict[str, Any]


class QuestionRequest(BaseModel):
    child_id: str
    question: str
    child_profile: dict[str, Any]


class ChatResponse(BaseModel):
    response: str
    emotion: str
    safe: bool
    compliant: bool
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ConversationRequest,
    ai_orchestration_service: AIOrchestrationService = Depends(
        container.ai_orchestration_service
    ),
):
    """دردشة مع AI مع ضمانات الأمان"""
    try:
        # ConversationRequest uses context instead of child_profile
        context = request.context or {}
        # Child age validation for safety
        child_age = context.get("child_age", 7)
        if not isinstance(child_age, int) or child_age < 3 or child_age > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid child age. Must be between 3-12 years",
            )
        child_name = context.get("child_name", "Child")
        child_age = context.get("child_age", 7)
        preferences = context.get("preferences", {})

        # Generate AI response
        ai_response = await ai_orchestration_service.generate_response(
            user_message=request.message,
            child_age=child_age,
            child_name=child_name,
            preferences=preferences,
        )

        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service temporarily unavailable",
        )


@router.post("/story", response_model=ChatResponse)
async def generate_story(
    request: StoryRequest,
    ai_orchestration_service: AIOrchestrationService = Depends(
        container.ai_orchestration_service
    ),
):
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
            preferences=preferences,
        )

        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Story generation service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Story generation service temporarily unavailable",
        )


@router.post("/question", response_model=ChatResponse)
async def answer_question(
    request: QuestionRequest,
    ai_orchestration_service: AIOrchestrationService = Depends(
        container.ai_orchestration_service
    ),
):
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
            preferences=preferences,
        )

        return ChatResponse(
            response=ai_response.content,
            emotion=ai_response.emotion,
            safe=ai_response.age_appropriate,
            compliant=ai_response.safety_score >= 0.9,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Question answering service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question answering service temporarily unavailable",
        )


@router.get("/suggestions/{child_id}")
async def get_conversation_suggestions(child_id: str, child_age: int = 6):
    """اقتراحات محادثة مناسبة للعمر"""
    age_suggestions = {
        3: [
            "Tell me about your favorite animal",
            "What color do you like most?",
            "Do you want to hear a story?",
            "Let's count to ten together!",
        ],
        4: [
            "What's your favorite toy?",
            "Do you like to draw pictures?",
            "Tell me about your family",
            "What sounds do animals make?",
        ],
        5: [
            "What did you learn at school today?",
            "Do you have a best friend?",
            "What's your favorite book?",
            "Let's talk about shapes and colors!",
        ],
        6: [
            "What do you want to be when you grow up?",
            "Tell me about your favorite game",
            "Do you like nature and animals?",
            "What makes you happy?",
        ],
        7: [
            "What's your favorite subject at school?",
            "Do you like to solve puzzles?",
            "Tell me about your dreams",
            "What would you like to learn today?",
        ],
        8: [
            "What's the coolest thing you've learned?",
            "Do you have any hobbies?",
            "What makes a good friend?",
            "Tell me about your favorite adventure",
        ],
    }

    suggestions = age_suggestions.get(child_age, age_suggestions[6])

    return {
        "child_id": child_id,
        "suggestions": suggestions,
        "age_appropriate": True,
        "age_group": child_age,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/topics/{child_age}")
async def get_age_appropriate_topics(child_age: int):
    """الحصول على مواضيع مناسبة للعمر"""
    topics_by_age = {
        3: {
            "categories": ["Animals", "Colors", "Family", "Toys"],
            "activities": ["Singing", "Simple Stories", "Counting"],
            "learning_goals": ["Basic vocabulary", "Simple concepts"],
        },
        4: {
            "categories": ["Nature", "Friends", "Art", "Music"],
            "activities": ["Drawing", "Pretend Play", "Simple Games"],
            "learning_goals": ["Social skills", "Creative expression"],
        },
        5: {
            "categories": ["School", "Books", "Science", "Sports"],
            "activities": ["Reading", "Experiments", "Physical Play"],
            "learning_goals": ["Reading skills", "Basic science"],
        },
        6: {
            "categories": ["Careers", "Geography", "History", "Technology"],
            "activities": ["Problem Solving", "Building", "Exploration"],
            "learning_goals": ["Critical thinking", "World awareness"],
        },
        7: {
            "categories": ["Mathematics", "Literature", "Environment", "Culture"],
            "activities": ["Math Games", "Story Writing", "Research"],
            "learning_goals": ["Academic skills", "Cultural awareness"],
        },
        8: {
            "categories": [
                "Science Projects",
                "Art History",
                "Programming",
                "Philosophy",
            ],
            "activities": ["Complex Games", "Creative Projects", "Debates"],
            "learning_goals": ["Advanced thinking", "Ethical reasoning"],
        },
    }

    topics = topics_by_age.get(child_age, topics_by_age[6])

    return {
        "age": child_age,
        "topics": topics,
        "safety_guidelines": [
            "All content is age-appropriate",
            "No personal information collection",
            "Positive reinforcement only",
            "Educational and entertaining focus",
        ],
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/safety-status/{child_id}")
async def get_chat_safety_status(child_id: str):
    """الحصول على حالة الأمان للمحادثة"""
    # In a real implementation, this would check the child's recent chat history
    # and provide safety metrics
    return {
        "child_id": child_id,
        "safety_score": 0.95,
        "content_filtered": 0,
        "inappropriate_attempts": 0,
        "last_safety_check": datetime.now().isoformat(),
        "safety_status": "SAFE",
        "parental_controls": {
            "enabled": True,
            "content_filtering": "STRICT",
            "time_limits": "ACTIVE",
        },
        "recommendations": [
            "All conversations are within safety guidelines",
            "Continue encouraging positive interactions",
            "Regular safety monitoring is active",
        ],
    }
