---
title: Linearizing the fast-weight update
publish: true
description: 'One sentence: it takes the nonlinear ephemeral-weight update and rewrites
  it in the standard discrete-time LTI "plant" form that LQR / $H_\infty$ / $\mu$-synthesis
  all require as input. Nothing more, nothing less.'
---

## What §6.1 of Report Skeleton is doing

One sentence: it takes the nonlinear ephemeral-weight update and rewrites it in the standard discrete-time LTI "plant" form that LQR / $H_\infty$ / $\mu$-synthesis all require as input. Nothing more, nothing less.

Everything in the section is in service of producing this object:

$$\delta x(t+1) \;=\; A\,\delta x(t) \;+\; B\,\delta u(t) \;+\; E\,\delta d(t)$$

with $A$, $B$, $E$ being real numbers (not matrices — the state is one scalar). Once you have that, the rest of §6 is "pick a controller off the shelf and apply it to this plant."

---

## Step 1 — what we start with

The ephemeral-weight update from §3, with the per-step decay folded in:

$$w_{\text{eph}}(t+1) \;=\; \gamma_0\,\big(w_{\text{eph}}(t) \;-\; \alpha\,g_{\text{raw}}(t)\big)$$

This is **nonlinear** in $\alpha$ and $w_{\text{eph}}$, because $g_{\text{raw}}$ itself depends on $w_{\text{eph}}$ through the loss landscape. You can't hand a nonlinear update to LQR or $H_\infty$ as-is; they only know how to design controllers for linear plants.

## Step 2 — collapse to a scalar state

You don't try to control the full ephemeral-weight tensor. You pick **one number** to call "the state":

$$x \;:=\; \|w_{\text{eph}}\|.$$

That scalar is the only thing the controller will ever see. From here on, "the dynamics" means the dynamics *of that scalar*, not the dynamics of the full tensor or the hidden state or the loss surface.

> [!warning] This is a big modeling commitment
> The state is one number. The model can't represent things like "which direction is the ephemeral-weight vector pointing" or "is the loss landscape curving differently here than at the operating point." When the controller misbehaves later, this is where to look first.

## Step 3 — linearize around an operating point

Pick a nominal point $(\bar x, \alpha_0, \bar g)$ — in practice these are just averages from a real training trace.

> [!info] What "averages from a real training trace" actually means
> §6.2 spells this out concretely. The procedure is:
> 1. Run training as you normally would, **but sweep $\alpha$** (linearly, in steps, whatever — anything that varies the input). If $\alpha$ is held constant, the control channel has no excitation and you can't see how the plant responds to it.
> 2. Log five scalars at every step into a CSV: `x` ($\|w_{\text{eph}}\|$), `g_raw`, `alpha`, `gamma`, `loss`.
> 3. Compute the column means: $\bar x = \overline{\|w_{\text{eph}}\|}$, $\alpha_0 = \overline\alpha$, $\bar g = \overline{g_{\text{raw}}}$. Three numbers, end of identification of the operating point.
>
> Why the **mean** specifically? Linearization is exact at one point and approximate nearby, so you want a point near which the trajectory typically lives. The mean is the natural pick because (a) it minimizes average squared deviation, so by construction the typical $\delta x, \delta u, \delta d$ are small, and (b) if a stable steady state exists, the mean approximates it.
>
> Where this breaks: if training is *drifting* (the mean over the first half of the trace is meaningfully different from the second half), one global mean is fiction — you're Taylor-expanding around a point the system never actually sits at. §8.2 ("the plant coefficient $A$ is time-varying") is exactly this failure mode showing up downstream.

Then define small **deviations** from that point:

