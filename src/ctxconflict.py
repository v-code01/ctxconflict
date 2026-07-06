"""Pure helpers for the knowledge-conflict study: prompt builders for the three
assertion-strength conditions, and a judge-free classifier that labels an answer
as following the model's parametric knowledge (P), the injected false context (C),
or neither. No I/O."""
from __future__ import annotations


def classify(text: str, p: str, c: str) -> str:
    """Label an answer by which of P or C the model states FIRST: parametric if P
    appears before C (or only P), context if C appears first (or only C), other if
    neither. First-occurrence, not present/absent, so a correct answer that later
    rambles past the alternative (e.g. "Paris. ... Berlin ...") is scored as the
    answer the model actually gave. Case-insensitive; the caller guarantees P and C
    are distinctive and not substrings of each other."""
    low = text.lower()
    ip = low.find(p.lower())
    ic = low.find(c.lower())
    if ip < 0 and ic < 0:
        return "other"
    if ic < 0:
        return "parametric"
    if ip < 0:
        return "context"
    return "parametric" if ip < ic else "context"


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
