from typing import Any

from src.domain.models.safety_bias_models import ConversationContext
from src.domain.models.safety_models.risk_level import RiskLevel
from src.domain.models.safety_models.safety_analysis_result import SafetyAnalysisResult


class AIBiasDetector:
    def __init__(self) -> None:
        self.bias_statistics = {
            "total_analyses": 0,
            "biased_responses": 0,
            "gender_bias_detected": 0,
            "cultural_bias_detected": 0,
            "socioeconomic_bias_detected": 0,
            "age_bias_detected": 0,
            "ability_bias_detected": 0,
            # يجب تحديث الدقة من نتائج تقييم حقيقية أو تركها None مع توثيق
            "system_accuracy": None,  # Set by evaluation pipeline
            "detection_method": "Rule-based + Keyword Matching",
        }

    async def detect_bias(
        self,
        response_text: str,
        context: ConversationContext,
    ) -> SafetyAnalysisResult:
        import logging

        logger = logging.getLogger("ai_bias_detector")
        self.bias_statistics["total_analyses"] += 1
        has_bias = False
        bias_scores = {}
        bias_categories = []
        mitigation_suggestions = []
        overall_bias_score = 0.0
        risk_level = RiskLevel.SAFE
        detected_patterns = []
        contextual_bias = {}

        # منطق الكشف عن التحيز (قابل للتوسعة أو الربط مع نموذج ML)
        def rule_based_bias_detection(text: str, ctx: ConversationContext):
            found_bias = False
            scores = {}
            categories = []
            suggestions = []
            contextual = {}
            # Gender bias
            if (
                "girls are naturally better" in text.lower()
                or "boys are stronger" in text.lower()
            ):
                found_bias = True
                scores["gender"] = 0.7
                categories.append("gender")
                suggestions.append("Use gender-neutral language.")
                self.bias_statistics["gender_bias_detected"] += 1
            # Cultural bias
            if "normal families celebrate christmas" in text.lower():
                found_bias = True
                scores["cultural"] = 0.6
                categories.append("cultural")
                suggestions.append("Be inclusive of diverse cultural backgrounds.")
                self.bias_statistics["cultural_bias_detected"] += 1
            # Socioeconomic bias
            if "expensive new toy" in text.lower() or "rich families" in text.lower():
                found_bias = True
                scores["socioeconomic"] = 0.5
                categories.append("socioeconomic")
                suggestions.append("Avoid assumptions about socioeconomic status.")
                self.bias_statistics["socioeconomic_bias_detected"] += 1
            # Age bias
            if "too young to understand" in text.lower():
                found_bias = True
                scores["age"] = 0.4
                categories.append("age")
                suggestions.append(
                    "Tailor content to age-appropriate levels without being dismissive."
                )
                self.bias_statistics["age_bias_detected"] += 1
            # Contextual bias
            if "gender_assumption" in ctx.conversation_history:
                contextual["gender_assumption"] = 0.3
            return found_bias, scores, categories, suggestions, contextual

        (
            has_bias,
            bias_scores,
            bias_categories,
            mitigation_suggestions,
            contextual_bias,
        ) = rule_based_bias_detection(response_text, context)

        if has_bias:
            self.bias_statistics["biased_responses"] += 1
            overall_bias_score = max(bias_scores.values())
            if overall_bias_score > 0.5:
                risk_level = RiskLevel.HIGH_RISK
            elif overall_bias_score > 0.2:
                risk_level = RiskLevel.MEDIUM_RISK
            else:
                risk_level = RiskLevel.LOW_RISK

        logger.info(
            f"Bias analysis: text='{response_text[:50]}...' has_bias={has_bias}, categories={bias_categories}, scores={bias_scores}"
        )

        return SafetyAnalysisResult(
            is_safe=not has_bias,
            overall_risk_level=risk_level,
            bias_scores=bias_scores,
            bias_categories=bias_categories,
            mitigation_suggestions=mitigation_suggestions,
            overall_bias_score=overall_bias_score,
            detected_patterns=detected_patterns,
            contextual_bias=contextual_bias,
        )

    async def batch_analyze_bias(
        self,
        responses: list[str],
        contexts: list[ConversationContext],
    ) -> list[SafetyAnalysisResult]:
        results = []
        for i, response in enumerate(responses):
            context = (
                contexts[i] if i < len(contexts) else ConversationContext(child_age=0)
            )  # Default context if not provided
            results.append(await self.detect_bias(response, context))
        return results

    def get_bias_statistics(self) -> dict[str, Any]:
        return self.bias_statistics

    async def generate_bias_report(
        self, results: list[SafetyAnalysisResult]
    ) -> dict[str, Any]:
        summary = {
            "total_responses_analyzed": len(results),
            "total_biased_responses": sum(1 for r in results if r.has_bias),
            "average_bias_score": (
                sum(r.overall_bias_score for r in results) / len(results)
                if results
                else 0
            ),
        }
        bias_breakdown = {}
        recommendations = []
        for result in results:
            for category in result.bias_categories:
                bias_breakdown[category] = bias_breakdown.get(category, 0) + 1
            recommendations.extend(result.mitigation_suggestions)
        return {
            "summary": summary,
            "bias_breakdown": bias_breakdown,
            "recommendations": list(set(recommendations)),  # Remove duplicates
        }
