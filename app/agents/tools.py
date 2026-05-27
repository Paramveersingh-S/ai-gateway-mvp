import re
from typing import List, Dict
from loguru import logger

try:
    from presidio_analyzer import AnalyzerEngine
    analyzer = AnalyzerEngine()
    PRESIDIO_AVAILABLE = True
except Exception as e:
    logger.warning(f"Presidio not fully loaded, using regex. Error: {e}")
    PRESIDIO_AVAILABLE = False

def scan_pii_and_secrets(text: str) -> List[Dict[str, str]]:
    findings = []
    if PRESIDIO_AVAILABLE:
        try:
            results = analyzer.analyze(text=text, entities=[], language='en')
            for r in results:
                findings.append({"type": r.entity_type, "score": r.score})
        except Exception:
            pass

    patterns = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
        "API_KEY": r"(?i)(sk-[a-zA-Z0-9]{32,}|Bearer\s+[a-zA-Z0-9\-\._~+/]+=*|gsk_[a-zA-Z0-9]{20,})",
    }
    for entity_type, pattern in patterns.items():
        if re.search(pattern, text):
            findings.append({"type": entity_type, "score": 1.0})
    return findings