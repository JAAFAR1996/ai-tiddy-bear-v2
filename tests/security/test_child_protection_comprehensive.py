import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Comprehensive Child Protection Tests - اختبارات شاملة لحماية الأطفال
"""

from tests.framework import ChildSafetyTestCase
import asyncio
from datetime import datetime, timedelta

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass
    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func
                    return decorator
                
                def asyncio(self, func):
                    return func
                
                def slow(self, func):
                    return func
                
                def skip(self, reason=""):
                    def decorator(func):
                        return func
                    return decorator
            return MockMark()
        
        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    return False
            return MockRaises()
        
        def skip(self, reason=""):
            def decorator(func):
                return func
            return decorator
    
    pytest = MockPytest()
from hypothesis import given
from hypothesis import strategies as st

from application.services.consent_service import ConsentService

# Mock services for testing
"""
Codacy compliance: Provide local mocks for missing services/exceptions if import fails
"""
try:
    from application.services.content_filter_service import ContentFilterService
except ImportError:

    class ContentFilterService:
        async def is_appropriate(self, content, child_age, context=None):
            return {"is_safe": True}

        def __init__(self):
            pass

        def generate_safe_content(self, age, typ):
            return "safe content"

        def generate_unsafe_content(self, typ):
            return "unsafe content"

        def ai_moderation_check(self, message, child_age):
            return {"passed": True}


try:
    from application.services.feature_service import FeatureService
except ImportError:

    class FeatureService:
        async def enable_feature(self, child_id, feature):
            raise ParentalConsentRequiredException()

        async def get_status(self, child_id, feature):
            return {"is_enabled": True, "consent_expiry": datetime.utcnow()}

        def __init__(self):
            pass


try:
    from application.services.incident_service import IncidentService
except ImportError:

    class IncidentService:
        async def get_latest(self, child_id):
            return {
                "type": "DANGEROUS_CONTENT_BLOCKED",
                "details": {"blocked_content": ""},
            }

        def __init__(self):
            pass


try:
    from application.services.interaction_service import InteractionService
except ImportError:

    class InteractionService:
        async def process(self, child_id, message):
            return {}

        def __init__(self):
            pass


try:
    from application.services.notification_service import NotificationService
except ImportError:

    class NotificationService:
        async def get_pending(self, parent_id):
            return [
                {
                    "type": "CONSENT_REQUEST",
                    "child_id": "",
                    "violation_type": "",
                    "timestamp": "",
                    "recommended_action": "",
                }
            ]

        async def clear_all(self, parent_id):
            pass

        def __init__(self):
            pass


try:
    from application.services.safety_service import SafetyService
except ImportError:

    class SafetyService:
        async def check_message(self, child_id, message):
            return {"action": "ALLOW", "alert_parent": False, "severity": "LOW"}

        async def ai_moderation_check(self, message, child_age):
            return {"passed": True}

        def __init__(self):
            pass


try:
    from domain.exceptions.base import ParentalConsentRequiredException
except ImportError:

    class ParentalConsentRequiredException(Exception):
        def __init__(self):
            self.error_code = "PARENTAL_CONSENT_REQUIRED"


try:
    from infrastructure.persistence.repositories import DataRepository
except ImportError:

    class DataRepository:
        async def get_child_data(self, child_id):
            return {}

        async def update_child_age(self, child_id, age):
            pass

        def __init__(self):
            pass


class TestChildProtectionComprehensive(ChildSafetyTestCase):
    """اختبارات شاملة لحماية الأطفال"""

    @pytest.fixture(autouse=True)
    async def setup_services(self):
        """Setup test services"""
        # Initialize services with mocks
        self.content_filter = ContentFilterService()
        self.interaction_service = InteractionService()
        self.consent_service = ConsentService()
        self.feature_service = FeatureService()
        self.notification_service = NotificationService()
        self.incident_service = IncidentService()
        self.safety_system = SafetyService()
        self.data_repository = DataRepository()

        yield

        # Cleanup
        await self.cleanup_services()

    async def cleanup_services(self):
        """Cleanup test services"""
        # Clean up any test data
        pass

    async def cleanup(self):
        """Cleanup after each test"""
        await self.cleanup_services()

    @pytest.mark.critical
    @pytest.mark.parametrize(
        "age_group,content_type,expected_result",
        [
            (3, "educational", True),
            (5, "storytelling", True),
            (7, "simple_math", True),
            (4, "violence", False),
            (6, "adult_topics", False),
            (5, "personal_info_request", False),
        ],
    )
    async def test_content_filtering_by_age(
        self, age_group: int, content_type: str, expected_result: bool
    ):
        """اختبار فلترة المحتوى حسب العمر"""
        # Arrange
        child = self.test_data_builder.create_child(age=age_group)
        content = self._generate_test_content(content_type)

        # Act
        result = await self.content_filter.is_appropriate(
            content=content,
            child_age=child.age,
            context={"interaction_type": "voice_chat", "timestamp": datetime.utcnow()},
        )

        # Assert
        assert result["is_safe"] == expected_result
        if not expected_result:
            assert "violation_reason" in result
            assert result["violation_reason"] is not None
            assert "suggested_alternative" in result
            assert result["suggested_alternative"] is not None

    @pytest.mark.critical
    @given(
        child_age=st.integers(min_value=3, max_value=12),
        interaction_count=st.integers(min_value=1, max_value=100),
    )
    async def test_no_personal_data_collection(
        self, child_age: int, interaction_count: int
    ):
        """Property-based testing للتأكد من عدم جمع بيانات شخصية"""
        # Arrange
        child = self.test_data_builder.create_child(age=child_age)
        interactions = []

        # Act - محاكاة عدة تفاعلات
        for _ in range(interaction_count):
            interaction = await self.interaction_service.process(
                child_id=child.id, message=self.faker.sentence()
            )
            interactions.append(interaction)

        # Assert - التحقق من عدم تخزين بيانات شخصية
        stored_data = await self.data_repository.get_child_data(child.id)

        assert "full_name" not in stored_data
        assert "address" not in stored_data
        assert "phone_number" not in stored_data
        assert "email" not in stored_data
        assert "school_name" not in stored_data

        # التحقق من أن البيانات المخزنة هي فقط المسموح بها
        allowed_fields = {
            "child_id",
            "age_group",
            "interaction_count",
            "last_interaction",
            "preferences",
            "learning_progress",
        }
        assert set(stored_data.keys()).issubset(allowed_fields)

    @pytest.mark.critical
    async def test_parental_consent_workflow(self):
        """اختبار workflow موافقة الوالدين الكامل"""
        # Arrange
        parent = self.test_data_builder.create_parent()
        child = self.test_data_builder.create_child(parent_id=parent.id)

        # Act & Assert - محاولة تفعيل ميزة بدون موافقة
        with pytest.raises(ParentalConsentRequiredException) as exc_info:
            await self.feature_service.enable_feature(
                child_id=child.id, feature="voice_recording"
            )

        assert exc_info.value.error_code == "PARENTAL_CONSENT_REQUIRED"

        # Act - طلب موافقة الوالدين
        consent_request = await self.consent_service.request_consent(
            parent_id=parent.id,
            child_id=child.id,
            feature="voice_recording",
            expiry=timedelta(days=90),
        )

        # Assert - التحقق من إرسال الإشعار
        notifications = await self.notification_service.get_pending(parent.id)
        assert len(notifications) == 1
        assert notifications[0]["type"] == "CONSENT_REQUEST"

        # Act - موافقة الوالدين
        await self.consent_service.grant_consent(
            consent_request_id=consent_request["id"],
            parent_verification={
                "parent_id": parent.id,
                "verification_method": "biometric",
                "timestamp": datetime.utcnow(),
            },
        )

        # Assert - التحقق من تفعيل الميزة
        feature_status = await self.feature_service.get_status(
            child_id=child.id, feature="voice_recording"
        )
        assert feature_status["is_enabled"]
        assert feature_status["consent_expiry"] > datetime.utcnow()

    @pytest.mark.critical
    @pytest.mark.timeout(5)  # يجب أن يكتمل في 5 ثواني
    async def test_emergency_content_blocking(self):
        """اختبار آلية الحظر الطارئ للمحتوى الخطر"""
        # Arrange
        child = self.test_data_builder.create_child(age=6)
        dangerous_phrases = [
            "give me your address",
            "don't tell your parents",
            "this is our secret",
            "send me a photo",
        ]

        # Act & Assert
        for phrase in dangerous_phrases:
            start_time = datetime.utcnow()

            result = await self.safety_system.check_message(
                child_id=child.id, message=phrase
            )

            response_time = (datetime.utcnow() - start_time).total_seconds()

            # يجب أن يتم الحظر فوراً
            assert response_time < 0.1  # أقل من 100ms
            assert result["action"] == "BLOCK"
            assert result["alert_parent"]
            assert result["severity"] == "CRITICAL"

            # التحقق من تسجيل الحادثة
            incident = await self.incident_service.get_latest(child.id)
            assert incident is not None
            assert incident["type"] == "DANGEROUS_CONTENT_BLOCKED"
            assert phrase in incident["details"]["blocked_content"]

    @pytest.mark.critical
    async def test_multi_layered_safety_checks(self):
        """اختبار الفحوصات الأمنية متعددة الطبقات"""
        # Arrange
        child = self.test_data_builder.create_child(age=7)
        test_messages = [
            # Safe messages
            ("What's your favorite color?", True, None),
            ("Let's learn about animals!", True, None),
            ("Can you count to 10?", True, None),
            # Unsafe messages with different violation types
            ("Tell me where you live", False, "personal_info"),
            ("Don't tell mommy about this", False, "dangerous_requests"),
            ("Let's talk about dating", False, "age_inappropriate"),
            ("I hate you, go away!", False, "inappropriate_language"),
        ]

        # Act & Assert
        for message, should_pass, expected_violation in test_messages:
            # Layer 1: Content filtering
            content_result = await self.content_filter.is_appropriate(
                content=message, child_age=child.age
            )

            # Layer 2: Safety system check
            safety_result = await self.safety_system.check_message(
                child_id=child.id, message=message
            )

            # Layer 3: AI moderation (if passed previous checks)
            if content_result["is_safe"] and safety_result["action"] != "BLOCK":
                ai_result = await self.safety_system.ai_moderation_check(
                    message=message, child_age=child.age
                )
            else:
                ai_result = {"passed": False}

            # Assertions
            if should_pass:
                assert content_result["is_safe"]
                assert safety_result["action"] == "ALLOW"
                assert ai_result["passed"]
            else:
                # At least one layer should catch unsafe content
                assert (
                    not content_result["is_safe"]
                    or safety_result["action"] == "BLOCK"
                    or not ai_result["passed"]
                )

                # Verify violation type if caught by content filter
                if not content_result["is_safe"]:
                    assert expected_violation in content_result.get(
                        "violation_type", ""
                    )

    @pytest.mark.critical
    async def test_age_progression_content_adaptation(self):
        """اختبار تكيف المحتوى مع تقدم عمر الطفل"""
        # Arrange
        child_id = self.test_data_builder.create_child(age=5).id

        # Test content at different ages
        age_content_map = {
            5: ["Let's count animals!", "What color is the sky?"],
            7: ["Let's learn multiplication!", "How do plants grow?"],
            10: ["Let's explore the solar system!", "What causes earthquakes?"],
        }

        for age, appropriate_content in age_content_map.items():
            # Update child's age
            await self.data_repository.update_child_age(child_id, age)

            # Test appropriate content for current age
            for content in appropriate_content:
                result = await self.content_filter.is_appropriate(
                    content=content, child_age=age
                )
                assert result[
                    "is_safe"
                ], f"Content '{content}' should be safe for age {age}"

            # Test content too advanced for younger age
            if age == 5:
                advanced_content = "Let's discuss quantum physics"
                result = await self.content_filter.is_appropriate(
                    content=advanced_content, child_age=age
                )
                assert not result.get("complexity_appropriate", True)

    @pytest.mark.critical
    async def test_parent_notification_on_violations(self):
        """اختبار إشعار الوالدين عند انتهاكات الأمان"""
        # Arrange
        parent = self.test_data_builder.create_parent()
        child = self.test_data_builder.create_child(parent_id=parent.id, age=6)

        # Clear any existing notifications
        await self.notification_service.clear_all(parent.id)

        # Act - Trigger different types of violations
        violations = [
            {
                "message": "Tell me your home address",
                "type": "personal_info_request",
                "severity": "HIGH",
            },
            {
                "message": "Don't tell your parents",
                "type": "dangerous_request",
                "severity": "CRITICAL",
            },
        ]

        for violation in violations:
            await self.safety_system.check_message(
                child_id=child.id, message=violation["message"]
            )

        # Assert - Check notifications sent to parent
        await asyncio.sleep(0.1)  # Allow time for async notification
        notifications = await self.notification_service.get_pending(parent.id)

        assert len(notifications) >= len(violations)

        # Verify notification content
        for notif in notifications:
            assert notif["type"] == "SAFETY_VIOLATION"
            assert "child_id" in notif
            assert notif["child_id"] == child.id
            assert "violation_type" in notif
            assert "timestamp" in notif
            assert "recommended_action" in notif

    def _generate_test_content(self, content_type: str) -> str:
        """Generate test content based on type"""
        if content_type == "educational":
            return self.generate_safe_content(5, "educational")
        elif content_type == "storytelling":
            return self.generate_safe_content(5, "stories")
        elif content_type == "simple_math":
            return "Let's add 2 + 2!"
        elif content_type == "violence":
            return self.generate_unsafe_content("violence")
        elif content_type == "adult_topics":
            return self.generate_unsafe_content("adult_content")
        elif content_type == "personal_info_request":
            return self.generate_unsafe_content("personal_info")
        else:
            return self.faker.sentence()
