import asyncio
import sys
from pathlib import Path

from src.domain.contracts import ContractResult, ContractTest
from src.domain.schemas import validate_against_schema

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    try:
        pass
    except ImportError:
        from common.mock_pydantic import BaseModel, ValidationError
except ImportError:
    from common.mock_pydantic import BaseModel, ValidationError
except ImportError:
    # Mock pydantic when not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        def json(self):
            import json

            return json.dumps(self.dict())

    class ValidationError(Exception):
        pass


async def _prepare_url(framework, endpoint: str, test_data: dict) -> str:
    """Prepares the request URL by substituting path parameters."""
    url = f"{framework.base_url}{endpoint}"
    for key, value in test_data.items():
        if f"{{{key}}}" in url:
            url = url.replace(f"{{{key}}}", str(value))
    return url


def _prepare_headers(contract_headers: dict) -> dict:
    """Prepares the request headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **contract_headers,
    }


async def _make_request(
    framework, method: str, url: str, data: dict, headers: dict
) -> tuple[dict | None, int]:
    """Makes an HTTP request using the specified method."""
    request_functions = {
        "GET": framework.session.get,
        "POST": framework.session.post,
    }
    request_function = request_functions.get(method.upper())

    if not request_function:
        raise ValueError(f"Unsupported method: {method}")

    request_kwargs = {"headers": headers}
    if method.upper() == "POST":
        request_kwargs["json"] = data

    async with request_function(url, **request_kwargs) as response:
        response_data = await response.json() if response.status // 100 == 2 else None
        return response_data, response.status


def _validate_response(
    response_data: dict | None, response_status: int, test: ContractTest
) -> list[str]:
    """Validates the HTTP response against the contract."""
    validation_errors = []
    if response_status == test.expected_status and response_data:
        try:
            validate_against_schema(response_data, test.contract.response_schema)
            for key in test.expected_response_keys:
                if key not in response_data:
                    validation_errors.append(f"Missing required key: {key}")
        except ValidationError as e:
            validation_errors.append(f"Response schema validation failed: {e}")
    return validation_errors


def _determine_test_status(
    response_status: int, expected_status: int, validation_errors: list[str]
) -> tuple[str, str | None]:
    """Determines the final status of the test."""
    if response_status != expected_status:
        return (
            "failed",
            f"Expected status {expected_status}, got {response_status}",
        )
    if validation_errors:
        return "failed", "; ".join(validation_errors)
    return "passed", None


async def execute_contract_test(framework, test: ContractTest) -> ContractResult:
    """تنفيذ اختبار عقد واحد"""
    start_time = asyncio.get_event_loop().time()

    try:
        validate_against_schema(test.test_data, test.contract.request_schema)

        url = await _prepare_url(framework, test.contract.endpoint, test.test_data)
        headers = _prepare_headers(test.contract.headers)

        response_data, response_status = await _make_request(
            framework, test.contract.method, url, test.test_data, headers
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        validation_errors = _validate_response(response_data, response_status, test)

        status, error_message = _determine_test_status(
            response_status, test.expected_status, validation_errors
        )

        return ContractResult(
            test_name=test.name,
            contract_name=test.contract.name,
            status=status,
            request_sent=test.test_data,
            response_received=response_data,
            response_status=response_status,
            validation_errors=validation_errors,
            execution_time=execution_time,
            error_message=error_message,
        )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return ContractResult(
            test_name=test.name,
            contract_name=test.contract.name,
            status="error",
            request_sent=test.test_data,
            execution_time=execution_time,
            error_message=str(e),
        )
