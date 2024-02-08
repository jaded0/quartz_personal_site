---
title: "Generating Synthetic Data Paper"
tags:
- paper_notes
- fakedata
---
#paper_notes  #work/patientsim 
# Generating Synthetic Data Paper
I took like 6hrs to crack this paper, reading it off and on. Since the authors were mainly interested in generating patient data, the encoding of the data into a good latent space was treated as a given. I initially thought I had cracked it, thinking that they simply threw a concatenated set of time blocks and their features into a normal VAE.
![[zotero_notes/patient_sim/fakedata-DJMSSG8H#notes]]

Nay, upon looking into its code, I find LSTMs inside the VAEs. The [[zotero_notes/patient_sim/fakedata-supplement-AXDGBHD7#fakedata supplement|supplementary info]] explains that they were just basing their idea on the 2015 paper called [DRAW](https://arxiv.org/pdf/1502.04623.pdf).
