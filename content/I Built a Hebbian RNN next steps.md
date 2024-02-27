---
title: "I Built a Hebbian RNN next steps"
tags:
- hebbian
- General
- Competitive
- Covariance
- crazy
---
 #hebbian  
2024-02-09 08:06


Four things to work on next:
- Try out some new rules found in the survey, [[List of Hebbian Weight Update Rules|listed here]]
- Use a more optimized dataset, perhaps simpler. Or make mine more efficient.
- Run it on university compute.
- Try some completely different rules from scratch, based on some other papers' code.

## new rules
Does [[Ojas Rule]] work? I might even be able to generalize, probably not this next step, though. I may want to combine the general equation with a metalearning approach, like in [[zotero_notes/hebbian/meta-learning-through-hebbian-plasticity-KG2BPTBB|meta-learning-through-hebbian-plasticity]].
![[List of Hebbian Weight Update Rules#General Local Synaptic Update Equation]]

That's not a simple approach. It would be simpler for me to just swap out rules like:
- [[Ojas Rule]]
- [[List of Hebbian Weight Update Rules#Competitive Learning Rule|competitive]]
- [[List of Hebbian Weight Update Rules#Covariance Rule|covariance rule]]
- maybe [[HPCA]]
I can straight-shot just test them in the [[Current Build of the Memory Encoding Hebbian RNN|current build]], maybe just excluding my existing normalization of the weights in hopes that these rules eliminate the need for that. 

I also had an interesting idea where I replace my next-character prediction reward signal with one that was layer-wise. It's based on HPCA, but time-shifted: [[HPCA#crazy idea]]
# better dataset
I'm currently using project gutenberg, with 100-character strings chosen randomly. It's one-hot encoded, fed in one character at a time. I'm not sure whether it's a bottleneck in the learning process, for a couple of reasons:
- it may be pulling from disk each time
- it could potentially fit on gpu, which would be faster
- it might be too complex for my current fast-iteration needs
I should look into:
- optimized, common datasets/dataloaders that are probably already built into pytorch
- data that more explicitly suits the needs: it should incentivize taking long-term dependencies into account. 
I'm not sure what sort of dataset I'd be looking for in the latter case. I just want to see the thing train faster, especially on the backprop-rnn baseline. Perhaps a baby name dataset? But that doesn't have long-term dependencies. Low vocab, like simple english wikipedia may be it. Maybe some common computer vision dataset would do the trick. I don't really want to do reinforcement learning environments.

pytorch has built-in text datasets: [torchtext.datasets — Torchtext 0.17.0 documentation](https://pytorch.org/text/stable/datasets.html)
Notably, the unsupervized ones look interesting:
- [CC100](https://pytorch.org/text/stable/datasets.html#cc100) common crawl
- [EnWik9](https://pytorch.org/text/stable/datasets.html#enwik9) wikipedia
The computer vision ones are interesting, too:
[Datasets — Torchvision 0.17 documentation](https://pytorch.org/vision/stable/datasets.html)
Especially [Omniglot](https://pytorch.org/vision/stable/generated/torchvision.datasets.Omniglot.html#torchvision.datasets.Omniglot)
![[Pasted image 20240209084726.png|500]]
This would have long-range dependencies, right? Like if I made it just put out one pixel at a time, left to right and down?
# university compute
I have to find my BYU id, contact Dr. Fulda, contact the office of research computing, use a vpn, it's a whole hassle. I'll want my code to be pretty organized and portable and optimized, so I guess I'm biased toward doing all the other things first. However, it's possible that my wishes for better understanding of the learning dynamics are just a 2-day supercomputer run away. I could literally be wasting time right now because my existing code just works.

## wipe and restart
Other papers already have hebbian learning running, I may just need to slap on my reward signal and rnn loop and get it going. It could be good to see how a new structure might prove superior. 