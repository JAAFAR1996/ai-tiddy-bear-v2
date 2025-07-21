"""ESP32 Audio Processing Use Case
Handles the complete workflow of processing audio input from ESP32 devices,
including speech-to-text, AI response generation, and text-to-speech output
with comprehensive child safety measures.
"""

from uuid import UUID, uuid4

from fastapi import HTTPException

from src.application.dto.ai_response import AIResponse
from src.application.dto.esp32_request import ESP32Request
from src.application.services.ai.ai_orchestration_service import AIOrchestrationService
from src.application.services.device.audio_processing_service import AudioProcessingService
from src.application.services.core.conversation_service import ConversationService
from src.infrastructure.persistence.child_repository import ChildRepository
from src.domain.value_objects.safety_level import SafetyLevel


class ProcessESP32AudioUseCase:
    """Use case for processing ESP32 audio input with comprehensive safety checks.
    This use case orchestrates the complete audio processing workflow:
    1. Audio transcription with safety validation
    2. Child profile and conversation context retrieval
    3. AI response generation with personalization
    4. Conversation history updates and learning
    5. Audio response generation.

    All operations include COPPA compliance and child safety measures.

    Attributes:
        audio_processing_service: Service for audio transcription and generation
        ai_orchestration_service: Service for AI response generation
        conversation_service: Service for conversation management
        child_repository: Repository for child profile data

    """

    def __init__(
        self,
        audio_processing_service: AudioProcessingService,
        ai_orchestration_service: AIOrchestrationService,
        conversation_service: ConversationService,
        child_repository: ChildRepository,
    ) -> None:
        """Initialize the ESP32 audio processing use case.

        Args:
            audio_processing_service: Service for audio transcription and TTS
            ai_orchestration_service: Service for AI response generation
            conversation_service: Service for conversation management
            child_repository: Repository for child profile operations

        """
        self.audio_processing_service = audio_processing_service
        self.ai_orchestration_service = ai_orchestration_service
        self.conversation_service = conversation_service
        self.child_repository = child_repository

    async def execute(self, request: ESP32Request) -> AIResponse:
        """Execute the complete ESP32 audio processing workflow.

        Processes audio input through a comprehensive pipeline including
        transcription, safety validation, AI response generation, and
        audio output generation with child safety measures.

        Args:
            request: ESP32 audio request containing audio data and metadata

        Returns:
            AI response with text, audio, emotion, and safety indicators

        Raises:
            HTTPException: If child profile is not found(404)

        Example:
            ```python
            use_case = ProcessESP32AudioUseCase(...)
            response = await use_case.execute(
                ESP32Request(child_id="child_123", audio_data=audio_bytes,
                           language_code="en"))
            ```

        """
        # 1. Process audio input (STT and safety check)
        (
            transcription,
            audio_safety_level,
        ) = await self.audio_processing_service.process_audio_input(
            request.audio_data,
            request.language_code,
        )

        if audio_safety_level == SafetyLevel.CRITICAL:
            # Handle critical safety level, e.g., return a canned response
            return AIResponse(
                response_text="I'm sorry, I can't process that. Let's talk about something else.",
                audio_response=b"",
                emotion="neutral",
                sentiment=0.0,
                safe=False,
            )

        # 2. Get child profile and conversation history
        child_profile = await self.child_repository.get_by_id(request.child_id)
        if not child_profile:
            raise HTTPException(status_code=404, detail="Child profile not found")

        conversation_history = await self.conversation_service.get_conversation_history(
            request.child_id,
        )

        # Extract relevant parts for AI context
        history_texts = [conv.summary for conv in conversation_history]

        # 3. Get AI response
        ai_response = await self.ai_orchestration_service.get_ai_response(
            request.child_id,
            history_texts,
            transcription,
            child_preferences=child_profile.preferences,  # Pass child preferences
            voice_id=child_profile.preferences.voice_preference,  # Use child's voice preference
        )

        # 4. Update conversation history and child preferences
        await self.conversation_service.start_new_conversation(
            request.child_id,
            transcription,
        )

        conversation_id = (
            UUID(ai_response.conversation_id)
            if isinstance(ai_response.conversation_id, str)
            else (
                ai_response.conversation_id if ai_response.conversation_id else uuid4()
            )
        )
        await self.conversation_service.update_conversation_analysis(
            conversation_id,
            ai_response.emotion,
            ai_response.sentiment,
        )

        # Update child preferences based on interaction for adaptive learning
        # This is a simplified example; a real implementation would involve more sophisticated NLP and analysis.
        child_profile.preferences.vocabulary_size += (
            len(transcription.split()) // 10
        )  # Simple approximation
        child_profile.preferences.interaction_history_summary = (
            (child_profile.preferences.interaction_history_summary or "")
            + " "
            + transcription
            + " "
            + ai_response.response_text
        )

        # Update emotional tendencies based on AI response emotion
        current_emotion_score = child_profile.preferences.emotional_tendencies.get(
            ai_response.emotion,
            0.0,
        )
        child_profile.preferences.emotional_tendencies[ai_response.emotion] = (
            current_emotion_score + 1.0
        ) / 2.0  # Simple averaging

        await self.child_repository.save(child_profile)  # Save updated child profile

        # 5. Generate audio response
        audio_output = await self.audio_processing_service.generate_audio_response(
            ai_response.response_text,
            voice_id=child_profile.preferences.voice_preference,  # Use child's voice preference
        )

        ai_response.audio_response = audio_output
        return ai_response
