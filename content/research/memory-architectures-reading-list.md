---
title: Memory, fast weights, and serial depth — a reading list
publish: true
date: 2026-08-08
tags:
- ephemeral-weights
- thesis
- fast-weights
description: Built around Do Language Models Need Sleep? (Lee, McLeish, Goldstein,
  Fanti — arXiv 2605.26099), sequenced so each track answers a question the previous
  one raises.
---

# Memory, Fast Weights, and Serial Depth — a reading list

Built around *Do Language Models Need Sleep?* (Lee, McLeish, Goldstein, Fanti — arXiv 2605.26099), sequenced so each track answers a question the previous one raises.

Annotations say **what the paper is for**, not just what it is. Skip freely; the tracks are independent except where noted.

---

## Read first, grok fully — then you're ~80% there

Chosen for *you*: skips what our conversations already covered (the reassociation identity, KV mechanics, hybrid layouts, the sleep paper itself), weights toward your dissertation's vocabulary and your estimation background.

1. ~~**Schlag, Irie & Schmidhuber — "Linear Transformers Are Secretly Fast Weight Programmers"**~~ (ICML 2021). **Read 2026-08-28** — notes in [[linear-transformers-fast-weight-programmers|Linear transformers are fast weight programmers]], audio guide in `papers/`. The conceptual spine. Fast weights as *programmed* memory, delta rule as the write primitive — this is your dissertation's middle tier given its canonical citation and cleanest formulation. You already know the math; read it for the framing you'll write against.
2. **Gu, Dao et al. — "HiPPO"** (arXiv 2008.07669). What *should* a fixed-size memory store? Answer derived, not designed: optimal online polynomial projection of the input history. The one paper in the stack that natively speaks estimation theory, and the connection nobody in your committee's orbit will make for you. Grok the derivation, not just the result.
3. **Dao & Gu — "Transformers are SSMs" (SSD)** (arXiv 2405.21060). Formalizes what we built by hand: attention and SSMs are one operator family, split by structure imposed on the mixing matrix. After this, every architecture in Tracks B and D is a special case, which is exactly what "80% there" means.
4. **Liu et al. — "The Serial Scaling Hypothesis"** (arXiv 2507.12549). The depth-vs-memory axis, stated as a general thesis with the complexity-theory backing (P-completeness, shortcut learning). This is the *why* under the sleep paper, and the frame that makes "consolidation is computation" a defensible dissertation claim rather than a slogan.
5. **McClelland, McNaughton & O'Reilly — "Why There Are Complementary Learning Systems"** (Psych. Review 1995). The two-timescale argument from first principles — *why* fast episodic + slow semantic must coexist (catastrophic interference), not just that brains do it. Your three-tier hierarchy's intellectual ancestor; grok it so your biological framing is load-bearing instead of decorative.

Stop there and you can read everything below as commentary. If you take one more: **Cabannes et al. 2509.24552** — the bypass/curriculum constraint is the most portable design rule for any multi-timescale system you'll build.

---

## Track A — The algebraic core

The question: *why does a fixed-size state exist at all, and what does softmax cost?*

- **Vaswani et al. (2017), "Attention Is All You Need"** — arXiv 1706.03762. Reread §3.2 specifically with the dual-operator view in mind: which matrix is dynamic, and what gets mixed.
- **Bahdanau, Cho & Bengio (2014), "Neural Machine Translation by Jointly Learning to Align and Translate"** — arXiv 1409.0473. Attention as a *patch* on the RNN bottleneck. Worth reading to see how contingent the eventual design was.
- **Katharopoulos et al. (2020), "Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention"** — ICML. ★ The `(QKᵀ)V = Q(KᵀV)` move, made an architecture. Everything about fixed-size state descends from here.
- **Schlag, Irie & Schmidhuber (2021), "Linear Transformers are Secretly Fast Weight Programmers"** — ICML. ★ Names the object: the network *programs* a weight matrix from data, then applies it. The fast/slow weight vocabulary your dissertation uses.
- **Choromanski et al. (2020), "Rethinking Attention with Performers"** — arXiv 2009.14794. Random-feature approximation of the softmax kernel. Read this to make concrete why exp() has no finite feature map — the whole "cache = infinite-dimensional feature map stored exactly" point.
- **Hebb (1949), *The Organization of Behavior*** — you don't need the book; you need the phrase. Outer-product association is the oldest idea in the stack.

