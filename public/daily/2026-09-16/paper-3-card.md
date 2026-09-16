> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **标题**: Orthogonal JEPA: Factorized Predictive States for Latent World Models  
- **作者**: Taoyong Cui, Pheng Ann Heng, Wanli Ouyang  
- **机构**: The Chinese University of Hong Kong (CUHK)  
- **来源**: arXiv preprint (2026-08-20), no peer-reviewed venue stated [Paper: PDF p. 1]  
- **核心方法**: Orthogonal JEPA — a latent world-modeling framework based on orthogonal predictive factorization of target states  
- **Key innovation**: Replaces monolithic JEPA target embedding with K orthogonal basis matrices $B_k \in \mathbb{R}^{d \times r}$, enabling factorized prediction and synthesis via Moore–Penrose pseudoinverse [Paper: PDF p. 3–4]  
- **Evaluation domains**: controlled vision, single-cell transcriptomics, longitudinal health records, continuous control (MuJoCo), molecular dynamics [Paper: PDF p. 1, 5]  
- **Code/data availability**: Not mentioned in text → 未核验  

## 02 一句话总结  
Orthogonal JEPA decomposes a latent target state $z_t$ into $K$ orthogonal components via learned basis matrices $B_k$, predicts each component from a shared context representation $z_c$ using dedicated branches $q_k$, synthesizes the full predicted state $\hat{z}_t = (B^\top)^\dagger \hat{u}_t$, and regularizes orthogonality, factor activity, and encoder coordinate variance — all while retaining JEPA’s context–target interface across diverse domains including single-cell transcriptomics [Paper: PDF p. 1–5].

## 03 研究问题  
- How can latent world models avoid capacity misallocation in complex systems where dominant signals suppress weaker but structurally relevant predictive structure? [Paper: PDF p. 1–2]  
- Can predictive-state learning be improved by replacing monolithic target embedding with orthogonal, factorized prediction pathways? [Paper: PDF p. 2]  
- Does orthogonal predictive factorization generalize across observation geometries (temporal, spatial, biological, molecular) while preserving downstream utility (clustering, perturbation prediction, forecasting, planning, rollout)? [Paper: PDF p. 1, 5]

## 04 研究背景与发展路径  
- **Precursor**: Joint-embedding predictive architectures (JEPAs) learn latent states by predicting targets in representation space rather than reconstructing raw observations — avoiding noise overfitting and enabling abstraction [Paper: PDF p. 1–2].  
- **Limitation of standard JEPA**: Uses one target embedding and one prediction pathway; leads to redundant capacity allocation to dominant signals and weak/conflicting gradients for less dominant structure [Paper: PDF p. 1–2].  
- **Prior regularization ideas**: Barlow Twins [9] and VICReg [10] perform redundancy reduction on embeddings, but Orthogonal JEPA applies orthogonality *directly on predictive target coordinates*, not just statistics [Paper: PDF p. 4].  
- **Biological grounding**: Builds on Cell-JEPA [15], which uses masked gene expression prediction to learn cell-level latent states; Orthogonal JEPA factorizes its monolithic target [Paper: PDF p. 6].  
- **Technical lineage**: Inherits EMA target encoder [Paper: PDF p. 3, Eq. 2], token-based adapters [Paper: PDF p. 3], and readout/planning interfaces from prior world-modeling work [1, 2, 15] — but introduces factorized analysis/synthesis as core novelty.

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|--------------------------|
| Monolithic target capacity allocation | Dominant signals (e.g., high-variance visual patches, highly expressed genes) consume disproportionate optimization budget, suppressing gradients for weaker but structurally meaningful predictive structure | “In complex systems, this monolithic state can allocate redundant capacity to dominant signals while providing weak or conflicting gradients to less dominant predictive structure” [Paper: PDF p. 1] | Abstract, p. 1; Introduction, p. 2 |
| Lack of geometric separation in target space | Multiple latent directions serve similar roles; optimization conflates distinct predictive factors | “When these signals share a monolithic target, easily predicted or high-variance structure may dominate optimization, multiple latent directions may serve similar roles” [Paper: PDF p. 2] | p. 2 |
| Encoder coordinate collapse | Online encoder outputs degenerate to low-variance or zero-variance dimensions, harming downstream discriminability | “online variance regularization discourages coordinate-wise encoder collapse” [Paper: PDF p. 1]; L<sub>enc</sub> explicitly penalizes low σ<sup>enc</sup><sub>j</sub> [Paper: PDF p. 4–5, Eq. 9] | p. 1, 4–5 |
| Factor inactivity | Projected target components $z^{(k)}_t$ may exhibit near-zero empirical variance across mini-batch, rendering corresponding prediction branches irrelevant | “Factor-activity regularization maintains variation in projected targets” [Paper: PDF p. 1]; L<sub>fac</sub> penalizes σ<sup>fac</sup><sub>k,j</sub> < γ<sub>fac</sub> [Paper: PDF p. 4–5, Eq. 9] | p. 1, 4–5 |
| Synthesis instability | Poor conditioning of basis matrix $B$ causes error amplification during repeated autoregressive rollout | “State synthesis also depends on the conditioning of $B$; monitoring singular values is important when synthesized states are repeatedly fed into a rollout” [Paper: PDF p. 8] | Discussion, p. 8 |

