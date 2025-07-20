import httpx


class AzureSpeechClient:
    def __init__(self, api_key: str, region: str) -> None:
        self.api_key = api_key
        self.region = region
        self.base_url = (
            f"https://{self.region}.stt.speech.microsoft.com/"
            "speech/recognition/conversation/cognitiveservices/v1?language=en-US"
        )
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        }

    async def speech_to_text(self, audio_data: bytes) -> str:
        # This is a simplified example. Azure Speech-to-Text typically involves
        # a more complex WebSocket or streaming API for real-time.
        # For a basic HTTP POST, you might need to adjust headers/URL based on Azure docs.
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                content=audio_data,
            )
            response.raise_for_status()
            return str(response.json()["DisplayText"])

    async def text_to_speech(
        self,
        text: str,
        voice_name: str = "en-US-JennyNeural",
    ) -> bytes:
        tts_url = (
            f"https://{self.region}.tts.speech.microsoft.com/" "cognitiveservices/v1"
        )
        tts_headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
        }
        ssml_text = (
            f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
            f"xml:lang='en-US'><voice name='{voice_name}'>{text}</voice></speak>"
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                tts_url,
                headers=tts_headers,
                content=ssml_text.encode("utf-8"),
            )
            response.raise_for_status()
            return response.content
