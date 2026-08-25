---
title: Ephemeral Weights as Optimizer-State-Made-Visible (paper reframe)
date: 2026-04-07
tags:
- ephemeral-weights
- paper-ideas
- optimizer
- research
publish: true
description: Reframe idea for a future rewrite of the ephemeral weights paper. The
  current framing presents eqs. (6)–(7) as a novel memory mechanism. They aren't —
  they're SGD with per-parameter LR and selective weight decay. Leaning into that
  honestly…
---

Reframe idea for a future rewrite of the ephemeral weights paper. The current framing presents eqs. (6)–(7) as a novel memory mechanism. They aren't — they're SGD with per-parameter LR and selective weight decay. Leaning into that honestly would make the contribution *sharper*, not weaker.

## The mechanical equivalence

- Eq. (6) $w_k(t+1) = w_k(t) - \alpha_k \nabla_k L(t)$ → per-parameter SGD
- Eq. (7) $w^{\text{fast}} \leftarrow \gamma w^{\text{fast}}$ → weight decay with rate $(1-\gamma)$ on the high-plast subset
- 10% sparse designation → a mask in optimizer state

Every piece of this maps directly onto `torch.optim.SGD` with two `param_groups`.

## The sharper observation: fast weights *are* a momentum buffer

Unroll $w_{t+1} = \gamma(w_t - \alpha g_t)$:

$$w_t = -\alpha \sum_{k=0}^{t-1} \gamma^{t-k} g_k$$

An exponential moving average of gradients with decay $\gamma$. Substitute $v = -w/\alpha$ and you get $v_{t+1} = \gamma v_t + \gamma g_t$ — literally SGD momentum with $\beta = \gamma$.

So the fast weights in this paper are a momentum buffer. The *only* thing that makes them "memory" and not "optimization state" is **who reads them**. Standard SGD+momentum: buffer $v$ is invisible to the forward pass, only influences the next $w$ update. Ephemeral weights: the buffer *is* $w$, so the forward pass sees it directly.

That's the whole trick — and it's a plumbing trick, not an algorithmic one: route the optimizer's gradient-history state into the forward pass.

## Reframed contribution claim

> We do not propose a new update rule. We observe that any optimizer maintaining gradient-history state (momentum, Adam's $m,v$) already implements a compressed, decaying record of recent inputs. By storing that state in the weight tensor itself — so the forward pass reads it directly — we obtain working memory as a byproduct of standard optimization, unifying training-time and inference-time dynamics under a single mechanism.

This is a **unification claim**, not an **invention claim**: optimizer state and working memory are the same object under the right plumbing.

## Why this reframe is better

- **Honest about what's new.** The contribution is plumbing + interpretation, not algorithm. Presenting it that way is both truer and more defensible.
- **Eliminates tension** between §3.3's "novel mechanism" language and the fact that eqs. (6)–(7) are stock SGD.
- **Makes the §4.2 gradient explosion observation follow naturally** — of course it explodes; we're running an optimizer with LR $10^5$ and reading the parameter mid-flight, so the forward pass is always looking at a diverging iterate.
- **Makes §4.1 dual-timescale result sharper.** What's being shown is that a single optimizer with two LR regimes produces two dynamical behaviors that can be read as "learning" vs "remembering" depending on the timescale.
- **Matches a cleaner code architecture.** If the thesis is "this is an optimizer interpreted as memory," the natural implementation IS a custom `Optimizer` subclass (plus per-sample state and the DFA coupling). Current code embeds update logic inside `HebbianLinear`, which actively obscures the claim.

## What the optimizer framing can't absorb (residual real contributions)

These are the legitimate non-algorithmic contributions that survive the reframe:

1. **Per-sample fast weights** (`candidate_weights` of shape `[B, out, in]`). Each sequence has its own isolated momentum buffer. Harness requirement, not an optimizer rule, but real.
2. **DFA as the gradient source.** Required because backprop through volatile high-magnitude weights explodes. Coupled design choice — can't just drop in arbitrary optimizers.
3. **Inference-time execution.** Dynamic evaluation (Krause 2018) already runs SGD at inference, so not new on its own, but (1)+(2)+(3) as a combined package is.
4. **Sparse 10% designation.** Structural choice — which parameters are "memory cells" vs "knowledge cells." Scaffolding for where the optimizer gets to act loudly.

## Related positioning

- Hinton 1987, Schmidhuber 1992, Ba 2016, Miconi differentiable plasticity — all variants of "fast weights" that *also* hide the optimizer structure behind custom mechanisms. The reframe would explicitly name what they and this paper share: an optimizer with state exposed to the forward pass.
- Clark et al. 2022 FWL — emulates gradient updates via an attention module. Our reframe: they're using an attention module to approximate what a plain optimizer already computes for free.

## TODO (someday)

- Actually rewrite §3 with the optimizer framing
- Refactor the code so the update rule lives in a custom `Optimizer` subclass, matching the reframed theory
- Check whether there's a clean way to present the momentum equivalence as a lemma early in §3
