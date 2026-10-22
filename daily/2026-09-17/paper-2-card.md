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
| Title | MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics | [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper: PDF p. 1] |
| Year | 2026 | [Paper: PDF p. 1] |
| Authors | Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim | [Paper: PDF p. 1] |
| Core task | Pixel-level consensus-support map prediction for SST candidate segmentation masks | [Paper: PDF p. 3, Eq. 3] |
| Input modalities | Candidate binary foreground mask $F_k$, aligned DAPI morphology $D$, transcript-density map $T$ | [Paper: PDF p. 3, Eq. 2] |
| Output | Continuous pixel-wise consensus-support map $\hat{C}_k \in [0,1]^{H\times W}$, aggregated to cell-level scores $S_{k,c}$ | [Paper: PDF p. 3, Eq. 3]; [Paper: PDF p. 5, Eq. 8] |
| Supervision signal | Leave-one-method-out (LOMO) mean consensus $C^{(-k)}$ computed from other three candidate methods | [Paper: PDF p. 3, Eq. 5]; [Paper: PDF p. 4] |
| Loss function | Foreground-Union Consensus Loss (FUCL), mean absolute error over union mask $U_k$ | [Paper: PDF p. 4, Eq. 7] |
| Architecture | Four-level U-Net-style encoder–decoder with 32–256 channel progression; final sigmoid output | [Paper: PDF p. 3, Sec 3.2]; [Figure 2: PDF p. 4] |
| Evaluation dataset | 4,642 held-out tiles from 10x Genomics Xenium FFPE human renal cell carcinoma | [Paper: PDF p. 5, Sec 4.1] |
| Candidate methods | Cellpose-SAM, BIDCell, ProSeg, Xenium 10x onboard segmentation | [Paper: PDF p. 5, Sec 4.1]; [Table 1: PDF p. 4] |
| Key metrics | Pixel-level: Foreground-union L1 ↓, Dice ↑, IoU ↑; Cell-level: Spearman ρ ↑ | [Table 1: PDF p. 4]; [Paper: PDF p. 5] |

## 02 一句话总结  
本文提出 MARC（Morphology-Aware Regression of Consensus），一种无需多方法推理即可预测 subcellular spatial transcriptomics（SST）中候选细胞分割掩码的跨方法共识支持度的深度学习框架；它通过将候选掩码 $F_k$、DAPI 形态 $D$ 和转录密度 $T$ 融合为三通道输入，回归出像素级连续共识支持图 $\hat{C}_k$，从而绕过显式多管道共识构造的计算瓶颈；该方法在 Xenium 肾癌数据上实现平均 Dice 0.9002 与细胞级 Spearman 相关性 0.7905，证明其可替代显式共识用于大规模 SST 分割质量控制，但其本质仍是共识代理（surrogate），非真值。

## 03 研究问题  
SST 中细胞分割质量评估缺乏可靠 ground truth：手动标注成本极高且生物边界本身模糊 [Paper: PDF p. 1]；而现有监督式 QC 方法（如 SegQC）依赖专家修正掩码，不确定性方法（如 Bayesian）需访问生成模型内部状态，均不适用于外部输入的异构候选掩码 [Paper: PDF p. 3]。因此，核心问题是：**如何在无真值、无模型白盒访问权限的前提下，对任意 SST 分割 pipeline 输出的候选掩码进行可扩展、共识感知的质量评估？** 作者假设：多方法间的一致性（consensus）虽非真值，却是最可行的代理监督信号；进一步假设：该共识支持度可被建模为形态与分子上下文驱动的回归任务，而非必须执行全部 pipeline。

