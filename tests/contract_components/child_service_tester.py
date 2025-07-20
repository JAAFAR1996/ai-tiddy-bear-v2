from .models import ContractDefinition, ContractTest, ContractTestSuite


async def test_child_service_contracts(framework):
    """اختبار عقود خدمة الطفل"""
    suite = ContractTestSuite(
        name="Child Service Contracts",
        description="عقود API لخدمة الطفل",
        provider="child-service",
        consumer="ai-teddy-bear",
    )

    # Contract 1: Get Child Profile
    child_profile_contract = ContractDefinition(
        name="Get Child Profile",
        version="1.0",
        provider="child-service",
        consumer="ai-teddy-bear",
        endpoint="/api/v1/children/{child_id}",
        method="GET",
        request_schema={
            "type": "object",
            "properties": {"child_id": {"type": "string", "format": "uuid"}},
            "required": ["child_id"],
        },
        response_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 18},
                "preferences": {"type": "object"},
                "safety_settings": {"type": "object"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
            },
            "required": [
                "id",
                "name",
                "age",
                "preferences",
                "safety_settings",
            ],
        },
    )

    suite.contracts.append(child_profile_contract)

    # Test the contract
    test = ContractTest(
        name="test_get_child_profile_contract",
        description="اختبار عقد الحصول على ملف الطفل",
        contract=child_profile_contract,
        test_data={"child_id": "test-child-123"},
        expected_status=200,
        expected_response_keys=[
            "id",
            "name",
            "age",
            "preferences",
            "safety_settings",
        ],
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

    framework.test_suites["child-service"] = suite
