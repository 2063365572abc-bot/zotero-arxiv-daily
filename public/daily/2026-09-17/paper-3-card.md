> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **标题**: MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics  
- **作者**: Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim  
- **出处**: arXiv preprint arXiv:2609.13665v1 [cs.CV], 2026-09-12  
- **核心任务**: 预测 subcellular spatial transcriptomics (SST) 中候选细胞分割掩码的跨方法共识支持度（pixel-level consensus-support map），无需运行多方法集成推理  
- **输入**: 候选二值掩码 $F_k$、配准的 DAPI 形态图像 $D$、转录本密度图 $T$ [Paper: PDF p. 3]  
- **输出**: 连续值共识支持图 $\hat{C}_k \in [0,1]^{H\times W}$，及其细胞级聚合得分 $S_{k,c}$ [Paper: PDF p. 3–5]  
- **关键创新**: Leave-one-method-out 伪监督 + Foreground-Union Consensus Loss (FUCL) + morphology-transcript-aware U-Net 架构  
- **评估数据集**: 10x Genomics Xenium FFPE human renal cell carcinoma dataset，空间留出划分，共 4,642 测试 tile [Paper: PDF p. 5]  
- **候选方法**: Cellpose-SAM, BIDCell, ProSeg, Xenium 10x onboard segmentation [Paper: PDF p. 5]  
- **代码/数据地址**: 未核验  
- **机构信息**: 未核验（仅从作者单位列表推断为悉尼大学相关机构，但未在文中作为研究背景陈述）  

## 02 一句话总结  
MARC 是一种 morphology-aware 的回归模型，通过以 leave-one-method-out 多方法共识为伪标签、以 foreground-union mask 为损失聚焦区域进行训练，仅需单个候选掩码 $F_k$、DAPI 形态 $D$ 和转录本密度 $T$ 即可预测像素级共识支持图 $\hat{C}_k$，在 Xenium 肾癌数据上实现平均 Dice 0.9002 与细胞级 Spearman 相关系数 0.7905，逼近显式多方法共识而免于多管道推理 [Paper: PDF p. 1, 4–5]。

## 03 研究问题  
- 如何在 subcellular spatial transcriptomics (SST) 中对**无真值标注**的候选细胞分割结果进行**可扩展、共识感知的质量评估**？[Paper: PDF p. 1]  
- 如何避免显式多方法共识构造（explicit multi-method consensus construction）所需的计算密集型多管道执行？[Paper: PDF p. 2]  
- 如何将形态学（DAPI）与分子信号（transcript density）整合进共识支持预测，超越候选掩码几何本身？[Paper: PDF p. 5–6]  

