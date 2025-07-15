from .models import ContractDefinition, ContractTest, ContractTestSuite


async def test_audio_service_contracts(framework):
    """اختبار عقود خدمة الصوت"""
    suite = ContractTestSuite(
        name="Audio Service Contracts",
        description="عقود API لخدمة معالجة الصوت",
        provider="audio-service",
        consumer="ai-teddy-bear",
    )

    # Contract 1: Process Audio
    audio_process_contract = ContractDefinition(
        name="Process Audio",
        version="1.0",
        provider="audio-service",
        consumer="ai-teddy-bear",
        endpoint="/api/v1/audio/process",
        method="POST",
        request_schema={
            "type": "object",
            "properties": {
                "audio_data": {"type": "string", "format": "base64"},
                "format": {"type": "string", "enum": ["wav", "mp3", "flac"]},
                "sample_rate": {
                    "type": "integer",
                    "minimum": 8000,
                    "maximum": 48000,
                },
                "language": {"type": "string", "default": "en"},
            },
            "required": ["audio_data", "format"],
        },
        response_schema={
            "type": "object",
            "properties": {
                "transcription": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "language_detected": {"type": "string"},
                "processing_time_ms": {"type": "number"},
                "status": {"type": "string", "enum": ["success", "error"]},
            },
            "required": ["transcription", "confidence", "status"],
        },
    )

    suite.contracts.append(audio_process_contract)

    # Test the contract
    test = ContractTest(
        name="test_audio_process_contract",
        description="اختبار عقد معالجة الصوت",
        contract=audio_process_contract,
        test_data={
            "audio_data": "base64_encoded_audio_data",
            "format": "wav",
            "sample_rate": 16000,
            "language": "en",
        },
        expected_status=200,
        expected_response_keys=["transcription", "confidence", "status"],
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

    framework.test_suites["audio-service"] = suite
