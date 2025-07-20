#!/usr/bin/env python3
"""📋 Contract Testing Framework - AI Teddy Bear Project
اختبارات العقد لضمان توافق APIs والخدمات

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

from src.infrastructure.logging_config import get_logger

from .contract_components import (
    _calculate_overall_results,
    _generate_recommendations,
    execute_contract_test,
    test_ai_service_contracts,
    test_audio_service_contracts,
    test_child_service_contracts,
    test_parent_service_contracts,
    test_security_service_contracts,
    validate_against_schema,
)

# Configure logging
logging.basicConfig(level=logging.INFO)

logger = get_logger(__name__, component="test")


class ContractDefinition(BaseModel):
    """تعريف عقد API"""

    name: str
    version: str
    provider: str
    consumer: str
    endpoint: str
    method: str
    request_schema: dict[str, Any]
    response_schema: dict[str, Any]
    headers: dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = 30


class ContractTest(BaseModel):
    """اختبار عقد واحد"""

    name: str
    description: str
    contract: ContractDefinition
    test_data: dict[str, Any]
    expected_status: int = 200
    expected_response_keys: list[str] = Field(default_factory=list)
    validation_rules: dict[str, Any] = Field(default_factory=dict)


class ContractResult(BaseModel):
    """نتيجة اختبار عقد"""

    test_name: str
    contract_name: str
    status: str  # passed, failed, error
    request_sent: dict[str, Any]
    response_received: dict[str, Any] | None = None
    response_status: int | None = None
    validation_errors: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ContractTestSuite(BaseModel):
    """مجموعة اختبارات العقد"""

    name: str
    description: str
    provider: str
    consumer: str
    contracts: list[ContractDefinition] = Field(default_factory=list)
    test_results: list[ContractResult] = Field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0


class ContractTestingFramework:
    """إطار اختبارات العقد الشامل"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_suites: dict[str, Any] = {}
        self.session: aiohttp.ClientSession | None = None
        self._execute_contract_test = execute_contract_test
        self._validate_against_schema = validate_against_schema

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()

    async def run_contract_testing(self) -> dict[str, Any]:
        """تشغيل جميع اختبارات العقد"""
        logger.info("📋 بدء اختبارات العقد...")

        start_time = asyncio.get_event_loop().time()

        # Define contracts for different services
        await test_child_service_contracts(self)
        await test_audio_service_contracts(self)
        await test_ai_service_contracts(self)
        await test_security_service_contracts(self)
        await test_parent_service_contracts(self)

        execution_time = asyncio.get_event_loop().time() - start_time

        # Calculate overall results
        overall_results = _calculate_overall_results(self.test_suites)

        return {
            "test_suites": self.test_suites,
            "overall_results": overall_results,
            "execution_time": execution_time,
            "recommendations": _generate_recommendations(self),
        }


async def test_contract_framework():
    """اختبار إطار اختبارات العقد"""
    async with ContractTestingFramework() as framework:
        results = await framework.run_contract_testing()

        print("📋 نتائج اختبارات العقد:")
        print(f"إجمالي الاختبارات: {results['overall_results']['total_tests']}")
        print(f"الاختبارات الناجحة: {results['overall_results']['passed_tests']}")
        print(f"معدل النجاح: {results['overall_results']['success_rate']:.1f}%")

        print("\n📋 التوصيات:")
        for rec in results["recommendations"]:
            print(f"  {rec}")


if __name__ == "__main__":
    asyncio.run(test_contract_framework())