---

## Track B — The SSM lineage (your control-theory home turf)

The question: *where did the ABCD machinery come from and why did it get abandoned?*

- **Gu, Dao et al. (2020), "HiPPO: Recurrent Memory with Optimal Polynomial Projections"** — arXiv 2008.07669. Start here, not with S4. Derives the state matrix as *optimal online function approximation* — a principled answer to "what should a fixed-size memory store?" This is the paper most directly in dialogue with your estimation background.
- **Gu, Goel & Ré (2021), "Efficiently Modeling Long Sequences with Structured State Spaces" (S4)** — arXiv 2111.00396. The LTI system, the convolution equivalence, the parallel training trick.
- **Gu & Dao (2023), "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"** — arXiv 2312.00752. Breaks LTI on purpose: input-dependent B, C, Δ. Time-varying system, selective gating, parallel scan instead of convolution. Read §3.3 on the hardware-aware scan.
- **Blelloch (1990), "Prefix Sums and Their Applications"** — tech report. The scan itself. Short, and it makes "parallelizable via scans" stop being a slogan: associativity of the transition-pair composition operator is the whole trick, and it holds *only* because the recurrence is linear.
- **Dao & Gu (2024), "Transformers are SSMs: Generalized Models and Efficient Algorithms through Structured State Space Duality"** — arXiv 2405.21060. ★ The unification. An SSM *is* a structured (semiseparable, decaying, masked) attention matrix. Read this after Track A so both directions of the duality land at once.
- **Yang et al. (2023), "Gated Linear Attention Transformers with Hardware-Efficient Training"** — arXiv 2312.06635.
- **Yang, Wang et al. (2024), "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"** — NeurIPS 37. The delta rule made trainable at scale.
- **Yang, Kautz & Hatamizadeh (2024), "Gated Delta Networks: Improving Mamba2 with Delta Rule"** — arXiv 2412.06464. GDN — the actual SSM in the sleep paper. Read the update rule as an innovation/LMS step and the connection to RLS writes itself.

> **Estimation-theory sidebar.** The delta rule is recursive least squares with a fixed scalar gain instead of a Riccati-propagated one; the forget gate is exponential forgetting from fading-memory filtering. If you want the classical reference to cite alongside: Ljung, *System Identification: Theory for the User*, ch. 11 (recursive methods). Worth one paragraph in your related-work — nobody in the ML-side literature says it cleanly.

---

## Track C — What a fixed state costs

The question: *what exactly is lost, and is it capacity or something else?*

- **Jelassi et al. (2024), "Repeat After Me: Transformers are Better than State Space Models at Copying"** — arXiv 2402.01032. The canonical capacity-limit result. This is the position the sleep paper is arguing *against* as a complete explanation.
- **Arora et al. (2024), "Simple Linear Attention Language Models Balance the Recall-Throughput Tradeoff" (Based)** — arXiv 2402.18668. The recall-vs-throughput Pareto frontier, stated as a law rather than an anecdote. Also the cleanest treatment of "just make the state bigger" and where that curve goes.
- **Noroozizadeh et al. (2025), "Deep Sequence Models Tend to Memorize Geometrically; It Is Unclear Why"** — arXiv 2510.26745. Directly relevant to your skepticism about clean structure emerging. The field admitting it doesn't know when geometric solutions appear.
- **Merrill & Sabharwal (2025), "A Little Depth Goes a Long Way: The Expressive Power of Log-Depth Transformers"** — arXiv 2503.03961. Expressivity as a function of depth — the formal backing for "depth is the scarce resource."

