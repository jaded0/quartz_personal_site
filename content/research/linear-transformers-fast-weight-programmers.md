---
title: Linear transformers are secretly fast weight programmers (notes)
date: 2026-08-28
tags:
- ephemeral-weights
- thesis
- fast-weights
publish: true
description: 'Schlag, Irie & Schmidhuber, ICML 2021 — arXiv 2102.11174v3. #1 on memory-architectures-reading-list,
  carried on the daily list since 2026-08-21. Audio guide at papers/FastWeightProgrammers_Audio_Guide.md.'
---

Schlag, Irie & Schmidhuber, ICML 2021 — arXiv 2102.11174v3. #1 on [[memory-architectures-reading-list|memory-architectures-reading-list]], carried on the daily list since 2026-08-21. Audio guide at `papers/FastWeightProgrammers_Audio_Guide.md`.

The title is literal. Move the parentheses in softmax-free attention and the growing KV cache collapses into a fixed-size matrix accumulating outer products of values with keys. That's a weight matrix being written and read at inference time — the same equations as Schmidhuber's 1991 fast weight programmer, up to a normalization term. Two literatures, thirty years apart, same object.

What makes it a paper rather than a historical note: the reframing makes three questions askable that are invisible from the attention side. *How much fits? Can it edit? What other instructions could there be?* Attention's answers are "everything," "doesn't need to," and "n/a" — so nobody asks.

## the answer to my standing question

Whole layer, and not close. The fast weight matrix is a full d-by-d matrix per head per layer that *replaces* attention, written by a designed forward-pass rule. Mine is a fraction of ordinary weights, scattered, written by the backward pass. Not the same mechanism.

The third branch I kept leaving open — "or equivalent and my code is inefficient" — is dead. Their write is rank-one, in a chosen subspace, one per token. Mine is whatever the task-loss gradient delivers. Closing that question.

**The bigger difference is who writes.** An FWP has two networks and a hand-designed instruction set; the slow net programs the fast net and only *when/how hard* is learned. Ephemeral weights have no programmer at all — the write signal is the task-loss gradient, so the fast-weight rule and the slow-weight rule are the same rule at different rates. That's the unification I said I wanted in [[do-language-models-need-sleep|Language models sleep]].

And the sharp version, which belongs in related work: **the delta rule is itself a gradient step.** Differentiate the squared error between target value and what the memory currently returns for that key, w.r.t. the memory matrix, and you get exactly their update with β as the learning rate. So DeltaNet's fast weights are *already* gradient-written. The difference isn't gradient-vs-not — it's *which loss*. They descend a local auxiliary reconstruction objective a researcher wrote down; I descend the actual task loss. That's a cleaner and more defensible positioning than "we don't add the complexity of an outer loop," which is what the proposal currently says — and which is anyway **wrong for this paper**: there's no outer loop here, fast weights are activations in the graph, ~5% throughput cost. Fix that paragraph.

## capacity — corridor stability questions Q6

Capacity = dimension of the key space, because that's how many orthogonal directions exist. Past it, interference is forced by geometry, not by undertraining. Grounded in Smolensky's TPRs (roles=keys, fillers=values), and the synthetic experiment breaks at 60 when the predicted bound is 64.

Two moves, cleanly separated: **expand the space** (DPFP — deterministic, parameter-free, projects up; the real version of what I was guessing at with Cyclic Plasticity Values) or **write more cheaply** (delta rule). The delta rule doesn't raise the ceiling, it stops you wasting the room — re-writing a fact you already hold costs *nothing*, because the error term is zero. Under the sum rule it costs full capacity every time.

Caveat I should not paper over: the counting argument needs a memory that is a sum of rank-one writes in a known space. Mine isn't. Can't import the number. **Can** import the reframing, which is worth more — "how much fits?" becomes "how many near-orthogonal directions does my write mechanism reach, and how much does each write consume?" Both measurable. See Hebbian Learning, and yes — for the outer-product case it basically *is* a Hopfield network, they say so themselves.

## the stability derivation (mine, not theirs)

Substitute the retrieved value back into the delta update and collect:

> W_i = W_{i-1}(I − β φφᵀ) + β v φᵀ

