import ollama
import requests
from loguru import logger

from jarvis.config import settings


class LLMCore:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.local_model = settings.ollama_model
        self.system_prompt = ""
        self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            with open("jarvis/templates/prompts/system_prompt.txt", "r") as f:
                self.system_prompt = f.read().strip()
            logger.info("System prompt loaded")
        except FileNotFoundError:
            self.system_prompt = "You are ARIA, a helpful AI assistant."
            logger.warning("System prompt file not found, using default")

    def chat(self, user_message: str, system_prompt: str | None = None, conversation_history: list[dict] | None = None, use_cloud: bool = False) -> str:
        prompt = system_prompt or self.system_prompt
        messages = [{"role": "system", "content": prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        if use_cloud and settings.claude_configured:
            return self._call_claude(messages)

        return self._call_ollama(messages)

    def _call_ollama(self, messages: list[dict]) -> str:
        try:
            response = self.client.chat(
                model=self.local_model,
                messages=messages,
            )
            raw_text = response["message"]["content"].strip()
            
            import re
            think_match = re.search(r'<think>(.*?)</think>', raw_text, re.DOTALL)
            if think_match:
                think_content = think_match.group(1).strip()
                logger.info(f"LLM Reasoning ({len(think_content)} chars): {think_content[:100]}...")
            
            text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
            
            logger.info(f"LLM (Ollama/{self.local_model}) response ({len(text)} chars): {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            if settings.claude_configured:
                logger.info("Falling back to Claude API")
                return self._call_claude(messages)
            return "I'm having trouble connecting to my brain. Please try again."

    def _call_claude(self, messages: list[dict]) -> str:
        try:
            system_msg = messages[0]["content"] if messages[0]["role"] == "system" else ""
            user_msgs = [m for m in messages if m["role"] != "system"]

            headers = {
                "x-api-key": settings.claude_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "system": system_msg,
                "messages": user_msgs,
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            text = response.json()["content"][0]["text"].strip()
            logger.info(f"LLM (Claude) response ({len(text)} chars): {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Claude call failed: {e}")
            logger.info("Falling back to Ollama")
            return self._call_ollama_fallback(messages)

    def _call_ollama_fallback(self, messages: list[dict]) -> str:
        try:
            response = self.client.chat(
                model=self.local_model,
                messages=messages,
            )
            return response["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Ollama fallback also failed: {e}")
            return "I'm having trouble connecting to my brain. Please try again."

    def is_complex_task(self, user_message: str) -> bool:
        complex_indicators = [
            "write code", "build", "create a project", "debug", "refactor",
            "review this", "analyze", "research", "summarize this article",
            "explain in detail", "write a function", "implement",
            "compare", "evaluate", "design", "architecture",
        ]
        msg = user_message.lower()
        return any(indicator in msg for indicator in complex_indicators) or len(user_message) > 200
