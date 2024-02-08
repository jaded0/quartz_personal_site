---
title: "Perceiver vs Informer"
tags:

---
 #work/patientsim 
# they're different
They were developed independently for different purposes:

- The [[Perceiver Paper|Perceiver]], developed by DeepMind, focuses on generalizing the transformer architecture to handle various types of input data without task-specific modifications.
- The [[Informer paper|Informer]], developed by researchers primarily from Tsinghua University, is tailored for efficient long sequence time-series forecasting, addressing specific challenges in handling long sequences with transformers.

# they are used for different things
1. **Perceivers**: Developed by DeepMind in 2021, Perceivers were created to generalize the transformer model to handle various input types (like images, audio, text) in a uniform way. This approach allows processing of different modalities and input sizes without task-specific architectures, using a fixed-size latent space.
2. **Informers**: Developed by researchers at Tsinghua University and other institutions in 2020, Informers are designed to improve the efficiency of transformers for long sequence time-series forecasting. They address the challenge of computational complexity in handling long sequences with innovations like ProbSparse self-attention, enabling the model to focus on the most relevant parts of the input.