## 04 研究背景与发展路径  
SST 细胞分割面临三重挑战：(1) 边界本质模糊（morphological contrast weak, transcripts sparse/displaced, cells densely packed）[Paper: PDF p. 1]; (2) 无可靠 ground truth（manual annotation prohibitively time-consuming, boundaries biologically ambiguous）[Paper: PDF p. 1, 3]; (3) 现有质量评估方法不适用——监督法依赖专家标注，不确定性估计法依赖生成模型内部预测 [Paper: PDF p. 1–3]。  
既有工作分三支：(i) SST 分割方法（Cellpose-SAM, BIDCell, ProSeg, Xenium）因输入/假设不同产生互补但冲突的边界 [Paper: PDF p. 1–2]; (ii) 共识方法（STAPLE, majority voting）提供实用替代真值，但需运行全部 pipeline [Paper: PDF p. 2–3]; (iii) 学习型质量评估（SegQC, Bayesian uncertainty）未针对 SST 设计 [Paper: PDF p. 3]。  
MARC 沿“共识即代理真值”路径演进：不追求单一最优分割，而建模**多方法一致性程度**；将共识构造从 inference-time 移至 training-time，用 pseudo-targets 实现 inference-time 单次前向 [Paper: PDF p. 2–3]。

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|--------------------------|
| **Computational intractability of explicit consensus** | Explicit multi-method consensus requires configuring and running all contributing pipelines with method-specific SST inputs on large tissue regions, limiting routine QC use [Paper: PDF p. 2]. | Each segmentation method has distinct input requirements (e.g., different preprocessing, modality weighting), making ensemble execution non-uniform and resource-heavy [Paper: PDF p. 2]. | Figure 1(a) illustrates computational intensity; Section 1 states “this process is computationally intensive and difficult to scale” [Paper: PDF p. 2]. |
| **Lack of scalable, consensus-aware quality control** | Conventional QC approaches (supervised or uncertainty-based) fail when expert annotations are unavailable and candidate masks come from heterogeneous external pipelines [Paper: PDF p. 1–3]. | Supervised methods require costly manual masks; uncertainty methods require access to the generating model’s internals—neither applies to black-box candidate masks [Paper: PDF p. 1, 3]. | Section 1: “these approaches do not readily support the evaluation of candidate masks produced by different SST segmentation pipelines when expert annotations are unavailable” [Paper: PDF p. 1]. |
| **Ambiguity of SST cell boundaries** | Boundaries cannot be reliably inferred from incomplete morphological and transcript signals alone, leading to biological ambiguity [Paper: PDF p. 1]. | Morphology may lack contrast; transcripts may be sparse or displaced; neighboring cells overlap—making ground truth fundamentally unattainable [Paper: PDF p. 1, 3]. | Abstract: “reliable ground-truth boundaries are unavailable because they must be inferred from incomplete morphological and transcript signals” [Paper: PDF p. 1]. |

## 06 核心思想  
将 SST 细胞分割质量评估重构为**稠密共识回归问题（dense consensus-regression problem）**：不直接优化分割掩码，而是学习从单个候选掩码 $F_k$、DAPI 形态 $D$、转录本密度 $T$ 预测其在 leave-one-method-out 多方法共识中的支持强度 $\hat{C}_k$ [Paper: PDF p. 2]。该预测在 inference 时免于多方法执行，且其细胞级聚合得分 $S_{k,c}$ 可直接用于排序、过滤或人工复审 [Paper: PDF p. 2, 5]。核心洞见是：**共识不是终点，而是可学习的中间监督信号**；形态与转录本提供互补上下文，使模型能泛化至未见的边界歧义区域 [Paper: PDF p. 5–6]。