## 04 研究背景与发展路径  
传统图像分割 QC 依赖人工标注或模型内不确定性估计，但 SST 的特殊性在于：① 分割直接决定 transcript-to-cell 分配，错误边界引发下游生物学误读 [Paper: PDF p. 1]；② 多种 SST 专用方法（Cellpose-SAM、BIDCell、ProSeg、Xenium）因输入模态与假设不同，产生互补但冲突的边界 [Paper: PDF p. 1–2]；③ 显式共识（如 Figure 1a 所示）需运行全部 pipeline，计算不可扩展 [Paper: PDF p. 2]。已有共识方法（如 STAPLE）仍需多方法执行 [Paper: PDF p. 3]；而 MARC 的发展路径是：放弃“执行共识” → 转向“学习共识模式” → 利用 leave-one-method-out 构造伪标签 → 设计 FUCL 聚焦前景与分歧区 → 实现单次前向即得共识支持图。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| No scalable ground truth | Manual annotation prohibitive for large SST datasets; boundaries biologically ambiguous even for experts | SST tissue contains many densely packed cells; weak morphological contrast, sparse/displaced transcripts [Paper: PDF p. 1] | “manual annotation of a large number of cells is time-consuming” [Paper: PDF p. 1]; “cell boundaries may be biologically ambiguous” [Paper: PDF p. 3] |
| Incompatibility of existing QC methods | SegQC requires expert-corrected masks; Bayesian uncertainty requires access to the segmentation model’s internals | Neither method supports evaluation of externally generated candidate masks when expert annotations are unavailable [Paper: PDF p. 3] | “these approaches do not readily support the evaluation of candidate masks produced by different SST segmentation pipelines when expert annotations are unavailable” [Paper: PDF p. 2] |
| Computational bottleneck of explicit consensus | Running all complementary segmentation pipelines per tile is computationally intensive and difficult to scale | Each method requires its own SST-specific inputs and configuration [Paper: PDF p. 2] | “explicit consensus averages outputs from multiple segmentation pipelines [...] making consensus construction computationally intensive” [Figure 1a: PDF p. 2]; “this process is computationally intensive and difficult to scale” [Paper: PDF p. 2] |
| Lack of consensus-aware representation for downstream use | Candidate masks lack interpretable, spatially resolved quality signals usable for filtering or review | Prior work focuses on generating better masks, not evaluating reliability of external candidates [Paper: PDF p. 3] | “Most existing work focuses on generating improved masks rather than evaluating the reliability of an externally generated candidate mask” [Paper: PDF p. 3] |

## 06 核心思想  
MARC 的核心思想是将“共识质量评估”重构为一个**形态与分子上下文感知的密集回归任务**，而非分类或不确定性估计：它不试图判断某个像素是否属于细胞（segmentation），而是判断该像素在多方法共识中的支持强度（consensus support）。这一范式转变的关键洞察在于——共识不是离散的“是/否”，而是连续的“支持程度”，且该程度可由局部形态（DAPI）、分子信号（transcript density）与候选几何（$F_k$）共同解释。因此，MARC 放弃了传统 QC 对真值或模型内部状态的依赖，转而以 leave-one-method-out 共识为可学习的代理目标，并通过 FUCL 强制模型关注最具判别力的区域（即候选与共识前景的并集），最终实现单次前向即输出空间可解释的质量图。