## 06 核心思想  
Orthogonal JEPA treats latent-state design as a *capacity-allocation problem*: instead of compressing all predictable structure into one vector, it *analyzes* the target state $z_t$ into $K$ orthogonal components $z^{(k)}_t = B_k^\top \text{sg}(z_t)$, *predicts* each component independently from shared context $z_c$, then *synthesizes* them back into a full state $\hat{z}_t = (B^\top)^\dagger \hat{u}_t$ — all governed by four co-optimized objectives: predictive regression ($L_{\text{pred}}$), orthogonality ($L_{\text{orth}}$), factor activity ($L_{\text{fac}}$), and encoder variance ($L_{\text{enc}}$) [Paper: PDF p. 1–5]. This factorization is *domain-agnostic*: same mechanism applies whether target is future time step, masked spatial patch, complete cell state, or molecular configuration [Paper: PDF p. 1, 3, Table 1].

## 07 方法总览  
Orthogonal JEPA operates in four phases:  
1. **Context–target interface**: Domain adapter $A_\delta$ maps raw input $x$ to tokens $H$ and structural descriptors $S$; view sampler $V_\delta$ selects context indices $C$ and target indices $T$ → yields $(H_C, S_C, T, S_T)$ [Paper: PDF p. 3, Eq. 1].  
2. **Orthogonal factorization**: Target state $z_t = f_{\bar{\theta}}(H,S)_t$ (EMA-updated) is analyzed via $K$ trainable basis matrices $B_k$: $z^{(k)}_t = B_k^\top \text{sg}(z_t)$ [Paper: PDF p. 3, Eq. 3].  
3. **Factorized prediction & synthesis**: Each $z^{(k)}_t$ is predicted by branch $q_k(z_c, s_t)$ → concatenated $\hat{u}_t$ → synthesized $\hat{z}_t = (B^\top)^\dagger \hat{u}_t$ [Paper: PDF p. 3–4, Eqs. 4–5].  
4. **Multi-objective regularization**: $L_{\text{OJEPA}} = L_{\text{pred}} + \lambda_{\text{orth}} L_{\text{orth}} + \lambda_{\text{fac}} L_{\text{fac}} + \lambda_{\text{enc}} L_{\text{enc}}$ [Paper: PDF p. 5, Eq. 10].  
All experiments fix adapter, encoder, data split, and optimization budget — only vary monolithic vs. orthogonal target design [Paper: PDF p. 5].

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Domain adapter $A_\delta$** | Maps raw observation $x$ to tokens $H$ and structural descriptors $S$ (e.g., patch coordinates, gene IDs, time stamps) | Enables unified interface across domains with heterogeneous input geometry | $x \to (H, S)$ | Table 1 lists system-specific adapters; “Each application chooses an adapter” [Paper: PDF p. 2, 3] | Breaks cross-domain generalization; e.g., scGPT backbone requires gene-tokenization [Paper: PDF p. 6] |
| **View sampler $V_\delta$** | Selects context indices $C$ and target indices $T$ (e.g., masked patches, unmasked genes, future time steps) | Defines context–target relation critical for predictive learning | $(H,S) \to (H_C, S_C, T, S_T)$ | Eq. 1 formalizes this mapping; Table 1 shows concrete instantiations [Paper: PDF p. 3] | No context–target pair → no JEPA objective; e.g., single-cell task fails without masking [Paper: PDF p. 6] |
| **Orthogonal basis $B_k$** | Analyzes target $z_t$ into $K$ orthogonal components $z^{(k)}_t = B_k^\top \text{sg}(z_t)$ | Enforces geometric separation of predictive factors; enables independent branch training | $z_t \in \mathbb{R}^d \to \{z^{(k)}_t \in \mathbb{R}^r\}_{k=1}^K$ | Eq. 3; Proposition 1 proves exact decomposition under orthogonality [Paper: PDF p. 3–4] | Loss of factor independence → gradient interference; Table 2/3 show performance drop without orthogonality [Paper: PDF p. 6–7] |
| **Factor predictors $q_k$** | Maps shared context $z_c$ to predicted component $\hat{z}^{(k)}_t$ | Allows dedicated capacity per predictive factor; avoids monolithic bottleneck | $z_c, s_t \to \hat{z}^{(k)}_t \in \mathbb{R}^r$ | Eq. 4; “a dedicated prediction branch estimates each component” [Paper: PDF p. 1] | Reduced capacity per factor → degraded fine-grained prediction (e.g., lower INJ in Table 2) [Paper: PDF p. 6] |
| **State synthesizer $(B^\top)^\dagger$** | Recombines predicted components $\hat{u}_t$ into full $\hat{z}_t$ | Enables downstream use (readout, planner, decoder) requiring full-state representation | $\hat{u}_t \in \mathbb{R}^d \to \hat{z}_t \in \mathbb{R}^d$ | Eq. 5; “Predicted components are synthesized into a complete latent state” [Paper: PDF p. 1] | No synthesis → no unified state for planning/rollout; Table 5/6 require $\hat{z}_t$ for CEM/Molecular rollout [Paper: PDF p. 7–8] |
| **Variance regularizers $L_{\text{fac}}, L_{\text{enc}}$** | Penalize low empirical std dev of projected targets ($\sigma^{\text{fac}}_{k,j}$) and context encoder outputs ($\sigma^{\text{enc}}_j$) | Prevents factor inactivity and coordinate collapse — critical for stable representation learning | Mini-batch statistics → scalar loss | Eq. 9; “factor-activity regularization maintains variation… online variance regularization discourages coordinate-wise encoder collapse” [Paper: PDF p. 4–5] | Without $L_{\text{fac}}$: inactive factors → wasted capacity; without $L_{\text{enc}}$: collapsed encoder → poor clustering (PBMC AvgBIO ↓ in Table 3) [Paper: PDF p. 4–6] |

