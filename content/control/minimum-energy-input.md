---
title: What a minimum-energy input actually is, intuitively
created: 2026-06-25
authorship: ai-generated
model: claude-opus-4-8
tags:
- robust-control
- convolution
- minimum-norm
- intuition
publish: true
description: Picture a small electric room heater and a thermometer. Once a minute
  you get to pick how hard to run the heater; call the setting in minute $j$ the input
  $u_j$. The thing you care about is the room's temperature, $y_k$, at minute $k$.
---

> [!note] Drafted with an AI assistant (claude-opus-4-8)
> I wrote this note with model help and then read it, checked the
> math, and kept it because I agree with it. Errors are still mine.

# What are we actually doing?

## The machine

Picture a small electric **room heater** and a thermometer. Once a minute you get to pick how hard to run the heater; call the setting in minute $j$ the input $u_j$. The thing you care about is the room's temperature, $y_k$, at minute $k$.

Heat doesn't act instantly and it lingers. A burst of heat in one minute keeps warming the room for several minutes afterward, fading as it leaks out the walls. The numbers $h_1,h_2,\dots,h_n$ describe exactly that fade:

$$y_k=\sum_{i=1}^n h_i\,u_{k-i}=h_1u_{k-1}+h_2u_{k-2}+\cdots+h_nu_{k-n}.$$

Read it right to left in time: $h_1$ is how much the heat from **1 minute ago** still contributes now, $h_2$ how much from 2 minutes ago, … , $h_n$ from $n$ minutes ago. After $n$ minutes the room has forgotten that burst — the machine has a **memory of $n$ minutes**. (This list $h_1,\dots,h_n$ is the system's *impulse response*: the temperature trace you'd see after one single unit puff of heat.)

## The data

- **Given to you:** the fade profile $h_1,\dots,h_n$ — a fixed property of this room + heater, something you'd measure once. And a **target** temperature $y^*$ you want to reach.
- **Your to choose:** the heating schedule $u_0,u_1,\dots,u_{n-1}$ — the dials, one per minute.

## What $h$ does and doesn't capture

Your two guesses split exactly along the line that defines $h$.

**Heat escaping through the walls — yes, that's $h$.** This is precisely what the decaying profile encodes. $h$ tells you how the heat *from your own heater* spreads out and leaks away over time. If $h_1>h_2>\cdots>h_n$ (fading), then heat you put in early is weighted by a *late, small* coefficient by the time we read minute $n$ — it's mostly gone through the walls. Heat you put in at the last minute ($u_{n-1}$, weight $h_1$) is still fresh and counts most. So your intuition "spend it all early and it leaks out before minute $n$" is exactly right, and it's the reason the optimal schedule pushes hardest in the minutes whose influence $h_{n-j}$ on the final temperature is largest.

**Sun through the window, or a door open for the first 15 minutes — no, that's *not* in $h$.** Those are *disturbances*: things that change the temperature without going through your heater dial. $h$ only ever multiplies *your input* $u$, so it can only describe how the room reacts to **you**. Two reasons they can't live in $h$:

