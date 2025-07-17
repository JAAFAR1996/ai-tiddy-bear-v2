from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from .chatgpt_client import ChatGPTClient

"""ChatGPT service with COPPA compliance management"""

try:
    from infrastructure.security.coppa_compliance import coppa_validator

    COPPA_AVAILABLE = True
except ImportError:
    COPPA_AVAILABLE = False

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class ChatGPTService:
    """ChatGPT service with COPPA compliance management."""

    def __init__(self) -> None:
        self.client = ChatGPTClient()
        self.conversation_history = {}

    async def chat_with_child(
        self,
        child_id: str,
        message: str,
        child_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Chat with child while respecting COPPA."""
        try:
            if COPPA_AVAILABLE:
                coppa_check = await coppa_validator.validate_child_interaction(
                    child_id,
                    child_profile,
                )
                if not coppa_check["compliant"]:
                    return {
                        "error": "COPPA compliance required",
                        "message": "Parental consent needed for this interaction",
                        "compliant": False,
                    }
            # Get response from ChatGPT
            response = await self.client.generate_child_safe_response(
                message=message,
                child_age=child_profile.get("age", 6),
                child_preferences=child_profile.get("preferences", {}),
            )
            # Save to conversation history
            if child_id not in self.conversation_history:
                self.conversation_history[child_id] = []
            self.conversation_history[child_id].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "user_message": message,
                    "ai_response": response["response"],
                    "safety_analysis": response["safety_analysis"],
                },
            )
            # Save for review if necessary
            if not response["safety_analysis"]["safe"]:
                await self._log_safety_concern(child_id, message, response)
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
        self,
        child_id: str,
        theme: str,
        child_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate personalized story for child."""
        story_prompt = (
            f"Tell me a short, fun story about {theme} suitable for a "
            f"{child_profile.get('age', 6)}-year-old"
        )
        return await self.chat_with_child(
            child_id, story_prompt, child_profile
        )

    async def answer_question(
        self,
        child_id: str,
        question: str,
        child_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Answer child's questions in an educational way."""
        educational_prompt = (
            f"Please explain this in a simple, educational way for a "
            f"{child_profile.get('age', 6)}-year-old: {question}"
        )
        return await self.chat_with_child(
            child_id, educational_prompt, child_profile
        )

    async def get_conversation_history(
        self,
        child_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if child_id not in self.conversation_history:
            return []
        return self.conversation_history[child_id][-limit:]

    async def _log_safety_concern(
        self,
        child_id: str,
        message: str,
        response: Dict[str, Any],
    ):
        """Log safety concerns for review."""
        safety_log = {
            "timestamp": datetime.now().isoformat(),
            "child_id": child_id,
            "user_message": message,
            "ai_response": response["response"],
            "safety_issues": response["safety_analysis"]["issues"],
            "severity": response["safety_analysis"]["severity"],
        }
        logger.warning(f"Safety concern logged: {safety_log}")


# Create global instance
chatgpt_service = ChatGPTService()
