import httpx
from pydantic import SecretStr


class ElevenLabsClient:
    def __init__(self, api_key: SecretStr) -> None:
        self.api_key = api_key.get_secret_value()
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00TNDk4EwAXMxZg8j",
    ) -> bytes:
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            # Raise an exception for bad status codes
            return response.content
