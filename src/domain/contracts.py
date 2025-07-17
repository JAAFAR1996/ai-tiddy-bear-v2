from dataclasses import dataclass
from typing import Any


@dataclass
class ContractTest:
    name: str
    contract: Any
    test_data: dict[str, Any]
    expected_status: int
    expected_response_keys: list[str]


@dataclass
class ContractResult:
    test_name: str
    contract_name: str
    status: str
    request_sent: dict[str, Any]
    response_received: dict[str, Any] | None = None
    response_status: int | None = None
    validation_errors: list[str] | None = None
    execution_time: float = 0.0
    error_message: str | None = None
