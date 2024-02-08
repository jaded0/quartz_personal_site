---
title: "HPCA Deets"
tags:
- hebbian
- phd
---
#hebbian #phd  
[[2024-02-07]]

An extension to [[Ojas Rule]], pulling the principle of extracting the main direction from the data, out into the space for more than just one neuron at a time. Basically performing a sort of principal component analysis among all neurons in the layer. 
[[PCA]] is a similar concept, basically wanting to find the main concepts that represent the original data. HPCA is basically asking the weight vector to change in such a way that improves the whole layer's ability to reconstruct the inputs if it were needed. 

Here's the equation:
![[List of Hebbian Weight Update Rules#HPCA]]

And the accompanying Lagani paper intuition:
![[zotero_notes/hebbian/hebbian-semi-supervised-in-sample-efficent-annotes-ECAMC5NF#^85af19|hebbian-semi-supervised-in-sample-efficent-annotes-ECAMC5NF]]

[[zotero_notes/hebbian/Survey-of-Hebbian-Learning-Lagani-2023-CF4RA22D#^0c21e9|more Lagani intuition]]

It's pretty competitive vs [[Variational Autoencoder|VAEs]] and [[partial derivative and backprop|backprop]], when the availability of labeled samples is below 10% (I assume of the available samples).

Pooling layers are [[zotero_notes/hebbian/hebbian-semi-supervised-in-sample-efficent-annotes-ECAMC5NF#^a1899a|crucial]] to its performance, interestingly enough.
# chat breakdown

The HPCA (Hebbian Principal Component Analysis) learning rule is given by:

$$
\Delta \mathbf{w}_i = \eta y_i \left( \mathbf{x} - \sum_{j=1}^{i} y_j \mathbf{w}_j \right)
$$

In this rule:

- $\Delta \mathbf{w}_i$ is the change in the weight vector of the $i^{th}$ neuron.
- $\eta$ is the learning rate.
- $y_i$ is the output of the $i^{th}$ neuron.
- $\mathbf{x}$ is the input vector.
- $\sum_{j=1}^{i} y_j \mathbf{w}_j$ is the subtracted summation term, which represents the reconstruction of the input vector up to the $i^{th}$ component.

In traditional Hebbian learning, the rule is often expressed as "cells that fire together wire together," implying that the synaptic weight is increased when both the presynaptic and postsynaptic neurons are active. A common extension to this rule includes a decay term to prevent unbounded growth of the weights.

In HPCA, the subtracted summation term $\sum_{j=1}^{i} y_j \mathbf{w}_j$ effectively replaces the decay term, but it does more than just control the growth of the weights. This term ensures that each weight vector learns to represent different principal components of the input data:

1. **Orthogonality and Decorrelation**: The term $\mathbf{x} - \sum_{j=1}^{i} y_j \mathbf{w}_j$ represents the residual error after removing the contributions of all the previous components (from 1 to $i$) from the input $\mathbf{x}$. This ensures that each weight vector $\mathbf{w}_i$ learns to be orthogonal to the previous weight vectors $\mathbf{w}_1, \mathbf{w}_2, ..., \mathbf{w}_{i-1}$. Orthogonality is a key property of the principal components in PCA, where each component is uncorrelated with the others.

2. **Variance Maximization**: By projecting the input $\mathbf{x}$ onto the residual error, the algorithm ensures that each weight vector aligns with the direction of maximum variance in the residual. This is akin to how each principal component in PCA captures the direction of maximum variance in the data that is not already captured by the previous components.

3. **Incremental Learning**: Unlike batch PCA, which computes all principal components at once using the entire dataset, HPCA learns the components incrementally. This allows it to be applied in online or streaming data scenarios, adapting to new data as it becomes available.

Thus, the subtracted summation in the HPCA learning rule effectively guides each neuron in the network to learn different principal components of the input data, following the spirit of PCA in terms of finding orthogonal directions of maximum variance, but in a neural network context and with an incremental, online learning capability.