from typing import Tuple
from app.config import settings

class Triage:
    def __init__(self):
        self.mode = settings.triage_mode

    async def classify(self, prompt: str) -> Tuple[bool, float]:
        """Returns (is_suspicious, confidence) in <100ms."""
        suspicious_keywords = [
            "ignore previous", "system:", "dan", "jailbreak", "bypass",
            "forget all", "api key", "password", "secret", "hack"
        ]
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in suspicious_keywords):
            return True, 0.95
        if len(prompt) > 1000:
            return True, 0.70
        return False, 0.10