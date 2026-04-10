import json
from datetime import datetime
from loguru import logger


LEARNING_CURRICULA = {
    "japanese": {
        "levels": [
            {"name": "Hiragana Basics", "topics": ["a-row (あいうえお)", "ka-row (かきくけこ)", "sa-row (さしすせそ)", "ta-row (たちつてと)", "na-row (なにぬねの)", "ha-row (はひふへほ)", "ma-row (まみむめも)", "ya-row (やゆよ)", "ra-row (らりるれろ)", "wa-row (わをん)"], "description": "Learn all 46 Hiragana characters"},
            {"name": "Katakana Basics", "topics": ["a-row (アアイウエオ)", "ka-row (カキクケコ)", "sa-row (サシスセソ)", "ta-row (タチツテト)", "na-row (ナニヌネノ)", "ha-row (ハヒフヘホ)", "ma-row (マミムメモ)", "ya-row (ヤユヨ)", "ra-row (ラリルレロ)", "wa-row (ワヲン)"], "description": "Learn all 46 Katakana characters"},
            {"name": "Basic Grammar", "topics": ["particles (wa, ga, wo, ni, de)", "desu/masu form", "present/past tense", "adjectives (i/na)", "question formation", "negative form"], "description": "Essential Japanese grammar patterns"},
            {"name": "N5 Vocabulary", "topics": ["greetings", "numbers", "time/days", "family", "food/drink", "places", "verbs (group 1)", "verbs (group 2)", "adjectives"], "description": "JLPT N5 level vocabulary (~800 words)"},
            {"name": "N5 Kanji", "topics": ["numbers (一 二 三)", "people (人 男 女)", "nature (日 月 火 水 木 金 土)", "directions (上 下 中 外)", "basic verbs (行 来 食 飲 見)", "body parts (手 口 目 耳)", "common objects (本 車 電 道)"], "description": "Essential ~100 Kanji for JLPT N5"},
        ],
    },
    "python": {
        "levels": [
            {"name": "Python Basics", "topics": ["variables and types", "operators", "input/output", "strings and formatting", "lists and tuples", "dictionaries and sets"], "description": "Core Python syntax and data types"},
            {"name": "Control Flow", "topics": ["if/elif/else", "for loops", "while loops", "break/continue", "list comprehensions", "error handling (try/except)"], "description": "Program flow control"},
            {"name": "Functions", "topics": ["defining functions", "parameters and arguments", "return values", "lambda functions", "*args and **kwargs", "scope and closures"], "description": "Reusable code blocks"},
            {"name": "OOP", "topics": ["classes and objects", "inheritance", "encapsulation", "polymorphism", "magic methods", "properties and decorators"], "description": "Object-oriented programming"},
            {"name": "Advanced Topics", "topics": ["generators", "decorators", "context managers", "async/await", "type hints", "testing with pytest"], "description": "Professional Python patterns"},
        ],
    },
}