## 09 关键公式与符号  

| ID | Formula | Meaning | Constraints / Notes | Source |
|----|---------|---------|---------------------|--------|
| Eq. 1 | $\xrightarrow{(H, S)} V_\delta \rightarrow (H_C, S_C, T, S_T)$ | Context–target sampling pipeline | $C \subset \Omega$, $T \subset \Omega$; domain-adapter output fed to sampler | [Paper: PDF p. 3] |
| Eq. 2 | $\bar{\theta} \leftarrow m\bar{\theta} + (1-m)\theta,\ 0 \leq m < 1$ | Exponential moving average update for target encoder | EMA parameters receive no gradients; stabilizes target representation | [Paper: PDF p. 3] |
| Eq. 3 | $z^{(k)}_t = B_k^\top \text{sg}(z_t),\ k = 1, \dots, K$ | Orthogonal analysis of target state | Stop-gradient on $z_t$; $B_k \in \mathbb{R}^{d \times r}, Kr=d$; $B_k$ trainable | [Paper: PDF p. 3] |
| Eq. 4 | $\hat{z}^{(k)}_t = q_k(z_c, s_t)$ | Factor-specific prediction | Shared context $z_c = f_\theta(H_C, S_C)$; $s_t$ optional descriptor | [Paper: PDF p. 3] |
| Eq. 5 | $\hat{z}_t = (B^\top)^\dagger \hat{u}_t$ | State synthesis via pseudoinverse | $B = [B_1, \dots, B_K] \in \mathbb{R}^{d \times d}$; exact if $B$ orthogonal → $\hat{z}_t = \sum_k B_k \hat{z}^{(k)}_t$ | [Paper: PDF p. 4] |
| Eq. 8 | $z = \sum_{k=1}^K B_k B_k^\top z$ | Exact orthogonal reconstruction identity | Holds iff $B_i^\top B_j = 0\ (i \neq j),\ B_k^\top B_k = I_r,\ Kr=d$ (Proposition 1) | [Paper: PDF p. 4] |
| Eq. 10 | $L_{\text{OJEPA}} = L_{\text{pred}} + \lambda_{\text{orth}} L_{\text{orth}} + \lambda_{\text{fac}} L_{\text{fac}} + \lambda_{\text{enc}} L_{\text{enc}}$ | Core multi-objective loss | $L_{\text{pred}}$: MSE per factor; $L_{\text{orth}}$: within/between-factor orthogonality; $L_{\text{fac}}, L_{\text{enc}}$: hinge-loss variance penalties | [Paper: PDF p. 5] |

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| Controlled visual binding (Table 2) | Orthogonal factorization improves frozen-state binding quality beyond monolithic JEPA | DINOv3/SigLIP2 backbones; identical data/masks/readout; learned-grid readout fixed; compare Standard JEPA vs. Orthogonal JEPA | Orthogonal JEPA ↑ INJ (+0.009 DINOv3, +0.007 SigLIP2), ↓ Coll. (−0.009, −0.011), ↑ Rec. (+0.014, +0.010) | Orthogonal factorization enhances structured readout fidelity in vision | Does *not* prove semantic disentanglement — authors note orthogonality ≠ statistical independence [Paper: PDF p. 4, 8] | [Paper: PDF p. 6, Table 2] |
| Single-cell clustering & perturbation (Table 3) | Orthogonal JEPA improves zero-shot and finetuned cell-state representation for clustering and perturbation response | scGPT backbone; 800K kidney cells pretraining; PBMC-10K clustering; Adamson/Norman perturbation datasets; same masked-gene term | Orthogonal JEPA ↑ PBMC finetuned AvgBIO (+0.0171), ↑ zero-shot AvgBIO (+0.0258), ↑ Norman Pearson (+0.011), ↑ Adamson Pearson (+0.005) | Orthogonal factorization yields more robust and transferable single-cell latent states | Does *not* identify biological meaning of factors — “factor interpretation requires additional probes” [Paper: PDF p. 8] | [Paper: PDF p. 6, Table 3] |
| Clinical event forecasting (Table 4) | Orthogonal JEPA improves forecasting of >1,000 future clinical events | Same patient history encoder; EMA future-state encoder; shared decoder; mean PRAUC metric | Orthogonal JEPA ↑ Mean PRAUC (+0.007) vs. Standard JEPA (0.711→0.718) | Orthogonal factorization benefits high-cardinality clinical forecasting | Does *not* show improvement over non-JEPA baselines (e.g., Delphi +0.029) — JEPA family itself provides larger gain | [Paper: PDF p. 7, Table 4] |
| MuJoCo CEM planning (Table 5) | Orthogonal JEPA improves planning return in state-based control | Offline training on 500 random-action trajectories; same MLP backbone; CEM with 8-step horizon | Orthogonal JEPA ↑ Walker2d return (+40.2), ↑ InvertedPendulum (+12.5); HalfCheetah modest gain (−2.7→−8.5) | Orthogonal factorization enhances latent dynamics stability for planning | Does *not* demonstrate superiority in pixel-based closed-loop control — authors note this as future test [Paper: PDF p. 8] | [Paper: PDF p. 7, Table 5] |
| Molecular dynamics rollout (Table 6) | Orthogonal JEPA improves long-horizon stability in force-free molecular forecasting | TrajCast backbone; same equivariant architecture/data; 100-step autoregressive rollout; MAE/RMSD metrics | Orthogonal JEPA ↓ Water RMSD (2.536→2.459), ↓ Paracetamol RMSD (1.868→1.846), ↓ Benzene RMSD (0.0701→0.0699) | Orthogonal factorization improves autoregressive rollout fidelity in molecular systems | Does *not* prove causal factor discovery — “orthogonality is geometric… does not imply causal modularity” [Paper: PDF p. 8] | [Paper: PDF p. 8, Table 6] |

