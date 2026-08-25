---
title: Control Theory — The Real Direction (Analysis, Not Synthesis)
date: 2026-05-30
tags:
- thesis
- ephemeral-weights
- robust-control
aliases:
- Real Control Direction
- Analysis Not Synthesis
publish: true
description: I spent the class trying to synthesize a controller to stabilize ephemeral
  weights (LQR / H∞ reading ‖w_eph‖, choosing α). That collapsed — on a scalar plant
  the Riccati machinery reduces to proportional norm-regulation, which is adaptive
  …
---

> What control theory could *actually* do for ephemeral weights — as opposed to the controller-synthesis attempt that collapsed into adaptive regularization (Report Skeleton §8, verdict in thesis-staging). Written to mine for the proposal's optional/stretch contribution. Companion to [[linearizing-the-fast-weight-update|linearizing_fast_weight_update]].

## The one-sentence pivot

I spent the class trying to **synthesize a controller** to stabilize ephemeral weights (LQR / H∞ reading `‖w_eph‖`, choosing `α`). That collapsed — on a scalar plant the Riccati machinery reduces to proportional norm-regulation, which is adaptive regularization, and it lost to a loss-watching heuristic.

The real leverage of control theory here is the **other half of the field: analysis.** Don't *add* a controller to the loop. Use control-theoretic analysis to **certify and characterize** the dynamics that are already there — derive the corridor instead of sweeping for it, and prove *why* it's narrow.

Two modes of the field:
- **Synthesis** — design a controller (LQR, H∞, MPC). Needs a trustworthy plant model. Mine was fictional → brittle → ≈ regularization.
- **Analysis** — prove properties (stability, robustness, fundamental limits) of a *given* system. Needs no inserted controller. **This is where the unshoehorned value is.**

---

## Direction 1 — Small-gain → a *derived* corridor (the grounded win)

This is the one I can actually do with the theorems from the class, and it upgrades the linearization that failed in Report Skeleton §8.1.

### The runaway is a feedback loop

The instability isn't mysterious — it's positive feedback:

$$\|w_{\text{eph}}\| \;\xrightarrow[\text{curvature}]{}\; \|g_{\text{raw}}\| \;\xrightarrow[\alpha,\;\gamma_0]{}\; \|w_{\text{eph}}\|$$

Bigger ephemeral weights → bigger induced gradients → bigger weight updates → bigger weights. Whether it explodes is just whether the **loop gain exceeds 1**. That is *exactly* the small-gain theorem from the course, not a metaphor.

### Bounding the two legs

Write the update with decay (retention `ρ := 1 − γ₀`) and let `x := ‖w_eph‖`:

$$x(t+1) \;\le\; \rho\,x(t) \;+\; \rho\,\alpha\,\|g_{\text{raw}}(t)\|.$$

- **Update/decay leg**, gradient → next weight norm: gain `ρα`. *I control this* (α is the knob, γ₀ sets ρ).
- **Gradient leg**, weight norm → gradient norm: governed by the **local Lipschitz constant of the gradient map**, `L_∇` — i.e. how fast `‖∇L‖` grows as the weights grow. Morally the loss curvature / Hessian magnitude along the growth direction. *I do not control this*; it's a property of the loss landscape. (This is the same object as the "Hessian-like" `H` in [[linearizing-the-fast-weight-update|linearizing_fast_weight_update]].)

Locally, `‖g_raw‖ ≲ L_∇·x + c`. Substitute:

$$x(t+1) \;\lesssim\; \rho\,(1 + \alpha L_\nabla)\,x(t) \;+\; \rho\alpha c.$$

### The certified corridor

This is a contraction (bounded, stable) iff the loop gain is below 1:

$$\boxed{\;\rho\,(1 + \alpha L_\nabla) < 1 \quad\Longleftrightarrow\quad \alpha \;<\; \alpha_{\max} \;=\; \frac{1-\rho}{\rho\,L_\nabla} \;=\; \frac{\gamma_0}{(1-\gamma_0)\,L_\nabla}\;}$$

