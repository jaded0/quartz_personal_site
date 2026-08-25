---
title: Robust control fundamentals — induced norms, H₂, H∞, LQR, what failed and what
  came next
date: 2026-04-07
tags:
- control-theory
- robust-control
- h-infinity
- lqr
- ephemeral-weights
- learning-notes
related:
- '[[ephemeral weights as optimizer-state-made-visible]]'
- '[[ephemeral weights optimizer refactor and DFA perf notes]]'
publish: true
description: 'Drawing-board note in response to the question: do I actually understand
  what induced norms / H₂ / H∞ / LQR mean, what was that "young guy paper that proved
  they don''t work," and is the controller in my repo doing something principled or
  a…'
---

Drawing-board note in response to the question: *do I actually understand what induced norms / H₂ / H∞ / LQR mean, what was that "young guy paper that proved they don't work," and is the controller in my repo doing something principled or a heuristic?*

Written in study-note form so I can come back and read it.

---

## 0. The setup, in your code (so we can be concrete)

Your repo has:

- **`plant_model.py`** — a linearized scalar plant in the **partitioned-input "generalized plant" form** from robust control:
  $$\delta x(t+1) \;=\; A\,\delta x(t) \;+\; B\,\delta u(t) \;+\; E\,\delta d(t)$$
  Each piece carries a specific role that the convention is built around:
  - $\delta x = \|w_{\text{eph}}\| - \bar x$ — **deviation of the state from the operating point**. Your one-dimensional state is the norm of the ephemeral weights.
  - $\delta u = \alpha - \alpha_0$ — **the control input you choose**: plasticity deviation from its nominal value $\alpha_0$.
  - $\delta d = \|g_{\text{raw}}\| - \bar g$ — **the exogenous disturbance you do not choose**: how much the raw gradient norm deviates from its nominal $\bar g$.
  - $A \in \mathbb{R}$ — autonomous dynamics; how the state evolves with no input and no disturbance. Comes out of the analytical fast-weight update as $A=(1-\gamma_0)(1+\alpha_0 H)$ with $H$ the effective Hessian, then **fit by least squares** on a sysid trace (`estimate_plant_analytical`).
  - $B \in \mathbb{R}$ — **control input matrix**: how much your knob $\delta u$ moves the state per step. Taken from the analytical formula $B = (1-\gamma_0)\bar g$, **not fit from data**.
  - $E \in \mathbb{R}$ — **disturbance input matrix**: how much an unwanted gradient fluctuation $\delta d$ moves the state per step. Taken from the analytical formula $E = (1-\gamma_0)\alpha_0$, **not fit from data**.

  The reason $E$ shows up as its own matrix (instead of being absorbed into $A$ or $B$ or hidden inside a stochastic noise term) is the central convention of robust control: *exogenous disturbances and control inputs must be kept structurally separate, because they play asymmetric roles in synthesis*. See §0.5 — that aside is the answer to "why does my plant look like this and is it really like that in the readings."
- **`controllers.py`** — `LQRController` (one-shot Riccati via `scipy.linalg.solve_discrete_are`, ignores $E$ entirely by construction), `HinfController` (custom scalar Riccati iterated to fixed point, with bisection on $\gamma$, *meant* to use $E$), `AdaptiveController` (a model-free heuristic that ramps $\alpha$ up when loss is decreasing and slams it down when loss is high).
- **`hebby_integration.py`** — at every char step, reads the current $\|w_{\text{eph}}\|$ from the live RNN and asks the controller for a new $\alpha$.
- **`sysid_results/sysid_results.json`** — current numbers: $A=0.152$, $B=4.44$, $E=0$, $\alpha_0=10^3$, $\gamma_0=0.7$, $Q=1$, $R=10^{-3}$, and *both LQR and H∞ producing the same $K=0.0342$*. That last bit matters — see §5 for the framework history and §8 for the *two independent reasons* it happens in your code.

So you're already doing the textbook robust-control loop: linearize a plant around an operating point in the partitioned-input form, identify the linear coefficients from data, then synthesize a state-feedback gain by solving an algebraic Riccati equation. The two Riccati controllers differ only in *which* Riccati equation — and what they make of the disturbance channel $E$.

This is **not** a model-free heuristic on the plant side. It is a heuristic in a different sense (see §7 and §9): the linear plant is itself a heuristic *approximation* of a wildly nonlinear, time-varying, possibly-bifurcating nonlinear system.

---

## 0.5 Aside — why is there an $E$ term at all, and is it really like this in the readings?

Short answer: **yes, but not in every textbook, and specifically not in the early chapters of yours.** The "plant has $A, B, E$ as three separate matrices" form is the *robust-control convention*, and the MIT 6.241J textbook in `~/Documents/brain/robust_control/dynamic_systems_and_control_mit_ocw_textbook` only adopts it about halfway through. The first half of that textbook, and most introductory control texts, use the simpler form where everything goes into $A$ and $B$.

### The two conventions

**Simple ("classical") state-space form** — what MIT 6.241J chapters 7 and 28 use:
$$\dot x = A x + B u, \qquad y = C x + D u.$$
There's exactly one input ($u$) and one output ($y$). Disturbances, references, and noise — if they're modeled at all — get folded into $u$, into the initial condition, or into a stochastic term. This is what you see in any first course on linear systems.

