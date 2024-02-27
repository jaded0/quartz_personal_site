---
title: "basic"
tags:

---
 #work/patientsim 
2024-02-07 13:59

I should really go with the transformer on this one. The triplets do turn the data into a sequence of values, some with much higher relative importance than others. That feels pretty [[attention]]-native.
The idea is much more incremental, too. The original [[triplet transformer for patient data|triplet paper]] simply uses a self-supervised prediction objective, and I could add only the [[Variational Autoencoder|VAE]] into the mix. 

I mean, look at this graphic:
![[zotero_notes/patient_sim/triplet-transformer-G7LK8EX5#^134274|triplet-transformer-G7LK8EX5]]
Looks a whole lot like Keith's formulation of one of our core problems!

