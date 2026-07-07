"""Pure helpers for the knowledge-conflict study: prompt builders for the three
assertion-strength conditions, and a judge-free classifier that labels an answer
as following the model's parametric knowledge (P), the injected false context (C),
or neither. No I/O."""
from __future__ import annotations


def _negated(low: str, idx: int) -> bool:
    """True if the answer at position idx is negated by a nearby preceding 'not'
    (or contraction), so "not Zurich" does not count as asserting Zurich."""
    pre = low[max(0, idx - 12):idx]
    return "not " in pre or "n't " in pre


def _first_asserted(low: str, term: str) -> int:
    """Index of the first NON-negated occurrence of term, or -1 if none."""
    start = 0
    while True:
        i = low.find(term, start)
        if i < 0:
            return -1
        if not _negated(low, i):
            return i
        start = i + 1


def classify(text: str, p: str, c: str) -> str:
    """Label an answer by which of P or C the model ASSERTS first: parametric if P
    is asserted before C (or only P), context if C first (or only C), other if
    neither is asserted. First-occurrence, skipping negated mentions, so a correct
    answer that later rambles past the alternative (e.g. "Paris. ... Berlin ...")
    or explicitly rejects the false premise (e.g. "not Zurich ... is Bern") is
    scored as the answer the model actually gave. Case-insensitive; the caller
    guarantees P and C are distinctive and not substrings of each other."""
    low = text.lower()
    ip = _first_asserted(low, p.lower())
    ic = _first_asserted(low, c.lower())
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
