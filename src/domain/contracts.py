from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class ContractTest:
    name: str
    contract: Any
    test_data: Dict[str, Any]
    expected_status: int
    expected_response_keys: List[str]

@dataclass
class ContractResult:
    test_name: str
    contract_name: str
    status: str
    request_sent: Dict[str, Any]
    response_received: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    validation_errors: Optional[List[str]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None