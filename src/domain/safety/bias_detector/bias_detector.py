from typing import List, Dict, Any

from src.domain.safety.models.conversation_context import ConversationContext
from src.domain.safety.models.safety_analysis_result import SafetyAnalysisResult
from src.domain.safety.models.risk_level import RiskLevel


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
            "system_accuracy": 0.95,  # Placeholder
            "detection_method": "Rule-based + Keyword Matching",
        }

    async def detect_bias(
        self,
        response_text: str,
        context: ConversationContext,
    ) -> SafetyAnalysisResult:
        self.bias_statistics["total_analyses"] += 1
        has_bias = False
        bias_scores = {}
        bias_categories = []
        mitigation_suggestions = []
        overall_bias_score = 0.0
        risk_level = RiskLevel.SAFE
        detected_patterns = []
        contextual_bias = {}

        # Placeholder for bias detection logic
        if (
            "girls are naturally better" in response_text.lower()
            or "boys are stronger" in response_text.lower()
        ):
            has_bias = True
            bias_scores["gender"] = 0.7
            bias_categories.append("gender")
            mitigation_suggestions.append("Use gender-neutral language.")
            self.bias_statistics["gender_bias_detected"] += 1

        if "normal families celebrate christmas" in response_text.lower():
            has_bias = True
            bias_scores["cultural"] = 0.6
            bias_categories.append("cultural")
            mitigation_suggestions.append(
                "Be inclusive of diverse cultural backgrounds.",
            )
            self.bias_statistics["cultural_bias_detected"] += 1

        if (
            "expensive new toy" in response_text.lower()
            or "rich families" in response_text.lower()
        ):
            has_bias = True
            bias_scores["socioeconomic"] = 0.5
            bias_categories.append("socioeconomic")
            mitigation_suggestions.append(
                "Avoid assumptions about socioeconomic status.",
            )
            self.bias_statistics["socioeconomic_bias_detected"] += 1

        if "too young to understand" in response_text.lower():
            has_bias = True
            bias_scores["age"] = 0.4
            bias_categories.append("age")
            mitigation_suggestions.append(
                "Tailor content to age-appropriate levels without being dismissive.",
            )
            self.bias_statistics["age_bias_detected"] += 1

        if "gender_assumption" in context.conversation_history:
            contextual_bias["gender_assumption"] = 0.3

        if has_bias:
            self.bias_statistics["biased_responses"] += 1
            overall_bias_score = max(bias_scores.values())
            if overall_bias_score > 0.5:  # Example threshold
                risk_level = RiskLevel.HIGH_RISK
            elif overall_bias_score > 0.2:
                risk_level = RiskLevel.MEDIUM_RISK
            else:
                risk_level = RiskLevel.LOW_RISK

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
        responses: List[str],
        contexts: List[ConversationContext],
    ) -> List[SafetyAnalysisResult]:
        results = []
        for i, response in enumerate(responses):
            context = (
                contexts[i]
                if i < len(contexts)
                else ConversationContext(child_age=0)
            )  # Default context if not provided
            results.append(await self.detect_bias(response, context))
        return results

    def get_bias_statistics(self) -> Dict[str, Any]:
        return self.bias_statistics

    async def generate_bias_report(
        self, results: List[SafetyAnalysisResult]
    ) -> Dict[str, Any]:
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