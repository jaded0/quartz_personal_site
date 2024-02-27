---
title: "patient similarity model"
tags:

---
#work/patientsim  

# choice
I've chosen [[basic]]. With some modifications, of course. 
I'm creating an [[autoencoder]], so there needs to be a way to both ingest and reconstruct the time series input. That's not exactly a solved problem.

I'll use transformers on both sides, the [[Triplet Sparsity Reduction|triplets]] treated as tokens.
1. I'll sum the outputs on a final attention layer to create the single-vector patient representation vector. 
2. The second transformer is a next-token predictor. Structured as a typical decoder-only transformer like GPT. During training, it receives preceding tokens directly from the same training data as the encoding transformer. However, it also gets the patient representation vector concatted in beside the attention layer. 
3. An additional value might be included with the patient representation vector, to inform the transformer what data type is being asked for.

Of course the decoding transformer could be trained on next-token prediction alone, but the idea is that we can create a cheat sheet for the whole patient that makes the task trivial. Ideally, the encoder makes any real prediction unnecessary. 

The idea is kinda similar to [[stable diffusion]], in that a model is trained to reconstruct incomplete data, based on some conditioning input. Except, in my case, the focus is less on the reconstruction ability, and more on the fidelity of the conditioning input. 
In stable diffusion, the autoencoder is actually frozen! All the action is happening inside the latent space. 

It's barely an autoencoder, really. A single training instance is not asking the decoder to reconstruct the full input, even, but just a small piece. 