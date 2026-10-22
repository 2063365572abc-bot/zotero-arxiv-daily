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
| Venue | arXiv preprint (cs.LG) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-01 | [Paper] [Paper: PDF p. 1] |
| Core task | Histology-to-ST prediction (spatial transcriptomics generation from H&E images) | [Paper] [Paper: PDF p. 1–2] |
| Method name | CorrFlow | [Paper] [Paper: PDF p. 1–2] |
| Key technique 1 | Annealed masked flow matching (Annealed-MFM) | [Paper] [Paper: PDF p. 2–5] |
| Key technique 2 | Gene graph-regularized optimization (STRING + WGCNA fusion) | [Paper] [Paper: PDF p. 2–6] |
| Primary evaluation metric | PCC (Pearson correlation coefficient) and HPCC (Hallmark-Gene PCC) on HMHVG-50 genes | [Paper] [Paper: PDF p. 7–8] |
| Benchmark datasets | HEST-1K (10 cancer/tissue types), STImage-1K4M (Brain, Breast) | [Paper] [Paper: PDF p. 7, 18] |
| Baseline model | STFlow (conditional flow matching) | [Paper] [Paper: PDF p. 7] |
| Code/data availability | Not stated in text; no URL, GitHub, or repository link provided | Not assessable from supplied material |

## 02 一句话总结  
本文提出 CorrFlow，一种面向空间转录组（ST）生成的条件流匹配框架，通过**渐进式基因掩码（annealed masking）** 和 **基因图正则化（gene graph regularization）** 两大机制，显式建模基因间依赖关系，解决现有生成模型将基因视为独立预测目标、忽略生物学共表达结构的根本缺陷。该方法在10个 HEST-1K 数据集上系统性超越 STFlow 等基线，在 PCC 和 HPCC 上取得最优平均性能，尤其提升通路级表达协调性；其设计直击单细胞与空间多组学中“基因非独立性”这一核心建模盲区，为跨模态对齐与 perturbation prediction 提供可解释的依赖建模范式。

## 03 研究问题  
论文聚焦于：**如何在 histology-to-ST 生成任务中，使生成模型不再将 G 维基因表达向量 x₁ ∈ ℝᴳ 视为 G 个独立标量输出，而是建模其内在的、受调控网络与通路活动驱动的联合分布 p(x₁ | z, q)**？  
作者指出，该问题并非技术实现细节，而是由标准流匹配（CFM）和扩散（diffusion）的目标函数结构性分解所导致——其损失函数天然按基因维度可分（L = Σ₉ L⁽ᵍ⁾），因此不奖励、也不要求模型学习跨基因推理能力 [Paper] [Paper: PDF p. 4–5]。这导致模型虽有共享骨干网络，却缺乏优化动力去捕捉如 KRT7 与其它上皮标志物间的协同表达模式 [Paper] [Paper: PDF p. 9]。研究问题本质是：**如何重构训练信号与约束，使模型的最优解必须依赖于基因间条件依赖**？

