"""Provides advanced safety and content filtering services for child interactions.

This service implements sophisticated content analysis, including harmful
content detection, toxicity analysis, emotional impact assessment, and
educational value evaluation. It is dependent on an `AIProvider` for core
AI analysis capabilities and integrates with `PerformanceMonitor` for metrics.
It ensures that all AI responses and user inputs adhere to strict child safety guidelines and COPPA compliance.
"""

from typing import Any

from src.application.interfaces.ai_provider import AIProvider
from src.domain.models.safety_models import (
    ContentCategory,
    ContentModification,
    ContextAnalysis,
    EducationalValue,
    EmotionalImpact,
    RiskLevel,
    SafetyAnalysisResult,
    SafetyConfig,
    ToxicityResult,
)
from src.infrastructure.logging_config import get_logger
from src.infrastructure.monitoring.performance_monitor import (
    PerformanceMonitor,
)

logger = get_logger(__name__, component="services")


class SafetyService:
    """Service for advanced content filtering and safety analysis."""

    def __init__(
        self,
        config: SafetyConfig,
        ai_provider: AIProvider,
        performance_monitor: PerformanceMonitor,
    ) -> None:
        """Initializes the safety service.

        Args:
            config: Safety configuration with filtering rules and thresholds.
            ai_provider: AI provider for advanced content analysis (toxicity, emotion, etc.).
            performance_monitor: Centralized monitor for collecting metrics.

        """
        self.config = config
        self.ai_provider = ai_provider
        self.performance_monitor = performance_monitor
        # self.metrics dictionary removed as metrics are now handled by
        # PerformanceMonitor.

    def _analyze_harmful_content(self, content: str, result: SafetyAnalysisResult):
        """Analyzes content for harmful keywords with comprehensive error handling.

        Args:
            content: The content string to analyze.
            result: The SafetyAnalysisResult object to update.

        """
        try:
            if not content or not isinstance(content, str):
                logger.warning("Invalid content provided for harmful content analysis")
                return
            # Validate result object
            if not result or not isinstance(result, SafetyAnalysisResult):
                logger.error("Invalid SafetyAnalysisResult object provided")
                raise ValueError("Valid SafetyAnalysisResult required for analysis")

            harmful_keywords = self.config.keyword_blacklist
            content_lower = content.lower()
            detected_keywords = [
                keyword for keyword in harmful_keywords if keyword in content_lower
            ]

            if detected_keywords:
                result.is_safe = False
                result.risk_level = RiskLevel.HIGH
                result.content_category = ContentCategory.HARMFUL_CONTENT
                result.modifications.append(
                    ContentModification(
                        type="redaction",
                        description=f"Detected harmful keywords: {detected_keywords}",
                    ),
                )
                logger.warning(f"Harmful content detected: {detected_keywords}")
            else:
                result.is_safe = True
                result.risk_level = RiskLevel.NONE

        except (
            ValueError,
            TypeError,
        ) as e:  # Catching specific input/type related errors
            logger.error(
                f"Validation or type error during harmful content analysis: {e}",
                exc_info=True,
            )
            result.is_safe = False
            result.risk_level = RiskLevel.CRITICAL
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Input/type validation error: {e!s}",
                ),
            )
        except Exception as e:  # Catching any other unexpected errors
            logger.critical(
                f"Unexpected critical error during harmful content analysis: {e}",
                exc_info=True,
            )
            result.is_safe = False
            result.risk_level = RiskLevel.CRITICAL
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Unexpected analysis error: {e!s}",
                ),
            )

    async def _analyze_toxicity(self, content: str, result: SafetyAnalysisResult):
        """Analyzes content for toxicity levels using the AI provider.

        Args:
            content: The content string to analyze.
            result: The SafetyAnalysisResult object to update.

        """
        try:
            toxicity_score = await self.ai_provider.analyze_toxicity(content)
            result.toxicity_result = ToxicityResult(score=toxicity_score)
            if toxicity_score > self.config.toxicity_threshold:
                result.is_safe = False
                result.risk_level = max(result.risk_level, RiskLevel.MEDIUM)
                result.content_category = ContentCategory.TOXIC_CONTENT
                result.modifications.append(
                    ContentModification(
                        type="flag",
                        description=f"Toxicity score: {toxicity_score}",
                    ),
                )
                self.logger.warning(f"Toxicity detected: score={toxicity_score}")
        except Exception as e:
            self.logger.error(f"Error during toxicity analysis: {e}", exc_info=True)
            result.is_safe = False
            result.risk_level = RiskLevel.CRITICAL
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Toxicity analysis error: {e!s}",
                ),
            )

    async def _analyze_emotional_impact(
        self,
        content: str,
        result: SafetyAnalysisResult,
    ):
        """Analyzes the emotional impact of the content using the AI provider.

        Args:
            content: The content string to analyze.
            result: The SafetyAnalysisResult object to update.

        """
        try:
            sentiment_label = await self.ai_provider.analyze_emotion(content)
            # Assuming AIProvider.analyze_emotion provides a simple label.
            # In a real scenario, this might return a more detailed object
            # including scores.
            emotional_impact = EmotionalImpact(
                sentiment=sentiment_label,
                emotions={},
            )  # Populate emotions based on real API response
            result.emotional_impact = emotional_impact
            self.logger.debug(f"Emotional impact analysis complete: {sentiment_label}")
        except Exception as e:
            self.logger.error(
                f"Error during emotional impact analysis: {e}",
                exc_info=True,
            )
            result.emotional_impact = EmotionalImpact(
                sentiment="error",
            )  # Indicate error state
            result.risk_level = max(result.risk_level, RiskLevel.CRITICAL)
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Emotional analysis error: {e!s}",
                ),
            )

    async def _analyze_educational_value(
        self,
        content: str,
        result: SafetyAnalysisResult,
    ):
        """Evaluates the educational value of the content.

        Args:
            content: The content string to analyze.
            result: The SafetyAnalysisResult object to update.

        """
        try:
            educational_value_data = await self.ai_provider.evaluate_educational_value(
                content,
            )
            educational_value = EducationalValue(
                score=educational_value_data.get("score", 0.0),
                topics=educational_value_data.get("topics", []),
            )  # Populate other fields if available from API
            result.educational_value = educational_value
            self.logger.debug(
                f"Educational value analysis complete: {educational_value}",
            )
        except Exception as e:
            self.logger.error(
                f"Error during educational value assessment: {e}",
                exc_info=True,
            )
            result.educational_value = EducationalValue(
                score=0.0,
            )  # Indicate error state
            result.risk_level = max(result.risk_level, RiskLevel.CRITICAL)
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Educational value analysis error: {e!s}",
                ),
            )

    async def _analyze_context(
        self,
        context: dict[str, Any],
        result: SafetyAnalysisResult,
    ):
        """Analyzes the context surrounding the content using the AI provider.

        Args:
            context: The context dictionary.
            result: The SafetyAnalysisResult object to update.

        """
        try:
            # Assuming AIProvider.analyze_context returns a dictionary that can
            # be used to construct ContextAnalysis
            context_result = await self.ai_provider.analyze_context(context)
            context_analysis = ContextAnalysis(
                is_personal_info=context_result.get("is_personal_info", False),
                is_sensitive_topic=context_result.get("is_sensitive_topic", False),
            )
            result.context_analysis = context_analysis
            self.logger.debug(f"Context analysis complete: {context_analysis}")
        except Exception as e:
            self.logger.error(f"Error during context analysis: {e}", exc_info=True)
            result.context_analysis = ContextAnalysis(
                context_safe=False,
            )  # Indicate error state
            result.risk_level = max(result.risk_level, RiskLevel.CRITICAL)
            result.modifications.append(
                ContentModification(
                    type="error",
                    description=f"Context analysis error: {e!s}",
                ),
            )

    async def analyze_content(
        self,
        content: str,
        context: dict[str, Any] | None = None,
    ) -> SafetyAnalysisResult:
        """Performs a comprehensive safety analysis on the given content.

        Args:
            content: The content string to analyze.
            context: Optional. Additional context for analysis.

        Returns:
            A SafetyAnalysisResult object containing the analysis findings.

        """
        await self.performance_monitor.record_safety_check(
            result="total_checked",
        )  # Increment total safety checks

        result = SafetyAnalysisResult(original_content=content)

        # Note: _analyze_harmful_content is synchronous and does not use
        # AIProvider, so it remains synchronous.
        self._analyze_harmful_content(content, result)
        await self._analyze_toxicity(content, result)
        await self._analyze_emotional_impact(content, result)
        await self._analyze_educational_value(content, result)
        if context:
            await self._analyze_context(context, result)

        if not result.is_safe:
            await self.performance_monitor.record_safety_check(
                result="blocked_content",
            )  # Increment blocked content checks

        return result

    def get_metrics(self) -> dict[str, Any]:
        """Retrieves the current safety service metrics.
        These metrics are now collected and managed by the PerformanceMonitor.

        Returns:
            An empty dictionary. Call PerformanceMonitor directly for comprehensive metrics.

        """
        self.logger.warning(
            "SafetyService.get_metrics is deprecated. Use PerformanceMonitor directly for comprehensive metrics.",
        )
        return {}
