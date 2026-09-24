> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation | [Paper] [Paper: PDF p. 1] |
| Authors | Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint | [Paper] [Paper: PDF p. 1] |
| Year | 2026 | [Paper] [Paper: PDF p. 1] |
| Core task | Histology-to-ST prediction (spatial transcriptomics generation from H&E images) | [Paper] [Paper: PDF p. 1, 2] |
| Method name | CorrFlow | [Paper] [Paper: PDF p. 1] |
| Key technique | Conditional flow matching + annealed masking + gene graph regularization | [Paper] [Paper: PDF p. 1, 4] |
| Primary evaluation metric | PCC (Pearson correlation coefficient) and HPCC (Hallmark-Gene PCC) on HMHVG-50 genes | [Paper] [Paper: PDF p. 7, Table 1] |
| Benchmark datasets | HEST-1K (10 cancer/tissue types), STImage-1K4M (Brain, Breast) | [Paper] [Paper: PDF p. 7, Table 9] |
| Baseline model | STFlow [11] (flow-matching baseline) | [Paper] [Paper: PDF p. 7] |
| Code/data availability | Not stated in text; “not verified” | Not mentioned in supplied material |

## 02 一句话总结

CorrFlow 提出一种面向空间转录组（ST）生成的条件流匹配框架，通过**渐进式掩码策略**（annealed masking）和**基因图正则化**（gene graph regularization）显式建模基因间依赖关系，解决现有生成模型将基因视为独立预测目标、无法保留生物学共表达模式的根本缺陷；该方法在10个HEST-1K数据集上显著提升PCC与HPCC，尤其增强通路级预测一致性，但其STRING+WGCNA融合策略的泛化性未在外部队列验证，且未开源实现。

## 03 研究问题

论文直面一个被既有工作系统性忽略的核心矛盾：**生成式ST预测模型虽能建模表达分布的随机性，却在训练目标层面默认基因独立**。作者指出，这种“per-gene decomposition”并非建模能力不足所致，而是标准流匹配（Eq. 2–3）与扩散目标（Remark 1）在数学上天然分解为G个独立损失项，导致优化过程对跨基因协同建模既无激励也无约束 [Paper] [Paper: PDF p. 4]。因此，研究问题不是“能否建模基因相关性”，而是“如何重构训练信号与正则化机制，使模型**必须**学习并利用基因互作结构才能最小化损失”。

## 04 研究背景与发展路径

该工作处于“histology-to-ST generative modeling”演进的关键转折点：早期为确定性回归（ST-Net [8]），后转向捕捉不确定性的生成范式（Stem [40]、STFlow [11]），但均延续“per-gene marginal estimation”范式；本文则首次将**基因互作建模**从特征编码/后处理环节（如WGCNA用于预处理 [24] 或图神经网络用于回归 [38]）前移至**生成动力学核心**——即在流匹配的插值轨迹（xt）构建与速度场（vθ）优化中，强制引入基因维度间的耦合。这一路径跳出了“用图结构增强输入特征”的旧范式，转向“用图结构约束输出空间+用掩码重构学习任务”，构成方法论跃迁 [Paper] [Paper: PDF p. 2–3]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| Per-gene decomposition of training objective | Uneven gene-level performance; highly correlated genes (e.g., x₃₁) predicted poorly despite accurate predictions for others (x₁₁, x₂₁); failure to preserve co-expression patterns | Standard CFM loss decomposes across genes (Proposition 1, Eq. 3), making cross-gene coordination unidentifiable — any gain from modeling correlation is equally achievable without it | [Paper] [Paper: PDF p. 2, 4]; Fig. 1 caption; Proposition 1 proof [Paper] [Paper: PDF p. 4] |
| Shortcut reconstruction near t=1 | Network copies near-target values from xt instead of learning meaningful transport dynamics | As t→1, xt→x₁, providing trivial reconstruction signal | [Paper] [Paper: PDF p. 5]; Eq. 8 motivation |
| Lack of biological constraint on output space | Predictions may violate known co-expression structures due to finite capacity/noisy gradients | Existing methods apply priors only to features or encoders, not to generative dynamics | [Paper] [Paper: PDF p. 6]; Section 3.3 intro |
| Train-inference magnitude mismatch from fixed masking | Input norm drops during training (masked entries = 0) but remains full during inference, causing instability | Fixed zero masking reduces average input norm by factor ~1−p(t), creating distribution shift analogous to dropout scaling problem | [Paper] [Paper: PDF p. 5]; Section 3.2.1 |

