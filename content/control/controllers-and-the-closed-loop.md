---
title: Controllers and the closed loop
publish: true
description: Taking the scalar plant from the linearization and building the three
  controllers on top of it — LQR, H-infinity, and a model-free adaptive heuristic
  — then closing the loop.
---

## Where we left off

[[linearizing-the-fast-weight-update|linearizing_fast_weight_update]] got us to the plant:

$$\delta x(t+1) = A\,\delta x(t) + B\,\delta u(t) + E\,\delta d(t)$$

One scalar state ($x = \|w_{\text{eph}}\|$), one control input ($\alpha$), one disturbance ($g_{\text{raw}}$), three coefficients ($A$, $B$, $E$). The rest of §6 is: figure out $A$ from data, then design a controller that picks $\delta u$ at every step to keep $x$ near $\bar x$.

This note covers §6.2 (system identification), §6.3 (the three controllers), and §6.4 (how the closed loop actually runs). The goal is to build up each controller from first principles so the logic is followable even without a controls background.

---

## §6.2 — Gray-box system identification

### The problem

We have the plant structure from §6.1:

$$A = (1-\gamma_0)(1 + \alpha_0 H), \qquad B = (1-\gamma_0)\bar g, \qquad E = (1-\gamma_0)\alpha_0$$

$B$ and $E$ are **known** the instant we know $\gamma_0$, $\alpha_0$, and $\bar g$ — they're just plug-in from the formulas. The only unknown is $H$, the effective Hessian-like coupling buried inside $A$. That one number encodes "how much does the gradient norm grow when the weight norm grows by a little?" — the curvature of the loss landscape along the direction that matters.

So the entire identification problem is: **estimate one scalar $H$ from data**.

### What "gray-box" means

"Gray-box" sits between two extremes:

| Approach | What's assumed | What's fit from data |
| --- | --- | --- |
| **White-box** | Everything — full analytical model, no fitting | Nothing |
| **Gray-box** (what we do) | The structure of $A$, $B$, $E$ (from the physics) | One parameter ($H$, or equivalently $A$ itself) |
| **Black-box** | Nothing — just "some linear model exists" | All three parameters ($A$, $B$, $E$) independently |

The gray-box approach is powerful here because committing to the physics-derived structure means we only have a 1-D regression problem, which is far more robust to noise and short traces than fitting all three at once.

### The procedure (as implemented in `plant_model.py`)

**Step 1 — Record a sysid trace.** Run training with $\alpha$ **varied** (swept linearly, stepped, anything non-constant). You need $\alpha$ to move around, otherwise the control channel has no excitation and you can't tell what $B$ is doing empirically. Log five columns at every step: `x` ($\|w_{\text{eph}}\|$), `g_raw`, `alpha`, `gamma`, `loss`.

**Step 2 — Compute the operating point.** Column means:

$$\bar x = \text{mean}(x), \qquad \alpha_0 = \text{mean}(\alpha), \qquad \bar g = \text{mean}(g_{\text{raw}})$$

**Step 3 — Compute deviations.**

$$\delta x(t) = x(t) - \bar x, \qquad \delta u(t) = \alpha(t) - \alpha_0, \qquad \delta d(t) = g_{\text{raw}}(t) - \bar g$$

**Step 4 — Compute $B$ and $E$ analytically.** No fitting:

$$B = (1-\gamma_0)\,\bar g, \qquad E = (1-\gamma_0)\,\alpha_0$$

**Step 5 — Isolate the $A\,\delta x$ term and fit $A$ by least squares.**

The plant equation says $\delta x(t+1) = A\,\delta x(t) + B\,\delta u(t) + E\,\delta d(t)$. We know $B$, $E$, $\delta u$, $\delta d$, $\delta x$ at every step. Subtract the known stuff from both sides:

$$\underbrace{\delta x(t+1) - B\,\delta u(t) - E\,\delta d(t)}_{\text{residual } r(t)} = A \cdot \delta x(t)$$

This is a 1-D linear regression: $r = A \cdot \delta x$. Solve by ordinary least squares:

$$\hat A = \frac{\sum_t r(t)\,\delta x(t)}{\sum_t \delta x(t)^2}$$

One number. That's the entire identification.

