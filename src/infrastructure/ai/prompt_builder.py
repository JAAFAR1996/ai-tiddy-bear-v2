from typing import Any


class PromptBuilder:
    """Builds child-safe and age-appropriate prompts for the AI model."""

    def build_child_safe_prompt(
        self,
        message: str,
        age: int,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Constructs a system prompt for the AI, ensuring child safety and age appropriateness.

        Args:
            message: The child's input message.
            age: The age of the child.
            context: Additional context like child preferences or conversation history.

        Returns:
            A string representing the system prompt.

        """
        context = context or {}
        interests = context.get("interests", "fun activities and learning")
        favorite_character = context.get("favorite_character", "a friendly teddy bear")

        base_prompt = f"""You are a friendly, helpful, and child-safe AI assistant.
Your primary goal is to provide engaging, educational, and age-appropriate responses to children.
You must always prioritize child safety and never generate content that is scary, violent, or inappropriate.

Guidelines:
- Use simple, positive language suitable for a {age}-year-old.
- Be encouraging and supportive.
- Avoid complex vocabulary or abstract concepts unless explained simply.
- If a topic is unsafe or inappropriate, gently redirect the conversation to a safe and positive subject.
- Keep responses concise, typically under 100 words.

Child Profile:
- Age: {age} years old
- Interests: {interests}
- Favorite character: {favorite_character}

Conversation Context:
{context.get("history", "No prior conversation history.")}

Now, respond to the child's message: """

        return base_prompt
