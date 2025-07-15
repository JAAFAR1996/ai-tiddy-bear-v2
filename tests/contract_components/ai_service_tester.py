from .models import ContractDefinition, ContractTest, ContractTestSuite


async def test_ai_service_contracts(framework):
    """اختبار عقود خدمة الذكاء الاصطناعي"""
    suite = ContractTestSuite(
        name="AI Service Contracts",
        description="عقود API لخدمة الذكاء الاصطناعي",
        provider="ai-service",
        consumer="ai-teddy-bear",
    )

    # Contract 1: Generate Response
    ai_response_contract = ContractDefinition(
        name="Generate AI Response",
        version="1.0",
        provider="ai-service",
        consumer="ai-teddy-bear",
        endpoint="/api/v1/ai/generate-response",
        method="POST",
        request_schema={
            "type": "object",
            "properties": {
                "child_id": {"type": "string", "format": "uuid"},
                "message": {"type": "string"},
                "context": {"type": "object"},
                "safety_level": {
                    "type": "string",
                    "enum": ["strict", "moderate", "relaxed"],
                },
                "response_type": {
                    "type": "string",
                    "enum": ["text", "audio", "both"],
                },
            },
            "required": ["child_id", "message"],
        },
        response_schema={
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "audio_url": {"type": "string", "format": "uri"},
                "safety_score": {"type": "number", "minimum": 0, "maximum": 1},
                "emotion_detected": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "processing_time_ms": {"type": "number"},
            },
            "required": ["response", "safety_score"],
        },
    )

    suite.contracts.append(ai_response_contract)

    # Test the contract
    test = ContractTest(
        name="test_ai_response_contract",
        description="اختبار عقد توليد استجابة الذكاء الاصطناعي",
        contract=ai_response_contract,
        test_data={
            "child_id": "test-child-123",
            "message": "Hello Teddy!",
            "context": {"previous_messages": []},
            "safety_level": "strict",
            "response_type": "text",
        },
        expected_status=200,
        expected_response_keys=["response", "safety_score"],
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

    framework.test_suites["ai-service"] = suite
