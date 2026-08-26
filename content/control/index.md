---
title: Control
publish: true
description: A semester spent treating neural network plasticity as a control problem
  — the derivations, the controllers, and why the model-based ones lost.
---

Ephemeral weights blow up if you push them hard. I spent a semester asking whether that's a
control problem: plasticity as the input, weight norm as the state.

These are the working notes — the derivation from the nonlinear update down to a scalar
plant, the controllers built on top of it, and the background reading. The short version of
how it turned out is in [what control theory actually did](../essays/what-control-theory-actually-did).
