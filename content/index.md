---
title: 🪴 jaden lorenc
publish: true
description: I work with the door open. This is the live transcript — research notes,
  build logs, and the occasional finished argument. Much of it is unpolished on purpose.
---

I work with the door open. This is the live transcript — research notes, build logs, and
the occasional finished argument. Much of it is unpolished on purpose.

## what I'm working on

**Ephemeral weights.** My thesis. Most neural networks keep short-term memory in
activations — a context window, a hidden state. I put it in the *weights* instead: designate
a fraction of the parameters as "ephemeral," give them a high learning rate and a fast decay,
and let ordinary backprop write to them at inference time. The result is a rolling record of
recent updates the network can read directly, with no recurrence and no context window.
[The paper](research/ephemeral-weights) and
[the code](https://github.com/jaded0/memory_encoding).

**Controlling plasticity.** Ephemeral weights blow up if you push them hard, so I spent a
semester treating that as a control problem: plasticity as the input, weight norm as the
state, LQR and H∞ against a model-free heuristic. It did not go how I expected —
[the model-based controllers lost to the heuristic](essays/what-control-theory-actually-did),
and understanding why turned out to be the useful part.

**Next.** PhD work on multi-timescale memory — what a fixed-size state should store, and
why consolidation looks more like computation than storage.

## elsewhere

Self-hosting most of my own infrastructure, building small tools for reading papers on
e-ink, and writing the occasional thing about privacy and where the mind stops and the
machine starts — [the Fifth Amendment one](essays/fifth-amendment-and-extensions-of-the-mind)
is the one I'd hand you first.

## reaching me

Email is best: **jaded79@student.byu.edu**. I'm on
[GitHub](https://github.com/jaded0) and [Lemmy](https://partizle.com/u/jaden).