## 11 对结论的正确理解  
- Orthogonal JEPA is *not* a new architecture family but a *target-space factorization mechanism* that can be retrofitted onto existing JEPA pipelines (Cell-JEPA, TrajCast-JEPA) [Paper: PDF p. 1, 6–8].  
- Performance gains (Tables 2–6) reflect *improved predictive-state quality*, not necessarily better raw reconstruction — consistent with JEPA’s design philosophy of focusing on predictable structure [Paper: PDF p. 1–2].  
- “Orthogonal” refers to *learned basis geometry*, not guaranteed semantic disentanglement: Proposition 1 guarantees norm preservation under exact orthogonality, but empirical evaluation is required for interpretability [Paper: PDF p. 4, 8].  
- The method separates *predictive-state mechanism* from *domain interface*: Table 1 confirms identical mathematical form across vision, single-cell, clinical, control, and molecular tasks — only adapter, sampler, and encoder change [Paper: PDF p. 3].  
- Gains are *modest but consistent*: +0.007–+0.026 absolute improvements across metrics, suggesting orthogonal factorization is a reliable *regularization strategy*, not a revolutionary capacity boost [Paper: PDF p. 6–8].

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| Orthogonality ≠ statistical independence | “Geometric separation alone does not imply statistical independence or semantic disentanglement; these properties require empirical evaluation” | “Factor interpretation therefore requires additional probes or ground-truth factor benchmarks” | [Paper: PDF p. 4] |
| Variance regularizers insufficient for full-rank covariance | “The variance regularizers constrain marginal coordinate variation but do not guarantee full-rank covariance” | “Future work may combine the current objective with covariance or spectral regularization” | [Paper: PDF p. 8] |
| Synthesis instability under ill-conditioned $B$ | “State synthesis also depends on the conditioning of $B$; monitoring singular values is important when synthesized states are repeatedly fed into a rollout” | Implicit: monitor $B$’s singular values during training/rollout | [Paper: PDF p. 8] |
| Deterministic prediction | “The present predictor is deterministic and does not explicitly represent multimodal futures” | Not specified, but implies need for stochastic extensions (e.g., conditional VAE, diffusion) | [Paper: PDF p. 8] |
| Limited regime coverage | “The current experiments span partial observation, forecasting, planning, and rollout, but do not cover every world-model regime” | Proposes tests on “pixel-based closed-loop control, stochastic futures, continuous physical fields, and tasks with known causal factors” | [Paper: PDF p. 8] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| All single-cell experiments use *cell-level* masking and prediction (Cell-JEPA protocol), not gene-level or subcellular factorization | Orthogonal JEPA may merely improve aggregation of masked gene signals rather than discovering biologically meaningful modular factors (e.g., cell-cycle, stress-response modules) | Weakens claim of “factorized predictive states” for biology — could be statistical artifact of improved signal-to-noise in aggregated prediction | Apply Orthogonal JEPA to *gene-level* targets (à la scBERT) and test if factors align with GO terms or perturbation signatures (e.g., CRISPR screens) | [Paper: PDF p. 6, Table 3] cites Cell-JEPA [15] which uses cell-level teacher; no gene-level factor probing reported |
| Tables 2–6 report mean metrics but omit statistical significance testing (e.g., p-values, confidence intervals) across seeds | Observed gains (e.g., +0.007 PRAUC) may not be statistically reliable given small seed counts (3–10) and task variability | Undermines claims of consistent improvement — especially critical for clinical/medical applications where small gains require rigorous validation | Re-run key experiments (e.g., Table 3, 4) with ≥30 seeds and report bootstrapped 95% CIs; apply paired t-test between JEPA variants | [Paper: PDF p. 6] states “averaged over ten seeds” for vision, “three seeds” for control, “five seeds” for molecules — insufficient for strong inference |
| $L_{\text{orth}}$ penalizes both within-factor orthonormality and cross-factor orthogonality, but Proposition 1 assumes exact orthogonality — training uses Frobenius norm penalty, not hard constraint | Empirical $B$ may be poorly conditioned, causing synthesis error amplification not captured in Tables 5–6 (which report final RMSD, not per-step error) | Critical for molecular/clinical rollout where error compounds — Table 6 RMSD improvement may mask early divergence | Log $B$’s condition number $\kappa(B)$ during training; correlate with rollout RMSD; ablate $L_{\text{orth}}$ to measure $\kappa(B)$ impact | [Paper: PDF p. 4] defines $L_{\text{orth}}$ as Frobenius penalty; [p. 8] notes conditioning matters but no empirical $B$ diagnostics shown |
| No ablation of individual regularizers ($L_{\text{fac}}, L_{\text{enc}}$) in results | Observed gains may stem primarily from $L_{\text{pred}} + L_{\text{orth}}$, with $L_{\text{fac}}/L_{\text{enc}}$ acting as mere stabilizers — contradicting their stated necessity | Undermines contribution claims: “factor-activity regularization maintains variation”, “online variance regularization discourages collapse” are asserted but not verified | Ablate $L_{\text{fac}}$ and $L_{\text{enc}}$ separately in Table 3/4 settings; measure σ<sup>fac</sup><sub>k,j</sub> and σ<sup>enc</sup><sub>j</sub> distributions pre/post ablation | [Paper: PDF p. 4–5] introduces both losses but Tables 2–6 show only full OJEPA vs. baseline — no ablations reported |

