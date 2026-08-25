---
title: 'Ephemeral Weights: Memory Encoding in Neural Network Parameters'
author: Jaden Lorenc
source: https://github.com/jaded0/memory_encoding
tags:
- paper
- neural-networks
- memory
- plasticity
- ephemeral-weights
publish: true
description: Error computation and backpropagation can be repurposed for use as short-term
  memory. In most artificial neural network (ANN) designs, the backward step updates
  only the slowly changing parameters of the network, while the forward step com…
---

## Abstract

Error computation and backpropagation can be repurposed for use as short-term memory. In most artificial neural network (ANN) designs, the backward step updates only the slowly changing parameters of the network, while the forward step computes only the ephemeral activations of the network thus providing the only viable mechanism for short-term memory. However, the backward pass can do it, too; a few weights with quickly decaying values and high learning rates can store short-term memory in the parameters themselves of an ANN via the standard loss calculation and backpropagation gradient calculation. Drawing on the biological principles of synaptic facilitation and long-term potentiation, we designate a fraction of the model's weights as "ephemeral weights," endowed with larger learning rates and decay, to enable swift adaptation and to prevent instability. The result is a constantly updating record of recent neural updates that are directly accessible to the network, negating the need for rolling context windows or recurrent connections. We demonstrate this approach functioning on progressively complex character-level sequence prediction tasks without explicitly passing any information forward. We establish that continuous state information can be propagated solely through parameter updates, allowing the existing weight update mechanism to encode short-term information where previously, only long-term information could be stored. Just as basic biological neural networks are capable of retaining information on various timescales, groundwork is laid for ANNs to also have the variety of memory mechanisms needed for continuous lifelong learning.

**Keywords:** neural networks, memory mechanisms, synaptic plasticity, recurrent networks, parameter adaptation, fast weights

# Introduction

While it is typical to consider the loss function and backpropagation as distinct from the forward pass components of an artificial neural net, it may be constructive to consider their permanent inclusion in the structure of the model, to be used even at inference-time. Error computation and backpropagation can be repurposed for use as a form of short-term memory, even to the point of replacing the connection between sequential forward passes of most modern AI architectures, such as the hidden connection present in the simple recurrent neural network (RNN) or the context window of a Transformer at inference time. To do so necessitates varying degrees of plasticity among the parameters of the neural network, so that long-term gradient descent can continue to improve the overall performance of the model, while faster-changing parameters grant the ability to encode short-term information. A simple way to do this is by designating a fraction of the parameters Ephemeral Weights, and giving them a larger learning rate. They also need a rate of decay in order to prevent gradient instability and eventual explosion. The result is a constantly updating record of recent gradient updates received from the loss function, directly accessible to the weights of the model. This creates a self-organizing memory system where parameter dynamics naturally cluster into distinct functional regimes.

Although transformer-based, leading architectures can simulate temporal learning via the use of context windows and attention mechanisms, this requires redundant processing of each token multiple times, contributing to the heavy energy cost of modern LLMs while failing to truly learn in the way that the model did during pretraining. The purpose of this paper is to establish that there exists a more gradual transition from manually stored memory to parameter-based memory, and that such a transition may allow us to relax our dependence on more expensive techniques.

The contributions of this paper are:

- We present the ephemeral weights mechanism, which enables temporal learning by encoding short-term knowledge directly within the weight values of a neural network.
- We demonstrate via two character-retrieval tasks that ephemeral weights can enable memory functions **without** recurrent connections.
- We provide mechanistic insight into the volatility dynamics of ephemeral weight networks.
- We show that dual-timescale learning is achieved, with weights of differing plasticity performing in tandem as demonstrated by gradient norm analysis.
- We present a comprehensive analysis of implementation requirements including gradient propagation methods, batching constraints, and stabilization strategies essential for practical experimentation.

# Related Works

Existing techniques encode memory either in activations (context windows, recurrent connections, external memory modules) or in parameters (pretraining, fine-tuning, hypernetworks, fast weights).

## Activation-Based Memory Mechanisms

