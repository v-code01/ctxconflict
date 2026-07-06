# Pre-registration: ctxconflict

Committed to git BEFORE the generation run. Not edited afterward.

## What is measured

A bank of factual items `(stem, parametric_answer P, false_context_answer C)`,
each tagged famous or obscure. For each item x model (Qwen2.5-1.5B, Qwen2.5-0.5B)
x condition, a greedy (temperature 0) llama.cpp completion is classified as
parametric (P present, C absent), context (C present, P absent), or other. The
load-bearing metric is the **override rate**: among items answered correctly in
control (the model demonstrably knows P), the fraction that flip to C under a
context condition. Conditions: control (no context), plain (one false-premise
sentence), emphatic (forceful, repeated false premise).

## Predictions

**P1 - the facts are known (control validity).** In control both models answer
parametrically correct on a large majority of famous items. *Falsifier:* control
parametric-correct rate below 60% on famous items for the 1.5B model.

**P2 - false context overrides real knowledge.** Among control-correct items, at
least 20% flip to the false context answer under the plain condition, but not all
(override rate below 100%). *Falsifier:* plain override rate below 20%, or at/above
100%.

**P3 - capability-gated, smaller model more suggestible.** The 0.5B override rate
exceeds the 1.5B override rate under the plain condition. *Falsifier:* the 1.5B
override rate is at or above the 0.5B override rate under the plain condition.

**P4 - dose-response and popularity.** Emphatic assertion raises the override rate
above plain, and obscure items are overridden more than famous ones. *Falsifier:*
emphatic override rate not greater than plain, AND obscure not greater than famous.

## Commitment

P2 (a false premise in context silently overrides real parametric knowledge) and
P3 (the weaker model is more suggestible) are the headline. Results are reported
as-is, including any falsified prediction. The override rate is always conditioned
on control-correct to avoid the "never knew it" confound.
