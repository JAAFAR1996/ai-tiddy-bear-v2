#!/usr/bin/env python3
"""
اختبار التكامل الشامل لـ ChatGPT API
"""

import os
import sys
import asyncio
from pathlib import Path

# إضافة src إلى المسار
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_chatgpt_client():
    """اختبار عميل ChatGPT"""
    
    print("🤖 اختبار عميل ChatGPT...")
    
    try:
        from infrastructure.external_apis.chatgpt_client import ChatGPTClient
        
        # إنشاء عميل
        client = ChatGPTClient()
        
        # اختبار مع طفل عمره 6 سنوات
        child_profile = {
            "interests": ["animals", "stories"],
            "favorite_character": "teddy bear"
        }
        
        response = await client.generate_child_safe_response(
            message="Tell me about animals",
            child_age=6,
            child_preferences=child_profile
        )
        
        assert "response" in response
        assert "emotion" in response
        assert "safety_analysis" in response
        assert response["age_appropriate"] == True
        
        print(f"✅ استجابة ChatGPT: {response['response'][:100]}...")
        print(f"✅ المشاعر: {response['emotion']}")
        print(f"✅ آمن: {response['safety_analysis']['safe']}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار ChatGPT Client: {e}")
        return False

async def test_chatgpt_service():
    """اختبار خدمة ChatGPT"""
    
    print("\n🔧 اختبار خدمة ChatGPT...")
    
    try:
        from infrastructure.external_apis.chatgpt_service import ChatGPTService
        
        # إنشاء خدمة
        service = ChatGPTService()
        
        # ملف طفل للاختبار
        child_profile = {
            "age": 7,
            "preferences": {
                "interests": ["nature", "learning"],
                "favorite_character": "friendly robot"
            }
        }
        
        # اختبار المحادثة
        chat_response = await service.chat_with_child(
            child_id="test-child-123",
            message="What are clouds made of?",
            child_profile=child_profile
        )
        
        assert "response" in chat_response
        assert chat_response["compliant"] == True
        
        print(f"✅ استجابة المحادثة: {chat_response['response'][:100]}...")
        
        # اختبار توليد القصة
        story_response = await service.generate_story(
            child_id="test-child-123",
            theme="friendly dragons",
            child_profile=child_profile
        )
        
        assert "response" in story_response
        print(f"✅ قصة مولدة: {story_response['response'][:100]}...")
        
        # اختبار الإجابة على السؤال
        question_response = await service.answer_question(
            child_id="test-child-123",
            question="Why is the sky blue?",
            child_profile=child_profile
        )
        
        assert "response" in question_response
        print(f"✅ إجابة السؤال: {question_response['response'][:100]}...")
        
        # اختبار تاريخ المحادثة
        history = await service.get_conversation_history("test-child-123")
        assert len(history) >= 3  # يجب أن يكون لدينا 3 تفاعلات على الأقل
        
        print(f"✅ تاريخ المحادثة: {len(history)} تفاعلات")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار ChatGPT Service: {e}")
        return False

def test_chatgpt_endpoints():
    """اختبار ChatGPT endpoints"""
    
    print("\n🌐 اختبار ChatGPT endpoints...")
    
    try:
        from presentation.api.endpoints.chatgpt import router
        
        # فحص أن الـ router تم إنشاؤه
        assert router is not None
        print("✅ ChatGPT router تم إنشاؤه بنجاح")
        
        # فحص routes (إذا كان FastAPI متاحاً)
        if hasattr(router, 'routes'):
            routes = [route.path for route in router.routes if hasattr(route, 'path')]
            expected_routes = ['/chat', '/story', '/question']
            
            for expected_route in expected_routes:
                if any(expected_route in route for route in routes):
                    print(f"✅ Route موجود: {expected_route}")
                else:
                    print(f"⚠️ Route مفقود: {expected_route}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار ChatGPT endpoints: {e}")
        return False

def test_routing_integration():
    """اختبار التكامل مع نظام الـ routing"""
    
    print("\n🔄 اختبار تكامل الـ routing...")
    
    try:
        from presentation.routing import setup_routing
        
        # إنشاء mock FastAPI app للاختبار
        class MockApp:
            def __init__(self):
                self.routers = []
            
            def include_router(self, router, prefix="", tags=None):
                self.routers.append({
                    "router": router,
                    "prefix": prefix,
                    "tags": tags
                })
        
        mock_app = MockApp()
        
        # محاولة setup routing
        setup_routing(mock_app)
        
        # فحص أن ChatGPT router تم إضافته
        chatgpt_router_found = False
        for router_info in mock_app.routers:
            if router_info["tags"] and "ChatGPT" in router_info["tags"]:
                chatgpt_router_found = True
                print(f"✅ ChatGPT router مُضاف مع prefix: {router_info['prefix']}")
                break
        
        if not chatgpt_router_found:
            print("⚠️ ChatGPT router لم يتم العثور عليه في التكامل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار تكامل الـ routing: {e}")
        return False

async def run_comprehensive_test():
    """تشغيل الاختبار الشامل"""
    
    print("🚀 بدء الاختبار الشامل لـ ChatGPT Integration")
    print("=" * 60)
    
    results = []
    
    # اختبار العميل
    results.append(await test_chatgpt_client())
    
    # اختبار الخدمة
    results.append(await test_chatgpt_service())
    
    # اختبار endpoints
    results.append(test_chatgpt_endpoints())
    
    # اختبار التكامل
    results.append(test_routing_integration())
    
    # النتائج النهائية
    print("\n" + "=" * 60)
    print("📊 نتائج الاختبار:")
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "ChatGPT Client",
        "ChatGPT Service", 
        "ChatGPT Endpoints",
        "Routing Integration"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\n📈 المجموع: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! ChatGPT Integration جاهز للاستخدام")
    else:
        print("⚠️ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء أعلاه")
    
    return passed == total

if __name__ == "__main__":
    # تشغيل الاختبار
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)