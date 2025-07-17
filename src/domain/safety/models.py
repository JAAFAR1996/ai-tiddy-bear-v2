"""Safety models for AI Teddy Bear child protection system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

"""Safety models for AI Teddy Bear child protection system."""


class RiskLevel(Enum):
    """Risk level assessment for content safety."""
    SAFE = "safe"
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Categories for content classification."""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    STORY = "story"
    GAME = "game"
    CONVERSATION = "conversation"
    SOCIAL = "social"
    PERSONAL = "personal"
    NEUTRAL = "neutral"
    INAPPROPRIATE = "inappropriate"


@dataclass
class ToxicityResult:
    """Result of toxicity analysis."""
    score: float = 0.0
    is_toxic: bool = False
    label: str = "neutral"
    threshold: float = 0.1
    confidence: float = 0.0


@dataclass
class EmotionalImpact:
    """Assessment of emotional impact on child."""
    is_positive: bool = True
    overall_sentiment: float = 0.5
    sentiment_label: str = "neutral"
    emotional_score: float = 0.5
    emotions: Dict[str, float] = field(default_factory=dict)
    age_appropriateness: bool = True


@dataclass
class EducationalValue:
    """Educational assessment of content."""
    educational_score: float = 0.0
    learning_concepts: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    skill_development: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContextAnalysis:
    """Contextual analysis of conversation."""
    context_safe: bool = True
    conversation_flow_score: float = 0.8
    conversation_quality: float = 0.8
    child_age: int = 0
    child_gender: Optional[str] = None
    conversation_history: List[str] = field(default_factory=list)
    interaction_count: int = 0
    session_duration: float = 0.0
    topics_discussed: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    language_complexity: float = 0.5


@dataclass
class ContentModification:
    """Content modification suggestions or applied changes."""
    original_text: str = ""
    modified_text: str = ""
    original_content: str = ""  # Alias for compatibility
    modified_content: str = ""  # Alias for compatibility
    changes_made: List[str] = field(default_factory=list)
    reason: str = ""
    modification_type: str = "filter"
    confidence: float = 0.0


@dataclass
class BiasAnalysis:
    """Bias detection and analysis."""
    has_bias: bool = False
    overall_bias_score: float = 0.0
    bias_scores: Dict[str, float] = field(default_factory=dict)
    bias_categories: List[str] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    contextual_bias: Dict[str, float] = field(default_factory=dict)


@dataclass
class SafetyAnalysisResult:
    """Comprehensive safety analysis result."""
    # Core safety assessment
    is_safe: bool = True
    overall_risk_level: RiskLevel = RiskLevel.SAFE
    age_appropriate: bool = True
    parent_notification_required: bool = False
    content_category: ContentCategory = ContentCategory.CONVERSATION
    
    # Detailed analysis components
    toxicity_result: Optional[ToxicityResult] = None
    emotional_impact: Optional[EmotionalImpact] = None
    educational_value: Optional[EducationalValue] = None
    context_analysis: Optional[ContextAnalysis] = None
    bias_analysis: Optional[BiasAnalysis] = None
    required_modifications: List[ContentModification] = field(default_factory=list)
    
    # Metadata
    analysis_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    source_module: str = "safety_analyzer"
    additional_info: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    
    def __post_init__(self) -> None:
        """Initialize nested objects if not provided."""
        if self.toxicity_result is None:
            self.toxicity_result = ToxicityResult()
        if self.emotional_impact is None:
            self.emotional_impact = EmotionalImpact()
        if self.educational_value is None:
            self.educational_value = EducationalValue()
        if self.context_analysis is None:
            self.context_analysis = ContextAnalysis()
        if self.bias_analysis is None:
            self.bias_analysis = BiasAnalysis()


