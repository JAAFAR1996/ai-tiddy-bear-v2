from pydantic import BaseModel
from typing import Any


class ChaosMetric(BaseModel):
    name: str
    value: float
    timestamp: float
    experiment_id: str
    extra: dict[str, Any] = {}


class SystemHealthSnapshot(BaseModel):
    experiment_id: str
    healthy_services: int
    total_services: int
    avg_response_time: float
    error_rate: float
    throughput: float
    safety_violations: int
    timestamp: float
