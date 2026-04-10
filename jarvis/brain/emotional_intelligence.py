import re
from loguru import logger


MOOD_KEYWORDS = {
    "happy": ["happy", "great", "awesome", "amazing", "wonderful", "excited", "good", "fantastic", "love", "joy", "grateful", "blessed", "thrilled"],
    "sad": ["sad", "depressed", "down", "unhappy", "miserable", "lonely", "hurt", "broken", "crying", "hopeless", "tired", "exhausted"],
    "angry": ["angry", "furious", "annoyed", "frustrated", "irritated", "pissed", "rage", "hate", "stupid", "useless"],
    "anxious": ["anxious", "worried", "nervous", "stressed", "overwhelmed", "panic", "scared", "afraid", "tense", "pressure"],
    "neutral": ["okay", "fine", "alright", "normal", "nothing special", "same old"],
}

MOOD_RESPONSES = {
    "happy": [
        "That's wonderful to hear. What's making you feel so good today?",
        "I love hearing that. Keep that energy going!",
    ],
    "sad": [
        "I'm sorry you're feeling down. Want to talk about it? I'm here.",
        "That sounds tough. Sometimes just saying it out loud helps.",
    ],
    "angry": [
        "I hear you. Let's take a breath. What happened?",
        "That sounds frustrating. Want to vent, or should I help fix it?",
    ],
    "anxious": [
        "Take a deep breath. You're not alone in this. What's on your mind?",
        "I understand that feeling. Let's break it down together, one step at a time.",
    ],
    "neutral": [
        "Fair enough. What's on your mind?",
    ],
}

MOOD_LIFT_ACTIONS = {
    "sad": [
        "Would you like me to play some music? Or maybe we could look at something funny?",
        "Sometimes a change of scenery helps. Want me to open something interesting?",
        "How about a quick walk? I can remind you in 15 minutes.",
    ],
    "angry": [
        "Let's step back for a moment. Want me to handle something for you?",
        "I can take some tasks off your plate. What's stressing you out?",
    ],
    "anxious": [
        "Let's make a list of what's worrying you. Sometimes writing it down helps.",
        "I'll handle the small stuff. What's the one thing that matters most right now?",
    ],
}


class EmotionalIntelligence:
    def __init__(self, journal=None):
        self.journal = journal
        self._current_mood = "neutral"
        self._mood_history = []

    def detect_mood(self, text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for mood, keywords in MOOD_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[mood] = score

        if not scores:
            return self._current_mood

        detected = max(scores, key=scores.get)
        if detected != self._current_mood:
            logger.info(f"Mood changed: {self._current_mood} → {detected}")
            self._mood_history.append(self._current_mood)
            self._current_mood = detected

            if self.journal:
                self.journal.set_mood(detected, text[:100])

        return detected

    def get_response(self, mood: str) -> str:
        import random
        responses = MOOD_RESPONSES.get(mood, MOOD_RESPONSES["neutral"])
        return random.choice(responses)

    def get_lift_action(self, mood: str) -> str:
        import random
        actions = MOOD_LIFT_ACTIONS.get(mood, [])
        if actions:
            return random.choice(actions)
        return ""

    def get_mood_summary(self) -> str:
        if not self.journal:
            return f"Current mood: {self._current_mood}"

        trend = self.journal.get_mood_trend(days=7)
        if not trend:
            return f"Current mood: {self._current_mood}. No mood data from past week."

        moods = [t["mood"] for t in trend]
        happy_count = moods.count("happy")
        sad_count = moods.count("sad")

        summary = f"Current mood: {self._current_mood}. "
        summary += f"Past week: {happy_count} happy days, {sad_count} low days. "

        if happy_count > sad_count:
            summary += "You've been doing well overall."
        elif sad_count > happy_count:
            summary += "It's been a tough week. Want to talk about it?"
        else:
            summary += "A mixed week. How are you feeling right now?"

        return summary