## 07 方法总览  
MARC 将 SST 分割 QC 解耦为两个阶段：① **训练阶段**：以每个候选方法 $k$ 的掩码 $F_k$、DAPI $D$、转录密度 $T$ 为输入，构建三通道张量 $X_k = \text{concat}(D,T,F_k)$；监督信号为其余 $K-1=3$ 个方法的平均二值前景图 $C^{(-k)}$；采用 Foreground-Union Consensus Loss（FUCL）优化 U-Net 回归器 $f_\theta$，输出连续共识支持图 $\hat{C}_k$；② **推理阶段**：仅需单次前向，输入任意 $F_k,D,T$，即得 $\hat{C}_k$，再按原始标签图 $M_k$ 聚合为细胞级分数 $S_{k,c}$。全程无需运行其他 segmentation pipeline，突破显式共识的计算墙。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|---------------------|------------------------|-----------------------------------|
| Leave-one-method-out (LOMO) consensus target $C^{(-k)}$ | Construct pseudo-ground-truth by averaging foreground maps of all *other* candidate methods | Provides scalable, multi-source supervision without manual labels or model internals | Input: $K-1$ binary foreground masks $F_j, j\neq k$; Output: $C^{(-k)} \in [0,1]^{H\times W}$ | Eq. 5 [Paper: PDF p. 3]; “excludes the candidate method from its own target prevents trivial self-agreement” [Paper: PDF p. 3] | Without LOMO, model would collapse to identity mapping (candidate-copy baseline Dice=0.8189 < MARC’s 0.9002) [Table 2: PDF p. 6] |
| Foreground-Union Consensus Loss (FUCL) | Compute MAE only over pixels in union of candidate foreground $F_k$ and LOMO consensus foreground $C^{(-k)}$ | Focuses training on discriminative regions (agreement + disagreement), avoids background-dominated gradients | Input: $\hat{C}_k$, $C^{(-k)}$, $U_k$; Output: scalar loss $L^{(k)}_{\text{FU}}$ | Eq. 6–7 [Paper: PDF p. 4]; “restricting the loss to $U_k$ focuses learning on foreground and disagreement regions” [Paper: PDF p. 4] | Without union masking, loss would be diluted by background zeros; ablation not performed but FUCL is core design claim [Paper: PDF p. 4] |
| Three-channel input fusion ($D,T,F_k$) | Encode complementary biological signals: nuclear morphology, transcript abundance, candidate geometry | Candidate mask alone is insufficient (Dice=0.8565); morphology adds ranking power (ρ jumps from 0.42→0.76); transcripts refine both pixel & cell levels | Input: $D,T,F_k$ (each $H\times W$); Output: $X_k \in \mathbb{R}^{3\times H\times W}$ | Eq. 2 [Paper: PDF p. 3]; Table 2 shows progressive gain from $F_k$ → $F_k+D$ → $F_k+D+T$ [PDF p. 6] | Removing $D$: cell-level ρ drops 0.034 (0.7905→0.7564); removing both $D$ & $T$: ρ collapses to 0.4228 [Table 2: PDF p. 6] |
| Cell-level aggregation (Eq. 8) | Convert dense $\hat{C}_k$ into per-cell quality score $S_{k,c}$ by averaging over pixels in cell $c$ | Enables practical QC tasks: ranking cells for manual review, filtering low-consensus cells | Input: $\hat{C}_k$, labelled mask $M_k$; Output: scalar $S_{k,c}$ per cell $c$ | Eq. 8 [Paper: PDF p. 5]; “scores can be used to rank cells for manual review” [Paper: PDF p. 5] | Without aggregation, no cell-level interpretation; candidate-copy baseline yields constant scores (ρ undefined) [Table 2: PDF p. 6] |
| U-Net regression head | Predict continuous $\hat{C}_k$ via encoder-decoder with skip connections | Captures multi-scale morphological and transcript context essential for consensus reasoning | Input: $X_k$; Output: $\hat{C}_k = \sigma(Z_k)$ (sigmoid-clamped) | Figure 2 [PDF p. 4]; Eq. 4 [Paper: PDF p. 3]; “four-level U-Net-style” [Paper: PDF p. 3] | Standard U-Net replaced by classifier head would lose spatial continuity; no ablation reported but architecture choice aligns with dense prediction need |

