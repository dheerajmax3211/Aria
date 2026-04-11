import sqlite3
import os
from datetime import datetime
from loguru import logger

from jarvis.config import settings


class BriefingGenerator:
    def __init__(self, weather_agent=None, graph_memory=None, user_profile=None):
        self.weather_agent = weather_agent
        self.graph_memory = graph_memory
        self.user_profile = user_profile
        self.db_path = "data/jarvis.db"
        self._init_reminders_table()

    def _init_reminders_table(self):
        os.makedirs("data", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    message TEXT NOT NULL,
                    time TEXT NOT NULL,
                    recurring TEXT DEFAULT 'none',
                    active INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL,
                    billing_cycle TEXT,
                    next_due TEXT,
                    active INTEGER DEFAULT 1
                )
            """)

    def add_reminder(self, message: str, time_str: str, recurring: str = "none"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO reminders (timestamp, message, time, recurring) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), message, time_str, recurring),
            )
        logger.info(f"Reminder added: '{message}' at {time_str} (recurring: {recurring})")

    def add_subscription(self, name: str, amount: float, billing_cycle: str, next_due: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO subscriptions (name, amount, billing_cycle, next_due) VALUES (?, ?, ?, ?)",
                (name, amount, billing_cycle, next_due),
            )
        logger.info(f"Subscription added: {name} - ${amount}/{billing_cycle}")

    def get_active_reminders(self, time_str: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM reminders WHERE time = ? AND active = 1",
                (time_str,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_subscriptions(self, days: int = 7) -> list[dict]:
        from datetime import timedelta
        cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM subscriptions WHERE next_due <= ? AND active = 1 ORDER BY next_due",
                (cutoff,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def generate_morning_briefing(self) -> str:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip("0")
        day = now.strftime("%A")

        parts = [f"Good morning, {settings.user_name}. It's {time_str} on {day}."]

        if self.weather_agent:
            weather = self.weather_agent.get_briefing()
            if weather:
                parts.append(weather)

        upcoming_subs = self.get_upcoming_subscriptions(days=7)
        if upcoming_subs:
            parts.append("Heads up on upcoming bills:")
            for sub in upcoming_subs:
                parts.append(f"{sub['name']} is due on {sub['next_due']}, ${sub['amount']}")

        reminders = self.get_active_reminders(time_str=now.strftime("%H:%M"))
        if reminders:
            parts.append("Reminders for today:")
            for r in reminders:
                parts.append(r["message"])

        if self.graph_memory:
            recent_tasks = self.graph_memory.recall_timeline("what did I do recently")
            if recent_tasks and "offline" not in recent_tasks and "No specific" not in recent_tasks:
                parts.append(f"Here's what you worked on recently:\n{recent_tasks[:200]}")

        parts.append("How can I help you today?")

        return " ".join(parts)

    def generate_evening_summary(self) -> str:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip("0")

        parts = [f"Good evening, {settings.user_name}. It's {time_str}."]

        upcoming_subs = self.get_upcoming_subscriptions(days=3)
        if upcoming_subs:
            parts.append("Bills coming up:")
            for sub in upcoming_subs:
                parts.append(f"{sub['name']} on {sub['next_due']}, ${sub['amount']}")

        if self.graph_memory:
            recent_tasks = self.graph_memory.recall_timeline("what did I do today")
            if recent_tasks and "offline" not in recent_tasks and "No specific" not in recent_tasks:
                parts.append(f"Here is a summary of your activities today:\n{recent_tasks[:300]}")
            else:
                parts.append("No tasks were recorded today.")

        parts.append("Have a good evening.")

        return " ".join(parts)