## 07 方法总览  
MARC 是一个四层 U-Net 架构 [Paper: PDF p. 3]，输入为三通道张量 $X_k = \text{concat}(D, T, F_k)$ [Eq. 2, Paper: PDF p. 3]；输出为连续值共识支持图 $\hat{C}_k = f_\theta(X_k) \in [0,1]^{H\times W}$，经 sigmoid 激活 [Eq. 4, Paper: PDF p. 3]。训练采用 leave-one-method-out 伪标签 $C_{(-k)}$（其余 $K-1=3$ 个方法前景图的算术平均）[Eq. 5, Paper: PDF p. 3]，并定义 foreground-union mask $U_k$（覆盖候选前景或共识前景的像素）[Eq. 6, Paper: PDF p. 4]；损失函数 FUCL 为 $U_k$ 区域内 $\hat{C}_k$ 与 $C_{(-k)}$ 的平均绝对误差 [Eq. 7, Paper: PDF p. 4]。细胞级得分 $S_{k,c}$ 由 $\hat{C}_k$ 在原始标记掩码 $M_k$ 对应细胞像素上平均得到 [Eq. 8, Paper: PDF p. 5]。

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Leave-one-method-out consensus target $C_{(-k)}$** | Generates pseudo-ground-truth by averaging binary foreground maps of all *other* $K-1$ methods, excluding candidate $k$ [Eq. 5, Paper: PDF p. 3]. | Prevents trivial self-agreement supervision; provides scalable surrogate for ground truth where manual annotation is infeasible [Paper: PDF p. 3]. | Input: $\{F_j\}_{j\neq k}$; Output: $C_{(-k)} \in [0,1]^{H\times W}$ [Eq. 5]. | Section 3.3: “Excluding the candidate method from its own target prevents the model from receiving trivial self-agreement as supervision” [Paper: PDF p. 3]. | Removal would cause overfitting to candidate geometry; ablation shows mean-consensus outperforms STAPLE in sensitivity & ranking [Paper: PDF p. 5]. |
| **Foreground-Union Consensus Loss (FUCL)** | Computes mean absolute error only within union mask $U_k = F_k \lor C_{(-k)}$, focusing gradients on foreground and disagreement regions [Eq. 7, Paper: PDF p. 4]. | Ensures learning prioritizes biologically relevant pixels (cell interiors & boundaries) rather than background; avoids dilution by zero-loss background pixels [Paper: PDF p. 4]. | Input: $\hat{C}_k, C_{(-k)}, U_k$; Output: scalar loss $L^{(k)}_{\text{FU}}$ [Eq. 7]. | Equation 7 clamps denominator to avoid division-by-zero; caption of Figure 2 cites FUCL [Paper: PDF p. 4]. | Removal would degrade foreground metrics (Dice/IoU); Table 1 shows high Dice (0.9002) implies FUCL successfully focuses on foreground. |
| **Morphology-Transcript-Candidate tri-input** | Concatenates DAPI morphology $D$, transcript density $T$, and candidate foreground $F_k$ into 3-channel input $X_k$ [Eq. 2, Paper: PDF p. 3]. | Candidate mask alone is insufficient; morphology provides nuclear context, transcripts provide molecular evidence—both complementary to geometry [Paper: PDF p. 5–6]. | Input: $D,T,F_k$; Output: $X_k \in \mathbb{R}^{3\times H\times W}$ [Eq. 2]. | Table 2 ablation: adding DAPI boosts Spearman ρ from 0.4228 → 0.7564; adding transcripts further → 0.7905 [Paper: PDF p. 6]. | Removal of $D$ or $T$ degrades both pixel-level (Dice) and cell-level (ρ) performance significantly (Table 2). |
| **Cell-level aggregation via $S_{k,c}$** | Averages predicted consensus $\hat{C}_k$ over pixels assigned to each candidate cell $c$ in labelled mask $M_k$ [Eq. 8, Paper: PDF p. 5]. | Enables practical QC: scores rank cells by consensus support for manual review/filtering, bridging pixel prediction to biological interpretation [Paper: PDF p. 5]. | Input: $\hat{C}_k, M_k$; Output: scalar $S_{k,c}$ per cell [Eq. 8]. | Figure 3 plots $S_{k,c}$ vs target; Section 4.2: “scores can be used to rank cells for manual review” [Paper: PDF p. 5]. | Without aggregation, no cell-level ranking possible; candidate-copy baseline has constant scores (undefined ρ in Table 2) [Paper: PDF p. 6]. |

## 09 关键公式与符号  