## 09 关键公式与符号  
论文未提供显式“算法公式”，但明确定义了以下关键符号与可核验关系：  
- $M_k$: 候选方法 $k$ 的带标签掩码（整数矩阵），$M_k(x,y)=c$ 表示像素 $(x,y)$ 属于细胞实例 $c$ [Paper: PDF p. 3, Sec 3.1]  
- $F_k$: $M_k$ 的二值前景图，$F_k(x,y) = \mathbf{1}[M_k(x,y)>0]$ [Eq. 1: PDF p. 3]  
- $D, T$: 对齐的 DAPI 形态图与转录密度图（均为 $H\times W$ 灰度图）[Paper: PDF p. 3, Sec 3.1]  
- $X_k = \text{concat}(D,T,F_k)$: 三通道输入张量 [Eq. 2: PDF p. 3]  
- $\hat{C}_k = f_\theta(X_k) = \sigma(Z_k)$: 连续共识支持图，$[0,1]$ 区间，$f_\theta$ 为 U-Net [Eq. 3–4: PDF p. 3]  
- $C^{(-k)} = \frac{1}{K-1}\sum_{j\neq k} F_j$: leave-one-method-out 共识目标（$K=4$）[Eq. 5: PDF p. 3]  
- $U_k(x,y) = \mathbf{1}[F_k(x,y)=1 \lor C^{(-k)}(x,y)>0]$: 前景并集掩码 [Eq. 6: PDF p. 4]  
- $L^{(k)}_{\text{FU}} = \frac{1}{|U_k|}\sum_{x,y} U_k(x,y)\cdot|\hat{C}_k(x,y)-C^{(-k)}(x,y)|$: FUCL 损失 [Eq. 7: PDF p. 4]  
- $S_{k,c} = \frac{1}{|\{(x,y):M_k(x,y)=c\}|}\sum_{(x,y):M_k(x,y)=c}\hat{C}_k(x,y)$: 细胞级共识分数 [Eq. 8: PDF p. 5]  
- Metrics: Foreground-union L1 (MAE on $U_k$), Dice, IoU, Sensitivity, Precision (all thresholded at 0.5), Cell-level Spearman ρ [Paper: PDF p. 5]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|-------------------------|----------------------------------|--------|
| Table 1 main results | MARC predicts explicit LOMO consensus with high fidelity | MARC vs. explicit $C^{(-k)}$ across 4 candidate methods; same test set (18,443 examples) | Avg. Dice=0.9002, L1=0.0981, ρ=0.7905 | MARC closely approximates explicit cross-method consensus at both pixel and cell levels | MARC predictions are *more accurate* than explicit consensus (no ground truth comparison) | [Table 1: PDF p. 4]; [Paper: PDF p. 5] |
| Table 2 input ablation | Morphology and transcript signals provide complementary information beyond candidate geometry | MARC variants: $F_k$ only / $F_k+D$ / $F_k+D+T$; all trained & evaluated on same LOMO targets | Adding $D$: ρ↑0.3336 (0.4228→0.7564); adding $T$: ρ↑0.0341 (0.7564→0.7905); Dice↑0.0437 (0.8565→0.9002) | DAPI morphology is primary driver for cell-level ranking; transcripts refine both pixel and cell performance | Transcript density is *necessary* for high performance (baseline $F_k+D$ already achieves ρ=0.7564) | [Table 2: PDF p. 6]; [Paper: PDF p. 6] |
| Figure 3 scatter plots | Cell-level aggregation preserves consensus-based ranking | Predicted $S_{k,c}$ vs. target $S^{\text{target}}_{k,c}$ (computed from $C^{(-k)}$) per candidate method | Strong linear trends (ρ=0.6251–0.8802); low-consensus cells clearly separable | Aggregation converts dense map into meaningful, rank-preserving cell scores for QC prioritization | The ranking is *biologically validated* (no external validation, only consensus agreement) | [Figure 3: PDF p. 5]; [Paper: PDF p. 5] |
| Figure 4 qualitative analysis | MARC localises weakly supported regions spatially | Visual inspection of predicted $\hat{C}_k$ vs. DAPI/T/F_k on held-out test tiles | High support where $F_k$ aligns with DAPI nuclei & transcript density; low support where $F_k$ extends into background or disagrees with morphology/molecules | MARC produces spatially varying, interpretable consensus maps that reflect multi-modal evidence | Low-prediction regions correspond to *true segmentation errors* (consensus is surrogate, not ground truth) | [Figure 4: PDF p. 7]; [Paper: PDF p. 7] |
| Target ablation (mean vs. STAPLE) | Mean consensus supervision yields better sensitivity & ranking than STAPLE | Two MARC models: same inputs/architecture/loss, differing only in target ($C^{(-k)}$ mean vs. STAPLE fusion) | Mean: higher sensitivity (0.9168 vs. 0.8860) & ρ (0.7905 vs. 0.7491); STAPLE: higher precision (0.9128 vs. 0.8843) | Mean consensus is pragmatically preferable for QC (prioritizes recall of low-consensus cells) | STAPLE targets are *less accurate* (models evaluated against different targets; no shared ground truth) | [Paper: PDF p. 5–6] |

