#!/usr/bin/env python3
"""Simple test runner that doesn't require pytest."""

import sys
import os
sys.path.insert(0, 'src')

def run_simple_tests():
    """Run basic functionality tests without pytest."""
    
    print("🧪 AI Teddy Bear - Simple Test Runner")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    def test(description, test_func):
        nonlocal tests_passed, tests_failed
        try:
            test_func()
            print(f"✅ {description}")
            tests_passed += 1
        except Exception as e:
            print(f"❌ {description}: {e}")
            tests_failed += 1
    
    # Import required modules
    from domain.entities.child_profile import ChildProfile
    from domain.events.child_registered import ChildRegistered
    from domain.events.child_profile_updated import ChildProfileUpdated
    from domain.value_objects.safety_level import SafetyLevel
    from application.dto.esp32_request import ESP32Request
    from application.dto.ai_response import AIResponse
    from application.dto.child_data import ChildData
    from application.dto.story_request import StoryRequest
    from common.settings import get_settings
    from uuid import uuid4
    
    print("\n📁 Testing Domain Layer")
    print("-" * 25)
    
    # Test ChildProfile entity
    def test_child_profile_creation():
        child = ChildProfile.create_new("Emma", 7, {"language": "en"})
        assert child.name == "Emma"
        assert child.age == 7
        assert child.preferences["language"] == "en"
    
    test("ChildProfile creation", test_child_profile_creation)
    
    def test_child_profile_update():
        child = ChildProfile.create_new("Bob", 5, {})
        child.update_profile(name="Bobby", age=6)
        assert child.name == "Bobby"
        assert child.age == 6
    
    test("ChildProfile update", test_child_profile_update)
    
    # Test Domain Events
    def test_child_registered_event():
        child_id = uuid4()
        event = ChildRegistered.create(child_id, "Alice", 8, {"interests": ["animals"]})
        assert event.child_id == child_id
        assert event.name == "Alice"
        assert event.age == 8
    
    test("ChildRegistered event creation", test_child_registered_event)
    
    def test_child_profile_updated_event():
        child_id = uuid4()
        event = ChildProfileUpdated.create(child_id, name="Updated Name")
        assert event.child_id == child_id
        assert event.name == "Updated Name"
    
    test("ChildProfileUpdated event creation", test_child_profile_updated_event)
    
    # Test Value Objects
    def test_safety_level_enum():
        assert SafetyLevel.NONE.value == "none"
        assert SafetyLevel.LOW.value == "low"
        assert SafetyLevel.MODERATE.value == "moderate"
        assert SafetyLevel.HIGH.value == "high"
        assert SafetyLevel.CRITICAL.value == "critical"
    
    test("SafetyLevel enum values", test_safety_level_enum)
    
    print("\n📦 Testing Application Layer")
    print("-" * 30)
    
    # Test DTOs
    def test_esp32_request():
        request = ESP32Request(
            child_id=uuid4(),
            audio_data=b"fake_audio",
            language_code="en"
        )
        assert request.language_code == "en"
        assert request.audio_data == b"fake_audio"
    
    test("ESP32Request DTO", test_esp32_request)
    
    def test_ai_response():
        response = AIResponse(
            response_text="Hello!",
            audio_response=b"audio",
            emotion="happy",
            sentiment=0.8,
            safe=True,
            conversation_id="123"
        )
        assert response.response_text == "Hello!"
        assert response.emotion == "happy"
        assert response.safe is True
    
    test("AIResponse DTO", test_ai_response)
    
    def test_child_data():
        child_data = ChildData(
            id=uuid4(),
            name="Test Child",
            age=6,
            preferences={"language": "es"}
        )
        assert child_data.name == "Test Child"
        assert child_data.age == 6
    
    test("ChildData DTO", test_child_data)
    
    def test_story_request():
        story_req = StoryRequest(
            child_id=uuid4(),
            theme="adventure",
            characters=["rabbit", "owl"],
            story_length="short"
        )
        assert story_req.theme == "adventure"
        assert len(story_req.characters) == 2
    
    test("StoryRequest DTO", test_story_request)
    
    print("\n⚙️  Testing Infrastructure Layer")
    print("-" * 35)
    
    # Test Settings
    def test_settings():
        settings = get_settings()
        assert settings.APP_NAME == "AI Teddy Bear"
        assert settings.APP_VERSION == "2.0.0"
        assert settings.DATABASE_URL is not None
        assert settings.SAFETY_THRESHOLD == 0.8
    
    test("Settings configuration", test_settings)
    
    def test_settings_caching():
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Should be same instance due to caching
    
    test("Settings caching", test_settings_caching)
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📈 Success Rate: {tests_passed/(tests_passed + tests_failed)*100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The AI Teddy Bear core functionality is working correctly!")
        return True
    else:
        print(f"\n⚠️  {tests_failed} tests failed. Please fix these issues.")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)