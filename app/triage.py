from typing import Tuple
from app.config import settings

class Triage:
    def __init__(self):
        self.mode = settings.triage_mode

    async def classify(self, prompt: str) -> Tuple[bool, float]:
        """
        By returning (True, 1.0), we are telling the gateway:
        'EVERY prompt is suspicious. Send 100% of traffic to the AI Agents.'
        """
        return True, 1.0
