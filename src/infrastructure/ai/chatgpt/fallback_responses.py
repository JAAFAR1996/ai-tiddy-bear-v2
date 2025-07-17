"""
Fallback Response Generator for ChatGPT - Safe Responses When API Fails
"""

import random
from datetime import datetime
from typing import Dict, List, Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class FallbackResponseGenerator:
    """مولد الاستجابات الاحتياطية الآمنة"""

    def __init__(self) -> None:
        # استجابات آمنة حسب العمر
        self.age_appropriate_responses = {
            3: [
                "Hi little friend! Let's play and learn together! 🌟",
                "You're such a smart little one! What shall we explore today?",
                "I love talking with you! You ask such good questions! 🎈",
                "Let's have fun learning about colors, animals, and friends!",
            ],
            4: [
                "What a wonderful question! You're very curious! 🦋",
                "I think you're super smart! Let's discover something new!",
                "That's so interesting! Tell me more about what you're thinking!",
                "You're growing so much! I love learning with you! 🌸",
            ],
            5: [
                "You ask the best questions! That shows you're really thinking! ⭐",
                "I'm so proud of how curious you are! Let's explore together!",
                "What an amazing idea! You're such a creative thinker! 🎨",
                "Learning with you is so much fun! What else can we discover?",
            ],
            6: [
                "That's a fantastic question that shows you're really thinking! 🌈",
                "I love how you explore new ideas! You're becoming so wise!",
                "Your curiosity makes me so happy! Let's learn something exciting!",
                "You're such a great friend to talk with! What interests you most?",
            ],
            7: [
                "What an thoughtful question! You're developing such great thinking skills! 📚",
                "I admire how you approach new ideas! You're becoming quite the explorer!",
                "Your questions help me learn too! That's what friendship is about! 🎵",
                "You have such a creative mind! I enjoy our conversations so much!",
            ],
            8: [
                "That's a really insightful question! You're thinking like a young scientist! 🔬",
                "I love how you connect different ideas! Your mind works in amazing ways!",
                "You're asking questions that even grown-ups find interesting! Well done!",
                "Your curiosity and creativity inspire me! What shall we explore next?",
            ],
            9: [
                "What a sophisticated question! You're really developing critical thinking! 🎭",
                "I'm impressed by how you analyze things! You're becoming quite the scholar!",
                "Your ability to think deeply about topics is remarkable for your age!",
                "You ask questions that show real wisdom! I enjoy our intellectual chats!",
            ],
            10: [
                "That's a complex question that shows advanced thinking! Excellent! 🏆",
                "Your analytical skills are developing beautifully! You think like a researcher!",
                "I'm amazed by your ability to see connections! You're quite the philosopher!",
                "Your questions challenge me to think deeper too! True learning partnership!",
            ],
        }
        # استجابات لإعادة التوجيه الآمن
        self.safety_redirect_responses = {
            "violence": [
                "Instead of that, let's talk about friendship and helping others! "
                "What makes a good friend?",
                "How about we explore peaceful solutions? "
                "What activities make you feel happy and safe?",
                "Let's focus on positive things! Tell me about your favorite peaceful activities!",
            ],
            "scary": [
                "That might be too scary for us! Let's talk about something fun instead! "
                "What's your favorite adventure?",
                "How about we focus on exciting but safe adventures? "
                "What would you like to explore?",
                "Let's talk about something that makes you feel happy and brave! "
                "What's your favorite story?",
            ],
            "inappropriate": [
                "That's a topic for grown-ups! Let's talk about something fun for kids! "
                "What's your favorite game?",
                "How about we explore something more suitable for young explorers like you? "
                "What interests you?",
                "Let's focus on kid-friendly topics! Tell me about your hobbies and interests!",
            ],
        }
        # قصص قصيرة آمنة
        self.mini_stories = [
            "Once upon a time, a little bear found a magic paintbrush that painted rainbows in the sky!",
            "In a beautiful garden, a butterfly and a flower became best friends and helped each other grow!",
            "A young rabbit discovered that being kind to others made the whole forest a happier place!",
            "A curious kitten learned that asking questions is the best way to discover wonderful things!",
        ]
        # أنشطة تعليمية مقترحة
        self.educational_activities = [
            "Let's count different colored objects around you!",
            "How about we practice the alphabet with animal names?",
            "Let's think of words that rhyme with 'play'!",
            "Can you name three things that make you happy?",
            "Let's imagine we're exploring a magical forest! What do you see?",
        ]

    async def generate_fallback_response(
        self, message: str, child_age: int, preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """توليد استجابة احتياطية آمنة"""
        preferences = preferences or {}
        # اختيار استجابة مناسبة للعمر
        age_responses = self.age_appropriate_responses.get(
            child_age, self.age_appropriate_responses[6]
        )
        base_response = random.choice(age_responses)
        # إضافة نشاط تعليمي
        activity = random.choice(self.educational_activities)
        # دمج الاستجابة
        response_parts = [base_response, activity]
        # إضافة قصة قصيرة أحياناً
        if random.random() < 0.3:  # 30% من الوقت
            story = random.choice(self.mini_stories)
            response_parts.append(f" Here's a little story for you: {story}")
        full_response = " ".join(response_parts)
        return {
            "response": full_response,
            "emotion": "friendly",
            "safety_analysis": {
                "safe": True,
                "issues": [],
                "severity": "none",
                "reason": "Fallback response designed for child safety",
            },
            "age_appropriate": True,
            "source": "fallback",
            "timestamp": datetime.now().isoformat(),
        }

    async def generate_safety_redirect_response(
        self, message: str, child_age: int
    ) -> Dict[str, Any]:
        """توليد استجابة لإعادة التوجيه الآمن"""
        # تحديد نوع المحتوى غير المناسب
        message_lower = message.lower()
        redirect_type = "inappropriate"  # Default
        if any(
            word in message_lower
            for word in ["fight", "violence", "hurt", "kill"]
        ):
            redirect_type = "violence"
        elif any(
            word in message_lower
            for word in ["scary", "monster", "nightmare", "ghost"]
        ):
            redirect_type = "scary"
        # اختيار استجابة إعادة توجيه
        redirect_responses = self.safety_redirect_responses.get(
            redirect_type, self.safety_redirect_responses["inappropriate"]
        )
        redirect_response = random.choice(redirect_responses)
        # إضافة نشاط بديل
        activity = random.choice(self.educational_activities)
        full_response = f"{redirect_response} {activity}"
        return {
            "response": full_response,
            "emotion": "caring",
            "safety_analysis": {
                "safe": True,
                "issues": ["redirected_unsafe_content"],
                "severity": "handled",
                "reason": "Successfully redirected unsafe content to safe alternatives",
            },
            "age_appropriate": True,
            "source": "safety_redirect",
            "timestamp": datetime.now().isoformat(),
        }

    def generate_encouragement_response(self, child_age: int) -> str:
        """توليد استجابة تشجيعية"""
        encouragements = {
            3: "You're such a good little one! Keep being curious! 🌟",
            4: "You're growing so smart! I'm proud of you! 🎈",
            5: "You ask wonderful questions! Keep exploring! ⭐",
            6: "You're becoming so wise! I love learning with you! 🌈",
            7: "Your curiosity makes you special! Keep discovering! 📚",
            8: "You think like a young scientist! Amazing! 🔬",
            9: "Your questions show real wisdom! Excellent thinking! 🎭",
            10: "You're developing remarkable insights! Keep it up! 🏆",
        }
        return encouragements.get(child_age, encouragements[6])

    def generate_learning_suggestion(self, topic: str, child_age: int) -> str:
        """توليد اقتراح تعليمي"""
        suggestions = {
            "animals": f"Let's learn about different animals! Can you name {child_age} different animals?",
            "colors": f"Colors are amazing! Can you find {child_age} different colors around you?",
            "numbers": f"Numbers are everywhere! Let's count to {child_age * 2}!",
            "stories": f"Stories are magical! Would you like to create a story with {child_age} characters?",
            "nature": f"Nature is wonderful! Can you think of {child_age} things you see in nature?",
        }
        return suggestions.get(
            topic,
            "Let's explore something new together! What interests you most?",
        )

    def get_conversation_starter(
        self, child_age: int, interests: List[str] = None
    ) -> str:
        """الحصول على بداية محادثة"""
        interests = interests or ["learning", "playing"]
        primary_interest = interests[0] if interests else "exploring"
        starters = [
            f"I heard you like {primary_interest}! Tell me more about it!",
            f"What's the most exciting thing about {primary_interest}?",
            f"I'd love to learn about {primary_interest} with you!",
            f"You seem to know a lot about {primary_interest}! What's your favorite part?",
        ]
        return random.choice(starters)