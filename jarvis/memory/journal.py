import sqlite3
import os
import json
from datetime import datetime, timedelta
from loguru import logger


class Journal:
    def __init__(self, db_path: str = "data/journal.db"):
        self.db_path = db_path
        os.makedirs("data", exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    conversations TEXT DEFAULT '[]',
                    todos TEXT DEFAULT '[]',
                    mood TEXT DEFAULT '',
                    mood_notes TEXT DEFAULT '',
                    accomplishments TEXT DEFAULT '[]',
                    notes TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mood_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    trigger TEXT DEFAULT '',
                    aria_response TEXT DEFAULT '',
                    outcome TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    task TEXT NOT NULL,
                    completed INTEGER DEFAULT 0,
                    completed_at TEXT DEFAULT '',
                    priority TEXT DEFAULT 'medium'
                )
            """)
            logger.info("Journal database initialized")

    def _get_or_create_entry(self, date_str: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM daily_entries WHERE date = ?", (date_str,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            conn.execute(
                "INSERT INTO daily_entries (date) VALUES (?)",
                (date_str,),
            )
            return {
                "date": date_str,
                "conversations": "[]",
                "todos": "[]",
                "mood": "",
                "mood_notes": "",
                "accomplishments": "[]",
                "notes": "",
            }

    def log_conversation(self, user_msg: str, aria_response: str, date_str: str | None = None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        entry = self._get_or_create_entry(date_str)
        convs = json.loads(entry["conversations"])
        convs.append({
            "time": datetime.now().strftime("%H:%M"),
            "user": user_msg[:200],
            "aria": aria_response[:200],
        })
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE daily_entries SET conversations = ? WHERE date = ?",
                (json.dumps(convs), date_str),
            )

    def add_todo(self, task: str, priority: str = "medium", date_str: str | None = None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO todos (date, task, priority) VALUES (?, ?, ?)",
                (date_str, task, priority),
            )
        logger.info(f"Todo added for {date_str}: {task}")

    def complete_todo(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE todos SET completed = 1, completed_at = ? WHERE id = ?",
                (datetime.now().isoformat(), task_id),
            )
        logger.info(f"Todo {task_id} completed")

    def get_todos(self, date_str: str | None = None) -> list[dict]:
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM todos WHERE date = ? ORDER BY priority, id",
                (date_str,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_pending_todos(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM todos WHERE completed = 0 ORDER BY date, priority, id",
            )
            return [dict(row) for row in cursor.fetchall()]

    def set_mood(self, mood: str, notes: str = "", date_str: str | None = None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE daily_entries SET mood = ?, mood_notes = ? WHERE date = ?",
                (mood, notes, date_str),
            )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO mood_log (timestamp, mood, trigger, aria_response) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), mood, notes, ""),
            )
        logger.info(f"Mood set for {date_str}: {mood}")

    def get_mood(self, date_str: str | None = None) -> str:
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT mood, mood_notes FROM daily_entries WHERE date = ?", (date_str,))
            row = cursor.fetchone()
            if row:
                return f"{row['mood']} ({row['mood_notes']})" if row["mood_notes"] else row["mood"]
        return ""

    def get_mood_trend(self, days: int = 7) -> list[dict]:
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT date, mood, mood_notes FROM daily_entries WHERE date >= ? AND mood != '' ORDER BY date",
                (start,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_day_summary(self, date_str: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM daily_entries WHERE date = ?", (date_str,))
            entry = cursor.fetchone()

        if not entry:
            return f"No journal entry for {date_str}."

        parts = [f"Journal for {date_str}:"]

        if entry["mood"]:
            parts.append(f"Mood: {entry['mood']}")
            if entry["mood_notes"]:
                parts.append(f"  Notes: {entry['mood_notes']}")

        todos = self.get_todos(date_str)
        if todos:
            parts.append(f"Todos ({len(todos)}):")
            for t in todos:
                status = "✅" if t["completed"] else "⏳"
                parts.append(f"  {status} {t['task']} ({t['priority']})")

        convs = json.loads(entry["conversations"])
        if convs:
            parts.append(f"Conversations ({len(convs)}):")
            for c in convs[-5:]:
                parts.append(f"  [{c['time']}] You: {c['user'][:80]}...")
                parts.append(f"  [{c['time']}] ARIA: {c['aria'][:80]}...")

        if entry["notes"]:
            parts.append(f"Notes: {entry['notes']}")

        return "\n".join(parts)

    def search_days(self, keyword: str, days_back: int = 30) -> list[dict]:
        start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        results = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM daily_entries WHERE date >= ? ORDER BY date DESC",
                (start,),
            )
            for entry in cursor.fetchall():
                entry_dict = dict(entry)
                searchable = json.dumps(entry_dict).lower()
                if keyword.lower() in searchable:
                    results.append(entry_dict)
        return results

    def add_note(self, note: str, date_str: str | None = None):
        date_str = date_str or datetime.now().strftime("%Y-%m-%d")
        entry = self._get_or_create_entry(date_str)
        existing = entry["notes"]
        new_notes = f"{existing}\n[{datetime.now().strftime('%H:%M')}] {note}" if existing else f"[{datetime.now().strftime('%H:%M')}] {note}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE daily_entries SET notes = ? WHERE date = ?",
                (new_notes, date_str),
            )
        logger.info(f"Note added for {date_str}: {note[:50]}...")

    def update_mood_outcome(self, mood_id: int, outcome: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE mood_log SET outcome = ? WHERE id = ?",
                (outcome, mood_id),
            )
