from .models import ContractDefinition, ContractTest, ContractTestSuite


async def test_parent_service_contracts(framework):
    """اختبار عقود خدمة الوالدين"""
    suite = ContractTestSuite(
        name="Parent Service Contracts",
        description="عقود API لخدمة الوالدين",
        provider="parent-service",
        consumer="ai-teddy-bear",
    )

    # Contract 1: Get Parent Dashboard
    parent_dashboard_contract = ContractDefinition(
        name="Get Parent Dashboard",
        version="1.0",
        provider="parent-service",
        consumer="ai-teddy-bear",
        endpoint="/api/v1/parents/{parent_id}/dashboard",
        method="GET",
        request_schema={
            "type": "object",
            "properties": {
                "parent_id": {"type": "string", "format": "uuid"},
                "date_range": {
                    "type": "string",
                    "enum": ["today", "week", "month", "year"],
                },
            },
            "required": ["parent_id"],
        },
        response_schema={
            "type": "object",
            "properties": {
                "parent_id": {"type": "string", "format": "uuid"},
                "children": {"type": "array", "items": {"type": "object"}},
                "conversation_summary": {"type": "object"},
                "safety_alerts": {"type": "array", "items": {"type": "object"}},
                "learning_progress": {"type": "object"},
                "last_updated": {"type": "string", "format": "date-time"},
            },
            "required": ["parent_id", "children", "conversation_summary"],
        },
    )

    suite.contracts.append(parent_dashboard_contract)

    # Test the contract
    test = ContractTest(
        name="test_parent_dashboard_contract",
        description="اختبار عقد لوحة تحكم الوالدين",
        contract=parent_dashboard_contract,
        test_data={"parent_id": "test-parent-123", "date_range": "week"},
        expected_status=200,
        expected_response_keys=[
            "parent_id",
            "children",
            "conversation_summary"],
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

    framework.test_suites["parent-service"] = suite
