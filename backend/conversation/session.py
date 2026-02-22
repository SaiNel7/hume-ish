from uuid import uuid4
from backend.config import MAX_HISTORY_TURNS


class HumeSession:
    def __init__(self):
        self.session_id = str(uuid4())
        self.history: list[dict] = []

    def add_turn(self, role: str, content: str) -> None:
        """Append a message and trim history to MAX_HISTORY_TURNS."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > MAX_HISTORY_TURNS:
            self.history = self.history[-MAX_HISTORY_TURNS:]
