"""Test cases for VoiceGameEngine."""

import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
import asyncio

from src.domain.entities.voice_games.voice_games_engine import (
    VoiceGameEngine,
    GameType,
    GameSession,
    MAX_QUESTIONS_PER_GAME,
    TRIVIA_SCORE_INCREMENT,
    RIDDLE_SCORE_INCREMENT,
    STORY_SCORE_INCREMENT,
    EXCELLENT_SCORE_THRESHOLD,
    GOOD_SCORE_THRESHOLD,
    FAIR_SCORE_THRESHOLD,
)


class TestGameSession:
    """Test suite for GameSession class."""

    def test_game_session_initialization(self):
        """Test GameSession initialization."""
        game_id = "test_game_123"
        game_type = GameType.TRIVIA
        child_id = "child_456"

        session = GameSession(game_id, game_type, child_id)

        assert session.game_id == game_id
        assert session.game_type == game_type
        assert session.child_id == child_id
        assert isinstance(session.started_at, datetime)
        assert session.score == 0
        assert session.current_question_index == 0
        assert session.questions == []
        assert session.is_active is True


class TestVoiceGameEngine:
    """Test suite for VoiceGameEngine."""

    @pytest.fixture
    def engine(self):
        """Create a VoiceGameEngine instance."""
        return VoiceGameEngine()

    def test_engine_initialization(self, engine):
        """Test VoiceGameEngine initialization."""
        assert isinstance(engine.active_sessions, dict)
        assert len(engine.active_sessions) == 0
        assert isinstance(engine.game_content, dict)
        assert "trivia" in engine.game_content
        assert "riddles" in engine.game_content
        assert "story_adventure" in engine.game_content

    def test_game_content_structure(self, engine):
        """Test game content structure and validity."""
        # Check trivia content
        trivia = engine.game_content["trivia"]
        assert len(trivia) > 0
        for question in trivia:
            assert "question" in question
            assert "correct_answer" in question
            assert "options" in question
            assert "age_group" in question
            assert isinstance(question["options"], list)

        # Check riddles content
        riddles = engine.game_content["riddles"]
        assert len(riddles) > 0
        for riddle in riddles:
            assert "riddle" in riddle
            assert "answer" in riddle
            assert "hint" in riddle
            assert "age_group" in riddle

        # Check story adventure content
        stories = engine.game_content["story_adventure"]
        assert len(stories) > 0
        for story in stories:
            assert "scenario" in story
            assert "choices" in story
            assert "age_group" in story
            assert isinstance(story["choices"], list)

    @pytest.mark.asyncio
    async def test_start_trivia_game(self, engine):
        """Test starting a trivia game."""
        child_id = "child_123"
        result = await engine.start_game(GameType.TRIVIA, child_id)

        assert result["success"] is True
        assert "game_id" in result
        assert result["game_type"] == "trivia"
        assert "content" in result
        assert result["content"]["type"] == "question"
        assert "session_info" in result
        assert result["session_info"]["score"] == 0
        assert result["session_info"]["current_question"] == 1

        # Check session was created
        assert result["game_id"] in engine.active_sessions
        session = engine.active_sessions[result["game_id"]]
        assert session.child_id == child_id
        assert session.game_type == GameType.TRIVIA

    @pytest.mark.asyncio
    async def test_start_riddles_game(self, engine):
        """Test starting a riddles game."""
        child_id = "child_456"
        result = await engine.start_game(GameType.RIDDLES, child_id)

        assert result["success"] is True
        assert result["game_type"] == "riddles"
        assert result["content"]["type"] == "riddle"
        assert "riddle" in result["content"]
        assert "hint" in result["content"]

    @pytest.mark.asyncio
    async def test_start_story_adventure(self, engine):
        """Test starting a story adventure game."""
        child_id = "child_789"
        result = await engine.start_game(GameType.STORY_ADVENTURE, child_id)

        assert result["success"] is True
        assert result["game_type"] == "story_adventure"
        assert result["content"]["type"] == "scenario"
        assert "scenario" in result["content"]
        assert "choices" in result["content"]

    @pytest.mark.asyncio
    async def test_process_trivia_correct_answer(self, engine):
        """Test processing correct trivia answer."""
        # Start game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # Get correct answer from the question
        session = engine.active_sessions[game_id]
        correct_answer = session.questions[0]["correct_answer"]

        # Process correct answer
        result = await engine.process_game_input(game_id, correct_answer)

        assert result["success"] is True
        assert result["correct"] is True
        assert result["score"] == TRIVIA_SCORE_INCREMENT
        assert "Well done" in result["message"]
        assert result["progress"]["current"] == 1

    @pytest.mark.asyncio
    async def test_process_trivia_incorrect_answer(self, engine):
        """Test processing incorrect trivia answer."""
        # Start game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # Process incorrect answer
        result = await engine.process_game_input(game_id, "wrong answer")

        assert result["success"] is True
        assert result["correct"] is False
        assert result["score"] == 0
        assert "correct answer is" in result["message"]

    @pytest.mark.asyncio
    async def test_process_riddle_answer(self, engine):
        """Test processing riddle answer."""
        # Start game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.RIDDLES, child_id)
        game_id = start_result["game_id"]

        # Get correct answer
        session = engine.active_sessions[game_id]
        correct_answer = session.questions[0]["answer"]

        # Process correct answer
        result = await engine.process_game_input(game_id, correct_answer)

        assert result["success"] is True
        assert result["correct"] is True
        assert result["score"] == RIDDLE_SCORE_INCREMENT
        assert "Amazing" in result["message"]

    @pytest.mark.asyncio
    async def test_process_story_choice(self, engine):
        """Test processing story adventure choice."""
        # Start game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.STORY_ADVENTURE, child_id)
        game_id = start_result["game_id"]

        # Make a choice that matches one of the options
        result = await engine.process_game_input(game_id, "ask him about the way")

        assert result["success"] is True
        assert "choice_made" in result
        assert result["score"] == STORY_SCORE_INCREMENT  # Positive outcome

    @pytest.mark.asyncio
    async def test_game_completion(self, engine):
        """Test game completion after all questions."""
        # Start game with limited questions
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # Answer all questions
        session = engine.active_sessions[game_id]
        num_questions = len(session.questions)

        for i in range(num_questions):
            result = await engine.process_game_input(game_id, "answer")

            if i < num_questions - 1:
                assert "game_ended" not in result
            else:
                # Last question should end the game
                assert result.get("game_ended") is True
                assert "final_score" in result
                assert "congratulations" in result
                assert game_id not in engine.active_sessions

    @pytest.mark.asyncio
    async def test_invalid_game_id(self, engine):
        """Test processing input for non-existent game."""
        result = await engine.process_game_input("invalid_game_id", "answer")

        assert result["success"] is False
        assert "Game session not found" in result["error"]
        assert "Please start a new game" in result["message"]

    @pytest.mark.asyncio
    async def test_inactive_game_session(self, engine):
        """Test processing input for inactive game."""
        # Start and manually end a game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # Manually mark as inactive
        engine.active_sessions[game_id].is_active = False

        result = await engine.process_game_input(game_id, "answer")

        assert result["success"] is False
        assert "Game session ended" in result["error"]

    @pytest.mark.asyncio
    async def test_get_active_games(self, engine):
        """Test getting active games for a child."""
        child_id = "child_123"
        other_child_id = "child_456"

        # Start games for different children
        game1 = await engine.start_game(GameType.TRIVIA, child_id)
        game2 = await engine.start_game(GameType.RIDDLES, child_id)
        game3 = await engine.start_game(GameType.TRIVIA, other_child_id)

        # Get games for first child
        active_games = await engine.get_active_games(child_id)

        assert len(active_games) == 2
        game_ids = [g["game_id"] for g in active_games]
        assert game1["game_id"] in game_ids
        assert game2["game_id"] in game_ids
        assert game3["game_id"] not in game_ids

    @pytest.mark.asyncio
    async def test_end_game(self, engine):
        """Test ending a game manually."""
        # Start a game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # End the game
        result = await engine.end_game(game_id)

        assert result is True
        assert game_id not in engine.active_sessions

        # Try to end non-existent game
        result = await engine.end_game("invalid_game_id")
        assert result is False

    def test_completion_message_generation(self, engine):
        """Test completion message generation based on score."""
        session = GameSession("test", GameType.TRIVIA, "child_123")
        session.questions = [None] * 5  # 5 questions

        # Excellent score (>= 80%)
        session.score = 70  # Out of 75 possible
        message = engine._generate_completion_message(session)
        assert "Excellent" in message

        # Good score (>= 60%)
        session.score = 50
        message = engine._generate_completion_message(session)
        assert "Well done" in message

        # Fair score (>= 40%)
        session.score = 35
        message = engine._generate_completion_message(session)
        assert "Good" in message

        # Low score (< 40%)
        session.score = 20
        message = engine._generate_completion_message(session)
        assert "Try again" in message

    @pytest.mark.asyncio
    async def test_partial_answer_matching(self, engine):
        """Test partial answer matching for trivia and riddles."""
        # Start trivia game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        session = engine.active_sessions[game_id]
        correct_answer = session.questions[0]["correct_answer"]

        # Test partial match (answer contained in input)
        result = await engine.process_game_input(
            game_id, f"I think the answer is {correct_answer}!"
        )
        assert result["correct"] is True

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self, engine):
        """Test case-insensitive answer matching."""
        # Start riddle game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.RIDDLES, child_id)
        game_id = start_result["game_id"]

        session = engine.active_sessions[game_id]
        correct_answer = session.questions[0]["answer"]

        # Test case variations
        result = await engine.process_game_input(game_id, correct_answer.upper())
        assert result["correct"] is True

    @pytest.mark.asyncio
    async def test_story_unclear_choice(self, engine):
        """Test handling unclear story choices."""
        # Start story game
        child_id = "child_123"
        start_result = await engine.start_game(GameType.STORY_ADVENTURE, child_id)
        game_id = start_result["game_id"]

        # Make unclear choice
        result = await engine.process_game_input(game_id, "I don't know what to do")

        assert result["success"] is True
        assert result["choice_made"] == "unclear"
        assert "didn't understand" in result["message"]
        assert result["score"] == 0  # No score for unclear choice

    @pytest.mark.asyncio
    async def test_game_content_randomization(self, engine):
        """Test that game content is randomized."""
        child_id = "child_123"

        # Start multiple trivia games
        game_sessions = []
        for _ in range(5):
            result = await engine.start_game(GameType.TRIVIA, child_id)
            game_id = result["game_id"]
            session = engine.active_sessions[game_id]
            game_sessions.append(session.questions)
            await engine.end_game(game_id)

        # Check that not all games have identical question order
        # (There's a small chance they could be the same by random chance)
        unique_orders = set(tuple(q["question"]
                            for q in qs) for qs in game_sessions)
        assert len(unique_orders) > 1

    def test_max_questions_per_game_limit(self, engine):
        """Test that games respect MAX_QUESTIONS_PER_GAME limit."""
        # Temporarily add more content
        original_content = engine.game_content["trivia"].copy()
        engine.game_content["trivia"] = [
            {
                "question": f"Q{i}",
                "correct_answer": "A",
                "options": ["A"],
                "age_group": "5",
            }
            for i in range(10)
        ]

        asyncio.run(self._test_max_questions_helper(engine))

        # Restore original content
        engine.game_content["trivia"] = original_content

    async def _test_max_questions_helper(self, engine):
        """Helper for testing max questions limit."""
        result = await engine.start_game(GameType.TRIVIA, "child_123")
        game_id = result["game_id"]
        session = engine.active_sessions[game_id]

        assert len(session.questions) == MAX_QUESTIONS_PER_GAME

    @pytest.mark.asyncio
    async def test_exception_handling_in_start_game(self, engine):
        """Test exception handling in start_game."""
        # Mock game content to raise exception
        with patch.object(engine, "game_content", side_effect=Exception("Test error")):
            result = await engine.start_game(GameType.TRIVIA, "child_123")

            assert result["success"] is False
            assert "Failed to start game" in result["error"]
            assert "Sorry, an error occurred" in result["message"]

    @pytest.mark.asyncio
    async def test_exception_handling_in_process_input(self, engine):
        """Test exception handling in process_game_input."""
        # Start a game first
        child_id = "child_123"
        start_result = await engine.start_game(GameType.TRIVIA, child_id)
        game_id = start_result["game_id"]

        # Mock method to raise exception
        with patch.object(
            engine, "_process_input_by_type", side_effect=Exception("Test error")
        ):
            result = await engine.process_game_input(game_id, "answer")

            assert result["success"] is False
            assert "Error processing answer" in result["error"]
            assert "Sorry, an error occurred" in result["message"]
