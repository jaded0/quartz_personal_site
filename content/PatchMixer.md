---
title: "PatchMixer"
tags:
- paper_notes
---
 #work/patientsim #paper_notes
[[2024-02-05]]

A convolutional neural network!! Haven't seen one in a minute, and certainly didn't expect it in time series processing.

![[zotero_notes/patient_sim/PatchMixer-G578PTIA#^08f144|PatchMixer-G578PTIA]]

Seems like the main innovation is in its [[zotero_notes/patient_sim/PatchMixer-G578PTIA#^68a782|patch-mixing]], used as an alternative to self-attention. Patch-mixing relies on convolutions. First, there's convolutions over each patch, then convolutions over those representations of the patches.

### 1. **Convolutions Over Each Patch**:

- **Depthwise Convolution**: This step involves applying convolutions to each patch of the input data separately.
- **Local Feature Extraction**: The purpose here is to capture the local features within each patch. Each patch is processed independently, allowing the model to learn detailed, location-specific patterns or characteristics within that segment of the data.

### 2. **Convolutions Over Representations of the Patches**:

- **Pointwise Convolution**: After processing each patch independently, the next step involves applying a pointwise convolution across these patch representations.
- **Global Feature Integration**: This stage is crucial for combining the information from different patches. It helps in understanding the relationships between patches, essentially capturing the global or long-range dependencies in the data.

This is not for heterogeneous data. seems like it's mostly for continuous time series. In fact, it's channel-independent, completely separating different features and not using them for predicting each other. Not ideal for patient similarity representation. ![[zotero_notes/patient_sim/PatchMixer-G578PTIA#^f51cf8|PatchMixer-G578PTIA]]



[[2310.00655] PatchMixer: A Patch-Mixing Architecture for Long-Term Time Series Forecasting](https://ar5iv.labs.arxiv.org/html/2310.00655v1)

