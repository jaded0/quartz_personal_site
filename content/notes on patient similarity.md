---
title: "notes on patient similarity"
tags:

---
#work/patientsim 

# obvious structure
- denoising autoencoders seem like the clear way to go for making some sort of embedding/latent space for patients
- the denoising is interesting for discussion, especially if we have additional boolean variables signifying whether the input is even present. When comes down to it, should a patient's data be represented identically if info is omitted? Are two patients the same if one has data the other doesn't? Keith said that they may not be, since missing data is information, in itself. If that's the case, we shouldn't do denoising. 

# time series
This one is weird, because it may truly just be a matter of using a mix of existing architectures.
- some papers used RNNs like GRU, LSTM, but [[Transformer-based Solutions|transformer]] is king, when the context length is small enough. [[patient record model type breakdown]]
- Context length is likely a limiting factor, so I can understand that only clustered bits were given little self-attention blocks. This is akin to a lot of hierarchical solutions to the context length problem found in plenty of big new papers. 

# conceptualizing
General vibes.

- really, isn't what the end goal is to just identify truly similar patients? We're looking for a latent space where the similar patients are closer than dissimilar. 
- To do that, we need something that weighs inputs by significance. Does autoencoding actually do that?? Really, how do we tell it that gender is a bigger deal than the material used in the dressing? Does it figure it out by how it affects other values?? I think the model needs an actual objective before this weighing can occur. 

# out-there brainstorming
![[ideas about ml structure for healthcare]]
# reading log

![[Patient Similarity Readings Log]]