---
title: Do language models need sleep? (notes)
publish: true
description: Straight up just a looped language model except it's also consolidating
  memory in fast weights during the loop. They're surprisingly unspecific about the
  actual weight update rule. They mostly care about the combination of broader ideas,
  h…
---

Straight up just a looped language model except it's also consolidating memory in fast weights during the loop. 
They're surprisingly unspecific about the actual weight update rule. They mostly care about the combination of broader ideas, here. 

The most interesting thing about this paper is the reframing of encoding as computation. Consolidation. The choice, in itself, to use a benchmark task that requires N steps that are more than the layers of the model is deep, implies that the encoding step is not there for simple storage, but rather to compute the expected answer first. It makes sense from a theory perspective, there's a good 3b1b video on it, too. Basically, a neural net is nothing but a powerful compression. To store info efficiently you compress it. There's probably a good way to formalize this connection. 

The efficiency of this approach is somehow worse than BPTT, but at least it's not MAML, with its outer loop. Every intermediate activation of the state S must be stored in training. Miserable.

The paper is a fantastic starting point into the space, though, connecting to fast weights, Mamba, SSMs, looped language models, it's awesome. I need to read all around it. I've been meaning to understand Mamba properly for years, now, and it appears that the approach is now used in major LLMs. Very validating, bc it was somewhat niche when I first fixated on it. 

If I understand correctly, the major difference between my thing and what they're doing is the actual weight update rule. I'm very curious to see what they do, specifically, in the related research, since this paper clearly just wanted to hand-wave it away. I'm personally interested in an approach that unifies fast weight update mechanisms *and* classic training weight updates (backprop) via some minimal mechanism or even just sliding value. I wanna get into the weeds of the weight update and then bitter lesson my way outta there, basically. 

I still need to dig more into results, too. So that's two things. Weight update and results.

## Backlinks

- 2026-06-01
- 2026-06-17
- 2026-07-13
- 2026-07-22
- 2026-08-19
