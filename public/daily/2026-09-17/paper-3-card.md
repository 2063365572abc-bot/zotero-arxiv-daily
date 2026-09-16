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
- **发布平台**: arXiv  
- **arXiv ID**: arXiv:2609.13665v1  
- **发布日期**: 2026-09-12  
- **研究任务**: subcellular spatial transcriptomics (SST) 中的细胞分割质量评估（consensus-aware segmentation quality control）  
- **核心输出**: 像素级 consensus-support map $\hat{C}_k \in [0,1]^{H\times W}$ 及其细胞级聚合得分 $S_{k,c}$ [Paper: PDF p. 3–5]  
- **输入模态**: 候选掩码 $F_k$、DAPI 形态图像 $D$、转录本密度图 $T$ [Paper: PDF p. 3]  
- **训练监督信号**: leave-one-method-out 显式共识伪标签 $C^{(-k)}$ [Paper: PDF p. 3]  
- **损失函数**: Foreground-Union Consensus Loss (FUCL) [Paper: PDF p. 4]  
- **骨干架构**: 四层 U-Net-style encoder–decoder [Paper: PDF p. 3]  
- **评估数据集**: 10x Genomics Xenium FFPE human renal cell carcinoma dataset，空间留出划分，共 4,642 测试 tile [Paper: PDF p. 5]  
- **候选分割方法**: Cellpose-SAM、BIDCell、ProSeg、Xenium 10x [Paper: PDF p. 5]  

## 02 一句话总结  
MARC 是一种 morphology-aware 的深度回归框架，通过联合建模候选掩码 $F_k$、DAPI 形态 $D$ 和转录本密度 $T$，直接预测像素级多方法共识支持度 $\hat{C}_k$，在推理时无需运行多分割 pipeline，即可逼近显式 leave-one-method-out 共识 $C^{(-k)}$，并在像素级（Dice=0.9002）和细胞级（Spearman ρ=0.7905）均取得高保真度 [Paper: PDF p. 1, 4–5].

## 03 研究问题  
- 如何在 subcellular spatial transcriptomics (SST) 中实现**无真值标注、无模型内生不确定性访问、不依赖多方法并行推理**的细胞分割质量评估？  
- 如何将**多方法共识**这一实用但计算昂贵的 surrogate ground truth，转化为可学习、可泛化的**单次前向预测任务**？  
- 如何使预测的共识支持度既具备**像素级空间分辨能力**，又能生成**有意义的细胞级排序分数**，用于下游人工复核或过滤？ [Paper: PDF p. 1–3]

