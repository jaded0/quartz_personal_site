---
title: "Synaptic Balancing"
tags:
- hebbian
- phd
---
 #hebbian #phd  
2024-02-12 14:19

This was a very confusing and math-heavy paper.


# chat transcript
Certainly! Let's outline a simple algorithm for updating synaptic weights in a neural network using a synaptic balancing rule, along with the computation and tracking of average gain. We'll use a ReLU activation function for this example:

### Variables and Setup
- Let \( w_{ij} \) be the weight of the synapse from neuron \( j \) to neuron \( i \).
- \( \sigma_j \) will represent the average gain (average activation) of neuron \( j \).
- \( a_j \) is the activation of neuron \( j \).
- Activation function for neuron \( j \), \( f(x) \), is ReLU: \( f(x) = \max(0, x) \).
- Learning rate: \( \eta \).

### Algorithm Steps

1. **Initialization**:
   - Initialize all synaptic weights \( w_{ij} \) randomly.
   - Initialize all average gains \( \sigma_j \) to 0.

2. **Forward Pass for Each Training Example**:
   - Compute the activation \( a_j \) for each neuron using ReLU.
   - Store these activations for calculating the average gain.

3. **Calculate Average Gain**:
   - For each neuron \( j \), update its average gain:
     $$ \sigma_j = \text{MovingAverage}(\sigma_j, a_j) $$
   - Here, \(\text{MovingAverage}\) is a function that computes the moving average, incorporating the latest activation \( a_j \) into the existing average \( \sigma_j \).

4. **Synaptic Balancing Rule for Weight Update**:
   - For each synapse \( w_{ij} \), update the weight based on the average gains of the pre- and post-synaptic neurons:
     $$ \Delta w_{ij} = \eta \cdot (\sigma_j^2 - \sigma_i^2) \cdot w_{ij} $$
   - Update the weight: \( w_{ij} \leftarrow w_{ij} + \Delta w_{ij} \).

5. **Repeat for Each Training Iteration**:
   - Repeat steps 2 to 4 for each training iteration, using the respective inputs and calculating the activations for each neuron.

### Additional Notes
- **Moving Average Calculation**: The moving average can be calculated using an exponential moving average or a simple windowed average. For instance, an exponential moving average with a smoothing factor \( \alpha \) would be:
  $$ \sigma_j = \alpha \cdot a_j + (1 - \alpha) \cdot \sigma_j $$
- **Training Data**: The algorithm runs through the training data, performing the forward pass and weight updates for each training example or batch of examples.
- **Learning Rate**: The learning rate \( \eta \) controls the speed of learning. It should be chosen carefully to balance the speed of convergence and the stability of learning.

This algorithm provides a framework for implementing synaptic balancing in a simple neural network, where the synaptic weight updates are influenced by the average activation levels (interpreted as gains) of the neurons. The balance between the pre- and post-synaptic neurons' average activations guides the adjustments of synaptic strengths, aiming to maintain a balanced and functional network.




In the context of the synaptic balancing rule and considering your focus on ReLU activation functions, using the derivative of the activation function to represent gain is indeed less informative due to its binary nature (0 or 1). However, if we were to include the derivative in the context of a different activation function, or if you prefer to include it even with ReLU, here's how it could be integrated into the algorithm:

### Algorithm with Derivative of Activation Function for Gain

1. **Initialization**:
   - Initialize synaptic weights \( w_{ij} \) and average gains \( \sigma_j \) as before.

2. **Forward Pass and Gain Calculation for Each Training Example**:
   - Compute the activation \( a_j \) for each neuron using the activation function.
   - Calculate the derivative of the activation function at \( a_j \). For ReLU, this is 0 for \( a_j < 0 \) and 1 for \( a_j \geq 0 \). For other functions, calculate the actual derivative.
   - Update the average gain \( \sigma_j \) using this derivative value.

3. **Update Average Gain**:
   - Update the average gain for each neuron \( j \):
     $$ \sigma_j = \text{MovingAverage}(\sigma_j, f'(a_j)) $$

4. **Synaptic Balancing Rule for Weight Update**:
   - Update the synaptic weights as before:
     $$ \Delta w_{ij} = \eta \cdot (\sigma_j^2 - \sigma_i^2) \cdot w_{ij} $$
   - Apply the weight update: \( w_{ij} \leftarrow w_{ij} + \Delta w_{ij} \).

5. **Repeat for Each Training Iteration**.

### Considerations

- **Derivative in ReLU**: For ReLU, this approach would mean that the average gain \( \sigma_j \) effectively tracks how often the neuron is active (since the derivative is 1 when the neuron is active and 0 otherwise).
- **Other Activation Functions**: If you use activation functions other than ReLU, like sigmoid or tanh, the derivative provides a more nuanced measure of gain, reflecting how sensitive the neuron's output is to changes in its input.

Using the derivative of the activation function to represent gain, especially with activation functions that have more variable derivatives, provides a measure of how a neuron's output changes in response to its inputs, which can be crucial for synaptic adjustments in learning algorithms.