## 04 研究背景与发展路径  
早期工作（ST-Net）采用确定性回归，无法建模表达不确定性；检索法（BLEEP）依赖参考集覆盖度；近期生成范式（Stem、STFlow）虽引入随机性，但仍未突破“per-gene marginal estimation”范式 [Paper] [Paper: PDF p. 2–3]。关键转折点在于作者识别出：**现有生成目标的数学结构（Proposition 1）决定了其无法内生地鼓励跨基因建模** [Paper] [Paper: PDF p. 4]。因此发展路径不是堆叠更强 backbone，而是从**目标函数层面重构学习信号**：先用掩码打破输入-输出维度一一对应（Section 3.2），再用图正则化施加生物学先验约束（Section 3.3）。该路径区别于单纯引入 GNN 编码器（如 Zeng et al. 2022 [38]）或图注意力（Shi et al. 2025 [25]），而是将图结构嵌入生成动力学（flow dynamics）与输出空间（expression space）双重层面。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|------------------------------|--------------------------|
| Per-gene decomposition of training objective | Models achieve high PCC on some genes but fail on highly correlated ones (e.g., x₃¹ in Fig. 1); uneven gene-level performance | Standard CFM/diffusion loss decomposes as sum over genes (Eq. 3), so optimal predictor for gene g depends only on marginal p(xᵍ₁ \| xₜ, t, c), not joint p(x₁ \| c) [Paper] [Paper: PDF p. 4–5] | [Paper] [Paper: PDF p. 4] Proposition 1 & proof; [Paper] [Paper: PDF p. 2] Fig. 1 caption; [Paper] [Paper: PDF p. 5] “cross-gene coordination is therefore unidentifiable under the standard objective” |
| Lack of biological coherence in generated expression | Predictions may be numerically accurate per gene but violate known co-expression modules or pathway activity | No explicit mechanism to enforce that functionally related genes (e.g., STRING-linked) or co-expressed genes (e.g., WGCNA modules) have consistent predicted expression patterns | [Paper] [Paper: PDF p. 1] Abstract: “overlook the intrinsic gene-gene interactions… limits their ability to preserve biologically meaningful co-expression patterns”; [Paper] [Paper: PDF p. 6] “finite model capacity and noisy gradients can still lead to predictions that violate known co-expression structures” |
| Shortcut reconstruction near t=1 | Network copies near-target values from xₜ instead of learning transport dynamics | As t→1, xₜ→x₁, making endpoint prediction trivial without additional pressure | [Paper] [Paper: PDF p. 5] “Conditional flow matching suffers from a practical shortcut issue… allowing the network to shortcut by copying near-target values” |

## 06 核心思想  
论文的核心思想是：**要让模型学会“基因依赖”，不能只靠更大模型或更多数据，而必须让“依赖建模”成为其最优解的必要条件**。这通过两个互补且可证明有效的机制实现：（1）**Annealed-MFM** 将标准 CFM 的输入 xt 替换为掩码版 ˜xt，且掩码比例 p(t) 随 t 线性增长（Eq. 8）；这使得当模型最易走捷径（t 接近 1）时，输入信息最匮乏，被迫从剩余基因中推断被掩码基因，从而将最优解从 v*ᵍ = E[xᵍ₁ \| xₜ, t, c] 强制升级为 v*ᵍ = E[xᵍ₁ \| x⁽ᴼ⁾ₜ, t, c]（Proposition 2），即必须利用观测基因集合 O 的联合条件分布；（2）**Gene Graph Regularization** 不满足于仅靠数据驱动学习依赖，而是融合外部功能先验（STRING）与数据驱动共表达（WGCNA）构建基因亲和图 S（Eq. 9），再通过 Huber 局部平滑项（Eq. 11）和图拉普拉斯全局平滑项（Eq. 12）双重约束输出 ˆx₁，使预测表达在图结构上既局部一致又全局平滑，直接锚定生物学合理性。

