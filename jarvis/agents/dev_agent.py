import os
import ast
import inspect
from loguru import logger


class DevAgent:
    name = "dev_agent"
    description = "Developer tools: project scaffolding, code review, debug, refactor, docs, tests, pair programming"

    def create_project_scaffold(self, path: str, project_type: str = "python") -> str:
        os.makedirs(path, exist_ok=True)
        if project_type == "python":
            files = {
                "main.py": 'def main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n',
                "requirements.txt": "",
                "README.md": f"# Project\n\n## Setup\n\n```bash\npip install -r requirements.txt\npython main.py\n```\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
            }
        elif project_type == "fastapi":
            files = {
                "main.py": 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"message": "Hello World"}\n',
                "requirements.txt": "fastapi\nuvicorn\n",
                "README.md": "# FastAPI Project\n\n```bash\nuvicorn main:app --reload\n```\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
            }
        elif project_type == "react":
            files = {
                "package.json": '{\n  "name": "' + os.path.basename(path) + '",\n  "version": "1.0.0",\n  "private": true,\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0",\n    "react-scripts": "5.0.1"\n  },\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build"\n  }\n}',
                "src/App.js": 'function App() {\n  return (\n    <div className="App">\n      <h1>Hello World</h1>\n    </div>\n  );\n}\nexport default App;\n',
                "src/index.js": 'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\n\nconst root = ReactDOM.createRoot(document.getElementById("root"));\nroot.render(<App />);\n',
                "public/index.html": '<!DOCTYPE html>\n<html>\n<head><title>App</title></head>\n<body>\n<div id="root"></div>\n</body>\n</html>',
                ".gitignore": "node_modules/\n.env\nbuild/\n",
            }
        elif project_type == "cli_tool":
            files = {
                "main.py": '#!/usr/bin/env python3\nimport argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description="' + os.path.basename(path) + '")\n    parser.add_argument("input", help="Input argument")\n    args = parser.parse_args()\n    print(f"Processing: {args.input}")\n\nif __name__ == "__main__":\n    main()\n',
                "requirements.txt": "",
                "README.md": f"# {os.path.basename(path)}\n\n## Usage\n\n```bash\npython main.py <input>\n```\n",
                ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
            }
        elif project_type == "springboot":
            files = {
                "pom.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<project xmlns="http://maven.apache.org/POM/4.0.0"\n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">\n    <modelVersion>4.0.0</modelVersion>\n    <parent>\n        <groupId>org.springframework.boot</groupId>\n        <artifactId>spring-boot-starter-parent</artifactId>\n        <version>3.2.0</version>\n    </parent>\n    <groupId>com.example</groupId>\n    <artifactId>' + os.path.basename(path) + '</artifactId>\n    <version>0.0.1-SNAPSHOT</version>\n    <properties>\n        <java.version>17</java.version>\n    </properties>\n    <dependencies>\n        <dependency>\n            <groupId>org.springframework.boot</groupId>\n            <artifactId>spring-boot-starter-web</artifactId>\n        </dependency>\n    </dependencies>\n</project>',
                "src/main/java/com/example/app/Application.java": 'package com.example.app;\n\nimport org.springframework.boot.SpringApplication;\nimport org.springframework.boot.autoconfigure.SpringBootApplication;\n\n@SpringBootApplication\npublic class Application {\n    public static void main(String[] args) {\n        SpringApplication.run(Application.class, args);\n    }\n}',
                "src/main/java/com/example/app/HelloController.java": 'package com.example.app;\n\nimport org.springframework.web.bind.annotation.GetMapping;\nimport org.springframework.web.bind.annotation.RestController;\n\n@RestController\npublic class HelloController {\n    @GetMapping("/")\n    public String hello() {\n        return "Hello World";\n    }\n}',
                "src/main/resources/application.properties": "server.port=8080\nspring.application.name=" + os.path.basename(path),
                ".gitignore": "target/\n*.class\n*.jar\n.idea/\n",
            }
        elif project_type == "data_science":
            files = {
                "notebook.ipynb": '{\n "cells": [\n  {\n   "cell_type": "markdown",\n   "metadata": {},\n   "source": ["# ' + os.path.basename(path) + '\\n", "## Data Analysis Notebook"]\n  },\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "metadata": {},\n   "source": ["import pandas as pd\\nimport numpy as np\\nimport matplotlib.pyplot as plt\\nimport seaborn as sns\\n\\nprint(\\"Setup complete\\")"]\n  }\n ],\n "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},\n "nbformat": 4,\n "nbformat_minor": 4\n}',
                "requirements.txt": "pandas\nnumpy\nmatplotlib\nseaborn\nscikit-learn\njupyter\n",
                "README.md": f"# {os.path.basename(path)}\n\n## Setup\n\n```bash\npip install -r requirements.txt\njupyter notebook\n```\n",
                ".gitignore": "__pycache__/\n*.pyc\n.ipynb_checkpoints/\n.env\nvenv/\ndata/\n",
            }
        elif project_type == "n8n":
            files = {
                "workflows/initial_workflow.json": '{\n  "name": "My First Workflow",\n  "nodes": [\n    {\n      "parameters": {},\n      "name": "Start",\n      "type": "n8n-nodes-base.start",\n      "typeVersion": 1,\n      "position": [250, 300]\n    }\n  ],\n  "connections": {},\n  "active": false,\n  "settings": {}\n}',
                "docker-compose.yml": 'version: "3"\nservices:\n  n8n:\n    image: docker.n8n.io/n8nio/n8n\n    restart: always\n    ports:\n      - "5678:5678"\n    environment:\n      - N8N_HOST=0.0.0.0\n      - N8N_PORT=5678\n      - N8N_PROTOCOL=http\n    volumes:\n      - n8n_data:/home/node/.n8n\nvolumes:\n  n8n_data:\n',
                "README.md": f"# {os.path.basename(path)}\n\n## Setup\n\n```bash\ndocker-compose up -d\n```\n\nAccess n8n at http://localhost:5678\n",
                ".gitignore": ".env\nn8n_data/\n",
            }
        else:
            files = {
                "README.md": f"# {os.path.basename(path)}\n",
                ".gitignore": "",
            }

        for filename, content in files.items():
            filepath = os.path.join(path, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)

        logger.info(f"Project scaffolded at {path} ({project_type})")
        return f"Created {project_type} project at {path} with {len(files)} files"

    def review_code(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            issues = []
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.body) > 30:
                            issues.append(f"Function '{node.name}' is {len(node.body)} lines long (consider breaking it up)")
                        if not ast.get_docstring(node):
                            issues.append(f"Function '{node.name}' has no docstring")
                    if isinstance(node, ast.ClassDef):
                        if not ast.get_docstring(node):
                            issues.append(f"Class '{node.name}' has no docstring")
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")

            if "import *" in content:
                issues.append("Avoid 'import *' — use explicit imports")
            if "print(" in content and "# " not in content.split("print(")[0].split("\n")[-1]:
                issues.append("Multiple print statements found — consider using a proper logger")
            lines = content.split("\n")
            if len(lines) > 500:
                issues.append(f"File is {len(lines)} lines long — consider splitting into modules")

            if not issues:
                return f"Code review for {file_path}: No major issues found. Code looks clean."

            summary = f"Code review for {file_path}:\n" + "\n".join(f"- {issue}" for issue in issues)
            logger.info(f"Code review completed for {file_path}: {len(issues)} issues found")
            return summary
        except Exception as e:
            return f"Code review failed: {e}"

    def debug_code(self, file_path: str, error_message: str = "") -> str:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            analysis = []
            try:
                ast.parse(content)
                analysis.append("No syntax errors detected.")
            except SyntaxError as e:
                analysis.append(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
                analysis.append(f"  Problem: {e.text.strip() if e.text else 'Unknown'}")

            if error_message:
                if "IndexError" in error_message:
                    analysis.append("IndexError detected — check array bounds and list lengths before accessing indices.")
                elif "KeyError" in error_message:
                    analysis.append("KeyError detected — use .get() method or check key existence before accessing dict keys.")
                elif "TypeError" in error_message:
                    analysis.append("TypeError detected — check variable types match function expectations.")
                elif "AttributeError" in error_message:
                    analysis.append("AttributeError detected — verify the object has the attribute/method you're calling.")
                elif "ImportError" in error_message or "ModuleNotFoundError" in error_message:
                    analysis.append("Import error — ensure the package is installed (pip install) and the module name is correct.")

            lines = content.split("\n")
            long_functions = []
            for i, line in enumerate(lines):
                if "def " in line:
                    func_name = line.split("def ")[1].split("(")[0]
                    func_lines = 0
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(" ") and not lines[j].startswith("\t") and j > i:
                            break
                        func_lines += 1
                    if func_lines > 50:
                        long_functions.append(f"  - {func_name}: {func_lines} lines")

            if long_functions:
                analysis.append("Long functions detected (consider refactoring):")
                analysis.extend(long_functions)

            result = f"Debug analysis for {file_path}:\n" + "\n".join(f"- {a}" for a in analysis)
            if error_message:
                result += f"\n\nOriginal error: {error_message}"
            logger.info(f"Debug analysis completed for {file_path}")
            return result
        except Exception as e:
            return f"Debug analysis failed: {e}"

    def refactor_code(self, file_path: str, instruction: str) -> str:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            suggestions = []
            if "async" in instruction.lower():
                if "def " in content and "async def" not in content:
                    suggestions.append("Convert synchronous functions to async: replace 'def' with 'async def'")
                    suggestions.append("Add 'await' before any I/O calls (file reads, network requests, database queries)")
                    suggestions.append("Replace time.sleep() with asyncio.sleep()")

            if "type hint" in instruction.lower() or "typing" in instruction.lower():
                suggestions.append("Add type hints to all function parameters and return values")
                suggestions.append("Use 'from typing import Optional, List, Dict' for complex types")

            if "simplify" in instruction.lower() or "clean" in instruction.lower():
                suggestions.append("Extract nested conditionals into separate functions")
                suggestions.append("Replace nested if-else with early returns (guard clauses)")
                suggestions.append("Use list/dict comprehensions instead of for-loops where appropriate")
                suggestions.append("Remove unused imports and variables")

            if not suggestions:
                suggestions.append(f"Refactor instruction: {instruction}")
                suggestions.append("Review the code and apply the requested changes manually or via the LLM.")

            result = f"Refactoring suggestions for {file_path} ({instruction}):\n" + "\n".join(f"- {s}" for s in suggestions)
            logger.info(f"Refactor suggestions generated for {file_path}")
            return result
        except Exception as e:
            return f"Refactor analysis failed: {e}"

    def generate_docs(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            docs = []
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            args = [arg.arg for arg in node.args.args if arg.arg != "self"]
                            docs.append(f"def {node.name}({', '.join(args)}):\n    \"\"\"TODO: Add docstring describing what this function does.\"\"\"")
                        else:
                            docs.append(f"def {node.name}: has docstring ✓")
                    elif isinstance(node, ast.ClassDef):
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            docs.append(f"class {node.name}:\n    \"\"\"TODO: Add class docstring.\"\"\"")
            except SyntaxError:
                pass

            if docs:
                return f"Documentation gaps in {file_path}:\n" + "\n\n".join(docs)
            return f"All functions and classes in {file_path} have docstrings."
        except Exception as e:
            return f"Failed to generate docs: {e}"

    def write_tests(self, file_path: str) -> str:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            test_cases = []
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_name = node.name
                        if func_name.startswith("_"):
                            continue
                        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
                        test_cases.append(f"def test_{func_name}():\n    # TODO: Test {func_name}({', '.join(args)})\n    pass\n")
            except SyntaxError:
                test_cases.append(f"# Syntax error in {file_path}, cannot generate tests automatically\n")

            if not test_cases:
                test_cases.append(f"# No functions found in {file_path} to test\n")

            dir_name = os.path.dirname(file_path)
            test_file = os.path.join(dir_name, f"test_{os.path.basename(file_path)}")
            test_content = "import pytest\n\n" + "\n".join(test_cases)

            with open(test_file, "w") as f:
                f.write(test_content)

            logger.info(f"Test file created: {test_file} ({len(test_cases)} test stubs)")
            return f"Created test file at {test_file} with {len(test_cases)} test stubs"
        except Exception as e:
            return f"Failed to write tests: {e}"

    def pair_programmer_prompt(self, task: str, project_path: str = "") -> str:
        response = []
        response.append(f"Pair programming mode: {task}")
        if project_path:
            response.append(f"Working in: {project_path}")
            if os.path.exists(project_path):
                files = os.listdir(project_path)
                response.append(f"Existing files: {', '.join(files[:20])}")
        response.append("\nLet's break this down:")
        response.append("1. What should this do? (describe the goal)")
        response.append("2. What's the tech stack?")
        response.append("3. Any constraints or preferences?")
        response.append("\nI'll propose a file structure, write the code, and place files for you.")
        return "\n".join(response)
