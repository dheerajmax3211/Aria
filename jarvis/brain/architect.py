import threading
import requests
from datetime import datetime
from loguru import logger

from jarvis.config import settings


class ArchitectAgent:
    """
    The Specialist. Runs heavy tasks (coding, debugging, architecture) 
    in a background thread using OpenRouter's Qwen model.
    Reports back to ARIA when done.
    """

    def __init__(self, user_name: str = "User"):
        self.user_name = user_name
        self.api_key = settings.openrouter_api_key
        self.model = settings.architect_model
        self._active = False
        self._result = None
        self._status = "idle"
        self._lock = threading.Lock()

    @property
    def is_working(self) -> bool:
        with self._lock:
            return self._active

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    def _call_architect(self, task: str, context: str = "", project_path: str = ""):
        with self._lock:
            self._active = True
            self._status = "thinking"

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://aria.local",
                "X-Title": "ARIA",
                "Content-Type": "application/json",
            }
            
            system_prompt = (
                "You are an expert software architect and senior developer. "
                "You are tasked with building, debugging, or refactoring production-ready code. "
                "Follow these rules:\n"
                "1. Write clean, secure, production-grade code.\n"
                "2. Include error handling, input validation, and logging.\n"
                "3. Use modern best practices and design patterns.\n"
                "4. If building a project, provide the full file structure and contents.\n"
                "5. If debugging, explain the root cause and provide the fix.\n"
                "6. If refactoring, explain what you changed and why.\n"
                "7. Always output code in a format that can be directly written to files.\n"
                "8. Use [FILE:path/to/file.ext] markers to denote file contents.\n"
                "Example: [FILE:main.py]\\nprint('hello')\\n[ENDFILE]"
            )

            user_msg = f"Task: {task}\n"
            if context:
                user_msg += f"\nContext:\n{context}\n"
            if project_path:
                user_msg += f"\nProject path: {project_path}\n"

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                "max_tokens": 8192,
                "temperature": 0.7,
            }

            logger.info(f"Architect started task: {task[:80]}...")

            with self._lock:
                self._status = "coding"

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=300,
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"]

            with self._lock:
                self._result = result
                self._status = "done"

            logger.info(f"Architect completed task: {task[:80]}...")

        except Exception as e:
            logger.error(f"Architect failed: {e}")
            with self._lock:
                self._result = f"Task failed: {e}"
                self._status = "failed"
        finally:
            with self._lock:
                self._active = False

    def start_task(self, task: str, context: str = "", project_path: str = ""):
        if self.is_working:
            return "I'm already working on a task. Please wait for it to finish."
        
        thread = threading.Thread(
            target=self._call_architect,
            args=(task, context, project_path),
            daemon=True,
        )
        thread.start()
        return f"I've assigned the Architect to your task. It's thinking deeply about '{task[:50]}...'. I'll let you know when it's done."

    def get_result(self) -> str | None:
        with self._lock:
            if self._status == "done" and self._result:
                result = self._result
                self._result = None
                self._status = "idle"
                return result
            return None

    def get_progress(self) -> str:
        with self._lock:
            if not self._active:
                return "The Architect is idle."
            return f"The Architect is currently {self._status}."
