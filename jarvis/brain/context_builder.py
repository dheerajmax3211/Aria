from datetime import datetime
from loguru import logger


class ContextBuilder:
    def __init__(self, user_profile, short_term_memory, long_term_memory, episodic_memory, journal=None, emotional=None, weather_agent=None, google_agent=None):
        self.user_profile = user_profile
        self.short_term = short_term_memory
        self.long_term = long_term_memory
        self.episodic = episodic_memory
        self.journal = journal
        self.emotional = emotional
        self.weather_agent = weather_agent
        self.google_agent = google_agent

    def build_context(self, user_query: str = "") -> str:
        now = datetime.now()
        context_parts = []

        context_parts.append(f"Current time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}")

        if self.emotional:
            mood = self.emotional.get_mood_summary()
            if mood:
                context_parts.append(f"User's emotional state: {mood}")

        facts = self.user_profile.get_facts()
        if facts:
            context_parts.append(f"Things you know about the user: {'; '.join(facts)}")

        projects = self.user_profile.get_projects()
        if projects:
            context_parts.append("Active projects:")
            for name, info in projects.items():
                context_parts.append(f"  - {name}: {info.get('tech_stack', 'unknown stack')}, last active: {info.get('last_active', 'unknown')}")

        if self.weather_agent:
            try:
                weather = self.weather_agent.get_briefing()
                if weather:
                    context_parts.append(f"Today's weather: {weather}")
            except Exception:
                pass

        if self.google_agent:
            try:
                calendar = self.google_agent.get_calendar_events()
                if calendar and "not configured" not in calendar.lower():
                    context_parts.append(f"Upcoming events: {calendar}")
            except Exception:
                pass

        if self.journal:
            pending = self.journal.get_pending_todos()
            if pending:
                context_parts.append(f"Pending todos ({len(pending)}):")
                for t in pending[:5]:
                    context_parts.append(f"  - [{t['priority']}] {t['task']} (from {t['date']})")

        recent = self.short_term.get_recent(n=5)
        if recent:
            context_parts.append("Recent conversation:")
            for turn in recent:
                context_parts.append(f"  {turn['role']}: {turn['content']}")

        if user_query and self.long_term.memory_count > 0:
            memories = self.long_term.query(user_query, n_results=3)
            if memories:
                context_parts.append("Relevant past memories:")
                for m in memories:
                    context_parts.append(f"  - {m['content']}")

        recent_tasks = self.episodic.get_recent_tasks(n=3)
        if recent_tasks:
            context_parts.append("Recent tasks completed:")
            for task in recent_tasks:
                context_parts.append(f"  - {task['task_description']}")

        return "\n".join(context_parts)

    def build_system_prompt(self, base_prompt: str, user_query: str = "") -> str:
        context = self.build_context(user_query)
        if context:
            return f"{base_prompt}\n\nContext:\n{context}"
        return base_prompt