1. **It's not your input.** A disturbance would show up as a separate added term, $y_k=\sum_i h_iu_{k-i}+d_k$, where $d_k$ is the sun/draft. It rides alongside the convolution, not inside it.
2. **$h$ is time-invariant.** "The door is open for the *first 15 minutes*" is tied to the clock, not to when you act. But $h$ gives the *same* response to a heat puff no matter which minute you apply it (that's what LTI — linear time-invariant — means). Anything that depends on absolute time, like a one-time open door, is by definition outside a fixed $h$.

(Disturbances are real and important — rejecting them is much of what robust control is about — but this exercise studies the clean case with none, so we can see the input-shaping idea by itself.)

## The problem (part i)

> Set the room to exactly $y^*$ at minute $n$, using the least total heater effort.

Why minute $n$ specifically? Because minute $n$ is the first time *all and only* your $n$ dials have had a chance to act — see k_vs_n_time_index_vs_system_order. So the single equation tying your choices to the goal is

$$y_n=h_1u_{n-1}+\cdots+h_nu_0=y^*.$$

There are many schedules that hit $y^*$ (one equation, $n$ unknowns — lots of slack). "Least effort" picks among them by minimizing total energy $u_0^2+\cdots+u_{n-1}^2$. That's the **minimum-norm** problem from Chapter 3.

The answer,

$$u^*=\frac{y^*}{\sum_i h_i^2}\,H^T\quad\Longleftrightarrow\quad u_j=\frac{h_{n-j}\,y^*}{\sum_i h_i^2},$$

says something intuitive: **push hardest in the minutes that matter most.** Heat injected in a minute with a big influence $h_{n-j}$ on the final temperature gets a big dial setting; heat that would mostly leak away before minute $n$ gets a small one. Spreading the effort this way — proportional to influence — is exactly what wastes the least energy.

## The relaxed problem (part ii)

Hitting the target *exactly* can be expensive. Maybe being a degree off is fine if it halves the electricity bill. So instead of forcing $y_n=y^*$, we put both concerns in one cost and trade them off:

$$J(u)=\underbrace{r\,(y^*-y_n)^2}_{\text{miss penalty}}+\underbrace{u_0^2+\cdots+u_{n-1}^2}_{\text{energy}}.$$

The knob $r$ is **how much you care about accuracy vs. effort**:

- $r\to 0$: you don't care about temperature at all, so the cheapest thing is to leave the heater off — $u^*=0$.
- $r\to\infty$: missing is unaffordable, so you must hit $y^*$ exactly — and the solution collapses back to the part (i) minimum-energy answer.
- In between, the solution is the same "push proportional to influence" shape, just scaled down a bit — you deliberately undershoot the target to save energy:

$$u^*=\frac{y^*}{\sum_i h_i^2+1/r}\,H^T.$$

Notice it's the part (i) formula with an extra $+1/r$ in the denominator. Small $r$ (cheap to miss) → big $1/r$ → tiny inputs. Large $r$ → $1/r\to0$ → back to part (i). That single term *is* the accuracy-vs-effort dial.

## The confusing step: why fold the error into the unknown?

This is the move that makes part (ii) feel like sleight of hand. Part (i) was a clean *constrained* problem — "minimize energy **subject to** hitting $y^*$ exactly." Part (ii) looks completely different — there's no constraint at all, just one cost $J=r e^2+u^Tu$ to push downhill. So why does the answer key suddenly invent a new variable, stack $\sqrt r\,e$ under $u$, and reuse the part (i) formula? Here's the picture that makes it inevitable.

**Treat the miss as one more dial.** In part (i) the error was *locked at zero* — you had no say in it. In part (ii) you're *allowed* to miss, so think of the miss $e=y^*-y_n$ as one extra knob you get to set, sitting alongside your $n$ real heater dials $u_0,\dots,u_{n-1}$. Like every dial it isn't free: turning the heater dial $u_j$ costs $u_j^2$; "turning the miss dial" to a value $e$ costs $r\,e^2$. Same kind of penalty, just a different price tag.

**The one equation they must jointly obey is a tautology.** Now ask: with $n$ real dials *plus* this one virtual dial, what ties them together? Just the definition of the miss, rearranged:

$$\underbrace{y_n}_{Hu}+\,e=y^*\qquad\Longleftrightarrow\qquad Hu+e=y^*.$$

"What you actually achieve, plus how much you missed by, equals the target." That's not a new physical law — it's true by definition of $e$. But written this way it's a *single linear equation* relating all $n+1$ dials. So part (ii) **is** part (i) — minimize total squared dial-effort subject to one linear constraint — just with one extra (cheap-or-expensive) dial in the lineup. That's the whole reason the part (i) machinery comes back.

**Where the $\sqrt r$ comes from — it's just bookkeeping.** The min-norm formula minimizes a plain sum of squares, $\sum(\text{dial})^2$. For the real dials that's exactly the cost we want, $u_j^2$. But for the miss dial we want the cost to be $r e^2$, not $e^2$. Fix the mismatch by putting the *rescaled* value $\sqrt r\,e$ into the vector instead of $e$: then its squared contribution is $(\sqrt r\,e)^2=r e^2$, exactly the price we meant to charge. That's why the unknown is

$$\tilde u=\begin{bmatrix}u\\\sqrt r\,e\end{bmatrix}\quad\text{with}\quad\|\tilde u\|_2^2=u^Tu+r e^2=J.$$

Having rescaled the dial, you must also rewrite the constraint in terms of it: since the dial now holds $v=\sqrt r\,e$, the actual error is $e=v/\sqrt r$, so the "$+e$" in $Hu+e=y^*$ becomes "$+\tfrac1{\sqrt r}v$." That lone $\tfrac1{\sqrt r}$ is the conversion factor turning the rescaled miss-dial back into real temperature error — and it's the entire reason

$$\tilde H=\begin{bmatrix}H&\tfrac1{\sqrt r}\end{bmatrix},\qquad \tilde H\tilde H^T=\sum_i h_i^2+\tfrac1r.$$

The extra dial contributes its own "influence-squared" $\left(\tfrac1{\sqrt r}\right)^2=\tfrac1r$ to the normalizer — and *that* is precisely the $+1/r$ you saw appear in the denominator. (The answer key calls our $H$ "$A$", the target $y^*$ "$\bar y$", and writes the cost as $\arg\min_u(\|u\|_2^2+r\|e\|_2^2)$ — but it's the identical augmentation; it just states the stacking without saying why it's legal. The "extra dial + tautological constraint" is the why.)

**Sanity check that the dial picture is right.** The miss dial's influence on the target is $\tfrac1{\sqrt r}$, so it competes with the real inputs to "explain" $y^*$:

- *Cheap to miss* (small $r$): the miss dial has a **huge** influence $\tfrac1{\sqrt r}$, so it grabs almost all the job of accounting for the target — barely any work is left for the real inputs. Indeed $u^*\!\to\!0$, and the realized miss $e=\frac{y^*/r}{\sum h_i^2+1/r}\to y^*$: you miss by the whole target (heater off, room stays put). 
- *Expensive to miss* (large $r$): the miss dial's influence $\tfrac1{\sqrt r}\to0$ — it's effectively unavailable, so the real inputs must do everything, recovering the part (i) exact-hit solution and $e\to0$.

So the augmentation isn't a trick pulled from nowhere: it's the statement that *letting yourself miss is just adding one more weighted knob*, and the price of that knob ($r$) sets how much of the target it's willing to absorb.

## Is the realized miss the "biggest miss"?

A natural question: the optimal solution comes with a built-in miss $e=\frac{y^*}{r\sum_i h_i^2+1}$ — is that the *most* you can miss? Two senses, opposite answers.

- **With any input you like — no.** You could overdrive the heater and blow past $y^*$ by any amount; $|e|$ is unbounded. The realized miss is not a ceiling on what's *possible*.
- **Across the optimal solutions as $r$ sweeps — yes.** The optimal miss runs over $(0,\,y^*]$: it's $\to0$ as $r\to\infty$ (perfect hit) and $\to y^*$ as $r\to0$ (output $0$, miss the whole target). So $e=y^*$ is the **worst the optimizer ever does**, hit in the do-nothing limit.

The reason it never does worse: **the optimal output always lands between $0$ and $y^*$ — it undershoots, never overshoots.** Pushing past $y^*$ would cost *extra energy* **and** leave *nonzero error* — both terms of $J$ rise, strictly worse. So the optimizer always stops short, sliding $y_n$ from $0$ (do nothing) toward $y^*$ (exact hit) as $r$ grows, and the miss stays trapped in $[0,y^*]$.

## The big picture

This is the simplest version of a question that runs through all of control: **given a system with memory, what input schedule achieves a goal — and how do you balance hitting the goal against the cost of the effort?** Part (i) is "hit it exactly, cheaply"; part (ii) is "hit it about right, cheaply," which is the realistic version and the seed of regularized / optimal control.
