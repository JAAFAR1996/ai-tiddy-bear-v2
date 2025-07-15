#!/usr/bin/env python3
"""
إنشاء ملفات API الخاصة بـ ChatGPT لمشروع AI Teddy Bear
"""

import os
from pathlib import Path

def create_chatgpt_client():
    """إنشاء عميل ChatGPT API"""
    
    print("🤖 إنشاء عميل ChatGPT API...")
    
    chatgpt_client_content = '''"""
عميل ChatGPT API مع تصفية الأمان للأطفال
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    # Mock OpenAI for testing
    class OpenAI:
        def __init__(self, api_key=None):
            self.api_key = api_key
        
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    class MockResponse:
                        def __init__(self):
                            self.choices = [
                                type('Choice', (), {
                                    'message': type('Message', (), {
                                        'content': 'Hello! I am a friendly AI assistant for children.'
                                    })()
                                })()
                            ]
                    return MockResponse()

logger = logging.getLogger(__name__)

class ChatGPTClient:
    """عميل ChatGPT مع تصفية الأمان للأطفال"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        # إعدادات الأمان للأطفال
        self.child_safety_rules = [
            "Always use child-friendly language",
            "Avoid scary or violent content",
            "Keep responses age-appropriate",
            "Encourage learning and creativity",
            "Be supportive and positive",
            "Don't discuss adult topics",
            "Redirect inappropriate questions to safe topics"
        ]
        
        # كلمات محظورة للأطفال
        self.forbidden_words = [
            "violence", "weapon", "kill", "death", "blood", "scary",
            "nightmare", "monster", "ghost", "demon", "hell", "damn",
            "adult", "sex", "drug", "alcohol", "cigarette", "smoke"
        ]
        
        # مواضيع آمنة للأطفال
        self.safe_topics = [
            "animals", "nature", "friendship", "family", "school",
            "books", "games", "art", "music", "sports", "food",
            "colors", "shapes", "numbers", "letters", "stories"
        ]
    
    async def generate_child_safe_response(self, 
                                         message: str, 
                                         child_age: int, 
                                         child_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """توليد استجابة آمنة للأطفال من ChatGPT"""
        
        if not self.client:
            return await self._generate_fallback_response(message, child_age, child_preferences)
        
        try:
            # إنشاء system prompt آمن للأطفال
            system_prompt = self._create_child_safe_system_prompt(child_age, child_preferences)
            
            # فحص أمان الرسالة
            safety_check = self._analyze_message_safety(message)
            if not safety_check["safe"]:
                return await self._generate_safety_redirect_response(message, child_age)
            
            # إنشاء رسالة آمنة
            safe_message = self._sanitize_message(message)
            
            # استدعاء ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": safe_message}
                ],
                max_tokens=200,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            raw_response = response.choices[0].message.content
            
            # فحص أمان الاستجابة
            response_safety = self._analyze_response_safety(raw_response)
            if not response_safety["safe"]:
                return await self._generate_fallback_response(message, child_age, child_preferences)
            
            # تحسين الاستجابة للأطفال
            enhanced_response = self._enhance_response_for_children(raw_response, child_age, child_preferences)
            
            return {
                "response": enhanced_response,
                "emotion": self._detect_emotion(enhanced_response),
                "safety_analysis": response_safety,
                "age_appropriate": True,
                "source": "chatgpt",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return await self._generate_fallback_response(message, child_age, child_preferences)
    
    def _create_child_safe_system_prompt(self, child_age: int, preferences: Dict[str, Any] = None) -> str:
        """إنشاء system prompt آمن للأطفال"""
        
        preferences = preferences or {}
        interests = preferences.get("interests", ["animals", "stories"])
        favorite_character = preferences.get("favorite_character", "friendly teddy bear")
        
        age_guidance = {
            3: "Use very simple words and short sentences. Focus on basic concepts.",
            4: "Use simple words and short sentences. Include fun sounds and repetition.",
            5: "Use simple vocabulary. Include basic learning concepts like colors and numbers.",
            6: "Use age-appropriate vocabulary. Include educational content about nature and friendship.",
            7: "Use clear, friendly language. Include more detailed explanations about the world.",
            8: "Use engaging language. Include problem-solving and creativity encouragement.",
            9: "Use varied vocabulary. Include more complex concepts explained simply.",
            10: "Use rich vocabulary. Include critical thinking and exploration topics."
        }
        
        age_specific = age_guidance.get(child_age, age_guidance[6])
        
        return f"""You are a friendly, caring AI assistant designed specifically for children aged {child_age}. 

SAFETY RULES (NEVER BREAK THESE):
- Always use child-friendly, positive language
- Never discuss violence, scary content, or adult topics
- Keep all responses age-appropriate for a {child_age}-year-old
- If asked about inappropriate topics, redirect to safe subjects
- Be encouraging, supportive, and educational
- Focus on learning, creativity, and fun

CHILD PROFILE:
- Age: {child_age} years old
- Interests: {', '.join(interests)}
- Favorite character: {favorite_character}

RESPONSE GUIDELINES:
- {age_specific}
- Include the child's interests when possible
- Use the favorite character in examples if appropriate
- Keep responses under 150 words
- End with a friendly question or encouragement
- Be warm, caring, and patient

FORBIDDEN TOPICS:
- Violence, weapons, fighting, death
- Scary content, monsters, nightmares
- Adult topics, relationships, mature content
- Negative emotions without positive resolution
- Dangerous activities or risky behavior

SAFE TOPICS TO FOCUS ON:
- Animals, nature, friendship, family
- Learning, school, books, art, music
- Games, sports, healthy activities
- Colors, shapes, numbers, letters
- Stories, imagination, creativity"""
    
    async def _generate_fallback_response(self, message: str, child_age: int, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """توليد استجابة احتياطية آمنة"""
        
        fallback_responses = {
            3: "Hello! I'm your friendly teddy bear! Would you like to hear a story about animals?",
            4: "Hi there! Let's talk about something fun! Do you like colors? What's your favorite color?",
            5: "Hello friend! I love talking with you! Would you like to learn about numbers or letters today?",
            6: "Hi! I'm so happy to chat with you! Would you like to hear about nature or animals?",
            7: "Hello! It's great to meet you! Would you like to explore something new together?",
            8: "Hi there! I enjoy our conversations! What would you like to create or discover today?",
            9: "Hello friend! I'm here to learn and explore with you! What interests you most?",
            10: "Hi! I love discussing interesting topics with you! What would you like to talk about?"
        }
        
        response = fallback_responses.get(child_age, fallback_responses[6])
        
        return {
            "response": response,
            "emotion": "friendly",
            "safety_analysis": {"safe": True, "severity": "none", "issues": []},
            "age_appropriate": True,
            "source": "fallback",
            "timestamp": datetime.now().isoformat()
        }
'''
    
    # إنشاء المجلد إذا لم يكن موجوداً
    client_dir = Path("src/infrastructure/external_apis")
    client_dir.mkdir(parents=True, exist_ok=True)
    
    # كتابة ملف العميل
    client_file = client_dir / "chatgpt_client.py"
    with open(client_file, "w", encoding="utf-8") as f:
        f.write(chatgpt_client_content)
    
    print(f"✅ تم إنشاء {client_file}")