## 07 方法总览  
CorrFlow 是一个端到端的 conditional flow matching 框架，以 histology features z 和 spatial coordinates q 为条件，学习从噪声先验 x₀（ZINB）到目标 ST 表达 x₁ 的连续传输场。其方法总览为：**给定线性插值 xt = (1−t)x₀ + t x₁（Eq. 1），模型接收掩码输入 ˜xt（Eq. 5），经 spatial-transformer denoiser 预测终点 x₁，并同时优化两项损失：（i）掩码流匹配损失 LMFM（Eq. 6），强制联合条件建模；（ii）基因图正则化损失 Lgraph = ρ Llocal + λ Lglobal（Eq. 12, 16），强制生物学一致性**。整个流程在 Algorithm 1 中完整呈现 [Paper] [Paper: PDF p. 14]，所有模块均服务于一个统一目标：使模型的最优参数 θ* 必须编码基因间依赖知识，否则无法最小化联合损失。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| Annealed Masking Schedule | Applies timestep-dependent Bernoulli mask to input xt, with p(t) = pmax·t (Eq. 8); replaces masked entries with learnable token m (Eq. 5) | To break per-gene decomposition (Proposition 1) and force joint conditional modeling (Proposition 2); annealing prevents shortcut at t≈1 | Input: xt, t; Output: ˜xt ∈ ℝᴳ | [Paper] [Paper: PDF p. 5] “suppress this by coupling the masking ratio to the timestep”; [Paper] [Paper: PDF p. 5] Proposition 2 proof; [Paper] [Paper: PDF p. 8] Table 2: w/o masking → PCC ↓0.004 | Ablation shows PCC drops to 0.609 (vs. 0.613), confirming its role in preventing shortcut and enabling dependency-aware inference [Paper] [Paper: PDF p. 8] |
| Gene Affinity Graph Construction | Fuses STRING prior S⁽ˢ⁾ and WGCNA-derived co-expression S⁽ʷ⁾ via weighted average S = αS⁽ˢ⁾ + (1−α)S⁽ʷ⁾ (Eq. 9), then computes normalized adjacency A and Laplacian L (Eq. 10) | To inject structured biological knowledge into the optimization, guiding predictions toward coherent co-expression patterns beyond what data alone may suggest | Input: STRING database, training expression data; Output: S, A, L ∈ ℝᴳˣᴳ | [Paper] [Paper: PDF p. 6] “We construct a gene affinity graph from two complementary sources”; [Paper] [Paper: PDF p. 8] Table 2: w/o Lgraph → PCC ↓0.008, larger drop than w/o masking | Removal causes largest PCC drop (0.605), indicating graph constraint is critical for stabilizing predictions under dependency structure [Paper] [Paper: PDF p. 8] |
| Local Graph Constraint (Llocal) | Penalizes discrepancy ∆n,ij = zi − zj between z-scored predictions of connected genes (i,j)∈E using Huber loss weighted by Sij (Eq. 11) | To enforce pairwise consistency among functionally related genes, robust to outliers on weak edges | Input: ˆx₁,n, µi, σi, S; Output: scalar Llocal | [Paper] [Paper: PDF p. 6] “Connected genes in G should produce similar predictions”; [Paper] [Paper: PDF p. 8] Table 2: w/o Llocal → PCC ↓0.008 | Ablation shows identical PCC drop as w/o Lgraph, suggesting Llocal carries most of the graph’s constraining power [Paper] [Paper: PDF p. 8] |
| Global Graph Constraint (Lglobal) | Penalizes ˆx₁,n⊤ L ˆx₁,n (Eq. 12), encouraging output to align with low-frequency eigenmodes of G | To capture graph-wide co-expression modules that local pairwise terms miss, suppressing rapid oscillations across the gene graph | Input: ˆx₁,n, L; Output: scalar Lglobal | [Paper] [Paper: PDF p. 6–7] “Llocal operates on individual edges and cannot capture graph-wide patterns”; [Paper] [Paper: PDF p. 8] Table 2: w/o Lglobal → PCC ↓0.004 (same as w/o masking) | Removal has same impact as w/o masking, indicating it provides complementary, non-redundant global smoothing [Paper] [Paper: PDF p. 8] |
| Learnable Mask Token | Replaces masked genes with trainable vector m ∈ ℝᴳ, initialized to zero | To avoid train-inference magnitude mismatch caused by fixed-zero masking (analogous to dropout scaling problem) | Input: None (parameter); Output: m used in Eq. 5 | [Paper] [Paper: PDF p. 5] “introduce a learnable mask token… to mitigate this issue”; [Paper] [Paper: PDF p. 5] “the network jointly learns what to substitute for missing genes” | Not ablated separately, but its design rationale addresses a concrete optimization instability, implying removal would harm convergence [Paper] [Paper: PDF p. 5] |