## 04 研究背景与发展路径  
- **SST 分割瓶颈**：边界模糊源于弱形态对比、稀疏/错位转录本、密集细胞重叠；视觉合理边界 ≠ 生物学合理转录分配 [Paper: PDF p. 1]。  
- **传统 QC 失效**：监督法需专家标注（耗时且 SST 边界本就模糊）[Paper: PDF p. 1]；不确定性估计法需访问生成分割模型的内部状态（不适用于黑盒第三方 pipeline）[Paper: PDF p. 1–3]。  
- **共识作为 surrogate**：多方法分歧反映边界不确定性；形态驱动（如 Cellpose-SAM）与转录驱动（如 Baysor、ProSeg）方法误差源互补 [Paper: PDF p. 1–2]。  
- **显式共识缺陷**：STAPLE 或多数投票需运行全部 K 个 pipeline（含 method-specific 输入预处理），计算不可扩展 [Paper: PDF p. 1–2, 3]。  
- **MARC 路径**：将共识构建从“运行时集成”转为“训练时学习”，用 DAPI + T + $F_k$ 三通道输入回归 $\hat{C}_k$，以 FUCL 聚焦前景与分歧区域 [Paper: PDF p. 2–4].

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|--------------------------|
| **Computational intractability of explicit consensus** | Consensus construction requires executing all K segmentation pipelines with their method-specific SST inputs, making it prohibitive for large-scale SST tissue regions [Paper: PDF p. 1]. | Each method has distinct input requirements (e.g., raw morphology vs. transcript-guided features), and parallel execution scales poorly with cell count [Paper: PDF p. 2]. | Figure 1(a) illustrates multi-pipeline execution; text states “computationally intensive” and “difficult to scale” [Paper: PDF p. 2]. |
| **Lack of scalable, annotation-free ground truth** | No reliable manual annotations exist for SST cell boundaries due to biological ambiguity and annotation cost [Paper: PDF p. 1]. | Boundaries must be inferred from incomplete morphological and transcript signals; dense manual labeling is time-consuming [Paper: PDF p. 1]. | Abstract: “reliable ground-truth boundaries are unavailable”; Introduction: “manual annotation of a large number of cells is time-consuming” [Paper: PDF p. 1]. |
| **Incompatibility of existing QC methods with SST pipelines** | Supervised QC needs expert masks; uncertainty-based QC needs internal model outputs — neither applies to externally generated candidate masks [Paper: PDF p. 1–3]. | SegQC relies on expert-corrected masks; Bayesian uncertainty requires access to the segmentation model’s prediction distribution [Paper: PDF p. 3]. | Section 2.2 explicitly contrasts MARC’s consensus-derived pseudo-supervision with SegQC and Bayesian methods [Paper: PDF p. 3]. |
| **Loss of spatial granularity in cell-level QC** | Candidate-copy baseline assigns uniform score per cell, preventing identification of weakly supported subregions within a cell [Paper: PDF p. 5–6]. | Treating foreground mask as consensus yields constant pixel values → constant cell scores → no ranking capability [Paper: PDF p. 6]. | Table 2 footnote: “Undefined because the candidate-copy baseline produces constant cell-level scores” [Paper: PDF p. 6]. |

## 06 核心思想  
- **Consensus-as-regression**：将多方法共识支持度建模为一个**连续值回归任务**（$\hat{C}_k = f_\theta(D,T,F_k)$），而非离散集成或分类，从而保留空间细节与强度梯度 [Paper: PDF p. 3]。  
- **Morphology-aware context fusion**：显式注入 DAPI 形态与转录本密度作为上下文，使模型能基于**核定位一致性**与**分子信号富集度**判断候选掩码可靠性，超越纯几何（$F_k$）线索 [Paper: PDF p. 3, 6]。  
- **Foreground-union supervision focus**：FUCL 损失仅在候选前景 $F_k$ 或 leave-one-out 共识前景 $C^{(-k)}$ 覆盖的像素上计算，强制模型学习**分歧区域**（如 $F_k=1$ 但 $C^{(-k)}\approx0$）的判别能力 [Paper: PDF p. 4]。  
- **Leave-one-method-out pseudo-targets**：对每个候选方法 $k$，其监督目标 $C^{(-k)}$ 是其余 $K-1$ 方法前景图的算术平均，避免模型学习 trivial self-agreement [Paper: PDF p. 3].

