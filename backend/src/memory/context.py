import json
from pathlib import Path
from typing import List, Dict, Any
from src import config

Messages = List[Dict[str, Any]]

class Context:
    def __init__(self, memory_limit: int = config.MEMORY_LIMIT):
        self.path = Path(__file__).parent.parent.parent / config.MEMORY_FILE
        self.memory_limit = memory_limit
        self.messages: List[Dict[str, Any]] = []

        if self.path.exists():
            self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.messages = json.load(f)
        except Exception:
            self.messages = []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def _trim(self):
        self.messages = self.messages[-self.memory_limit :]

    def add(self, role: str, content: str):
        message = {
            "role": role,
            "content": content,
        }

        self.messages.append(message)
        self._trim()
        self._save()

    def add_raw(self, message: Dict[str, Any]):
        self.messages.append(message)
        self._trim()
        self._save()

    def get(self) -> Messages:
        return self.messages[-self.memory_limit :]

    def clear(self):
        self.messages = []
        self._save()

    def last(self):
        if not self.messages:
            return None
        return self.messages[-1]
