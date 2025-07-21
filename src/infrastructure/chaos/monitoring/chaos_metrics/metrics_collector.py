import asyncio

from .data_models import ChaosMetric, SystemHealthSnapshot

"""Metrics Collector Implementation"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="chaos")


class ChaosMetricsCollector:
    """Advanced metrics collector for chaos experiments."""

    def __init__(self) -> None:
        self.metrics_buffer: list[ChaosMetric] = []
        self.health_snapshots: list[SystemHealthSnapshot] = []
        self.collection_interval = 5  # seconds
        self.is_collecting = False

    async def start_collection(self, experiment_id: str):
        """Start metrics collection for experiment."""
        self.is_collecting = True
        logger.info(f"Starting metrics collection for experiment {experiment_id}")
        while self.is_collecting:
            try:
                # Collect system health snapshot
                snapshot = await self._collect_health_snapshot(experiment_id)
                self.health_snapshots.append(snapshot)
                # Collect individual metrics
                metrics = await self._collect_metrics(experiment_id)
                self.metrics_buffer.extend(metrics)
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(self.collection_interval)

    async def stop_collection(self):
        """Stop metrics collection."""
        self.is_collecting = False
        logger.info("Stopped metrics collection")

    async def _collect_health_snapshot(
        self,
        experiment_id: str,
    ) -> SystemHealthSnapshot:
        """Collect system health snapshot."""
        # Mock implementation
        from datetime import datetime

        return SystemHealthSnapshot(
            timestamp=datetime.now(),
            experiment_id=experiment_id,
            services_healthy=5,
            services_total=5,
            avg_response_time=100.0,
            error_rate=0.0,
            throughput=1000.0,
            safety_violations=0,
        )

    async def _collect_metrics(self, experiment_id: str) -> list[ChaosMetric]:
        """Collect individual service metrics (production)."""
        import aiohttp
        from datetime import datetime
        metrics = []
        services = {
            "auth_service": "http://localhost:8001/metrics",
            "user_service": "http://localhost:8002/metrics",
            "chat_service": "http://localhost:8003/metrics",
        }
        async with aiohttp.ClientSession() as session:
            for service, url in services.items():
                try:
                    async with session.get(url, timeout=3) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            cpu = data.get("cpu_usage", 0.0)
                            metrics.append(
                                ChaosMetric(
                                    timestamp=datetime.now(),
                                    experiment_id=experiment_id,
                                    service_name=service,
                                    metric_name="cpu_usage",
                                    metric_value=cpu,
                                    tags={"region": "us-east-1"},
                                )
                            )
                        else:
                            logger.error(f"Failed to fetch metrics from {service}: HTTP {resp.status}")
                            metrics.append(
                                ChaosMetric(
                                    timestamp=datetime.now(),
                                    experiment_id=experiment_id,
                                    service_name=service,
                                    metric_name="cpu_usage",
                                    metric_value=None,
                                    tags={"region": "us-east-1", "error": f"HTTP {resp.status}"},
                                )
                            )
                except Exception as e:
                    logger.error(f"Error collecting metrics from {service}: {e}")
                    metrics.append(
                        ChaosMetric(
                            timestamp=datetime.now(),
                            experiment_id=experiment_id,
                            service_name=service,
                            metric_name="cpu_usage",
                            metric_value=None,
                            tags={"region": "us-east-1", "error": str(e)},
                        )
                    )
        return metrics

    def get_all_metrics(self) -> list[ChaosMetric]:
        """Get all collected metrics."""
        return self.metrics_buffer

    def get_health_snapshots(self) -> list[SystemHealthSnapshot]:
        """Get all health snapshots."""
        return self.health_snapshots
