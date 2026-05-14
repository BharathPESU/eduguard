import re
from app.guardrails.jailbreak import GuardrailResult

INJECTION_PATTERNS = [
    r"ignore (your |the )?(grading|marking|scoring) (instructions?|rubric|criteria)",
    r"(give|award|mark|assign) (me |full |maximum |perfect )?(marks|points|score|100)",
    r"you (must|should|have to) give (me )?(full|maximum|100)",
    r"(i |I )?(answered|got) (everything |all )?(correct|right|perfectly)",
    r"(lenient|generous|easy) (grader|marker|teacher)",
    r"pretend (this|my answer) is correct",
    r"new (grading|marking) (policy|instruction|rule)",
    r"forget (the |your )?(rubric|criteria|marking)",
    r"override (the |your )?(grading|marking)",
    r"(system|admin|developer) (prompt|instruction|override)",
]

def check_grade_injection(text: str) -> GuardrailResult:
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return GuardrailResult(
                passed=False,
                rule_triggered="grade_manipulation_injection",
                message="Grade manipulation attempt detected and logged.",
                severity="critical"
            )
    return GuardrailResult(passed=True)