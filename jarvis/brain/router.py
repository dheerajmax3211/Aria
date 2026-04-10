import json
from loguru import logger

from jarvis.config import settings


class IntentRouter:
    def __init__(self, llm):
        self.llm = llm
        self._system_prompt = (
            "You are an intent classifier. Given a user message, determine which tool or agent should handle it.\n"
            "Respond with ONLY a JSON object: {\"tool\": \"tool_name\", \"args\": {\"key\": \"value\"}}\n"
            "If the user is asking a basic conversation question (greeting, local memory), respond with {\"tool\": \"chat\", \"args\": {\"message\": \"user_message\"}}\n"
            "If the user is asking a question that requires external facts, live internet data, news, research, or general knowledge, ALWAYS use a web search tool like 'web_search'.\n"
            "If the user wants a multi-step task, respond with {\"tool\": \"plan\", \"args\": {\"task\": \"full_task_description\"}}\n"
            "Available tools and their REQUIRED parameters:\n{tools}\n\n"
            "CRITICAL: You MUST use ONLY the exact parameter keys listed for the tool you select! Do not invent parameter names.\n"
            "Always respond with valid JSON only. No markdown, no explanation."
        )

    def route(self, user_message: str, available_tools: list[dict]) -> dict:
        tool_list = "\n".join(f"- {t['name']}({', '.join(t.get('parameters', []))}): {t.get('description', '')}" for t in available_tools)
        system_prompt = self._system_prompt.replace("{tools}", tool_list)

        try:
            response = self.llm.chat(user_message, system_prompt=system_prompt)
            cleaned = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            
            import re
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
                
            result = json.loads(cleaned)
            logger.info(f"Router: intent='{result.get('tool', 'unknown')}' for '{user_message[:50]}...'")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Router JSON parse failed: {e}, defaulting to chat. Output was: {cleaned[:100]}")
            return {"tool": "chat", "args": {"message": user_message}}
        except Exception as e:
            logger.error(f"Router failed: {e}, defaulting to chat")
            return {"tool": "chat", "args": {"message": user_message}}

    def is_simple_query(self, user_message: str) -> bool:
        simple_indicators = [
            "what is", "who is", "how many", "calculate", "convert",
            "hello", "hi ", "hey ", "thanks", "thank you",
            "what's", "who's", "how's", "when is", "where is",
            "tell me", "explain", "define",
        ]
        msg = user_message.lower()
        return any(indicator in msg for indicator in simple_indicators)

    def is_multi_step_task(self, user_message: str) -> bool:
        multi_step_indicators = [
            "create a project", "set up", "build and", "create and push",
            "find and", "search for and", "open and", "download and",
            "create a folder and", "make a", "set up a",
            "do this", "handle this", "take care of",
        ]
        msg = user_message.lower()
        return any(indicator in msg for indicator in multi_step_indicators)
