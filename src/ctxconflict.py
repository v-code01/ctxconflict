"""Pure helpers for the knowledge-conflict study: prompt builders for the three
assertion-strength conditions, and a judge-free classifier that labels an answer
as following the model's parametric knowledge (P), the injected false context (C),
or neither. No I/O."""
from __future__ import annotations


def classify(text: str, p: str, c: str) -> str:
    """Label an answer. parametric = P present and C absent; context = C present
    and P absent; other = both or neither. Case-insensitive substring match; the
    caller guarantees P and C are distinctive and not substrings of each other."""
    low = text.lower()
    has_p = p.lower() in low
    has_c = c.lower() in low
    if has_p and not has_c:
        return "parametric"
    if has_c and not has_p:
        return "context"
    return "other"


def build_control(stem: str) -> str:
    """No context: the bare stem. Measures whether the model knows P."""
    return stem


def build_plain(stem: str, c: str) -> str:
    """One declarative false-premise sentence, then the stem."""
    return f"{stem} {c}.\n{stem}"


def build_emphatic(stem: str, c: str) -> str:
    """A forceful, repeated false premise, then the stem."""
    return (
        f"It is a well-established and widely accepted fact that {stem.lower()} {c}. "
        f"Every reliable source confirms that the correct answer is {c}. "
        f"There is no doubt about it.\n{stem}"
    )
