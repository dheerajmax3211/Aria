import os
import json
from loguru import logger


class GitHubIntegration:
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_repo(self, repo_name: str, private: bool = False, description: str = "") -> str:
        import requests
        url = f"{self.base_url}/user/repos"
        data = {
            "name": repo_name,
            "private": private,
            "description": description,
            "auto_init": True,
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            html_url = response.json()["html_url"]
            logger.info(f"GitHub repo created: {html_url}")
            return f"Created repo: {html_url}"
        return f"Failed to create repo: {response.text}"

    def create_issue(self, repo: str, title: str, body: str = "") -> str:
        import requests
        url = f"{self.base_url}/repos/{self.username}/{repo}/issues"
        data = {"title": title, "body": body}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            html_url = response.json()["html_url"]
            return f"Created issue: {html_url}"
        return f"Failed to create issue: {response.text}"

    def get_issues(self, repo: str, state: str = "open") -> str:
        import requests
        url = f"{self.base_url}/repos/{self.username}/{repo}/issues"
        params = {"state": state}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            issues = response.json()
            if not issues:
                return f"No {state} issues in {repo}"
            parts = [f"{i['number']}: {i['title']} ({i['state']})" for i in issues[:10]]
            return f"Issues in {repo}: " + "; ".join(parts)
        return f"Failed to get issues: {response.text}"

    def create_pr(self, repo: str, title: str, head: str, base: str = "main", body: str = "") -> str:
        import requests
        url = f"{self.base_url}/repos/{self.username}/{repo}/pulls"
        data = {"title": title, "head": head, "base": base, "body": body}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            html_url = response.json()["html_url"]
            return f"Created PR: {html_url}"
        return f"Failed to create PR: {response.text}"

    def star_repo(self, repo: str) -> str:
        import requests
        url = f"{self.base_url}/user/starred/{self.username}/{repo}"
        response = requests.put(url, headers=self.headers)
        if response.status_code == 204:
            return f"Starred {self.username}/{repo}"
        return f"Failed to star repo: {response.text}"

    def fork_repo(self, owner: str, repo: str) -> str:
        import requests
        url = f"{self.base_url}/repos/{owner}/{repo}/forks"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 202:
            return f"Forked {owner}/{repo} to your account"
        return f"Failed to fork repo: {response.text}"

    def clone_repo(self, repo_url: str, local_path: str) -> str:
        import subprocess
        try:
            subprocess.run(["git", "clone", repo_url, local_path], capture_output=True, text=True, timeout=120)
            return f"Cloned {repo_url} to {local_path}"
        except Exception as e:
            return f"Clone failed: {e}"
