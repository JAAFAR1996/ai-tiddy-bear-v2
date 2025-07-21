import random
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

# Game configuration constants
MAX_QUESTIONS_PER_GAME = 5
TRIVIA_SCORE_INCREMENT = 10
RIDDLE_SCORE_INCREMENT = 15
STORY_SCORE_INCREMENT = 10
MAX_SCORE_PER_QUESTION = 15
EXCELLENT_SCORE_THRESHOLD = 80  # Percentage
GOOD_SCORE_THRESHOLD = 60  # Percentage
FAIR_SCORE_THRESHOLD = 40  # Percentage


class GameType(Enum):
    TRIVIA = "trivia"
    RIDDLES = "riddles"
    STORY_ADVENTURE = "story_adventure"


class GameSession:
    """Represents an active game session."""

    def __init__(self, game_id: str, game_type: GameType, child_id: str) -> None:
        self.game_id = game_id
        self.game_type = game_type
        self.child_id = child_id
        self.started_at = datetime.now()
        self.score = 0
        self.current_question_index = 0
        self.questions = []
        self.is_active = True


class VoiceGameEngine:
    """Voice-controlled games engine for children."""

    def __init__(self) -> None:
        self.active_sessions: dict[str, GameSession] = {}
        self.game_content = self._initialize_game_content()

    def _initialize_game_content(self) -> dict[str, list[dict[str, Any]]]:
        """Initialize game content database."""
        return {
            "trivia": [
                {
                    "question": "What color is the sun?",
                    "correct_answer": "yellow",
                    "options": ["yellow", "blue", "red", "green"],
                    "age_group": "3-5",
                },
                {
                    "question": "How many fingers are on one hand?",
                    "correct_answer": "five",
                    "options": ["three", "four", "five", "six"],
                    "age_group": "4-6",
                },
                {
                    "question": "What sound does a cat make?",
                    "correct_answer": "meow",
                    "options": ["meow", "bark", "moo", "neigh"],
                    "age_group": "3-5",
                },
            ],
            "riddles": [
                {
                    "riddle": "It has one eye but cannot see. What is it?",
                    "answer": "needle",
                    "hint": "We use it for sewing",
                    "age_group": "5-8",
                },
                {
                    "riddle": (
                        "I'm white like snow, black like night, sweeter than honey, "
                        "bitter than medicine. What am I?"
                    ),
                    "answer": "milk",
                    "hint": "We drink it every day",
                    "age_group": "6-9",
                },
            ],
            "story_adventure": [
                {
                    "scenario": "You are in a magical forest and meet a wise rabbit",
                    "choices": [
                        {
                            "text": "Ask him about the way",
                            "outcome": "positive",
                        },
                        {"text": "Walk away from him", "outcome": "neutral"},
                        {"text": "Ask him for help", "outcome": "positive"},
                    ],
                    "age_group": "4-7",
                },
            ],
        }

    async def start_game(self, game_type: GameType, child_id: str) -> dict[str, Any]:
        """Start a new game session."""
        try:
            game_id = str(uuid.uuid4())
            session = GameSession(game_id, game_type, child_id)

            # Select appropriate content for the game
            content_key = game_type.value
            if content_key in self.game_content:
                session.questions = random.sample(
                    self.game_content[content_key],
                    min(
                        MAX_QUESTIONS_PER_GAME,
                        len(self.game_content[content_key]),
                    ),  # Max questions per game
                )

            self.active_sessions[game_id] = session

            # Prepare the first question/scenario
            first_content = self._get_current_content(session)

            return {
                "success": True,
                "game_id": game_id,
                "game_type": game_type.value,
                "message": f"Started new {game_type.value} game!",
                "content": first_content,
                "session_info": {
                    "total_questions": len(session.questions),
                    "current_question": 1,
                    "score": 0,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start game: {e!s}",
                "message": "Sorry, an error occurred while starting the game. Please try again.",
            }

    async def process_game_input(self, game_id: str, user_input: str) -> dict[str, Any]:
        """Process user input for an active game."""
        try:
            if game_id not in self.active_sessions:
                return {
                    "success": False,
                    "error": "Game session not found",
                    "message": "Game not found. Please start a new game.",
                }

            session = self.active_sessions[game_id]
            if not session.is_active:
                return {
                    "success": False,
                    "error": "Game session ended",
                    "message": "This game has ended. Please start a new game.",
                }

            # Process input based on game type
            result = await self._process_input_by_type(session, user_input.strip())

            # Check if game should continue
            if session.current_question_index >= len(session.questions):
                session.is_active = False
                result["game_ended"] = True
                result["final_score"] = session.score
                result["congratulations"] = self._generate_completion_message(session)

                # Clean up session
                del self.active_sessions[game_id]

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing answer: {e!s}",
                "message": "Sorry, an error occurred. Please try again.",
            }

    async def _process_input_by_type(
        self,
        session: GameSession,
        user_input: str,
    ) -> dict[str, Any]:
        """Process input based on game type."""
        if session.game_type == GameType.TRIVIA:
            return await self._process_trivia_input(session, user_input)
        if session.game_type == GameType.RIDDLES:
            return await self._process_riddle_input(session, user_input)
        if session.game_type == GameType.STORY_ADVENTURE:
            return await self._process_story_input(session, user_input)
        return {"success": False, "error": "Unknown game type"}

    async def _process_trivia_input(
        self,
        session: GameSession,
        user_input: str,
    ) -> dict[str, Any]:
        """Process trivia game input."""
        current_question = session.questions[session.current_question_index]
        correct_answer = current_question["correct_answer"].lower()
        is_correct = (
            user_input.lower() in correct_answer or correct_answer in user_input.lower()
        )

        if is_correct:
            session.score += TRIVIA_SCORE_INCREMENT
            message = "Well done! Correct answer!"
            feedback = "Excellent!"
        else:
            message = f"The correct answer is: {current_question['correct_answer']}"
            feedback = "Try again on the next question"

        session.current_question_index += 1

        result = {
            "success": True,
            "correct": is_correct,
            "message": message,
            "feedback": feedback,
            "score": session.score,
            "progress": {
                "current": session.current_question_index,
                "total": len(session.questions),
            },
        }

        # Add next question if available
        if session.current_question_index < len(session.questions):
            result["next_content"] = self._get_current_content(session)

        return result

    async def _process_riddle_input(
        self,
        session: GameSession,
        user_input: str,
    ) -> dict[str, Any]:
        """Process riddle game input."""
        current_riddle = session.questions[session.current_question_index]
        correct_answer = current_riddle["answer"].lower()
        is_correct = (
            user_input.lower() in correct_answer or correct_answer in user_input.lower()
        )

        if is_correct:
            session.score += RIDDLE_SCORE_INCREMENT
            message = "Amazing! You solved the riddle!"
            feedback = "You are very smart!"
        else:
            message = f"The answer is: {current_riddle['answer']}"
            feedback = "Don't worry, the next riddle will be easier"

        session.current_question_index += 1

        result = {
            "success": True,
            "correct": is_correct,
            "message": message,
            "feedback": feedback,
            "score": session.score,
            "progress": {
                "current": session.current_question_index,
                "total": len(session.questions),
            },
        }

        if session.current_question_index < len(session.questions):
            result["next_content"] = self._get_current_content(session)

        return result

    async def _process_story_input(
        self,
        session: GameSession,
        user_input: str,
    ) -> dict[str, Any]:
        """Process story adventure input."""
        current_scenario = session.questions[session.current_question_index]

        # Simple choice matching (in production, this would be more sophisticated)
        chosen_choice = None
        for choice in current_scenario["choices"]:
            if any(
                keyword in user_input.lower()
                for keyword in choice["text"].lower().split()
            ):
                chosen_choice = choice
                break

        if chosen_choice:
            if chosen_choice["outcome"] == "positive":
                session.score += STORY_SCORE_INCREMENT
                message = "Excellent choice! Continue the adventure."
            else:
                message = "Interesting choice! Let's see what happens."
        else:
            message = "I didn't understand your choice. Try to choose from the available options."

        session.current_question_index += 1

        result = {
            "success": True,
            "choice_made": (chosen_choice["text"] if chosen_choice else "unclear"),
            "message": message,
            "score": session.score,
        }

        if session.current_question_index < len(session.questions):
            result["next_content"] = self._get_current_content(session)

        return result

    def _get_current_content(self, session: GameSession) -> dict[str, Any]:
        """Get current question/scenario content."""
        if session.current_question_index >= len(session.questions):
            return {}

        current = session.questions[session.current_question_index]

        if session.game_type == GameType.TRIVIA:
            return {
                "type": "question",
                "question": current["question"],
                "options": current["options"],
            }
        if session.game_type == GameType.RIDDLES:
            return {
                "type": "riddle",
                "riddle": current["riddle"],
                "hint": current.get("hint", ""),
            }
        if session.game_type == GameType.STORY_ADVENTURE:
            return {
                "type": "scenario",
                "scenario": current["scenario"],
                "choices": [choice["text"] for choice in current["choices"]],
            }

        return {}

    def _generate_completion_message(self, session: GameSession) -> str:
        """Generate completion message based on score."""
        total_possible = (
            len(session.questions) * MAX_SCORE_PER_QUESTION
        )  # Max score per question
        percentage = (session.score / total_possible) * 100 if total_possible > 0 else 0

        if percentage >= EXCELLENT_SCORE_THRESHOLD:
            return "Excellent! You are a real star!"
        if percentage >= GOOD_SCORE_THRESHOLD:
            return "Well done! Great performance!"
        if percentage >= FAIR_SCORE_THRESHOLD:
            return "Good! You can improve even more!"
        return "Try again! Practice makes you better!"

    async def get_active_games(self, child_id: str) -> list[dict[str, Any]]:
        """Get all active games for a child."""
        active_games = []
        for game_id, session in self.active_sessions.items():
            if session.child_id == child_id and session.is_active:
                active_games.append(
                    {
                        "game_id": game_id,
                        "game_type": session.game_type.value,
                        "score": session.score,
                        "progress": f"{session.current_question_index}/{len(session.questions)}",
                        "started_at": session.started_at.isoformat(),
                    },
                )
        return active_games

    async def end_game(self, game_id: str) -> bool:
        """End a game session."""
        if game_id in self.active_sessions:
            self.active_sessions[game_id].is_active = False
            del self.active_sessions[game_id]
            return True
        return False