## 11 对结论的正确理解  
MARC **并未解决 SST 分割的根本歧义性问题**，而是提供了一种**高效、可扩展的共识代理评估工具**：它成功证明，给定一个候选掩码 $F_k$ 及其对应的形态 $D$ 与分子 $T$ 信号，一个轻量 U-Net 可以高保真地回归出该掩码在多方法共识中的支持强度 $\hat{C}_k$，其像素级重叠（Dice 0.90）和细胞级排序（ρ 0.79）均接近显式共识。这意味着：① QC no longer requires running all pipelines —— 单次前向即可获得空间分辨的质量图；② 低共识细胞可被自动识别用于人工复核；③ 共识支持图本身可作为下游分析（如 perturbation prediction）的细胞状态置信度加权因子。但必须清醒认识：**所有结论均相对于 LOMO 共识这一代理目标成立；MARC 的输出是“共识一致性”的度量，而非“生物学正确性”的度量** [Paper: PDF p. 7]。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Consensus as surrogate | Failure modes common to all candidate methods may be reinforced; consensus does not guarantee biological correctness | Acknowledge it’s a pragmatic alternative to manual annotation, reducing reliance on single-method biases | [Paper: PDF p. 7] |
| Limited generalisability | Evaluated only on one Xenium renal cell carcinoma dataset; candidate methods share inputs from same assay, thus not fully independent | Evaluate on additional tissues, platforms, and segmentation methods; incorporate orthogonal membrane/protein markers for validation; test if consensus-guided filtering improves downstream analyses | [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|---------------------------------------------|----------------|------------------|--------|
| MARC’s high cell-level Spearman (ρ=0.79) may reflect correlation with *size* or *compactness*, not true consensus | Candidate masks with larger area or smoother boundaries may inherently receive higher average $\hat{C}_k$ due to geometric averaging bias in Eq. 8, independent of multi-method agreement | Would undermine MARC’s utility for QC: low-consensus small cells (e.g., apoptotic) could be masked by size-driven averaging | Regress $S_{k,c}$ against cell area/roundness; compute partial correlation controlling for morphology features; compare ρ on size-stratified subsets | Eq. 8 aggregates by pixel count; Figure 4 legends report “area in pixels” but no analysis of area-confounding [Figure 4: PDF p. 7] |
| FUCL’s union mask $U_k$ may under-supervise *background disagreement* (e.g., false positives outside all methods’ foreground) | $U_k$ excludes pixels where both $F_k=0$ and $C^{(-k)}=0$; yet false positives in $F_k$ that disagree with *all* other methods are clinically critical errors | Missed false positives reduce QC sensitivity for over-segmentation; FUCL’s focus on foreground may ignore this failure mode | Train variant with full-image MAE or background-weighted loss; compare false positive rates on held-out examples with known artifacts | FUCL definition explicitly restricts to $U_k$ [Eq. 7: PDF p. 4]; no ablation of loss region reported |
| Input ablation shows DAPI dominates ranking gain, but transcript density’s role is underspecified | Table 2 shows $T$ adds only +0.0341 to ρ; yet transcripts are central to SST biology — perhaps $T$’s signal is redundant with DAPI in renal carcinoma, or its encoding (density map) is too coarse | Risks overlooking transcript-specific consensus cues (e.g., gene co-expression patterns) crucial for cell state representation | Replace $T$ with gene-specific or pathway-level transcript embeddings; test on datasets with stronger transcript-morphology discordance (e.g., immune infiltration) | $T$ defined as “transcript-density image” [Paper: PDF p. 3]; no details on binning/resolution or gene selection |

## 14 学到的知识  
- **Consensus-as-supervision paradigm**: 在无真值场景下，leave-one-method-out 共识是可学习、可泛化的高质量代理监督信号，尤其适用于多源异构方法产出的评估任务。  
- **FUCL design principle**: 对密集回归任务，损失函数的空间掩码（如 foreground-union）比全局损失更有效——它 forces the model to attend to discriminative regions (agreement + disagreement)，避免背景主导梯度。  
- **Modality contribution hierarchy**: 在 SST QC，候选几何 $F_k$ provides baseline structure; DAPI morphology $D$ is the dominant signal for *cell-level ranking* (ρ jump +0.33); transcript density $T$ acts as a refinement layer for both pixel accuracy and ranking robustness.  
- **Aggregation matters**: Simple averaging (Eq. 8) suffices for cell-level scores, but its sensitivity to cell size/shape is an unexamined confounder — future work should explore attention-based or morphology-aware pooling.  
- **Evaluation protocol insight**: Reporting both pixel-level (Dice/IoU) and cell-level (Spearman ρ) metrics is essential; high Dice alone doesn’t guarantee useful ranking for QC.

## 15 与既有知识的连接  
- **候选连接/方法论连接**: MARC 的 leave-one-method-out + dense regression framework is directly transferable to **single-cell foundation models**, where consensus among multiple scRNA-seq imputation or batch-correction methods could serve as proxy targets for quality control of latent representations.  
- **候选连接/方法论连接**: The foreground-union loss (FUCL) design resonates with **graph neural networks** for spatial omics — one could define a graph where nodes are superpixels and edges encode morphological/transcript similarity, then apply a GNN to predict consensus support, using $U_k$ as node mask for loss.  
- **候选连接/方法论连接**: MARC’s input fusion ($D,T,F_k$) exemplifies **multi-omics integration at the image level**, offering a blueprint for fusing spatial proteomics (e.g., CODEX) or metabolomics maps with transcript data in future SST QC.  
- **弱连接/方法论连接**: While MARC itself doesn’t perform perturbation prediction, its cell-level consensus score $S_{k,c}$ is a natural confidence weight for **perturbation prediction models** — e.g., downweighting low-$S_{k,c}$ cells in training to improve robustness.  
- **弱连接/方法论连接**: The idea of regressing a “support map” instead of hard segmentation aligns with **cell state representation** goals — one could extend MARC to predict not just consensus, but also state stability (e.g., transcriptional noise) conditioned on multi-modal inputs.

## 16 研究想法  

- **name**: Consensus-Guided Perturbation Filtering (CGPF)  
  **originating limitation/observation**: MARC outputs cell-level consensus scores $S_{k,c}$, but paper does not test whether filtering low-consensus cells improves downstream perturbation prediction [Paper: PDF p. 7].  
  **core hypothesis**: Cells with low MARC consensus ($S_{k,c} < \tau$) exhibit higher technical noise and lower biological signal-to-noise ratio, so excluding them during training will improve perturbation response prediction accuracy.  
  **delta from paper**: MARC is purely a QC tool; CGPF integrates its output as a *training filter* for perturbation models (e.g., scGen, trVAE).  
  **initial method**: On a perturbed SST dataset (e.g., drug-treated Xenium), train perturbation predictor using only cells with $S_{k,c} > 0.7$; compare MSE on held-out perturbed cells vs. full-cell training.  
  **validation**: Downstream metric: correlation between predicted and observed transcript changes for top 100 DEGs; ablation: vary $\tau$ (0.5–0.9).  
  **failure modes**: Over-filtering removes biologically rare but high-fidelity perturbed states; consensus may not correlate with perturbation-specific noise.  
  **innovation status**: unverified  

- **name**: Multi-Modal Consensus Graph (MMCG)  
  **originating limitation/observation**: MARC uses rasterized $D,T,F_k$; but spatial relationships (e.g., cell-cell communication) are lost — a graph representation could capture neighborhood consensus.  
  **core hypothesis**: Consensus support is not only pixel-intrinsic but context-dependent: a cell’s $S_{k,c}$ should be modulated by the consensus scores of its spatial neighbors.  
  **delta from paper**: Replace U-Net with a GNN that takes as node features $[D_c, T_c, \text{area}_c, S^{\text{init}}_c]$ and edge features (distance, morphology similarity), predicting refined $S^{\text{refined}}_c$.  
  **initial method**: Build k-NN graph on cell centroids; use GCN or GAT; supervise on LOMO $S^{\text{target}}_c$; compare ρ with MARC baseline.  
  **validation**: Ablate neighborhood features; visualize attention weights on edges; test on tissue regions with known spatial gradients (e.g., tumor core vs. margin).  
  **failure modes**: Graph construction sensitive to segmentation errors; no guarantee neighborhood consensus improves over pixel-level signal.  
  **innovation status**: unverified  

- **name**: Transcript-Embedding MARC (TE-MARC)  
  **originating limitation/observation**: Input ablation shows transcript density $T$ contributes modestly (+0.0341 ρ); but $T$ is a scalar density map, discarding gene identity — using gene-specific embeddings may unlock stronger signal.  
  **core hypothesis**: Gene-module or pathway-level transcript embeddings (e.g., from scFoundation) contain richer consensus cues than raw density, especially for functionally coherent cell states.  
  **delta from paper**: Replace $T$ (scalar density) with $T_{\text{emb}} \in \mathbb{R}^{d\times H\times W}$, where each channel is a pathway activity score; modify first conv layer to handle $3+d$ channels.  
  **initial method**: Precompute pathway scores (e.g., Hallmark) on Xenium spots; upsample to image grid; train TE-MARC; ablate pathways (e.g., EMT, proliferation).  
  **validation**: Compare ρ gain vs. baseline MARC; check if pathway ablation degrades ρ more for relevant cell types (e.g., EMT pathway for invasive cells).  
  **failure modes**: Pathway scores noisy at subcellular resolution; embedding dimension $d$ may cause overfitting on small dataset.  
  **innovation status**: unverified