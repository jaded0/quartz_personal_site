---
title: "Triplet Sparsity Reduction"
tags:

---
#work/patientsim  

This note was originally created in contrast to the gru-based autoencoder in the [[Merkelbach Paper]]. That's right, I had the idea before I found it in the paper. I got a big head about it.
# My Version

- RNN (of some sort), each data point gets a timestep of its own.
- Each data point/feature gets turned into an embedding. 
	- basically im just saying that instead of having a big sparse representation, i'm densifying it early. like character one-hots to word embeddings. 
	- it also gets its own positional encoding, which may be identical to the previous iteration of the rnn bc it's collected at the same time. 
- maybe the static data gets tacked onto the output after recurring stuff is summed, or otherwise collected into a standard vector of fixed size.
- we're gonna have issues with long-term dependencies. That's just a fact. 

# existing similar approaches
Another paper already does, this for use in a transformer-based approach! That's where I get the [[triplet transformer for patient data|triplet]] name from.

It's super similar to the way that tokens themselves are treated in a [[transformer|transformer]]. The time, feature type embedding, and the value of the instance of the feature, are akin to [[keys, queries, values]].