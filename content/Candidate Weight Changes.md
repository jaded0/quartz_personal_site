---
title: "Candidate Weight Changes"
tags:
- hebbian
---
 #hebbian 

[[2024-01-30]]

My loss graph looks wild:
![[files/W&BChart1_30_202485501AM.png]]
[Weights & Biases](https://wandb.ai/jadens_team/hebby/runs/qmezepr7?workspace=user-jaden-lorenc)
I attribute the wave pattern to the self-reinforcing [[Hebbian Learning|weight updates]] improving performance quickly when they've found something right, then rapidly diverging because of biases inherent in that pattern being magnified and getting out of control. Unfortunately, it's like it's rewarding extreme-ness too much.

Maybe my training pattern is wavy because the training process doesn't actually check if a change is effective before making an edit to the weights. A solution could be to create another set of parameters which represent candidate changes, and my imprint only adds to it. Those candidate parameters, with the same shape as the weights of the network, are just added onto them during a run when activations are calculated. Crucially, they're not modifying the weights, yet. Only after we have a reward signal based on the weights+candidate do we add the candidate to the value of the weights as a long-term change, modulated by the reward. Then, we wipe the candidate parameter. 

Alternatively, we could just divide the candidate parameter by two or something. When the imprint (activationXactivation) is added to it, the candidate weight change gets a sort of long tail of evaluation. 

The benefit of all this is that a weight change is only applied if it's actually improving the reward. The long tail ought to only help that by requiring it to improve the reward over many iterations.