Two things to notice:

1. **It reproduces the linearized `|A|<1` condition exactly** (sub in `A = (1−γ₀)(1+α₀H)`, `H ↔ L_∇`) — but now as a *region* statement via a Lipschitz bound, not a tangent at one operating point. That's the part that **survives the bifurcation** that killed §8.1: a Lipschitz/sector bound gives you the cliff, where a local linearization only gave you the slope at one spot.
2. It's a **predictive design rule**, not a sweep. Measure `L_∇` along a trajectory, get `α_max` directly. The corridor stops being something you grope for by trial and error.

### The corridor is an interval, and that's the whole story

Memory needs `α` *large* (encode strongly enough to be read back) — call the floor `α_min(task)`, set by the task's signal-to-noise. Stability caps `α` from above at `α_max`. So:

$$\text{corridor} \;=\; \big[\,\alpha_{\min}(\text{task}),\;\; \tfrac{\gamma_0}{(1-\gamma_0)L_\nabla}\,\big],\qquad \text{non-empty iff } \alpha_{\min} < \alpha_{\max}.$$

You can only **widen** the corridor two ways:
- **Raise `γ₀`** (more decay) → bigger `α_max`. But more decay *shortens the memory horizon* (the whole point of the weights). Tradeoff, not a free win. ← this is the conservation law, see Direction 3.
- **Lower `L_∇`** (smoother / better-conditioned loss). You don't tune this directly — but **scale and conditioning change it.**

### Why this is the elegant part: it fuses the optional work with the *required* work

The proposal's required contribution is **upscaling**, and its open empirical question is *"does stability come more easily at larger scale?"* (proposal §4.1). The small-gain corridor answers exactly that:

> Stability-comes-easier-at-scale **iff** `L_∇` (local gradient Lipschitz / curvature) shrinks as the model grows.

That's a falsifiable prediction with a measurable quantity. So the control-theoretic analysis and the upscaling experiment **become the same investigation** — I measure `L_∇` across model sizes and check whether the corridor widens. The "optional/stretch" control work stops competing with the required scaling work and starts *explaining* it. This is the structural insight that makes the whole thesis cohere.

**Honest caveats (state these in the writeup):** NN losses aren't globally Lipschitz, so `L_∇` is a *local/empirical* bound measured along trajectories, not a global constant. `g_raw` is a DFA pseudo-gradient (§3.1), so `L_∇` is the Lipschitz constant of the *DFA* map, one more step removed from `∇²L`. The bound is sufficient, not tight — it'll be conservative. Do the derivation cleanly on a low-D surrogate; treat the full NN empirically.

---

## Direction 2 — IQC analysis (the recognized academic bridge; ambitious)

If I want the legitimate, citable framework where control theory meets optimization, it's **Integral Quadratic Constraints**:

> Lessard, Recht & Packard, *"Analysis and Design of Optimization Algorithms via Integral Quadratic Constraints,"* SIAM J. Optim. 26(1), 2016.

IQC is the **generalization of the small-gain theorem** I learned: instead of one scalar gain bound, you characterize the nonlinearity (here, the gradient map) by a *quadratic constraint* it satisfies (sector-bounded, co-coercive, slope-restricted), and prove stability / convergence rate of the optimizer-as-feedback-system **without linearizing at all.** It treats the gradient as a structured uncertainty block — which is precisely the right way to handle the thing linearization couldn't.

Why it's worth knowing about:
- It's the rigorous version of what I was groping toward, and it's *recognized* — reviewers know this lineage (Lessard, Hu & Lessard, Van Scoy et al.).
- **Nobody has applied it to fast-weight / plasticity dynamics.** My report's §2.2 literally flags this gap ("control-theoretic analysis of SGD"). That's a real, open research lane.
- It directly subsumes the small-gain corridor of Direction 1 as a special case, so #1 is the on-ramp to #2.

