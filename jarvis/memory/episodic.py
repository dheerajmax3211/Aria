import sqlite3
import os
from datetime import datetime
from loguru import logger


class EpisodicMemory:
    def __init__(self, db_path: str = "data/jarvis.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    result TEXT,
                    agent TEXT,
                    success INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    company TEXT,
                    role TEXT,
                    source TEXT,
                    status TEXT DEFAULT 'applied',
                    notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    topic TEXT,
                    progress TEXT,
                    next_session TEXT,
                    accuracy REAL
                )
            """)
            logger.info("Episodic memory database initialized")

    def log_task(self, task_description: str, result: str = "", agent: str = "", success: bool = True):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO episodes (timestamp, task_description, result, agent, success) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), task_description, result, agent, int(success)),
            )
        logger.info(f"Episodic memory logged: '{task_description[:80]}...'")

    def get_recent_tasks(self, n: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM episodes ORDER BY timestamp DESC LIMIT ?",
                (n,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def log_job_application(self, company: str, role: str, source: str = "", notes: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO job_applications (timestamp, company, role, source, notes) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), company, role, source, notes),
            )
        logger.info(f"Job application logged: {role} at {company}")

    def log_learning_progress(self, subject: str, topic: str = "", progress: str = "", next_session: str = "", accuracy: float = 0.0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO learning_progress (timestamp, subject, topic, progress, next_session, accuracy) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), subject, topic, progress, next_session, accuracy),
            )
        logger.info(f"Learning progress logged: {subject} - {topic}")

    def get_learning_progress(self, subject: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM learning_progress WHERE subject = ? ORDER BY timestamp DESC",
                (subject,),
            )
            return [dict(row) for row in cursor.fetchall()]
