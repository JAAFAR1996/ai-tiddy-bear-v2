from typing import Protocol


class SpeechProcessor(Protocol):
    async def speech_to_text(self, audio_data: bytes, language: str) -> str:
        ...

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        ...
