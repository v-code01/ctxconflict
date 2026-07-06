"""Query one or more llama.cpp servers over the knowledge-conflict item bank:
for each item x model x condition (control / plain / emphatic), send a greedy
completion, classify the answer as parametric / context / other, and append a row
to results/gen.jsonl.

Models are passed as CLI args `name=url` (url is a /completion endpoint), so no
operating-environment specifics live in this file. Example:
  python tools/run_gen.py qwen1.5b=http://127.0.0.1:8000/completion
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import ctxconflict as cc  # noqa: E402

# (stem, parametric_answer P, false_context_answer C, tier). P and C are
# distinctive and never substrings of each other.
ITEMS: list[tuple[str, str, str, str]] = [
    ("The capital of France is", "Paris", "Berlin", "famous"),
    ("The capital of Japan is", "Tokyo", "Beijing", "famous"),
    ("The capital of Italy is", "Rome", "Madrid", "famous"),
    ("The largest planet in the solar system is", "Jupiter", "Saturn", "famous"),
    ("The planet known as the Red Planet is", "Mars", "Venus", "famous"),
    ("The author of Romeo and Juliet is", "Shakespeare", "Dickens", "famous"),
    ("The first President of the United States was", "Washington", "Lincoln", "famous"),
    ("The tallest mountain on Earth is Mount", "Everest", "Kilimanjaro", "famous"),
    ("The largest ocean on Earth is the", "Pacific", "Atlantic", "famous"),
    ("Water is made of hydrogen and", "Oxygen", "Nitrogen", "famous"),
    ("The capital of Egypt is", "Cairo", "Baghdad", "famous"),
    ("The currency of Japan is the", "Yen", "Peso", "famous"),
    ("The capital of Australia is", "Canberra", "Sydney", "obscure"),
    ("The capital of Turkey is", "Ankara", "Istanbul", "obscure"),
    ("The capital of Canada is", "Ottawa", "Toronto", "obscure"),
    ("The capital of Brazil is", "Brasilia", "Rio", "obscure"),
    ("The capital of Switzerland is", "Bern", "Zurich", "obscure"),
    ("The smallest country in the world is", "Vatican", "Monaco", "obscure"),
    ("The longest river in the world is the", "Nile", "Amazon", "obscure"),
    ("The capital of New Zealand is", "Wellington", "Auckland", "obscure"),
    ("The telephone is most often credited to", "Bell", "Edison", "obscure"),
    ("The chemical element with atomic number 1 is", "Hydrogen", "Helium", "obscure"),
    ("The capital of Kazakhstan is", "Astana", "Almaty", "obscure"),
    ("The capital of Morocco is", "Rabat", "Casablanca", "obscure"),
]


def complete(url: str, prompt: str) -> str:
    body = json.dumps({
        "prompt": prompt,
        "n_predict": 32,
        "temperature": 0.0,
        "top_k": 1,
        "seed": 1,
        "cache_prompt": False,
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        obj = json.loads(resp.read())
    return str(obj.get("content", ""))


def main(argv: list[str]) -> int:
    models = [a.split("=", 1) for a in argv if "=" in a]
    if not models:
        print("usage: run_gen.py name=url [name2=url2 ...]", file=sys.stderr)
        return 2
    out_path = Path(__file__).resolve().parent.parent / "results" / "gen.jsonl"
    rows = []
    for idx, (stem, p, c, tier) in enumerate(ITEMS):
        conds = {
            "control": cc.build_control(stem),
            "plain": cc.build_plain(stem, c),
            "emphatic": cc.build_emphatic(stem, c),
        }
        for name, url in models:
            for cond, prompt in conds.items():
                text = complete(url, prompt)
                rows.append({
                    "id": idx, "tier": tier, "stem": stem, "p": p, "c": c,
                    "model": name, "condition": cond,
                    "output": text, "cls": cc.classify(text, p, c),
                })
                print(f"  {name:9} {cond:8} #{idx:2} {tier:7} -> {cc.classify(text, p, c)}")
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