## 07 方法总览  
MARC 是一个端到端的 U-Net 架构，输入为三通道张量 $X_k = \text{concat}(D, T, F_k)$，输出为连续值共识支持图 $\hat{C}_k \in [0,1]^{H\times W}$。训练使用 leave-one-method-out 共识 $C^{(-k)}$ 作为伪标签，并采用 Foreground-Union Consensus Loss (FUCL) 进行优化。推理时仅需单次前向传播，随后通过原始标记掩码 $M_k$ 将 $\hat{C}_k$ 聚合为细胞级得分 $S_{k,c}$。整个流程解耦了共识构建与分割执行，实现计算高效的质量评估 [Paper: PDF p. 2–5].

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Three-channel input concatenation** | Fuses candidate geometry ($F_k$), nuclear morphology ($D$), and molecular context ($T$) into unified representation $X_k$ | Enables joint reasoning about shape, structure, and gene expression; ablation shows DAPI+T add complementary signal beyond $F_k$ alone [Paper: PDF p. 6]. | Input: $D,T,F_k \in \mathbb{R}^{H\times W}$; Output: $X_k \in \mathbb{R}^{3\times H\times W}$ [Eq. 2, Paper: PDF p. 3]. | Equation 2 defines $X_k = \text{concat}(D,T,F_k)$; Table 2 shows Dice ↑ from 0.8565 ($F_k$ only) to 0.9002 ($F_k+D+T$) [Paper: PDF p. 3,6]. | Removal of $D$ or $T$ degrades cell-level Spearman correlation (0.4228 → 0.7564 → 0.7905), indicating loss of ranking ability [Paper: PDF p. 6]. |
| **U-Net encoder–decoder backbone** | Extracts hierarchical features and reconstructs dense pixel-wise prediction $\hat{C}_k$ | Standard architecture for dense prediction; handles multi-scale morphological and transcript patterns [Paper: PDF p. 3]. | Input: $X_k$; Output: logit map $Z_k$, then $\hat{C}_k = \sigma(Z_k)$ [Eq. 4, Paper: PDF p. 3]. | Section 3.2 specifies 4-level U-Net with conv-BN-ReLU blocks and transposed conv decoder [Paper: PDF p. 3]. | Not assessed directly, but U-Net is canonical for biomedical segmentation; replacement would require architectural ablation not performed. |
| **Foreground-Union Consensus Loss (FUCL)** | Computes mean absolute error only over pixels in union of $F_k$ and $C^{(-k)}$ foreground | Focuses training on biologically relevant regions (cell interiors) and disagreement zones, ignoring background where consensus is undefined [Paper: PDF p. 4]. | Input: $\hat{C}_k$, $C^{(-k)}$, $U_k$; Output: scalar loss $L^{(k)}_{\text{FU}}$ [Eq. 7, Paper: PDF p. 4]. | Equation 6 defines $U_k(x,y) = \mathbf{1}[F_k=1 \lor C^{(-k)}>0]$; Eq. 7 defines loss restricted to $U_k$ [Paper: PDF p. 4]. | Using full-image L1 would dilute gradient signal with irrelevant background; FUCL ensures learning concentrates on cell boundaries and ambiguous regions. |
| **Cell-level aggregation via $M_k$** | Converts dense $\hat{C}_k$ into per-cell consensus score $S_{k,c}$ by averaging over pixels assigned to cell $c$ in $M_k$ | Enables practical QC workflows: ranking cells for review, filtering low-confidence instances [Paper: PDF p. 4–5]. | Input: $\hat{C}_k$, $M_k$; Output: scalar $S_{k,c}$ for each cell $c$ [Eq. 8, Paper: PDF p. 5]. | Equation 8: $S_{k,c} = \frac{1}{|\{(x,y):M_k(x,y)=c\}|}\sum_{(x,y):M_k(x,y)=c} \hat{C}_k(x,y)$ [Paper: PDF p. 5]. | Without $M_k$, no cell identity; candidate-copy baseline fails here (constant scores) [Table 2, Paper: PDF p. 6]. |

## 09 关键公式与符号  

