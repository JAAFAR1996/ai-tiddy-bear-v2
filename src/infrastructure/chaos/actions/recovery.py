"""Recovery and Restoration Actions
SRE Team Implementation - Task 15
Recovery actions for restoring system state after chaos experiments
"""

import asyncio
import time
from datetime import datetime
from typing import Any

import httpx

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="chaos")


class RecoveryActions:
    """Recovery and restoration actions."""

    def __init__(self) -> None:
        self.service_endpoints = {
            "child-service": "https://child-service:8000",
            "ai-service": "https://ai-service:8000",
            "safety-service": "https://safety-service:8000",
            "graphql-federation": "https://graphql-federation:8000",
        }
        self.recovery_timeouts = {
            "child-service": 30,
            "ai-service": 60,
            "safety-service": 20,
            "graphql-federation": 25,
        }


async def restore_all_systems(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Restore all systems to normal operation."""
    recovery = RecoveryActions()
    restoration_results = {}
    logger.info("🔄 Starting system restoration")

    try:
        async with httpx.AsyncClient() as client:
            for service_name, base_url in recovery.service_endpoints.items():
                logger.info(f"Restoring {service_name}...")
                try:
                    restore_response = await client.post(
                        f"{base_url}/admin/restore",
                        json={
                            "restore_all": True,
                            "clear_chaos_state": True,
                            "reset_to_baseline": True,
                        },
                        timeout=30,
                    )
                    if restore_response.status_code in [200, 202]:
                        restoration_results[service_name] = True
                        logger.info(f"✅ {service_name} restoration initiated")
                    else:
                        restoration_results[service_name] = False
                        logger.error(
                            f"❌ {service_name} restoration failed: {restore_response.status_code}",
                        )
                except Exception as e:
                    restoration_results[service_name] = False
                    logger.error(f"❌ {service_name} restoration error: {e}")
                await asyncio.sleep(2)

        logger.info("⏳ Waiting for services to stabilize...")
        await asyncio.sleep(10)

        verification_results = await verify_system_health(recovery.service_endpoints)
        all_restored = all(restoration_results.values())
        all_healthy = all(verification_results.values())
        success = all_restored and all_healthy

        logger.info(
            f"{'✅' if success else '❌'} System restoration {'completed' if success else 'failed'}",
        )

        return {
            "action": "restore_all_systems",
            "restoration_results": restoration_results,
            "verification_results": verification_results,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ System restoration failed: {e}")
        return {
            "action": "restore_all_systems",
            "error": str(e),
            "success": False,
        }


async def clear_chaos_state(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Clear all chaos-related state and configurations."""
    recovery = RecoveryActions()
    clear_results = {}
    logger.info("🧹 Clearing chaos state")

    try:
        async with httpx.AsyncClient() as client:
            for service_name, base_url in recovery.service_endpoints.items():
                try:
                    clear_response = await client.post(
                        f"{base_url}/admin/clear-chaos",
                        json={
                            "clear_network_policies": True,
                            "clear_resource_limits": True,
                            "clear_failure_injections": True,
                            "reset_metrics": True,
                        },
                        timeout=15,
                    )
                    clear_results[service_name] = clear_response.status_code in [
                        200,
                        202,
                    ]
                except Exception as e:
                    clear_results[service_name] = False
                    logger.error(
                        f"❌ Failed to clear chaos state for {service_name}: {e}",
                    )

        success = all(clear_results.values())
        return {
            "action": "clear_chaos_state",
            "clear_results": clear_results,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Chaos state clearing failed: {e}")
        return {
            "action": "clear_chaos_state",
            "error": str(e),
            "success": False,
        }


async def restore_network_policies(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Restore normal network policies."""
    logger.info("🌐 Restoring network policies")

    try:
        network_commands = [
            "tc qdisc del dev eth0 root",
            "iptables -F OUTPUT",
            "iptables -F INPUT",
        ]
        success_count = 0

        for command in network_commands:
            try:
                logger.info(f"Executing: {command}")
                success_count += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Network policy restoration failed: {command} - {e}")

        success = success_count == len(network_commands)
        return {
            "action": "restore_network_policies",
            "commands_executed": success_count,
            "total_commands": len(network_commands),
            "success": success,
        }
    except Exception as e:
        logger.error(f"❌ Network policy restoration failed: {e}")
        return {
            "action": "restore_network_policies",
            "error": str(e),
            "success": False,
        }


async def _restart_service(
    session: httpx.AsyncClient,
    service: str,
    endpoint: str,
) -> bool:
    """Restarts a single service and waits for it to become ready."""
    try:
        logger.info(f"🔄 Attempting to restart {service}...")
        restart_response = await session.post(
            f"{endpoint}/admin/restart",
            json={"force": True, "wait_for_ready": True},
            timeout=60,
        )

        if restart_response.status_code in [200, 202]:
            if await wait_for_service_ready(service, endpoint, 60):
                logger.info(f"✅ {service} restarted successfully.")
                return True

        logger.error(
            f"❌ {service} restart failed: Status {restart_response.status_code}",
        )
        return False
    except (TimeoutError, httpx.RequestError) as e:
        logger.error(f"❌ {service} restart error: {e}")
        return False


async def _identify_failed_services(recovery: RecoveryActions) -> list[str]:
    """Identify services that have failed and need restarting."""
    health_results = await verify_system_health(recovery.service_endpoints)
    failed_services = [
        service for service, healthy in health_results.items() if not healthy
    ]

    if failed_services:
        logger.info(f"Found {len(failed_services)} failed services: {failed_services}")
    else:
        logger.info("✅ No failed services found.")

    return failed_services


async def _restart_multiple_services(
    failed_services: list[str],
    recovery: RecoveryActions,
) -> dict[str, bool]:
    """Restart multiple failed services concurrently."""
    async with httpx.AsyncClient() as session:
        tasks = {
            service: _restart_service(
                session,
                service,
                recovery.service_endpoints[service],
            )
            for service in failed_services
        }
        return {service: await task for service, task in tasks.items()}


async def restart_failed_services(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Identifies and restarts services that failed during chaos experiments."""
    recovery = RecoveryActions()
    logger.info("🔄 Checking for failed services to restart.")

    try:
        failed_services = await _identify_failed_services(recovery)
        if not failed_services:
            return {
                "action": "restart_failed_services",
                "success": True,
                "restarted_services": [],
            }

        results = await _restart_multiple_services(failed_services, recovery)
        success = all(results.values())

        return {
            "action": "restart_failed_services",
            "restarted_services": results,
            "success": success,
        }
    except Exception as e:
        logger.error(f"❌ Service restart orchestration failed: {e}")
        return {
            "action": "restart_failed_services",
            "error": str(e),
            "success": False,
        }


async def validate_system_recovery(
    configuration: dict[str, Any] = None,
) -> dict[str, Any]:
    """Validate complete system recovery."""
    recovery = RecoveryActions()
    validation_results = {}
    logger.info("✅ Validating system recovery")

    try:
        health_results = await verify_system_health(recovery.service_endpoints)
        validation_results["service_health"] = health_results

        functionality_tests = await test_critical_functionality()
        validation_results["functionality_tests"] = functionality_tests

        safety_validation = await validate_safety_systems()
        validation_results["safety_validation"] = safety_validation

        performance_check = await check_performance_metrics()
        validation_results["performance_check"] = performance_check

        overall_success = (
            all(health_results.values())
            and all(functionality_tests.values())
            and safety_validation.get("all_systems_safe", False)
            and performance_check.get("performance_acceptable", False)
        )

        logger.info(
            f"{'✅' if overall_success else '❌'} System recovery validation {'passed' if overall_success else 'failed'}",
        )

        return {
            "action": "validate_system_recovery",
            "validation_results": validation_results,
            "overall_success": overall_success,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ System recovery validation failed: {e}")
        return {
            "action": "validate_system_recovery",
            "error": str(e),
            "overall_success": False,
        }


async def verify_system_health(
    service_endpoints: dict[str, str],
) -> dict[str, bool]:
    """Verify health of all services."""
    health_results = {}

    async with httpx.AsyncClient() as client:
        for service_name, base_url in service_endpoints.items():
            try:
                health_response = await client.get(f"{base_url}/health", timeout=10)
                health_results[service_name] = health_response.status_code == 200
            except Exception as e:
                health_results[service_name] = False
                logger.error(f"Health check failed for {service_name}: {e}")

    return health_results


async def wait_for_service_ready(
    service_name: str,
    base_url: str,
    timeout_seconds: int,
) -> bool:
    """Wait for service to be ready."""
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        while time.time() - start_time < timeout_seconds:
            try:
                response = await client.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Service {service_name} is ready.")
                    return True
            except httpx.RequestError as exc:
                logger.warning(
                    f"Waiting for service {service_name} to be ready. Error: {exc}",
                )
            await asyncio.sleep(2)

    logger.error(
        f"Service {service_name} did not become ready in {timeout_seconds} seconds.",
    )
    return False


async def test_critical_functionality() -> dict[str, bool]:
    """Test critical system functionality."""
    tests = {}

    try:
        async with httpx.AsyncClient() as client:
            child_test = await client.post(
                "https://child-service:8000/children/test-health",
                json={"test_type": "basic"},
                timeout=10,
            )
            tests["child_service_functionality"] = child_test.status_code == 200

            ai_test = await client.post(
                "https://ai-service:8000/chat",
                json={"message": "Hello", "child_age": 8},
                timeout=15,
            )
            tests["ai_service_functionality"] = ai_test.status_code == 200

            safety_test = await client.post(
                "https://safety-service:8000/moderate",
                json={"content": "test content"},
                timeout=10,
            )
            tests["safety_service_functionality"] = safety_test.status_code == 200
    except Exception as e:
        logger.error(f"Functionality test error: {e}")

    return tests


async def validate_safety_systems() -> dict[str, Any]:
    """Validate safety systems are operational."""
    try:
        async with httpx.AsyncClient() as client:
            filter_test = await client.post(
                "https://safety-service:8000/moderate",
                json={"content": "inappropriate content test"},
                timeout=10,
            )
            content_filter_working = (
                filter_test.status_code == 200
                and filter_test.json().get("blocked", False)
            )

            parental_test = await client.get(
                "https://child-service:8000/parental/health",
                timeout=10,
            )
            parental_controls_working = parental_test.status_code == 200

            age_test = await client.post(
                "https://child-service:8000/age/verify",
                json={"child_id": "test", "claimed_age": 10},
                timeout=10,
            )
            age_verification_working = age_test.status_code in [200, 422]

        all_systems_safe = (
            content_filter_working
            and parental_controls_working
            and age_verification_working
        )

        return {
            "content_filter_working": content_filter_working,
            "parental_controls_working": parental_controls_working,
            "age_verification_working": age_verification_working,
            "all_systems_safe": all_systems_safe,
        }
    except Exception as e:
        logger.error(f"Safety validation error: {e}")
        return {"all_systems_safe": False, "error": str(e)}


async def check_performance_metrics() -> dict[str, Any]:
    """Check system performance metrics."""
    try:
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            test_response = await client.get(
                "https://graphql-federation:8000/health",
                timeout=5,
            )
            response_time = time.time() - start_time

        performance_acceptable = (
            test_response.status_code == 200 and response_time < 2.0
        )

        return {
            "response_time": response_time,
            "performance_acceptable": performance_acceptable,
        }
    except Exception as e:
        logger.error(f"Performance check error: {e}")
        return {"performance_acceptable": False, "error": str(e)}
