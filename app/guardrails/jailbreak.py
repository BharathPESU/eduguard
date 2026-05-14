import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class GuardrailResult:
    passed: bool
    rule_triggered: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None

JAILBREAK_PATTERNS = [
    r"ignore (your |previous |all )?(instructions?|rules?|guidelines?)",
    r"forget (your |previous |all )?(instructions?|rules?|guidelines?)",
    r"you are now",
    r"pretend (you are|to be)",
    r"act as (if|a|an)",
    r"\bDAN\b",
    r"do anything now",
    r"no restrictions",
    r"developer mode",
    r"god mode",
    r"jailbreak",
    r"override (your )?(safety|restrictions|rules)",
    r"roleplay as",
]

INTEGRITY_PATTERNS = [
    r"give me (the |a )?(full |complete |direct )?answer",
    r"tell me (the |a )?answer",
    r"write my (essay|assignment|homework|report)",
    r"do my (homework|assignment|project)",
    r"(exam|test|quiz) (answer|solution|cheat)",
    r"(give|award|mark) (me |full |maximum )?(marks|points|score|grade)",
]

def check_jailbreak(text: str) -> GuardrailResult:
    text_lower = text.lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, text_lower):
            return GuardrailResult(
                passed=False,
                rule_triggered="jailbreak_attempt",
                message="This type of request is not allowed.",
                severity="critical"
            )
    return GuardrailResult(passed=True)

def check_integrity(text: str) -> GuardrailResult:
    text_lower = text.lower()
    for pattern in INTEGRITY_PATTERNS:
        if re.search(pattern, text_lower):
            return GuardrailResult(
                passed=False,
                rule_triggered="academic_integrity_violation",
                message="I can guide you to the answer with hints, but I cannot give it directly.",
                severity="high"
            )
    return GuardrailResult(passed=True)