| Symbol | Definition | Context & Page | Notes |
|--------|------------|----------------|-------|
| $M_k$ | Labelled mask from candidate method $k$: $M_k \in \{0,1,\dots\}^{H\times W}$, positive values = cell IDs, 0 = background [Eq. 1, Paper: PDF p. 3]. | Section 3.1, Eq. 1 | Basis for cell-level aggregation (Eq. 8). |
| $F_k$ | Binary foreground map of $M_k$: $F_k(x,y) = \begin{cases}1 & M_k(x,y)>0 \\ 0 & \text{otherwise}\end{cases}$ [Eq. 1, Paper: PDF p. 3]. | Eq. 1, Paper: PDF p. 3 | Used in input concatenation (Eq. 2) and FUCL (Eq. 6). |
| $D, T$ | Aligned DAPI morphology image and transcript-density image, both $\in \mathbb{R}^{H\times W}$ [Paper: PDF p. 3]. | Section 3.1, Paper: PDF p. 3 | Provide contextual biological signals beyond $F_k$. |
| $X_k$ | Three-channel input: $X_k = \text{concat}(D,T,F_k) \in \mathbb{R}^{3\times H\times W}$ [Eq. 2, Paper: PDF p. 3]. | Eq. 2, Paper: PDF p. 3 | Core multimodal input to MARC. |
| $\hat{C}_k$ | Predicted continuous consensus-support map: $\hat{C}_k = f_\theta(X_k) \in [0,1]^{H\times W}$ [Eq. 3, Paper: PDF p. 3]. | Eq. 3, Paper: PDF p. 3 | Output of MARC; sigmoid ensures [0,1] range (Eq. 4). |
| $C^{(-k)}$ | Leave-one-method-out consensus target: $C^{(-k)}(x,y) = \frac{1}{K-1}\sum_{j\neq k} F_j(x,y)$ [Eq. 5, Paper: PDF p. 3]. | Eq. 5, Paper: PDF p. 3 | Pseudo-ground truth; arithmetic mean of other $K-1$ methods’ $F_j$. |
| $U_k$ | Foreground-union mask: $U_k(x,y) = \begin{cases}1 & F_k(x,y)=1 \lor C^{(-k)}(x,y)>0 \\ 0 & \text{otherwise}\end{cases}$ [Eq. 6, Paper: PDF p. 4]. | Eq. 6, Paper: PDF p. 4 | Defines region for FUCL computation (Eq. 7). |
| $L^{(k)}_{\text{FU}}$ | Foreground-Union Consensus Loss: $L^{(k)}_{\text{FU}} = \frac{\sum_{x,y} U_k(x,y) |\hat{C}_k(x,y) - C^{(-k)}(x,y)|}{\max(1, \sum_{x,y} U_k(x,y))}$ [Eq. 7, Paper: PDF p. 4]. | Eq. 7, Paper: PDF p. 4 | Clamped denominator avoids division-by-zero. |
| $S_{k,c}$ | Cell-level consensus score for candidate cell $c$: average of $\hat{C}_k$ over pixels in cell $c$ of $M_k$ [Eq. 8, Paper: PDF p. 5]. | Eq. 8, Paper: PDF p. 5 | Enables ranking; Spearman correlation computed between $S_{k,c}$ and target analogues. |

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|-------------------------------|--------|
| **Main evaluation (Table 1)** | MARC predicts explicit leave-one-method-out consensus $C^{(-k)}$ with high fidelity at pixel and cell levels. | MARC trained on 4 methods (Cellpose-SAM, BIDCell, ProSeg, Xenium); evaluated on held-out test tiles (n=18,443) against $C^{(-k)}$ targets; metrics: Foreground-union L1, Dice, IoU, Sensitivity, Precision, Cell Spearman ρ. | Avg. Dice=0.9002, IoU=0.8186, ρ=0.7905; best per-method Dice up to 0.9127 (Xenium) [Table 1, Paper: PDF p. 4]. | MARC closely approximates explicit cross-method consensus without multi-method inference. | MARC achieves *absolute* ground-truth accuracy (impossible, as $C^{(-k)}$ itself is surrogate). | Table 1, Section 4.2, Paper: PDF p. 4–5. |
| **Input ablation (Table 2)** | DAPI morphology and transcript density provide complementary, non-redundant signals beyond candidate mask geometry. | Four configurations: (i) candidate-copy baseline (no model), (ii) MARC with $F_k$ only, (iii) MARC with $F_k+D$, (iv) MARC with $F_k+D+T$; all trained/evaluated identically against same $C^{(-k)}$ targets. | Adding $D$: Dice ↑ 0.8565→0.8866, ρ ↑ 0.4228→0.7564; adding $T$: Dice ↑ 0.8866→0.9002, ρ ↑ 0.7564→0.7905 [Table 2, Paper: PDF p. 6]. | Morphology is primary driver for cell-level ranking; transcript density refines both pixel-level prediction and ranking. | DAPI or T alone suffices for robust QC (not tested; ablation is cumulative). | Table 2, Section 4.3, Paper: PDF p. 6. |
| **Target ablation (Section 4.3)** | Arithmetic mean consensus is a viable and pragmatically preferable supervision target over STAPLE. | Two MARC models: (i) mean-consensus supervision, (ii) STAPLE-fused supervision; identical inputs/architecture/loss; evaluated against respective targets. | Mean: higher sensitivity (0.9168 vs 0.8860) and ρ (0.7905 vs 0.7491); STAPLE: higher precision (0.9128 vs 0.8843); Dice/IoU nearly identical [Paper: PDF p. 5]. | Mean consensus directly encodes fraction-of-supporting-methods and better preserves cell rankings. | STAPLE is *less accurate* (comparison is cross-target; no shared ground truth). | Section 4.3, Paper: PDF p. 5. |
| **Qualitative analysis (Figure 4)** | MARC predictions localize weakly supported regions and reflect biological plausibility. | Visual inspection of representative cells across all 4 methods; overlay of DAPI, $T$, $F_k$, $\hat{C}_k$, and cell-level map. | High $\hat{C}_k$ where $F_k$ aligns with nuclear morphology and transcript density; low $\hat{C}_k$ where $F_k$ extends into background or disagrees with $D/T$ [Figure 4, Paper: PDF p. 6]. | MARC learns biologically meaningful cues, not just statistical artifacts. | MARC generalizes to unseen tissue types or platforms (only Xenium data used). | Figure 4, Section 4.4, Paper: PDF p. 6–7. |

