---
title: Control of learning dynamics literature
created: 2026-06-29
authorship: ai-generated
model: openai/gpt-5.5
tags:
- robust-control
- report
- optimization
- dynamical-systems
- learning-rate
- literature
publish: true
description: 'What to cite when you frame learning-rate and plasticity adaptation
  as a control problem: the Lessard/Recht/Packard IQC line, and where fast-weight
  plasticity sits relative to it.'
---

> [!note] Drafted with an AI assistant (openai/gpt-5.5)
> I wrote this note with model help and then read it, checked the
> math, and kept it because I agree with it. Errors are still mine.

# Control of learning dynamics literature

This note fills the §2.2 gap in Report Skeleton: what should be cited when framing fast-weight plasticity control as a control problem over training dynamics.

## Bottom line for the report

There **is** a substantial optimization-as-dynamical-system literature, and some of it is explicitly control-theoretic. The strongest citation is Lessard, Recht & Packard's IQC paper, because it literally casts first-order optimization algorithms as robust-control feedback interconnections. However, that line mostly analyzes or synthesizes *optimization algorithms* under assumptions like smooth strong convexity. It does **not** directly solve this paper's problem: online control of a neural-network plasticity hyperparameter in a nonconvex, time-varying, fast-weight system.

So the right claim is not "nobody has used control for optimization." The right claim is:

> Prior work has used Lyapunov, IQC, and dynamical-systems tools to analyze gradient methods, and separate work has used adaptive/learned controllers for learning-rate schedules. Our setting differs because the controlled input is a fast-weight plasticity parameter inside a live training/inference memory mechanism, and the controlled state is a stability proxy for volatile parameter dynamics rather than the optimizer iterate itself.

## Core citations to use in §2.2

### Optimization algorithms as feedback systems

