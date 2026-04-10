import os
import subprocess
from loguru import logger


class GitAgent:
    name = "git_agent"
    description = "Git operations: init, add, commit, push, branch, status, diff"

    def init_repo(self, path: str) -> str:
        try:
            os.makedirs(path, exist_ok=True)
            result = subprocess.run(
                ["git", "init"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            logger.info(f"Git repo initialized at {path}")
            return f"Initialized git repo at {path}"
        except Exception as e:
            return f"Git init failed: {e}"

    def add_files(self, path: str, files: str = ".") -> str:
        try:
            result = subprocess.run(
                ["git", "add", files],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return f"Added {files} to staging"
        except Exception as e:
            return f"Git add failed: {e}"

    def commit(self, path: str, message: str) -> str:
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info(f"Committed: {message}")
                return f"Committed: {message}"
            return f"Commit failed: {result.stderr.strip()}"
        except Exception as e:
            return f"Git commit failed: {e}"

    def push(self, path: str, remote: str = "origin", branch: str = "main") -> str:
        try:
            result = subprocess.run(
                ["git", "push", "-u", remote, branch],
                cwd=path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info(f"Pushed to {remote}/{branch}")
                return f"Pushed to {remote}/{branch}"
            return f"Push failed: {result.stderr.strip()}"
        except Exception as e:
            return f"Git push failed: {e}"

    def create_branch(self, path: str, branch_name: str) -> str:
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return f"Created and switched to branch {branch_name}"
        except Exception as e:
            return f"Branch creation failed: {e}"

    def status(self, path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() or "Working tree clean"
        except Exception as e:
            return f"Git status failed: {e}"

    def diff(self, path: str) -> str:
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() or "No changes"
        except Exception as e:
            return f"Git diff failed: {e}"

    def add_remote(self, path: str, name: str, url: str) -> str:
        try:
            subprocess.run(
                ["git", "remote", "add", name, url],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return f"Added remote {name}: {url}"
        except Exception as e:
            return f"Add remote failed: {e}"
