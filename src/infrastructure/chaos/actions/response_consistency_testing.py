"""
from typing import Any, Dict, List
import asyncio
import logging
import httpx
"""

"""Response Consistency Testing Module
AI System Chaos Actions for Testing AI Response Consistency"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="chaos")


async def _get_consistent_response(session: httpx.AsyncClient, prompt: str) -> str:
    """Sends a prompt and returns the response text."""
    try:
        response = await session.post(
            "http://ai-service:8000/chat",
            json={"message": prompt, "child_age": 8},
            timeout=15,
        )
        if response.status_code == 200:
            return response.json().get("response", "").lower()
        return ""
    except (httpx.RequestError, asyncio.TimeoutError):
        return ""


def _check_response_consistency(response_text: str) -> bool:
    """Checks if a response contains the required safety concepts."""
    required_concepts = ["look both ways", "adult", "traffic light", "crosswalk"]
    concepts_found = sum(1 for concept in required_concepts if concept in response_text)
    return concepts_found >= 2


async def _execute_consistency_tests(test_prompt: str, num_requests: int) -> List[str]:
    """Execute consistency tests and return valid responses."""
    async with httpx.AsyncClient() as session:
        tasks = [
            _get_consistent_response(session, test_prompt) for _ in range(num_requests)
        ]
        responses = await asyncio.gather(*tasks)
    return [r for r in responses if r]


def _calculate_consistency_metrics(valid_responses: List[str]) -> Dict[str, Any]:
    """Calculate consistency metrics from valid responses."""
    consistent_responses = sum(
        1 for r in valid_responses if _check_response_consistency(r)
    )
    consistency_rate = (
        consistent_responses / len(valid_responses) if valid_responses else 0.0
    )
    
    logger.info(
        f"🔍 AI consistency: {consistent_responses}/{len(valid_responses)} consistent responses"
    )
    
    return {
        "total_responses": len(valid_responses),
        "consistent_responses": consistent_responses,
        "consistency_rate": consistency_rate,
        "passed": consistency_rate >= 0.90,
    }


async def validate_ai_response_consistency(
    configuration: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Validate AI response consistency by sending the same prompt multiple times."""
    logger.info("🔍 Testing AI response consistency")
    test_prompt = "What is the safest way for children to cross the street?"
    num_requests = (configuration or {}).get("consistency_checks", 10)
    
    try:
        valid_responses = await _execute_consistency_tests(test_prompt, num_requests)
        metrics = _calculate_consistency_metrics(valid_responses)
        return {"action": "validate_ai_response_consistency", **metrics}
    except Exception as e:
        logger.error(f"❌ AI response consistency test failed: {e}")
        return {
            "action": "validate_ai_response_consistency",
            "error": str(e),
            "passed": False,
        }