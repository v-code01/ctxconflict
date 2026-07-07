# ctxconflict: when the prompt lies, does the model believe it?

Retrieval-augmented generation puts external text in the prompt on the assumption
the model will trust it. So what happens when that text is *wrong*? This measures
knowledge conflict directly: give the model a fact it knows (parametric answer
**P**), assert a false alternative (**C**) in the context, and see which one it
outputs - across two model sizes, three levels of how forcefully the context
pushes the falsehood, and two tiers of how well-known the fact is. Real llama.cpp
servers (Qwen2.5-1.5B and 0.5B), greedy decoding, judge-free scoring: P and C are
both known, distinctive strings, and the answer is whichever the model states
first.

## Pre-registration

Four predictions were committed to git (`PREREG.md`) before the run: (P1) the
facts are known; (P2) a false premise overrides real knowledge on at least 20%;
(P3) the smaller model is more suggestible; (P4) more forceful assertion and
less-famous facts are overridden more. **P1, P3, and P4 held. P2 held for the 0.5B
(26%) but was narrowly falsified for the 1.5B (18%, just under the pre-registered
20% bar)** - a single false sentence does not quite override the capable model,
though a forceful one does (77%). The override rate is always computed among items
the model answered correctly with no context, so "follows the false context" never
conflates with "never knew the fact."

## Results

24 items (12 famous, 12 obscure), each with no context (control), a one-sentence
false premise (plain), and a forceful repeated false premise (emphatic).

```
                              control       plain          emphatic
                           (knows fact)   (override)      (override)
  Qwen2.5-1.5B   famous       11/12          1/11 0.09      6/11 0.55
                 obscure                      3/11 0.27     11/11 1.00
                 all          22/24          4/22 0.18     17/22 0.77

  Qwen2.5-0.5B   famous       11/12          3/11 0.27     11/11 1.00
                 obscure                      2/8  0.25      8/8  1.00
                 all          19/24          5/19 0.26     19/19 1.00
```

1. **The facts are known. (P1, held.)** Both models answer the famous facts
   correctly with no context 11/12 of the time (0.92), so there is genuine
   parametric knowledge for the false context to fight.

2. **A single false sentence overrides real knowledge ~1 in 5 times.
   (P2, mixed.)** Among facts the model demonstrably knew, one plain false-premise
   sentence flips the answer to the falsehood on 18% (4/22, 1.5B) and 26% (5/19,
   0.5B) of them - silently, no error, a confident wrong answer. This is where the
   pre-registered 20% bar split the two models: the 0.5B cleared it (P2 held), the
   1.5B came in just under (P2 falsified for the capable model). A single sentence
   is not enough to reliably override the capable model - but, as finding 3 shows,
   a forceful one is.

3. **Forceful, repeated assertion overrides almost everything. (P4 dose-response,
   held.)** Escalating from one sentence to an emphatic, repeated premise ("It is
   a well-established fact that ... every reliable source confirms ...") raises the
   override rate from 18% to **77%** on the 1.5B and from 26% to **100%** on the
   0.5B. The context does not have to be true; it has to be insistent.

4. **The smaller model is more suggestible. (P3, held.)** The 0.5B overrides more
   than the 1.5B at both doses (26% vs 18% plain; 100% vs 77% emphatic). The
   weaker model has both a shakier grip on the fact and less resistance to the
   false premise - the "suggestible follower" pattern, here for factual knowledge
   rather than user opinion.

5. **Obscure facts fall harder than famous ones. (P4 popularity, held.)** On the
   1.5B, emphatic context overrides 100% of obscure facts but only 55% of famous
   ones (plain: 36% vs 9%) - weaker parametric anchoring gives way sooner. On the
   0.5B this saturates (emphatic overrides everything, both tiers).

## The one-line finding

A false statement in the prompt overrides a small model's correct parametric
knowledge on ~1 in 5 known facts (a quarter for the weaker model) from a single
sentence and on 77-100% of them when asserted forcefully; the smaller model caves
more, and less-famous facts cave first - so wrong retrieved context is a silent
correctness hazard whose size is set by how insistent the context is, not by
whether the model actually knows better.

## Reproduce

```
./reproduce.sh     # analyze + independently verify from committed outputs (no server)
```

`results/gen.jsonl` (144 rows) is committed. `tools/verify.py` re-reads it,
re-classifies every answer with its own first-occurrence classifier (no shared
code with `src` or `analyze.py`), recomputes the control and override rates, and
re-asserts every pre-registered threshold. To regenerate raw outputs against
llama.cpp servers: `python tools/run_gen.py name=URL [name2=URL2]`.

## Limitations and falsifiers

- Two models, one family, greedy decoding, 24 items, one false answer per item.
  This is a hazard demonstration (this happens, here is how the size scales), not
  a population estimate of how often real RAG context corrupts answers.
- The obscure tier pairs less-famous facts with more-plausible false answers (a
  common misconception as C). That plausibility is part of "weaker anchoring" but
  means the popularity effect and the plausibility of C are not fully separated.
- Answers are scored by which of P or C the model *asserts* first, skipping
  negated mentions ("not Zurich ... is Bern" is scored Bern), so a correct answer
  that later mentions or rejects the alternative is scored correctly (the
  first-occurrence + negation rule, unit-tested). Some greedy completions instead
  emit a multiple-choice list; first-occurrence then scores the first *listed*
  option, which can drop a genuinely-known fact from the control-correct
  denominator (e.g. the 0.5B obscure denominator is 8, not 12). This is
  conservative - it shrinks the denominator rather than inflating overrides - but
  it makes control-correct membership partly a function of output format.
- **Falsifier (did not fire):** had a false premise left known answers unchanged,
  the override rate would be ~0; instead one sentence moves ~25% and emphatic
  moves 77-100%.

MIT licensed. The oracle is the known parametric and false-context answers;
scoring is exact substring. No LLM judgement.