- $\delta x \;=\; x - \bar x$  — state deviation
- $\delta u \;=\; \alpha - \alpha_0$  — control deviation (what the controller picks)
- $\delta d \;=\; g_{\text{raw}} - \bar g$  — disturbance deviation (what we can't control)

> [!info] Where do $\delta x$, $\delta u$, $\delta d$ come from at runtime? (Not gradients!)
> Easy to confuse these with gradients because $g_{\text{raw}}$ is a gradient norm, but the $\delta$'s themselves are *just signed differences from the operating point*. At each training step:
>
> - **$\delta x$ is measured.** Read the current weights from the live network, compute $\|w_{\text{eph}}\|$, subtract the precomputed constant $\bar x$. That's $\delta x(t)$.
> - **$\delta u$ is chosen by the controller.** The controller outputs a number, you set $\alpha(t) = \alpha_0 + \delta u(t)$, and you use that $\alpha$ for the actual weight update.
> - **$\delta d$ is observed but uncontrolled.** Compute $g_{\text{raw}}(t) = \|\nabla L\|$ from the actual training step, subtract the precomputed constant $\bar g$.
>
> The only thing in this whole pipeline that's a gradient is $g_{\text{raw}}$ itself (norm of the loss gradient w.r.t. weights, computed via DFA per §3). The $\delta$'s are just $(\text{measured value}) - (\text{operating point})$. No autograd, no chain rule, just subtraction.

A first-order Taylor expansion of the update equation around $(\bar x, \alpha_0, \bar g)$ then gives the standard discrete-time LTI form:

$$\delta x(t+1) \;=\; A\,\delta x(t) \;+\; B\,\delta u(t) \;+\; E\,\delta d(t).$$

The three coefficients are *just the partial derivatives of the update equation evaluated at the operating point*. That's literally all linearization is.

## Step 4 — what each coefficient means physically

**$A$** is $\partial(\text{update})/\partial x$ at the operating point: how a kick to the weight norm propagates one step forward. The "Hessian-like" term $H$ inside $A$ is $\partial g_{\text{raw}}/\partial x$ — i.e. *if the weight norm grows by a little, how much does the gradient norm grow with it?* This is the term that captures the runaway feedback loop: if $H$ is large and positive, $A > 1$, and the open-loop plant is unstable. That's the whole reason this paper exists.

**$B$** is $\partial(\text{update})/\partial \alpha$: sensitivity of the next-step weight norm to the plasticity knob. It's proportional to $\bar g$ because $\alpha$ only matters insofar as there's a gradient for it to multiply — at zero gradient, twiddling $\alpha$ does nothing.

**$E$** is $\partial(\text{update})/\partial g_{\text{raw}}$: sensitivity of the next-step weight norm to a fluctuation in gradient norm. It's proportional to $\alpha_0$ for the symmetric reason — a gradient fluctuation only matters insofar as $\alpha$ is multiplying it.

> [!tip] Why partials?
> Linearization is just first-order Taylor. For any smooth $f(x,u,d)$, near a base point $(\bar x, \bar u, \bar d)$:
> $$f(x,u,d) \approx f(\bar x, \bar u, \bar d) + \tfrac{\partial f}{\partial x}\delta x + \tfrac{\partial f}{\partial u}\delta u + \tfrac{\partial f}{\partial d}\delta d.$$
> Subtract the constant offset (which is $\bar x$ at steady state) and you're left with $\delta x(t+1) = A\delta x + B\delta u + E\delta d$. The "matrices" $A$, $B$, $E$ are *defined* to be those partials. There's no separate identification step in the math — though §6.2 will identify $H$ (the only nontrivial piece) from data.

### Jacobians vs Hessians — where each one shows up

Yes, we are using Jacobians, and the Hessian shows up too, but in a subtler place. Worth being precise about which is which.

**Jacobian.** For a vector-valued function of vector inputs, the Jacobian is the matrix of all first partial derivatives. For our scalar update $f(x, \alpha, g_{\text{raw}})$ with three scalar inputs, the "Jacobian" is just the row of three numbers

$$J \;=\; \begin{bmatrix} \tfrac{\partial f}{\partial x} & \tfrac{\partial f}{\partial \alpha} & \tfrac{\partial f}{\partial g_{\text{raw}}} \end{bmatrix}_* \;=\; \begin{bmatrix} A & B & E \end{bmatrix}.$$

So **$A$, $B$, $E$ literally *are* the Jacobian** of the update map at the operating point — just split into three slots by which input we differentiated with respect to (state, control, disturbance). Step 4 already wrote them as partial derivatives; calling that collection "the Jacobian" is just the linear-algebra name for the same object.

**Hessian.** The Hessian is the matrix of *second* partial derivatives of a scalar function — typically the loss $L(w)$:

$$\nabla^2 L \;=\; \left[\tfrac{\partial^2 L}{\partial w_i \partial w_j}\right]_{ij}.$$

Robust-control papers usually invoke a Hessian for one of two reasons: as the curvature of the loss (governing the dynamics of gradient descent) or as the cost weighting in LQR. Here, **we're not using it for the LQR cost** — $Q$ and $R$ are picked by hand in §6.3.1. The Hessian only enters through the dynamics, and only via a *surrogate*.

That surrogate is the "Hessian-like" term $H = \partial g_{\text{raw}} / \partial x$ inside $A$. It's not the literal Hessian — it's *one scalar* representing how the gradient norm responds to a change in weight norm. But morally it's a second derivative of the loss, because $g_{\text{raw}}$ is itself essentially $\|\nabla L\|$, so $\partial g_{\text{raw}} / \partial w$ is morally $\partial^2 L / \partial w^2$. Collapsed onto our scalar state, this becomes a single number representing an effective curvature eigenvalue along the weight-growth direction.

So the division of labor is:

| Object | Role in §6.1 | Where it lives |
| --- | --- | --- |
| Jacobian of the update | The plant matrices $A$, $B$, $E$ themselves | The structure of the LTI plant |
| Loss Hessian (surrogate $H$) | The curvature term that lives *inside* $A$ | One scalar coefficient buried in $A$ |

The Jacobian determines the *shape* of the controller. The Hessian-surrogate determines whether the open-loop $A$ is bigger or smaller than 1 — i.e., whether you have a runaway problem in the first place. If $H$ is small, $A < 1$, the system is stable on its own and you don't need any of this. If $H$ is large and positive, $A > 1$, the open-loop plant is unstable, and the entire paper is about finding a $K$ that puts it back inside the unit circle.

## Step 5 — why $E$ gets its own letter

This is the conceptual punchline of the section, and the part most likely to feel arbitrary on a first read.

In a vanilla LQR setup you'd just write

$$\delta x(t+1) \;=\; A\,\delta x \;+\; B\,\delta u$$

and any noise gets shoved into a generic "process noise" term that doesn't appear explicitly in the plant. LQR doesn't *care* where the noise comes from — it's solving an average-case problem and just averages it away.

But $H_\infty$ (and $\mu$-synthesis later) is built around a *different* question: **"how much does a disturbance push the state around, in the worst case?"** To even ask that question, you need a separate, named **disturbance channel** in the plant — a place to point at and say "this is the input I'm worst-casing over." Keeping $E$ as its own matrix instead of folding it into $A$ or $B$ is what makes the worst-case-disturbance question expressible at all.

That structural commitment — splitting "what we choose" ($\delta u$, with channel $B$) from "what's done to us" ($\delta d$, with channel $E$) — is what the paper means by **"partitioned generalized plant form"**. It's not an extra theorem, it's a *layout convention* for the plant matrices, and it's the thing that makes §6.3.2 ($H_\infty$ controller) and §9.1 ($\mu$-synthesis) even possible to write down.

So §6.1 is doing two things at once:
1. Producing the simplest plant that captures the runaway dynamics ($A$ encoding the feedback loop).
2. Writing it in the *shape* that the later $H_\infty$ / $\mu$-synthesis machinery requires (separate $E$ channel).

---

## Slide view: what we're modeling and what we're sacrificing

If §6.1 had to be one slide titled "what's in this model and what's not," it would look like this.

**What we keep ✓**

- The runaway feedback loop. The single load-bearing physics of the section is captured in $H = \partial g_{\text{raw}}/\partial x$, the term that says "gradient norm grows with weight norm." Without that, there's no instability and no need for control.
- A control channel ($\alpha$ via $B$) and a disturbance channel ($g_{\text{raw}}$ via $E$), separated, in the partitioned-plant form $H_\infty$ needs.
- Discrete-time dynamics matched one-for-one to the training step.

**What we sacrifice ✗**

1. **Vector → scalar.** The full ephemeral-weight tensor (~10% of millions of parameters) becomes one number, $\|w_{\text{eph}}\|$. We lose all directional information, all per-weight detail, and the entire question of *which* weights are doing the memorization. (This shows up in §8.3: the thing we actually care about — accuracy — is not monotone in $\|w_{\text{eph}}\|$.)
2. **Nonlinear → linear.** Only valid in a small neighborhood of the operating point. The instant the trajectory wanders out of that neighborhood, $A$, $B$, $E$ are wrong and the controller is solving the wrong problem. (§8.1: linearization doesn't survive the bifurcation.)
3. **Time-varying → time-invariant.** $A$, $B$, $E$ are identified once and frozen for the whole training run. The real loss landscape morphs as training progresses, so the *true* $A$ drifts; we don't track it. (§8.2: $A$ is time-varying.)
4. **Tensor-valued curvature → one scalar $H$.** The actual loss Hessian is a giant matrix with rich structure (eigenvalues, anisotropy, alignment with the gradient). We replace it with one number that represents an "effective" coupling along the weight-growth direction.
5. **Online identification → offline.** We sysid once on a separate trace and then deploy the result. There's no adaptive update of the plant, even though the adaptive controller (§6.3.3) adapts the *gain*.
6. **Operating point as a fiction.** We pretend a stable operating point exists by averaging over a trace. Real training has no fixed point — the mean is a least-squares convenience, not a steady state.
7. **DFA gradients, not true gradients.** $g_{\text{raw}}$ is computed via Direct Feedback Alignment (§3.1), not full backprop. So even calling $H$ a "Hessian-like" coupling is generous — it's the response of a *DFA-flavored* gradient norm to weight norm, which is yet another step removed from $\nabla^2 L$.

The paper's bet is that even with all these shortcuts, the resulting plant is rich enough to support a controller that beats hand-tuning on at least *some* operating regime. §8 is the honest accounting of which shortcuts hurt and how much.

## Quick & dirty: what to measure before doing a full sysid run

The minimum viable sysid procedure, in order of effort:

1. **Three column means.** Run training once with $\alpha$ swept (anything non-constant). Log $\|w_{\text{eph}}\|$, $g_{\text{raw}}$, $\alpha$ at every step. Compute $\bar x$, $\alpha_0$, $\bar g$. That's the entire operating point — three numbers.
2. **$B$ and $E$ for free.** Plug straight into the analytical formulas — no fitting needed. They depend only on $\bar g$, $\alpha_0$, and the known $\gamma_0$. Done.
3. **One-parameter fit for $A$.** Compute the residual $r(t) = \delta x(t+1) - B\,\delta u(t) - E\,\delta d(t)$ and run a 1-D least squares against $\delta x(t)$ to recover $A$. One scalar regression on the residuals.
4. **Sanity check (gray-box vs black-box).** Also fit all three coefficients with an unconstrained 3-parameter least squares. If the gray-box $A$ matches the black-box $A$ and the black-box $B, E$ are close to the analytical values, the structural assumption is consistent with the data. If they're wildly off, the linearization is not capturing what's happening.

**Even quicker — the one-second sniff test.** Compute $|A|$. If $|A| < 1$ the open-loop plant is stable on its own and you don't need a controller — just leave $\alpha$ alone. If $|A| > 1$ you have a runaway problem and the rest of §6 is justified. This is the only number you need to look at before deciding whether the project is real.

**What you can also peek at without much work:**

- **Std dev of $g_{\text{raw}}$.** Tells you how big the disturbance signal is in absolute terms — gives you a sense of how much $E\,\delta d$ will push the state around even with a perfect controller.
- **Std dev of $x$ across the trace.** If this is comparable to $\bar x$ itself, the trajectory wanders far from any single operating point and the linearization is on thin ice from the start.
- **First-half mean vs second-half mean.** If they disagree by more than a few percent, the system is drifting and you should expect the time-invariant assumption (and therefore $A$) to fail.

The whole gray-box trick is what makes the "quick & dirty" so quick: by committing to the analytical structure, you reduce identification from "fit a 3-parameter LTI model" to "estimate one scalar." Everything else falls out of formulas you already wrote down in Step 4.

---

## Notation conflict on $\gamma_0$ — checked against the code

The draft writes:

$$A \;=\; (1-\gamma_0)(1+\alpha_0 H), \qquad B \;=\; (1-\gamma_0)\,\bar g, \qquad E \;=\; (1-\gamma_0)\,\alpha_0.$$

I checked these against `plant_model.py` and `hebbian_model.py`. Here's what's actually going on.

**The code's convention.** In `hebbian_model.py:228` the per-step decay is implemented as

```python
self.candidate_weights.data = self.candidate_weights.data * (1 - self.forgetting_factor)
```

so `forgetting_factor` is the **decay fraction** (the part you lose), and `1 - forgetting_factor` is the retention. With the default `forget_rate=0.7`, only 30% of the weight survives each step. (The `run_palindrome_*` scripts override this to `GAMMA=0.01`, so retention is 0.99 — the *value* is wildly different across experiments, but the convention is the same.)

In `plant_model.py:19` this is bound directly: `gamma0 = config["forget_rate"]`, and the docstring (lines 12–15) gives

```
A = (1-γ)(1 + α₀·H)
B = (1-γ)·ḡ
E = (1-γ)·α₀
```

verbatim — and `estimate_plant_analytical` uses these formulas literally. So **the §6.1 closed-form line is consistent with the code**: $\gamma_0$ in the formula is the *decay* rate, and $(1-\gamma_0)$ is the retention factor that actually multiplies the weight.

**Where the paper contradicts itself.** The convention $\gamma_0 =$ decay only works if you read it consistently. But:

1. **§3.2** writes the decay step as $w_k^{\text{fast}}(t+1) \leftarrow \gamma\,w_k^{\text{fast}}(t+1)$ with $\gamma_0 = 0.7$ "as the nominal forgetting coefficient." Here $\gamma$ is *multiplied into* the weight, which makes $\gamma$ the **retention** factor, not the decay. With $\gamma_0 = 0.7$ this update would retain 70% per step, but the code with `forget_rate=0.7` retains 30%. So §3.2's update equation and the code's behavior **do not agree** at all — same number, opposite meaning.
2. **§6.1's update equation** $w_{\text{eph}}(t+1) = \gamma_0(w_{\text{eph}}(t) - \alpha\,g_{\text{raw}}(t))$ has $\gamma_0$ outside the parentheses as a *multiplier* on the post-gradient weight, which again only makes sense if $\gamma_0$ is the retention.
3. **§6.1's closed-form line** uses $(1-\gamma_0)$ as the retention (so $\gamma_0$ is the decay).

So §6.1 swaps conventions on $\gamma_0$ in consecutive lines: the update equation treats $\gamma_0$ as retention, and the formulas immediately below treat $\gamma_0$ as decay. That's the contradiction. (§3.2 sides with the update equation; the code sides with the closed-form.)

> [!note] Concretely, what to fix in the draft
> The cleanest fix is to flip §3.2 and §6.1's update equation to match the code, since the code and the closed-form are the load-bearing pieces:
> - §3.2 should read $w_k^{\text{fast}}(t+1) \leftarrow (1-\gamma)\,w_k^{\text{fast}}(t+1)$ with $\gamma_0 = 0.7$ as the **decay rate** (and explicitly note that $1-\gamma_0 = 0.3$ is the per-step retention).
> - §6.1's update equation should read $w_{\text{eph}}(t+1) = (1-\gamma_0)(w_{\text{eph}}(t) - \alpha\,g_{\text{raw}}(t))$.
> - The closed-form line and the notation table can stay as-is.
>
> Alternatively, rename the symbol in one place — call the decay $\gamma_0$ and the retention something like $\rho_0 = 1-\gamma_0$, and use $\rho_0$ in all the multiplicative updates and formulas. Either fix kills the ambiguity; the current draft has it both ways within a single section.

> [!warning] My earlier note about missing minus signs on $B$ and $E$ was wrong
> If you naively differentiate $f(x,\alpha,g) = (1-\gamma_0)(x - \alpha g)$ at the operating point you get $B = -(1-\gamma_0)\bar g$ and $E = -(1-\gamma_0)\alpha_0$ — negative. The code uses positive $B$ and $E$, which match the empirical dynamics: in the runaway regime, increasing $\alpha$ or $g_{\text{raw}}$ *grows* $\|w_{\text{eph}}\|$ on the next step. The reconciliation is that the linearization is for the dynamics of $\|w_{\text{eph}}\|$ (a norm), not for $w_{\text{eph}}$ itself, and $\|w - \alpha\nabla L\|$ does not factor as $\|w\| - \alpha\|\nabla L\|$ except in degenerate alignment cases. The paper hand-waves past this — the closed-form formulas are *postulated* in a structure that matches the empirical signs, not derived by symbolic differentiation of the literal $f(x,\alpha,g)$ written one line above. **This is a separate gap in §6.1 worth flagging in the draft**: the step from the vector update to the scalar formulas is not actually shown, and the signs only work because of an implicit assumption about how $\nabla L$ aligns with $w$ in the runaway regime. A careful reader will trip on this.

---

## Blackboard version

$$w_{\text{eph}}(t+1) = \gamma_0(w_{\text{eph}}(t) - \alpha\,g_{\text{raw}}(t))$$

$$x = \|w_{\text{eph}}\|, \qquad \delta x = x - \bar x, \quad \delta u = \alpha - \alpha_0, \quad \delta d = g_{\text{raw}} - \bar g$$

$$\delta x(t+1) = A\,\delta x(t) + B\,\delta u(t) + E\,\delta d(t)$$

$$A = \tfrac{\partial f}{\partial x}\Big|_*, \quad B = \tfrac{\partial f}{\partial \alpha}\Big|_*, \quad E = \tfrac{\partial f}{\partial g_{\text{raw}}}\Big|_*$$

$$A = (1-\gamma_0)(1 + \alpha_0 H), \quad B = (1-\gamma_0)\,\bar g, \quad E = (1-\gamma_0)\,\alpha_0 \qquad [\gamma_0 \text{ is the decay; retention is } 1-\gamma_0]$$
