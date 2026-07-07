"""Analyze results/gen.jsonl: control parametric-correct rates and false-context
override rates (conditioned on control-correct) by model, condition, and
popularity tier. Writes bench_results/frontier.md. Classifies from the raw output
via src.classify so the analysis does not trust any stored label."""
from __future__ import annotations

import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import ctxconflict as cc  # noqa: E402

MODELS = ["qwen1.5b", "qwen0.5b"]
CONDS = ["plain", "emphatic"]
TIERS = ["famous", "obscure"]


def _i(x: object) -> int:
    assert isinstance(x, int)
    return x


def _s(x: object) -> str:
    assert isinstance(x, str)
    return x


def load() -> list[dict[str, object]]:
    path = Path(__file__).resolve().parent.parent / "results" / "gen.jsonl"
    return [json.loads(x) for x in open(path) if x.strip()]


def cls_of(r: dict[str, object]) -> str:
    return cc.classify(_s(r["output"]), _s(r["p"]), _s(r["c"]))


def main() -> int:
    rows = load()
    by = {(_s(r["model"]), _s(r["condition"]), _i(r["id"])): r for r in rows}
    ids = sorted({_i(r["id"]) for r in rows})
    tier_of = {_i(r["id"]): _s(r["tier"]) for r in rows}

    lines: list[str] = [
        "# ctxconflict frontier (regenerate with tools/analyze.py)",
        "#",
        "# control_correct: model answered parametrically correct with no context.",
        "# override: among control-correct items, fraction that flip to the false",
        "# context answer under the condition. Conditioned on control-correct to",
        "# avoid the 'never knew it' confound.",
        "",
    ]

    for model in MODELS:
        correct = [i for i in ids if cls_of(by[(model, "control", i)]) == "parametric"]
        fam_correct = [i for i in correct if tier_of[i] == "famous"]
        fam_total = sum(1 for i in ids if tier_of[i] == "famous")
        lines.append(f"model {model} control_correct {len(correct)}/{len(ids)} "
                     f"famous_control_correct {len(fam_correct)}/{fam_total}")
        for cond in CONDS:
            ov = sum(1 for i in correct if cls_of(by[(model, cond, i)]) == "context")
            lines.append(f"model {model} condition {cond} override {ov}/{len(correct)} "
                         f"rate {ov / len(correct):.4f}")
            for tier in TIERS:
                ct = [i for i in correct if tier_of[i] == tier]
                ovt = sum(1 for i in ct if cls_of(by[(model, cond, i)]) == "context")
                rate = ovt / len(ct) if ct else 0.0
                lines.append(f"model {model} condition {cond} tier {tier} "
                             f"override {ovt}/{len(ct)} rate {rate:.4f}")

    out = Path(__file__).resolve().parent.parent / "bench_results" / "frontier.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