## 11 对结论的正确理解  
- MARC **does not predict ground-truth cell boundaries**, nor does it improve segmentation masks; it predicts *how much multi-method consensus supports a given candidate mask* [Paper: PDF p. 1, 5].  
- The reported Dice=0.9002 measures overlap between $\hat{C}_k$ and $C^{(-k)}$, **not** between $\hat{C}_k$ and true biology — $C^{(-k)}$ is itself an imperfect surrogate [Paper: PDF p. 1, 7].  
- Cell-level Spearman ρ=0.7905 means MARC preserves the *relative ranking* of cells by consensus support, enabling prioritization for review, **not** that absolute scores are calibrated probabilities [Paper: PDF p. 4–5].  
- Success on Xenium renal cell carcinoma **does not imply generalizability** to other tissues, assays (e.g., Slide-seq, seqFISH+), or segmentation methods outside the tested quartet [Paper: PDF p. 7].  
- MARC’s value lies in **computational efficiency**: replacing O(K) pipeline executions with O(1) inference, enabling routine QC at scale [Paper: PDF p. 1–2].

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| **Consensus as surrogate, not ground truth** | Failure modes common to all K segmentation methods may be reinforced in $C^{(-k)}$ and thus learned by MARC [Paper: PDF p. 7]. | Acknowledge utility despite limitation: consensus captures agreement across methods, reducing reliance on single-method bias [Paper: PDF p. 7]. | Section 4.5, Paper: PDF p. 7. |
| **Limited generalizability** | Evaluation conducted on single dataset (Xenium renal cell carcinoma) with candidate methods sharing inputs from same assay → methods not fully independent [Paper: PDF p. 7]. | Future work: evaluate on additional tissues/platforms/methods; incorporate orthogonal markers (e.g., membrane proteins) for validation; test consensus-guided filtering on downstream analyses [Paper: PDF p. 7]. | Section 4.5, Paper: PDF p. 7. |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| MARC uses arithmetic mean $C^{(-k)}$ as target, but methods differ in reliability (e.g., Xenium onboard vs. ProSeg); mean treats all equally, potentially propagating errors from weaker methods. | STAPLE (tested ablatively) estimates method-specific sensitivity/specificity, which could yield more robust targets if validated on independent ground truth. | Over-reliance on mean may degrade MARC’s ability to flag cells where *all* methods fail similarly (systematic bias), not just where they disagree. | Train MARC with STAPLE targets on a small subset with expert annotations; compare error localization accuracy (e.g., distance to expert boundary) vs. mean targets. | Section 4.3 notes STAPLE achieved higher precision but lower ρ; no test against expert truth [Paper: PDF p. 5]. |
| Input ablation shows DAPI contributes most to cell-level ranking (ρ jump 0.42→0.76), yet MARC treats $D$ and $T$ as raw intensity images — no explicit modeling of nuclear shape, size, or transcript spatial clustering. | Learned features may capture coarse correlations but miss fine-grained biophysical constraints (e.g., nucleus-to-cytoplasm ratio, transcript dispersion entropy). | Limits interpretability and transfer to tissues with divergent nuclear morphology or transcript distributions. | Replace $D$ and $T$ with handcrafted features (e.g., Hu moments, Ripley’s K) or graph-based representations (e.g., nucleus-cell graphs) and measure ρ drop. | Figure 4 shows alignment with nuclear morphology, but no feature attribution is provided [Paper: PDF p. 6–7]. |
| MARC aggregates $\hat{C}_k$ via simple mean over $M_k$ pixels (Eq. 8), but cell boundary uncertainty is often non-uniform (e.g., high near nuclei, low at periphery). | Uniform averaging may dilute localized low-consensus signals (e.g., a thin protrusion with low $\hat{C}_k$) if majority of cell has high support. | Compromises utility for detecting partial boundary errors, which are critical in SST for transcript misassignment. | Compare Eq. 8 aggregation to alternatives: max-pooling (sensitive to worst pixel), weighted mean (by distance to centroid), or attention-based pooling; evaluate on synthetic boundary perturbations. | No ablation on aggregation strategy is reported; Figure 4 shows spatially varying $\hat{C}_k$ but cell scores are scalars [Paper: PDF p. 5–6]. |

