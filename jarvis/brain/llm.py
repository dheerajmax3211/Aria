import ollama
import requests
import re
from loguru import logger
from google import genai
from pydantic import BaseModel

from jarvis.config import settings


class LLMCore:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.local_model = settings.ollama_model
        
        self.gemini_client = None
        if settings.gemini_api_key:
            self.gemini_client = genai.Client(api_key=settings.gemini_api_key)
        self.fast_cloud_model = settings.fast_cloud_model
        self.reasoning_model = settings.reasoning_model
            
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

        if use_cloud and self.gemini_client:
            return self.chat_cloud_fast(user_message, system_prompt, conversation_history)
        elif use_cloud and settings.claude_configured:
            return self._call_claude(messages)

        return self.chat_local(messages)
    
    def chat_local(self, messages: list[dict]) -> str:
        """Strictly forces interaction over local Ollama model."""
        try:
            response = self.client.chat(
                model=self.local_model,
                messages=messages,
            )
            raw_text = response["message"]["content"].strip()
            
            think_match = re.search(r'<think>(.*?)</think>', raw_text, re.DOTALL)
            if think_match:
                think_content = think_match.group(1).strip()
                logger.info(f"LLM Reasoning ({len(think_content)} chars): {think_content[:100]}...")
            
            text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
            
            logger.info(f"LLM (Ollama/{self.local_model}) response ({len(text)} chars): {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            if self.gemini_client:
                return self.chat_cloud_fast(messages[-1]["content"], messages[0]["content"], messages[1:-1])
            return "I'm having trouble connecting to my brain. Please check Ollama."

    def _convert_to_gemini_format(self, messages: list[dict]):
        system_instruction = ""
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})
        return system_instruction, contents

    def chat_cloud_fast(self, user_message: str, system_prompt: str | None = None, conversation_history: list[dict] | None = None) -> str:
        """Hits Gemini Flash for rapid classification or background processing."""
        if not self.gemini_client:
            return self.chat(user_message, system_prompt, conversation_history)
            
        prompt = system_prompt or self.system_prompt
        messages = [{"role": "system", "content": prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            sys_inst, contents = self._convert_to_gemini_format(messages)
            response = self.gemini_client.models.generate_content(
                model=self.fast_cloud_model,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=sys_inst,
                )
            )
            logger.info(f"LLM (Gemini Flash) response ({len(response.text)} chars)")
            return response.text
        except Exception as e:
            logger.error(f"Gemini Fast cloud failed: {e}")
            return self.chat_local(messages)

    def chat_cloud_heavy(self, user_message: str, system_prompt: str | None = None, conversation_history: list[dict] | None = None) -> str:
        """Hits the flagship Gemini Pro reasoning model for dense logic/coding tasks."""
        if not self.gemini_client:
            return self.chat_cloud_fast(user_message, system_prompt, conversation_history)
            
        prompt = system_prompt or self.system_prompt
        messages = [{"role": "system", "content": prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            sys_inst, contents = self._convert_to_gemini_format(messages)
            response = self.gemini_client.models.generate_content(
                model=self.reasoning_model,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=sys_inst,
                    temperature=0.7
                )
            )
            logger.info(f"LLM (Gemini Heavy) response ({len(response.text)} chars)")
            return response.text
        except Exception as e:
            logger.error(f"Gemini Heavy cloud failed: {e}")
            return self.chat_cloud_fast(user_message, system_prompt, conversation_history)

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
            logger.info(f"LLM (Claude) response ({len(text)} chars)")
            return text
        except Exception as e:
            logger.error(f"Claude call failed: {e}")
            return self.chat_local(messages)

    def is_complex_task(self, user_message: str) -> bool:
        complex_indicators = [
            "write code", "build", "create a project", "debug", "refactor",
            "review this", "analyze", "research", "summarize this article",
            "explain in detail", "write a function", "implement",
            "compare", "evaluate", "design", "architecture",
        ]
        msg = user_message.lower()
        return any(indicator in msg for indicator in complex_indicators) or len(user_message) > 200
