#!/usr/bin/env python3
"""
🧬 Mutation Testing Framework - AI Teddy Bear Project
اختبارات الطفرة لضمان جودة الاختبارات وتغطية الحالات الحدية

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import ast
import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="test")


class MutationOperator(BaseModel):
    """مشغل طفرة واحد"""

    name: str
    description: str
    pattern: str
    replacement: str
    category: str  # arithmetic, logical, comparison, etc.


class MutationResult(BaseModel):
    """نتيجة طفرة واحدة"""

    file_path: str
    line_number: int
    original_code: str
    mutated_code: str
    operator: str
    killed: bool = False
    test_failure: Optional[str] = None
    execution_time: float = 0.0


class MutationTestSuite(BaseModel):
    """مجموعة اختبارات الطفرة"""

    name: str
    total_mutations: int = 0
    killed_mutations: int = 0
    survived_mutations: int = 0
    mutation_score: float = 0.0
    results: List[MutationResult] = Field(default_factory=list)
    execution_time: float = 0.0


class MutationTestingFramework:
    """إطار اختبارات الطفرة الشامل"""

    def __init__(self):
        self.mutation_operators = self._initialize_mutation_operators()
        self.test_suites: Dict[str, MutationTestSuite] = {}

    def _initialize_mutation_operators(self) -> List[MutationOperator]:
        """تهيئة مشغلات الطفرة"""
        return [
            # Arithmetic Operators
            MutationOperator(
                name="AOR (Arithmetic Operator Replacement)",
                description="استبدال مشغلات الحساب",
                pattern="+",
                replacement="-",
                category="arithmetic",
            ),
            MutationOperator(
                name="AOR",
                description="استبدال مشغلات الحساب",
                pattern="-",
                replacement="+",
                category="arithmetic",
            ),
            MutationOperator(
                name="AOR",
                description="استبدال مشغلات الحساب",
                pattern="*",
                replacement="/",
                category="arithmetic",
            ),
            MutationOperator(
                name="AOR",
                description="استبدال مشغلات الحساب",
                pattern="/",
                replacement="*",
                category="arithmetic",
            ),
            # Logical Operators
            MutationOperator(
                name="LOR (Logical Operator Replacement)",
                description="استبدال المشغلات المنطقية",
                pattern="and",
                replacement="or",
                category="logical",
            ),
            MutationOperator(
                name="LOR",
                description="استبدال المشغلات المنطقية",
                pattern="or",
                replacement="and",
                category="logical",
            ),
            MutationOperator(
                name="LOR",
                description="استبدال المشغلات المنطقية",
                pattern="not",
                replacement="",
                category="logical",
            ),
            # Comparison Operators
            MutationOperator(
                name="COR (Comparison Operator Replacement)",
                description="استبدال مشغلات المقارنة",
                pattern="==",
                replacement="!=",
                category="comparison",
            ),
            MutationOperator(
                name="COR",
                description="استبدال مشغلات المقارنة",
                pattern="!=",
                replacement="==",
                category="comparison",
            ),
            MutationOperator(
                name="COR",
                description="استبدال مشغلات المقارنة",
                pattern="<",
                replacement=">=",
                category="comparison",
            ),
            MutationOperator(
                name="COR",
                description="استبدال مشغلات المقارنة",
                pattern=">",
                replacement="<=",
                category="comparison",
            ),
            # String Operators
            MutationOperator(
                name="SOR (String Operator Replacement)",
                description="استبدال مشغلات النصوص",
                pattern="+",
                replacement="",
                category="string",
            ),
            # Return Statement
            MutationOperator(
                name="ROR (Return Operator Replacement)",
                description="استبدال return بـ pass",
                pattern="return",
                replacement="pass",
                category="return",
            ),
        ]

    async def run_mutation_testing(self, target_files: List[str]) -> Dict[str, Any]:
        """تشغيل اختبارات الطفرة على الملفات المستهدفة"""
        logger.info("🧬 بدء اختبارات الطفرة...")

        start_time = asyncio.get_event_loop().time()

        for file_path in target_files:
            if not Path(file_path).exists():
                logger.warning(f"⚠️ الملف غير موجود: {file_path}")
                continue

            suite = await self._mutate_file(file_path)
            self.test_suites[file_path] = suite

        execution_time = asyncio.get_event_loop().time() - start_time

        # Calculate overall results
        overall_results = self._calculate_overall_results()

        return {
            "test_suites": self.test_suites,
            "overall_results": overall_results,
            "execution_time": execution_time,
            "recommendations": self._generate_recommendations(),
        }

    async def _mutate_file(self, file_path: str) -> MutationTestSuite:
        """إجراء طفرات على ملف واحد"""
        logger.info(f"🧬 إجراء طفرات على: {file_path}")

        suite = MutationTestSuite(name=f"Mutation Tests for {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Parse the file
            tree = ast.parse(original_content)

            # Find all lines that can be mutated
            mutable_lines = self._find_mutable_lines(tree, original_content)

            for line_num, line_content in mutable_lines:
                for operator in self.mutation_operators:
                    if operator.pattern in line_content:
                        result = await self._apply_mutation(
                            file_path,
                            line_num,
                            line_content,
                            operator,
                            original_content,
                        )
                        if result:
                            suite.results.append(result)
                            suite.total_mutations += 1

                            if result.killed:
                                suite.killed_mutations += 1
                            else:
                                suite.survived_mutations += 1

            # Calculate mutation score
            if suite.total_mutations > 0:
                suite.mutation_score = (
                    suite.killed_mutations / suite.total_mutations
                ) * 100

        except Exception as e:
            logger.error(f"❌ خطأ في إجراء طفرات على {file_path}: {e}")

        return suite

    def _find_mutable_lines(self, tree: ast.AST, content: str) -> List[Tuple[int, str]]:
        """العثور على الأسطر القابلة للطفرة"""
        lines = content.split("\n")
        mutable_lines = []

        for node in ast.walk(tree):
            if hasattr(node, "lineno"):
                line_num = node.lineno - 1  # Convert to 0-based index
                if line_num < len(lines):
                    line_content = lines[line_num].strip()
                    if line_content and not line_content.startswith("#"):
                        mutable_lines.append((line_num + 1, line_content))

        return list(set(mutable_lines))  # Remove duplicates

    async def _apply_mutation(
        self,
        file_path: str,
        line_num: int,
        line_content: str,
        operator: MutationOperator,
        original_content: str,
    ) -> Optional[MutationResult]:
        """تطبيق طفرة واحدة"""
        try:
            # Create mutated content
            lines = original_content.split("\n")
            mutated_line = line_content.replace(operator.pattern, operator.replacement)
            lines[line_num - 1] = lines[line_num - 1].replace(
                line_content, mutated_line
            )
            mutated_content = "\n".join(lines)

            # Create temporary file with mutation
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(mutated_content)
                temp_file = f.name

            # Run tests against mutated code
            start_time = asyncio.get_event_loop().time()
            killed = await self._run_tests_against_mutation(temp_file)
            execution_time = asyncio.get_event_loop().time() - start_time

            # Clean up temporary file
            os.unlink(temp_file)

            return MutationResult(
                file_path=file_path,
                line_number=line_num,
                original_code=line_content,
                mutated_code=mutated_line,
                operator=operator.name,
                killed=killed,
                execution_time=execution_time,
            )

        except Exception as e:
            logger.error(f"❌ خطأ في تطبيق الطفرة: {e}")
            return None

    async def _run_tests_against_mutation(self, mutated_file: str) -> bool:
        """تشغيل الاختبارات ضد الكود المتحور"""
        try:
            # Run pytest on the mutated file
            result = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "pytest",
                mutated_file,
                "-v",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            # If tests fail, the mutation is killed (good)
            return result.returncode != 0

        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل الاختبارات: {e}")
            return False

    def _calculate_overall_results(self) -> Dict[str, Any]:
        """حساب النتائج الإجمالية"""
        total_mutations = sum(
            suite.total_mutations for suite in self.test_suites.values()
        )
        total_killed = sum(
            suite.killed_mutations for suite in self.test_suites.values()
        )
        total_survived = sum(
            suite.survived_mutations for suite in self.test_suites.values()
        )

        overall_score = (
            (total_killed / total_mutations * 100) if total_mutations > 0 else 0
        )

        return {
            "total_mutations": total_mutations,
            "killed_mutations": total_killed,
            "survived_mutations": total_survived,
            "mutation_score": overall_score,
            "files_tested": len(self.test_suites),
        }

    def _generate_recommendations(self) -> List[str]:
        """توليد توصيات لتحسين الاختبارات"""
        recommendations = []

        overall_results = self._calculate_overall_results()

        if overall_results["mutation_score"] < 80:
            recommendations.append("🔴 معدل قتل الطفرات منخفض - تحتاج اختبارات إضافية")

        if overall_results["survived_mutations"] > 0:
            recommendations.append(
                "🟡 بعض الطفرات نجت - راجع الاختبارات للحالات الحدية"
            )

        for file_path, suite in self.test_suites.items():
            if suite.mutation_score < 70:
                recommendations.append(
                    f"🔴 {file_path}: معدل قتل الطفرات منخفض ({suite.mutation_score:.1f}%)"
                )

        if not recommendations:
            recommendations.append("✅ معدل قتل الطفرات ممتاز - الاختبارات قوية")

        return recommendations


# Test the mutation testing framework


async def test_mutation_framework():
    """اختبار إطار اختبارات الطفرة"""
    framework = MutationTestingFramework()

    # Test files to mutate
    target_files = [
        "src/domain/entities/child.py",
        "src/application/services/child_interaction_service.py",
        "src/infrastructure/security/encryption_service.py",
    ]

    results = await framework.run_mutation_testing(target_files)

    print("🧬 نتائج اختبارات الطفرة:")
    print(f"إجمالي الطفرات: {results['overall_results']['total_mutations']}")
    print(f"الطفرات المقتولة: {results['overall_results']['killed_mutations']}")
    print(f"معدل القتل: {results['overall_results']['mutation_score']:.1f}%")

    print("\n📋 التوصيات:")
    for rec in results["recommendations"]:
        print(f"  {rec}")


if __name__ == "__main__":
    asyncio.run(test_mutation_framework())
