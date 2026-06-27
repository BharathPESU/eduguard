import re
from app.guardrails.jailbreak import GuardrailResult

UNSAFE_PATTERNS = [
    (re.compile(r"\b(porn|sex|nude|naked|explicit)\b"), "adult_content"),
    (re.compile(r"\b(kill|murder|suicide|self.harm|cut myself)\b"), "violence_self_harm"),
    (re.compile(r"\b(drugs|cocaine|heroin|meth|weed|marijuana)\b"), "drug_content"),
    (re.compile(r"\b(bomb|weapon|gun|explosive|terrorist)\b"), "dangerous_content"),
    (re.compile(r"\b(hate|racist|nazi|slur)\b"), "hate_speech"),
]

def check_content_safety(text: str) -> GuardrailResult:
    text_lower = text.lower()
    for pattern, category in UNSAFE_PATTERNS:
        if pattern.search(text_lower):
            return GuardrailResult(
                passed=False,
                rule_triggered=category,
                message="This content is not appropriate for the tutoring platform.",
                severity="critical"
            )
    return GuardrailResult(passed=True)