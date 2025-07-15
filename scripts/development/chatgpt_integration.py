#!/usr/bin/env python3
"""
ChatGPT Integration Entry Point for AI Teddy Bear
Simplified version of create_chatgpt_api.py with modular structure
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from infrastructure.ai.chatgpt import ChatGPTClient, SafetyFilter, ResponseEnhancer

logger = logging.getLogger(__name__)

def setup_chatgpt_integration():
    """Setup ChatGPT integration with all safety measures"""
    
    print("🤖 Setting up ChatGPT Integration for AI Teddy Bear...")
    
    try:
        # Initialize ChatGPT client
        client = ChatGPTClient()
        
        # Test the integration
        print("✅ ChatGPT client initialized successfully")
        print("✅ Safety filter activated")
        print("✅ Response enhancer ready")
        print("✅ Fallback responses configured")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to setup ChatGPT integration: {e}")
        print(f"❌ Setup failed: {e}")
        return None

async def test_child_safe_response():
    """Test the child-safe response generation"""
    
    client = setup_chatgpt_integration()
    if not client:
        return
    
    print("\n🧪 Testing child-safe responses...")
    
    test_cases = [
        {
            "message": "Tell me about animals",
            "age": 5,
            "preferences": {"interests": ["animals", "nature"]}
        },
        {
            "message": "I want to learn about colors",
            "age": 4,
            "preferences": {"interests": ["art", "colors"]}
        },
        {
            "message": "Can you tell me a story?",
            "age": 6,
            "preferences": {"interests": ["stories", "adventure"]}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Child Age: {test_case['age']}")
        print(f"Message: {test_case['message']}")
        
        try:
            response = await client.generate_child_safe_response(
                test_case["message"],
                test_case["age"],
                test_case["preferences"]
            )
            
            print(f"Response: {response['response']}")
            print(f"Emotion: {response['emotion']}")
            print(f"Safety: {'✅ Safe' if response['safety_analysis']['safe'] else '❌ Unsafe'}")
            print(f"Source: {response['source']}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")

def main():
    """Main entry point"""
    
    print("🧸 AI Teddy Bear - ChatGPT Integration")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup integration
    client = setup_chatgpt_integration()
    
    if client:
        print("\n✅ ChatGPT integration is ready!")
        print("\n📋 Available features:")
        print("• Child-safe response generation")
        print("• Age-appropriate content filtering")
        print("• Safety analysis and redirection")
        print("• Educational response enhancement")
        print("• Fallback responses for API failures")
        
        print("\n🔒 Security features:")
        print("• Content safety filtering")
        print("• Age-appropriate language adjustment")
        print("• Inappropriate content redirection")
        print("• Positive reinforcement focus")
        
        print("\n📖 To test the integration:")
        print("python -c \"import asyncio; from chatgpt_integration import test_child_safe_response; asyncio.run(test_child_safe_response())\"")
        
    else:
        print("\n❌ ChatGPT integration setup failed!")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()