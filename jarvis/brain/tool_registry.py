import json
import re
from loguru import logger


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, agent_method, description: str, parameters: list[str]):
        self.tools[name] = {
            "method": agent_method,
            "description": description,
            "parameters": parameters,
        }
        logger.debug(f"Registered tool: {name}")

    def get_tool_descriptions(self) -> str:
        if not self.tools:
            return "No tools available."
        descriptions = []
        for name, tool in self.tools.items():
            params = ", ".join(tool["parameters"])
            descriptions.append(f"- {name}({params}): {tool['description']}")
        return "\n".join(descriptions)

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        if tool_name not in self.tools:
            return f"Unknown tool: {tool_name}"
        try:
            method = self.tools[tool_name]["method"]
            result = method(**kwargs)
            logger.info(f"Tool executed: {tool_name} -> {str(result)[:100]}")
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}: {e}")
            return f"Tool '{tool_name}' failed: {e}"

    def parse_tool_calls(self, response: str) -> list[dict]:
        pattern = r'\[TOOL:([a-z_]+)\((.*?)\)\]'
        matches = re.findall(pattern, response, re.DOTALL)
        calls = []
        for name, args_str in matches:
            name = name.strip()
            try:
                args = json.loads(f"{{{args_str.strip()}}}")
            except json.JSONDecodeError:
                args = {"text": args_str.strip()}
            calls.append({"tool": name, "args": args})
        return calls

    def clean_response(self, response: str) -> str:
        cleaned = re.sub(r'\[TOOL:[a-z_]+\(.*?\)\]', '', response, flags=re.DOTALL)
        return cleaned.strip()