## 14 学到的知识  
- In subcellular ST, **cell segmentation quality control is decoupled from segmentation generation**: one can build a dedicated QC model (MARC) that consumes segmentation outputs as inputs, enabling modular, pipeline-agnostic evaluation.  
- **Consensus is learnable**: multi-method agreement, though computationally expensive to compute explicitly, exhibits sufficient structure to be regressed from multimodal inputs ($D,T,F_k$) with high fidelity.  
- **Foreground-union loss design is critical**: restricting supervision to $U_k$ (Eq. 6) forces the model to attend to disagreement regions — a simple full-image L1 would fail to localize uncertainty.  
- **Morphology dominates molecular context for ranking**: DAPI addition drove larger ρ gain (0.42→0.76) than transcript addition (0.76→0.79), suggesting nuclear architecture is the primary anchor for consensus in this dataset.  
- **Cell-level scores require spatially resolved prediction**: the candidate-copy baseline fails at ranking because it lacks intra-cell variation; MARC’s dense $\hat{C}_k$ enables meaningful aggregation.

## 15 与既有知识的连接  
- **single-cell foundation models**: MARC is *not* a foundation model — it’s task-specific and requires retraining per assay; however, its use of multimodal inputs ($D,T,F_k$) aligns with trends in cross-modal foundation learning, suggesting future extension to pretrain on diverse SST data.  
- **spatial transcriptomics**: Directly addresses the core SST challenge of boundary ambiguity [Paper: PDF p. 1]; complements segmentation methods (BIDCell, ProSeg) by providing their QC layer.  
- **graph neural networks**: While MARC uses CNNs, its goal — aggregating local evidence (transcripts, nuclei) into global cell scores — mirrors GNN message passing; future work could replace U-Net with GNNs operating on nucleus-graphs.  
- **multi-omics**: Treats morphology ($D$) and transcriptomics ($T$) as complementary omics layers; ablation confirms their synergy, supporting multi-omics integration paradigms.  
- **biomedical AI**: Exemplifies “pragmatic AI” — bypassing unattainable ground truth (expert boundaries) with a scalable surrogate (consensus), a pattern seen in medical imaging QC (e.g., STAPLE for segmentation validation).  
- **perturbation prediction / cell state representation / cross-modal alignment**: Weak connection/Methodology connection — MARC does not model perturbations, infer cell states, or perform cross-modal alignment; its alignment is purely spatial (co-registration of $D,T,F_k$), not semantic.

