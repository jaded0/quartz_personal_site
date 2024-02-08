---
title: Denoising Diffusion Probabilistic Models Notes
date: 2023-02-16
---

#cs/advdl 

![[Pasted image 20230216095306.png]]
forward and backward processes are reversed in this picture. The forward proces is actually from right to left.


# algorithms
$q\left(\mathbf{x}_0\right)$  is just the sample from the data distribution.
alpha hat t is really close to 1, and we just multiply it with the image in step 5
e is the noise, so it's small. 
Our network being trained is trying to predict the *noise* instead of the clean image. So when $t$ is big, the network is almost an identity function, just let through the noise. When $t$ is small, it has to eke out the noise that it has. 
Double bars is L2 norm. 
$$
\begin{aligned}
& \hline \text { Algorithm } 1 \text { Training } \\
& \hline \text { 1: } \quad \text { repeat } \\
& \text { 2: } \quad \mathbf{x}_0 \sim q\left(\mathbf{x}_0\right) \\
& \text { 3: } \quad t \sim \text { Uniform }(\{1, \ldots, T\}) \\
& \text { 4: } \quad \boldsymbol{\epsilon} \sim \mathcal{N}(\mathbf{0}, \mathbf{I}) \\
& \text { 5: } \quad \text { Take gradient descent step on } \\
& \quad \quad \nabla_\theta\left\|\boldsymbol{\epsilon}-\boldsymbol{\epsilon}_\theta\left(\sqrt{\bar{\alpha}_t} \mathbf{x}_0+\sqrt{1-\bar{\alpha}_t} \boldsymbol{\epsilon}, t\right)\right\|^2 \\
& \text { 6: until converged }
\end{aligned}
$$


$z$ is gaussian, and turns to zero at penultimate step of diffusion.
4: subtracting off noise, adding other extra noise.
$$
\begin{aligned}
& \text { Algorithm } 2 \text { Sampling } \\
& \hline \text { 1: } \mathbf{x}_T \sim \mathcal{N}(\mathbf{0}, \mathbf{I}) \\
& \text { 2: for } t=T, \ldots, 1 \text { do } \\
& \text { 3: } \quad \mathbf{z} \sim \mathcal{N}(\mathbf{0}, \mathbf{I}) \text { if } t>1, \text { else } \mathbf{z}=\mathbf{0} \\
& \text { 4: } \quad \mathbf{x}_{t-1}=\frac{1}{\sqrt{\alpha_t}}\left(\mathbf{x}_t-\frac{1-\alpha t}{\sqrt{1-\bar{\alpha}_t}} \boldsymbol{\epsilon}_\theta\left(\mathbf{x}_t, t\right)\right)+\sigma_t \mathbf{z} \\
& \text { 5: end for } \\
& \text { 6: return } \mathbf{x}_0
\end{aligned}
$$

# crazy vocab

> optimizing the usual variational bound on negative log likelihood

[[Denoising Diffusion Probabilistic Models#^i4lyzrh1sui|right here]]
???
## jensen's Inequality
If our hard to optimize function is always more than an easier to optimize function, you can use the easier to optimize function. As long as you're trying to maximize it. 
It's a convex/concave thing. Your inequality will always hold if what you need to be convex is convex. 

# markov assumption
[markov assumption](https://en.wikipedia.org/wiki/Causal_Markov_condition)
$p(a,b,c,d)=p(a)\ p(b|a)\ p(c|a,b)\ p(d|a,b,c)$
you can change it up:
$= p(a)\ p(c|d)\ p(c,d)\ p(a|b,c,d)$
so also: $p(b|a)=\frac{p(b)\ p(a|b)}{p(a)}$ 
The **markov assumption** is where you take away the complicated dependencies, making all dependencies a chain. So under the markov assumption, $p(a,b,c,d) = p(a)\ p(b|a)\ p(c|b)\ p(d|c)$, instead. 

[[Denoising Diffusion Probabilistic Models#^i4lyzrh1sui|this]] is done because of the markov assumption. 

[[Denoising Diffusion Probabilistic Models#^xw39thwc9|equation 1]]: $q\left(\mathbf{x}_t \mid \mathbf{x}_{t-1}\right):=\mathcal{N}\left(\mathbf{x}_t ; \sqrt{1-\beta_t} \mathbf{x}_{t-1}, \beta_t \mathbf{I}\right)$ > objective is to learn mu thing and sigma thing.

# getting gaussian
at any t for time, we can get the gaussian for the noise. that's kinda neat.

# equation 5 
first little guy just drops out. the second term added is important.
closed form??
[[Denoising Diffusion Probabilistic Models#^3z3x8ipbs9r|equation 5]]
$\mathbb{E}_q[\underbrace{D_{\mathrm{KL}}\left(q\left(\mathbf{x}_T \mid \mathbf{x}_0\right) \| p\left(\mathbf{x}_T\right)\right)}_{L_T}+\sum_{t>1} \underbrace{D_{\mathrm{KL}}\left(q\left(\mathbf{x}_{t-1} \mid \mathbf{x}_t, \mathbf{x}_0\right) \| p_\theta\left(\mathbf{x}_{t-1} \mid \mathbf{x}_t\right)\right)}_{L_{t-1}} \underbrace{-\log p_\theta\left(\mathbf{x}_0 \mid \mathbf{x}_1\right)}_{L_0}]$
# chatgpt questions

in the following equation, why condition on $x_0$? Training is performed by optimizing the usual variational bound on negative log likelihood: $$ \mathbb{E}\left[-\log p_\theta\left(\mathbf{x}_0\right)\right] \leq \mathbb{E}_q\left[-\log \frac{p_\theta\left(\mathbf{x}_{0: T}\right)}{q\left(\mathbf{x}_{1: T} \mid \mathbf{x}_0\right)}\right]=\mathbb{E}_q\left[-\log p\left(\mathbf{x}_T\right)-\sum_{t \geq 1} \log \frac{p_\theta\left(\mathbf{x}_{t-1} \mid \mathbf{x}_t\right)}{q\left(\mathbf{x}_t \mid \mathbf{x}_{t-1}\right)}\right]=: L $$

The equation conditions on $x_0$ because it represents the initial observation in a time series. The goal of this equation is to optimize the negative log likelihood of the first observation $x_0$ under the probabilistic model $p_\theta$. However, because the model's probability distribution depends on previous observations, the optimization cannot be done directly on $x_0$.