| Symbol | Definition | Context / Page | Notes |
|--------|------------|----------------|-------|
| $M_k$ | Labelled mask from candidate method $k$, $M_k \in \{0,1,\dots\}^{H\times W}$ | [Eq. 1, Paper: PDF p. 3] | Positive values = cell instance IDs; 0 = background. |
| $F_k(x,y)$ | Binary foreground map: $1$ if $M_k(x,y)>0$, else $0$ | [Eq. 1, Paper: PDF p. 3] | Derived from $M_k$; used as input channel. |
| $D, T$ | Aligned DAPI morphology image and transcript-density image, both $\in \mathbb{R}^{H\times W}$ | [Paper: PDF p. 3] | Pre-aligned to same grid (0.2125 µm/pixel) [Paper: PDF p. 5]. |
| $X_k$ | Three-channel input: $X_k = \text{concat}(D, T, F_k) \in \mathbb{R}^{3\times H\times W}$ | [Eq. 2, Paper: PDF p. 3] | Core input to MARC encoder. |
| $\hat{C}_k$ | Predicted continuous consensus-support map: $\hat{C}_k = f_\theta(X_k) \in [0,1]^{H\times W}$ | [Eq. 3, Paper: PDF p. 3] | Output of U-Net decoder + sigmoid [Eq. 4]. |
| $C_{(-k)}(x,y)$ | Leave-one-method-out consensus target: mean of other $K-1$ methods’ $F_j$ | [Eq. 5, Paper: PDF p. 3] | $K=4$ in experiments; $C_{(-k)} = \frac{1}{3}\sum_{j\neq k} F_j$ [Paper: PDF p. 3]. |
| $U_k(x,y)$ | Foreground-union mask: $1$ if $F_k(x,y)=1$ OR $C_{(-k)}(x,y)>0$ | [Eq. 6, Paper: PDF p. 4] | Defines region for FUCL computation. |
| $L^{(k)}_{\text{FU}}$ | Foreground-Union Consensus Loss: MAE of $\hat{C}_k$ vs $C_{(-k)}$ over $U_k$ | [Eq. 7, Paper: PDF p. 4] | Denominator clamped to ≥1 to avoid division-by-zero. |
| $S_{k,c}$ | Cell-level consensus score for candidate cell $c$: mean $\hat{C}_k$ over pixels in $M_k=c$ | [Eq. 8, Paper: PDF p. 5] | Used for ranking; Spearman ρ computed between $\{S_{k,c}\}$ and $\{C_{(-k),c}\}$. |

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| **Main evaluation (Table 1)** | MARC predicts explicit leave-one-method-out consensus $C_{(-k)}$ with high fidelity at pixel and cell levels. | MARC trained on 4 candidate methods (Cellpose-SAM, BIDCell, ProSeg, Xenium); evaluated on held-out test tiles (4,642) against $C_{(-k)}$ targets. Metrics: Foreground-union L1, Dice, IoU, Sensitivity, Precision, Cell Spearman ρ. | Avg. Dice = 0.9002, Avg. ρ = 0.7905; best per-method Dice up to 0.9127 (Xenium 10x). | MARC closely approximates explicit cross-method consensus without multi-method inference. | MARC achieves *biological* ground-truth accuracy (not claimed; authors state consensus is a surrogate) [Paper: PDF p. 7]. | Table 1, Section 4.2 [Paper: PDF p. 4–5] |
| **Input ablation (Table 2)** | DAPI morphology and transcript density provide complementary signal beyond candidate-mask geometry. | Four configurations: (i) candidate-copy baseline (no model), (ii) MARC with $F_k$ only, (iii) $F_k+D$, (iv) $F_k+D+T$. All trained with same $C_{(-k)}$ target and FUCL. | Adding $D$: Dice ↑ 0.8565→0.8866, ρ ↑ 0.4228→0.7564; Adding $T$: Dice ↑ 0.8866→0.9002, ρ ↑ 0.7564→0.7905. | Morphology is primary driver for cell-level ranking; transcripts add complementary molecular signal improving both pixel and cell metrics. | Transcript density is *necessary* for high performance (not tested; ablation shows incremental gain, not necessity). | Table 2, Section 4.3 [Paper: PDF p. 6] |
| **Target ablation (Section 4.3)** | Arithmetic mean consensus is a viable and pragmatic pseudo-target compared to STAPLE. | Two MARC models: one trained on mean $C_{(-k)}$, one on STAPLE fusion of same three masks. Identical inputs/architecture/loss. Evaluated against respective targets. | Mean: Avg. Dice 0.9002, ρ 0.7905; STAPLE: Avg. Dice 0.8992, ρ 0.7491. Mean has higher sensitivity, STAPLE higher precision. | Mean consensus is sufficient and directly interpretable (fraction of supporting methods); trade-offs exist but mean is preferred for primary evaluation. | STAPLE is *inferior* (not supported; models evaluated on different targets, so no cross-target accuracy claim) [Paper: PDF p. 5]. | Section 4.3 [Paper: PDF p. 5] |
| **Qualitative analysis (Figure 4)** | MARC localises weakly supported regions and produces spatially varying predictions aligned with biological evidence. | Visual inspection of predicted $\hat{C}_k$ and cell-level maps on held-out test region, overlaid with DAPI, $T$, $F_k$. | High $\hat{C}_k$ where candidate aligns with nuclear morphology & transcript density & cross-method support; low $\hat{C}_k$ where candidate extends into background or disagrees with evidence. | MARC captures contextual agreement, enabling identification of ambiguous cells for review. | MARC’s spatial predictions are *causally explained* by morphology/transcripts (not established; correlation shown, not mechanism) [Paper: PDF p. 7]. | Figure 4, Section 4.4 [Paper: PDF p. 6–7] |