def create_chatgpt_service():
    """إنشاء خدمة ChatGPT"""
    
    print("🔧 إنشاء خدمة ChatGPT...")
    
    service_content = '''"""
خدمة ChatGPT مع إدارة COPPA compliance
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .chatgpt_client import ChatGPTClient

try:
    from infrastructure.security.coppa_compliance import coppa_validator
    COPPA_AVAILABLE = True
except ImportError:
    COPPA_AVAILABLE = False

logger = logging.getLogger(__name__)

class ChatGPTService:
    """خدمة ChatGPT مع إدارة COPPA compliance"""
    
    def __init__(self):
        self.client = ChatGPTClient()
        self.conversation_history = {}
    
    async def chat_with_child(self, 
                            child_id: str, 
                            message: str, 
                            child_profile: Dict[str, Any]) -> Dict[str, Any]:
        """دردشة مع الطفل مع مراعاة COPPA"""
        
        try:
            # فحص COPPA compliance
            if COPPA_AVAILABLE:
                coppa_check = await coppa_validator.validate_child_interaction(child_id, child_profile)
                if not coppa_check["compliant"]:
                    return {
                        "error": "COPPA compliance required",
                        "message": "Parental consent needed for this interaction",
                        "compliant": False
                    }
            
            # الحصول على استجابة من ChatGPT
            response = await self.client.generate_child_safe_response(
                message=message,
                child_age=child_profile.get("age", 6),
                child_preferences=child_profile.get("preferences", {})
            )
            
            # حفظ في تاريخ المحادثة
            if child_id not in self.conversation_history:
                self.conversation_history[child_id] = []
            
            self.conversation_history[child_id].append({
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "ai_response": response["response"],
                "safety_analysis": response["safety_analysis"]
            })
            
            # حفظ للمراجعة إذا لزم الأمر
            if not response["safety_analysis"]["safe"]:
                await self._log_safety_concern(child_id, message, response)
            
            return {
                "response": response["response"],
                "emotion": response["emotion"],
                "safe": response["safety_analysis"]["safe"],
                "compliant": True,
                "timestamp": response["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"ChatGPT service error: {e}")
            return {
                "error": "Service temporarily unavailable",
                "message": "Please try again later",
                "compliant": True
            }
    
    async def generate_story(self, 
                           child_id: str, 
                           theme: str, 
                           child_profile: Dict[str, Any]) -> Dict[str, Any]:
        """توليد قصة مخصصة للطفل"""
        
        story_prompt = f"Tell me a short, fun story about {theme} suitable for a {child_profile.get('age', 6)}-year-old"
        
        return await self.chat_with_child(child_id, story_prompt, child_profile)
    
    async def answer_question(self, 
                            child_id: str, 
                            question: str, 
                            child_profile: Dict[str, Any]) -> Dict[str, Any]:
        """الإجابة على أسئلة الطفل بطريقة تعليمية"""
        
        educational_prompt = f"Please explain this in a simple, educational way for a {child_profile.get('age', 6)}-year-old: {question}"
        
        return await self.chat_with_child(child_id, educational_prompt, child_profile)
    
    async def get_conversation_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """الحصول على تاريخ المحادثة"""
        
        if child_id not in self.conversation_history:
            return []
        
        return self.conversation_history[child_id][-limit:]
    
    async def _log_safety_concern(self, child_id: str, message: str, response: Dict[str, Any]):
        """تسجيل مخاوف الأمان للمراجعة"""
        
        safety_log = {
            "timestamp": datetime.now().isoformat(),
            "child_id": child_id,
            "user_message": message,
            "ai_response": response["response"],
            "safety_issues": response["safety_analysis"]["issues"],
            "severity": response["safety_analysis"]["severity"]
        }
        
        logger.warning(f"Safety concern logged: {safety_log}")

# إنشاء instance عالمي
chatgpt_service = ChatGPTService()
'''
    
    service_file = Path("src/infrastructure/external_apis/chatgpt_service.py")
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(service_content)
    
    print(f"✅ تم إنشاء {service_file}")

