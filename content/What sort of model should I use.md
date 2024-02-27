---
title: "What sort of model should I use"
tags:

---
#work/patientsim  
[[2024-02-07]]

Well, there's lots of [[patient record model type breakdown|examples]]. I'm pretty sold on those [[Triplet Sparsity Reduction|triplets]] because they're cool and they solve the whole time+feature space sparsity issue in a pretty way. That's really more of a way of fitting the data in. Definitely superior to how it's done in the others, though. They'll:
- cut it into windows, create overlapping embeddings
- give each feature their own entire NN
- stuff it into an RNN and just grab the whole final output, throw that into the main solution
	- or worse, they'll aggregate the RNN output by summing over the outputs of each step???? [[Merkelbach Paper|@merkelbach]]
	- at least one of them computes the attention or smth over the outputs of each step. idk which tho

So, it comes down to what I'm piping the triplets into. I could really pick anything. There's really two routes: 
- [[wild]] - try out the $CNN$ for time series
- [[basic]] - just do another transformer™

[[patient similarity model|my choice]]