---

## Track D — Hybrids

The question: *what do people actually build, and why two tiers?*

- **Ren et al. (2024), "Samba: Simple Hybrid State Space Models for Efficient Unlimited Context Language Modeling"** — arXiv 2406.07522. The SWA + Mamba recipe. The sleep paper's N=1 baseline in §6.4 is essentially this.
- **De et al. (2024), "Griffin: Mixing Gated Linear Recurrences with Local Attention"** — arXiv 2402.19427.
- **Dong et al. (2024), "Hymba: A Hybrid-Head Architecture for Small Language Models"** — arXiv 2411.13676. Parallel rather than interleaved heads — a different answer to the same layout question.
- **Gu, Hu et al. (2025), "Jet-Nemotron: Efficient Language Model with Post Neural Architecture Search"** — arXiv 2508.15884. One of the two models fine-tuned in §6.3.
- **NVIDIA (2025), "Nemotron Nano 2"** — arXiv 2508.14444. Hybrid at production scale.
- **Bick et al. (2024), "Transformers to SSMs: Distilling Quadratic Knowledge to Subquadratic Models" (MOHAWK)** — NeurIPS 37, and **Wang et al. (2024), "The Mamba in the Llama"** — NeurIPS 37. The attention→hybrid conversion recipes; the SSM-only warm-up stage in §6.4 comes from this line.
- **Cabannes et al. (2025), "Short Window Attention Enables Long-Term Memorization"** — arXiv 2509.24552. The underutilization phenomenon the sleep paper cites for its warm-up fix. Generalizes into a real curriculum principle: *a tier that can be bypassed by a faster tier won't train unless you handicap the bypass.* Directly load-bearing for a multi-timescale design.

---

## Track E — Depth-recurrence and serial compute

The question: *where does sequential computation come from if not from tokens?*

- **Dehghani et al. (2018), "Universal Transformers"** — arXiv 1807.03819. Depth-recurrence, and Turing-completeness as the motivation.
- **Graves (2016), "Adaptive Computation Time for Recurrent Neural Networks"** — arXiv 1603.08983. Learned halting.
- **Bai, Kolter & Koltun (2019), "Deep Equilibrium Models"** — NeurIPS 32. Implicit differentiation through a fixed point — O(1) memory in depth. The principled answer to the BPTT blowup the sleep paper flags in §7.
- **Schwarzschild et al. (2021), "Can You Learn an Algorithm? Generalizing from Easy to Hard Problems with Recurrent Networks"** — NeurIPS 34, and **Bansal et al. (2022), "End-to-End Algorithm Synthesis with Recurrent Networks"** — NeurIPS 35. Recurrence buying *extrapolation* to harder instances at test time.
- **Geiping et al. (2025), "Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach" (Huginn)** — NeurIPS. ★ Depth-recurrence trained from scratch at scale.
- **Zhu et al. (2025), "Scaling Latent Reasoning via Looped Language Models" (Ouro)** — arXiv 2510.25741. The other model in §6.3. Note the confound: Ouro's native pretrained depth is 4, matching the paper's N=4 ceiling.
- **McLeish et al. (2025), "Teaching Pretrained Language Models to Think Deeper with Retrofitted Recurrence"** — arXiv 2511.07384. Retrofitting rather than pretraining; also the source of the middle-block looping convention and the Muon setup.
- **Prairie et al. (2026), "Parcae: Scaling Laws for Stable Looped Language Models"** — arXiv 2604.12946, and **Schwethelm et al. (2026), "How Much is One Recurrence Worth? Iso-Depth Scaling Laws"** — arXiv 2604.21106. The exchange rate between recurrence and parameters. Read if you need to *budget* depth rather than just add it.
- **Liu et al. (2022), "Transformers Learn Shortcuts to Automata"** — arXiv 2210.10749. Why parallel models fake sequential tasks, and how the fake breaks.
- **Liu et al. (2025), "The Serial Scaling Hypothesis"** — arXiv 2507.12549. ★ The thesis statement for this whole track.
- **Neary & Woods (2006), "P-completeness of Cellular Automaton Rule 110"** — ICALP, and **Cook (2004), "Universality in Elementary Cellular Automata"** — *Complex Systems* 15(1). The formal basis for "no parallel shortcut." Skim for the statement, not the proof; the useful fact is that P-complete + (conjectured) P ≠ NC means no polylog-depth circuit exists.

