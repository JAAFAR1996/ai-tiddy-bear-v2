from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContractDefinition(BaseModel):
    """تعريف عقد API"""

    name: str
    version: str
    provider: str
    consumer: str
    endpoint: str
    method: str
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = 30


class ContractTest(BaseModel):
    """اختبار عقد واحد"""

    name: str
    description: str
    contract: ContractDefinition
    test_data: Dict[str, Any]
    expected_status: int = 200
    expected_response_keys: List[str] = Field(default_factory=list)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class ContractResult(BaseModel):
    """نتيجة اختبار عقد"""

    test_name: str
    contract_name: str
    status: str  # passed, failed, error
    request_sent: Dict[str, Any]
    response_received: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    validation_errors: List[str] = Field(default_factory=list)
    execution_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ContractTestSuite(BaseModel):
    """مجموعة اختبارات العقد"""

    name: str
    description: str
    provider: str
    consumer: str
    contracts: List[ContractDefinition] = Field(default_factory=list)
    test_results: List[ContractResult] = Field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0
