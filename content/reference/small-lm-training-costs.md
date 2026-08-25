---
title: Training Compute & Cost of Open Small-LM Families (and the Distillation Hair)
date: 2026-06-17
tags:
- reference
- mirror
publish: true
description: 'The question this answers: when is pretraining your own small base model
  (~≤1–3B params) cost-justified, versus just taking an open-weight model off the
  shelf?'
---

# Training Compute & Cost of Open Small-LM Families

The question this answers: when is pretraining your own small base model (~≤1–3B params) cost-justified, versus just taking an open-weight model off the shelf?

**The central nuance ("the hair"):** Some small models are *distillations* of a much larger sibling. For those, the honest cost of *having* the small model includes the cost of training the big teacher — you cannot get the small distilled model's quality without first paying for the large one. So for each family below I distinguish **(a)** trained from scratch vs. distilled, and **(b)** if distilled, the teacher size/cost that rides along.

**Cost-estimate convention:** Where no dollar figure is published, I estimate `GPU-hours × rate`. For modern H100/H200-class runs I use **\$3.50/GPU-hr** (mid-point of the mid-2026 H200 on-demand market, which spans ~\$2.30–\$4.50 with a working median near \$3.95; spot is 40–65% cheaper). For Pythia's A100-40GB era I use **\$1.50/A100-hr** (typical commodity A100 cloud rate). **All such figures are labeled `[EST]`.** Anthropic's own knowledge cutoff is Jan 2026; rates verified via 2026 GPU-pricing trackers.

---

## 1. Pythia (EleutherAI) — the from-scratch baseline

| | |
|---|---|
| Sizes | 70M, 160M, 410M, 1.0B, 1.4B, 2.8B, 6.9B, 12B (×2 variants: standard Pile + dedup Pile). 14M/31M added to repo later. |
| Tokens | **~300B** standard (exactly 299,892,736,000, ~1 epoch of the 334B-token Pile); **~207B** for the deduplicated-Pile variant (still trained to the same ~300B budget → ~1.5 epochs over dedup data). |
| Hardware | **A100 40GB** (explicit: *"All GPUs are A100s with 40 GiB VRAM"*). Per-size GPU counts: 70M–410M = 32; 1.0B/1.4B/2.8B = 64; 6.9B = 128; 12B = 256. Compute donated by Stability AI. |
| GPU-hours | **Published** (Table 5). Per model: 70M=510, 160M=1,030, 410M=2,540, 1.0B=4,830, 1.4B=7,120, 2.8B=14,240, 6.9B=33,500, 12B=72,300. **One full suite = 136,070 A100-hr.** Total for the paper (2 variants, retrained) = **544,280 A100-hr.** |
| Distillation | **NONE. From scratch.** No teacher anywhere. Canonical from-scratch baseline; design goal is interpretability/scaling research with identical data order across all sizes and 154 checkpoints/model. |
| \$ cost | Not published (compute was donated → EleutherAI out-of-pocket ≈ \$0). |

**Cost estimate [EST]** at \$1.50/A100-40GB-hr:
- 410M ≈ 2,540 hr → **~\$3.8K**
- 1.0B ≈ 4,830 hr → **~\$7.2K**
- 1.4B ≈ 7,120 hr → **~\$10.7K**
- Full 8-size suite ≈ 136,070 hr → **~\$204K**

**Takeaway:** A clean small base model in the ≤1.4B range, trained from scratch on ~300B tokens, is genuinely cheap — **single-digit to low-five-figure dollars** of compute. No hidden teacher. This is the honest floor for "build your own small model."

