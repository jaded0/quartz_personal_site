---
title: "meta-learning with hospital data"
tags:
- paper_notes
---
 #work/patientsim #paper_notes
[[2024-02-05]]

DynEHR, written about in 2021, was frustrating to figure out, due to a paywall. I just grabbed its description from a paper that speaks about it:
> DynEHR, a model designed to adapt to various ICU lengths of stay. This approach employs an LSTM model on the time-series data and applies MAML on the top of the LSTM layers. The performance of DynEHR was evaluated on the MIMIC-III dataset for different tasks.

Underwhelming, given the effort I put in to get it. 

The second paper is more useful+available. It seems to suggest that the biggest benefits of meta-learning are concerned with there being a very low amount of data available in a new domain. Seems cool, but it's not the problem I'm dealing with. 

[[2308.02877] Meta-learning in healthcare: A survey](https://ar5iv.labs.arxiv.org/html/2308.02877)