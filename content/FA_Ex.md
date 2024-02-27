---
title: "FA_Ex"
tags:
- hebbian
- phd
- Differential
---
 #hebbian #phd  
2024-02-10 16:57

Honestly just seems like it's a fancy way to say, "Multiply the hebbian rule by your error signal". It was bringing [[partial derivative and backprop|backprop]] and [[Omnivore/2023-08-11/Feedback alignment in deep convolutional net- works|Feedback alignment]] into it, idk. 
The mathematical notation is weak in this paper. It's super unclear whether the output is used in the weights update or if it's the *derivative* of the output. It may actually, if the latter case is true, be more like [[List of Hebbian Weight Update Rules#Differential Hebbian Learning (DHL)|differential hebbian learning]] with a global training/reward signal tacked on. 

Here's a diagram of what they essentially are doing:
![[zotero_notes/hebbian/FA_Ex-J5ETYZL4#^5db1d8|FA_Ex-J5ETYZL4]]

[[zotero_notes/hebbian/FA_Ex-J5ETYZL4#^9aa788|the caption]]:
Schematic illustration of three learning rules:
1. **BP (backpropagation):** Requires the information in $W_2$ to backpropagate.
2. **FA (feedback alignment):** Requires heterogeneity in the tentative impact of the middle layer neurons on the output.
3. **FA_Ex-100% (feedback alignment with 100% excitatory neurons in middle layer):** Most biologically plausible, as it computes using locally available information at a synaptic triad. Its performance is fairly good and comparable to BP.

With the notations:
- $y_i^{(1)} := f\left( \sum_j W_{ij}^{(1)} x_j \right)$
- $y^{(2)} := f\left( \sum_i W_i^{(2)} y_i^{(1)} \right)$
- $J := \frac{e^2}{2} = \frac{(y^{(2)} - y)^2}{2}$

The gradient for BP is given by:
$$ \frac{\partial J}{\partial W_{ij}^{(1)}} = e W_i^{(2)} f'\left( \sum_j W_{ij}^{(1)} x_j \right) \cdot x_j $$

In FA, $W_i^{(2)}$ is replaced by a random number $B_i$, and in FA_Ex-100%, it's replaced by 1. Therefore, for FA_Ex-100%, the synaptic weights in the middle layer are updated by the following rule:
$$ (\Delta W)_{ij} = -0.01 \frac{\partial J}{\partial W_{ij}^{(1)}} = -0.01 x_j \theta(I_i) e $$

Here, $\theta$ is a step function and $I_i$ is the current input to neuron $i$. This can be interpreted as:
$$ (\Delta W)_{ij} \propto \text{pre}_i \times \text{post}_j \times \text{dopamine} $$

Interestingly, simplified and biologically plausible learning rules like FA_Ex-100% work robustly as long as the error signal, possibly conveyed by dopaminergic neurons, is accurate.

# chat transcript
### Original FA_Ex-100% Learning Rule
The original FA_Ex-100% rule is given by:
$$ (1W)_{ij} = -0.01 \frac{\partial J}{\partial W_{ij}^1} = -0.01 x_j \theta(I_i) e $$
where:
- $(1W)_{ij}$: Change in weight for the synapse from neuron $j$ to neuron $i$.
- $-0.01$: Learning rate.
- $x_j$: Pre-synaptic activity (input to the synapse).
- $\theta(I_i)$: Step function of the input to neuron $i$, representing post-synaptic activity.
- $e$: Error signal, related to the difference between actual and desired output.

### Revised FA_Ex-100% Learning Rule using Standard Notation for Error Signal
The revised FA_Ex-100% rule using standard error signal notation is:
$$ \Delta W_{ij} = \eta \cdot x_j \cdot \theta(I_i) \cdot \frac{\partial L}{\partial y_i} $$
where:
- $\Delta W_{ij}$: Change in weight for the synapse from neuron $j$ to neuron $i$.
- $\eta$: Learning rate.
- $x_j$: Pre-synaptic activity.
- $\theta(I_i)$: Step function of the input to neuron $i$, representing post-synaptic activity.
- $\frac{\partial L}{\partial y_i}$: Error signal, represented as the derivative of the loss function with respect to the output of neuron $i$.