While we focus on techniques that unify the training and inference phases of AI development, the mainstream AI industry often approaches these challenges from the opposite direction, excluding training loop components to preserve inference-time compute. Attention mechanisms preserve all information and perform expensive relevance computations. Retrieval-augmented generation addresses limitations in context window capacity by retrieving external information, but fails to fully incorporate that information. Recent state-space models like Mamba attempt to address these limitations but create lossy representations of context. RWKV aims to apply attention-like mechanisms to true RNNs but still faces long-term dependency challenges similar to LSTM, GRU, and vanilla RNN architectures, causing generated outputs to easily veer from context.

## Parameter-Based Adaptation

In modern continual and online learning, models must adapt to new data without forgetting previous knowledge—a capability that standard neural networks struggle with due to the rigid training/inference paradigm. Fine-tuning serves as a workaround for the constraints of static, non-learning models, but continual usage of it leads to catastrophic forgetting. A common approach is experience replay, where past experiences are stored and periodically revisited. Popularized by Mnih et al. in deep Q-networks, replay buffers stabilize training and improve data efficiency by breaking temporal correlations in online data.

### External Memory Architectures

Some approaches augment neural networks with explicit memory structures. Neural Turing Machines pair a neural controller with a read-write memory matrix, allowing networks to store and retrieve information over extended sequences. Subsequent variants like the Differentiable Neural Computer refined these mechanisms but both still struggle with consistency and scalability over very long sequences.

### Dynamic Parameter Adaptation and Fast Weights

Techniques like fast weights, hypernetworks, and differentiable plasticity allow certain parameters to update rapidly in response to new inputs or tasks, adding a form of in-network memory stored in temporary weight changes.

Fast weights have a long history in neural network research, dating back to Hinton (1987), who described a dual weight architecture where each weight is mirrored by one with a higher learning rate that decays toward zero. Schmidhuber (1992) further developed this concept, drawing inspiration from biological short-term synaptic plasticity. Rather than being components of every weight, our approach differentiates itself by designating only a fraction of weights as much more highly plastic, seeking to explicitly encode short-term information rather than deblur features for typical learning.

Miconi (2018) implemented differentiable Hebbian plasticity, where each synapse has a plastic component adjusted with a Hebb rule during forward passes, with the *degree* of plasticity learned through gradient descent.

Hypernetworks extend this idea by using one neural network to generate the weights of another. Fast Weight Programmers (FWP) apply this concept to compute weight changes at each step. Ephemeral weights do not add the additional complexity that FWPs do, encoding both fast and slow weights in the same backward pass.

MAML (Finn et al., 2017) created a meta-learning approach to train models that can be quickly fine-tuned with a few gradient steps on a new task.

Interestingly, multi-head attention can itself be viewed as a special case of fast weight programming. In attention, the fast weights are effectively the key-value associations—an ephemeral weight matrix computed on the fly for each sequence of queries.

# Methods

## Biological Inspiration

Our approach draws inspiration from biological mechanisms of synaptic plasticity, particularly Long-Term Potentiation (LTP). In biological neural networks, LTP induces a temporary strengthening of synapses that lasts approximately 2-3 hours in the first phase and from several hours to weeks in the second phase, operating on a timescale between immediate neural firing and permanent structural changes.

## Model Architecture and Implementation

Our experimental setup compares a traditional RNN with a novel model using ephemeral weights to store short-term memory. Both networks are character-level predictors trained on synthetic datasets designed to test memory capabilities.

### Baseline RNN Model

The baseline is a standard RNN with a 3-layer architecture:

$$h_t = \text{ReLU}(W_{xh}x_t + W_{hh}h_{t-1} + b_h)$$
$$y_t = \text{softmax}(W_{hy}h_t + b_y)$$

Each hidden layer contains 256 units.

### Ephemeral Weights Model

Our proposed model eliminates the recurrent connection ($W_{hh}h_{t-1}$) entirely:

$$h_t = \text{ReLU}(W_{xh}x_t + b_h)$$
$$y_t = \text{softmax}(W_{hy}h_t + b_y)$$

Unlike traditional neural networks where parameters are fixed during inference, our model continues to update parameters even during evaluation.

