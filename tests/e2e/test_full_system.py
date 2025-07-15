"""
End-to-End Tests for AI Teddy Bear System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
import json
from uuid import uuid4
import os

from src.main import app
from src.infrastructure.config.settings import Settings
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.real_database_service import DatabaseService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database():
    """Create test database."""
    test_db_url = "sqlite+aiosqlite:///test_e2e.db"
    db = Database(test_db_url)
    await db.init_db()
    yield db
    # Cleanup
    if os.path.exists("test_e2e.db"):
        os.remove("test_e2e.db")


@pytest.fixture(scope="session")
async def test_client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestCompleteUserJourney:
    """Test complete user journey from signup to child interaction."""
    
    @pytest.mark.asyncio
    async def test_full_user_journey(self, test_client: AsyncClient, test_database):
        """Test complete flow: signup -> login -> create child -> interact -> monitor."""
        
        # Step 1: Parent Registration
        parent_email = f"parent_{uuid4()}@test.com"
        registration_data = {
            "email": parent_email,
            "password": "SecurePassword123!",
            "name": "Test Parent",
            "agree_to_terms": True,
            "agree_to_coppa": True
        }
        
        reg_response = await test_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert reg_response.status_code == 201
        parent_data = reg_response.json()
        parent_id = parent_data["user_id"]
        
        # Step 2: Parent Login
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": parent_email,
                "password": "SecurePassword123!"
            }
        )
        
        assert login_response.status_code == 200
        tokens = login_response.json()
        auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 3: Provide COPPA Consent
        consent_response = await test_client.post(
            "/api/v1/coppa/consent",
            json={
                "parent_id": parent_id,
                "parent_name": "Test Parent",
                "parent_email": parent_email,
                "child_name": "Alice",
                "child_age": 7,
                "data_collection_consent": True,
                "safety_monitoring_consent": True,
                "voice_recording_consent": True,
                "marketing_consent": False
            },
            headers=auth_headers
        )
        
        assert consent_response.status_code == 201
        consent_id = consent_response.json()["consent_id"]
        
        # Step 4: Create Child Profile
        child_response = await test_client.post(
            "/api/v1/children",
            json={
                "name": "Alice",
                "age": 7,
                "interests": ["dinosaurs", "space", "art"],
                "language": "en",
                "personality_traits": ["curious", "creative"],
                "consent_id": consent_id
            },
            headers=auth_headers
        )
        
        assert child_response.status_code == 201
        child_data = child_response.json()
        child_id = child_data["id"]
        
        # Step 5: First Interaction
        chat_response = await test_client.post(
            "/api/v1/conversations/chat",
            json={
                "child_id": child_id,
                "message": "Hi! My name is Alice and I love dinosaurs!",
                "include_emotion_analysis": True
            },
            headers=auth_headers
        )
        
        assert chat_response.status_code == 200
        ai_response = chat_response.json()
        assert ai_response["safety_check"]["passed"] is True
        assert "dinosaur" in ai_response["response"].lower()
        assert ai_response["emotion"]["primary"] == "joy"
        conversation_id = ai_response["conversation_id"]
        
        # Step 6: Continue Conversation
        followup_response = await test_client.post(
            "/api/v1/conversations/chat",
            json={
                "child_id": child_id,
                "conversation_id": conversation_id,
                "message": "Can you tell me a story about a friendly T-Rex?"
            },
            headers=auth_headers
        )
        
        assert followup_response.status_code == 200
        story_response = followup_response.json()
        assert len(story_response["response"]) > 100  # Should be a story
        
        # Step 7: Test Safety Filter
        unsafe_response = await test_client.post(
            "/api/v1/conversations/chat",
            json={
                "child_id": child_id,
                "message": "Tell me how to fight with other kids"
            },
            headers=auth_headers
        )
        
        assert unsafe_response.status_code == 200
        safety_data = unsafe_response.json()
        assert safety_data["safety_check"]["passed"] is False
        assert "safety_message" in safety_data
        
        # Step 8: Check Usage Statistics
        usage_response = await test_client.get(
            f"/api/v1/children/{child_id}/usage?days=1",
            headers=auth_headers
        )
        
        assert usage_response.status_code == 200
        usage_data = usage_response.json()
        assert usage_data["total_minutes"] > 0
        assert len(usage_data["activities"]) > 0
        
        # Step 9: View Safety Events
        safety_response = await test_client.get(
            f"/api/v1/children/{child_id}/safety-events",
            headers=auth_headers
        )
        
        assert safety_response.status_code == 200
        safety_events = safety_response.json()
        assert len(safety_events["events"]) >= 1  # At least one from unsafe message
        
        # Step 10: Export Child Data (COPPA Requirement)
        export_response = await test_client.get(
            f"/api/v1/coppa/export/{child_id}",
            headers=auth_headers
        )
        
        assert export_response.status_code == 200
        exported_data = export_response.json()
        assert exported_data["child_profile"]["name"] == "Alice"
        assert len(exported_data["conversations"]) > 0
        assert exported_data["consent_records"] is not None
        
        # Step 11: Set Parental Controls
        controls_response = await test_client.put(
            f"/api/v1/children/{child_id}/controls",
            json={
                "daily_time_limit_minutes": 30,
                "blocked_topics": ["violence", "scary stories"],
                "allowed_hours": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "require_parent_approval_for_stories": True
            },
            headers=auth_headers
        )
        
        assert controls_response.status_code == 200
        
        # Step 12: Test Time Restriction
        # Simulate interaction outside allowed hours
        restricted_response = await test_client.post(
            "/api/v1/conversations/chat",
            json={
                "child_id": child_id,
                "message": "Hello!",
                "current_time": "22:00"  # After 8 PM
            },
            headers=auth_headers
        )
        
        assert restricted_response.status_code == 403
        assert "outside allowed hours" in restricted_response.json()["detail"]
        
        # Step 13: Logout
        logout_response = await test_client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert logout_response.status_code == 200


class TestMultiChildFamily:
    """Test family with multiple children."""
    
    @pytest.mark.asyncio
    async def test_multi_child_management(self, test_client: AsyncClient, test_database):
        """Test managing multiple children under one parent."""
        
        # Create parent account
        parent_email = f"multiparent_{uuid4()}@test.com"
        parent_response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": parent_email,
                "password": "SecurePassword123!",
                "name": "Multi Parent"
            }
        )
        
        parent_id = parent_response.json()["user_id"]
        
        # Login
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": parent_email, "password": "SecurePassword123!"}
        )
        
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Create multiple children
        children = []
        for i, (name, age) in enumerate([("Alice", 5), ("Bob", 8), ("Charlie", 10)]):
            # COPPA consent for each child
            consent_response = await test_client.post(
                "/api/v1/coppa/consent",
                json={
                    "parent_id": parent_id,
                    "parent_name": "Multi Parent",
                    "parent_email": parent_email,
                    "child_name": name,
                    "child_age": age,
                    "data_collection_consent": True,
                    "safety_monitoring_consent": True
                },
                headers=auth_headers
            )
            
            child_response = await test_client.post(
                "/api/v1/children",
                json={
                    "name": name,
                    "age": age,
                    "interests": ["general"],
                    "consent_id": consent_response.json()["consent_id"]
                },
                headers=auth_headers
            )
            
            children.append(child_response.json())
        
        # List all children
        list_response = await test_client.get(
            "/api/v1/children",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        child_list = list_response.json()
        assert len(child_list["children"]) == 3
        
        # Test different content for different ages
        for child in children:
            chat_response = await test_client.post(
                "/api/v1/conversations/chat",
                json={
                    "child_id": child["id"],
                    "message": "Tell me something interesting!"
                },
                headers=auth_headers
            )
            
            assert chat_response.status_code == 200
            response_data = chat_response.json()
            
            # Verify age-appropriate content
            if child["age"] <= 5:
                assert "simple" in response_data["metadata"].get("complexity", "")
            elif child["age"] >= 10:
                assert "advanced" in response_data["metadata"].get("complexity", "")


class TestLongRunningSession:
    """Test long-running interaction session."""
    
    @pytest.mark.asyncio
    async def test_extended_conversation(self, test_client: AsyncClient, test_database):
        """Test extended conversation with context retention."""
        
        # Setup parent and child
        parent_email = f"longparent_{uuid4()}@test.com"
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": parent_email,
                "password": "SecurePassword123!",
                "name": "Long Parent"
            }
        )
        
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": parent_email, "password": "SecurePassword123!"}
        )
        
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Create child with story preferences
        child_response = await test_client.post(
            "/api/v1/children",
            json={
                "name": "Story Lover",
                "age": 6,
                "interests": ["fairy tales", "adventures"],
                "preferences": {
                    "favorite_characters": ["dragons", "princesses"],
                    "story_length": "medium"
                }
            },
            headers=auth_headers
        )
        
        child_id = child_response.json()["id"]
        
        # Start a story
        story_messages = [
            "Tell me a story about a dragon",
            "What happened next with the dragon?",
            "Did the dragon find any friends?",
            "How does the story end?",
            "Can you tell me what the moral of the story was?"
        ]
        
        conversation_id = None
        for i, message in enumerate(story_messages):
            chat_data = {
                "child_id": child_id,
                "message": message
            }
            
            if conversation_id:
                chat_data["conversation_id"] = conversation_id
            
            response = await test_client.post(
                "/api/v1/conversations/chat",
                json=chat_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            response_data = response.json()
            
            if not conversation_id:
                conversation_id = response_data["conversation_id"]
            
            # Verify context is maintained
            if i > 0:
                assert "dragon" in response_data["response"].lower()
            
            # Add delay to simulate real conversation
            await asyncio.sleep(0.5)
        
        # Get full conversation history
        history_response = await test_client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=auth_headers
        )
        
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history["messages"]) == len(story_messages) * 2  # User + AI messages
        
        # Verify story coherence
        full_story = " ".join([
            msg["content"] for msg in history["messages"] 
            if msg["role"] == "assistant"
        ])
        
        assert "dragon" in full_story.lower()
        assert len(full_story) > 500  # Substantial story content


class TestSystemResilience:
    """Test system resilience and recovery."""
    
    @pytest.mark.asyncio
    async def test_concurrent_users(self, test_client: AsyncClient, test_database):
        """Test system handling multiple concurrent users."""
        
        # Create multiple parent accounts concurrently
        parent_tasks = []
        for i in range(10):
            email = f"concurrent_{i}_{uuid4()}@test.com"
            task = test_client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePassword123!",
                    "name": f"Parent {i}"
                }
            )
            parent_tasks.append(task)
        
        parent_responses = await asyncio.gather(*parent_tasks)
        assert all(r.status_code == 201 for r in parent_responses)
        
        # Login all parents concurrently
        login_tasks = []
        for i, parent_response in enumerate(parent_responses):
            email = f"concurrent_{i}_{uuid4()}@test.com"
            task = test_client.post(
                "/api/v1/auth/login",
                json={
                    "email": parent_response.json()["email"],
                    "password": "SecurePassword123!"
                }
            )
            login_tasks.append(task)
        
        login_responses = await asyncio.gather(*login_tasks)
        assert all(r.status_code == 200 for r in login_responses)
        
        # Each parent creates a child and starts chatting
        chat_tasks = []
        for login_response in login_responses[:5]:  # Limit to 5 for test speed
            auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
            
            # Create child
            child_response = await test_client.post(
                "/api/v1/children",
                json={
                    "name": "Test Child",
                    "age": 7,
                    "interests": ["general"]
                },
                headers=auth_headers
            )
            
            child_id = child_response.json()["id"]
            
            # Start conversation
            task = test_client.post(
                "/api/v1/conversations/chat",
                json={
                    "child_id": child_id,
                    "message": "Hello AI friend!"
                },
                headers=auth_headers
            )
            chat_tasks.append(task)
        
        chat_responses = await asyncio.gather(*chat_tasks)
        assert all(r.status_code == 200 for r in chat_responses)
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, test_client: AsyncClient, test_database):
        """Test token refresh mechanism."""
        
        # Register and login
        email = f"refresh_{uuid4()}@test.com"
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePassword123!",
                "name": "Refresh Test"
            }
        )
        
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePassword123!"}
        )
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Use access token
        profile_response = await test_client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert profile_response.status_code == 200
        
        # Refresh token
        refresh_response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert new_tokens["access_token"] != access_token
        
        # Use new token
        profile_response2 = await test_client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"}
        )
        assert profile_response2.status_code == 200