## 11 对结论的正确理解  
- MARC **approximates explicit multi-method consensus**, not biological ground truth; its success is measured *relative to the consensus surrogate*, not absolute boundary correctness [Paper: PDF p. 1, 7].  
- The high Dice (0.9002) means MARC’s predicted foreground closely overlaps the *leave-one-method-out mean consensus foreground*, not that it recovers true cell boundaries [Paper: PDF p. 4–5].  
- Cell-level Spearman ρ = 0.7905 indicates MARC preserves the *ranking order* of candidate cells by their consensus support (e.g., top 10% lowest-scoring cells are indeed those with weakest multi-method agreement), enabling prioritisation for review—not that absolute score values are calibrated probabilities [Paper: PDF p. 5].  
- Input ablations confirm DAPI and transcripts are *complementary* to candidate geometry, but do not prove they resolve specific biological ambiguities (e.g., mitotic cells, doublets); they improve statistical agreement with consensus [Paper: PDF p. 5–6].  
- “Consensus-aware evaluation” means using MARC’s output scores for QC decisions (e.g., filtering low-$S_{k,c}$ cells), not that MARC itself performs segmentation [Paper: PDF p. 1, 5].

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| **Consensus as surrogate, not ground truth** | Failure modes common across segmentation methods may be reinforced in consensus, making it an imperfect proxy. | Acknowledge utility despite limitation: “such a surrogate is useful because it captures agreement across multiple methods… reducing reliance on any single method’s biases.” | [Paper: PDF p. 7] |
| **Limited generalisability** | Evaluation conducted on single Xenium renal cell carcinoma dataset; candidate methods share inputs from same assay, reducing independence. | Future work: “evaluate additional tissues, platforms, and segmentation methods, incorporate orthogonal membrane or protein markers for validation, and determine whether consensus-guided filtering improves downstream analyses.” | [Paper: PDF p. 7] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|----------------|-------|
| MARC’s training relies on leave-one-method-out consensus $C_{(-k)}$, which assumes errors of the $K-1$ methods are independent and uncorrelated. However, all four candidate methods (Cellpose-SAM, BIDCell, ProSeg, Xenium) operate on the *same underlying Xenium assay data* and likely share systematic biases (e.g., resolution limits, probe efficiency artifacts). | If methods share correlated failure modes (e.g., all miss boundaries in low-DAPI regions), $C_{(-k)}$ may reinforce those errors rather than average them out, making MARC learn to reproduce shared hallucinations. This undermines the “surrogate truth” assumption. | Compromises validity of MARC’s pseudo-supervision: high Dice against $C_{(-k)}$ may reflect agreement on wrong boundaries, not accurate consensus. Impacts trust in low-$S_{k,c}$ cells flagged for review. | Train MARC on datasets with truly orthogonal inputs (e.g., Xenium + MERFISH + seqFISH+), or inject controlled synthetic errors into one method and measure MARC’s sensitivity to breaking consensus. Compare MARC’s low-score cells against orthogonal validation (e.g., membrane stains). | Authors state “candidate methods also share inputs from the same Xenium assay and are therefore not fully independent” [Paper: PDF p. 7]; consensus literature notes correlated raters bias STAPLE-like estimates [21]. |
| The Foreground-Union Consensus Loss (FUCL) excludes background pixels ($U_k=0$) from gradient updates. While this focuses learning, it may cause MARC to ignore contextual cues *outside* the foreground that help resolve boundary ambiguity (e.g., transcript deserts adjacent to a cell may indicate a sharp boundary). | Background regions contain discriminative information for boundary refinement (e.g., intensity gradients, neighbor cell proximity). Ignoring them could limit MARC’s ability to correct over-segmentation where candidate $F_k$ bleeds into low-signal background. | May explain why precision (0.8843) lags sensitivity (0.9168) in Table 1—MARC is good at recalling consensus foreground but less precise at excluding false positives near boundaries. | Modify FUCL to include a weighted background term (e.g., inverse distance to nearest foreground pixel) or train with a hybrid loss (FUCL + background-aware auxiliary task). Measure precision/sensitivity trade-off. | FUCL definition explicitly restricts loss to $U_k$ [Eq. 7, Paper: PDF p. 4]; Section 4.2 notes thresholding at 0.5 corresponds to “majority of other three methods” [Paper: PDF p. 5], implying binary treatment of support. |
| Cell-level aggregation (Eq. 8) computes simple mean of $\hat{C}_k$ over cell pixels. This treats all pixels equally, but boundary pixels are more informative for consensus than cell interior pixels (where all methods likely agree). | Uniform averaging dilutes boundary disagreement signals. A cell with high interior consensus but low boundary consensus may receive a misleadingly high $S_{k,c}$, masking its segmentation ambiguity. | Reduces utility for QC: cells needing review may be missed if ambiguity is localized to boundaries. Contradicts goal of “localis[ing] weakly supported regions” [Paper: PDF p. 7]. | Replace mean with boundary-weighted average (e.g., using morphological gradient of $F_k$ as weight) or compute separate interior/boundary scores. Correlate new score with manual boundary error rates. | Figure 4 shows spatially varying $\hat{C}_k$ predictions, including low values at boundaries [Paper: PDF p. 6–7]; Eq. 8 specifies uniform mean [Paper: PDF p. 5]. |

