from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

# Production-only imports - no fallbacks allowed
try:
    from openai import AsyncOpenAI
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: OpenAI library is required for production use: {e}")
    logger.critical("Install required dependencies: pip install openai")
    raise ImportError(f"Missing required dependency: openai")

from src.application.interfaces.ai_provider import AIProvider
from src.domain.value_objects.child_preferences import ChildPreferences


class OpenAIClient(AIProvider):
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(
        self,
        child_id: UUID,
        conversation_history: List[str],
        current_input: str,
        child_preferences: ChildPreferences,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": f"You are an AI Teddy Bear. Respond in {child_preferences.language}. The child's favorite topics are {', '.join(child_preferences.favorite_topics)}. Their learning level is {child_preferences.learning_level}. Be friendly, age-appropriate, and adapt to their preferences.",
            }
        ]
        # Add conversation history
        for msg in conversation_history:
            messages.append(
                {"role": "user", "content": msg}
            )  # Assuming all history is user for simplicity
        messages.append({"role": "user", "content": current_input})
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",  # Or another suitable model
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        return str(response.choices[0].message.content)
    
    async def analyze_sentiment(self, text: str) -> float:
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the sentiment of the following text and return a score between -1.0 (negative) and 1.0 (positive).",
                },
                {"role": "user", "content": text},
            ],
            max_tokens=10,
            temperature=0.0,
        )
        try:
            return float(response.choices[0].message.content)
        except ValueError:
            return 0.0
    
    async def analyze_emotion(self, text: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the emotion of the following text and return a single word emotion (e.g., happy, sad, angry, neutral).",
                },
                {"role": "user", "content": text},
            ],
            max_tokens=10,
            temperature=0.0,
        )
        return str(response.choices[0].message.content.strip().lower())