## 06 核心思想

论文的核心思想是**将基因互作从“可选先验”升级为“不可绕过的生成约束”**。其逻辑链为：（1）观察到标准流匹配目标（Proposition 1）在数学上禁止跨基因梯度共享 → （2）提出annealed masking打破输入-输出维度一一对应，使masked基因的最优预测必须依赖joint conditional p(x⁽ᴹ⁾₁ \| x⁽ᴼ⁾₁, c)，从而**将联合建模从可选变为必需**（Proposition 2）→ （3）叠加gene graph正则化，将STRING功能关联与WGCNA数据驱动共表达融合为图拉普拉斯（Eq. 10）与Huber边约束（Eq. 11），使输出空间本身被生物结构所塑造。二者协同，前者改写学习任务，后者锚定解空间，共同迫使模型习得生物学一致的生成动力学。

## 07 方法总览

CorrFlow 是一个两阶段协同框架：**第一阶段（Annealed-MFM）重构学习任务**——通过timestep-dependent masking（Eq. 8）将标准流匹配转化为“部分观测下的联合推断”，使模型必须利用剩余基因推断被掩码基因，从而内生驱动跨基因建模；**第二阶段（Gene Graph Regularization）约束解空间**——构建融合STRING（S⁽ˢ⁾）与WGCNA（S⁽ʷ⁾）的基因亲和图（Eq. 9），并施加双重正则：Huber边损失（Llocal, Eq. 11）保障邻近基因预测一致性，图拉普拉斯损失（Lglobal, Eq. 12）抑制全图高频振荡，引导输出对齐低频共表达模块。最终目标为L = LMFM + ρLlocal + λLglobal（Eq. 16），所有组件均服务于一个目标：让生成的ST在数值准确（PCC）与生物合理（HPCC, GGC-Pearson）上同步提升。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-----------------------------------|
| Annealed Masking Schedule | Replaces subset of gene dimensions in xt with learnable mask tokens mg, where masking ratio p(t) = pmax·t increases linearly with timestep | To break per-gene decomposition (Proposition 1) and suppress shortcut reconstruction near t=1; forces joint conditional modeling for masked genes | Input: xt ∈ ℝᴳ, t ∈ [0,1]; Output: ˜xt ∈ ℝᴳ with masked entries replaced by mg [Paper] [Paper: PDF p. 5, Eq. 5] | Proposition 2 proof [Paper] [Paper: PDF p. 5]; Ablation shows PCC ↓0.004 (Table 2); Hyperparameter study confirms f(t)=t optimal (Table 3) | Removal → reverts to per-gene marginal estimation; ablation shows PCC drops to 0.609 [Paper] [Paper: PDF p. 8, Table 2] |
| Learnable Mask Token mg | Adapts token value during backprop to preserve input statistics across masking ratios | To avoid train-inference magnitude mismatch caused by fixed-zero masking (dropout scaling problem) | Input: mask set M; Output: mg ∈ ℝᴳ, shared across spatial locations [Paper] [Paper: PDF p. 5] | Explicitly motivated as mitigation for norm shift [Paper] [Paper: PDF p. 5]; no ablation on token vs. fixed zero, but design choice enables stable optimization | Expected: Fixed-zero masking would cause training instability and degraded convergence; not directly ablated but implied critical for stability |
| Gene Affinity Graph Fusion | Fuses STRING functional prior S⁽ˢ⁾ and WGCNA data-driven co-expression S⁽ʷ⁾ via weighted average S = αS⁽ˢ⁾ + (1−α)S⁽ʷ⁾ | To combine stable cross-dataset prior knowledge with dataset-specific co-expression structure, avoiding over-reliance on either alone | Input: S⁽ˢ⁾ (STRING), S⁽ʷ⁾ (WGCNA); Output: fused affinity matrix S ∈ ℝᴳˣᴳ [Paper] [Paper: PDF p. 6, Eq. 9] | Ablation shows both w/o WGCNA (PCC=0.607) and w/o STRING (PCC=0.604) underperform full model (0.613) [Paper] [Paper: PDF p. 8, Table 2] | Removal of either source → loss of complementary information; PCC drops more for STRING removal (−0.009) than WGCNA (−0.006), suggesting STRING provides stronger anchor |
| Huber-based Local Constraint (Llocal) | Penalizes discrepancy ∆n,ij = zi − zj between z-scored predictions of connected genes (i,j)∈E, weighted by Sij | To enforce pairwise consistency among functionally related genes, robust to outliers on weak edges | Input: predicted expression ˆx₁,n, graph S; Output: scalar loss Llocal [Paper] [Paper: PDF p. 6, Eq. 11] | Ablation shows w/o Llocal → PCC=0.605 [Paper] [Paper: PDF p. 8, Table 2]; hyperparameter study shows ρ=0.3 optimal [Paper] [Paper: PDF p. 15, Table 6] | Removal → loss of fine-grained local coherence; ablation confirms larger drop than w/o Lglobal (0.605 vs 0.609) |
| Graph Laplacian Global Constraint (Lglobal) | Penalizes ˆx⊤₁,nLˆx₁,n, where L is normalized Laplacian of fused graph | To suppress global oscillations and align predictions with low-frequency eigenmodes (large-scale co-expression modules) | Input: ˆx₁,n, graph Laplacian L; Output: scalar loss Lglobal [Paper] [Paper: PDF p. 6–7, Eq. 12] | Ablation shows w/o Lglobal → PCC=0.609 [Paper] [Paper: PDF p. 8, Table 2]; hyperparameter study shows λ=10⁻³ optimal [Paper] [Paper: PDF p. 15, Table 6] | Removal → loss of global module-level smoothness; smaller PCC drop than Llocal, indicating complementary role |

