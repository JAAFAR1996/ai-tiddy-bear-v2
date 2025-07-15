from .models import ContractDefinition, ContractTest, ContractTestSuite


async def test_security_service_contracts(framework):
    """اختبار عقود خدمة الأمان"""
    suite = ContractTestSuite(
        name="Security Service Contracts",
        description="عقود API لخدمة الأمان",
        provider="security-service",
        consumer="ai-teddy-bear",
    )

    # Contract 1: Validate Token
    token_validation_contract = ContractDefinition(
        name="Validate Security Token",
        version="1.0",
        provider="security-service",
        consumer="ai-teddy-bear",
        endpoint="/api/v1/security/validate-token",
        method="POST",
        request_schema={
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "device_id": {"type": "string"},
                "permissions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["token", "device_id"],
        },
        response_schema={
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"},
                "user_id": {"type": "string", "format": "uuid"},
                "permissions": {"type": "array", "items": {"type": "string"}},
                "expires_at": {"type": "string", "format": "date-time"},
                "device_verified": {"type": "boolean"},
            },
            "required": ["valid", "user_id", "permissions"],
        },
    )

    suite.contracts.append(token_validation_contract)

    # Test the contract
    test = ContractTest(
        name="test_token_validation_contract",
        description="اختبار عقد التحقق من الرمز المميز",
        contract=token_validation_contract,
        test_data={
            "token": "test-jwt-token",
            "device_id": "test-device-123",
            "permissions": ["read:child", "write:conversation"],
        },
        expected_status=200,
        expected_response_keys=["valid", "user_id", "permissions"],
    )

    result = await framework._execute_contract_test(test)
    suite.test_results.append(result)
    suite.total_tests += 1

    if result.status == "passed":
        suite.passed_tests += 1
    elif result.status == "failed":
        suite.failed_tests += 1
    else:
        suite.error_tests += 1

    framework.test_suites["security-service"] = suite