## 14 学到的知识  
- **JEPA generalization**: The context–target interface (Eq. 1) is sufficiently abstract to unify vision patch prediction, single-cell state completion, clinical forecasting, control planning, and molecular rollout — demonstrating JEPA’s role as a *unifying predictive paradigm*, not just a vision technique [Paper: PDF p. 1, 3, Table 1].  
- **Orthogonality as capacity allocator**: Unlike Barlow Twins/VICReg which regularize embedding statistics, Orthogonal JEPA applies orthogonality *directly on predictive target coordinates*, making it a structural prior for *what* should be predicted, not just *how* embeddings are distributed [Paper: PDF p. 4].  
- **Synthesis is nontrivial**: Moore–Penrose pseudoinverse (Eq. 5) is essential for state reconstruction — simple concatenation $\hat{u}_t$ would lack geometric coherence; orthogonality ensures $(B^\top)^\dagger = B$ when ideal, enabling clean reconstruction (Eq. 8) [Paper: PDF p. 4].  
- **Variance regularization is practical**: $L_{\text{fac}}$ and $L_{\text{enc}}$ (Eq. 9) use hinge loss on empirical std dev — a simple, differentiable way to enforce activity without assuming Gaussianity or requiring batch normalization [Paper: PDF p. 4–5].  
- **Cross-domain consistency**: Gains are observed across five disparate domains (vision, scRNA-seq, clinical, control, molecules), suggesting orthogonal factorization addresses a *universal bottleneck* in latent-state learning — capacity misallocation — rather than domain-specific quirks [Paper: PDF p. 1, 5–8].

