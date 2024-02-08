---
title: "Informer paper"
tags:
- paper_notes
---
 #work/patientsim #paper_notes
[[2024-02-05]]

[[2012.07436] Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting](https://ar5iv.labs.arxiv.org/html/2012.07436) published in 2021

It's just a [[transformer|transformer]] with $O(L \log{L})$ complexity in its attention mechanism, using some sparse version of self-attention via distilling it. It's proven to work well on time-series data.