from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


@dataclass
class TestConfig:
    """تكوين الاختبارات الشاملة"""

    # Coverage Requirements
    min_coverage: float = 95.0
    critical_modules_coverage: float = 98.0

    # Performance Benchmarks
    max_response_time_ms: int = 500
    max_memory_usage_mb: int = 512
    max_cpu_usage_percent: float = 80.0

    # Load Testing
    concurrent_users: int = 10000
    ramp_up_time_seconds: int = 60
    test_duration_minutes: int = 30

    # Security Testing
    penetration_test_timeout: int = 300
    vulnerability_scan_timeout: int = 600

    # Child Safety
    max_inappropriate_content_score: float = 0.1
    min_privacy_protection_score: float = 0.95

    # Quality Gates
    max_cyclomatic_complexity: int = 10
    max_cognitive_complexity: int = 15
    min_maintainability_index: int = 65


class TestResult(BaseModel):
    """نتيجة اختبار واحدة"""

    test_name: str
    test_type: str  # unit, integration, e2e, security, performance
    status: str  # passed, failed, skipped, error
    duration_ms: float
    coverage_percent: Optional[float] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    security_score: Optional[float] = None
    child_safety_score: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class TestSuite(BaseModel):
    """مجموعة اختبارات"""

    name: str
    description: str
    test_results: List[TestResult] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    coverage_percent: float = 0.0
    execution_time_seconds: float = 0.0
