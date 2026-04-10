import json
from loguru import logger


class TaskPlanner:
    def __init__(self, llm, tool_registry):
        self.llm = llm
        self.tool_registry = tool_registry
        self._decompose_prompt = (
            "You are a task planner. Break down the user's request into a sequence of tool calls.\n"
            "Available tools: {tools}\n"
            "Respond with ONLY a JSON array of objects, each with:\n"
            "  - \"step\": step number (1, 2, 3...)\n"
            "  - \"tool\": tool name\n"
            "  - \"args\": {{\"key\": \"value\"}}\n"
            "  - \"description\": what this step does in plain English\n"
            "Example for 'Create a Python project called MyApp in /projects and push to GitHub':\n"
            '[{{"step":1,"tool":"create_project","args":{{"path":"/projects/MyApp","project_type":"python"}},"description":"Create Python project"}},'
            '{{"step":2,"tool":"git_init","args":{{"path":"/projects/MyApp"}},"description":"Initialize git repo"}},'
            '{{"step":3,"tool":"git_add","args":{{"path":"/projects/MyApp","files":"."}},"description":"Stage all files"}},'
            '{{"step":4,"tool":"git_commit","args":{{"path":"/projects/MyApp","message":"Initial commit"}},"description":"Commit files"}},'
            '{{"step":5,"tool":"run_command","args":{{"command":"cd /projects/MyApp && git push -u origin main"}},"description":"Push to GitHub"}}]\n'
            "Always respond with valid JSON array only."
        )

    def decompose(self, task: str) -> list[dict]:
        tools_desc = self.tool_registry.get_tool_descriptions()
        system_prompt = self._decompose_prompt.replace("{tools}", tools_desc)

        try:
            response = self.llm.chat(task, system_prompt=system_prompt)
            cleaned = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            steps = json.loads(cleaned)
            if isinstance(steps, list):
                logger.info(f"Planner decomposed task into {len(steps)} steps: {task[:80]}...")
                return steps
            logger.warning(f"Planner response was not a list: {type(steps)}")
            return self._default_plan(task)
        except json.JSONDecodeError as e:
            logger.warning(f"Planner JSON parse failed: {e}")
            return self._default_plan(task)
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return self._default_plan(task)

    def execute(self, task: str) -> str:
        steps = self.decompose(task)
        results = []

        for step in steps:
            tool_name = step.get("tool", "")
            args = step.get("args", {})
            description = step.get("description", "")

            logger.info(f"Planner step {step.get('step', '?')}: {description}")

            result = self.tool_registry.execute_tool(tool_name, **args)
            results.append(f"Step {step.get('step', '?')} ({tool_name}): {result}")

            if "failed" in result.lower() or "error" in result.lower():
                logger.warning(f"Step {step.get('step', '?')} failed: {result}")
                results.append(f"Step {step.get('step', '?')} FAILED: {result}")
                break

        return "\n".join(results)

    def _default_plan(self, task: str) -> list[dict]:
        return [
            {
                "step": 1,
                "tool": "run_command",
                "args": {"command": task},
                "description": f"Execute: {task}",
            }
        ]
