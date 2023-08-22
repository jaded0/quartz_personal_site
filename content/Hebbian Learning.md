---
title: "Hebbian Learning"
tags:

---
 

It's an alternative to backprop that uses only local update rules. It seems far more similar to spiking neural networks in that it tries to follow a more "fires together, wires together" paradigm. What's really appealing to me about this weight update mechanism is that it feels more online learning-friendly. I've long wondered why we try to represent short-term memory as activations only, when we know that they ought to have a pathway towards being encoded in the weights. 

I think that weight update rules that *never* turn off, even during inference time and in production environments, may be the key to bridging short-term and long-term memory in neural nets. Think, a transformer with no memory limits despite its context length.

I'm aware that this concept has a big history. Biologically-plausible neural net design is a common obsession, but it has mixed results, with current backprop and fully-connected linear networks kinda spitting in its face. So, it seems like a common folly to keep obsessing about trying to get neural nets to behave like my own brain, yet, I can't help but thinking about the local weight update rules in Hebbian learning potentially producing some interesting results in terms of some sort of knowledge retention.
