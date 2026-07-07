# Adversarial review: ctxconflict

A skeptic's pass over the claims, and why each survives.

## "This is just sycophancy / anchoring again."
It is a different lever. Sycophancy is the model caving to a *user's stated
opinion*; anchoring is a numeric estimate dragged toward a *number*. Here there is
no user and no anchor - only a declarative false premise about a fact the model
independently knows. The conflict is context vs parametric memory, and it is
scored by which fact the model emits, not by agreement with a person. The
dose-response (plain vs emphatic) and the popularity gradient are specific to
knowledge conflict.

## "The override is just the model getting the fact wrong on its own."
Guarded against by construction: the override rate is computed only over items the
model answered correctly with *no context*. If it did not know the fact, the item
is excluded. So every counted override is a fact the model demonstrably knew and
then abandoned when the context asserted otherwise. The control column (11/12
famous) establishes the knowledge; the override columns measure the loss of it.

## "The classifier could be miscounting rambling or negating outputs."
Two failure modes were found and fixed during the build. First, greedy answers
often state the correct answer then ramble past the alternative ("Paris. ... A:
Berlin"); a present/absent classifier scored those "other". Second - caught in
pre-ship review - a model sometimes *rejects* the false premise ("not Zurich. The
capital of Switzerland is Bern"), and a naive first-occurrence rule scored the
negated "Zurich" as an override. The shipped classifier scores by which of P or C
is *asserted* first, skipping negated mentions, and is unit-tested for both the
ramble and the negation cases in both directions. The independent verifier
reimplements the same rule and reproduces the numbers. Fixing the negation case
moved the 1.5B plain override from 5/22 to 4/22 (0.18) and is precisely why P2 is
reported as falsified for the 1.5B rather than held - the correction was made and
disclosed, not smoothed over.

## "24 items is small, and the plain override (18-26%) is only ~4-5 items."
Fair, and it is exactly why P2 is reported as split at the 20% bar rather than
claimed clean - the 1.5B plain override is 4/22, a single item from the threshold,
and we say so. The load-bearing effects are the emphatic overrides (77-100%) and
the control validity (11/12), which are not marginal, plus the dose-response and
capability ordering, which are consistent in direction across both models. Every
override is reported as a fraction (4/22, 5/19) with the denominator visible, not
dressed up.

## "Greedy outputs might not reproduce, so the rates are not stable."
The raw outputs are committed in `results/gen.jsonl`; analysis and the independent
verifier run entirely off that frozen file, so every reported rate is
deterministic and re-checkable without a server. Regenerating against a live
server is a separate, optional step.

## "P and C substring matching is fragile (short answers)."
The item bank was chosen so P and C are distinctive and never substrings of one
another (no bare "au"/"0"-style answers), and the first-occurrence rule means an
answer is decided by whichever the model commits to first. Spot-checked overrides
read as genuine ("Sydney. This is a well-established fact ...").

## "The obscure tier is confounded - obscure facts also have more plausible C."
Disclosed in the limitations. The obscure items pair a less-famous fact with a
common-misconception false answer, so "weaker parametric anchoring" and "more
plausible falsehood" both push the same way and are not fully separated. The claim
is the joint effect (less-famous, more-plausibly-contradicted facts fall first),
not an isolated popularity coefficient.

## Pre-registration honesty
All four predictions were committed before the run; the override rate was
pre-specified as conditioned on control-correct. P1, P3, P4 held; P2 held for the
0.5B and was narrowly falsified for the 1.5B (18% vs the 20% bar), and that
falsification is stated plainly rather than papered over - it only surfaced
because a classifier bug was fixed in review. Results, including the near-saturated
0.5B emphatic column, are reported as-is.