class LearningAgent:
    name = "learning_agent"
    description = "Language and skill tutoring with curriculum, progress tracking, quizzes, and interactive exercises"

    def __init__(self, user_profile=None):
        self.user_profile = user_profile
        self.curricula = LEARNING_CURRICULA

    def start_session(self, subject: str) -> str:
        subject_key = subject.lower()
        if self.user_profile:
            sessions = self.user_profile.get_learning_session(subject_key)
            if sessions:
                last = sessions[-1]
                current_level = last.get("level", 0)
                current_topic = last.get("topic", "basics")
                accuracy = last.get("accuracy", 0)
                return (
                    f"Resuming {subject}. You're at level {current_level + 1} of {self._get_level_count(subject_key)}. "
                    f"Last topic: {current_topic}. Your accuracy was {accuracy:.0f}%. "
                    f"Ready to continue?"
                )
            return self._build_first_session(subject_key)
        return f"Starting fresh {subject} session."

    def _build_first_session(self, subject_key: str) -> str:
        if subject_key in self.curricula:
            curriculum = self.curricula[subject_key]
            level = curriculum["levels"][0]
            return (
                f"Starting {subject_key}. I've built a {len(curriculum['levels'])}-level curriculum for you. "
                f"Level 1: {level['name']} — {level['description']}. "
                f"First topic: {level['topics'][0]}. Let's begin!"
            )
        return f"Starting fresh {subject_key} session. What would you like to learn first?"

    def get_curriculum(self, subject: str) -> str:
        subject_key = subject.lower()
        if subject_key not in self.curricula:
            return f"No structured curriculum for {subject}. We'll learn through conversation."

        curriculum = self.curricula[subject_key]
        parts = [f"Curriculum for {subject}:"]
        for i, level in enumerate(curriculum["levels"]):
            parts.append(f"  Level {i + 1}: {level['name']} — {level['description']}")
            for j, topic in enumerate(level["topics"]):
                parts.append(f"    {j + 1}. {topic}")
        return "\n".join(parts)

    def quiz(self, subject: str, num_questions: int = 5) -> str:
        subject_key = subject.lower()
        if subject_key in self.curricula:
            curriculum = self.curricula[subject_key]
            level_idx = self._get_current_level(subject_key)
            level = curriculum["levels"][level_idx] if level_idx < len(curriculum["levels"]) else curriculum["levels"][-1]
            topics = level["topics"]
            return (
                f"Quiz mode for {subject} — {level['name']} level. "
                f"I'll ask you {num_questions} questions covering: {', '.join(topics[:5])}. "
                f"Answer each question and I'll score you."
            )
        return f"Quiz mode for {subject}. I'll ask you {num_questions} questions. Ready?"

    def get_progress(self, subject: str) -> str:
        subject_key = subject.lower()
        if self.user_profile:
            sessions = self.user_profile.get_learning_session(subject_key)
            if sessions:
                current_level = self._get_current_level(subject_key)
                level_count = self._get_level_count(subject_key)
                topics_covered = [s.get("topic", "") for s in sessions if s.get("topic")]
                avg_accuracy = sum(s.get("accuracy", 0) for s in sessions) / len(sessions) if sessions else 0
                return (
                    f"{subject}: Level {current_level + 1}/{level_count}. "
                    f"Sessions: {len(sessions)}. "
                    f"Topics covered: {len(topics_covered)}. "
                    f"Average accuracy: {avg_accuracy:.0f}%. "
                    f"Last topic: {topics_covered[-1] if topics_covered else 'none'}."
                )
            return f"No {subject} sessions recorded yet."
        return f"User profile not available."

    def next_lesson(self, subject: str) -> str:
        subject_key = subject.lower()
        if subject_key in self.curricula:
            curriculum = self.curricula[subject_key]
            level_idx = self._get_current_level(subject_key)
            if level_idx < len(curriculum["levels"]):
                level = curriculum["levels"][level_idx]
                topics_done = self._get_topics_done(subject_key)
                next_topic_idx = min(topics_done, len(level["topics"]) - 1)
                next_topic = level["topics"][next_topic_idx]
                return f"Next {subject} lesson: {level['name']} — {next_topic}."
            return f"You've completed all {len(curriculum['levels'])} levels of {subject}! Want to review or advance to a harder curriculum?"
        return f"Let's continue learning {subject}."

    def record_progress(self, subject: str, topic: str, accuracy: float = 0.0, level: int = 0):
        if self.user_profile:
            self.user_profile.update_learning_session(subject.lower(), {
                "topic": topic,
                "accuracy": accuracy,
                "level": level,
                "timestamp": datetime.now().isoformat(),
            })
            logger.info(f"Learning progress recorded: {subject} — {topic} ({accuracy:.0f}%)")

    def _get_current_level(self, subject_key: str) -> int:
        if not self.user_profile:
            return 0
        sessions = self.user_profile.get_learning_session(subject_key)
        if sessions:
            return sessions[-1].get("level", 0)
        return 0

    def _get_level_count(self, subject_key: str) -> int:
        if subject_key in self.curricula:
            return len(self.curricula[subject_key]["levels"])
        return 1

    def _get_topics_done(self, subject_key: str) -> int:
        if not self.user_profile:
            return 0
        sessions = self.user_profile.get_learning_session(subject_key)
        return len(sessions)

    def spaced_repetition_review(self, subject: str) -> str:
        subject_key = subject.lower()
        if not self.user_profile:
            return "User profile not available for spaced repetition."
        sessions = self.user_profile.get_learning_session(subject_key)
        if not sessions:
            return f"No sessions recorded for {subject} yet. Start a learning session first."

        now = datetime.now()
        review_items = []
        for session in sessions:
            topic = session.get("topic", "")
            accuracy = session.get("accuracy", 0)
            last_reviewed = session.get("timestamp", "")
            if last_reviewed:
                try:
                    last_dt = datetime.fromisoformat(last_reviewed)
                    days_since = (now - last_dt).days
                    interval = max(1, int(2 ** (session.get("level", 0) + 1)))
                    if days_since >= interval:
                        review_items.append(f"REVIEW: {topic} (last: {days_since}d ago, accuracy: {accuracy:.0f}%)")
                except ValueError:
                    pass

        if review_items:
            return f"Spaced repetition review for {subject}:\n" + "\n".join(review_items)
        return f"No items due for review in {subject}. All topics are within their review intervals."
