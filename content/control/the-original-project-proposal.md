---
title: 'Controlling plasticity: the original project proposal'
publish: true
description: 'The proposal I wrote at the start of the robust control class: treat
  metaparameters as a control problem, because gradient descent is boring and stable
  until you try to metalearn the hyperparameters, and then the gradients go everywhere.'
---

*The project proposal I wrote at the start of the robust control class, kept as-is. It is worth reading against what actually happened.*

**Metaparameters as a Control Problem**
In my experiments, gradient descent, even in a deep neural net and even in a reinforcement learning environment, presents a boring control problem. Pick the right dataset/environment, optimizer, and hyperparameters, and gradient descent happens reliably and stably. However, I try to do something fancy, like metalearning, on those hyperparameters, and the gradients go everywhere. I'd like to approach the management of metaparameters as a robust control problem. 

In python, that will mean creating a new optimizer, with values adjusted based on vanilla SGD, LQR, H-infinity, and mu synthesis approaches in separate experiments. I'll experiment with error signals derived from loss calculations as well as simpler bounds based on known-stable hyperparameter magnitudes. You may ask, what is the measured output y? is it the gradient norm? The learning rate itself? The ratio of consecutive gradient magnitudes? I'll need to test out a few options. 

It's important to note, however, that I don't intend to treat the entire neural net as part of my control system. For simplicity, the control system I create doesn't really care whether the overall loss converges or not, only that its movement is within certain bounds and feedback loops are controlled. Just entirely forget that the neural net is also a model. I want to minimize the gain between incoming gradient signals and final gradient updates, something like an active suspension, except the ground is the loss landscape and the car is our neural net. I will let existing python tools compute the system, but tweak parameters as I see them perform, like adjusting between high- and low-pass filters on signals. 

To get the linearized plant matrices, I'll first need to do some more work on exactly I intend to adjust my metaparameters. If I can't do it analytically, I'm sure I can make some estimate based of a bunch of runs. I'll likely start with a single scalar metalearning rate, and if that works, a individual metalearning rates for each parameter in the NN. Alternatives include hebbian (fire together wire together) style metalearning rules, which are nice because they don't require backpropagation, simplifying the math required.

To start slow and make sure I at least have *something* to show in case the idea is bad, I'll code basic simulations of the cartpole task and active suspension using a variety of models, and include a few visualizations confirming that they work on the toy problems. This serves the dual function of preparing for possible failure while also allowing me to validate that I can get the control systems functioning at all before trying them on a novel problem.