## 09 关键公式与符号

- **No verifiable closed-form equation for the core method**: The paper defines components (Eq. 5, 8, 9, 10, 11, 12, 16) but does not present a single unified equation for CorrFlow’s forward pass or loss; the overall objective is modularly composed.
- **Key symbols & metrics**:
  - `xt = (1−t)x₀ + tx₁` (Eq. 1): Linear interpolant in flow matching; `x₀` ~ ZINB prior, `x₁` = ground-truth ST.
  - `p(t) = pmax · t` (Eq. 8): Annealed masking ratio; `pmax ∈ (0,1)` controls max masking intensity.
  - `S = α S(s) + (1−α) S(w)` (Eq. 9): Fused gene affinity matrix; `S(s)` = STRING, `S(w)` = WGCNA, `α ∈ [0,1]`.
  - `L = I − A`, `A = D⁻¹ᐟ²SD⁻¹ᐟ²` (Eq. 10): Normalized graph Laplacian and adjacency.
  - `rg = cov(ŷ:,g, y:,g) / (σ(ŷ:,g) σ(y:,g))` (Eq. 17): Gene-wise Pearson correlation coefficient (PCC).
  - `Pearson = (1/|G|) Σg rg` (Eq. 18): Mean PCC over gene set G.
  - `HPCC = (1/|K|) Σk (1/|Pk∩G|) Σg∈Pk∩G rg` (Eq. 13): Hallmark-Gene PCC, averaged over MSigDB Hallmark pathways with ≥5 genes in G.
  - `GGC-Pearson = corr(vec△(Ĉ), vec△(C))` (Eq. 20): Correlation between upper-triangular vectors of predicted vs. ground-truth gene-gene correlation matrices.

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|-------------------------------|--------|
| Main benchmark (HEST-1K, 10 datasets) | CorrFlow > STFlow in average PCC/HPCC | Same HMHVG-50 genes, patient-stratified CV, identical backbone architecture | PCC: 0.613 vs 0.600 (+0.013); HPCC: 0.628 vs 0.613 (+0.015); all p<0.05 [Table 12] | CorrFlow’s dependency-aware design yields statistically significant gains over strongest flow-matching baseline | That gains generalize to *all* cancer types equally (e.g., PAAD missing in Table 4 expansion) | [Paper] [Paper: PDF p. 8, Table 1; p. 19, Table 12] |
| Ablation study (HMHVG-50) | Each component contributes positively | Full model vs. variants removing masking, Lgraph, Llocal, Lglobal, WGCNA, or STRING | Full model best (0.613); removals cause PCC drops: masking (−0.004), Lgraph (−0.008), STRING (−0.009) | All proposed components are complementary and necessary for peak performance | That masking is *more important* than graph (drop magnitudes similar; no statistical test on delta) | [Paper] [Paper: PDF p. 8, Table 2; p. 15, Table 5] |
| Hyperparameter study (masking/graph) | Optimal settings exist and are identifiable | Varying f(t), pmax, α, ρ, λ on HMHVG-50 | Best: f(t)=t, pmax=0.75, α=0.6, ρ=0.3, λ=10⁻³ [Tables 3, 6] | Design choices are empirically grounded, not arbitrary | That these settings are globally optimal across *all* gene panels or datasets (e.g., PAAD excluded from Table 4) | [Paper] [Paper: PDF p. 8–9, Tables 3, 6] |
| Expanded gene sets (HMHVG-100/150/200) | Dependency-aware design scales with gene panel size | Same HEST-1K, broader gene sets | Consistent PCC/HPCC gains over STFlow across all sizes (e.g., PCC +0.007 at 100 genes) [Table 4] | Benefit of modeling dependencies persists beyond top-50 marker genes | That gains increase with panel size (margins are stable, not growing) | [Paper] [Paper: PDF p. 14, Table 4; p. 17, C.1] |
| GGC-Pearson evaluation | CorrFlow better preserves gene-gene correlation structure | Compared to STFlow, BLEEP-UNI on HMHVG-50 | Avg. GGC-Pearson: 0.648 vs 0.633 (STFlow) [Table 7] | Improved dependency modeling translates to better preservation of global co-expression topology | That this directly causes improved downstream biological utility (no downstream task validation) | [Paper] [Paper: PDF p. 17, Table 7; p. 15, B] |
| Supplementary STImage-1K4M | Generalizability to larger, non-benchmark ST collections | Brain & Breast cancer categories, random 8:1:1 split | PCC: 0.542 vs 0.530 (STFlow) [Table 9] | Gains hold on larger, less standardized datasets | That generalizability extends to *fully independent external cohorts* (no such validation performed) | [Paper] [Paper: PDF p. 18, Table 9; p. 19, C.3] |