Linear time-varying system. Transition operator is identity minus β times a rank-one projector — eigenvalue (1 − β‖φ‖²) along the written direction, exactly 1 in every orthogonal direction. **Each write is a contraction along what it touches and identity everywhere else.** The sum rule's transition is the identity in all directions: pure integrator, every pole at 1, guaranteed blowup under persistent excitation. Which is exactly the untruncated result — perplexity >260 vs 29.4, same params, same state size.

Non-expansiveness needs β‖φ‖² ≤ 2; a clean contraction with no sign flip needs ≤ 1. β is a sigmoid so ≤1 already, which puts the binding requirement on the other factor — and **sum normalization forces ‖φ‖₂ ≤ 1**, since φ is non-negative and its components are made to sum to one. That's *why* they report the models diverged without sum normalization — they state it as an experimental finding and never explain it. It's not numerical hygiene, it's the condition that keeps the write non-expansive.

**This is the transferable thing for the corridor.** Q1–Q4 ask why the gradient explodes, in what conditions, what the loop is, and how it stabilizes at all. Here's the same phenomenon in a system simple enough to solve in closed form, and the stability condition turns out to be a *norm bound on the write direction*. Hypothesis to actually measure: **is the corridor the region where the effective per-step write operator on the ephemeral weights is non-expansive?** That's mechanistic in the way the committee asked for, and far better than "somewhat linear relationship between stable fast and slow weights."

Loose joint, stated honestly: my writes aren't rank-one projectors, so the closed-form eigenvalue argument doesn't transfer — I'd be measuring the operator norm empirically. Cheap, and a natural companion to the noise-injection experiment.

It also **reframes the failed stabilization work** (fix the exploding gradients, regularization, clipping, hebbian homeostasis). All three shrink write *magnitude* globally, which is why they all blocked short-term encoding. The delta rule leaves magnitude alone and changes *direction* — writes the error instead of the value, so it's self-limiting without being globally damped. Genuinely different knob from anything on my tried-and-failed list.

## encoding vs retrieval — Q5

The delta rule makes the write *depend on a read* — query with the key you're about to write to, then store the difference. Read-modify-write, not blind superposition. Strictly more expressive than pure associative memory, which is the direction Brainstorm associative memory and palindromes was pointing.

Interesting and against my guess: they find **positional encoding isn't needed** for the Delta Net. Suggests order lives in the sequential structure of the writes rather than in a positional tag on the keys. Probe: if my mechanism handles some order-sensitive tasks and fails palindromes, is order in the writes or does it need to be in the keys?

## estimation theory

The delta rule is Widrow–Hoff LMS verbatim. RLS updates by the innovation shaped by a Riccati-propagated gain *matrix*; the delta rule throws that away and substitutes a learned *scalar* β. And Gated DeltaNet's 2024 improvement — the decay term — is exactly the forgetting factor from fading-memory RLS. **So the 2024 advance over this paper is putting back one of the two things classical RLS already had. The propagated gain matrix is still missing.** That's an open direction and it's mine to notice.

## lineage — it shipped

Worth recording because it's the same shape as the Mamba story. Their "Delta Network" → **DeltaNet** (Yang, Wang, Zhang, Shen, Kim, arXiv 2406.06484, NeurIPS 2024 — parallelizes the delta rule over sequence length via Householder products; 1.3B beats Mamba and GLA) → **Gated DeltaNet** (Yang, Kautz, Hatamizadeh, arXiv 2412.06464, ICLR 2025 — gating for wholesale erasure *plus* delta for targeted edits; they're complementary) → **Qwen3-Next** (3:1 hybrid, mostly Gated DeltaNet), **Qwen3.5** (Feb 2026), **Kimi Linear** (channel-wise instead of per-head decay gates).

Dormant 1991 → 2021 identification → 2024 made trainable → 2026 default linear-attention layer in frontier open-weight models.

## todo out of this

- [ ] add arXiv 2102.11174 to `ieee_ephemeral_weights.bib` — the proposal cites Irie et al. 2021 (the follow-up) for a claim that is *this* paper's
- [ ] rewrite the FWP related-work paragraph: drop the outer/inner-loop efficiency claim, replace with the which-loss framing
- [ ] measure the effective write operator norm inside vs outside the corridor

## Backlinks

- 2026-08-28
