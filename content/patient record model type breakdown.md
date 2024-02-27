---
title: "patient record model type breakdown"
tags:

---
#work/patientsim  
[[2024-02-06]]
## transformer
![[Transformer-based Solutions]]

## RNNs
- [[meta-learning with hospital data|DynEHR]], metalearning with [[model-agnostic metalearning|MAML]] atop an LSTM
- [[coupled rnn paper|coupled rnns]] well-suited to dual data types, like image+poses
- [[Generating Synthetic Data Paper|EHR-M-GAN]] is based on an LSTM for its encoding of time series, which is based off [DRAW](https://arxiv.org/pdf/1502.04623.pdf).
- [[Merkelbach Paper]] just uses a GRU, pretty basic. One of the few that demonstrate the true autoencoder structure I'm looking to use any of this stuff for, though. Everything else just uses some sort of outcomes or next-event prediction or smth.


## Convolutional Neural Networks (CNNs)
- [[PatchMixer|PatchMixer]], very strange. It compares itself a **lot** with the [[transformer]], though.
- [[zotero_notes/patient_sim/dilated-convolutions-BC5HWKRF|dilated-convolutions-BC5HWKRF]] very weird