- **Lessard, Recht & Packard (2016), “Analysis and Design of Optimization Algorithms via Integral Quadratic Constraints.”** [arXiv](https://arxiv.org/abs/1408.3595), [SIAM DOI](https://doi.org/10.1137/15M1009597).  
  **Evidence:** The paper explicitly adapts IQCs from robust control to first-order optimization, casts gradient methods as a known discrete-time linear system in feedback with an uncertain nonlinearity (the gradient map), and uses small SDPs to certify convergence rates and robustness to gradient noise. This is the most on-point robust-control citation.

- **Van Scoy & Lessard (2023), “A Tutorial on a Lyapunov-Based Approach to the Analysis of Iterative Optimization Algorithms.”** [PDF](https://laurentlessard.com/public/cdc23_tutorial/P2.pdf).  
  **Evidence:** A readable tutorial saying iterative gradient algorithms can be viewed as dynamical systems and, more recently, as robust controllers; the gradient is the uncertainty. Useful if the class report needs an accessible bridge rather than only the SIAM paper.

- **Wang & Elia (2011), “A control perspective for centralized and distributed convex optimization.”** [DOI](https://doi.org/10.1109/cdc.2011.6161503).  
  **Evidence:** Earlier control-systems viewpoint on optimization, especially distributed convex optimization. Less directly relevant to neural training, but useful for showing the viewpoint predates the recent IQC revival.

### Lyapunov / dynamical stability of gradient descent and SGD

- **Cohen et al. (2021), “Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability.”** [OpenReview](https://openreview.net/forum?id=jh-rTtvkGeM), [arXiv](https://arxiv.org/abs/2103.00065).  
  **Evidence:** Empirical finding that neural-network GD often trains with the top Hessian eigenvalue near or slightly above the classical quadratic stability threshold, two over step size. This is highly relevant to the “narrow corridor” story: successful training may live near a stability boundary rather than comfortably inside a conservative linear regime.

- **Wu & Su (2023), “The Implicit Regularization of Dynamical Stability in Stochastic Gradient Descent.”** [arXiv](https://arxiv.org/abs/2305.17490).  
  **Evidence:** Studies SGD minima through dynamical stability. A key result: SGD stability imposes constraints involving Hessian trace/Frobenius norm and learning rate, while GD stability constrains the largest Hessian eigenvalue. Useful for connecting learning rate, stability, and implicit regularization.

- **Chemnitz & Engel (2025), “Characterizing Dynamical Stability of Stochastic Gradient Descent in Overparameterized Learning.”** [JMLR](https://www.jmlr.org/papers/v26/24-1547.html).  
  **Evidence:** Introduces a characteristic Lyapunov exponent for SGD near global minima and proves the sign determines whether SGD can accumulate at that minimum. This is current and directly answers the search phrase “Lyapunov stability of SGD.”

- **Orvieto & Lucchi (2019), “Continuous-time Models for Stochastic Optimization Algorithms.”** [NeurIPS](https://proceedings.neurips.cc/paper/2019/hash/9cd78264cf2cd821ba651485c111a29a-Abstract.html).  
  **Evidence:** Builds continuous-time stochastic models for minibatch GD/SVRG and uses Lyapunov analysis plus stochastic calculus. Good background for the broader stochastic-dynamical-systems framing.

### Adaptive learning-rate / step-size control

- **Schaul, Zhang & LeCun (2013), “No More Pesky Learning Rates.”** [PMLR](https://proceedings.mlr.press/v28/schaul13.html).  
  **Evidence:** Automatically adjusts learning rates using local gradient variation; rates can increase or decrease, making it suitable for nonstationary problems. This is close to the “adaptive learning rate” part, but it is optimization-driven, not robust-control synthesis.

- **Daniel, Taylor & Nowozin (2016), “Learning Step Size Controllers for Robust Neural Network Training.”** [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/10187).  
  **Evidence:** Explicitly learns an adaptive controller for NN learning rate from features of the training process. This is probably the closest prior work in *language* to “controller for learning rate,” though it is learned/model-free rather than LQR/$H_\infty$.

- **Baydin et al. (2018), “Online Learning Rate Adaptation with Hypergradient Descent.”** [OpenReview](https://openreview.net/forum?id=BkrsAzWAb).  
  **Evidence:** Updates the learning rate online by differentiating the update rule with respect to the learning rate. Relevant contrast: it controls the learning-rate scalar via a hypergradient, not via plant identification or state feedback.

- **An et al. (2018), “A PID Controller Approach for Stochastic Optimization of Deep Networks.”** [CVPR](https://openaccess.thecvf.com/content_cvpr_2018/html/An_A_PID_Controller_CVPR_2018_paper.html).  
  **Evidence:** Draws an explicit analogy between PID control and stochastic optimization, connecting SGD-momentum to PID-style terms. Relevant as a control metaphor and optimizer design, but not a stability-guaranteed robust-control wrapper around an existing training process.

## How this changes §2.2

Replace the skeleton's “I'm not aware of a body of work...” sentence with something more defensible:

> There is a substantial control-theoretic literature on optimization algorithms as dynamical systems, especially the IQC framework of Lessard, Recht & Packard, Lyapunov-based analyses of first-order methods, and recent work on edge-of-stability behavior in neural-network training. However, most of this literature treats the optimizer itself as the dynamical system to be analyzed or designed. It does not usually treat a neural-network plasticity hyperparameter as an online control input acting on a volatile memory subsystem.

Then split the neighbors into three buckets:

1. **Formal control analysis of optimizers:** IQC/Lyapunov analysis of GD, heavy-ball, Nesterov, noise robustness.
2. **Dynamical stability of neural training:** edge of stability, SGD Lyapunov exponents, learning-rate/stability threshold effects.
3. **Adaptive learning-rate controllers:** Schaul et al., Daniel et al., Baydin et al., PID optimizer papers, plus Adam/RMSProp/AdaGrad as implicit per-parameter gain scheduling.

## Trade-offs / caveats

- **Evidence:** IQC and Lyapunov methods give real certificates, but under stylized function classes. They support the framing but not the final empirical claims of this report.
- **Evidence:** Edge-of-stability work supports the idea that aggressive learning rates near instability can be useful, not merely pathological.
- **Opinion:** This makes the negative result in §8 stronger: the failure is not “control theory is irrelevant,” but “the clean convex/IQC picture is too local and too conservative for this particular fast-weight memory regime.”
- **Opinion:** If this project continues, the most natural bridge from this literature is not classical $H_\infty$ synthesis; it is constrained or supervisory control layered on top of an adaptive schedule, because the practical requirement is “do not cross the cliff,” not “minimize a quadratic norm around one operating point.”

## Suggested citation keys

- `LessardRechtPackard2016IQCOptimization`
- `VanScoyLessard2023LyapunovOptimizationTutorial`
- `WangElia2011ControlPerspectiveOptimization`
- `CohenEtAl2021EdgeOfStability`
- `WuSu2023DynamicalStabilitySGD`
- `ChemnitzEngel2025DynamicalStabilitySGD`
- `OrvietoLucchi2019ContinuousTimeStochasticOptimization`
- `SchaulZhangLeCun2013PeskyLearningRates`
- `DanielTaylorNowozin2016StepSizeControllers`
- `BaydinEtAl2018HypergradientDescent`
- `AnEtAl2018PIDStochasticOptimization`
