---
title: "wild"
tags:

---
 #work/patientsim 
2024-02-07 14:16

look at [[PatchMixer]]. Its single time-series is cut into pieces and fed into the embedding to be internally convoluted. There must be no room for [[Triplet Sparsity Reduction|triplets]]! 

Oh, but there is. I'll devise a way to cram in, just smash together the triplet-encoded data right in ther

One curious little detail is that the paper makes a big deal out of not needing time embeddings to track anything, but with the triplets, I'll prolly need to. Otherwise, lots of features that may happen in the same timestamp will be considered to be sequential, given that the triplets only go in one at a time. Also, my data is very time-sparse, too. not continuous, like what the paper uses. So, I'll have to worry about representing gaps somehow. 