## 14 学到的知识  
- In SST, **consensus among complementary segmentation methods is a pragmatic, scalable surrogate for ground truth**, especially when manual annotation is infeasible and boundaries are biologically ambiguous [Paper: PDF p. 1, 7].  
- **Dense regression of consensus support** (rather than segmentation or uncertainty estimation) is a viable QC paradigm, enabling inference-time efficiency and spatially resolved quality maps [Paper: PDF p. 2, 5].  
- **Morphology (DAPI) is the dominant contextual signal for cell-level ranking**, while **transcript density provides complementary molecular information**, jointly boosting both pixel-level consensus prediction and cell-level Spearman correlation [Paper: PDF p. 5–6, Table 2].  
- **Foreground-union masking** for loss computation effectively focuses training on biologically relevant regions (foreground + disagreements) and avoids background noise dilution [Paper: PDF p. 4, Eq. 7].  
- **Leave-one-method-out pseudo-supervision** prevents trivial self-agreement and enables learning from ensemble disagreement without requiring ensemble execution at inference [Paper: PDF p. 3].  

## 15 与既有知识的连接  
- **single-cell foundation models**: Weak connection/methodological connection. MARC does not build or use foundation models; it’s a task-specific regression model. However, its use of multi-modal inputs (morphology + transcripts) aligns with foundation model goals of cross-modal integration, and its consensus-aware design could inspire foundation model evaluation protocols.  
- **spatial transcriptomics**: Direct domain application. MARC addresses the core SST bottleneck of cell segmentation QC, specifically for subcellular resolution (Xenium), leveraging spatially aligned DAPI and transcript density—core SST data modalities [Paper: PDF p. 1, 5].  
- **graph neural networks**: Weak connection. GNNs are used in some SST segmentation methods (e.g., Baysor [3]), but MARC is CNN-based (U-Net) and makes no use of graph structures. No GNN component or motivation is present.  
- **multi-omics**: Methodological connection. MARC fuses imaging (DAPI) and molecular (transcript density) data—a minimal multi-omics setup—demonstrating that even two modalities yield significant gains over single-modality baselines [Paper: PDF p. 5–6].  
- **biomedical AI**: Direct application. MARC is a biomedical AI tool for quality control in computational pathology, following best practices: clear problem framing, ablation studies, quantitative benchmarks, and qualitative validation [Paper: PDF p. 1–7].  
- **perturbation prediction / cell state representation / cross-modal alignment**: Weak connection. MARC does not predict perturbations, model cell states, or perform cross-modal alignment (e.g., image-to-RNA mapping); it uses pre-aligned inputs for consensus regression. Selection note confirms “未显式建模cell state或跨模态对齐” [Selection reason].  

