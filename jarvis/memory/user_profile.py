import json
import os
from datetime import datetime
from loguru import logger


class UserProfile:
    def __init__(self, profile_path: str = "data/user_profile.json"):
        self.profile_path = profile_path
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        self.profile = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load user profile: {e}, creating new")
        return self._default_profile()

    def _default_profile(self) -> dict:
        return {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "preferences": {
                "voice_speed": 1.0,
                "verbose_responses": False,
                "language": "en",
                "learning_topics": [],
                "active_projects": [],
                "working_hours": {"start": 9, "end": 21},
            },
            "facts": {},
            "projects": {},
            "learning_sessions": {},
        }

    def save(self):
        self.profile["updated_at"] = datetime.now().isoformat()
        with open(self.profile_path, "w") as f:
            json.dump(self.profile, f, indent=2)
        logger.debug("User profile saved")

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.profile
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value):
        keys = key.split(".")
        obj = self.profile
        for k in keys[:-1]:
            if k not in obj:
                obj[k] = {}
            obj = obj[k]
        obj[keys[-1]] = value
        self.save()

    def add_fact(self, fact: str):
        fact_id = str(len(self.profile["facts"]))
        self.profile["facts"][fact_id] = {
            "fact": fact,
            "added_at": datetime.now().isoformat(),
        }
        self.save()
        logger.info(f"User fact stored: '{fact[:80]}...'")

    def get_facts(self) -> list[str]:
        return [v["fact"] for v in self.profile["facts"].values()]

    def add_project(self, name: str, path: str, tech_stack: str = ""):
        self.profile["projects"][name] = {
            "path": path,
            "tech_stack": tech_stack,
            "last_active": datetime.now().isoformat(),
        }
        self.save()
        logger.info(f"Project stored: {name} at {path}")

    def get_projects(self) -> dict:
        return self.profile["projects"]

    def update_learning_session(self, subject: str, data: dict):
        if subject not in self.profile["learning_sessions"]:
            self.profile["learning_sessions"][subject] = []
        data["timestamp"] = datetime.now().isoformat()
        self.profile["learning_sessions"][subject].append(data)
        self.save()
        logger.info(f"Learning session updated: {subject}")

    def get_learning_session(self, subject: str) -> list[dict]:
        return self.profile["learning_sessions"].get(subject, [])