## Ephemeral Weights Mechanism

Each weight $w_k$ is paired with a plasticity parameter $\alpha_k$:

1. **Slow weights** ($\alpha_k = 1$): Standard parameters that learn long-term patterns
2. **Ephemeral weights** ($\alpha_k = 10^4$ or $10^5$): Highly plastic parameters that rapidly encode recent information

We randomly designate approximately 10% of the total parameters as ephemeral weights, excluding the final output layer. The weight update rule:

$$w_k(t+1) = w_k(t) - \alpha_k \cdot \nabla_k L(t)$$

For ephemeral weights using Direct Feedback Alignment (DFA), $\nabla_k L(t)$ represents the feedback signal computed via fixed random projection matrices rather than the true backpropagated gradient. DFA's fixed random feedback weights provide a stable gradient signal regardless of the volatile state of the high-plasticity parameters.

## Forgetting Rate Mechanism

$$w_k^{\text{fast}}(t+1) = \gamma \cdot w_k^{\text{fast}}(t+1)$$

Where $\gamma = 0.7$ is the forgetting rate coefficient applied after each standard update.

## Training Procedure

Networks are trained using cross-entropy loss. Both models use simple SGD. Learning rate is typically $1 \times 10^{-4}$.

During both training and inference, the Ephemeral Weights model computes gradients and updates parameters after every character prediction. Traditional batching approaches fail with ephemeral weights because they cause working memory to be shared across different sequence instances.

# Experiments

## Key-Recall

A synthetic dataset for single character retrieval. The sequence contains '?' indicating the next input contains a value to be stored, and '!' requests the stored value:

```
0000?10!1
00000?200!2
00?,00!,
```

Despite higher loss, ephemeral weights achieves full accuracy in fewer steps than the baseline RNN at the same learning rate.

## Reversed Sequence

Random-character palindromes test more complex memory operations:

```
abcba
12321
qwerttrewq
```

This task requires both memory storage and transformation capabilities.

## Preservation of Long-Term Learning

Gradient norms for high-plasticity and low-plasticity weights remain highly distinct throughout training, indicating separate dynamic regimes. The steady decrease in loss suggests the model continues to learn long-term patterns while managing working memory.

## Volatility Emergence and Gradient Explosion

The ephemeral weights mechanism exhibits characteristic volatility patterns closely resembling exploding gradient phenomena. Instability stems from positive feedback in the update rule: as parameter magnitudes increase, the induced gradients scale up, amplifying subsequent updates.

Traditional stabilization techniques are ineffective:
- **Gradient clipping** fails because memory encoding depends on occasional large gradient magnitudes
- **Batch/layer normalization** actively harm performance by normalizing away the extreme bimodal gradient distribution

There is a corridor of effective parameter values. The linear interaction of base learning rate and high-plasticity learning rate determines both performance and stability outcomes.

# Discussion

## Ephemeral Weights as Functional Working Memory

Ephemeral weights successfully encode functional working memory without explicit gatekeeping mechanisms. The gradient explosion patterns that threaten stability are not merely implementation artifacts but fundamental consequences of the memory encoding mechanism.

## Toward a Multi-Scale Memory Pipeline

We envision a biologically-inspired memory architecture across multiple timescales: context windows for immediate access, recurrent connections for short-term rehearsal, high-plasticity weights for rapid encoding, medium-plasticity weights for intermediate storage, and low-plasticity weights for long-term consolidation.

## Future Work

- Dynamic plasticity values via a metalearning outer loop
- Biologically-inspired learning rules (Hebbian plasticity) to stabilize volatile learning
- More rigorous examination of dynamics between forgetting rate, ephemeral/slow weight ratio, plasticity, and base learning rate
- Sinusoidal plasticity values (akin to transformers' positional encodings but changing across time)

# Conclusion

This paper demonstrates that short-term memory in neural networks can be effectively stored in rapidly adapting parameters, without relying on traditional recurrent connections. Ephemeral weights represent a middle ground based on biological plasticity, where information storage exists on a continuum of timescales rather than a binary distinction between training and inference.

## Backlinks

- index
- 2026-08-19