## 16 研究想法  

- **name**: Consensus-Guided Boundary Refinement (CGBR)  
  **originating limitation/observation**: MARC outputs spatially varying consensus support $\hat{C}_k$ but does not use it to *refine* the candidate segmentation; low-$\hat{C}_k$ boundary pixels indicate ambiguity needing correction [Paper: PDF p. 6–7, Fig 4].  
  **core hypothesis**: Integrating MARC’s pixel-level $\hat{C}_k$ as a spatial attention mask into a segmentation refinement module will improve boundary accuracy more than post-hoc filtering.  
  **delta from paper**: MARC is a QC tool; CGBR repurposes its output as a trainable guidance signal for segmentation correction, moving from evaluation to improvement.  
  **initial method**: Augment a lightweight U-Net refinement head that takes $(D, T, F_k, \hat{C}_k)$ and outputs a refined mask $F_k^{\text{ref}}$; supervise with Dice loss against $C_{(-k)}$ or orthogonal ground truth.  
  **validation**: Compare $F_k^{\text{ref}}$ vs original $F_k$ on boundary F1-score against membrane stain validation; measure downstream impact on cell-type annotation consistency.  
  **failure modes**: Over-correction where $\hat{C}_k$ is noisy; failure to generalise to unseen tissue types.  
  **innovation status**: unverified  

- **name**: Orthogonal Consensus Validation (OCV)  
  **originating limitation/observation**: Authors acknowledge consensus is a surrogate and candidate methods are not fully independent due to shared Xenium assay inputs [Paper: PDF p. 7]; this risks reinforcing correlated errors.  
  **core hypothesis**: Introducing an orthogonal modality (e.g., immunofluorescence membrane marker) as an independent consensus anchor will break error correlations and yield a more robust surrogate.  
  **delta from paper**: Replaces leave-one-method-out consensus with leave-one-modality-out consensus (e.g., $C_{(-\text{membrane})}$ = mean of DAPI-based, transcript-based, and morphology-transcript fusion methods).  
  **initial method**: Acquire membrane stain for subset of Xenium tiles; train MARC variants with membrane-informed $C_{(-k)}$ targets; compare Dice/ρ against membrane-ground-truth boundaries.  
  **validation**: Quantify reduction in shared failure modes (e.g., via disagreement heatmaps); test generalisability to new tissues lacking membrane stain.  
  **failure modes**: Membrane stain misalignment; limited availability of high-quality orthogonal markers.  
  **innovation status**: unverified  

- **name**: Boundary-Weighted Consensus Scoring (BWCS)  
  **originating limitation/observation**: Cell-level aggregation (Eq. 8) uses uniform mean, diluting boundary disagreement signals critical for QC [Analysis in 13].  
  **core hypothesis**: Weighting $\hat{C}_k$ pixels by their distance to the candidate cell boundary (e.g., morphological gradient magnitude) will produce cell scores more sensitive to segmentation ambiguity.  
  **delta from paper**: Modifies Eq. 8 to $S_{k,c}^{\text{BW}} = \frac{\sum_{(x,y)\in c} w(x,y) \cdot \hat{C}_k(x,y)}{\sum_{(x,y)\in c} w(x,y)}$, where $w$ peaks at boundaries.  
  **initial method**: Compute $w$ from Sobel gradient of $F_k$; recompute cell scores on test set; correlate new scores with manual boundary error counts.  
  **validation**: Compare AUROC of $S_{k,c}^{\text{BW}}$ vs $S_{k,c}$ for detecting manually corrected cells; assess ranking stability under segmentation perturbations.  
  **failure modes**: Gradient computation sensitive to $F_k$ noise; weights may over-prioritise irrelevant texture.  
  **innovation status**: unverified