## 16 研究想法  

- **name**: Consensus-Guided Perturbation Masking  
  **originating limitation/observation**: MARC identifies low-consensus cells (Figure 4), but these may represent genuine biological heterogeneity (e.g., stressed cells) rather than segmentation errors [Paper: PDF p. 6–7].  
  **core hypothesis**: Low-consensus regions flagged by MARC correlate with transcriptionally dysregulated or perturbed cellular subpopulations.  
  **delta from paper**: Shift from QC to biological discovery: use MARC scores as masks to extract low-consensus cells for differential expression or trajectory inference.  
  **initial method**: Apply MARC to Xenium dataset; bin cells by $S_{k,c}$; perform DEG analysis between top/bottom deciles; validate with known stress markers.  
  **validation**: Enrichment of stress-response GO terms in low-$S_{k,c}$ cells; spatial clustering of low-consensus cells near tumor necrosis.  
  **failure modes**: Low consensus driven by technical artifacts (e.g., low RNA capture) rather than biology; confounding by cell type (some types inherently harder to segment).  
  **innovation status**: unverified  

- **name**: MARC-GNN: Graph-Augmented Consensus Regression  
  **originating limitation/observation**: MARC uses pixel-grid CNNs, but SST data has natural graph structure (nuclei as nodes, spatial proximity as edges) [Paper: PDF p. 3].  
  **core hypothesis**: Modeling inter-nuclear relationships via GNNs improves consensus prediction in crowded regions where pixel CNNs lose long-range context.  
  **delta from paper**: Replace U-Net encoder with GNN that takes nucleus centroids (from $D$) and per-nucleus transcript counts (from $T$) as node features, and builds k-NN graph.  
  **initial method**: Extract nuclei from $D$; compute node features (area, eccentricity, avg $T$ intensity); build graph; train GNN to predict per-nucleus consensus score; upsample to pixel level.  
  **validation**: Higher Dice in dense regions (defined by nucleus density >95th percentile) vs. U-Net MARC; ablation of graph connectivity.  
  **failure modes**: Nucleus detection errors propagate; graph construction sensitive to k; increased computational cost negates MARC’s efficiency advantage.  
  **innovation status**: unverified  

- **name**: Cross-Assay MARC Transfer  
  **originating limitation/observation**: MARC evaluated only on Xenium; authors note limited generalizability due to shared assay inputs [Paper: PDF p. 7].  
  **core hypothesis**: Pretraining MARC on diverse SST assays (Xenium, Visium, seqFISH+) enables zero-shot or few-shot adaptation to new platforms.  
  **delta from paper**: Introduce assay-conditioning token or adapter layers; pretrain on multi-assay consensus targets; fine-tune on target assay with minimal data.  
  **initial method**: Collect $D,T,F_k$ triples from 3+ public SST datasets; train MARC with assay ID embedding; evaluate on held-out assay with <100 tiles.  
  **validation**: Dice >0.85 on target assay with 50 fine-tuning tiles; feature similarity (CKA) between assay-specific encoder layers.  
  **failure modes**: Domain gap too large (e.g., Visium’s low resolution vs. Xenium’s subcellular); lack of standardized $D/T$ preprocessing across assays.  
  **innovation status**: unverified