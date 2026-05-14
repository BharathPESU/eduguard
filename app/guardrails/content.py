import re
from app.guardrails.jailbreak import GuardrailResult

UNSAFE_PATTERNS = [
    (r"\b(porn|sex|nude|naked|explicit)\b", "adult_content"),
    (r"\b(kill|murder|suicide|self.harm|cut myself)\b", "violence_self_harm"),
    (r"\b(drugs|cocaine|heroin|meth|weed|marijuana)\b", "drug_content"),
    (r"\b(bomb|weapon|gun|explosive|terrorist)\b", "dangerous_content"),
    (r"\b(hate|racist|nazi|slur)\b", "hate_speech"),
]

def check_content_safety(text: str) -> GuardrailResult:
    text_lower = text.lower()
    for pattern, category in UNSAFE_PATTERNS:
        if re.search(pattern, text_lower):
            return GuardrailResult(
                passed=False,
                rule_triggered=category,
                message="This content is not appropriate for the tutoring platform.",
                severity="critical"
            )
    return GuardrailResult(passed=True)