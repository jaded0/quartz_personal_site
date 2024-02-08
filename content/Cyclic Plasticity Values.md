---
title: "Cyclic Plasticity Values"
tags:
- hebbian
- ideas
---

 #hebbian #ideas 

Inspired by a youtube video by Artem Kirsanov (I think it might be [this one](https://youtu.be/iV-EMA5g288?si=RJ7I36tyjFiU4YC2)), which describes how biological neurons have a 6hr period of varying plasticity, and each might be most plastic at a different time than the rest. It's thought to drive sparsity, and distributed representations in the brain. 

Another parameter for each weight, determining its plasticity, a value between 0 and 1 that multiplies with any weight update directed toward the weight. Perhaps there's a set of parameters that just determine different aspects of the sine wave, like so:

$$ y = A \sin(B(x - C)) + D $$

Where:
- $A$ is the **Amplitude**, affecting vertical stretching.
- $B$ influences the **Frequency**, impacting horizontal stretching.
- $C$ is the **Phase Shift**, moving the wave horizontally.
- $D$ represents the **Vertical Shift**, moving the wave vertically.

These parameters could likely be meta-learned, like in [[zotero_notes/hebbian/meta-learning-through-hebbian-plasticity-KG2BPTBB|meta-learning-through-hebbian-plasticity]]. Actually, the idea in that paper closely resembles this one. 