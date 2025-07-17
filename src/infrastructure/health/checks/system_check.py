"""System resources health check module."""

import time
from datetime import datetime

import psutil

from src.infrastructure.logging_config import get_logger

from ..models import HealthCheckResult, HealthStatus

logger = get_logger(__name__, component="infrastructure")


class SystemHealthCheck:
    """System resources(CPU, memory, disk) health check."""

    async def check(self) -> HealthCheckResult:
        """Check system resources health."""
        start_time = time.time()
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)

            # Determine status based on thresholds
            issues = []
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent}%")
            elif cpu_percent > 70:
                issues.append(f"Elevated CPU usage: {cpu_percent}%")

            if memory_percent > 90:
                issues.append(f"High memory usage: {memory_percent}%")
            elif memory_percent > 80:
                issues.append(f"Elevated memory usage: {memory_percent}%")

            if disk_percent > 90:
                issues.append(f"Low disk space: {disk_free_gb:.1f}GB free")
            elif disk_percent > 80:
                issues.append(f"Disk space warning: {disk_free_gb:.1f}GB free")

            # Determine overall status
            if any("High" in issue for issue in issues):
                status = HealthStatus.UNHEALTHY
            elif issues:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

            message = "; ".join(issues) if issues else "System resources are healthy"

            return HealthCheckResult(
                name="system",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_available_gb": round(memory_available_gb, 2),
                    "disk_percent": disk_percent,
                    "disk_free_gb": round(disk_free_gb, 2),
                },
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return HealthCheckResult(
                name="system",
                status=HealthStatus.UNHEALTHY,
                message=f"System check failed: {e!s}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
            )