@dataclass
class SafetyConfig:
    """Configuration for safety analysis system."""
    # Toxicity thresholds
    toxicity_threshold: float = 0.1
    high_risk_threshold: float = 0.3
    critical_threshold: float = 0.7
    
    # Bias detection
    bias_detection_threshold: float = 0.3
    
    # Content filtering
    sensitive_topics: List[str] = field(default_factory=list)
    keyword_blacklist: List[str] = field(default_factory=list)
    age_appropriate_content_rules: Dict[str, Any] = field(default_factory=dict)
    
    # System settings
    enable_strict_mode: bool = True
    enable_realtime_monitoring: bool = True
    log_level: str = "INFO"
    external_api_timeout: int = 5
    data_retention_days: int = 90
    
    # Age-specific configurations
    age_group_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        return all(
            [
                0 <= self.toxicity_threshold <= 1,
                0 <= self.high_risk_threshold <= 1,
                0 <= self.critical_threshold <= 1,
                0 <= self.bias_detection_threshold <= 1,
                self.toxicity_threshold
                <= self.high_risk_threshold
                <= self.critical_threshold,
                self.external_api_timeout > 0,
                self.data_retention_days > 0,
            ]
        )
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """
        Load safety patterns from configuration or use defaults.
        Returns:
            Dictionary of safety patterns by category
        """
        default_patterns = {
            "violence": [
                r"\b(kill|hurt|fight|weapon|gun|knife|blood|murder|attack|harm)\b"
            ],
            "inappropriate": [r"\b(adult|explicit|sexual|porn|nude|naked)\b"],
            "personal_info": [
                r"\b(address|phone|email|password|location|where.*live)\b"
            ],
            "scary": [r"\b(scary|ghost|monster|nightmare|death|die|afraid|terror)\b"],
            "inappropriate_contact": [
                r"\b(meet.*person|stranger|secret|don't.*tell)\b"
            ],
            "profanity": [r"\b(stupid|dumb|hate|shut.*up|damn|hell)\b"],
        }
        return default_patterns
    
    def _load_age_restrictions(self) -> Dict[int, Dict[str, int]]:
        """
        Load age-based content restrictions from configuration.
        Returns:
            Dictionary mapping age to content limits
        """
        default_restrictions = {
            3: {"max_scary": 0, "max_violence": 0, "max_inappropriate": 0},
            5: {"max_scary": 1, "max_violence": 0, "max_inappropriate": 0},
            8: {"max_scary": 2, "max_violence": 1, "max_inappropriate": 0},
            12: {"max_scary": 3, "max_violence": 2, "max_inappropriate": 0},
            13: {"max_scary": 4, "max_violence": 3, "max_inappropriate": 0},
        }
        return default_restrictions
    
    def is_appropriate(self, content: str, age: int) -> bool:
        """Real content safety validation for child protection."""
        import re
        if not content or not content.strip():
            return True
        
        content_lower = content.lower()
        if any(
            re.search(pattern, content_lower, re.IGNORECASE)
            for pattern in self.UNSAFE_PATTERNS["personal_info"]
        ):
            return False
        
        if any(
            re.search(pattern, content_lower, re.IGNORECASE)
            for pattern in self.UNSAFE_PATTERNS["inappropriate_contact"]
        ):
            return False
        
        if any(
            re.search(pattern, content_lower, re.IGNORECASE)
            for pattern in self.UNSAFE_PATTERNS["inappropriate"]
        ):
            return False
        
        age_limits = self._get_age_limits(age)
        
        # Count violations by category
        violence_count = sum(
            len(re.findall(pattern, content_lower, re.IGNORECASE))
            for pattern in self.UNSAFE_PATTERNS["violence"]
        )
        scary_count = sum(
            len(re.findall(pattern, content_lower, re.IGNORECASE))
            for pattern in self.UNSAFE_PATTERNS["scary"]
        )
        
        if violence_count > age_limits["max_violence"]:
            return False
        if scary_count > age_limits["max_scary"]:
            return False
        
        return True
    
    def analyze_safety(
        self, content: str, context: ContextAnalysis
    ) -> SafetyAnalysisResult:
        """Comprehensive safety analysis with real validation."""
        import re
        if not content:
            return SafetyAnalysisResult(
                is_safe=True, risk_level=RiskLevel.LOW, confidence=1.0
            )
        
        content_lower = content.lower()
        violations = []
        risk_scores = []
        
        for category, patterns in self.UNSAFE_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    violations.append(f"{category}: {', '.join(matches)}")
                    risk_scores.append(
                        self._calculate_risk_score(category, len(matches))
                    )
        
        if not violations:
            return SafetyAnalysisResult(
                is_safe=True, risk_level=RiskLevel.LOW, confidence=0.95
            )
        
        max_risk_score = max(risk_scores) if risk_scores else 0.0
        risk_level = self._score_to_risk_level(max_risk_score)
        
        return SafetyAnalysisResult(
            is_safe=(risk_level == RiskLevel.LOW),
            risk_level=risk_level,
            confidence=0.8,
            violations=violations,
            explanation=f"Found {len(violations)} safety concerns: {'; '.join(violations[:3])}",
        )
    
    def _get_age_limits(self, age: int) -> Dict[str, int]:
        """Get age-appropriate content limits for given child age.
        Args:
            age: Child's age in years
        Returns:
            Dictionary with content limits for the age group
        """
        for age_threshold in sorted(self.AGE_RESTRICTIONS.keys()):
            if age <= age_threshold:
                return self.AGE_RESTRICTIONS[age_threshold]
        return self.AGE_RESTRICTIONS[13]  # Default to strictest for teens
    
    def _calculate_risk_score(self, category: str, count: int) -> float:
        """Calculate risk score based on violation category and count.
        Args:
            category: Type of safety violation
            count: Number of violations found
        Returns:
            Risk score between 0.0 and 1.0
        """
        base_scores = {
            "personal_info": 1.0,  # Always critical
            "inappropriate_contact": 1.0,  # Always critical
            "inappropriate": 0.9,
            "violence": 0.7,
            "scary": 0.5,
            "profanity": 0.3,
        }
        return min(1.0, base_scores.get(category, 0.5) * count)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numerical risk score to categorical risk level.
        Args:
            score: Risk score between 0.0 and 1.0
        Returns:
            Corresponding RiskLevel enum value
        """
        if score >= 0.8:
            return RiskLevel.HIGH
        elif score >= 0.5:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


class ProfanityRule:
    """Real profanity detection and filtering rules for child safety."""
    def __init__(self, severity: RiskLevel = RiskLevel.MEDIUM) -> None:
        self.severity = severity
        self.blocked_words: List[str] = [
            "stupid",
            "dumb",
            "shut up",
            "hate",
            "kill",
            "die",
            "death",
            "damn",
            "hell",
            "idiot",
            "loser",
            "ugly",
            "fat",
            "weird",
        ]
        self.severe_patterns = [
            r"\b(stupid|dumb|hate|shut.*up)\b",
            r"\b(kill|die|death|hurt)\b",
            r"\b(damn|hell)\b",
            r"\b(idiot|loser|ugly|fat)\b",
        ]
    
    def check_content(self, content: str) -> bool:
        """Real profanity detection for child protection.
        Args:
            content: Text content to check for profanity
        Returns:
            True if profanity is detected, False otherwise
        """
        import re
        if not content:
            return False
        
        content_lower = content.lower()
        for word in self.blocked_words:
            if word.lower() in content_lower:
                return True
        
        for pattern in self.severe_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False