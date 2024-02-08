---
title: "List of Hebbian Weight Update Rules"
tags:
- hebbian
---
 #hebbian 

### Simple Hebbian Learning Rule:
$$ \Delta w_i = \eta y x_i $$

### Weight Decay Term Added:
$$ \Delta w_i = \eta y x_i - \gamma(\mathbf{w}, \mathbf{x}) $$

### Competitive Learning Rule:
$$ \Delta w_i = \eta y x_i - \eta y w_i = \eta y (x_i - w_i) $$

### Post-synaptic Gating:
$$ \Delta w_i = \eta y (x_i - \theta) $$

### Pre-synaptic Gating Rule:
$$ \Delta w_i = \eta x_i (y - \theta) $$

### Covariance Rule:
$$ \Delta w_i = \eta (y - \theta_y) (x_i - \theta_x) $$

### BCM Rule:
$$ \Delta w_i = \eta x_i \phi(y - \theta) $$

### Soft Thresholds on Weights:
$$ \Delta w_i = \eta \Delta w_i(\text{base}) (w_i - \theta_{\text{LB}}) (\theta_{\text{UB}} - w_i) $$

### Bi-stable Synapse Model (Part 1):
$$ \Delta w_i = H + R $$

### Bi-stable Synapse Model (Refresh Term):
$$ R = \gamma w_i (1 - w_i) (w_i - \theta) $$

### Oja's Rule:
$$ \Delta w_i = \eta y (x_i - y w_i) $$

### General Local Synaptic Update Equation:
$$ \Delta w_i = a_0 + a_1 x_i + a_2 y + a_3 x_i y + a_4 x_i^2 + a_5 y^2 + \ldots $$

### Differential Hebbian Learning (DHL):
$$ \Delta w_i = \eta \frac{dy}{dt} x_i $$
### HPCA
$$
\Delta \mathbf{w}_i = \eta y_i \left( \mathbf{x} - \sum_{j=1}^{i} y_j \mathbf{w}_j \right)
$$

pulled from [[zotero_notes/hebbian/Survey-of-Hebbian-Learning-Lagani-2023-CF4RA22D#^12a1aa|Survey-of-Hebbian-Learning-Lagani-2023-CF4RA22D]]