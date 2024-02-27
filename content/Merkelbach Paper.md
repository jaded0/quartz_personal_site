---
title: "Merkelbach Paper"
tags:
- paper_notes
---
 #work/patientsim #paper_notes

# Merkelbach version
Based on the MIMIC dataset.
## data prep
- time series data collected, normalized
- filled in missing data, imputed via linear interpolation, or in the case of no intag:#work/patientsimstance of this data at all, the median
- static data tacked onto every single instance of the time series data
## GRU
(it's bidirectional)
processes the whole of the data in both directions. Outputs are averaged over all the time steps, presumable leaving a single vector the length of the number of features.

## autoencoder
The single vector is put through a dense layer, making the bottleneck.
That bottleneck is "repeated through time", which I just think means it's copy/pasted as many times as there are timesteps, with the related timestep features added on. 

### decoder gru
Takes in the expanded bottleneck, turns it into another set (size of n timesteps) of vectors. A dense layer turns that into a copy of the original data. 

## pic

![[Pasted image 20240125124146.png]]
## my issues
- data is imputed - I'd personally rather it be robust to missingness
- static data repeated too much. We shouldn't have to repeat ourselves.
- the gru is just summed. what a weird way to combine all those values. Really messy. There's gotta be a better way.
- really, why is a gru even used?? Simply because it's the only thing that could fit a time series?

[[Triplet Sparsity Reduction]] is my proposed solution to those issues.