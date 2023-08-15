---
title: "Augment WLASL"
tags:
- stablediffusion
---

# previous attempt
My little attempt at straight training an entire stable diffusion model on just the WLASL dataset was fairly ineffectual. Months of training on university compute resources culminated in a bit of a blurry mess:
![[/files/example_book_43402_7bbb996a33a6757f0c3d.gif|500]]

This is supposed to be the sign for 'book'.

I spent probably about 100 hours, total, trying to force this to work, fiddling with hyperparameters and diving into the code to learn what might be improved. I tried my own set of augmentations: cropping the windows randomly, skipping frames, cropping the video at different times. 
The odyssey, with loss graphs and sample outputs, is logged [here](https://wandb.ai/jadens_team/vid-signs?workspace=user)].

Truly, I needed an existing video diffusion model, but there wasn't one available at the time.

# current go at it
- There are now some pretty solid video diffusion models. 
- ControlNet-guided diffusion does a pretty good job at maintaining some temporal consistency between frames. 
- Temporal conditioning techniques also exist, allowing me to pass frames into existing stablediffusion models and expect better consistency between them. 
- I now have access to GPT-4, which offers a few advantages:
	- The large model may possess enough contextual knowledge of ASL to offer some data augmentation avenues as far as the labeling of the videos go.
		- I can add in words that are signed the same to the labels. 
		- I can attempt to disambiguate some words.
	- I can work towards a full translation pipeline. I believe that GPT-4 is likely able to translate spoken english to an intelligible ASL representation using only word-level knowledge.
		- I could potentially use this to transform a person's photo into a live ASL translating avatar.