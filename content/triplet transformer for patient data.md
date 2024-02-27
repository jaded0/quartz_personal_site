---
title: "triplet transformer for patient data"
tags:
- paper_notes
- triplet
---
 #work/patientsim #paper_notes
# Self-Supervised Transformer

Seems like it's the modern, best way to do it. Triplets are stored, solving the whole sparsity problem in both the time and feature space. It's a [[transformer|transformer]], effectively getting those long-term dependencies.
Keith's problem with the triplet idea was that the relationship between different features within the same timestep might not be so emphasized/preserved. I don't really think that'd be a problem with a transformer like this, on account of the self-attention mechanism.

The idea with a triplet is really cool. I'm biased, because I suggested it to Keith, and he found a paper that actually described just what I was talking about. Instead of having tons of empty space taken up by features that don't have data available at a given timestep, or alternatively, taken up by gaps in time where the feature doesn't have data, we can directly encode a sort of 'value' of the data, some sort of data identity, and finally the positional encoding of the data. Then, we just give one piece of data at a time. It can be lots of different kinds of features, doesn't matter, but it's one feature at a time. If they happen at the same timestamp, we just give them the same positional encoding and still put them one after another. 
![[zotero_notes/patient_sim/triplet-transformer-G7LK8EX5#triplet justification|triplet-transformer-G7LK8EX5]]


# notes
- is there a causal mask in the Contextual Triplet Embedding?
- i should use the attention layer less or smth. this one uses two.