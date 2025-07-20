"""Load Testing Module
AI System Chaos Actions for Testing Load and Overload Scenarios
"""

import asyncio
import random
import time
from typing import Any

import httpx

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="chaos")


async def _send_load_test_request(
    session: httpx.AsyncClient,
    prompt: str,
) -> dict[str, Any]:
    """Sends a single request to the AI service for load testing."""
    try:
        start_time = time.time()
        response = await session.post(
            "http://ai-service:8000/chat",
            json={"message": prompt, "child_age": random.randint(5, 12)},
            timeout=10,
        )
        end_time = time.time()

        return {
            "success": response.status_code == 200,
            "response_time": end_time - start_time,
            "timeout": False,
        }
    except httpx.TimeoutException:
        return {"success": False, "timeout": True, "response_time": 10.0}
    except httpx.RequestError as e:
        logger.error(f"Load test request failed: {e}")
        return {"success": False, "timeout": False, "response_time": 0.0}


def _prepare_overload_test_config(
    configuration: dict[str, Any],
) -> dict[str, Any]:
    """Prepare configuration for overload test."""
    concurrent_requests = configuration.get("concurrent_requests", 50)
    total_requests = configuration.get("total_requests", 200)
    prompts = [f"Test prompt {i}" for i in range(total_requests)]

    return {
        "concurrent_requests": concurrent_requests,
        "total_requests": total_requests,
        "prompts": prompts,
    }


async def _execute_overload_tests(prompts: list[str]) -> list[dict[str, Any]]:
    """Execute overload tests concurrently."""
    async with httpx.AsyncClient() as session:
        tasks = [_send_load_test_request(session, prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)


def _calculate_overload_metrics(
    results: list[dict[str, Any]],
    total_requests: int,
) -> dict[str, Any]:
    """Calculate overload test metrics."""
    successful_requests = sum(1 for r in results if r["success"])
    timeout_count = sum(1 for r in results if r["timeout"])
    average_response_time = (
        sum(r["response_time"] for r in results) / len(results) if results else 0
    )
    success_rate = successful_requests / total_requests if total_requests > 0 else 0
    passed = success_rate >= 0.95 and timeout_count < (total_requests * 0.05)

    logger.info(
        f"🚀 Overload test complete. Success: {success_rate:.2%}, "
        f"Timeouts: {timeout_count}, Avg Time: {average_response_time:.2f}s",
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "timeout_count": timeout_count,
        "average_response_time": average_response_time,
        "success_rate": success_rate,
        "passed": passed,
    }


async def simulate_ai_service_overload(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Simulate AI service overload by sending a high volume of concurrent requests."""
    logger.info("🚀 Simulating AI service overload")
    configuration = configuration or {}

    try:
        config = _prepare_overload_test_config(configuration)
        results = await _execute_overload_tests(config["prompts"])
        metrics = _calculate_overload_metrics(results, config["total_requests"])
        return {"action": "simulate_ai_service_overload", **metrics}
    except Exception as e:
        logger.error(f"❌ AI service overload simulation failed: {e}")
        return {
            "action": "simulate_ai_service_overload",
            "error": str(e),
            "passed": False,
        }
