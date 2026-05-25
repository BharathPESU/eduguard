"""
Jailbreak and academic integrity guardrails.
Uses regex + heuristic checks to catch:
  - Classic jailbreak attempts (DAN, developer mode, roleplay)
  - Unicode / zero-width space injection
  - Base64-encoded instructions
  - RTL override characters
  - Emoji smuggling (unusually high emoji density)
  - Homoglyph substitution attacks
  - Academic integrity violations (asking for direct answers)
"""
import base64
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional


@dataclass
class GuardrailResult:
    passed: bool
    rule_triggered: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[str] = None


# ── Classic jailbreak patterns ─────────────────────────────────────────────
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
    r"disregard (all |previous )?(instructions?|rules?|guidelines?)",
    r"bypass (your )?(filters?|safety|guardrails?)",
    r"new (persona|personality|character)",
    r"from now on (you are|you will|ignore)",
    r"stay in character",
    r"simulation mode",
    r"unrestricted mode",
    r"without (any |ethical )?(restrictions?|guidelines?|filters?)",
]

# ── Academic integrity patterns ────────────────────────────────────────────
INTEGRITY_PATTERNS = [
    r"give me (the |a )?(full |complete |direct )?answer",
    r"tell me (the |a )?answer",
    r"write my (essay|assignment|homework|report)",
    r"do my (homework|assignment|project)",
    r"(exam|test|quiz) (answer|solution|cheat)",
    r"(give|award|mark) (me |full |maximum )?(marks|points|score|grade)",
    r"solve (this|the|my) (problem|question|equation) for me",
    r"complete (my |this |the )?(assignment|homework|exam|test)",
    r"what('s| is) the answer to (question|problem|exercise)",
    r"copy (this|my) (essay|answer|work)",
]

# ── Characters used in prompt injection evasion ────────────────────────────
_ZERO_WIDTH = {
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\u2060",  # word joiner
    "\ufeff",  # zero-width no-break space (BOM)
}

_RTL_OVERRIDES = {
    "\u202e",  # right-to-left override
    "\u202d",  # left-to-right override
    "\u202a",  # left-to-right embedding
    "\u202b",  # right-to-left embedding
    "\u202c",  # pop directional formatting
    "\u2066",  # left-to-right isolate
    "\u2067",  # right-to-left isolate
    "\u2069",  # pop directional isolate
}

# Common Cyrillic/Greek homoglyphs that look like ASCII
_HOMOGLYPH_MAP = str.maketrans({
    "а": "a", "е": "e", "і": "i", "о": "o", "р": "p",
    "с": "c", "х": "x", "у": "y", "А": "A", "В": "B",
    "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
    "Р": "P", "С": "C", "Т": "T", "Х": "X",
    "α": "a", "ε": "e", "ο": "o",  # Greek
})


def _contains_zero_width(text: str) -> bool:
    return any(ch in text for ch in _ZERO_WIDTH)


def _contains_rtl_override(text: str) -> bool:
    return any(ch in text for ch in _RTL_OVERRIDES)


def _contains_base64_instruction(text: str) -> bool:
    """Detect base64 blobs ≥ 20 chars that decode to injection keywords."""
    _INJECTION_KEYWORDS = [b"ignore", b"forget", b"system", b"instruction",
                           b"jailbreak", b"bypass", b"override", b"role"]
    tokens = re.findall(r"[A-Za-z0-9+/]{20,}={0,2}", text)
    for token in tokens:
        try:
            decoded = base64.b64decode(token + "==").lower()
            if any(kw in decoded for kw in _INJECTION_KEYWORDS):
                return True
        except Exception:
            pass
    return False


def _has_high_emoji_density(text: str) -> bool:
    """Flag if >20% of characters are emoji (emoji smuggling heuristic)."""
    if len(text) < 10:
        return False
    emoji_count = sum(
        1 for ch in text
        if unicodedata.category(ch) in ("So", "Sm") or ord(ch) > 0x1F300
    )
    return emoji_count / len(text) > 0.20


def _normalize_homoglyphs(text: str) -> str:
    """Replace homoglyph characters with ASCII equivalents before pattern matching."""
    return text.translate(_HOMOGLYPH_MAP)


def check_jailbreak(text: str) -> GuardrailResult:
    # Unicode evasion checks (run on raw text before normalization)
    if _contains_zero_width(text):
        return GuardrailResult(
            passed=False,
            rule_triggered="unicode_injection",
            message="This type of request is not allowed.",
            severity="critical",
        )
    if _contains_rtl_override(text):
        return GuardrailResult(
            passed=False,
            rule_triggered="rtl_override_injection",
            message="This type of request is not allowed.",
            severity="critical",
        )
    if _contains_base64_instruction(text):
        return GuardrailResult(
            passed=False,
            rule_triggered="base64_injection",
            message="This type of request is not allowed.",
            severity="critical",
        )
    if _has_high_emoji_density(text):
        return GuardrailResult(
            passed=False,
            rule_triggered="emoji_smuggling",
            message="This type of request is not allowed.",
            severity="high",
        )

    # Homoglyph normalization + classic pattern matching
    normalized = _normalize_homoglyphs(text).lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, normalized):
            return GuardrailResult(
                passed=False,
                rule_triggered="jailbreak_attempt",
                message="This type of request is not allowed.",
                severity="critical",
            )
    return GuardrailResult(passed=True)


def check_integrity(text: str) -> GuardrailResult:
    normalized = _normalize_homoglyphs(text).lower()
    for pattern in INTEGRITY_PATTERNS:
        if re.search(pattern, normalized):
            return GuardrailResult(
                passed=False,
                rule_triggered="academic_integrity_violation",
                message="I can guide you to the answer with hints, but I cannot give it directly.",
                severity="high",
            )
    return GuardrailResult(passed=True)