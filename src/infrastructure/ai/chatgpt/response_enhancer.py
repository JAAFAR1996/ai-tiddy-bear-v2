"""
Response Enhancer for ChatGPT - Child - Friendly Response Enhancement
"""

from datetime import datetime
from typing import Dict, List, Any
import logging
import random
import re

PRESCHOOL_MAX_AGE = 5
ELEMENTARY_MAX_AGE = 8
EMOJI_PROBABILITY = 0.3
MAX_ENHANCEMENT_ATTEMPTS = 3

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="infrastructure")

class ResponseEnhancer:
    """Response enhancer for child - friendly AI interactions."""
    def __init__(self) -> None:
        # Encouraging phrases for children
        self.encouraging_phrases = [
            "That's a great question!",
            "You're so curious!",
            "I love how you think!",
            "What a wonderful idea!",
            "You're very smart!",
            "That's fantastic!",
            "Keep exploring!",
            "You're doing great!"
        ]
        # Child-friendly emojis
        self.child_friendly_emojis = [
            "😊", "🌟", "🎈", "🦋", "🌸", "🎨", "📚", "🎵",
            "🐻", "🦊", "🐱", "🐶", "🌈", "⭐", "🎪", "🎭"
        ]
        # Follow-up questions
        self.follow_up_questions = [
            "What do you think about that?",
            "Would you like to know more?",
            "What's your favorite part?",
            "Can you tell me more?",
            "What would you do?",
            "How does that make you feel?",
            "What else would you like to explore?"
        ]

    def enhance_response_for_children(self, response: str, child_age: int, preferences: Dict[str, Any] = None) -> str:
        """Enhance response for children with age - appropriate content."""
        preferences = preferences or {}
        # Apply age-specific enhancements
        enhanced = self._apply_age_specific_enhancements(response, child_age)
        # Add interactive elements
        enhanced = self._add_interactive_elements(enhanced, child_age)
        # إضافة التشجيع
        enhanced = self._add_encouragement(enhanced)
        # إضافة سؤال للمتابعة
        enhanced = self._add_follow_up_question(enhanced)
        # تطبيق تفضيلات الطفل
        enhanced = self._apply_child_preferences(enhanced, preferences)
        return enhanced

    def _apply_age_specific_enhancements(self, response: str, child_age: int) -> str:
        """تطبيق تحسينات خاصة بالعمر"""
        if child_age <= 4:
            # للأطفال الصغار: جمل قصيرة وكلمات بسيطة
            response = self._simplify_language(response)
            response = self._add_repetition(response)
        elif child_age <= 7:
            # للأطفال المتوسطين: إضافة أصوات وحركات
            response = self._add_sound_effects(response)
        elif child_age <= 10:
            # للأطفال الأكبر: إضافة معلومات تعليمية
            response = self._add_educational_elements(response)
        return response

    def _simplify_language(self, response: str) -> str:
        """تبسيط اللغة للأطفال الصغار"""
        # استبدال الكلمات المعقدة بكلمات بسيطة
        replacements = {
            "magnificent": "beautiful",
            "extraordinary": "amazing",
            "immediately": "right now",
            "definitely": "yes",
            "probably": "maybe",
            "understand": "know",
            "remember": "think of",
            "interesting": "cool",
            "wonderful": "great",
            "fantastic": "awesome"
        }
        for complex_word, simple_word in replacements.items():
            response = re.sub(
                r'\b' + re.escape(complex_word) + r'\b',
                simple_word,
                response,
                flags=re.IGNORECASE
            )
        # تقسيم الجمل الطويلة
        sentences = response.split('. ')
        short_sentences = []
        for sentence in sentences:
            if len(sentence.split()) > 8:  # إذا كانت الجملة طويلة
                # تقسيمها إلى جمل أقصر
                words = sentence.split()
                mid = len(words) // 2
                short_sentences.append(' '.join(words[:mid]) + '.')
                short_sentences.append(' '.join(words[mid:]))
            else:
                short_sentences.append(sentence)
        return '. '.join(short_sentences)

    def _add_repetition(self, response: str) -> str:
        """إضافة التكرار للأطفال الصغار"""
        # إضافة تكرار للكلمات المهمة
        important_words = ["fun", "happy", "good", "nice", "pretty"]
        for word in important_words:
            if word in response.lower():
                response = re.sub(
                    r'\b' + re.escape(word) + r'\b',
                    f"{word}, very {word}",
                    response,
                    flags=re.IGNORECASE,
                    count=1  # فقط مرة واحدة لتجنب الإفراط
                )
        return response

    def _add_sound_effects(self, response: str) -> str:
        """إضافة الأصوات للأطفال"""
        sound_mappings = {
            "cat": "meow",
            "dog": "woof",
            "cow": "moo",
            "bird": "tweet",
            "car": "vroom",
            "train": "choo-choo",
            "water": "splash",
            "wind": "whoosh"
        }
        for word, sound in sound_mappings.items():
            if word in response.lower():
                response = response.replace(word, f"{word} ({sound})", 1)
        return response

    def _add_educational_elements(self, response: str) -> str:
        """إضافة عناصر تعليمية"""
        # إضافة حقائق بسيطة
        educational_additions = {
            "animals": "Did you know that animals have families just like us?",
            "colors": "Colors make the world beautiful and bright!",
            "numbers": "Numbers help us count and understand the world!",
            "nature": "Nature is full of amazing surprises!",
            "friends": "Friends make everything more fun!"
        }
        response_lower = response.lower()
        response_parts = [response]
        for topic, fact in educational_additions.items():
            if topic in response_lower:
                response_parts.append(f" {fact}")
                break  # إضافة حقيقة واحدة فقط
        return "".join(response_parts)

    def _add_interactive_elements(self, response: str, child_age: int) -> str:
        """إضافة عناصر تفاعلية"""
        if child_age <= 6:
            # للأطفال الصغار: إضافة رموز تعبيرية
            emoji = random.choice(self.child_friendly_emojis)
            response = f"{emoji} {response}"
        return response

    def _add_encouragement(self, response: str) -> str:
        """إضافة التشجيع"""
        # إضافة عبارة تشجيعية في البداية أحياناً
        if random.random() < 0.3:  # 30% من الوقت
            encouragement = random.choice(self.encouraging_phrases)
            response = f"{encouragement} {response}"
        return response

    def _add_follow_up_question(self, response: str) -> str:
        """إضافة سؤال للمتابعة"""
        # إضافة سؤال للمتابعة في النهاية
        if not response.endswith('?'):
            question = random.choice(self.follow_up_questions)
            response = f"{response} {question}"
        return response

    def _apply_child_preferences(self, response: str, preferences: Dict[str, Any]) -> str:
        """تطبيق تفضيلات الطفل"""
        favorite_character = preferences.get("favorite_character")
        if favorite_character:
            # إضافة الشخصية المفضلة في الأمثلة
            if "for example" in response.lower() or "like" in response.lower():
                response = response.replace(
                    "like",
                    f"like {favorite_character} or like",
                    1
                )
        interests = preferences.get("interests", [])
        if interests:
            # ربط الاستجابة بالاهتمامات
            for interest in interests[:1]:  # أول اهتمام فقط
                if interest not in response.lower():
                    response_parts = [response, f" Just like when you're interested in {interest}!"]
                    response = "".join(response_parts)
                    break
        return response

    def detect_emotion(self, response: str) -> str:
        """اكتشاف المشاعر في الاستجابة"""
        emotion_keywords = {
            "happy": ["happy", "joy", "smile", "laugh", "fun", "great", "awesome", "wonderful"],
            "excited": ["excited", "amazing", "fantastic", "wow", "incredible", "awesome"],
            "curious": ["wonder", "question", "explore", "discover", "learn", "find out"],
            "caring": ["care", "love", "friend", "help", "support", "together"],
            "playful": ["play", "game", "fun", "silly", "laugh", "giggle"]
        }
        response_lower = response.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return emotion
        return "friendly"  # Default emotion