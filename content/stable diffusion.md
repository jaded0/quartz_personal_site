---
title: "stable diffusion"
tags:

---
 
[[2024-02-05]]

It's a technique based on [[Denoising Diffusion Probabilistic Models Notes|denoising diffusion]], where images are put into a latent [[subspace|space]] before being worked on, then the model is trained to iteratively remove random noise from images. Eventually, we can give it pure tv static and it will give a realistic image. Add in a [[CLIP guidance|CLIP]] embedding that comes from the text description of the image as a hint during training, and we can type in our own prompts along with the tv static to influence what's created. 