from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any, Dict, List

import requests

from src.infrastructure.logging_config import get_logger

if TYPE_CHECKING:
    from .chaos_orchestrator import ChaosOrchestrator, ExperimentMetrics

logger = get_logger(__name__, component="chaos")


class ChaosMonitor:
    def __init__(self, orchestrator: ChaosOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.chaos_targets = orchestrator.chaos_targets

    async def monitor_experiment(
        self,
        experiment_id: str,
        duration_seconds: int,
        metrics: ExperimentMetrics,
    ):
        """Monitor experiment progress and safety."""
        start_time = time.time()
        safety_violations = 0

        while time.time() - start_time < duration_seconds:
            for monitor in self.orchestrator.safety_monitors:
                try:
                    if not monitor({"experiment_id": experiment_id}):
                        safety_violations += 1
                        logger.warning(
                            f"⚠️ Safety violation detected in {experiment_id}",
                        )
                        if safety_violations >= 3:
                            logger.error(
                                f"🚨 Too many safety violations, aborting {experiment_id}",
                            )
                            await self.orchestrator._emergency_rollback(
                                experiment_id
                            )
                            return
                except Exception as e:
                    logger.error(f"Safety monitor error: {e}")

            await self._collect_performance_metrics(metrics)
            await asyncio.sleep(10)

        metrics.safety_violations = safety_violations

    async def _collect_baseline_metrics(
        self, targets: List[str]
    ) -> Dict[str, Any]:
        """Collect baseline performance metrics."""
        baseline = {}
        for target in targets:
            try:
                response = requests.get(
                    f"http://{target}:8000/metrics", timeout=5
                )
                if response.status_code == 200:
                    baseline[target] = response.json()
            except Exception as e:
                logger.warning(f"Failed to collect baseline for {target}: {e}")
                baseline[target] = {}
        return baseline

    async def _collect_performance_metrics(self, metrics: ExperimentMetrics):
        """Collect performance metrics during experiment."""
        try:
            # This can be expanded with more detailed metric collection
            logger.debug(
                f"Collecting performance metrics for {metrics.experiment_id}"
            )
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")

    async def validate_recovery(
        self, targets: List[str], metrics: ExperimentMetrics
    ):
        """Validate system recovery after chaos."""
        recovery_start = time.time()

        for target in targets:
            target_config = self.chaos_targets.get(target)
            if not target_config:
                continue

            max_wait = target_config.recovery_time
            recovered = False

            for _ in range(max_wait):
                try:
                    response = requests.get(
                        f"http://{target}:8000{target_config.health_endpoint}",
                        timeout=5,
                    )
                    if response.status_code == 200:
                        recovered = True
                        break
                except requests.RequestException:
                    # Service is likely still down, continue waiting
                    pass
                await asyncio.sleep(1)

            if recovered:
                logger.info(f"✅ {target} recovered successfully")
                metrics.failures_detected += 1
            else:
                logger.error(
                    f"❌ {target} failed to recover within {max_wait}s"
                )

        recovery_time = time.time() - recovery_start
        metrics.recovery_time_seconds = recovery_time

        if metrics.failures_injected > 0:
            metrics.success_rate = (
                metrics.failures_detected / metrics.failures_injected
            )