**Step 6 — Sanity check.** Also run an unconstrained 3-parameter OLS (`estimate_plant_unconstrained`) fitting $A$, $B$, $E$ all at once with no structural assumption. If the gray-box $A$ roughly agrees with the black-box $A$, and the black-box $B$, $E$ are close to the analytical values, the structural model is consistent. If they wildly disagree, the linearization itself is suspect.

> [!info] Why the sanity check matters
> If the unconstrained fit gives, say, $B_{\text{free}} \approx 0.8 \cdot B_{\text{analytical}}$, that's fine — the structural assumption is approximately right and the constraint helped by reducing variance. But if $B_{\text{free}}$ has the *wrong sign* compared to $B_{\text{analytical}}$, the structure is wrong and the analytical formulas don't describe this operating regime. This is your early-warning system for "the linearization is a fiction here."

### Once you have $A$: the one-second verdict

$$|A| < 1 \implies \text{stable open-loop. No controller needed.}$$
$$|A| > 1 \implies \text{unstable open-loop. The runaway is real. §6.3 is justified.}$$

$H$ can be recovered from $A$ if you want the physical interpretation:

$$H = \frac{A/(1-\gamma_0) - 1}{\alpha_0}$$

A large positive $H$ means the loss landscape is curving in a way that amplifies weight growth — the gradient *grows* when the weights grow, creating the positive feedback loop that makes the system blow up.

---

## §6.3 — The three controllers

### First: what is a controller even doing?

Before diving into specific algorithms, let's be very concrete about what the controller's job is at every training step.

The system has a **target weight norm** $\bar x$ (the operating-point value from sysid). At each step, the controller:

1. **Reads** the current $\|w_{\text{eph}}\|$ from the live network.
2. **Computes** a deviation: $\delta x = \|w_{\text{eph}}\| - \bar x$.
3. **Picks** a control action $\delta u$ (how much to adjust $\alpha$ away from $\alpha_0$).
4. **Sets** the new plasticity: $\alpha = \alpha_0 + \delta u$.
5. The network then uses that $\alpha$ for its next weight update.

That's it. Every controller in this paper is a different *rule* for step 3 — a different answer to "given how far I am from the target, what should $\alpha$ be?"

The simplest possible rule: proportional feedback. If the weight norm is too high ($\delta x > 0$), reduce $\alpha$ so the next gradient step is smaller, slowing the growth. If the weight norm is too low ($\delta x < 0$), increase $\alpha$ so the gradient step is bigger, pushing back toward the target. In equation form:

$$\delta u = -K \cdot \delta x$$

where $K > 0$ is a **gain**. This is exactly what all three model-based controllers compute — they just differ in *how they choose $K$*.

> [!tip] Why negative feedback?
> The minus sign is the fundamental idea of feedback control. If $\delta x$ is positive (weight norm above target), $\delta u$ becomes negative (reduce $\alpha$), which slows growth and pushes $x$ back toward the target. Without the minus sign, you'd have *positive* feedback — deviations would amplify instead of correct. The entire point of the controller is to turn the open-loop positive feedback (the runaway, caused by $A > 1$) into closed-loop negative feedback ($|A - BK| < 1$).

---

### §6.3.1 — LQR (Linear Quadratic Regulator)

#### The intuition

LQR answers the question: **"What gain $K$ minimizes a weighted sum of state deviation and control effort over the infinite horizon?"**

