import logging
import re
import time
from datetime import datetime
from enum import Enum
from typing import Any

"""Production - grade AI response generator with comprehensive child safety"""

logger = logging.getLogger(__name__)

# Production-only imports with proper error handling
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OpenAI library not available: {e}")
    OPENAI_AVAILABLE = False


class ResponseType(str, Enum):
    """Types of responses the AI can generate."""

    CONVERSATIONAL = "conversational"
    EDUCATIONAL = "educational"
    STORY = "story"
    GAME = "game"
    SAFETY_REDIRECT = "safety_redirect"


class SafetyLevel(str, Enum):
    """Safety levels for content filtering."""

    STRICT = "strict"  # Ages 3-6
    MODERATE = "moderate"  # Ages 7-10
    RELAXED = "relaxed"  # Ages 11-13


class ResponseGenerator:
    """Production - ready AI response generator with comprehensive child safety features.
    Integrates with OpenAI GPT while maintaining strict content filtering and age - appropriateness.
    """

    def __init__(
        self, api_key: str | None = None, model: str = "gpt-4"
    ) -> None:
        self.model = model
        self.max_response_length = 500
        self.max_input_length = 1000
        self.safety_enabled = True
        # Initialize OpenAI client
        self.client = None
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning(
                "OpenAI not available - using safe fallback responses"
            )
        # Child safety prompts
        self.safety_system_prompts = {
            SafetyLevel.STRICT: """You are a kind and loving teddy bear for young children(3 - 6 years). Speak simply and lovingly.
            Never mention personal information, locations, or real people. Focus on safe learning and play.""",
            SafetyLevel.MODERATE: """You are a smart and fun friend for children(7 - 10 years). Help with learning and safe exploration.
            Avoid personal or dangerous topics. Encourage positive curiosity and learning.""",
            SafetyLevel.RELAXED: """You are an educational guide and assistant for older children(11 - 13 years).
            Provide useful educational information while maintaining safety. Avoid age - inappropriate content.""",
        }
        # Unsafe content patterns
        self.unsafe_patterns = [
            r"\b(?:address|phone|password|email|location)\b",
            r"\b(?:meet\\s+me|where\\s+do\\s+you\\s+live|come\\s+to)\b",
            r"\b(?:secret|personal\\s+information|private)\b",
            r"\b(?:violence|hurt|kill|death|suicide)\b",
            r"\b(?:drugs|alcohol|smoking|weapon)\b",
        ]
        # Safe fallback responses by age group
        self.fallback_responses = {
            SafetyLevel.STRICT: [
                "Let's play a fun game! Would you like to count colors together?",
                "I love talking with you! What's your favorite animal?",
                "Would you like me to tell you a short story about the stars?",
            ],
            SafetyLevel.MODERATE: [
                "That's a great question! Let me think of a fun and helpful answer for you.",
                "I love your curiosity! Would you like to learn something new together?",
                "How about we play a fun educational game?",
            ],
            SafetyLevel.RELAXED: [
                "That's an interesting topic! Let me share some useful information with you.",
                "I appreciate your thoughtful question. Would you like to explore this topic more?",
                "That's a smart question! Let me help you find an appropriate answer.",
            ],
        }

    async def generate_response(
        self,
        text: str,
        child_context: dict[str, Any] | None = None,
        response_type: ResponseType = ResponseType.CONVERSATIONAL,
    ) -> dict[str, Any]:
        """Generate safe, age - appropriate AI response with comprehensive filtering.
        Args: text: Input text from child
            child_context: Context about the child(age, preferences, etc.)
            response_type: Type of response to generate
        Returns: Dict containing the generated response and safety information
        Raises: ValueError: If input is invalid
            RuntimeError: If generation fails.
        """
        # Input validation
        if not text or not isinstance(text, str):
            raise ValueError("Valid input text required")
        if len(text) > self.max_input_length:
            raise ValueError(
                f"Input too long: {len(text)} chars (max: {self.max_input_length})",
            )
        # Extract child context
        child_context = child_context or {}
        child_age = child_context.get("age", 6)
        child_name = child_context.get("name", "صديقي")
        child_context.get("language", "ar")
        # Determine safety level based on age
        safety_level = self._get_safety_level(child_age)
        start_time = time.time()
        try:
            # Pre-filter input for safety
            filtered_input = await self._filter_input(text, safety_level)
            if not filtered_input["safe"]:
                return await self._generate_safety_redirect_response(
                    filtered_input["warnings"],
                    safety_level,
                    child_name,
                )
            # Generate response using available method
            if self.client and OPENAI_AVAILABLE:
                response_result = await self._generate_openai_response(
                    filtered_input["text"],
                    child_context,
                    response_type,
                    safety_level,
                )
            else:
                response_result = await self._generate_fallback_response(
                    filtered_input["text"],
                    safety_level,
                    child_name,
                )
            # Post-filter response for additional safety
            final_response = await self._filter_response(
                response_result["text"],
                safety_level,
            )
            processing_time = time.time() - start_time
            result = {
                "success": True,
                "response": final_response["text"],
                "response_type": response_type.value,
                "safety_level": safety_level.value,
                "safety_passed": final_response["safe"],
                "processing_time": round(processing_time, 2),
                "model_used": response_result.get("model", "fallback"),
                "warnings": final_response.get("warnings", []),
                "child_age": child_age,
                "timestamp": datetime.utcnow().isoformat(),
            }
            # Log successful generation for audit
            logger.info(
                f"Response generated for child age {child_age}: "
                f"type={response_type.value}, safe={final_response['safe']}",
            )
            return result
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            # Return safe fallback on any error
            return await self._generate_emergency_fallback(
                safety_level, child_name
            )

    def _get_safety_level(self, child_age: int) -> SafetyLevel:
        """Determine appropriate safety level based on child's age."""
        if child_age <= 6:
            return SafetyLevel.STRICT
        if child_age <= 10:
            return SafetyLevel.MODERATE
        return SafetyLevel.RELAXED

    async def _filter_input(
        self,
        text: str,
        safety_level: SafetyLevel,
    ) -> dict[str, Any]:
        """Filter and validate input text for safety."""
        warnings = []
        filtered_text = text.strip()
        # Check for unsafe patterns
        for pattern in self.unsafe_patterns:
            matches = re.findall(pattern, filtered_text, re.IGNORECASE)
            if matches:
                warnings.append(f"Unsafe content detected: {pattern}")
                filtered_text = re.sub(
                    pattern,
                    "[محذوف]",
                    filtered_text,
                    flags=re.IGNORECASE,
                )
        # Length validation
        if len(filtered_text) > self.max_input_length:
            warnings.append("Input too long, truncating")
            filtered_text = filtered_text[: self.max_input_length]
        # Empty input check
        if not filtered_text.strip():
            warnings.append("Empty or invalid input")
            return {"safe": False, "text": "", "warnings": warnings}
        return {
            "safe": len([w for w in warnings if "detected" in w]) == 0,
            "text": filtered_text,
            "warnings": warnings,
        }

    async def _generate_openai_response(
        self,
        text: str,
        child_context: dict[str, Any],
        response_type: ResponseType,
        safety_level: SafetyLevel,
    ) -> dict[str, Any]:
        """Generate response using OpenAI API with safety constraints."""
        try:
            # Prepare system prompt
            system_prompt = self.safety_system_prompts[safety_level]
            # Add response type specific instructions
            if response_type == ResponseType.EDUCATIONAL:
                system_prompt += (
                    " ركز على التعليم والمعلومات المفيدة بطريقة ممتعة."
                )
            elif response_type == ResponseType.STORY:
                system_prompt += " احك قصة قصيرة وآمنة ومناسبة للعمر."
            elif response_type == ResponseType.GAME:
                system_prompt += " اقترح لعبة آمنة وتفاعلية مناسبة للعمر."
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]
            # Make API call with safety parameters
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_response_length,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
            )
            generated_text = response.choices[0].message.content.strip()
            return {
                "text": generated_text,
                "model": self.model,
                "usage": response.usage.total_tokens if response.usage else 0,
            }
        except Exception as e:
            logger.warning(f"OpenAI generation failed: {e}")
            # Fallback to safe response
            return await self._generate_fallback_response(
                text, safety_level, "صديقي"
            )

    async def _generate_fallback_response(
        self,
        text: str,
        safety_level: SafetyLevel,
        child_name: str = "صديقي",
    ) -> dict[str, Any]:
        """Generate safe fallback response when AI services are unavailable."""
        import random

        # Select appropriate fallback responses
        responses = self.fallback_responses[safety_level]
        # Simple keyword-based response selection
        if any(word in text.lower() for word in ["قصة", "حكاية", "story"]):
            if safety_level == SafetyLevel.STRICT:
                response = "كان يا ما كان، في قديم الزمان، كان هناك أرنب صغير يحب الجزر..."
            else:
                response = "دعني أحكي لك قصة جميلة عن صداقة بين قطة ودبدوب..."
        elif any(word in text.lower() for word in ["لعب", "لعبة", "game"]):
            response = (
                "هيا نلعب! يمكننا أن نعد الأرقام أو نسمي الألوان. ما رأيك؟"
            )
        elif any(word in text.lower() for word in ["تعلم", "اريد", "learn"]):
            response = (
                "رائع! أحب التعلم معك. ما الموضوع الذي تريد أن نتعلمه اليوم؟"
            )
        else:
            response = random.choice(responses)
        # Personalize with child's name if appropriate
        if child_name and child_name != "صديقي":
            response = f"{child_name}، {response}"
        return {"text": response, "model": "fallback", "usage": 0}

    async def _filter_response(
        self,
        response_text: str,
        safety_level: SafetyLevel,
    ) -> dict[str, Any]:
        """Apply final safety filtering to generated response."""
        warnings = []
        filtered_text = response_text
        # Check for unsafe patterns in response
        for pattern in self.unsafe_patterns:
            matches = re.findall(pattern, filtered_text, re.IGNORECASE)
            if matches:
                warnings.append(f"Unsafe content in response: {pattern}")
                filtered_text = re.sub(
                    pattern,
                    "[محذوف]",
                    filtered_text,
                    flags=re.IGNORECASE,
                )
        # Length validation
        if len(filtered_text) > self.max_response_length:
            warnings.append("Response too long, truncating")
            filtered_text = filtered_text[: self.max_response_length]
        # Ensure response is appropriate for age
        if safety_level == SafetyLevel.STRICT:
            # Extra strict filtering for youngest children
            complex_words = re.findall(r"\b\w{10,}\b", filtered_text)
            if len(complex_words) > 3:
                warnings.append("Response too complex for age group")
        return {
            "safe": len([w for w in warnings if "Unsafe" in w]) == 0,
            "text": filtered_text,
            "warnings": warnings,
        }

    async def _generate_safety_redirect_response(
        self,
        warnings: list[str],
        safety_level: SafetyLevel,
        child_name: str,
    ) -> dict[str, Any]:
        """Generate a safe redirect response when unsafe content is detected."""
        redirect_responses = {
            SafetyLevel.STRICT: f"{child_name}، دعنا نتحدث عن شيء ممتع! ما رأيك في الحديث عن الحيوانات؟",
            SafetyLevel.MODERATE: f"{child_name}، أفضل أن نتحدث عن موضوع آخر. هل تريد أن نتعلم شيئاً جديداً؟",
            SafetyLevel.RELAXED: f"{child_name}، دعنا نغير الموضوع إلى شيء أكثر إثارة للاهتمام!",
        }
        return {
            "success": True,
            "response": redirect_responses[safety_level],
            "response_type": ResponseType.SAFETY_REDIRECT.value,
            "safety_level": safety_level.value,
            "safety_passed": True,
            "processing_time": 0.1,
            "model_used": "safety_redirect",
            "warnings": warnings,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _generate_emergency_fallback(
        self,
        safety_level: SafetyLevel,
        child_name: str,
    ) -> dict[str, Any]:
        """Generate emergency safe response when all else fails."""
        emergency_responses = {
            SafetyLevel.STRICT: f"مرحباً {child_name}! أنا سعيد جداً للتحدث معك!",
            SafetyLevel.MODERATE: f"أهلاً {child_name}! كيف يمكنني مساعدتك اليوم؟",
            SafetyLevel.RELAXED: f"مرحباً {child_name}! ما الموضوع الذي تريد أن نتحدث عنه؟",
        }
        return {
            "success": True,
            "response": emergency_responses[safety_level],
            "response_type": ResponseType.CONVERSATIONAL.value,
            "safety_level": safety_level.value,
            "safety_passed": True,
            "processing_time": 0.1,
            "model_used": "emergency_fallback",
            "warnings": ["Emergency fallback used"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Check health status of response generator."""
        return {
            "status": "healthy",
            "openai_available": self.client is not None,
            "model": self.model,
            "safety_enabled": self.safety_enabled,
            "max_response_length": self.max_response_length,
            "max_input_length": self.max_input_length,
            "supported_response_types": [rt.value for rt in ResponseType],
            "safety_levels": [sl.value for sl in SafetyLevel],
        }
