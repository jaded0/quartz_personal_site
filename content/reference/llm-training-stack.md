---
title: The LLM training stack, by abstraction tier
description: Where Megatron, DeepSpeed, Lightning, Accelerate, Composer, NeMo and
  HF Transformers actually sit relative to each other — five abstraction tiers, from
  raw PyTorch ops up to end-to-end RLHF recipes.
publish: true
---

## 🧱 Abstraction Tiers for Modern LLM Training Frameworks

|Tier|Name|Core Concept|Responsibilities|
|---|---|---|---|
|**T0**|**PyTorch Primitives**|Direct tensor and distributed ops|Custom autograd, manual DDP, NCCL calls, writing your own optimizer loops|
|**T1**|**Parallelism & Efficiency Engine**|Extend PyTorch for sharding, offloading, parallelization, kernel fusion, memory efficiency|FSDP, ZeRO, DeepSpeed engine, Megatron tensor/pipeline parallelism|
|**T2**|**Training Loop Orchestration**|High-level trainer abstractions that manage optimizer steps, checkpointing, logging, precision, distributed setup|Lightning Trainer, Composer Engine, Accelerate, Fabric|
|**T3**|**Model & Task Ecosystem Layer**|Predefined architectures, configs, data loaders, tokenizers, etc.|NeMo, Transformers|
|**T4**|**Pipeline / Full-Stack Layer**|End-to-end recipes (RLHF, MoE, evaluation, inference, serving)|DeepSpeed-Chat, MII, NeMo-Megatron pipelines, HF RLHF toolkit|

---

## ⚙️ Where Each Framework Lives (Now Including MosaicML Composer)

|Framework|T0|T1|T2|T3|T4|Key Roles & Design Philosophy|
|---|---|---|---|---|---|---|
|**Megatron-Core**|⚪ partial|🟢 **Primary**|⚪|⚪|⚪|Focused on fused kernels, tensor/pipeline/expert parallelism; low-level optimization layer; forms NeMo’s “muscle.”|
|**DeepSpeed**|⚪|🟢 **Primary**|🟢|⚪|🟢 partial|Extends PyTorch for ZeRO/FSDP-like scaling, MoE, offload (GPU/CPU/NVMe), inference, RLHF (Chat); spans T1→T2→T4.|
|**Lightning (Trainer)**|⚪|⚪ partial|🟢 **Primary**|⚪|⚪|Abstracts loops, logging, callbacks; strategy system supports FSDP/DS/TorchElastic backends; high developer ergonomics.|
|**Lightning Fabric**|⚪|🟢|🟢|⚪|⚪|Thin “bring-your-own-loop” layer providing DDP/FSDP launch, mixed precision, checkpointing — sits between raw PyTorch & Lightning Trainer.|
|**Hugging Face Accelerate**|⚪|🟢|🟢|⚪|⚪|Ultra-light orchestration; you keep your training loop, it handles device setup, distributed, mixed precision. Integrates seamlessly with Transformers/DeepSpeed.|
|**MosaicML Composer**|⚪|🟢|🟢 **Primary**|⚪|⚪|Built around **speed-centric, pluggable training algorithms** (“speedups”) — gradient clipping, selective recompute, layer freezing, EMA, etc. Pure PyTorch interface, no model zoo. Often paired with FSDP or DeepSpeed under the hood.|
|**NeMo**|⚪ partial|🟢|🟢|🟢 **Primary**|🟢 partial|NVIDIA’s full ecosystem (configs, tokenizer, pretrained GPT, TTS, ASR); orchestrates Megatron-Core or DeepSpeed via YAML configs.|
|**HF Transformers**|⚪|⚪|⚪|🟢 **Primary**|⚪ partial|Model/task library layer. Uses Accelerate or Trainer underneath for orchestration.|
|**DeepSpeed Chat / MII**|⚪|🟢|🟢|🟢|🟢 **High**|End-to-end RLHF and inference frameworks; built directly atop DeepSpeed engine.|
|**HF Trainer (transformers.Trainer)**|⚪|⚪|🟢|🟢|⚪|Higher-level loop for HF models; can delegate to DS/FSDP via config.|

# existing projects
Full Projects:
- Pythia (eleutherAI)
- OpenLLaMa (not meta)
- llm-foundry (mosaicML, databricks)

graphics
![[attachments/Pasted image 20250922135333.png]]

![[attachments/Pasted image 20250922135351.png]]![[attachments/Pasted image 20250922140425.png]]
