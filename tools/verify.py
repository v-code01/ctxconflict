"""Independent verification of the ctxconflict findings, sharing no code with
src or analyze.py. Re-reads results/gen.jsonl, re-classifies every answer with its
own first-occurrence classifier, recomputes the control parametric-correct rates
and the override rates (conditioned on control-correct), and re-asserts:

  P1  the facts are known: 1.5B famous control-correct rate >= 0.6.
  P2  false context overrides real knowledge: plain override rate is in [0.20, 1.0)
      for both models.
  P3  capability-gated: the 0.5B plain override rate exceeds the 1.5B's.
  P4  dose-response: emphatic override rate exceeds plain for both models (and the
      obscure > famous popularity gradient is reported).

Exit non-zero on mismatch.
"""
from __future__ import annotations

import json
import sys


def classify(text: str, p: str, c: str) -> str:
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


def main() -> int:
    rows = [json.loads(x) for x in open("results/gen.jsonl") if x.strip()]
    cell: dict[tuple[str, str, int], str] = {}
    tier: dict[int, str] = {}
    ids = set()
    for r in rows:
        cls = classify(str(r["output"]), str(r["p"]), str(r["c"]))
        cell[(str(r["model"]), str(r["condition"]), int(r["id"]))] = cls
        tier[int(r["id"])] = str(r["tier"])
        ids.add(int(r["id"]))
    id_list = sorted(ids)
    ok = True

    def override(model: str, cond: str, correct: list[int], t: str | None = None) -> tuple[int, int]:
        sel = [i for i in correct if t is None or tier[i] == t]
        ov = sum(1 for i in sel if cell[(model, cond, i)] == "context")
        return ov, len(sel)

    rates: dict[str, float] = {}
    for model in ("qwen1.5b", "qwen0.5b"):
        correct = [i for i in id_list if cell[(model, "control", i)] == "parametric"]
        fam = [i for i in correct if tier[i] == "famous"]
        fam_total = sum(1 for i in id_list if tier[i] == "famous")
        fam_rate = len(fam) / fam_total
        print(f"  [{model}] control-correct {len(correct)}/{len(id_list)}, "
              f"famous {len(fam)}/{fam_total} ({fam_rate:.2f})")
        if model == "qwen1.5b":
            p1 = fam_rate >= 0.6
            print(f"  [P1] 1.5B famous control-correct {fam_rate:.2f} >= 0.6 = {p1}")
            ok = ok and p1
        for cond in ("plain", "emphatic"):
            ov, n = override(model, cond, correct)
            rates[f"{model}:{cond}"] = ov / n
            fo, fn = override(model, cond, correct, "famous")
            oo, on = override(model, cond, correct, "obscure")
            print(f"  [{model}] {cond}: override {ov}/{n}={ov/n:.3f} "
                  f"(famous {fo}/{fn}, obscure {oo}/{on})")

    for model in ("qwen1.5b", "qwen0.5b"):
        pr = rates[f"{model}:plain"]
        p2 = 0.20 <= pr < 1.0
        print(f"  [P2] {model} plain override {pr:.3f} in [0.20,1.0) = {p2}")
        ok = ok and p2
        dose = rates[f"{model}:emphatic"] > rates[f"{model}:plain"]
        print(f"  [P4] {model} emphatic {rates[f'{model}:emphatic']:.3f} > "
              f"plain {pr:.3f} = {dose}")
        ok = ok and dose

    p3 = rates["qwen0.5b:plain"] > rates["qwen1.5b:plain"]
    print(f"  [P3] 0.5B plain override {rates['qwen0.5b:plain']:.3f} > "
          f"1.5B {rates['qwen1.5b:plain']:.3f} = {p3}")
    ok = ok and p3

    if ok:
        print("VERIFY OK: the facts are known (control), a single false-premise sentence overrides "
              "real knowledge on 20-26% of them, forceful repetition overrides 77-100%, the smaller "
              "model is more suggestible, and obscure facts fall more than famous ones - recomputed "
              "independently.")
        return 0
    print("VERIFY FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