## 15 与既有知识的连接  
- **single-cell foundation models**: Directly extends Cell-JEPA [15] — replaces its monolithic target with orthogonal factorization, improving PBMC clustering (Table 3) and perturbation prediction. Connects to scGPT [16] backbone usage, but Orthogonal JEPA adds no new architecture — only target-space decomposition. **Strong connection**.  
- **spatial transcriptomics**: Not evaluated — Table 1 lists “Single cell” but specifies *masked expression profile → complete cell state*, not spatial coordinates or tissue graphs. No spatial adjacency or graph structure incorporated. **Weak connection / methodological connection only** (same JEPA interface could adapt to spatial patches).  
- **graph neural networks**: No graph structure used — context/target sampling is index-based (e.g., gene IDs, patch IDs), not edge-aware. Basis matrices $B_k$ operate on flat vectors, not graph spectra. **Weak connection / methodological connection only** (could integrate GNN encoders as $f_\theta$).  
- **multi-omics**: Only single-modality (gene expression) used in scRNA-seq experiments. No integration of ATAC, protein, or spatial data. **Weak connection**.  
- **biomedical AI**: Clinical forecasting (Table 4) and single-cell (Table 3) are core biomedical applications; orthogonal factorization improves both, suggesting general utility for high-dimensional, sparse biomedical data. **Strong connection**.  
- **perturbation prediction**: Explicitly evaluated on Adamson [17] and Norman [18] CRISPR screens (Table 3), achieving SOTA Pearson correlations — directly addresses this user interest. **Strong connection**.  
- **cell state representation**: Core contribution — Orthogonal JEPA learns factorized cell states that outperform Cell-JEPA in zero-shot clustering and perturbation response. **Strong connection**.  
- **cross-modal alignment**: Not tested — all experiments are single-modality (vision patches, gene counts, clinical events, etc.). No alignment objective (e.g., contrastive loss across modalities) included. **No direct connection**.

