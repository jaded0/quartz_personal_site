---
title: "PerceiverIO Paper"
tags:

---
 #work/patientsim 
[[2024-02-05]]

# on NLP
They seem to pretty much match transformers, flop-for-flop.

> We first compare Perceiver IO to standard Transformers for language. Although Transformers were originally developed for language, their quadratic complexity makes them difficult to use on language inputs without tokenization, which typically shortens the length of input sequences by a factor of ∼4. But unlike Transformer-based models such as BERT (Devlin et al., [2019](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib21)) or XLNet (Yang et al., [2019](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib97)), Perceiver IO scales linearly with input length. Our experiments focus on showing that Perceiver IO performs as well as or better than Transformers for masked language modeling (MLM) while removing tokenization (which is hard to maintain, introduces engineering overhead, and adds needless complexity to language models (Bostrom & Durrett, [2020](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib6); Clark et al., [2022](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib14))).
> We compare results for a given FLOPs budget rather than a given parameter budget as the former grows quadratically with sequence length but the latter is independent (except for positional encodings). From a practioner’s perspective, FLOPs matter more than parameters since FLOPs directly relate to training time. We evaluate the quality of the learned representation on the GLUE benchmark (Wang et al., [2019](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib92)) and report our results in Tab. [1](https://ar5iv.labs.arxiv.org/html/2107.14795#S4.T1 "Table 1 ‣ 4.1 Language ‣ 4 Experiments ‣ Perceiver IO: A General Architecture for Structured Inputs & Outputs"). We find that at a given FLOPs budget, Perceiver IO trained without tokenization matches the performance of a strong Transformer-based model trained with SentencePiece tokenization (Sennrich et al., [2016](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib69); Kudo & Richardson, [2018](https://ar5iv.labs.arxiv.org/html/2107.14795#bib.bib43)).