---

## Track F — Moving context into weights

The question: *what else has been tried for the same job, and how does sleep differ?*

**Compression (keep it in attention, but smaller):**
- Ge et al. (2023), "In-Context Autoencoder for Context Compression" — arXiv 2307.06945.
- Eyuboglu et al. (2025), "Cartridges: Lightweight and General-Purpose Long Context Representations via Self-Study" — arXiv 2506.06266. ★ Offline amortization done well; the closest cousin in spirit.

**Distillation (push it into parameters via a loss):**
- Snell, Klein & Zhong (2022), "Learning by Distilling Context" — arXiv 2209.15189.
- Askell et al. (2021), "A General Language Assistant as a Laboratory for Alignment" — arXiv 2112.00861 (§ context distillation).
- Chen et al. (2024), "Generative Adapter" — arXiv 2411.05877.
- Cao, Cai & Lam (2025), "InfiniteICL" — arXiv 2504.01707.
- Caccia et al. (2025), "Training Plug-n-Play Knowledge Modules with Deep Context Distillation" — arXiv 2503.08727.
- Tack et al. (2024), "Online Adaptation of Language Models with a Memory of Amortized Contexts" — arXiv 2403.04317.

**Test-time training (gradient steps as the memory write):**
- Sun et al. (2024), "Learning to (Learn at Test Time): RNNs with Expressive Hidden States" — arXiv 2407.04620. The state *is* a model; the update *is* SGD.
- Tandon et al. (2025), "End-to-End Test-Time Training for Long Context" — arXiv 2512.23675. The paper's explicit foil: one gradient step per chunk, fixed CE objective.
- Zhang et al. (2026), "Training Large Reasoning Models Efficiently via Progressive Thought Encoding" — arXiv 2602.16839. LoRA-per-chunk, RL setting.

> **The distinction worth holding:** compression and Cartridges keep the result *inside attention* (a shorter cache); TTT and sleep push it into *weights*. And sleep's update rule is *learned* (a recurrent forward pass) rather than a predetermined gradient step on a fixed scalar loss. That's the axis on which its novelty actually sits.

---

## Track G — Sleep, replay, consolidation

The question: *how much of the biological framing is load-bearing versus decorative?*

- **McClelland, McNaughton & O'Reilly (1995), "Why There Are Complementary Learning Systems in the Hippocampus and Neocortex"** — *Psychological Review* 102(3). ★ The canonical fast/slow two-system argument. If your dissertation cites one neuroscience paper, it's this one.
- **Rasch & Born (2013), "About Sleep's Role in Memory"** — *Physiological Reviews*. The survey. Note that biological consolidation is *generative*, not a copy — replay produces trajectories never experienced. Relevant to the "is this really consolidation?" argument.
- **Momennejad et al. (2018), "Offline Replay Supports Planning in Human Reinforcement Learning"** — *eLife* 7:e32548. Offline compute as amortization, with human neural evidence.
- **Hinton et al. (1995), "The Wake-Sleep Algorithm for Unsupervised Neural Networks"** — *Science* 268. The ML-side ancestor of the metaphor.
- **Lin et al. (2025), "Sleep-Time Compute: Beyond Inference Scaling at Test-Time"** — arXiv 2504.13171. Offline precomputation of anticipated queries. The "sleep as amortization" reading, at the token level rather than the weight level.
- **Behrouz, Hashemi & Mirrokni, "Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories"** — OpenReview. The title-collision paper. Different mechanism (RL, parameter expansion, distillation, synthetic data) — worth reading precisely because it's the nearest competitor.
- **Behrouz et al. (2025), "Titans: Learning to Memorize at Test Time"** — arXiv 2501.00663. Surprise-gated memory writing; the same team's broader program.
- **Chalvidal, Serre & VanRullen (2022), "Meta-Reinforcement Learning with Self-Modifying Networks"** — NeurIPS 35. Recursive Hebbian updates for fast adaptation.
- **Sutton (1991), "Dyna"**; **Ha & Schmidhuber (2018), "World Models"**; **Hafner et al. (2019), "Dreamer"** — the RL branch of the sleep metaphor, if you want the full genealogy. Optional.

