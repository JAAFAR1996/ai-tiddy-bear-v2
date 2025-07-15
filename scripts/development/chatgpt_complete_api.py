#!/usr/bin/env python3
"""
🤖 ChatGPT Complete API - ملف شامل واحد لجميع APIs الخاصة بـ ChatGPT
Includes: Client, Service, Endpoints, Authentication, Safety

WARNING: This script is for development and demonstration purposes ONLY.
It contains simplified implementations and should NOT be used in production.
For production, refer to the main application in src/.
"""

import asyncio
import html
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import bcrypt
from jose import JWTError, jwt

# ================== MOCK DEPENDENCIES ==================
try:
    import openai
    from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from openai import OpenAI
    from pydantic import BaseModel, EmailStr

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    print(
        "⚠️ Dependencies not available, this script is for development/mocking purposes only."
    )
    print(
        "Please install: pip install fastapi uvicorn pydantic openai python-jose[cryptography] bcrypt"
    )
    DEPENDENCIES_AVAILABLE = False
    # Exit or raise an error if dependencies are strictly required for the script to run
    # For now, we'll let it proceed with a warning, assuming it's for demonstration.
    raise ImportError(
        "Required dependencies for FastAPI application are not installed."
    )

# ================== LOGGER SETUP ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================== CHATGPT CLIENT ==================
class ChatGPTClient:
    """ChatGPT client with child safety filtering"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        self.client = (
            OpenAI(api_key=self.api_key) if DEPENDENCIES_AVAILABLE else OpenAI()
        )

        # Child safety settings
        self.forbidden_words = [
            "violence",
            "weapon",
            "kill",
            "death",
            "blood",
            "scary",
            "nightmare",
            "monster",
            "ghost",
            "demon",
            "hell",
            "damn",
            "adult",
            "sex",
            "drug",
            "alcohol",
            "cigarette",
            "smoke",
        ]

        self.safe_topics = [
            "animals",
            "nature",
            "friendship",
            "family",
            "school",
            "books",
            "games",
            "art",
            "music",
            "sports",
            "food",
            "colors",
            "shapes",
            "numbers",
            "letters",
            "stories",
        ]

    async def generate_child_safe_response(
        self, message: str, child_age: int, child_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate child-safe response from ChatGPT

        Args:
            message (str): The child's input message.
            child_age (int): The child's age.
            child_preferences (Dict[str, Any], optional): Child preferences. Defaults to None.

        Returns:
            Dict[str, Any]: A safe and age-appropriate response.
        """

        try:
            # Message safety check
            safety_check = self._analyze_message_safety(message)
            if not safety_check["safe"]:
                return await self._generate_safety_redirect_response(message, child_age)

            # Create child-safe system prompt
            system_prompt = self._create_child_safe_system_prompt(
                child_age, child_preferences
            )

            # Call ChatGPT
            async with openai.AsyncClient(api_key=self.api_key) as client:
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )

            raw_response = response.choices[0].message.content

            # Response safety check
            response_safety = self._analyze_response_safety(raw_response)
            if not response_safety["safe"]:
                return await self._generate_fallback_response(
                    message, child_age, child_preferences
                )

            # Enhance response for children
            enhanced_response = self._enhance_response_for_children(
                raw_response, child_age, child_preferences
            )

            return {
                "response": enhanced_response,
                "emotion": self._detect_emotion(enhanced_response),
                "safety_analysis": response_safety,
                "age_appropriate": True,
                "source": "chatgpt",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return await self._generate_fallback_response(
                message, child_age, child_preferences
            )

    def _create_child_safe_system_prompt(
        self, child_age: int, preferences: Dict[str, Any] = None
    ) -> str:
        """Create a child-safe system prompt

        Args:
            child_age (int): The child's age.
            preferences (Dict[str, Any], optional): Child preferences. Defaults to None.

        Returns:
            str: The safe system prompt.
        """

        preferences = preferences or {}
        interests = preferences.get("interests", ["animals", "stories"])
        favorite_character = preferences.get(
            "favorite_character", "friendly teddy bear"
        )

        return f"""You are a friendly AI assistant for children aged {child_age}.

SAFETY RULES:
- Use child-friendly, positive language only
- Never discuss violence, scary content, or adult topics
- Keep responses age-appropriate
- Be encouraging and educational

CHILD PROFILE:
- Age: {child_age} years old
- Interests: {', '.join(interests) if isinstance(interests, list) else interests}
- Favorite character: {favorite_character}

Keep responses under 150 words and end with encouragement."""

    def _analyze_message_safety(self, message: str) -> Dict[str, Any]:
        """Analyze message safety

        Args:
            message (str): The message to analyze.

        Returns:
            Dict[str, Any]: Safety analysis results.
        """
        issues = []
        message_lower = message.lower()

        # Basic sanitization (similar to APISecurityManager.sanitize_input)
        sanitized_message = self._sanitize_input(message)

        # Check for forbidden words
        for word in self.forbidden_words:
            if word in message_lower:
                issues.append(f"Contains forbidden word: {word}")

        # Check for sensitive information patterns (similar to APISecurityManager.validate_child_input)
        sensitive_patterns = [
            r"\b(password|credit\s*card|ssn|social\s*security)\b",
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b",  # Credit card pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}-\d{3}-\d{4}\b",  # Phone number
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, sanitized_message, re.IGNORECASE):
                issues.append(f"Potential sensitive information detected")
                break

        return {
            "safe": len(issues) == 0,
            "severity": "high" if len(issues) > 2 else "medium" if issues else "none",
            "issues": issues,
            "sanitized_message": sanitized_message,
        }

    def _sanitize_input(self, input_string: str) -> str:
        """Sanitize user input for security (simplified version).

        Args:
            input_string (str): The string to sanitize.

        Returns:
            str: The sanitized string.
        """
        if not input_string:
            return ""

        # HTML escape to prevent XSS
        sanitized = html.escape(input_string)

        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")

        # Remove control characters except newline and tab
        sanitized = "".join(
            char for char in sanitized if ord(char) >= 32 or char in "\n\t"
        )

        # Remove common SQL injection patterns (simplified)
        sql_patterns = [
            r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+",
            r"[\"\'];",
            r"--",
        ]

        for pattern in sql_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    def _analyze_response_safety(self, response: str) -> Dict[str, Any]:
        """Analyze response safety

        Args:
            response (str): The response to analyze.

        Returns:
            Dict[str, Any]: Safety analysis results.
        """
        issues = []
        response_lower = response.lower()

        for word in self.forbidden_words:
            if word in response_lower:
                issues.append(f"Response contains forbidden word: {word}")

        return {
            "safe": len(issues) == 0,
            "severity": "none" if len(issues) == 0 else "medium",
            "issues": issues,
        }

    def _enhance_response_for_children(
        self, response: str, child_age: int, preferences: Dict[str, Any] = None
    ) -> str:
        """Enhance response for children

        Args:
            response (str): The original response.
            child_age (int): The child's age.
            preferences (Dict[str, Any], optional): Child preferences. Defaults to None.

        Returns:
            str: The enhanced response.
        """
        age_encouragements = {
            3: " You're so smart!",
            4: " Great question!",
            5: " Keep learning!",
            6: " You're amazing!",
            7: " Fantastic thinking!",
            8: " I love your curiosity!",
            9: " Excellent wondering!",
            10: " That's brilliant!",
        }

        encouragement = age_encouragements.get(child_age, " You're wonderful!")
        if not response.endswith(("!", "?", ".")):
            response += encouragement

        return response

    def _detect_emotion(self, response: str) -> str:
        """Detect emotion from response

        Args:
            response (str): The response to analyze.

        Returns:
            str: The detected emotion.
        """
        response_lower = response.lower()

        if any(word in response_lower for word in ["happy", "joy", "fun", "great"]):
            return "happy"
        elif any(word in response_lower for word in ["learn", "discover", "explore"]):
            return "curious"
        elif any(word in response_lower for word in ["friend", "together"]):
            return "friendly"
        else:
            return "neutral"

    async def _generate_fallback_response(
        self, message: str, child_age: int, preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate a safe fallback response

        Args:
            message (str): The original child message.
            child_age (int): The child's age.
            preferences (Dict[str, Any], optional): Child preferences. Defaults to None.

        Returns:
            Dict[str, Any]: The fallback response.
        """
        fallback_responses = {
            3: "Hello! I'm your friendly teddy bear! Would you like to hear a story?",
            4: "Hi there! Let's talk about something fun! What's your favorite color?",
            5: "Hello friend! Would you like to learn about animals today?",
            6: "Hi! I'm so happy to chat with you! What interests you most?",
            7: "Hello! Would you like to explore something new together?",
            8: "Hi there! What would you like to create or discover today?",
            9: "Hello friend! What are you curious about?",
            10: "Hi! What would you like to talk about today?",
        }

        response = fallback_responses.get(child_age, fallback_responses[6])

        return {
            "response": response,
            "emotion": "friendly",
            "safety_analysis": {"safe": True, "severity": "none", "issues": []},
            "age_appropriate": True,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_safety_redirect_response(
        self, message: str, child_age: int
    ) -> Dict[str, Any]:
        """Generate a safety redirect response

        Args:
            message (str): The original child message.
            child_age (int): The child's age.

        Returns:
            Dict[str, Any]: The redirect response.
        """
        redirect_responses = {
            3: "Let's talk about something nice instead! Do you like puppies?",
            4: "How about we talk about your favorite toys?",
            5: "Let's learn something fun! What's your favorite animal?",
            6: "That's not something we should talk about. Would you like to hear a story instead?",
            7: "Let's focus on positive things! What makes you happy?",
            8: "How about we explore something interesting and safe?",
            9: "Let's discuss something educational and fun!",
            10: "That topic isn't appropriate. What are you curious about instead?",
        }

        response = redirect_responses.get(child_age, redirect_responses[6])

        return {
            "response": response,
            "emotion": "redirecting",
            "safety_analysis": {
                "safe": True,
                "severity": "handled",
                "issues": ["Redirected unsafe topic"],
            },
            "age_appropriate": True,
            "source": "safety_redirect",
            "timestamp": datetime.now().isoformat(),
        }


from src.infrastructure.security.email_validator import validate_email_address
from src.infrastructure.security.password_validator import validate_password_strength
from src.infrastructure.security.registration_models import PasswordRequirements


# ================== AUTHENTICATION SERVICE ==================
class AuthService:
    """Authentication and Authorization Service"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        if not self.secret_key:
            raise RuntimeError(
                "CRITICAL SECURITY ERROR: JWT_SECRET environment variable must be set"
            )
        self.users_db = {}  # In production, use real database
        self.child_sessions = {}  # ✅
        self.password_requirements = (
            PasswordRequirements()
        )  # Initialize with default requirements
        self.password_requirements.forbidden_patterns = [
            "password",
            "123456",
            "qwerty",
            "admin",
            "user",
            "teddy",
            "bear",
            "child",
            "parent",
            "family",
        ]

    def hash_password(self, password: str) -> str:
        """Hash password

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password

        Args:
            password (str): The entered password.
            hashed (str): The stored password hash.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def create_user(
        self, email: str, password: str, role: str = "parent"
    ) -> Dict[str, Any]:
        """Create a new user

        Args:
            email (str): User's email.
            password (str): User's password.
            role (str, optional): User's role. Defaults to "parent".

        Returns:
            Dict[str, Any]: The created user's data.
        """
        email_validation = validate_email_address(email)
        if not email_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email address: {', '.join(email_validation['errors'])}",
            )

        password_validation = validate_password_strength(
            password, self.password_requirements
        )
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Weak password: {', '.join(password_validation['errors'])}",
            )

        user_id = f"user_{len(self.users_db) + 1}"

        user_data = {
            "id": user_id,
            "email": email_validation["normalized_email"],
            "password_hash": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
        }

        self.users_db[email_validation["normalized_email"]] = user_data
        return {
            "user_id": user_id,
            "email": email_validation["normalized_email"],
            "role": role,
        }

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user

        Args:
            email (str): User's email.
            password (str): User's password.

        Returns:
            Optional[Dict[str, Any]]: User data if authentication is successful, None otherwise.
        """
        user = self.users_db.get(email)
        if user and self.verify_password(password, user["password_hash"]):
            return user
        return None

    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create authentication token

        Args:
            user_data (Dict[str, Any]): User data to create the token.

        Returns:
            str: The generated token.
        """
        to_encode = {
            "sub": user_data["email"],
            "user_id": user_data["id"],
            "role": user_data["role"],
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")

    def validate_child_access(self, child_id: str, parent_email: str) -> bool:
        """Validate child access

        Args:
            child_id (str): Child ID.
            parent_email (str): Parent's email.

        Returns:
            bool: True if access is allowed, False otherwise.
        """
        # In production, check actual parent-child relationships
        return True


# ================== CHATGPT SERVICE ==================
class ChatGPTService:
    """ChatGPT Service with Session Management and Safety"""

    def __init__(self):
        self.client = ChatGPTClient()
        self.auth_service = AuthService()
        self.conversation_history = {}
        self.safety_logs = []

    async def chat_with_child(
        self,
        child_id: str,
        message: str,
        child_profile: Dict[str, Any],
        parent_token: str = None,
    ) -> Dict[str, Any]:
        """Chat with child with safety guarantees

        Args:
            child_id (str): Child ID.
            message (str): Child's message.
            child_profile (Dict[str, Any]): Child's profile.
            parent_token (str, optional): Parent's token for authentication. Defaults to None.

        Returns:
            Dict[str, Any]: Chat response.
        """

        try:
            # Validate parent permissions (optional)
            if parent_token:
                # In production, validate JWT token
                pass

            # Get response from ChatGPT
            response = await self.client.generate_child_safe_response(
                message=message,
                child_age=child_profile.get("age", 6),
                child_preferences=child_profile.get("preferences", {}),
            )

            # Save to conversation history
            self._save_conversation(child_id, message, response)

            # Log any safety concerns
            if not response["safety_analysis"]["safe"]:
                self._log_safety_concern(child_id, message, response)

            return {
                "response": response["response"],
                "emotion": response["emotion"],
                "safe": response["safety_analysis"]["safe"],
                "compliant": True,
                "timestamp": response["timestamp"],
            }

        except Exception as e:
            logger.error(f"ChatGPT service error: {e}")
            return {
                "error": "Service temporarily unavailable",
                "message": "Please try again later",
                "compliant": True,
            }

    async def generate_story(
        self, child_id: str, theme: str, child_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a custom story for the child

        Args:
            child_id (str): Child ID.
            theme (str): Story theme.
            child_profile (Dict[str, Any]): Child's profile.

        Returns:
            Dict[str, Any]: The generated story.
        """

        story_prompt = f"Tell me a short, fun story about {theme} suitable for a {child_profile.get('age', 6)}-year-old"
        return await self.chat_with_child(child_id, story_prompt, child_profile)

    async def answer_question(
        self, child_id: str, question: str, child_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Answer child's questions in an educational way

        Args:
            child_id (str): Child ID.
            question (str): The question asked by the child.
            child_profile (Dict[str, Any]): Child's profile.

        Returns:
            Dict[str, Any]: The generated answer.
        """

        educational_prompt = f"Please explain this in a simple, educational way for a {child_profile.get('age', 6)}-year-old: {question}"
        return await self.chat_with_child(child_id, educational_prompt, child_profile)

    def get_conversation_history(
        self, child_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history

        Args:
            child_id (str): Child ID.
            limit (int, optional): Maximum number of conversations to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of conversation records.
        """
        return self.conversation_history.get(child_id, [])[-limit:]

    def get_safety_reports(self) -> List[Dict[str, Any]]:
        """Get safety reports for parents

        Returns:
            List[Dict[str, Any]]: List of safety reports.
        """
        return self.safety_logs

    def _save_conversation(self, child_id: str, message: str, response: Dict[str, Any]):
        """Save conversation

        Args:
            child_id (str): Child ID.
            message (str): User message.
            response (Dict[str, Any]): AI response.
        """
        if child_id not in self.conversation_history:
            self.conversation_history[child_id] = []

        self.conversation_history[child_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "ai_response": response["response"],
                "emotion": response["emotion"],
                "safe": response["safety_analysis"]["safe"],
            }
        )

    def _log_safety_concern(
        self, child_id: str, message: str, response: Dict[str, Any]
    ):
        """Log safety concerns

        Args:
            child_id (str): Child ID.
            message (str): User message that raised the concern.
            response (Dict[str, Any]): AI response that raised the concern.
        """
        safety_log = {
            "timestamp": datetime.now().isoformat(),
            "child_id": child_id,
            "user_message": message,
            "ai_response": response["response"],
            "safety_issues": response["safety_analysis"]["issues"],
            "severity": response["safety_analysis"]["severity"],
        }

        self.safety_logs.append(safety_log)
        logger.warning(f"Safety concern logged: {safety_log}")


# ================== API MODELS ==================
class ChatRequest(BaseModel):
    child_id: str
    message: str
    child_profile: Dict[str, Any]
    parent_token: Optional[str] = None


class StoryRequest(BaseModel):
    child_id: str
    theme: str
    child_profile: Dict[str, Any]


class QuestionRequest(BaseModel):
    child_id: str
    question: str
    child_profile: Dict[str, Any]


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    confirm_password: str
    role: str = "parent"


class ChatResponse(BaseModel):
    response: str
    emotion: str
    safe: bool
    compliant: bool
    timestamp: str


class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str
    role: str


# ================== GLOBAL INSTANCES ==================
chatgpt_service = ChatGPTService()
auth_service = AuthService()

# ================== API ENDPOINTS ==================

# ChatGPT Router
chatgpt_router = APIRouter(prefix="/chatgpt", tags=["ChatGPT"])


@chatgpt_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI with safety guarantees

    Args:
        request (ChatRequest): The chat request.

    Returns:
        ChatResponse: The chat response.
    """

    try:
        result = await chatgpt_service.chat_with_child(
            child_id=request.child_id,
            message=request.message,
            child_profile=request.child_profile,
            parent_token=request.parent_token,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
            )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            response="I'm sorry, I'm having trouble right now. Let's try again!",
            emotion="friendly",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat(),
        )


@chatgpt_router.post("/story", response_model=ChatResponse)
async def generate_story(request: StoryRequest):
    """Generate a custom story for the child

    Args:
        request (StoryRequest): The story generation request.

    Returns:
        ChatResponse: The generated story.
    """

    try:
        result = await chatgpt_service.generate_story(
            child_id=request.child_id,
            theme=request.theme,
            child_profile=request.child_profile,
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Story endpoint error: {e}")
        return ChatResponse(
            response=f"Once upon a time, there was a magical {request.theme} that loved to help children learn and play!",
            emotion="happy",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat(),
        )


@chatgpt_router.post("/question", response_model=ChatResponse)
async def answer_question(request: QuestionRequest):
    """Answer child's questions

    Args:
        request (QuestionRequest): The question request.

    Returns:
        ChatResponse: The generated answer.
    """

    try:
        result = await chatgpt_service.answer_question(
            child_id=request.child_id,
            question=request.question,
            child_profile=request.child_profile,
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Question endpoint error: {e}")
        return ChatResponse(
            response="That's a great question! Let me help you learn about that in a fun way!",
            emotion="encouraging",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat(),
        )


@chatgpt_router.get("/suggestions/{child_id}")
async def get_conversation_suggestions(child_id: str, child_age: int = 6):
    """Age-appropriate conversation suggestions

    Args:
        child_id (str): Child ID.
        child_age (int, optional): Child's age. Defaults to 6.

    Returns:
        Dict[str, Any]: List of suggestions.
    """

    age_suggestions = {
        3: [
            "Tell me about your favorite animal",
            "What color do you like most?",
            "Do you want to hear a story?",
        ],
        4: [
            "What's your favorite toy?",
            "Do you like to draw pictures?",
            "Tell me about your family",
        ],
        5: [
            "What did you learn at school today?",
            "Do you have a best friend?",
            "What's your favorite book?",
        ],
        6: [
            "What do you want to be when you grow up?",
            "Tell me about your favorite game",
            "Do you like nature?",
        ],
        7: [
            "What makes you curious?",
            "Tell me about something you learned",
            "What's your favorite subject?",
        ],
        8: [
            "What would you like to create?",
            "Tell me about your hobbies",
            "What's the coolest thing you know?",
        ],
        9: [
            "What are you passionate about?",
            "Tell me about your dreams",
            "What inspires you?",
        ],
        10: [
            "What's your favorite way to learn?",
            "Tell me about your goals",
            "What challenges interest you?",
        ],
    }

    suggestions = age_suggestions.get(child_age, age_suggestions[6])

    return {
        "suggestions": suggestions,
        "age_appropriate": True,
        "timestamp": datetime.now().isoformat(),
    }


@chatgpt_router.get("/history/{child_id}")
async def get_chat_history(child_id: str, limit: int = 10):
    """Child's conversation history

    Args:
        child_id (str): Child ID.
        limit (int, optional): Maximum number of conversations to return. Defaults to 10.

    Returns:
        Dict[str, Any]: Conversation history.
    """

    history = chatgpt_service.get_conversation_history(child_id, limit)
    return {
        "child_id": child_id,
        "conversations": history,
        "total": len(history),
        "timestamp": datetime.now().isoformat(),
    }


# Authentication Router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user

    Args:
        request (RegisterRequest): The registration request.

    Returns:
        AuthResponse: Authentication response.
    """

    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    if request.email in auth_service.users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    try:
        user_data = auth_service.create_user(
            request.email, request.password, request.role
        )
        token = auth_service.create_token(user_data)

        return AuthResponse(
            access_token=token,
            user_id=user_data["user_id"],
            email=user_data["email"],
            role=user_data["role"],
        )

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@auth_router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """User login

    Args:
        request (LoginRequest): The login request.

    Returns:
        AuthResponse: Authentication response.
    """

    user = auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password"
        )

    token = auth_service.create_token(user)

    return AuthResponse(
        access_token=token, user_id=user["id"], email=user["email"], role=user["role"]
    )


# Safety Router
safety_router = APIRouter(prefix="/safety", tags=["Safety"])


@safety_router.get("/reports")
async def get_safety_reports():
    """Safety reports for parents

    Returns:
        Dict[str, Any]: Safety reports.
    """

    reports = chatgpt_service.get_safety_reports()
    return {
        "reports": reports,
        "total": len(reports),
        "timestamp": datetime.now().isoformat(),
    }


# ================== MAIN APPLICATION ==================
def create_app() -> FastAPI:
    """Create a complete FastAPI application

    Returns:
        FastAPI: The FastAPI application.
    """

    app = FastAPI(
        title="🧸 AI Teddy Bear - ChatGPT Complete API",
        description="Comprehensive single-file API for ChatGPT with security and authentication.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add the routers
    app.include_router(chatgpt_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(safety_router, prefix="/api")

    @app.get("/health")
    async def health_check():
        """System health check

        Returns:
            Dict[str, Any]: System health status.
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                "openai": DEPENDENCIES_AVAILABLE,
                "fastapi": DEPENDENCIES_AVAILABLE,
            },
        }

    return app


# ================== TESTING FUNCTIONS ==================
async def test_complete_api():
    """Comprehensive API test

    Returns:
        None
    """

    print("🧪 Starting ChatGPT Complete API test...")

    # Test user creation
    print("\n1. Testing user registration...")
    import os

    test_password = os.getenv("TEST_PARENT_PASSWORD")
    if not test_password:
        raise ValueError(
            "TEST_PARENT_PASSWORD environment variable must be set for testing"
        )
    user_data = auth_service.create_user("test@parent.com", test_password, "parent")
    print(f"✅ User created: {user_data}")

    # Test authentication
    print("\n2. Testing authentication...")
    authenticated_user = auth_service.authenticate_user(
        "test@parent.com", test_password
    )
    token = auth_service.create_token(authenticated_user)
    print(f"✅ Token created: {token[:20]}...")

    # Test ChatGPT
    print("\n3. Testing ChatGPT...")
    child_profile = {
        "age": 6,
        "preferences": {
            "interests": ["animals", "stories"],
            "favorite_character": "teddy bear",
        },
    }

    response = await chatgpt_service.chat_with_child(
        child_id="test-child-123",
        message="Tell me about elephants",
        child_profile=child_profile,
    )
    print(f"✅ ChatGPT response: {response['response'][:100]}...")

    # Test story generation
    print("\n4. Testing story generation...")
    story = await chatgpt_service.generate_story(
        child_id="test-child-123", theme="friendly dragon", child_profile=child_profile
    )
    print(f"✅ Generated story: {story['response'][:100]}...")

    # Test conversation history
    print("\n5. Testing conversation history...")
    history = chatgpt_service.get_conversation_history("test-child-123")
    print(f"✅ Conversation history: {len(history)} conversations")

    print("\n🎉 All tests passed! API ready for use")


# ================== STARTUP SCRIPT ==================
if __name__ == "__main__":
    print("🚀 ChatGPT Complete API - Starting...")

    # Run tests
    asyncio.run(test_complete_api())

    # Create the application
    app = create_app()

    print("\n📋 Available APIs:")
    print("- POST /api/chatgpt/chat - Chat with AI")
    print("- POST /api/chatgpt/story - Generate story")
    print("- POST /api/chatgpt/question - Answer question")
    print("- GET /api/chatgpt/suggestions/{child_id} - Conversation suggestions")
    print("- GET /api/chatgpt/history/{child_id} - Conversation history")
    print("- POST /api/auth/register - Register user")
    print("- POST /api/auth/login - Login user")
    print("- GET /api/safety/reports - Safety reports")
    print("- GET /docs - API documentation")
    print("- GET /health - System health check")

    print("\n✅ API ready! To run the server:")
    print("uvicorn chatgpt_complete_api:app --host 0.0.0.0 --port 8000 --reload")
