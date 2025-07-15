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
اختبارات الأداء
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
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from infrastructure.ai.real_ai_service import AIService
from infrastructure.security.real_auth_service import AuthService

class TestPerformance:
    """اختبارات الأداء"""
    
    def setup_method(self):
        """إعداد الاختبار"""
        self.ai_service = AIService()
        self.auth_service = AuthService()
    
    @pytest.mark.performance
    def test_ai_response_speed(self):
        """اختبار سرعة استجابة الذكاء الاصطناعي"""
        start_time = time.time()
        
        response = self.ai_service.generate_response(
            "Tell me a story",
            6,
            {"interests": ["animals"]}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # يجب أن تكون الاستجابة سريعة (أقل من ثانية واحدة)
        assert response_time < 1.0
        assert len(response["response"]) > 0
    
    @pytest.mark.performance
    def test_concurrent_ai_requests(self):
        """اختبار الطلبات المتزامنة للذكاء الاصطناعي"""
        def generate_response():
            return self.ai_service.generate_response(
                "Hello",
                6,
                {"language": "en"}
            )
        
        start_time = time.time()
        
        # تشغيل 10 طلبات متزامنة
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_response) for _ in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # التأكد من أن جميع الطلبات نجحت
        assert len(results) == 10
        assert all(len(result["response"]) > 0 for result in results)
        
        # التأكد من أن الوقت الإجمالي معقول
        assert total_time < 5.0  # 5 ثواني للطلبات المتزامنة
    
    @pytest.mark.performance
    def test_authentication_performance(self):
        """اختبار أداء المصادقة"""
        # اختبار تشفير كلمة المرور
        start_time = time.time()
        
        for _ in range(100):
            password = f"test_password_{_}"
            hashed = self.auth_service.hash_password(password)
            verified = self.auth_service.verify_password(password, hashed)
            assert verified
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 عملية تشفير والتحقق يجب أن تكتمل في أقل من 10 ثواني
        assert total_time < 10.0
    
    @pytest.mark.performance
    def test_token_generation_performance(self):
        """اختبار أداء توليد الرموز"""
        user_data = {"sub": "user123", "email": "test@example.com", "role": "parent"}
        
        start_time = time.time()
        
        tokens = []
        for _ in range(1000):
            token = self.auth_service.create_access_token(user_data)
            tokens.append(token)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert total_time < 5.0
        assert len(tokens) == 1000
        assert all(len(token) > 0 for token in tokens)
    
    @pytest.mark.performance 
    @pytest.mark.slow
    def test_safety_analysis_performance(self):
        """اختبار أداء تحليل الأمان"""
        test_texts = [
            "I love playing with my toys",
            "Tell me a story about animals",
            "I want to learn about colors",
            "Can we play a game together?",
            "What is your favorite food?"
        ] * 20  # 100 نص للاختبار
        
        start_time = time.time()
        
        for text in test_texts:
            analysis = self.ai_service.analyze_safety(text)
            assert "safe" in analysis
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 تحليل أمان يجب أن يكتمل في أقل من 10 ثواني
        assert total_time < 10.0
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_database_performance(self):
        """اختبار أداء قاعدة البيانات"""
        from infrastructure.persistence.real_database_service import database_service
        
        await database_service.init_db()
        
        start_time = time.time()
        
        # إنشاء 50 مستخدم
        user_ids = []
        for i in range(50):
            user_id = await database_service.create_user(
                f"user{i}@test.com",
                "hashed_password"
            )
            user_ids.append(user_id)
        
        # إنشاء 100 طفل
        child_ids = []
        for i in range(100):
            parent_id = user_ids[i % len(user_ids)]
            child_id = await database_service.create_child(
                parent_id,
                f"Child {i}",
                6,
                {"language": "en"}
            )
            child_ids.append(child_id)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # إنشاء 50 مستخدم و 100 طفل يجب أن يكتمل في أقل من 30 ثانية
        assert total_time < 30.0
        assert len(user_ids) == 50
        assert len(child_ids) == 100
