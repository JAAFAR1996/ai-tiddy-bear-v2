"""ChatGPT Integration Module for AI Teddy Bear"""

from .client import ChatGPTClient
from .fallback_responses import FallbackResponseGenerator
from .response_enhancer import ResponseEnhancer
from .safety_filter import SafetyFilter

__all__ = [
    "ChatGPTClient",
    "FallbackResponseGenerator",
    "ResponseEnhancer",
    "SafetyFilter",
]

# Version information
__version__ = "1.0.0"
__author__ = "AI Teddy Bear Team"
__description__ = "Child-safe ChatGPT integration with comprehensive safety filtering"