## 09 关键公式与符号  
论文未提供单一主导性“模型公式”，而是定义了一套相互支撑的**目标函数组件与图结构算子**。关键符号与公式如下（全部可核验）：  
- **Flow interpolation**: xt = (1 − t) x₀ + t x₁ (Eq. 1)  
- **Masked input**: ˜xt,g = { mg if g ∈ M; xt,g if g ∈ O } (Eq. 5), where M is mask set, O is observed set  
- **Annealed masking ratio**: p(t) = pmax · t (Eq. 8)  
- **Gene affinity fusion**: S = α S⁽ˢ⁾ + (1 − α) S⁽ʷ⁾ (Eq. 9), with S⁽ˢ⁾ from STRING, S⁽ʷ⁾ from WGCNA  
- **Normalized adjacency & Laplacian**: A = D⁻¹ᐟ² S D⁻¹ᐟ², L = I − A (Eq. 10)  
- **Local graph loss**: Llocal = (1/N) Σₙ Σ₍ᵢ,ⱼ₎∈E wij Huberβ(∆n,ij), wij ∝ Sij (Eq. 11)  
- **Global graph loss**: Lglobal = (1/N) Σₙ ˆx₁,n⊤ L ˆx₁,n (Eq. 12)  
- **Overall objective**: L = LMFM + Lgraph = LMFM + ρ Llocal + λ Lglobal (Eq. 16)  
- **PCC per gene**: rg = cov(ˆy:,g, y:,g) / (σ(ˆy:,g) σ(y:,g)) (Eq. 17)  
- **HPCC**: HPCC = (1/|K|) Σₖ (1/|Pk ∩ G|) Σg∈Pk∩G rg (Eq. 13), where K = {k : |Pk ∩ G| ≥ 5}  
- **GGC-Pearson**: corr(vec△(Ĉ), vec△(C)) (Eq. 20), measuring agreement of gene-gene correlation matrices  
- **MSE-Mean**: (1/G) Σg MSEg, MSEg = (1/N) Σᵢ (ˆyig − yig)² (Eq. 21–22)  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| Main benchmark (Table 1) | CorrFlow > STFlow on average PCC/HPCC across 10 HEST-1K datasets | CorrFlow vs. STFlow, TRIPLEX, BLEEP, etc., on HMHVG-50, patient-stratified CV | CorrFlow: PCC=0.613, HPCC=0.628; STFlow: PCC=0.600, HPCC=0.613 | CorrFlow achieves state-of-the-art on this benchmark; gain on HPCC > PCC suggests improved pathway-level coherence | That CorrFlow generalizes to *all* ST tasks or clinical settings; no external validation performed | [Paper] [Paper: PDF p. 8] Table 1 |
| Ablation study (Table 2) | Each proposed component contributes positively | Full CorrFlow vs. variants removing masking, Lgraph, Llocal, Lglobal, WGCNA, or STRING | Full model: 0.613; w/o masking: 0.609; w/o Lgraph: 0.605; w/o STRING: 0.604 | Annealed masking and graph regularization are both necessary and complementary; STRING and WGCNA provide distinct value | That any single component is *sufficient*; removal effects are additive, not synergistic | [Paper] [Paper: PDF p. 8] Table 2 |
| Hyperparameter study (Table 3) | Optimal hyperparameters align with design intuition | Varying f(t), pmax, α on HMHVG-50 | Best: f(t)=t, pmax=0.75, α=0.6 | Proportional annealing is superior; strong but not excessive masking works best; modest preference for STRING prior is justified | That these hyperparameters are globally optimal across all datasets or gene panels; PAAD omitted from some rows [Paper] [Paper: PDF p. 9] | [Paper] [Paper: PDF p. 9] Table 3 |
| Qualitative visualization (Fig. 3) | CorrFlow improves spatial pattern fidelity and gene-level PCC, especially for highly correlated genes | CorrFlow vs. STFlow on LYMPH_IDC sample NCBI68 (KRT7), gene-wise PCC scatter, top-AvgAbsCorr genes | Fig. 3(a): cleaner spatial gradients; Fig. 3(b): majority of points above diagonal; Fig. 3(c): higher PCC on top-correlated genes | Visual and gene-level evidence confirms quantitative gains reflect real biological improvement, not just metric artifact | That improvements hold for *all* marker genes or tissue contexts; only one sample visualized per dataset | [Paper] [Paper: PDF p. 9] Fig. 3 |
| Expanded gene sets (Table 4) | Dependency-aware design scales to broader gene panels | CorrFlow vs. STFlow on HMHVG-100/150/200 | CorrFlow consistently outperforms (e.g., PCC-100: 0.591 vs. 0.584) | Benefit is not limited to highly variable marker genes but extends to larger, biologically relevant scopes | That performance gap *widens* with scale; margins are stable but moderate | [Paper] [Paper: PDF p. 14] Table 4 |
| GGC-Pearson (Table 7) | CorrFlow better preserves gene-gene correlation structure | CorrFlow vs. STFlow on GGC-Pearson metric | CorrFlow: avg=0.648; STFlow: avg=0.633 | Direct evidence that CorrFlow’s core claim—improving dependency structure—is empirically validated | That GGC-Pearson perfectly correlates with downstream biological utility; no such analysis performed | [Paper] [Paper: PDF p. 17] Table 7 |
| Statistical significance (Table 12) | CorrFlow’s superiority is statistically robust at gene level | Paired Wilcoxon tests on pooled 500 gene-dataset pairs | All Holm-corrected p < 10⁻¹⁶; vs. STFlow: mean diff=0.0129, wins=330/500 | The observed PCC advantage is not due to chance or dataset-level averaging artifacts | That every single gene benefits; 170 losses indicate some genes are worse | [Paper] [Paper: PDF p. 19] Table 12 |