**Generalized plant ("partitioned") form** — the robust-control convention:
$$\dot x = A x + B_1 w + B_2 u, \qquad z = C_1 x + D_{11} w + D_{12} u, \qquad y = C_2 x + D_{21} w + D_{22} u.$$
The inputs are partitioned into two groups — the **exogenous** signal $w$ (disturbances, references, sensor noise, anything you don't choose) and the **control** signal $u$ (the actuator commands the controller picks). The outputs are partitioned the same way — the **performance** output $z$ (errors and weighted controls you want kept small) and the **measured** output $y$ (everything the controller actually gets to see).

**Your $E$ is exactly $B_1$.** Your $B$ is $B_2$. Your scalar plant has no nontrivial $C, D$ partition because $y = x$ (full state feedback) and $z = [\sqrt Q\, x;\ \sqrt R\, u]$ is implicit in the LQR cost.

### Why partition them at all

It would be possible to lump everything into a single input vector $\tilde u = [w;\, u]$ and write $\dot x = A x + \tilde B \tilde u$. Robust control refuses to do this for three reasons, all important enough that the asymmetry is structural:

1. **You choose $u$, you do not choose $w$.** Synthesis is a constrained game: pick a function $K$ that maps the *measured* signal $y$ into $u$ in real time, subject to causality. The controller cannot read $w$ — by definition — only $y$. Lumping $w$ and $u$ together loses the constraint that one half of the input is adversarial / random and the other half is yours to design.
2. **Performance specifications are statements about specific transfer functions.** "Reject disturbance" is "make $T_{zw}$ small." "Track reference" is "make $T_{zr}$ small." "Low control effort" is a weight on a row of $z$. Every meaningful spec has the form "make the transfer function from *this* input partition to *this* output partition small." If you don't partition, you can't even *write down* the spec.
3. **The synthesis math fundamentally needs the partition.** $H_\infty$ minimizes $\|T_{zw}\|_\infty$. $H_2$ minimizes $\|T_{zw}\|_2$. μ-synthesis minimizes $\mu_\Delta(F_l(P, K))$ where $P$ is the partitioned generalized plant. None of these problems make sense without the partition; they all *consume* the $B_1, B_2, C_1, C_2, D_{ij}$ blocks individually as separate arguments. Try to call `scipy.signal.place` versus the DGKF $H_\infty$ formulas and you'll see immediately that one wants $(A,B)$ and the other wants $(A, B_1, B_2, C_1, C_2, D_{11}, D_{12}, D_{21}, D_{22})$.

So the $E$ term in your code isn't a stylistic flourish — it's the place where "robust control" first diverges from "classical control." A controller that ignores $E$ has no protection against disturbances; a controller that designs against $E$ is doing $H_\infty$ (or $H_2$, or μ) by definition.

### Where in your textbook the partition is introduced

`dynamic_systems_and_control_mit_ocw_textbook` (MIT 6.241J, Dahleh / Dahleh / Verghese) does not introduce the partitioned form right away. Tracing it forward:

- **chap07 (State-Space Models)** — establishes $\dot x = Ax + Bu$, $y = Cx + Du$. One input, one output. No $E$.
- **chap08 (Simulation/Realization), chap22–chap27** (reachability, observability, minimal & balanced realization, poles/zeros) — all live in the simple-form world. The disturbance channel doesn't exist yet because none of these topics need it.
- **chap15 (External Input-Output Stability)** — introduces signal norms ($L_2$, $L_\infty$, RMS, $L_1$). This is the prerequisite for talking about induced norms on systems.
- **chap16 (System Norms)** — introduces *induced* norms on LTI systems. Defines the $L_2$-induced norm and identifies it with the $H_\infty$ norm. **Theorem 16.5** gives the **Hamiltonian-matrix test**: $\|H\|_\infty < \gamma$ iff the matrix
  $$M_\gamma = \begin{bmatrix} A & \tfrac{1}{\gamma}BB^\top \\ -\tfrac{1}{\gamma}C^\top C & -A^\top \end{bmatrix}$$
  has no purely imaginary eigenvalues. **This is directly relevant to your bisection routine** — Theorem 16.5 is *the* clean alternative to iterating a Riccati equation by hand. Wrap it in bisection on $\gamma$ and you have a numerically robust H∞-norm computer that doesn't need a fixed-point iteration at all. See §8.
- **chap17 (Interconnected Systems and Feedback: Well-Posedness, Stability, and Performance)** — **this is the first chapter where the textbook draws a feedback diagram with disturbance and noise as separate signals.** Figure 17.4 shows the standard control configuration with reference $r$, plant disturbance $d$, measurement noise $n$, control $u$, and measured output $y$ all present and labeled. The text doesn't yet use the matrix-partition notation $(B_1, B_2)$ but the conceptual partition is now on the page.
- **chap18 (Performance of Feedback Systems)** — **this is where the partition becomes formal.** The chapter opens by stating that performance specs are closed-loop relations between **exogenous inputs $w$** and **regulated outputs $z$**. From here on the textbook is in generalized-plant land. Sensitivity $S = (1 + PK)^{-1}$, complementary sensitivity $T = PK(1+PK)^{-1}$, $S+T=1$, loop shaping, all of it. **If you read one chapter to understand why your plant has an $E$, read chap18.**
- **chap19 (Robust Stability in SISO Systems)** — defines the additive uncertainty set $\Omega_a = \{P : P = P_0 + W\Delta,\ \|\Delta\|_\infty \leq 1\}$ and the multiplicative set $\Omega_m = \{P : P = P_0(I + W\Delta)\}$. This is where the textbook is closest to motivating μ-synthesis: it explicitly notes that "if the uncertainties of major concern to us were *parametric uncertainties*… the above uncertainty set would greatly overestimate the set of plants of interest" — which is *exactly* the conservatism gap that μ exists to close (see §10). The textbook stops just short of introducing μ.
- **chap28 (Stabilization: State Feedback)** — uses $\delta x = Ax + Bu$, $u = Fx + v$, **no separate disturbance term**. The chapter explicitly punts: line 30 says "uncertainty and unmodeled dynamics should be dealt with as discussed in previous chapters; namely, by imposing a norm constraint on an appropriate closed loop transfer function." That's a pointer back to chap16–chap19.
- **chap30 (Minimality and Stability of Interconnected Systems)** — gives the state-space algebra for series, parallel, and feedback connections. **This is the closest the textbook gets to LFT material, although it does not use the LFT name or notation.** It's the right chapter to read if you want to see the algebra you'd need in order to *write* an LFT representation of your plant by hand.

### Where LFT (linear-fractional transformation) actually lives

**LFT is not introduced anywhere in this textbook** — not by name, not by notation. The closest the textbook gets is the feedback-interconnection algebra in chap30 (the math is almost there, just without the LFT framing) plus the additive/multiplicative uncertainty parameterization in chap19 (which is *one* canonical LFT, presented without the LFT label).

If you want the LFT formalism proper — $F_u(M, \Delta)$, $F_l(M, K)$, the upper/lower LFT diagrams, the "pull out the $\Delta$" procedure that turns parametric uncertainty into a standard $\Delta$-block — you need a different reading. The two canonical sources:

- **Skogestad & Postlethwaite, *Multivariable Feedback Control* (2005)** — **chapter 3 §3.2 ("Frequency-domain analysis")** introduces small-gain-theorem framing; **chapter 8** ("Robust stability and performance analysis") is where LFTs get formal definitions and where the generalized plant $P$ is constructed via LFT explicitly. Chapter 8 §8.1–§8.4 is the most pedagogically friendly introduction to LFTs in print.
- **Zhou, Doyle & Glover, *Robust and Optimal Control* (1996)** — **chapter 9 ("Linear Fractional Transformations")** is the rigorous treatment. Chapter 10 ("μ and μ-synthesis") then builds μ on top. Heavier than Skogestad–Postlethwaite but the canonical reference.

If you go further into the MIT OCW directory: there is a 6.245 ("Multivariable Control Systems") follow-on course that *does* cover LFTs, $\mu$, and DGKF in full. If those notes are sitting next to the 6.241J ones in your `robust_control/` directory, look there next — 6.245 picks up exactly where 6.241J leaves off (chap19) and is where the LFT machinery would be developed in the MIT lineage.

### TL;DR of this aside

- The $E$ term in your plant is the disturbance-input matrix $B_1$ from the **partitioned generalized-plant form**, the convention robust control uses to keep exogenous inputs (disturbances, references, noise) structurally separate from control inputs (the actuator commands you choose). It's not optional decoration: $H_\infty$, $H_2$ as a synthesis problem, and μ-synthesis all *require* the partition to be defined.
- Your textbook (MIT 6.241J) starts in the simple $Ax + Bu$ form (chap7, chap28), then introduces the partition gradually: feedback diagram with $r,d,n$ in **chap17 (Fig 17.4)**, formal $w/z$ partition in **chap18 (opening paragraph)**, uncertainty parameterization in **chap19**. Read **chap18 first**, then chap17 and chap19. **Chap16 (Theorem 16.5)** is the H∞-norm computation tool relevant to §8.
- LFT proper is **not in this textbook**. For the LFT formalism, read **Skogestad–Postlethwaite chap 8** (friendlier) or **Zhou–Doyle–Glover chap 9** (rigorous). If MIT 6.245 notes are also in your `robust_control/` directory, that's the natural next reading inside the MIT lineage.

---

## 1. Induced norms — the building block everything else is named after

For a linear operator $T : X \to Y$ between normed spaces, the **induced norm** is

$$\|T\| := \sup_{x \neq 0} \frac{\|Tx\|_Y}{\|x\|_X}.$$

In words: the worst-case amplification of input magnitude into output magnitude. For a matrix $T \in \mathbb{R}^{m\times n}$ with $\ell_2$ norms on both sides, $\|T\|_2 = \sigma_{\max}(T)$, the largest singular value.

When you replace $T$ with a linear time-invariant *system* — a transfer function $G(s)$ that maps input signals $u$ to output signals $y$ — you need a norm on the signal spaces. Two natural choices give two different system norms:

- $L^2$ norm on signals → $H^2$ system norm
- $L^\infty$ norm on signals (or actually $L^2 \to L^2$ induced) → $H^\infty$ system norm

The "H" stands for **Hardy space** — the space of functions analytic on the right-half plane (continuous time) or outside the unit disk (discrete time). $H^2$ means $G$ has finite $L^2$ norm on the boundary; $H^\infty$ means $G$ is bounded on the boundary. In control language: $H^2$ requires the system to be "energy bounded" and $H^\infty$ requires the system to have "bounded gain at every frequency." Both require stability.

The terminology is unfortunate. There is no "H₁ norm" used in mainstream robust control — you almost certainly mean $H^2$. ($H^1$ exists in pure math as a Hardy space, but it's not used as a system norm in any control textbook I've ever seen.) From here on I'll write $H_2$ and $H_\infty$ since that's the convention.

---

## 2. The $H_2$ norm — average gain, energy interpretation

$$\|G\|_{H_2}^2 := \frac{1}{2\pi}\int_{-\infty}^{\infty} \operatorname{tr}\!\big(G^*(j\omega) G(j\omega)\big)\,d\omega.$$

Three equivalent reads:

1. **Frequency**: integrate the squared singular values across all frequencies. It's a *root-mean-square* over frequency, not a worst-case.
2. **Time, impulse**: $\|G\|_{H_2}^2 = \int_0^\infty \operatorname{tr}\!\big(g(t)^\top g(t)\big)\,dt$ — total energy of the impulse response.
3. **Time, white noise**: it's the steady-state RMS of the output when the input is unit white noise.

That last reading is the bridge to LQR.

---

## 3. The $H_\infty$ norm — worst-case gain at any frequency

$$\|G\|_{H_\infty} := \sup_\omega \sigma_{\max}\!\big(G(j\omega)\big).$$

This is the **induced $L^2 \to L^2$ norm**. It says: across all bounded-energy input signals, what's the largest energy-amplification any of them can ever cause? It's a single number that bounds the worst frequency, the worst direction, and the worst input shape simultaneously.

Two ways the same number is used in practice:

- **Performance**: minimize $\|T_{zw}\|_{H_\infty}$ where $w$ is exogenous disturbance and $z$ is performance output. You're shrinking the worst possible disturbance-to-error gain.
- **Robustness**: by the *small gain theorem*, if you have a stable nominal closed loop and an unknown stable perturbation $\Delta$ with $\|\Delta\|_{H_\infty} \leq 1$ wrapped around some channel, the loop stays stable iff $\|T\|_{H_\infty} < 1$ where $T$ is the closed-loop map seen by $\Delta$. So shrinking the $H_\infty$ norm of the right channel buys you a *guaranteed robustness margin* against any unmodeled perturbation in a unit ball.

The two readings are duals of each other. That's the magic of $H_\infty$: the same Riccati machinery that minimizes worst-case performance also maximizes guaranteed robustness, because performance against worst-case disturbance ≡ stability under worst-case perturbation.

---

## 4. LQR — what it actually minimizes

LQR minimizes the quadratic cost

$$J = \sum_{t=0}^{\infty} \big(x_t^\top Q x_t + u_t^\top R u_t\big)$$

subject to $x_{t+1} = A x_t + B u_t$. The optimal policy is linear state feedback $u_t = -K x_t$, with $K = (R + B^\top P B)^{-1} B^\top P A$ where $P$ solves the **discrete-time algebraic Riccati equation (DARE)**

$$P = A^\top P A - A^\top P B (R + B^\top P B)^{-1} B^\top P A + Q.$$

Two facts that aren't always emphasized:

**Fact 1: LQR is exactly an $H_2$ design.** Take the closed-loop map from a fictitious input-disturbance $w$ (white-noise driving the state) to the stacked performance output $z = [\sqrt{Q}\,x;\ \sqrt{R}\,u]$. Minimizing $\|T_{zw}\|_{H_2}^2$ is *the same problem* as minimizing the LQR cost. So LQR isn't a different theory from $H_2$ — it's the most famous instance of $H_2$ optimal control with full state information.

**Fact 2: LQR (with full state feedback) has very nice classical margins.** When you can measure $x$ directly and feed it back, the resulting loop has guaranteed gain margin $[0.5, \infty)$ and phase margin $\geq 60°$ in the SISO case — independent of $A, B, Q, R$. This is the "classical LQR robustness" result that made everyone love it in the 60s and 70s.

The trouble starts when you can't measure $x$.

---

## 5. The young-guy paper: Doyle 1978

You're thinking of **John Doyle's "Guaranteed Margins for LQG Regulators"**, *IEEE TAC* August 1978. It's *one page long*. Doyle was a grad student. The abstract reads, in full:

> "There are none."

That's it. The body shows that as soon as you replace measured state with a Kalman filter estimate (forming the LQG = Linear Quadratic Gaussian regulator, which is the natural way to use LQR when you only see noisy outputs), you can have *arbitrarily small* gain and phase margins. The classical robustness of LQR is fundamentally a property of the *state-feedback* loop and does not survive the addition of an observer, even though LQG inherits LQR's optimality in the noise-free limit.

This was the bomb that opened the field of modern robust control. It said: the most popular optimal-control method of the era is *not robust* in any guaranteed sense, even though it looks robust when you stare at the LQR-only half. You cannot just slap an estimator onto an LQR design and expect the margins to follow.

**The improvements that followed**, in rough order:

- **Zames 1981, "Feedback and optimal sensitivity..."** — proposes that the right thing to minimize is an $H_\infty$ norm of the sensitivity function, because that's a worst-case measure that survives any uncertainty in a class.
- **Doyle, Glover, Khargonekar, Francis 1989, "State-space solutions to standard $H_2$ and $H_\infty$ control problems"** — the famous **DGKF** paper. Reduces $H_\infty$ synthesis to *two coupled Riccati equations* (one for control, one for filtering, plus a coupling condition). This made $H_\infty$ a tool you could actually use, not just a frequency-domain sketch.
- **Doyle 1982, structured singular value $\mu$** → **$\mu$-synthesis / D-K iteration**. $H_\infty$ is conservative because it allows the perturbation $\Delta$ to be any norm-bounded LTI map, including ones that couple unrelated channels arbitrarily. In reality your uncertainty has structure — a parameter is a scalar, an unmodeled actuator is a single SISO block, etc. $\mu$-synthesis lets you exploit that structure to get a tighter bound. The "later improved on" you may be remembering.
- **LMI-based synthesis (Boyd, Ghaoui, Feron, Balakrishnan 1994)**. Reformulate everything as linear matrix inequalities solved by interior-point methods. Same answers as DGKF in clean cases, but extends gracefully to multi-objective ($H_2/H_\infty$ mixed), gain-scheduled, and uncertain-system designs without rewriting the whole derivation each time.
- **Model Predictive Control (MPC)** for nonlinear / constrained problems. Robust MPC, tube MPC, and learning-based MPC are the modern descendants for systems where neither LQR nor $H_\infty$ fit cleanly.

So: **Doyle 1978 said "LQG is not robust." Zames 1981 / DGKF 1989 said "use $H_\infty$ instead." Doyle 1982 / 1985 said "use $\mu$ to exploit structure." Modern LMI/MPC said "and here's how to scale that to messy real systems."**

---

## 6. So is $H_\infty$ what I should be using?

Probably yes — *for the role you're using it in*. But the leverage isn't where you might think, and there are subtleties that hit your specific code.

**The case for $H_\infty$ over LQR in your problem:**

- You explicitly model a disturbance channel $E\,\delta d$ (gradient-norm fluctuation around the operating point). LQR ignores $E$ entirely. $H_\infty$ designs against the worst-case disturbance through that channel, which is *exactly* the right thing if you don't trust $\bar g$ to be stationary.
- Your system is nonlinear and your linearization has *parameter uncertainty* (the effective Hessian $H$ in $A=(1-\gamma)(1+\alpha_0 H)$ is not a constant — it changes as the optimizer moves through the loss landscape). $H_\infty$ buys robustness against unmodeled dynamics and parameter drift via the small-gain theorem, in a way LQR cannot.
- The loss-explosion / bifurcation behavior you've alluded to is the *signature* of a worst-case problem: the controller needs to keep the closed loop from ever venturing into the unstable region, even when the disturbance tries hard to push it there. That's an $H_\infty$-shaped objective, not an $H_2$-shaped one.

**The case against, or at least: the reasons it doesn't currently help you:**

- Your sysid has $E = 0$ in the JSON. With zero disturbance gain, the $H_\infty$ Riccati collapses to the $H_2$/LQR Riccati exactly. There is *nothing* for the disturbance-attenuation level $\gamma$ to do, because there is no disturbance to attenuate. **This is why your saved JSON shows LQR and H∞ producing identical $K=0.0342$ — it's not a coincidence and not a bug, it's the math telling you the disturbance channel is empty.** Until $E$ has real magnitude, $H_\infty$ buys you literally zero over LQR.
- Even when $E > 0$, your *implementation* of `_solve_hinf` (more in §8) ends up returning $K = BAP/(R+B^2P)$, which is the LQR formula evaluated at the H∞-Riccati $P$. That's only a partial $H_\infty$ controller — the gain expression is missing the $\gamma$-dependent indefinite term. So even if $E$ were nonzero, the gain you'd compute would be closer to "LQR with $P$ shifted by the disturbance" than "true $H_\infty$ state feedback." See §8.

**A bigger question that $H_\infty$ doesn't answer for you:** the linear model is fine *near the operating point* but your control problem is fundamentally about *not leaving* the linear regime. That's a constrained-nonlinear-control question, which is the natural turf of MPC, not Riccati methods. See §12. (And see §10 for whether μ-synthesis — the structured-uncertainty refinement of $H_\infty$ — is the right next move within the Riccati family.)

---

## 7. Is your code linearizing your "real" model, or fitting a different model?

Both, actually, layered.

`estimate_plant_analytical` does this:

1. Take a sysid trace from a *real* hebby training run with varying $\alpha$ — `data` has columns `x` (weight norm), `g_raw` (gradient norm), `alpha`, `gamma`, `loss`.
2. Compute deviations $\delta x, \delta u, \delta d$ from operating-point means.
3. Use the **analytical structure** $B = (1-\gamma_0)\bar g$ and $E = (1-\gamma_0)\alpha_0$ — these come straight from differentiating the fast-weight update, no data needed.
4. Subtract the known terms from $\delta x(t+1)$ and run a 1-D least squares to fit $A$.

So yes — this is genuine system identification. You are not assuming the linear model exists in some abstract sense; you are *estimating it from data*. But you are forcing it to obey the analytical form derived from the fast-weight update equation. In control terms, this is **gray-box system identification**: structure from physics, parameters from data.

`estimate_plant_unconstrained` is the sanity check — it fits all three coefficients ($A, B, E$) by unconstrained least squares, no analytical structure. If the gray-box and black-box fits agree, your structural assumption is consistent with the data. Worth running both regularly.

What you are *not* doing:

- You are not linearizing the actual hebby network state ($w_{\text{eph}}$ as a tensor, the full hidden state, the loss landscape geometry). Your "state" is one scalar — $\|w_{\text{eph}}\|$ — and your model is the dynamics of that scalar.
- You are not identifying a high-order or nonlinear model. The model is first order, linear, time-invariant, scalar.
- You are not online-adapting the model. It's identified once and deployed.

This is fine for a first cut. It is also where the brittleness will live. The first thing to question if the controller misbehaves is whether $A$ has drifted because the operating point moved.

Your controller is **principled, given the model**. The heuristic part is the *modeling choice*, not the synthesis.

---

## 8. What is actually wrong with your $H_\infty$ controller

You asked "you mention I don't have a working H∞ — what's wrong with it?" Here's the consolidated answer in punch-list order, severity descending. Most-load-bearing first.

### The structure is right, the inner solve is wrong

The discrete-time scalar $H_\infty$ Riccati for state feedback is approximately

$$P = A^2 P\Big/\!\big(1 + P(B^2/R - E^2/\gamma^2)\big) + Q,$$

which *is* what `_solve_hinf_riccati` iterates. The bisection on $\gamma$ is the textbook recipe: as $\gamma$ shrinks, you demand more disturbance attenuation, and at some critical $\gamma_\star$ the Riccati stops admitting a positive definite solution. The smallest $\gamma$ for which $P > 0$ exists is the optimal H∞ disturbance-attenuation level. Bisection between a known-feasible upper bound and an infeasible lower bound is the standard way to find it. **As a piece of architecture, `_solve_hinf` is doing the right kind of thing.**

What it then does with the $P$ that bisection produces is where it stops being H∞.

### Bug 1 (the load-bearing one): the gain formula on `controllers.py:184` is the LQR formula, not the H∞ formula

This is the bug that would matter if everything else were fixed. Inside `_solve_hinf`, after the bisection lands on a $\gamma$ and a corresponding $P$ from the H∞ Riccati, line 184 computes
```python
K = (B * A * P) / (R + B**2 * P)
```
That is the **LQR gain formula** $K = BAP/(R + B^2 P)$, which is the closed-form $K = (R + B^\top P B)^{-1} B^\top P A$ specialized to the scalar case. It is *not* the H∞ state-feedback gain.

True scalar discrete-time H∞ state feedback has the form
$$K_{H_\infty} = \frac{B A P}{R + (B^2 - E^2/\gamma^2)\,P + (\text{coupling correction})}$$
i.e. the denominator carries an explicit $\gamma$-dependent indefinite term coming from the disturbance channel. The line 138 comment in `_solve_hinf` hints that the author knew this was supposed to happen, but line 184 silently falls back to the LQR formula. **The result is that `HinfController.K` numerically equals the LQR gain evaluated at the H∞-Riccati $P$, not the H∞-optimal gain.** When $E = 0$ this is harmless because the H∞ Riccati collapses to the LQR Riccati anyway and the two formulas agree. The instant $E \neq 0$, the controller will still be reporting an LQR gain at a slightly different $P$, which is *not* what you wanted.

**Fix:** stop iterating by hand. Reduce the discrete-time H∞ state-feedback problem to a *modified DARE* with the disturbance channel folded into the cross term, and call `scipy.linalg.solve_discrete_are` on that. The modification is the standard one — replace $R$ with the indefinite block $\operatorname{diag}(R, -\gamma^2 I)$ and the input matrix with the augmented $[B,\ E]$. `scipy` will compute the correct $P$ and the correct $K$ in one call, generalizes immediately to the 2D plant, and removes both this bug and bug 3 below in a single edit.

### Bug 2: `gamma_opt = 0.0` in `sysid_results.json` is impossible

A genuine optimal disturbance-attenuation level can't be exactly zero — that would be infinite disturbance rejection, which is achievable only if the disturbance channel has no effect at all. With $E = 0$ in your data, the latter *is* true ("any $\gamma$ works"), so bisection collapses to the lower bound, which is `tol = 1e-6` — not `0.0`. The JSON shows `0.0` exactly, which means **something in the pipeline overwrites $\gamma$ between bisection and serialization.** Drop a `print(gamma)` right after bisection terminates and right before the JSON dump, and watch for the value changing. Probably a lazy default initializer somewhere.

This is cosmetic when $E = 0$ (you'd still get the LQR gain either way, see below) but you do not want a load-bearing number to be silently wrong by the time you start trusting it.

### Bug 3: a 1000-step hand-rolled fixed-point iteration won't survive 2D

`_solve_hinf_riccati` iterates the scalar Riccati to fixed point by hand for 1000 steps. This is fine for the 1D case — the scalar Riccati has a closed-form root and Newton converges in single digits anyway — but the moment you move to `PlantModel2D` you cannot iterate a $2\times2$ Riccati this way without thinking carefully about positive definiteness, conditioning, and convergence. The fix is the same as for bug 1: call `scipy.linalg.solve_discrete_are` on the modified DARE. One call replaces the entire `_solve_hinf_riccati` body and works for any state dimension.

### Bug 4 (latent): with $E = 0$, all of the above is silent

Right now, $E = 0$ in your `sysid_results.json`. The H∞ Riccati and the LQR Riccati produce *exactly the same* $P$. The LQR formula and the H∞ formula at that $P$ produce *exactly the same* $K$. So your saved JSON dutifully reports `K = 0.0342` from both controllers — and they agree because **two separate things are broken in a way that masks each other**, plus the data has no disturbance to attenuate. You will see no symptom until $E$ becomes nonzero. At that moment, bug 1 will start producing wrong gains and you will not know it from the controller output alone — you'd only catch it by comparing against a `solve_discrete_are`-based reference.

This is what makes "fix the H∞ inner solver" item #3 in §12. It's not visibly broken yet, and getting $E \neq 0$ in the data is a precondition for the bug to even manifest.

### Structural alternative worth considering: Theorem 16.5 from your textbook

If you want to throw out the Riccati-iteration approach entirely, MIT 6.241J **chap16 Theorem 16.5** gives a cleaner characterization. Define
$$M_\gamma = \begin{bmatrix} A & \tfrac{1}{\gamma} B B^\top \\ -\tfrac{1}{\gamma} C^\top C & -A^\top \end{bmatrix}.$$
Then $\|H\|_\infty < \gamma$ if and only if $M_\gamma$ has no purely imaginary eigenvalues. Wrap that test in a bisection on $\gamma$ and you have a numerically robust H∞-norm computer that needs nothing but `numpy.linalg.eig` per evaluation — no Riccati iteration, no positive-definiteness checks, no fixed-point convergence to babysit. This is the *analysis* tool, not the synthesis tool, but it's worth knowing because (a) it's the right way to *verify* whatever your synthesis spits out, and (b) it gives you a clean second opinion if the modified-DARE call from bug 1's fix gives you suspicious numbers.

### Verdict

The bisection structure is correct. The bug that matters is the gain formula at line 184: it is the LQR formula and was probably copy-pasted from `_solve_lqr` and never finished. Until $E \neq 0$ this is invisible; the moment $E \neq 0$ it will silently hide H∞'s entire contribution. The right fix is not "patch line 184" — it is "delete `_solve_hinf_riccati` and call `scipy.linalg.solve_discrete_are` on the modified DARE." That single edit eliminates bugs 1, 3, and 4 at once and gets you a real $H_\infty$ controller for the first time. Bug 2 (the JSON `0.0` weirdness) is independent of all of this and worth a 30-second `print` to track down separately.

---

## 9. Where LQR / $H_\infty$ fundamentally fail for your problem

This is the most important section. None of the above matters if the *framework* is the wrong one.

**Failure mode 1: Linearization doesn't survive the bifurcation.** Your evidence (loss explodes when $\alpha$ goes too high) says the real system has a regime change, not a smooth response. A linear model fit around a stable operating point cannot represent a regime where the system is one $\delta\alpha$ away from blowing up. Locally the gain looks small; globally there's a cliff. LQR/H∞ minimize a quadratic cost in a neighborhood — they have *no concept* of "don't go off the cliff." They will happily issue a control action that pushes the state out of the basin of attraction, because nothing in the cost says they shouldn't.

**Failure mode 2: Time-varying coefficients.** $A=(1-\gamma_0)(1 + \alpha_0 H)$ where $H$ is the effective Hessian, and the Hessian *changes* as training progresses. A model fit on early-training data is wrong by mid-training. You can re-identify periodically, but then you're not really using a fixed-coefficient theory anymore — you're doing gain scheduling, and you should be honest about it.

**Failure mode 3: The state you actually care about isn't $\|w_{\text{eph}}\|$.** You care about *loss / accuracy / capacity to learn the next batch*. Those are nonlinearly related to the weight norm and to each other. Your scalar state model conflates "high weight norm" (could be fine, just storing useful structure) with "weight norm rising fast" (probably about to explode). A 2D model with $[\|w_{\text{eph}}\|, \|g\|]$ as in `PlantModel2D` is closer, but still not what you really care about. The genuine state is the entire optimizer trajectory in loss-landscape coordinates.

**Failure mode 4: $H_\infty$'s conservatism.** $H_\infty$ assumes the *worst* disturbance, every step, in the worst frequency direction. Real disturbances in your system are gradient-norm fluctuations, which are bounded in expectation but not in worst-case (a single bad batch can produce a massive gradient). $H_\infty$ would protect against that single bad batch by being very cautious all the time, which is exactly what you don't want when training is going well. This is the conservatism that $\mu$-synthesis was invented to fight (see §10), and that *robust MPC* / *learning-based MPC* fights better.

---

## 10. μ-synthesis — does the structure of my uncertainty help?

### What it actually is

μ-synthesis is the framework Doyle introduced in 1982 to fix $H_\infty$'s biggest source of conservatism: the assumption that the perturbation $\Delta$ wrapped around your loop can be *any* norm-bounded LTI matrix.

In $H_\infty$ via the small-gain theorem, you protect against an unknown stable $\Delta$ with $\|\Delta\|_\infty \leq 1$. The set of allowed $\Delta$ is the entire unit ball of stable LTI matrices — enormous, and *most of the perturbations in it are physically impossible* in your system. A real-parameter uncertainty (the Hessian is just one number) is treated as freely as a fully-coupled MIMO unmodeled-dynamics block. You pay for that generality in performance.

μ-synthesis says: tell me the *structure* of your uncertainty, and I'll only protect against perturbations of that structure. Define the **structured singular value** of a matrix $M$ with respect to a structure set $\mathbf{\Delta}$:

$$\mu_{\mathbf{\Delta}}(M) := \frac{1}{\min\{\bar\sigma(\Delta) : \Delta \in \mathbf{\Delta},\ \det(I - M\Delta) = 0\}}.$$

In words: one over the size of the smallest *structured* perturbation that destabilizes the loop. The structure $\mathbf{\Delta}$ might be:

- "block-diagonal: one $1\times1$ real block (parametric) + one $2\times2$ complex block (unmodeled dynamics)"
- "diagonal scalar real" (only parametric uncertainties)
- "full complex block" — and in this case $\mu = \sigma_{\max}$, recovering plain $H_\infty$

For any nontrivial structure, $\mu(M) \leq \sigma_{\max}(M)$, often strictly. So **the stability margin you get from μ is at least as good as $H_\infty$, and usually better**, because it doesn't waste robustness on perturbations that can't physically occur.

The synthesis problem: find a controller $K$ that minimizes $\mu_{\mathbf{\Delta}}(F_l(P, K))$, where $F_l$ is the lower linear-fractional transformation closing $K$ around the generalized plant $P$.

### How it's actually solved (and why it's hard)

Computing $\mu$ exactly is **NP-hard** in general. The standard practical approach is **D-K iteration**:

1. **D step:** hold $K$ fixed. Find diagonal scaling matrices $D$ that commute with the structure $\mathbf{\Delta}$, minimizing $\inf_D \|D M(K) D^{-1}\|_\infty$. This is a convex problem (an LMI) and gives an *upper bound* on $\mu$ — the "D-scaled" upper bound.
2. **K step:** hold $D$ fixed. Run standard $H_\infty$ synthesis on the scaled plant $D P D^{-1}$. This is a Riccati problem (DGKF).
3. Iterate until $D$ and $K$ stop moving.

D-K iteration is **not guaranteed to converge to the global optimum** — the joint problem in $(D, K)$ is non-convex, even though each step alone is. In practice it works well for moderate-size problems. Variants exist for mixed real/complex structures (DGK iteration, mixed-μ).

The K step calls a standard $H_\infty$ solver, so **μ-synthesis is built on top of $H_\infty$**. If your $H_\infty$ inner solver is broken, your μ-synthesis is broken — see §8.

### Do you already do it?

No. Your `controllers.py` has $H_2$/LQR, a partial $H_\infty$ implementation, and the adaptive heuristic. There is no:

- LFT (linear-fractional transformation) representation of your plant
- Generalized plant $P$ with separated performance and uncertainty channels
- D-K iteration loop
- μ computation (`mussv` or equivalent)

To add it you would need to:

1. **Reframe your plant as an LFT.** Pull the parametric uncertainties out of the nominal $A=(1-\gamma_0)(1+\alpha_0 H)$ and $B = (1-\gamma_0)\bar g$ as feedback perturbations $\Delta_H$, $\Delta_g$. Decide which channels also need an unmodeled-dynamics block $\Delta_u$.
2. **Pick weights.** Performance weights on $z = [\sqrt Q\,x;\,\sqrt R\,u]$, plus uncertainty-bound weights on each $\Delta$ block (these encode how *big* you believe each parameter can vary).
3. **Run D-K iteration.** And here Python tooling becomes a real friction — see Q4 in the open questions below.

### Does it fit your problem?

The argument *for* μ-synthesis on your specific setup is strong on paper:

- You have **real parametric uncertainty** of exactly the right shape: $H$ is one real scalar that drifts during training. $\bar g$ is another real scalar. These are textbook μ-synthesis use cases — in fact "single real parametric uncertainty in the dynamics matrix" is the canonical pedagogical example.
- You also have **unmodeled dynamics** — your scalar plant doesn't capture the coupling to slow weights, hidden state, or the full optimizer trajectory in the loss landscape. That's naturally one or more complex full blocks.
- $H_\infty$ would treat all of these as a single full unstructured perturbation, wasting most of its robustness budget. μ-synthesis would respect the fact that "$H$ is a real scalar" and "the unmodeled dynamics is a separate channel" and not let them conspire arbitrarily.
- **Aggressive $\alpha$ is the entire game for your method.** The whole point of pushing plasticity high is to get useful memory. Anything that lets you safely run $\alpha$ higher is on the critical path of the research. Conservatism is *especially expensive* for you, in a way it isn't for an aerospace control problem.

The argument *against*, in order of severity:

- **You have to fix the $H_\infty$ inner solver first.** μ-synthesis is built on top of $H_\infty$ as the K-step. Adding μ on top of a broken $H_\infty$ produces a broken μ-controller, with the additional bug surface of D-K iteration on top.
- **Python tooling is genuinely thin.** MATLAB's Robust Control Toolbox (`musyn`, `dksyn`) is the gold standard and Just Works. In Python, `python-control` has `mussv` for the upper-bound *analysis* but limited to no full *synthesis*. You'd be looking at porting D-K iteration manually around an $H_\infty$ solver, or using `Skogestad-Python` examples as a starting point. This is a real cost that doesn't apply to plain LQR/H∞ (both of which `scipy`+`python-control` handle natively).
- **You haven't shown that conservatism is your bottleneck.** μ-synthesis only buys you something if your *working* $H_\infty$ controller is *too cautious* and you have evidence of the gap. Right now you have neither — no working $H_\infty$, no measured conservatism. It's premature to optimize away conservatism you haven't seen.
- **Your parametric variations may be too large.** μ-synthesis assumes the LFT model is faithful — i.e., the perturbations are *small* enough that the linearization holds across the whole uncertainty set. If $H$ varies by 100× across training, the linearization is broken before μ even gets a chance, and no clever robust synthesis can fix that. This is the same point as failure mode 2 in §9 but with sharper teeth: μ specifically requires the perturbations to fit inside the LFT envelope.

### Does it solve problems relevant to your use?

It addresses *one* specific problem — **conservatism of $H_\infty$ when uncertainty is structured** — and it does it well.

It does **not** solve any of the other failure modes from §9:

- **Bifurcation / "don't go off the cliff":** μ-synthesis is still a Riccati method optimizing a quadratic worst-case cost. Nothing in it understands constraints. The bifurcation in your system is naturally a *constraint*, not an objective term — it lives in MPC's world, not μ's world.
- **Time-varying $H$:** μ assumes the parameter is *uncertain but constant*. If $H$ drifts during a training run, you're really in **gain-scheduling / LPV (linear parameter-varying)** territory, which is a different framework. μ is a special case of the more general LPV synthesis but it's not designed for parameters that move during operation.
- **Wrong state variable:** still working with the same scalar $\|w_{\text{eph}}\|$ state. μ doesn't add a state, it just gives you a better controller for the state you already have.
- **Linear model fit on early-training is wrong by mid-training:** μ assumes a fixed nominal plant. Re-identifying online and re-running μ-synthesis is technically possible but turns the deployment story from "compute a gain once, use it forever" into "solve a non-convex iterative problem online." Painful.

So μ-synthesis sits in the same universe as $H_\infty$ — it's a *less-conservative* version of the same Riccati framework — and it does *not* address any of the failure modes that aren't about conservatism. It would let you push $\alpha$ higher *in the regime where the linear model is valid*. It does nothing to extend that regime.

### Should you do it?

**Not as your next move, but yes as a longer-term direction *if* you stay in the Riccati framework.** The blocking issues in front of you (see §12) are all upstream of μ:

1. Get $E \neq 0$ in your sysid data
2. Fix the $H_\infty$ gain formula in `_solve_hinf`
3. Validate the linear model on held-out data
4. Decide whether MPC is the right framework instead

Until those are resolved, μ-synthesis is a luxury problem on top of a foundation that doesn't yet hold weight. The right time to come back to it is *after* you have a working $H_\infty$ controller, *and* you've measured how much performance it leaves on the table due to conservatism (for example, by comparing the highest $\alpha$ it permits before triggering blow-up vs. the highest a hand-tuned policy can safely use), *and* you've decided to stay in the Riccati family rather than jumping to MPC.

If/when you reach that point, μ-synthesis is the natural next step *for the parametric-uncertainty channel specifically*. It is not a substitute for thinking about whether the linear model is the right model in the first place.

### Open questions you actually need to answer before committing

These are the things *I can't answer for you* — they require running stuff against your training data — but you need answers before sinking time into a μ-synthesis branch.

1. **What is the empirical range of $H$ (the effective Hessian) across a full training run?** Compute it from your sysid data: $\hat H = (\hat A/(1-\gamma_0) - 1)/\alpha_0$, recomputed in sliding windows over the training trace. If $H$ varies by ±20% it's a tractable parametric perturbation and μ is a great fit. If it varies by 10× it's a regime change and you need a *different* framework (LPV / gain scheduling / MPC), not μ.
2. **Are $H$ and $\bar g$ correlated?** Both depend on where the optimizer is in the loss landscape. If they covary tightly, modeling them as *independent* block perturbations *overestimates* the uncertainty set and gives back some of the conservatism μ was supposed to remove. A scatter plot from the sysid trace answers this in five minutes. If they're correlated, you may want to model a single underlying parameter (loss-landscape-position) that affects both coefficients, rather than two independent ones.
3. **How fast does $H$ change?** μ assumes uncertain-but-constant. If $H$ drifts on the same timescale as your control bandwidth (one update per character), the structured-uncertainty framework doesn't apply cleanly — you're really doing LPV control. Compute the autocorrelation time of $\hat H(t)$ and compare it to your control update rate.
4. **Is there usable Python tooling for D-K iteration?** Worth a one-hour spike before deciding to roll your own. Check: `python-control` `mussv` and any synthesis routines, `Skogestad-Python` examples, `cvxpy`-based LMI implementations of the D step. If the answer is "no usable tooling, you have to write D-K iteration yourself around `python-control`'s $H_\infty$ solver," that meaningfully changes the cost-benefit math. If the answer turns out to be "MATLAB has it for free," that's also informative about what to do.
5. **What's your *measurable* evidence that $H_\infty$ is too conservative?** This question can't be answered until you have a working $H_\infty$ controller (so it's gated on §12 items 1–3). Once you do, run it and a hand-tuned aggressive baseline against the same training task. The gap in the highest sustainable $\alpha$ is what μ would close. If there's no gap, μ buys you nothing; don't bother.
6. **(The deepest one.)** **Do you actually want robustness against the worst case, or robustness in expectation?** μ-synthesis (and $H_\infty$) protect against the worst admissible perturbation. *Stochastic* / *risk-sensitive* / *scenario-based* methods protect *expected* performance across a *distribution* of perturbations. The training-time setting is closer to "expected performance over a distribution of training dynamics" than to "worst case across an adversarial perturbation set" — there is no adversary, only stochasticity. If the answer is "expected, not worst-case," then the right framework isn't μ at all — it's something like risk-sensitive MPC, scenario-MPC, or even Bayesian-optimization-based control. **Question 6 is the one I'd put first.** The answer changes the whole framework, not just whether to add μ.

---

## 11. So is the AdaptiveController heuristic actually better than LQR/H∞ here?

Honest answer: **probably yes, today, for a specific reason.** The heuristic is *outcome-driven* (it watches loss) while LQR/H∞ are *model-driven* (they watch a state and trust the model). When the model is wrong in the ways listed in §9, an outcome-driven policy that ramps $\alpha$ down whenever loss starts diverging is *exactly* the right safety net — because divergence is the failure mode you can't afford, and divergence is directly observable in the loss.

The heuristic's weaknesses, in order of severity:

- No formal stability guarantee — if the response is too slow you blow up before it kicks in.
- The increase/decrease rates and `loss_window` are themselves hyperparameters that need tuning.
- No notion of *anticipation* — it only reacts after loss has already started moving. A model-based controller can react to the *state* (weight norm rising) before the loss catches up.
- The recipe "halve $\alpha$ when loss > 2× target, multiply by 0.9 if just over target, multiply by 1.02 if trending down" is essentially a hand-coded P controller on loss, with hysteresis. It works because the underlying problem is shaped right for it, not because there's any optimality argument.

The strongest position is probably **both, layered**: an LQR or $H_\infty$ controller as the inner loop computing the *intended* $\alpha$, and an adaptive override that snaps it down whenever the loss leaves a safety envelope. The model-based controller gets you anticipation and theoretical justification; the adaptive override gets you a hard guard against the bifurcation the model can't see. This is essentially *supervisory control* — old idea, well studied, fits your situation.

The cleanest principled alternative is **MPC with constraints**:

- The state is $\|w_{\text{eph}}\|$ (or 2D: $[\|w_{\text{eph}}\|, \|g\|]$).
- The cost is the LQR cost over a short horizon.
- The *constraint* is "predicted state must stay below the bifurcation threshold for the next $N$ steps."
- At each step, solve a small QP to find the $\alpha$ that minimizes cost subject to the constraint.

This gives you the anticipation of a model-based controller *and* an explicit, unviolable safety constraint, which is what your problem really wants. It is also the framework that lets you encode "don't go off the cliff" directly. The cost is one small QP per step, which for a 1D or 2D state is genuinely cheap.

---

## 12. The honest hierarchy of next moves, ranked

1. **Make $E$ non-zero.** Until your sysid produces a real disturbance gain, every minute spent on $H_\infty$ vs LQR is wasted — they are *literally the same controller*. Either inject controlled gradient-norm perturbations during sysid, or use your unconstrained fit's $\hat E$ and check it's nonzero. Without this, the H∞ track is theatre.
2. **Validate the linear model out of distribution.** Take the fitted $A,B,E$ and predict on a *different* training segment than the one you fit on. If $R^2$ drops a lot, your operating point assumption is broken and any Riccati controller is going to be wrong in ways neither $Q$ nor $R$ tuning can fix. `validate_model` in `plant_model.py` already does the math — just run it on held-out data.
3. **Fix the H∞ inner solve** if you're going to keep that branch alive. Either rewrite as a modified DARE call (clean, correct, generalizes to 2D) or derive the scalar formula carefully and unit-test it against the 1D case where $E\to 0$ should reproduce LQR exactly. Right now your code reproduces LQR exactly *because of a bug*, not because the math says so.
4. **Think about whether MPC is the right framework.** For a 1D state with a hard constraint (don't blow up), MPC is so much closer to what you want that staying in Riccati-land is choosing the wrong tool. The implementation cost is one small QP per step via `cvxpy` or `scipy.optimize`.
5. **Layer the adaptive override regardless.** Whatever model-based controller wins, putting an outcome-driven safety net on top costs nothing and is the only thing that protects you from the modeling errors in §9.
6. **(Deferred.) Quantify $H_\infty$'s conservatism, then consider μ-synthesis.** Only after items 1–3 land, and only if you've decided against MPC at item 4. Step 6a: characterize the empirical range, drift rate, and correlation of $H$ and $\bar g$ from your sysid trace (open questions 1–3 in §10) — this tells you whether the LFT framework is even valid for your system. Step 6b: with the working $H_\infty$ controller, measure the gap between its safest-sustainable $\alpha$ and a hand-tuned baseline's. If that gap is large *and* the parametric perturbations are small enough that the LFT model holds, μ-synthesis (or LMI-based mixed-$H_2/H_\infty$ synthesis) is the principled way to close it. If the gap is small, or the perturbations are too large, skip it. Do **not** start a μ-synthesis branch before items 1–3 — it builds on a broken $H_\infty$ inner solver and will silently inherit the bug.

---

## 13. References for the road

- Doyle, J. C. (1978). **"Guaranteed margins for LQG regulators."** *IEEE TAC* 23(4), 756–757. The one-page paper. Read it once just to enjoy how short it is.
- Zames, G. (1981). **"Feedback and optimal sensitivity..."** *IEEE TAC* 26(2), 301–320. The $H_\infty$ idea.
- Doyle, J. C. (1982). **"Analysis of feedback systems with structured uncertainties."** *IEE Proceedings D* 129(6), 242–250. The original μ paper. Introduces the structured singular value.
- Doyle, Glover, Khargonekar, Francis (1989). **"State-space solutions to standard $H_2$ and $H_\infty$ control problems."** *IEEE TAC* 34(8), 831–847. The DGKF paper. The two Riccati equations.
- Packard & Doyle (1993). **"The complex structured singular value."** *Automatica* 29(1), 71–109. The big survey of μ — properties, computation, why it's NP-hard, what the upper-bound looks like.
- Zhou, Doyle, Glover (1996). **Robust and Optimal Control.** The textbook. Heavy but everything's in there. Chapters 8–11 cover μ-synthesis end to end.
- Skogestad & Postlethwaite (2005). **Multivariable Feedback Control.** Friendlier teaching textbook, opens with classical loop shaping and walks up to $\mu$-synthesis. Chapter 8 ("Robust stability and performance analysis") and chapter 9 ("Controller design") are the relevant ones for μ.
- Boyd, Ghaoui, Feron, Balakrishnan (1994). **Linear Matrix Inequalities in System and Control Theory.** Free PDF online. The LMI bible. Modern way to do mixed $H_2/H_\infty$ design and to encode structured uncertainty without going through D-K.
- Rawlings, Mayne, Diehl (2017). **Model Predictive Control: Theory, Computation, and Design.** Free PDF online. The MPC bible. Read chapters 1, 2, and 3 if you want to know whether MPC fits your problem before committing.
- Balas, Doyle, Glover, Packard, Smith (1998+). **MATLAB μ-Analysis and Synthesis Toolbox** user's guide. Surprisingly good *practical* reference for what D-K iteration looks like in code, even if you end up implementing it elsewhere.

---

## TL;DR

- $H_2$ = average / energy-weighted gain. LQR is its most famous instance.
- $H_\infty$ = worst-case gain at any frequency. Robust to bounded perturbations via small-gain.
- $\mu$-synthesis (§10) = $H_\infty$ refined to respect the *structure* of your uncertainty (real parameters vs unmodeled dynamics vs disturbance), removing the conservatism of treating every perturbation as a full unstructured block.
- Doyle 1978 showed LQG (LQR + Kalman estimator) can have *no* stability margins. This kicked off the modern robust-control field and led to $H_\infty$ → $\mu$-synthesis → LMI → MPC.
- Your code does proper gray-box sysid + Riccati synthesis. It is principled given the model, but the model is a heuristic linearization of a system that bifurcates, drifts, and lives in a higher-dim state space than the scalar $\|w_{\text{eph}}\|$ captures.
- Today, your H∞ controller is numerically equal to your LQR controller for *two separate reasons* (the data has $E=0$, *and* the gain formula in `_solve_hinf` is the LQR formula). Either fixing $E$ or fixing the gain formula is necessary before H∞ buys anything. μ-synthesis builds on $H_\infty$ as its inner solver, so it inherits this bug — fix $H_\infty$ before going anywhere near μ.
- The adaptive heuristic is probably outperforming both right now because it watches the right signal (loss) and reacts before the model-based controllers — which trust the linear model — would notice anything wrong.
- If you want to go further than a heuristic without going further than your modeling can support, the natural next step is **MPC with a hard "don't blow up" constraint**, optionally layered with the adaptive override as a safety net. This is closer to what your problem actually wants than any Riccati method — including μ.
- μ-synthesis is the *right* upgrade *if* you stay in the Riccati family, *if* the linear model proves valid out of distribution, *and if* you've measured a real conservatism gap in your working $H_\infty$ controller. None of those preconditions are met yet, so μ is a deferred move, not a next move. The deepest open question (§10, Q6): do you want worst-case robustness or expected-case robustness? The answer changes the entire framework, not just whether to add μ.
- Not acting on any of this yet — this is a study note. Decide what to ship after thinking about §12 and §6 together, and after answering open questions 1, 2, 3, and 6 from §10.