---

## Track H — Tasks and evaluation

Read these when you need to *design* a probe rather than understand one.

- **Allen-Zhu, "Physics of Language Models: Part 4.1 — Architecture Design and the Magic of Canon Layers"** — source of Depo, and the budget-controlled-synthetic methodology generally. The methodological argument (fixed token budget exposes trends early) is worth more than the specific task.
- **Zhou et al. (2025), "GSM-Infinite"** — ICML workshop. Procedurally generated, independently controls length and operation count.
- **Hsieh et al. (2024), "RULER"** — COLM. The retrieval-focused contrast case.
- **Kabra et al. (2026), "Learning from Synthetic Data Improves Multi-Hop Reasoning"** — ICLR. Justifies that GSM-Infinite training transfers.
- **Cobbe et al. (2021), "Training Verifiers to Solve Math Word Problems" (GSM8K)** — arXiv 2110.14168. The ancestor.

---

## The gap this list points at

Nothing above consolidates **fast weights into slow weights**. The sleep paper moves KV cache → fast weights and learns the transfer operator end-to-end; pretraining moves corpus → slow weights by SGD. The third transfer — the one that would make the hierarchy actually recursive — is unoccupied territory.

Adjacent literature to raid when you go there: continual learning and consolidation-as-regularization (EWC and successors), the Cartridges/context-distillation line (Track F) for "context → parameters" precedents at a slower timescale, and Track C on what makes a representation worth promoting at all.

Open questions worth writing down while they're fresh:

1. **Is sleep consolidation or latent CoT?** It computes facts never present in the input, so the honest description is scratchpad-in-fast-weights. The consolidation framing is strongest on Depo (query-agnostic, must restructure) and weakest on the automaton (fixed `t`, can precompute the answer). GSM-Infinite puts the question *before* the context, which quietly converts eager commitment back into query-conditioned deferral.
2. **What does the model actually build for Depo?** The graceful degradation with hop count suggests a smeared approximate successor map, not binary lifting / clean partial transitive closure. Testable with probes.
3. **The Ouro N=1 confound.** Ouro's native depth is 4; its no-loop baseline may be artificially depressed. The missing Jet replication of §6.4 is the experiment that would settle it.
4. **Curriculum constraint from Cabannes/§6.4.** Any memory tier that a faster tier can bypass probably won't train unless you handicap the bypass during its formation phase. This is a general design rule for multi-timescale systems, not an implementation detail.

---

## Suggested order

If starting cold: **A → B → D** gets you architecturally literate. **C** then tells you what's broken. **E** tells you why the fix isn't more memory. **F and G** are the related-work sweep. **H** only when writing experiments.

Given what you've already covered — Track A and D are largely done in conversation; the highest-marginal-value reads are **HiPPO** (for the estimation connection nobody else will make), **SSD** (for the duality, formally), **the Serial Scaling Hypothesis** (for the thesis framing), and **Cabannes** (for the curriculum constraint).

## Backlinks

- 2026-08-08