Sources: [arXiv 2304.01373](https://arxiv.org/abs/2304.01373) · [HTML/Table 5](https://ar5iv.labs.arxiv.org/html/2304.01373) · [GitHub](https://github.com/EleutherAI/pythia) · third-party cost cross-check [arXiv 2410.23261](https://arxiv.org/html/2410.23261v1).

---

## 2. SmolLM2 (Hugging Face) — from scratch, more tokens

| | |
|---|---|
| Sizes | 135M, 360M, 1.7B |
| Tokens | **135M = 2T · 360M = 4T · 1.7B = 11T** (confirmed in paper + model cards). 1.7B used a 4-stage curriculum; small models single-stage with re-ablated data mixes. |
| Hardware | **H100**, nanotron framework. 135M = 64×H100; 360M = 128×H100; 1.7B = 256×H100. |
| GPU-hours | **Not published** for any size. |
| Distillation | **NONE for base models. All three trained from scratch** on their own token budgets — the 135M/360M are *not* distilled from the 1.7B. The paper's only distillation mention is a *contrast*: "Llama3.2-1B, derived from a pruned 8B model, was trained using distillation." (Instruct variants use ordinary SFT+DPO, not model-to-model distillation.) |
| \$ cost | **Published for 1.7B only: ~\$250,000 / ~1e23 FLOPs** of GPU compute. No published cost for 135M/360M. |

**Cost estimate for the small ones [EST]:** No GPU-hours published, so estimate via FLOPs. Using the paper's own anchor (1.7B ≈ 1e23 FLOPs ≈ \$250K) and the rule-of-thumb `C ≈ 6·N·D`:
- 1.7B × 11T ≈ 1.1e23 FLOPs (matches the published ~\$250K).
- 360M × 4T ≈ 8.6e21 FLOPs → ~\$19K [EST]
- 135M × 2T ≈ 1.6e21 FLOPs → ~\$3.6K [EST]

**Takeaway:** SmolLM2 is the "from scratch but trained hard" case. The small models stay cheap (~\$4K–\$20K [EST]), but the flagship 1.7B's **\$250K** shows that pushing a 1.7B to SOTA via 11T tokens is ~25–35× costlier than Pythia-1.4B's ~300B-token run. Quality here comes from *tokens*, not a teacher — so the cost is honest and self-contained.

Sources: [arXiv 2502.02737](https://arxiv.org/abs/2502.02737) · [HTML](https://arxiv.org/html/2502.02737v1) · model cards [1.7B](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B) / [360M](https://huggingface.co/HuggingFaceTB/SmolLM2-360M) / [135M](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) · [GitHub](https://github.com/huggingface/smollm).

---

## 3. OLMo / OLMo 2 (AI2) — from scratch, with published energy/carbon

|                 |                                                                                                                                                                                                                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Sizes           | OLMo v1: 1B, 7B (+65B in progress). OLMo 2: 1B, 7B, 13B, 32B.                                                                                                                                                                                                                                          |
| Tokens          | OLMo-7B v1 = **2.46T** (Dolma); 1B ~2T. OLMo 2: **1B ~4.05T · 7B 4.05T · 13B 5.6T · 32B 6.6T** (pretrain + Dolmino mid-train).                                                                                                                                                                         |
| Hardware        | **v1:** dual clusters — LUMI (up to 256 nodes × 4 AMD MI250X) + MosaicML (27 nodes × 8 **A100-40GB** = 216 A100). **OLMo 2:** Jupiter (1,024 **H100**) + Augusta/GCP (1,280 H100), ~38% MFU, >1,800 tok/s/GPU.                                                                                         |
| GPU-hours       | **NOT reported directly** in either paper (they report MWh instead).                                                                                                                                                                                                                                   |
| Energy / carbon | **Published.** v1 7B: 239 MWh combined, **69.78 tCO2eq** (104 MWh/70 t on the A100 Australia run; 135 MWh on hydro-powered LUMI ≈ 0–3.5 t). OLMo 2: 7B = 131 MWh / **52 tCO2eq**; 13B = 257 MWh / **101 tCO2eq**; combined ~391 MWh / ~154 t / ~1.1M L water. 32B & 1B power not separately tabulated. |
| Distillation    | **NONE. From scratch** (random init, std 0.02). Mid-training = continued pretraining on the same base, **not** teacher distillation.                                                                                                                                                                   |
| \$ cost          | Not published. Only relative claim: OLMo 2 32B matched Qwen2.5-32B "at one third of the cost of training Qwen 2.5 32B."                                                                                                                                                                                |

**Cost estimate [EST]:** Deriving GPU-hours from energy is rough but illustrative. OLMo 2 7B at 131 MWh / PUE 1.2, H100 ≈ 0.7 kW board power → ~131,000 kWh ÷ (0.7 kW × 1.2) ≈ **~156K H100-hr → ~\$546K [EST]** at \$3.50/hr. (Cross-check via FLOPs: 7B × 4.05T × 6 ≈ 1.7e23 FLOPs, ~\$425K–\$550K range — consistent order of magnitude.) **OLMo 2 1B (~4T tokens) ≈ 2.4e22 FLOPs → ~\$75K [EST].**

**Takeaway:** OLMo 2 is the best-documented from-scratch case and the most directly relevant comparison for a lab wanting full transparency. A 7B from-scratch run is **mid-six-figures [EST]**; a 1B is **~\$75K [EST]**. Still no hidden teacher — the cost is the cost.

Sources: [OLMo arXiv 2402.00838](https://arxiv.org/abs/2402.00838) (Table 6 carbon) · [OLMo 2 arXiv 2501.00656](https://arxiv.org/abs/2501.00656) (§6, Table 19) · [AI2 blog: OLMo 2 32B](https://allenai.org/blog/olmo2-32b) · cards [OLMo-2-1B](https://huggingface.co/allenai/OLMo-2-0425-1B) / [OLMo-7B](https://huggingface.co/allenai/OLMo-7B-hf).

---

## 4. Qwen (Alibaba) — and the strongest distillation hair

### Qwen2.5 — from scratch (no distillation for dense base models)

| | |
|---|---|
| Sizes | 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B (open-weight) + proprietary MoE Turbo/Plus. |
| Tokens | Pretraining corpus scaled to **~18T tokens** (up from 7T in Qwen2). Stated as the family-wide corpus scale; **no per-size token table published.** |
| Hardware / GPU-hours | **NOT published** (no GPU type, count, hours, or cost anywhere in the report). |
| Distillation | **NONE for dense base models.** Pretrained on 18T, then SFT (>1M samples) + multistage RL (DPO/GRPO). No distillation in the dense recipe. |

### Qwen3 — explicit strong-to-weak distillation (THE hair)

| | |
|---|---|
| Sizes | Dense: 0.6B, 1.7B, 4B, 8B, 14B, 32B. MoE: 30B-A3B and flagship **235B-A22B**. |
| Tokens | **~36T tokens** (≈2× Qwen2.5), 119 languages. (Pretraining is still on full corpus for all sizes.) |
| **Distillation** | **YES — and this is the key example.** Post-training has two tracks: a full **4-stage RL pipeline** for the frontier models (32B, 235B-A22B), and **Strong-to-Weak Distillation** for the *lightweight* models: **0.6B, 1.7B, 4B, 8B, 14B dense + 30B-A3B MoE.** |
| Teachers | **Qwen3-32B and Qwen3-235B-A22B.** On-policy phase: student "aligns its logits with those of a teacher model (Qwen3-32B or Qwen3-235B-A22B) to minimize the KL divergence." |
| Where | **Post-training, not pretraining.** Base models are still pretrained on 36T; distillation replaces the expensive 4-stage RL *post-training* (long-CoT cold start → reasoning RL → thinking-mode fusion → general RL) for the small models. |
| Efficiency | Distillation needs **"only 1/10 of the GPU hours compared to the four-stage training method"** and yields *better* quality (higher Pass@1 and Pass@64). This 1/10 ratio is the **only** compute figure published — no absolute GPU-hours, hardware, or dollar cost for any Qwen2.5/Qwen3 model. |

**The lineage, stated by Qwen themselves:** "by leveraging the knowledge from large-scale models, we substantially reduce both the computational costs and the development efforts required for building smaller-scale models." **Translation:** the small Qwen3 models' reasoning quality is literally distilled from the 235B-A22B / 32B teachers' logits. You cannot reproduce a small Qwen3's quality without first having those frontier teachers in hand.

Sources: [Qwen2.5 report arXiv 2412.15115](https://arxiv.org/abs/2412.15115) · [Qwen3 report arXiv 2505.09388](https://arxiv.org/abs/2505.09388) · [HTML](https://arxiv.org/html/2505.09388v1) · [Qwen3 blog](https://qwenlm.github.io/blog/qwen3/).

---

## Cross-family summary

| Family | Small sizes | Tokens (small/flagship) | From scratch? | Teacher (if distilled) | Published cost | Small-model \$ [EST] |
|---|---|---|---|---|---|---|
| **Pythia** | 70M–1.4B | ~300B (all) | ✅ from scratch | — | none (GPU-hrs pub.) | ~\$4K–\$11K |
| **SmolLM2** | 135M–1.7B | 2T / 4T / 11T | ✅ from scratch | — | \$250K (1.7B only) | ~\$4K–\$20K (small) |
| **OLMo 2** | 1B, 7B | ~4T / 4–6.6T | ✅ from scratch | — | none (MWh/CO2 pub.) | ~\$75K (1B) |
| **Qwen2.5** | 0.5B–7B | ~18T (corpus) | ✅ from scratch | — | none | unknown (unpub.) |
| **Qwen3** | 0.6B–14B | ~36T pretrain | pretrain ✅; **post-train distilled** | **Qwen3-235B-A22B + Qwen3-32B** | none (only "1/10 GPU-hr") | **see below** |

---

## Implications for build-vs-rent

**1. A from-scratch small base model is cheap and honest.** If you want a clean ≤1.5B base model on a few hundred billion tokens, the compute floor is genuinely low: Pythia-1.4B = 7,120 A100-hr (**~\$11K [EST]**); an OLMo-style 1B on ~4T tokens is **~\$75K [EST]**; SmolLM2-360M on 4T is **~\$19K [EST]**. None of these carry a hidden teacher. **For a modest internal base model, build is plausibly cheaper than people assume — low-five-figure to mid-five-figure dollars.**

**2. But "cheap small model" off the open market can be a mirage — the distillation hair.** Qwen3 is the clearest case. A Qwen3-1.7B or Qwen3-4B looks nearly free to grab, and its *marginal* post-training cost is tiny (1/10 the GPU-hours of the RL pipeline). **But that 1/10 number is conditional on the teachers already existing.** The small model's reasoning quality is distilled — via logit/KL matching — from **Qwen3-235B-A22B** (235B total / 22B active, pretrained on ~36T tokens) and **Qwen3-32B**. The honest replacement cost of a Qwen3-1.7B is therefore *not* its own little training run; it is **"a 1.7B that rides on a frontier-scale teacher you would also have to train."**

**3. Putting a number on the teacher [EST, low confidence — Qwen publishes no absolute compute].** A 235B-A22B (22B active params) over 36T tokens, costed on active params via `C ≈ 6·N·D`: 6 × 22e9 × 36e12 ≈ **4.75e24 FLOPs**. On H100/H200 at ~40% MFU (~4e14 effective FLOP/s/GPU): ≈ **3.3M GPU-hours → ~\$11.5M [EST]** at \$3.50/GPU-hr — and likely **2–5× higher** once failed runs, data, and the full-params (not just active) attention/routing overhead are counted, so a defensible band is **~\$10M–\$40M+** for the teacher alone. The Qwen3-32B teacher adds roughly **\$5M–\$10M [EST]** on its own.

   So: **the true "replacement cost" of a distilled Qwen3-1.7B is on the order of tens of millions of dollars**, not the ~\$10–20K its own footprint suggests — because you cannot regenerate its quality without the teacher. You get that teacher's distilled value *for free* by renting/downloading. That is an argument *for* renting the distilled model, not building it.

**4. The decision rule that falls out of the hair:**
   - **If the goal is a transparent, controllable, modest-capability base model** (interpretability, domain-specific pretraining, full data provenance, no IP entanglement): **build.** Pythia/OLMo/SmolLM2 prove it's \$10K–\$100K [EST] for ≤1–3B, fully from scratch, no teacher debt.
   - **If the goal is frontier-grade small-model *quality* (reasoning/instruction following):** **rent/download.** That quality in models like Qwen3 is manufactured by distilling a multi-million-dollar teacher you would otherwise have to fund. Trying to "build" that capability from scratch at 1–3B without a teacher will underperform — the whole point of strong-to-weak distillation is that the small-from-scratch path *can't* match it cheaply.

**Confidence & unknowns (flagged honestly):**
- **High confidence:** distillation status of all four families (Pythia/SmolLM2/OLMo from scratch; Qwen3 small models post-train-distilled from 235B-A22B/32B); Pythia GPU-hours; SmolLM2 token counts + the published \$250K for 1.7B; OLMo energy/carbon figures.
- **Medium:** my FLOP-based dollar estimates for SmolLM2-small and OLMo (rule-of-thumb `6ND`, real rate, real MFU — order-of-magnitude reliable).
- **Low:** the Qwen3 *teacher* dollar figure — Qwen publishes **zero** absolute compute; the \$10M–\$40M band is my estimate from active-param FLOPs and should be treated as directional, not precise. Qwen2.5/Qwen3 GPU-hours and hardware are entirely unpublished.
- **Caveat on "rent":** open-weight ≠ unrestricted — check Qwen's license terms before commercial use; the "free teacher" only stays free within license bounds.

# Jaden's Comment Draft

Ok, looking into what we actually wanted to know, though, which is the costs of actual models already trained.

**Pythia**, 3yrs ago, published numbers in terms of hours, and when you use the cost of A100s at the time:
410M \$3.8K of compute
1.0B 7.2K of compute
1.4B 10.7K of compute. 
All 8 of their models for \$204K. They did them sequentially, no distillation.

**SmolLM2** reported by tokens and published the cost of training for only the 1.7B model at \$250K, 1e23 flops. Based on that alone:
1.7B × 11T ≈ 1.1e23 FLOPs (matches the published ~\$250K).
360M × 4T ≈ 8.6e21 FLOPs → ~\$19K
135M × 2T ≈ 1.6e21 FLOPs → ~\$3.6K
They used more tokens than pythia for their models, to explain the price discrepancy. On H100s. Fully from scratch, no distilling.

**OLMo** reported only in terms of power usage and tokens. H100s
OLMo 2 7B burned 131 MWh; at ~0.7 kW/H100 and PUE 1.2 that's ~156K H100-hours → ~\$546K of compute. Costing it the other way (flops) lands in the same ballpark:
7B × 4.05T ≈ 1.7e23 FLOPs → ~\$425K–\$550K
1B × ~4T ≈ 2.4e22 FLOPs → ~\$75K

**Qwen** heavily used distillations so it's not really an apples to apples comparison. But, based on the 36T tokens, perhaps on H200s, for their 22B model, somewhere between \$10m-\$40M. 32B more expensive ofc. That's just for the teacher model, so the actual tiny finetune might've been comparable to the others, idk. They advertised that their distillation process costs like 1/10 the GPU-hour to do, so it could've been cheaper if you don't account for the teacher training.

# Jaden's Summary

I eyeballed the pricing in claude's report based on available cloud sources and it looks correct. The scaling is pretty conservative, too. But it's about 4x the price of real models trained at that size, maybe that's accounted for by bulk pricing or special deals or something, but also our GPU utilization.

It got the amount of tokens we use kinda wrong, thinking it was 2B, we run that many through the model but the dataset is smaller. Other small models use way more tokens to train their models. Pythia used 300B, smollm 2T to 11T, olmo 2-6T, etc. 

Chinchilla says that at our 100M and 1B sizes, we oughta have a dataset of 2B and 20B tokens, but even that's small compared to the several trillion required to have models that anyone would want to use commercially. 

So, Scott's product, to be successful as-is, needs like one hundred thousand times more data, and oughta cost ~\$200k in compute at best.

## Backlinks

- 2026-06-17