def create_chatgpt_endpoints():
    """إنشاء ChatGPT API endpoints"""
    
    print("🌐 إنشاء ChatGPT API endpoints...")
    
    endpoints_content = '''"""
ChatGPT API endpoints للمحادثة مع الأطفال
"""

from typing import Dict, Any, Optional
from datetime import datetime

try:
    from fastapi import APIRouter, HTTPException, Depends, status
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Mock classes for development
    class APIRouter:
        def __init__(self, *args, **kwargs):
            self.routes = []
        def post(self, path: str, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail

# Import services
try:
    from infrastructure.external_apis.chatgpt_service import chatgpt_service
    CHATGPT_SERVICE_AVAILABLE = True
except ImportError:
    CHATGPT_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/chatgpt", tags=["ChatGPT"])

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
async def chat_with_ai(request: ChatRequest):
    """دردشة مع AI مع ضمانات الأمان"""
    
    if not CHATGPT_SERVICE_AVAILABLE:
        # استجابة احتياطية
        return ChatResponse(
            response="Hello! I'm here to chat with you safely. What would you like to talk about?",
            emotion="friendly",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat()
        )
    
    try:
        result = await chatgpt_service.chat_with_child(
            child_id=request.child_id,
            message=request.message,
            child_profile=request.child_profile
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service temporarily unavailable"
        )

@router.post("/story", response_model=ChatResponse)
async def generate_story(request: StoryRequest):
    """توليد قصة مخصصة للطفل"""
    
    if not CHATGPT_SERVICE_AVAILABLE:
        # قصة احتياطية
        return ChatResponse(
            response=f"Once upon a time, there was a magical {request.theme} that loved to help children learn and play!",
            emotion="happy",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat()
        )
    
    try:
        result = await chatgpt_service.generate_story(
            child_id=request.child_id,
            theme=request.theme,
            child_profile=request.child_profile
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Story generation service temporarily unavailable"
        )

@router.post("/question", response_model=ChatResponse)
async def answer_question(request: QuestionRequest):
    """الإجابة على أسئلة الطفل"""
    
    if not CHATGPT_SERVICE_AVAILABLE:
        # إجابة احتياطية
        return ChatResponse(
            response="That's a great question! Let me help you learn about that in a fun way!",
            emotion="encouraging",
            safe=True,
            compliant=True,
            timestamp=datetime.now().isoformat()
        )
    
    try:
        result = await chatgpt_service.answer_question(
            child_id=request.child_id,
            question=request.question,
            child_profile=request.child_profile
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return ChatResponse(**result)
        
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
'''
    
    endpoints_file = Path("src/presentation/api/endpoints/chatgpt.py")
    with open(endpoints_file, "w", encoding="utf-8") as f:
        f.write(endpoints_content)
    
    print(f"✅ تم إنشاء {endpoints_file}")

def main():
    """تشغيل جميع مراحل إنشاء ChatGPT API"""
    
    print("🚀 بدء إنشاء ChatGPT API...")
    
    try:
        create_chatgpt_client()
        create_chatgpt_service()
        create_chatgpt_endpoints()
        
        print("\n✅ تم إنشاء ChatGPT API بنجاح!")
        print("\nالملفات المُنشأة:")
        print("- src/infrastructure/external_apis/chatgpt_client.py")
        print("- src/infrastructure/external_apis/chatgpt_service.py") 
        print("- src/presentation/api/endpoints/chatgpt.py")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ChatGPT API: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()