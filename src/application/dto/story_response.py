from typing import Optional
import sys

try:
    from pydantic import BaseModel
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.critical(f"CRITICAL ERROR: Pydantic is required for production use: {e}")
    logger.critical("Install required dependencies: pip install pydantic")
    raise ImportError(f"Missing required dependency: pydantic") from e

class StoryResponse(BaseModel):
    story_text: str
    audio_url: Optional[str] = None