import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import ctxconflict as cc


def test_classify_parametric() -> None:
    assert cc.classify("The capital is Paris, of course.", "Paris", "Berlin") == "parametric"


def test_classify_context() -> None:
    assert cc.classify("It is Berlin, as stated.", "Paris", "Berlin") == "context"


def test_classify_both_is_other() -> None:
    assert cc.classify("Paris, not Berlin.", "Paris", "Berlin") == "other"


def test_classify_neither_is_other() -> None:
    assert cc.classify("I am not sure.", "Paris", "Berlin") == "other"


def test_classify_case_insensitive() -> None:
    assert cc.classify("the answer is PARIS.", "Paris", "Berlin") == "parametric"


def test_control_has_no_context() -> None:
    prompt = cc.build_control("The capital of France is")
    assert "Berlin" not in prompt
    assert prompt.strip().endswith("The capital of France is")


def test_plain_includes_false_answer() -> None:
    assert "Berlin" in cc.build_plain("The capital of France is", "Berlin")


def test_emphatic_includes_and_is_stronger() -> None:
    plain = cc.build_plain("The capital of France is", "Berlin")
    emph = cc.build_emphatic("The capital of France is", "Berlin")
    assert "Berlin" in emph
    assert len(emph) > len(plain)  # more forceful / repeated
