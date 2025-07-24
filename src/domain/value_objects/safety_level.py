from enum import Enum


class SafetyLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    STRICT = "strict"  # Ages 3-6 (أضف الشرح المناسب حسب الحاجة)
    MODERATE = "moderate"  # Ages 7-10
    RELAXED = "relaxed"  # Ages 11-13
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def create_safe_level(cls) -> "SafetyLevel":
        # اختر القيمة الافتراضية الأنسب لمشروعك (هنا NONE مثال)
        return cls.NONE

    def is_safe(self) -> bool:
        # عدل هذا المنطق حسب ما يعتبر "آمن" فعلاً في مشروعك
        return self in [
            SafetyLevel.NONE,
            SafetyLevel.LOW,
            SafetyLevel.STRICT,
            SafetyLevel.MODERATE,
            SafetyLevel.RELAXED,
        ]

    @property
    def level(self) -> int:
        level_map = {
            SafetyLevel.NONE: 0,
            SafetyLevel.LOW: 1,
            SafetyLevel.STRICT: 2,
            SafetyLevel.MODERATE: 3,
            SafetyLevel.RELAXED: 4,
            SafetyLevel.HIGH: 5,
            SafetyLevel.CRITICAL: 6,
        }
        return level_map.get(self, 0)