Scope honesty: this is probably the boundary between the master's and a first dissertation chapter. The standard IQC results assume convex / sector-bounded losses, which NN losses violate globally. The contribution would be *adapting* the framing (local sectors, region-of-attraction), not turning a crank. Read the 2016 paper first to see if it clicks before committing.

---

## Direction 3 — A fundamental-limit / conservation law (most "control theory", most honest)

Control theory's most beautiful results are **conservation laws** — Bode's sensitivity integral (the "waterbed": push sensitivity down at one frequency, it pops up at another) and Doyle's one-line *"There are none"* for LQG margins. The deepest honest claim about ephemeral weights has exactly this shape, and Direction 1 already exposes it:

> **Memory–stability conservation.** The decay `γ₀` is the only free knob that widens the stability corridor, but it is *also* what sets the memory horizon. Raising `γ₀` buys stability margin and spends it directly out of retention time. Stability margin and memory horizon trade off through a single conserved parameter — no causal controller reading `‖w_eph‖` can improve both at once.

Make it quantitative from Direction 1: the stability margin scales with `γ₀/(1−γ₀)`, while the memory horizon (decay time constant) scales like `1/γ₀`-ish (weight retained falls as `(1−γ₀)^t`). Increasing `γ₀` moves them in opposite directions. That's the waterbed, in this system, with closed-form edges.

This is the **reframe that converts my negative result into a positive one.** Not "I failed to stabilize it" but "I characterized *why* the corridor is intrinsically narrow and exactly what widens it (curvature/scale), as a conservation law." It also explains §8.3 rigorously: `‖w_eph‖` is a conflicted control variable *because* memory and stability pull on the same parameter. A fundamental-limit result is publishable, defensible, and far stronger than a controller that happens to work on one task.

---

## The one synthesis direction still worth keeping

**MPC** — but *only after* Direction 1 gives a trustworthy model. MPC's entire value over LQR/H∞ is that the cliff becomes a **hard constraint** ("predicted `x` stays below blow-up for the next N steps"), which a soft quadratic cost structurally cannot express (§8.1). But MPC needs a predictive model, and the fictional linearized plant was the weak link. So even the synthesis path routes through the analysis first. Park it as "future work, conditional on the model."

---

## Bits to actually lift into the proposal

For the **optional/stretch contribution** section — framed honestly, these are defensible and don't oversell:

1. **Reframe the stability investigation as analysis, not synthesis.** "We analyze the stability of the ephemeral-weight update as a feedback system rather than attempting to regulate it with a synthesized controller." One sentence; sets the right expectation and dodges the "this is just regularization" critique.
2. **The small-gain corridor `α_max = γ₀ / ((1−γ₀) L_∇)`** as the headline analytical result. Predictive, derived from course theory, ties to scale.
3. **The scale hypothesis, made falsifiable:** stability eases at scale *iff* `L_∇` shrinks with model size — measurable, and it *unifies* the optional analysis with the required upscaling experiment. Lead with this; it's what makes the thesis cohere.
4. **The memory–stability conservation law** as the framing of the contribution: a fundamental-limit result, not a failed controller. Cite Bode/Doyle as the genre.
5. **The grad-norm ratio early-warning observable** (from Report Skeleton §3.3: ratio shrinks in stable runs, grows from the start in runs that explode) — the right *output* to watch, an analysis byproduct worth one line.
6. **IQC + MPC as honest future work**, explicitly scoped beyond the master's, with the Lessard–Recht–Packard citation as the anchor for the "control-theoretic analysis of plasticity" framing.

What to **drop** from the prior framing: any claim that LQR/H∞/μ-synthesis *stabilized* the model, and the three-way controller comparison as a positive result (it's a negative result — keep it as motivation for the analysis pivot, per thesis-staging).

---

## First step when ready

Read **Lessard–Recht–Packard (2016)** — one sitting tells me whether the IQC framing clicks and gives the citation backbone. Everything in Direction 1 I can derive myself from the existing `|A|<1` condition in an afternoon (it's done above — just needs `L_∇` measured on a real trace to make it concrete).
