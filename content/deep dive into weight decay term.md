---
title: "deep dive into weight decay term"
tags:
- hebbian
- Weight
- Competitive
---
 #hebbian 

the term: ![[List of Hebbian Weight Update Rules#Weight Decay Term Added]]

> The problem with \[the basic Hebbian learning rule\] is that there are no mechanisms to prevent the weights from growing unbounded, thus leading to possible instability. This issue can be counteracted by adding a weight decay term γ(𝐰,𝐱) to the learning rule


The paper doesn't define any specific weight decay term besides the [[List of Hebbian Weight Update Rules#Competitive Learning Rule|Competitive Learning Rule]], but there could be others. 
- L2 Regularization
- L1 Regularization
- Elastic Net Regularization
- Weight Normalization

I'm already doing Weight Normalization, with the L2 norm, here:
![[Current Build of the Memory Encoding Hebbian RNN#^99b36f]]
 However, the Ridge Regression (L2 again) [[decay chat transcript#^4045d3|here]] is typically not applied to the weights by division, but instead as a decay term to the weight update, so like this:
 
$$ \Delta w_i = \eta y x_i - \gamma(\mathbf{w}, \mathbf{x}) $$
$$\gamma(\mathbf{w}, \mathbf{x}) = \gamma(\mathbf{w}) = \lambda \|\mathbf{w}\|^2$$
i guess we are just not caring about $\mathbf{x}$ anymore, which is mentally healthy behavior and should be encouraged.
finally,
$$\Delta w_i = \eta y x_i - \lambda \|\mathbf{w}\|^2$$

, I guess?

determined from [[decay chat transcript]]