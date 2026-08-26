---
title: 🪴 jaden lorenc
publish: true
description: Jaden Lorenc's digital garden. PhD student at BYU working on ephemeral
  weights, a way to put a neural network's short-term memory in its parameters instead
  of its activations.
---

I work with the door open. I'll keep putting research tangents and half-finished projects
here, so anyone who wants to work with me has a live transcript to go off of instead of a
resume.

## current status
- PhD student at BYU. My thesis is **ephemeral weights**. Most networks keep short-term
  memory in the activations, a context window or a hidden state. I put it in the weights
  instead. Take a fraction of the parameters, give them a big learning rate and a fast
  decay, and let ordinary backprop write to them at inference time. What you get is a
  rolling record of recent updates that the network can read directly, with no recurrence
  and no context window at all. Here's [the paper](research/ephemeral-weights) and
  [the code](https://github.com/jaded0/memory_encoding).
- Those weights blow up if you push them hard, so I spent a semester asking whether that's
  a control problem. Plasticity is the input, weight norm is the state. It went badly, and
  that's the interesting part: the model-based controllers did *worse than doing nothing*,
  and a dumb heuristic that just watches the loss beat all of them.
  [Here's why](essays/what-control-theory-actually-did).
- Reading toward the dissertation on multi-timescale memory. What a fixed-size state
  should actually store, and why consolidation looks more like computation than storage.
  The [reading list](research/memory-architectures-reading-list) is annotated with what
  each paper is *for*, not just what it says.

## side projects
- I self-host almost everything I use. About twenty services, and the whole thing deploys
  on `git push`.
- Small tools for reading papers on e-ink, because the PDFs are unreadable on a 7 inch
  screen and I got tired of it.

## goals
I want to build models that keep learning after training stops. That's the whole thing.

## talk to me
Email is best: **jaded79@student.byu.edu**. I'm also on
[GitHub](https://github.com/jaded0) and [Lemmy](https://partizle.com/u/jaden).