## 11 对结论的正确理解

论文结论应被理解为：**在HEST-1K标准化患者分层交叉验证框架下，CorrFlow通过annealed masking与gene graph regularization的协同，实现了对STFlow基线的统计显著且稳健的PCC/HPCC提升，且该提升与基因互作建模的理论动机一致**。关键限定包括：（1）提升幅度虽小（+0.013 PCC）但稳定，在10个数据集、多基因面板、多指标（PCC/HPCC/GGC-Pearson/MSE）上均成立；（2）HPCC增益（+0.015）大于PCC，证实其对通路级生物学一致性的特异性增强；（3）所有结论均基于同一骨干网络（STFlow），差异仅在于损失与正则，排除了架构优势干扰；（4）“biologically coherent”指定量指标（HPCC, GGC-Pearson）提升及可视化中空间模式更贴近ground truth（Fig. 3a），而非定性生物学发现。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|-------------------------------------|--------|
| Lack of external cohort validation | Evaluation uses HEST-1K (cross-platform but internal) and STImage-1K4M (non-standard splits); no fully independent external cohort with different tissue prep/sequencing/scanner | Incorporate independently collected ST cohorts to assess clinical robustness under out-of-distribution variations | [Paper] [Paper: PDF p. 19, D] |
| Insufficient clinical translation readiness | Prediction quality still insufficient for direct clinical use due to intrinsic challenge of inferring molecular states from morphology alone | Improve robustness via stronger dependency-aware modeling and higher-quality ST training data | [Paper] [Paper: PDF p. 19, D] |
| Limited downstream utility assessment | Evaluation focuses on reconstruction fidelity (PCC) and structure preservation (GGC), not downstream biological/clinical tasks | Assess benefits for tissue-domain identification, pathway activity estimation, biomarker discovery, patient stratification, and prognosis modeling | [Paper] [Paper: PDF p. 20, D] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| STRING+WGCNA fusion assumes static functional associations, but gene interactions are context-dependent (e.g., tumor vs. normal, cell-type specific) | The fused graph S may misrepresent true co-expression in specific disease contexts, leading to over-regularization on irrelevant edges | Could degrade performance on datasets where STRING prior is weak (e.g., novel cancer subtypes) or WGCNA fails (low N spots) | Compare CorrFlow using cell-type-specific co-expression networks (e.g., from scRNA-seq) vs. bulk WGCNA on same ST dataset; measure PCC delta per cell type | [Paper] [Paper: PDF p. 6, Eq. 9]; STRING/WGCNA are bulk-level resources, not context-aware |
| Annealed masking with p(t)=pmax·t treats all genes identically, ignoring their biological roles (e.g., housekeeping vs. regulatory) | Masking key regulators uniformly may hinder learning of master regulatory logic, while masking noisy genes adds little signal | May limit ability to capture hierarchical gene regulation, not just pairwise correlation | Stratify masking probability by gene centrality (e.g., degree in STRING) or variance; test if adaptive masking improves HPCC on regulatory pathways | [Paper] [Paper: PDF p. 5, Eq. 8]; no gene-specific masking strategy explored |
| Graph Laplacian Lglobal (Eq. 12) penalizes high-frequency oscillations but assumes smoothness = biological coherence | Some biologically valid expression patterns (e.g., sharp boundaries in tumor-stroma interface) require high-frequency variation, which Lglobal may suppress | Could blur spatially resolved biological signals, harming domain identification | Visualize spatial residuals (ŷ−y) in high-Lglobal regions (e.g., tumor margins) vs. low-Lglobal; correlate with histology-defined domains | [Paper] [Paper: PDF p. 7, Eq. 12]; Laplacian smoothness is a generic assumption, not biology-validated for ST |
| HPCC metric (Eq. 13) aggregates only over Hallmark pathways with ≥5 genes in G, excluding many disease-specific signatures | For cancer datasets like PAAD or SKCM, Hallmark coverage may be low, making HPCC an incomplete proxy for disease-relevant coherence | May underestimate true biological utility in oncology contexts where custom pathways matter more | Compute PCC on cancer-specific pathway databases (e.g., Oncogenic Signatures) and compare delta CorrFlow-STFlow | [Paper] [Paper: PDF p. 7, Eq. 13]; MSigDB Hallmark is general, not cancer-focused |