## 11 对结论的正确理解  
论文结论应被理解为：**在 HEST-1K 这一特定、泄漏控制的、患者分层的 benchmark 下，CorrFlow 通过其双机制设计，在 PCC/HPCC/GGC-Pearson 等指标上实现了统计显著且稳健的提升，且提升源于其对基因依赖的显式建模**。这不是一个泛泛而谈的“更好模型”，而是对一个被严格证明存在的结构性缺陷（Proposition 1）的针对性修复。其结论成立的关键边界是：（1）评估基于 HMHVG-50 等预选基因集，而非全转录组；（2）依赖于 STRING/WGCNA 图的可用性与质量；（3）效果在 HEST-1K 内部 CV 上稳健，但尚未在完全独立外部队列上验证 [Paper] [Paper: PDF p. 19]。因此，正确理解是：“CorrFlow 为 histology-to-ST 生成提供了一种原理清晰、证据充分、在当前主流 benchmark 上有效的依赖感知范式”，而非“解决了所有 ST 生成问题”。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| Lack of external validation | Evaluation uses HEST-1K (diverse but internal) and STImage-1K4M (non-standard splits); no fully independent external cohort with different tissue prep, platform, scanner | Incorporate independently collected ST cohorts to rigorously evaluate out-of-distribution generalization | [Paper] [Paper: PDF p. 19] |
| Insufficient clinical readiness | Prediction quality, while best-in-benchmark, remains insufficient for direct clinical translation due to intrinsic challenge of inferring molecular states from morphology alone | Improve robustness via stronger dependency-aware modeling and higher-quality ST training data | [Paper] [Paper: PDF p. 19] |
| Downstream utility unassessed | Current evaluation focuses on reconstruction fidelity (PCC) and structure preservation (GGC), not biological/clinical utility | Assess whether generated ST profiles benefit downstream tasks: tissue-domain identification, pathway activity estimation, biomarker discovery, patient stratification, prognosis modeling | [Paper] [Paper: PDF p. 19–20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| The "learnable mask token" m is shared across all spatial locations (n) and all genes (g) in the mask set M [Paper] [Paper: PDF p. 5], meaning it cannot encode gene-specific or location-specific masking semantics. | This design conflates two distinct concepts: (i) a generic placeholder for *any* masked gene, and (ii) a gene-specific prior (e.g., expected expression level of KRT7). A gene-specific token could better guide imputation. | If masking is meant to simulate biological uncertainty, a uniform token ignores known gene-specific baselines (e.g., housekeeping vs. low-abundance genes), potentially weakening the dependency signal. | Replace scalar m with gene-specific vector m_g; compare PCC and gene-level error distribution (e.g., does KRT7 imputation improve more than background genes?). | [Paper] [Paper: PDF p. 5] “learnable gene-wise mask tokens m ∈ ℝᴳ, shared across spatial locations” |
| The graph fusion weight α=0.6 favors STRING over WGCNA [Paper] [Paper: PDF p. 9], yet Table 5 shows w/o STRING (0.604) hurts performance more than w/o WGCNA (0.607), suggesting STRING is more critical. However, STRING is static and may not reflect tissue-specific regulation. | Relying heavily on a static functional prior risks misalignment in contexts where co-expression diverges from protein interaction (e.g., post-transcriptional regulation, tumor-specific rewiring). The model may over-smooth tissue-specific signals. | This could explain why gains are larger on HPCC (pathway-focused) than on raw PCC, and why some datasets (e.g., HCC in Table 1) show large absolute PCC gaps but modest HPCC gaps. | Train separate models with α=0.0 (WGCNA-only) and α=1.0 (STRING-only); analyze per-dataset PCC/HPCC delta and correlate with tissue type (e.g., does α=1.0 work better in homogeneous tissues like SKCM?). | [Paper] [Paper: PDF p. 9] Table 3 (α=0.6 best), Table 5 (w/o STRING drop > w/o WGCNA drop) |
| The Huber loss (Eq. 11) and Laplacian loss (Eq. 12) both aim for smoothness but operate on different scales; however, the paper does not analyze whether they conflict (e.g., Lglobal may suppress biologically valid high-frequency variation captured by Llocal). | Over-regularization could flatten genuine biological heterogeneity, such as sharp expression boundaries between tumor and stroma, which are crucial for domain identification. | This directly impacts the "biological coherence" claim—if coherence means "smooth", it may sacrifice "spatially resolved biological accuracy". | Visualize Llocal and Lglobal gradients on a sample; compute spatial gradient magnitude of ˆx₁ before/after applying each loss term; correlate with ground-truth domain annotations. | [Paper] [Paper: PDF p. 6–7] Llocal for "pairwise consistency", Lglobal for "graph-wide patterns"; no conflict analysis |

## 14 学到的知识  
- **Flow matching 的结构性缺陷是可证明、可修复的**：Proposition 1 不是经验观察，而是从 CFM 目标函数导出的必然结论；Annealed-MFM 是其第一个被证明能改变最优解性质的修复方案（Proposition 2）。  
- **掩码策略的设计必须与生成动力学耦合**：简单随机掩码（如 BERT）无效；p(t) ∝ t 的 annealing 是针对 t→1 时 shortcut 问题的精准干预，非启发式技巧。  
- **生物学图谱应作为正则化器，而非特征编码器**：CorrFlow 不将 STRING/WGCNA 输入网络，而是将其转化为对 *输出* ˆx₁ 的软约束（Llocal/Lglobal），这更符合“先验应指导结果而非扭曲特征”的原则。  
- **指标选择揭示建模意图**：HPCC（Eq. 13）和 GGC-Pearson（Eq. 20）不是锦上添花，而是 CorrFlow 核心主张的直接验证工具——它们量化了“通路级”和“基因对级”的一致性，比单一 PCC 更贴近论文目标。  
- **计算效率与科学严谨可兼得**：CorrFlow 与 STFlow 参数量相同（Table 14），证明创新在 loss 设计而非模型规模，这对资源受限的 biomedical AI 研究极具借鉴价值。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：本文的“annealed masking”与 single-cell foundation models 中的 masked autoencoding（如 scGPT）有形式相似性，但目标迥异——前者旨在诱导跨基因条件推理，后者旨在学习通用表征；CorrFlow 的图正则化与 spatial transcriptomics 中的 graph neural networks（如 SpaGCN [9]）共享图结构思想，但 SpaGCN 用于聚类/spot embedding，CorrFlow 将图嵌入生成动力学，属 novel application。  
- **候选连接/方法论连接**：其“dependency-aware generation”思路与 perturbation prediction 任务（如 CausalCell）高度共鸣——两者均需建模基因扰动后的联合响应，CorrFlow 的 annealed-MFM 可视为一种无扰动的、自监督的依赖发现机制。  
- **候选连接/方法论连接**：multi-omics 对齐常依赖 cross-modal contrastive learning；CorrFlow 的 conditional flow matching on histology→ST offers an alternative generative alignment paradigm, where the “alignment” is enforced by the joint flow trajectory and graph constraints, not by shared latent space.

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Gene-Specific Annealed Masking  
  **originating limitation/observation**: [Analysis] The shared learnable mask token m ignores gene-specific expression baselines and may weaken dependency signal [Paper] [Paper: PDF p. 5].  
  **core hypothesis**: Assigning gene-specific mask tokens m_g, initialized to gene-wise median expression from training data, will improve imputation accuracy for biologically relevant genes (e.g., markers) without harming others.  
  **delta from paper**: Replace scalar m with vector m ∈ ℝᴳ; initialize m_g to median(x¹_g) over training spots.  
  **initial method**: Implement in CorrFlow codebase; train on HEST-1K HMHVG-50; compare PCC per gene (especially top-10 AvgAbsCorr genes from Fig. 3c).  
  **validation**: Significant PCC improvement (>0.02) on ≥5 marker genes (e.g., KRT7, CD44) with no degradation on housekeeping genes (e.g., ACTB, GAPDH).  
  **failure modes**: Increased overfitting if m_g is over-optimized; failure to converge if initialization is poor.  
  **innovation status**: unverified  

- **name**: Dynamic Graph Fusion for Perturbation Context  
  **originating limitation/observation**: Static STRING/WGCNA fusion (Eq. 9) may misalign in perturbed states (e.g., drug treatment), where co-expression rewires [Paper] [Paper: PDF p. 9].  
  **core hypothesis**: A lightweight adapter that modulates α based on histology-derived perturbation cues (e.g., necrosis, mitotic count) will improve ST prediction under intervention.  
  **delta from paper**: Replace fixed α with α = σ(Wz + b), where z is histology feature vector, σ is sigmoid.  
  **initial method**: Add adapter head to UNI encoder; train end-to-end on simulated perturbation dataset (e.g., HEST-1K + synthetic drug-response patches).  
  **validation**: On held-out perturbed samples, achieve >0.03 PCC gain over fixed-α CorrFlow and >0.05 over STFlow.  
  **failure modes**: Adapter collapses to constant α; introduces noise that degrades baseline performance.  
  **innovation status**: unverified  

- **name**: Cross-Modal Alignment via Joint Flow Trajectories  
  **originating limitation/observation**: CorrFlow aligns histology→ST, but multi-omics requires alignment across modalities (e.g., ATAC+RNA); its flow matching framework is inherently extendable.  
  **core hypothesis**: Modeling ATAC→RNA and histology→RNA as *joint* conditional flows (with shared graph regularization) will improve cross-modal imputation consistency.  
  **delta from paper**: Extend CorrFlow to multi-condition: vθ(˜xt, t, c_histology, c_atac); share Lgraph across modalities; add modality-specific masking.  
  **initial method**: Adapt to paired ATAC/RNA/histology dataset (e.g., SNARE-seq + H&E); use same STRING+WGCNA graph; report joint PCC and cross-modal correlation preservation.  
  **validation**: Joint model achieves higher GGC-Pearson on RNA than either single-modality model, and improves ATAC→RNA PCC by >0.02.  
  **failure modes**: Optimization instability from multi-condition input; graph regularization over-constrains modality-specific signals.  
  **innovation status**: unverified