from abc import ABC, abstractmethodclass TextToSpeechService(ABC): @ abstractmethod async def text_to_speech(self, text: str, voice_id: str) -> bytes: pass