## 14 学到的知识

- **Flow matching的可塑性远超标准应用**：其插值轨迹（xt）不仅是数学工具，更是可编辑的“学习界面”——通过掩码（Eq. 5）、重加权或注入结构，能将任意先验（如基因图）无缝嵌入动力学训练，比扩散模型的score matching更易耦合结构约束。
- **渐进式掩码（annealed masking）是诱导联合建模的轻量级杠杆**：不需修改网络架构，仅通过输入扰动（p(t)）即可将优化目标从边际估计（Proposition 1）转向条件联合（Proposition 2），且理论保证收敛（Theorem 1）。
- **多源图融合需谨慎平衡**：STRING提供跨数据集稳定性，WGCNA offers dataset specificity；α=0.6（Table 3）表明功能先验略占优，但二者缺一不可（Table 2 ablation），提示在single-cell foundation models中融合scRNA-seq co-expression与 PPI networks时，需动态调整权重。
- **评估必须分层**：PCC衡量单基因空间保真，HPCC衡量通路级协调，GGC-Pearson衡量全局拓扑保真——三者提升方向一致（Table 1/7），证实CorrFlow的改进是系统性的，非指标偏倚。
- **计算效率与科学严谨可兼得**：CorrFlow与STFlow参数量完全相同（Table 14），证明结构化正则（Lgraph）和掩码（LMFM）不增加模型复杂度，仅改变训练动态，这对资源受限的biomedical AI部署至关重要。

## 15 与既有知识的连接

