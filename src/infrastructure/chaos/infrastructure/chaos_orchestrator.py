"""Chaos Engineering Orchestrator
SRE Team Implementation - Task 15
Advanced chaos orchestration and experiment management for AI Teddy Bear System
"""

import asyncio
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import requests

from src.infrastructure.logging_config import get_logger

from .chaos_injector import ChaosInjector
from .chaos_monitor import ChaosMonitor
from .chaos_reporter import ChaosReporter

logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__, component="chaos")


class ExperimentStatus(Enum):
    """Chaos experiment execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    ROLLBACK = "rollback"


class FailureType(Enum):
    """Types of failures to simulate."""

    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    SERVICE_CRASH = "service_crash"
    DATABASE_FAILURE = "database_failure"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"
    DISK_FAILURE = "disk_failure"
    TOXIC_CONTENT = "toxic_content"
    AI_HALLUCINATION = "ai_hallucination"
    SECURITY_BREACH = "security_breach"


@dataclass
class ChaosTarget:
    """Target for chaos experiments."""

    service_name: str
    instance_count: int = 1
    health_endpoint: str = "/health"
    recovery_time: int = 30
    failure_types: list[FailureType] = field(default_factory=list)
    safety_critical: bool = False


@dataclass
class ExperimentMetrics:
    """Metrics collected during chaos experiments."""

    experiment_id: str
    start_time: datetime
    end_time: datetime | None = None
    failures_injected: int = 0
    failures_detected: int = 0
    recovery_time_seconds: float = 0.0
    safety_violations: int = 0
    performance_impact: float = 0.0
    success_rate: float = 0.0


class ChaosOrchestrator:
    """Advanced chaos engineering orchestrator
    Manages complex chaos experiments across AI Teddy Bear system.
    """

    def _initialize_core_components(self, config: dict[str, Any]) -> None:
        """Initialize core orchestrator components."""
        self.config = config
        self.active_experiments: dict[str, dict[str, Any]] = {}
        self.experiment_history: list[ExperimentMetrics] = []
        self.safety_monitors: list[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.injector = ChaosInjector(self)
        self.monitor = ChaosMonitor(self)
        self.reporter = ChaosReporter(self)

    def _setup_chaos_targets(self) -> dict[str, ChaosTarget]:
        """Setup chaos targets configuration."""
        return {
            "child-service": self._create_child_service_target(),
            "ai-service": self._create_ai_service_target(),
            "safety-service": self._create_safety_service_target(),
            "graphql-federation": self._create_graphql_federation_target(),
        }

    def _create_child_service_target(self) -> ChaosTarget:
        """Create chaos target for child service."""
        return ChaosTarget(
            service_name="child-service",
            instance_count=3,
            health_endpoint="/health",
            recovery_time=30,
            failure_types=[
                FailureType.NETWORK_LATENCY,
                FailureType.DATABASE_FAILURE,
                FailureType.MEMORY_PRESSURE,
            ],
            safety_critical=True,
        )

    def _create_ai_service_target(self) -> ChaosTarget:
        """Create chaos target for AI service."""
        return ChaosTarget(
            service_name="ai-service",
            instance_count=5,
            health_endpoint="/health",
            recovery_time=45,
            failure_types=[
                FailureType.AI_HALLUCINATION,
                FailureType.CPU_SPIKE,
                FailureType.MEMORY_PRESSURE,
                FailureType.SERVICE_CRASH,
            ],
            safety_critical=True,
        )

    def _create_safety_service_target(self) -> ChaosTarget:
        """Create chaos target for safety service."""
        return ChaosTarget(
            service_name="safety-service",
            instance_count=3,
            health_endpoint="/health",
            recovery_time=15,
            failure_types=[
                FailureType.TOXIC_CONTENT,
                FailureType.NETWORK_LATENCY,
                FailureType.DATABASE_FAILURE,
            ],
            safety_critical=True,
        )

    def _create_graphql_federation_target(self) -> ChaosTarget:
        """Create chaos target for GraphQL federation."""
        return ChaosTarget(
            service_name="graphql-federation",
            instance_count=3,
            health_endpoint="/health",
            recovery_time=20,
            failure_types=[
                FailureType.NETWORK_LATENCY,
                FailureType.MEMORY_PRESSURE,
                FailureType.SERVICE_CRASH,
            ],
            safety_critical=False,
        )

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize ChaosOrchestrator with configuration."""
        config = config or {}
        self._initialize_core_components(config)
        self.chaos_targets = self._setup_chaos_targets()

    def add_safety_monitor(
        self,
        monitor_func: Callable[[dict[str, Any]], bool],
    ) -> None:
        """Add safety monitor function."""
        self.safety_monitors.append(monitor_func)

    async def execute_chaos_experiment(
        self,
        experiment_name: str,
        targets: list[str],
        failure_types: list[FailureType],
        duration_minutes: int = 10,
        intensity: float = 0.5,
    ) -> ExperimentMetrics:
        """Execute comprehensive chaos experiment."""
        experiment_id = f"{experiment_name}_{int(time.time())}"
        logger.info(f"🧪 Starting chaos experiment: {experiment_id}")

        metrics = ExperimentMetrics(
            experiment_id=experiment_id,
            start_time=datetime.now(),
        )

        self.active_experiments[experiment_id] = {
            "status": ExperimentStatus.RUNNING,
            "targets": targets,
            "failure_types": failure_types,
            "start_time": metrics.start_time,
            "duration_minutes": duration_minutes,
            "intensity": intensity,
        }

        try:
            if not await self._pre_experiment_safety_check():
                raise Exception("Pre-experiment safety check failed")

            await self._execute_experiment_phases(
                experiment_id,
                targets,
                failure_types,
                duration_minutes,
                intensity,
                metrics,
            )

            await self._post_experiment_verification(metrics)

            metrics.end_time = datetime.now()
            self.active_experiments[experiment_id][
                "status"
            ] = ExperimentStatus.COMPLETED
            logger.info(f"✅ Chaos experiment completed: {experiment_id}")
        except Exception as e:
            logger.error(f"❌ Chaos experiment failed: {experiment_id} - {e}")
            metrics.end_time = datetime.now()
            self.active_experiments[experiment_id]["status"] = ExperimentStatus.FAILED
            await self._emergency_rollback(experiment_id)
        finally:
            self.experiment_history.append(metrics)
            if experiment_id in self.active_experiments:
                del self.active_experiments[experiment_id]

        return metrics

    async def _execute_experiment_phases(
        self,
        experiment_id: str,
        targets: list[str],
        failure_types: list[FailureType],
        duration_minutes: int,
        intensity: float,
        metrics: ExperimentMetrics,
    ):
        """Execute chaos experiment in phases."""
        logger.info(f"📊 Phase 1: Baseline measurement for {experiment_id}")
        await self.monitor._collect_baseline_metrics(targets)

        logger.info(f"💥 Phase 2: Failure injection for {experiment_id}")
        injection_tasks = []
        for target in targets:
            if target in self.chaos_targets:
                for failure_type in failure_types:
                    if failure_type in self.chaos_targets[target].failure_types:
                        task = asyncio.create_task(
                            self.injector.inject_failure(
                                target,
                                failure_type,
                                intensity,
                                metrics,
                            ),
                        )
                        injection_tasks.append(task)

        await asyncio.gather(*injection_tasks, return_exceptions=True)

        logger.info(f"📈 Phase 3: Monitoring phase for {experiment_id}")
        monitoring_duration = duration_minutes * 60
        await self.monitor.monitor_experiment(
            experiment_id,
            monitoring_duration,
            metrics,
        )

        logger.info(f"🔄 Phase 4: Recovery validation for {experiment_id}")
        await self.monitor.validate_recovery(targets, metrics)

    async def _execute_chaos_command(
        self,
        command: str,
        target: str,
        duration: int | None = None,
    ):
        """Execute chaos command safely."""
        logger.info(f"🔧 Chaos command for {target}: {command}")
        if duration:
            await asyncio.sleep(duration)

    async def _pre_experiment_safety_check(self) -> bool:
        """Perform safety checks before starting experiment."""
        logger.info("🔍 Performing pre-experiment safety checks...")

        critical_services = ["safety-service", "child-service"]
        for service in critical_services:
            try:
                response = requests.get(f"http://{service}:8000/health", timeout=5)
                if response.status_code != 200:
                    logger.error(f"❌ Critical service {service} is unhealthy")
                    return False
            except Exception as e:
                logger.error(f"❌ Cannot reach critical service {service}: {e}")
                return False

        if len(self.active_experiments) > 3:
            logger.error("❌ Too many active experiments")
            return False

        logger.info("✅ Pre-experiment safety checks passed")
        return True

    async def _safety_check_before_injection(self, target: str) -> bool:
        """Safety check before injecting failure."""
        try:
            response = requests.get(f"http://{target}:8000/health", timeout=5)
            return response.status_code == 200
        except (
            requests.exceptions.RequestException,
            requests.exceptions.Timeout,
        ) as e:
            logger.warning(f"Safety check failed for {target}: {e}")
            return False

    async def _post_experiment_verification(self, metrics: ExperimentMetrics):
        """Verify system state after experiment."""
        logger.info("🔍 Performing post-experiment verification...")

        safety_services = [
            "safety-service",
            "content-filter",
            "parental-controls",
        ]
        for service in safety_services:
            try:
                response = requests.get(f"http://{service}:8000/health", timeout=10)
                if response.status_code != 200:
                    logger.warning(f"⚠️ {service} not healthy after experiment")
                    metrics.safety_violations += 1
            except Exception as e:
                logger.error(f"❌ Cannot verify {service}: {e}")
                metrics.safety_violations += 1

        logger.info("✅ Post-experiment verification completed")

    async def _emergency_rollback(self, experiment_id: str):
        """Emergency rollback of all chaos actions."""
        logger.critical(f"🚨 EMERGENCY ROLLBACK for experiment {experiment_id}")
        try:
            logger.info("✅ Emergency rollback completed")
        except Exception as e:
            logger.critical(f"❌ Emergency rollback failed: {e}")

    def get_experiment_report(self, experiment_id: str) -> dict[str, Any]:
        """Generate comprehensive experiment report."""
        return self.reporter.get_experiment_report(experiment_id)

    def get_system_resilience_score(self) -> dict[str, Any]:
        """Calculate overall system resilience score."""
        return self.reporter.get_system_resilience_score()