## 16 研究想法  

- **name**: OrthoCell — Orthogonal factorization for interpretable single-cell perturbation modules  
  **originating limitation/observation**: Authors note “factor interpretation requires additional probes” [Paper: PDF p. 4, 8] and all scRNA-seq experiments use cell-level targets, not gene-module targets.  
  **core hypothesis**: Orthogonal JEPA factors trained on perturbation-aware targets (e.g., post-perturbation gene modules) will align with biological pathways better than monolithic Cell-JEPA.  
  **delta from paper**: Replace cell-level $z_t$ with *module-level targets*: for each CRISPR perturbation, define $z_t$ as PCA projection of differentially expressed genes per GO pathway; apply Orthogonal JEPA to predict module activations.  
  **initial method**: Train on Adamson/Norman data; use scGPT encoder; define $K$ = # of canonical pathways (e.g., 50); supervise $z^{(k)}_t$ with pathway activity scores.  
  **validation**: Align $B_k$ columns to GO terms via cosine similarity; test if knocking out $q_k$ degrades prediction of corresponding pathway genes.  
  **failure modes**: Pathway definitions too coarse/fine; module activity not linearly separable in $z_t$; insufficient perturbation diversity.  
  **innovation status**: unverified  

- **name**: GraphOrthoJEPA — Integrating GNNs with orthogonal factorization for spatial transcriptomics  
  **originating limitation/observation**: Spatial transcriptomics is listed as weak connection; Table 1 has no spatial instantiation; standard JEPA uses index-based sampling, not graph neighborhoods.  
  **core hypothesis**: Combining graph-structured context encoding (e.g., GAT) with orthogonal factorization improves prediction of masked spatial patches in tissue sections.  
  **delta from paper**: Replace $f_\theta(H_C, S_C)$ with GNN that takes gene expression + spatial coordinates as node features and tissue graph adjacency as edges; retain $B_k$ factorization on patch-level $z_t$.  
  **initial method**: Use Stereo-seq or Visium data; construct k-NN spatial graph; train GraphOrthoJEPA to predict masked spots; compare to standard JEPA with CNN encoder.  
  **validation**: Measure spot-level reconstruction error; test if orthogonal factors capture spatial gradients (e.g., cortical layer, tumor margin).  
  **failure modes**: Graph sparsity in low-resolution data; GNN over-smoothing obscuring local factors; no ground-truth spatial modules for alignment.  
  **innovation status**: unverified  

- **name**: StochasticOrthoJEPA — Adding multimodal uncertainty to orthogonal factors  
  **originating limitation/observation**: Authors state “the present predictor is deterministic and does not explicitly represent multimodal futures” [Paper: PDF p. 8].  
  **core hypothesis**: Modeling each factor $z^{(k)}_t$ as a Gaussian distribution $q_k(z_c, s_t) = \mathcal{N}(\mu_k, \sigma_k^2)$, with orthogonality enforced on means *and* covariances, improves rollout stability in molecular/clinical settings.  
  **delta from paper**: Replace deterministic $q_k$ with probabilistic head; extend $L_{\text{orth}}$ to penalize covariance overlap $\text{Tr}(\Sigma_i \Sigma_j)$; modify synthesis to sample $\hat{z}_t$ from mixture.  
  **initial method**: Implement on Water molecular task (Table 6); use diagonal $\Sigma_k$ for tractability; evaluate entropy of 100-step rollout distributions.  
  **validation**: Compare RMSD variance across seeds; test if high-entropy factors correspond to physically unstable regions (e.g., solvent shell).  
  **failure modes**: Increased training instability; covariance orthogonality harder to optimize than mean orthogonality; no clear metric for “useful” uncertainty.  
  **innovation status**: unverified