- **候选连接/方法论连接**：  
  - *single-cell foundation models*: CorrFlow’s gene graph regularization (Eq. 9–12) directly inspires integrating scRNA-seq-derived co-expression graphs (e.g., from CellxGene) as dynamic priors, replacing static STRING/WGCNA.  
  - *spatial transcriptomics*: The annealed masking strategy (Eq. 8) is transferable to spot-to-spot imputation tasks where spatial neighbors serve as conditioning context, analogous to masking spatial coordinates.  
  - *graph neural networks*: CorrFlow’s dual graph constraints (Llocal + Lglobal) provide a blueprint for GNNs in ST: local message passing (Huber on edges) + global spectral filtering (Laplacian), moving beyond standard GCN layers.  
  - *multi-omics*: The fusion weight α (Eq. 9) formalizes how to balance prior knowledge (e.g., chromatin accessibility) and data-driven omics correlations (e.g., ATAC-RNA co-variation).  
  - *perturbation prediction*: Proposition 2’s joint conditional modeling (Eq. 7) is foundational for predicting multi-gene perturbation effects—masking a gene set M and inferring it from O mirrors knockdown/knockout experiments.  
  - *cross-modal alignment*: CorrFlow’s conditioning on histology features z and spatial q (Fig. 2) exemplifies tight modality binding; its success suggests that alignment should occur in the *generation space*, not just feature space.

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Cell-Type-Aware Gene Graph (CTAG)  
  **originating limitation/observation**: [Analysis] STRING+WGCNA fusion ignores context-dependency; current graph is bulk-level, not cell-type-specific [Paper] [Paper: PDF p. 6, Eq. 9].  
  **core hypothesis**: Using scRNA-seq-derived cell-type-specific co-expression graphs as dynamic priors will improve CorrFlow’s accuracy in heterogeneous tissues (e.g., tumor microenvironment).  
  **delta from paper**: Replace static S⁽ʷ⁾ with cell-type-weighted ensemble: S⁽ʷ⁾_ct = Σc w_c · S⁽ʷ⁾_c, where w_c is cell-type proportion from histology segmentation, and S⁽ʷ⁾_c is co-expression graph for cell type c.  
  **initial method**: Integrate UNI [5] histology encoder with cell-type classifier (e.g., based on nuclei morphology); compute w_c per spot; fetch precomputed S⁽ʷ⁾_c from scRNA-seq atlas (e.g., Human Cell Atlas).  
  **validation**: Test on LYMPH_IDC (Fig. 3a) where tumor/stroma boundaries are clear; measure PCC delta in stromal vs. tumor regions.  
  **failure modes**: Poor cell-type segmentation → erroneous w_c; sparse scRNA-seq for rare cell types → noisy S⁽ʷ⁾_c.  
  **innovation status**: unverified  

- **name**: Hierarchical Annealed Masking (HAM)  
  **originating limitation/observation**: [Analysis] Uniform masking ignores gene functional hierarchy; masking master regulators may disrupt learning [Paper] [Paper: PDF p. 5, Eq. 8].  
  **core hypothesis**: Prioritizing masking of downstream effector genes (high variance, low centrality) while sparing upstream regulators (low variance, high STRING degree) will yield more biologically interpretable joint modeling.  
  **delta from paper**: Replace Bernoulli masking with stratified sampling: mask probability p_g(t) = p(t) · (1 − centrality_g), where centrality_g is degree in STRING or variance-normalized expression variance.  
  **initial method**: Precompute gene centrality from STRING; during training, sample M with p_g(t) instead of uniform p(t).  
  **validation**: Compare HPCC on regulatory pathways (e.g., KEGG MAPK) vs. metabolic pathways; expect larger HPCC gain in regulatory sets.  
  **failure modes**: Over-suppression of regulator masking may revert to marginal estimation; centrality metrics may not reflect true regulatory hierarchy in cancer.  
  **innovation status**: unverified  

- **name**: Spatial Boundary-Aware Laplacian (SBAL)  
  **originating limitation/observation**: [Analysis] Standard Lglobal (Eq. 12) may suppress biologically valid sharp expression boundaries [Paper] [Paper: PDF p. 7, Eq. 12].  
  **core hypothesis**: Modifying the graph Laplacian to preserve high-gradient spatial interfaces (e.g., tumor-stroma) will improve domain identification utility without sacrificing global coherence.  
  **delta from paper**: Replace constant weight wij in Lglobal with spatially adaptive weight: wij ← wij · exp(−β · ‖∇I_i − ∇I_j‖²), where ∇I is histology gradient magnitude at spots i,j.  
  **initial method**: Compute Sobel gradients on histology patches; embed gradient difference into edge weights before computing L.  
  **validation**: Quantify boundary sharpness (e.g., gradient magnitude of ŷ) at histology-defined tumor margins; correlate with domain segmentation accuracy (e.g., Dice score).  
  **failure modes**: Gradient noise in low-contrast regions → unstable weights; requires precise histology-ST spatial alignment.  
  **innovation status**: unverified