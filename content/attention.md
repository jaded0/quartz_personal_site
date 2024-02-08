---
title: "attention"
tags:

---

2024-02-07 14:38

key component of the [[transformer]]

The word embedding is fed into three layers side by side, they each make some representation of it, called query, key, and value.

![[Pasted image 20240207144646.png]]

these three vectors are thrown together to get a final vector for all the words seen. That's thrown through the layers of the network to finally get a next word-prediction. 
The throwing together is just the query of the word getting multiplied for the 