You want $\delta x$ to be small (stay near the target) but you also want $\delta u$ to be small (don't swing $\alpha$ wildly). These goals conflict — aggressive correction reduces $\delta x$ faster but costs more $\delta u$, and vice versa. LQR finds the optimal tradeoff.

#### Building it from scratch

Define a cost function that penalizes both state deviation and control effort, summed over all future time steps:

$$J = \sum_{t=0}^{\infty} \Big[\underbrace{Q \cdot \delta x(t)^2}_{\text{cost of being off-target}} + \underbrace{R \cdot \delta u(t)^2}_{\text{cost of moving } \alpha}\Big]$$

- **$Q$** is how much you care about staying at the target weight norm. Large $Q$ means "deviations are expensive; correct aggressively."
- **$R$** is how much you care about not moving $\alpha$ too much. Large $R$ means "control effort is expensive; be gentle."

The ratio $Q/R$ is what really matters. In our code: $Q = 1$, $R = 10^{-3}$, so $Q/R = 1000$. We care a *lot* about keeping the weight norm on target and relatively little about how hard we push $\alpha$.

Now, under the constraint that the plant evolves as $\delta x(t+1) = A\,\delta x(t) + B\,\delta u(t)$, what $\delta u(t)$ at each step minimizes $J$?

The answer (this is the core LQR result from optimal control theory) is that the optimal policy is **linear state feedback**:

$$\delta u(t) = -K \cdot \delta x(t)$$

where $K$ is computed from the solution of the **Discrete Algebraic Riccati Equation** (DARE):

$$P = A^T P A - A^T P B (R + B^T P B)^{-1} B^T P A + Q$$

For our scalar system, all the matrices are just numbers, so the transposes disappear:

$$P = A^2 P - \frac{A^2 P^2 B^2}{R + B^2 P} + Q$$

Solve for $P$ (a single positive number), then the gain is:

$$K = \frac{B \cdot A \cdot P}{R + B^2 P}$$

#### What the DARE is actually doing (intuition)

$P$ is the **cost-to-go**: if you're at deviation $\delta x$ right now and you play the optimal policy forever, the total future cost is $P \cdot \delta x^2$. The Riccati equation is a self-consistency condition: the cost-to-go right now has to equal (the immediate cost) + (the discounted cost-to-go one step later, under the optimal policy). It's dynamic programming compressed into one equation.

You don't need to understand the derivation to use it — `scipy.linalg.solve_discrete_are` handles the solve. But what matters is:

- $P$ depends on $A$, $B$, $Q$, $R$.
- $K$ then depends on $P$.
- The resulting **closed-loop dynamics** are $\delta x(t+1) = (A - BK)\,\delta x(t)$.

The magic of LQR is that $|A - BK| < 1$ is *guaranteed* whenever the plant is stabilizable (i.e., $B \neq 0$ — we can actually influence the state). So if the open-loop $A = 1.3$ (unstable), LQR finds a $K$ such that $A - BK = 0.7$ (stable, with some specific rate of convergence back to the target).

#### What LQR ignores

Look at the cost function again:

$$J = \sum_{t=0}^{\infty} \Big[Q \cdot \delta x(t)^2 + R \cdot \delta u(t)^2\Big]$$

There's no $\delta d$ anywhere. LQR has **no concept of the disturbance**. It doesn't know $E$ exists, it doesn't know gradient fluctuations are buffeting the system. It designs the gain assuming the only thing affecting $\delta x$ is the controller itself.

In practice, the gradient disturbance $E\,\delta d$ acts like noise on the state. LQR happens to be reasonably robust to small noise (a well-known folk result), but it's not *optimizing* for disturbance rejection. If the disturbance is large relative to the state, LQR will underperform because it designed $K$ for a world that doesn't exist.

> [!info] Why not just pick $K$ by hand?
> You could. If you set $K = (A - 0.5)/B$ then the closed-loop eigenvalue is exactly $0.5$ and the system converges at a specific rate. But that requires knowing $A$ and $B$ and choosing a target eigenvalue — and the tradeoff between convergence speed and control effort is implicit, not principled. LQR automates this: you state your preferences ($Q$ and $R$) and it returns the $K$ that optimally trades them off. For a scalar system this barely matters; for higher-dimensional systems (like the 2D variant with state $[\|w_{\text{eph}}\|, \|g\|]$), LQR handles multi-input multi-output tradeoffs that would be painful to tune by hand.

#### In the code (`controllers.py:39–79`)

```python
# Solve the DARE — scipy does the heavy lifting
P = solve_discrete_are(A_mat, B_mat, Q_mat, R_mat)

# Compute gain from P
K = (B * P * A) / (R + B * P * B)

# At runtime: u = -K * (x - x_ref), then alpha = alpha0 + u
```

That's the whole controller. Solve one equation offline. Apply one multiplication online. The elegance is the point.

---

### §6.3.2 — $H_\infty$ (robust control)

#### The motivating question

LQR answers "what $K$ minimizes the average cost?" $H_\infty$ answers a different question: **"What $K$ minimizes the worst-case effect of the disturbance on the state?"**

This is the reason $E$ got its own letter in §6.1. LQR doesn't need a disturbance channel — it optimizes for a world without disturbances. $H_\infty$ is built specifically to deal with a named adversary ($\delta d$) entering through a specific channel ($E$).

#### The game-theoretic framing

$H_\infty$ is often described as a **minimax game** between two players:

- **The controller** (you) picks $\delta u$ to minimize the "performance output" (a weighted combination of state error and control effort, just like LQR).
- **The adversary** (nature) picks $\delta d$ to *maximize* the same performance output.

The controller is trying to keep the state on target *no matter what the disturbance does*. The adversary is trying to knock it off *despite the controller's best efforts*. $H_\infty$ finds the Nash equilibrium of this game.

The performance output is measured by a ratio:

$$\gamma = \sup_{\delta d \neq 0} \frac{\|\text{performance output}\|}{\|\delta d\|}$$

$\gamma$ is the **worst-case gain** from disturbance to performance. Think of it as: "in the worst case, how many units of state error do I get per unit of disturbance?" A smaller $\gamma$ means the controller is better at rejecting disturbances.

The $H_\infty$ design problem: **find the smallest $\gamma$ for which a stabilizing $K$ exists**.

> [!warning] $\gamma$ here is NOT the forgetting rate
> The paper uses $\gamma$ (no subscript) for the $H_\infty$ attenuation level and $\gamma_0$ for the forgetting rate. They're completely different quantities. The notation table in §5 flags this, but it's easy to trip on.

#### The modified Riccati equation

Just like LQR has its Riccati equation, $H_\infty$ has a modified version. For our scalar system:

$$P = \frac{A^2 P}{1 + P\left(\frac{B^2}{R} - \frac{E^2}{\gamma^2}\right)} + Q$$

Compare this to the LQR Riccati:

$$P = \frac{A^2 P}{1 + \frac{B^2 P}{R}} + Q$$

The only difference is the term $-E^2/\gamma^2$ in the denominator. Let's unpack what that does:

- The $B^2/R$ term captures "how much can the controller help?" (control authority divided by control cost).
- The $-E^2/\gamma^2$ term captures "how much can the adversary hurt?" (disturbance authority divided by the budget we're allowing it).
- The denominator is $1 + P \cdot (\text{help} - \text{hurt})$.

When $\gamma$ is large (we're being generous with the disturbance budget), $E^2/\gamma^2 \approx 0$ and the equation reduces to the LQR Riccati. When $\gamma$ is small (we're being strict — demanding robustness to large disturbances), the $-E^2/\gamma^2$ term grows and **can make the denominator go to zero or negative**, at which point no solution exists. This is the fundamental tradeoff: there's a floor $\gamma_{\min}$ below which no controller can guarantee performance.

#### The bisection procedure

The code finds $\gamma_{\min}$ by bisection:

1. Start with a range $[\gamma_{\text{lb}}, \gamma_{\text{ub}}]$.
2. Try $\gamma_{\text{mid}}$. Iterate the Riccati to convergence.
3. If a positive $P$ exists and the closed loop is stable: $\gamma_{\text{mid}}$ is achievable. Move the upper bound down.
4. If $P$ diverges or goes negative: $\gamma_{\text{mid}}$ is too ambitious. Move the lower bound up.
5. Repeat until $\gamma_{\text{ub}} - \gamma_{\text{lb}} < \varepsilon$.

The result is $\gamma_{\text{opt}}$ (the smallest achievable worst-case gain) and the corresponding $P$ and $K$.

#### What makes $H_\infty$ more conservative than LQR

LQR optimizes for the *average-case* cost. $H_\infty$ optimizes for the *worst-case* disturbance. In practice, the worst case that $H_\infty$ prepares for may never actually happen — the gradient disturbance is typically well-behaved, not adversarial. So $H_\infty$ "spends" some of its control authority hedging against scenarios that don't occur, leaving less authority for normal operation.

Concretely: $H_\infty$ tends to produce a **smaller $K$** than LQR (more cautious feedback), because it's reserving headroom for a disturbance attack. The system converges more slowly in the typical case, but it won't be knocked off track as easily in the worst case.

> [!note] When would $H_\infty$ clearly beat LQR?
> If the gradient disturbance has heavy tails — occasional huge spikes in $g_{\text{raw}}$ — then LQR's gain might be too aggressive during those spikes (it wasn't designed for them), while $H_\infty$ was explicitly designed to survive them. In our experiments, the gradient disturbance turned out to be relatively mild compared to the *model mismatch* (the linearization being wrong), so $H_\infty$'s conservatism didn't buy much. The disturbance it was hedging against wasn't the thing that actually broke the system.

#### The gain formula (previously bugged, now fixed)

After the bisection finds $\gamma_{\text{opt}}$ and the corresponding $P$, the code originally computed the gain using the LQR formula. This was wrong — it used the $P$ from the $H_\infty$ Riccati but the $K$ formula from LQR, making the disturbance channel $E$ invisible to the final gain.

The correct $H_\infty$ gain for the scalar case, derived from the saddle-point conditions of the minimax game $\min_u \max_d \sum [Qx^2 + Ru^2 - \gamma^2 d^2]$, is:

$$K_{H_\infty} = \frac{\gamma^2 \cdot B \cdot A \cdot P}{\gamma^2(R + B^2 P) - R \cdot E^2 \cdot P}$$

When $E = 0$ or $\gamma \to \infty$, this reduces to the LQR formula $K = BAP/(R+B^2P)$. The denominator can go to zero when $\gamma$ is small and $E$ is large — that's the regime where no controller can guarantee performance, and is exactly the boundary the bisection is searching for.

The fix was applied to both `_solve_hinf_riccati` (stability check during bisection) and `_solve_hinf` (final gain computation). Verified: with $E=0.3$, H-inf gives $K=4.60$ vs LQR $K=2.59$; with $E=0$, both match.

---

### §6.3.3 — Adaptive controller (the model-free one)

#### A completely different philosophy

LQR and $H_\infty$ are **model-based**: they take the plant ($A$, $B$, $E$) as input and compute $K$ offline. The adaptive controller is **model-free**: it has never heard of the plant. It doesn't know $A$, doesn't know $B$, doesn't know $E$, doesn't know $H$. It just watches the loss and reacts.

This is the "I don't trust your linearization" controller.

#### The logic

The adaptive controller operates on the **loss**, not the weight norm. Its policy is a simple set of rules:

1. Track loss in a sliding window of the last $N$ steps (default $N = 20$).
2. Compute the mean loss over that window.
3. Apply one of three actions:

| Condition | Action | Rationale |
| --- | --- | --- |
| Mean loss $> 2 \times$ target | $\alpha \leftarrow 0.5 \cdot \alpha$ | Emergency: halve plasticity immediately |
| Mean loss $>$ target | $\alpha \leftarrow 0.9 \cdot \alpha$ | Gentle reduction: back off |
| Mean loss $\leq$ target and trending down | $\alpha \leftarrow 1.02 \cdot \alpha$ | Safe to push: nudge plasticity up |

That's the entire controller. No Riccati equation, no optimization, no plant model.

#### Why it works (and when it doesn't)

**Why it works:** The runaway manifests as loss explosion. Long before the linearization breaks down or $A$ drifts, the loss starts climbing. The adaptive controller catches this early and backs off $\alpha$. It's reactive rather than predictive — it doesn't know *why* the system is going unstable, but it doesn't need to. It just sees the symptom (rising loss) and applies the treatment (reduce plasticity).

**Why it's the widest-operating-range controller:** LQR and $H_\infty$ are tuned for the neighborhood of one operating point. When the trajectory leaves that neighborhood, their $K$ is based on the wrong $A$ and can make things worse. The adaptive controller has no operating point — it's always responding to what's actually happening. It can't be "out of regime" because it has no regime.

**The cost:** It's purely reactive. It can't *prevent* instability — it can only *respond* to it after the loss has already started rising. There's a lag: the sliding window needs to fill up before the mean shifts. And because it's heuristic, there's no optimality guarantee — the gain is hardcoded, not derived from any cost function. It also has **no concept of the weight norm at all** — it reads loss, not $\|w_{\text{eph}}\|$. So it can't keep the weight norm in a specific corridor; it can only keep the loss near a target.

> [!info] The adaptive controller's input is different
> This is easy to miss: LQR and $H_\infty$ call `compute_alpha(x)` where `x` is the weight norm. The adaptive controller calls `compute_alpha(loss_val)` — it receives the **loss**, not the state. The dispatch happens in `hebby_integration.py:84`:
>
> ```python
> if isinstance(controller, AdaptiveController):
>     new_alpha = controller.compute_alpha(loss_val)
> else:
>     new_alpha = controller.compute_alpha(x)
> ```
>
> This means the adaptive controller is solving a fundamentally different problem: regulating loss (what we actually care about) rather than regulating weight norm (a proxy for what we care about). This is both its strength (it optimizes what matters) and its weakness (it has no predictive model of how its actions affect the future).

---

## §6.4 — The closed loop

### How it runs

The closed-loop integration (`hebby_integration.py`) connects the controller to the live training loop. At every character step — every single character the RNN processes — the following happens:

```
┌────────────────────────────────────────────────────────────┐
│  For each character in the training sequence:              │
│                                                            │
│  1. Forward pass + DFA backward pass (compute gradients)   │
│  2. Read ‖w_eph‖ from the live network                     │
│  3. Read loss from the current step                        │
│  4. Pass (‖w_eph‖ or loss) to the controller               │
│  5. Controller returns new α                               │
│  6. Set α for the next step's gradient update              │
│  7. Log: step, x, g_raw, alpha, gamma, loss, accuracy     │
│                                                            │
│  Repeat.                                                   │
└────────────────────────────────────────────────────────────┘
```

The control update rate is **one per character**. This is fast — matching the rate at which the ephemeral weights themselves change. The controller doesn't wait for an epoch boundary or a batch; it reacts at the finest timescale the system offers.

### Where $\alpha$ actually gets applied

`update_plasticity` (`hebby_integration.py:109`) takes the controller's output and writes it into the live network:

```python
module.plasticity.data[module.mask] = new_alpha
```

`module.mask` selects the ephemeral weights (the volatile ~10% of parameters). `module.plasticity` is the per-weight learning rate tensor. So the controller's scalar output becomes the uniform plasticity for all ephemeral weights in each `HebbianLinear` layer (excluding the last layer, which is left alone).

### The init pipeline

When a training run starts, `init_controller` reads command-line args to decide which controller to instantiate:

- `mode = "fixed"` → `FixedController` (baseline, constant $\alpha$)
- `mode = "lqr"` → loads sysid results from a JSON file, extracts $A$, $B$, $Q$, $R$, builds `LQRController`
- `mode = "hinf"` → same sysid results, also extracts $E$, builds `HinfController`
- `mode = "adaptive"` → `AdaptiveController` (no sysid needed)

LQR and $H_\infty$ **require a pre-existing sysid JSON** (from a prior identification run). If the file doesn't exist, the system falls back to fixed $\alpha$ with a warning. The adaptive controller needs nothing.

---

## Summary: three strategies for one problem

| | **LQR** | **$H_\infty$** | **Adaptive** |
| --- | --- | --- | --- |
| **What it reads** | $\|w_{\text{eph}}\|$ | $\|w_{\text{eph}}\|$ | loss |
| **What it knows** | $A$, $B$ | $A$, $B$, $E$ | nothing |
| **What it optimizes** | Average cost (state + effort) | Worst-case disturbance gain | Loss target (heuristic) |
| **Gain computed** | Offline, once (DARE) | Offline, once (modified DARE + bisection) | Online, continuously (rules) |
| **Key equation** | $P = A^2P/(1+B^2P/R)+Q$ | $P = A^2P/(1+P(B^2/R-E^2/\gamma^2))+Q$ | `alpha *= rate` |
| **Regime** | Near operating point only | Slightly wider (hedges disturbance) | Anywhere loss is meaningful |
| **Failure mode** | $A$ drifts; $K$ is wrong | $A$ drifts; conservatism wastes budget | Reactive lag; no optimality |

---

## Experimental results — 4-way palindrome comparison

We ran all four controllers on the palindrome reversal task ($\gamma = 0.01$, no recurrence) at $\alpha \in \{1000, 10000, 100000\}$, 3 seeds each. Sysid was done on the palindrome task itself (not reused from the earlier `long_range_memory` experiments).

### The sysid red flag

The gray-box and black-box plant fits **wildly disagreed**:

| | $A$ | $B$ | $E$ | Stable? |
| --- | --- | --- | --- | --- |
| Gray-box (analytical) | $-299{,}784$ | $4{,}240$ | $990$ | No |
| Black-box (unconstrained OLS) | $0.198$ | $\approx 0$ | $-0.0002$ | Yes |

The analytical structure assumption — that $A = (1-\gamma)(1 + \alpha_0 H)$ with the physics-derived $B$ and $E$ — completely breaks down at $\gamma = 0.01$. The retention factor $(1-\gamma) = 0.99$ is so close to 1 that the scalar-norm dynamics don't behave like the linearized update equation predicts. The LQR and $H_\infty$ controllers were designed from the analytical (garbage) model.

### Results by $\alpha$

| $\alpha$ | Fixed loss | LQR loss | $H_\infty$ loss | Adaptive loss |
| --- | --- | --- | --- | --- |
| 1,000 | 47 ± 64 | 450 ± 317 | 377 ± 280 | **1.5 ± 0.04** |
| 10,000 | 121 ± 32 | 253 ± 181 | 395 ± 231 | **1.5 ± 0.09** |
| 100,000 | 18 ± 5 | 28 ± 14 | **15 ± 2** | **1.5 ± 0.10** |

(Average loss over last 100 steps, ± std across seeds.)

### Summary plot

![[attachments/palindrome_4way_summary.png]]

### Time-domain traces ($\alpha = 10{,}000$)

![[attachments/palindrome_4way_traces_a10000.png]]

### What happened

- **Adaptive** dominates everywhere — 12–80× lower loss than fixed, stable across the full $\alpha$ range.
- **LQR and $H_\infty$ are worse than fixed** at $\alpha = 1{,}000$ and $10{,}000$. They were designed from a plant model that says $A = -300{,}000$, so the gains are wildly miscalibrated. The controllers actively destabilize the system — visible in the traces as enormous loss spikes and $\alpha$ oscillations.
- **$H_\infty$ slightly beats fixed at $\alpha = 100{,}000$** (15 vs 18). This is the one regime where the model-based controller marginally helped, possibly because the large $\alpha$ puts the system closer to the regime where the linearization has some validity.
- **Accuracy is similar across all controllers** (~73–77%). The loss differences are about stability (whether the system blows up), not about learning capacity.

> [!important] Why the model-free controller won
> The model-based controllers (LQR, $H_\infty$) failed not because the control theory was wrong, but because the *plant model* was wrong. The gray-box structural assumption doesn't hold at $\gamma = 0.01$, and controllers designed from a bad model are worse than no controller at all. The adaptive controller won because it sidestepped the model entirely — it reads loss, not weight norm, and reacts to what's actually happening.
>
> This is the central diagnostic: **the bottleneck is the plant model, not the controller design**. Fix the model (online identification, $\mu$-synthesis for structured uncertainty in $A$), and the model-based controllers should pull ahead. Until then, the model-free heuristic is the only safe option.

---

## Connecting to what's next (§9)

The paper's roadmap based on these results:

1. **$\mu$-synthesis**: Treat the time-varying $A$ as *structured uncertainty* rather than a known constant. Instead of one $A$, you specify a *set* of possible $A$'s (an uncertainty block), and the controller must work for all of them simultaneously. This is the natural next step beyond $H_\infty$.
2. **MPC (Model Predictive Control)**: Express the weight-norm corridor as a *hard constraint* ($x_{\min} \leq x \leq x_{\max}$) rather than a soft penalty ($Q \cdot \delta x^2$). This prevents the controller from ever leaving the corridor, rather than just penalizing it for doing so.
3. **Online identification**: Track $A$ as training progresses (running sysid continuously, updating the plant model in real time). This directly attacks the "stale $A$" problem.
4. **Vector-valued state**: Replace $x = \|w_{\text{eph}}\|$ (one scalar) with something richer — e.g., $[x_1, x_2] = [\|w_{\text{eph}}\|, \|g_{\text{raw}}\|]$ (the 2D plant model already prototyped in `plant_model.py`). This recovers some of the directional information lost in the scalar collapse.
