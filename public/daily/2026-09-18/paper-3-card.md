> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: resource  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-12 | [Paper meta] |
| Authors | Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim | [Paper] [Paper: PDF p. 1] |
| Core task | Pixel-level consensus-support regression for SST cell segmentation quality estimation | [Paper] [Paper: PDF p. 1–2, Fig 1b] |
| Input modalities | Candidate mask $F_k$, DAPI morphology $D$, transcript-density map $T$ | [Eq. 2, Paper: PDF p. 3] |
| Output | Dense consensus-support map $\hat{C}_k \in [0,1]^{H\times W}$ → cell-level score $S_{k,c}$ | [Eq. 3, Eq. 8, Paper: PDF p. 3, 5] |
| Training supervision | Leave-one-method-out mean consensus $C^{(-k)}$ (pseudo-target) | [Eq. 5, Paper: PDF p. 3] |
| Loss function | Foreground-Union Consensus Loss (FUCL) | [Eq. 7, Paper: PDF p. 4] |
| Evaluation dataset | Xenium FFPE human renal cell carcinoma (spatially held-out tiles) | [Paper] [Paper: PDF p. 5] |
| Candidate methods | Cellpose-SAM, BIDCell, ProSeg, Xenium 10x onboard | [Paper] [Paper: PDF p. 5, Table 1] |
| Key metrics | Pixel-level Dice ↑ / L1 ↓; Cell-level Spearman ρ ↑ | [Table 1, Paper: PDF p. 4] |
| Code/data availability | Not reported in text; “未开源代码” noted in selection reason | [Selection reason] |

## 02 一句话总结  
该论文提出 MARC（Morphology-Aware Regression of Consensus），一个无需多方法集成推理即可预测亚细胞空间转录组（SST）中候选细胞分割掩码的跨方法共识支持度的回归框架。它通过将候选掩码、DAPI形态与转录密度三通道融合输入 U-Net 架构，以 leave-one-method-out 平均共识为伪标签、Foreground-Union Consensus Loss（FUCL）为监督目标进行训练，在 Xenium 肾癌数据上实现了像素级 Dice 0.90 和细胞级 Spearman 相关性 0.79，显著优于仅用候选掩码或单模态输入的基线。其核心价值在于将原本计算密集的显式共识构建（需运行全部4种分割流程）压缩为单次前向推理，为大规模 SST 分析提供了可扩展的质量控制范式；但该共识仍是代理指标（surrogate），不等价于生物学真值边界。

## 03 研究问题  
SST 细胞分割质量评估缺乏可靠 ground truth：手动标注成本过高且边界本身存在生物学模糊性 [Paper] [Paper: PDF p. 1]；而现有监督/不确定性方法依赖专家标注或模型内部状态，无法泛化至外部生成的异构候选掩码 [Paper] [Paper: PDF p. 1–2]。因此，如何在**无真值、无模型访问权限、跨方法异构输入**条件下，对任意 SST 分割结果进行**高效、一致、空间可解释的质量量化**？论文将此问题重构为：能否从单一候选掩码及其配套形态与分子信号中，直接回归出该掩码在多方法共识空间中的像素级支持强度？

## 04 研究背景与发展路径  
传统图像分割质量评估依赖人工标注（如 SegQC [19]）或模型内不确定性估计（如 Bayesian dropout [7,12]），但二者均不适用于 SST 场景：前者因细胞密度过高、标注主观性强而不可扩展 [Paper] [Paper: PDF p. 1–2]；后者要求访问生成该掩码的原始模型参数与推理路径，而实际中用户常仅持有黑盒输出掩码 [Paper] [Paper: PDF p. 2]。共识方法（如 STAPLE [21]、多数投票）虽能规避真值依赖，却需完整执行所有参与方法的 pipeline（含各自 SST 输入预处理），导致计算开销随方法数线性增长，难以用于千级 tile 的常规质控 [Paper] [Paper: PDF p. 2, Fig 1a]。MARC 的发展路径是：**放弃“运行共识” → 转向“学习共识”**：将共识视为可建模的隐变量，利用 leave-one-method-out 伪标签将其蒸馏为一个轻量回归任务，使共识能力内化于单模型中。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **No scalable ground truth** | Manual annotation is prohibitively time-consuming for large SST datasets; boundaries are biologically ambiguous even for experts | SST boundaries must be inferred from incomplete morphological and transcript signals; dense packing and weak contrast exacerbate ambiguity | [Paper] [Paper: PDF p. 1, "However, reliable ground-truth boundaries are unavailable..."] |
| **Incompatibility of existing QC methods** | Supervised QC requires expert masks; uncertainty-based QC requires internal model access | Existing approaches were not developed specifically for SST; they assume either full annotation access or white-box model deployment | [Paper] [Paper: PDF p. 1–2, "Conventional segmentation quality-assessment approaches were not developed specifically for SST..."] |
| **Computational bottleneck of explicit consensus** | Multi-method consensus construction is computationally intensive and difficult to scale | Requires configuring and running all contributing pipelines with their method-specific SST inputs (e.g., different preprocessing, alignment) | [Paper] [Paper: PDF p. 2, Fig 1a caption; "making consensus construction computationally intensive"] |
| **Lack of spatially resolved, cross-method quality signal** | Candidate masks lack per-pixel reliability estimates; cell-level scores cannot prioritize ambiguous regions for review | Prior work focuses on generating better masks, not evaluating externally generated candidates; no framework produces dense consensus-support maps usable for spatial filtering | [Paper] [Paper: PDF p. 2, "Most existing work focuses on generating improved masks rather than evaluating the reliability of an externally generated candidate mask."] |

## 06 核心思想  
论文的核心洞察是：**共识不是必须被“计算”的结果，而是可以被“感知”的上下文模式**。当多个互补的 SST 分割方法（如 morphology-driven Cellpose-SAM 与 transcript-aware ProSeg）对同一组织区域产生分歧时，其分歧模式本身携带了关于局部信号质量（如核形态清晰度、转录富集强度、邻近细胞重叠程度）的强判别信息。MARC 的核心思想即：将候选掩码 $F_k$ 视为查询（query），将 DAPI 形态 $D$ 与转录密度 $T$ 视为支撑证据（evidence），联合建模三者之间的几何-分子一致性关系，从而在像素级预测该候选区域获得其余 $K-1$ 种方法共同支持的概率。这本质上是将共识建模为一种**跨模态、跨方法的条件置信度场**，而非离散的二值集成输出。

## 07 方法总览  
MARC 将 SST 分割质量评估解耦为两个阶段：**（1）像素级共识支持回归**：以三通道输入 $X_k = \text{concat}(D, T, F_k)$ 经 U-Net 编码-解码，输出连续值 $\hat{C}_k \in [0,1]^{H\times W}$，表示每个像素属于跨方法共识前景的概率；**（2）细胞级分数聚合**：利用原始标签掩码 $M_k$ 对 $\hat{C}_k$ 进行实例平均，得到每个候选细胞 $c$ 的标量支持分 $S_{k,c}$。训练目标为 Foreground-Union Consensus Loss（FUCL），仅在候选前景 $F_k$ 或 leave-one-method-out 共识前景 $C^{(-k)}$ 覆盖的并集区域 $U_k$ 内计算 L1 误差，强制模型聚焦于最具判别力的争议区域（如候选延伸至背景、或遗漏真实核区）。整个流程完全避免在推理时调用其他分割方法，实现 O(1) 推理复杂度。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|------------------------|-----------------------------------|
| **Three-channel input fusion** | Concatenates DAPI morphology $D$, transcript density $T$, and candidate foreground $F_k$ into $X_k \in \mathbb{R}^{3\times H\times W}$ | Enables joint modeling of geometric, structural, and molecular cues; avoids modality silos that would miss cross-signal inconsistencies | Input: $D, T, F_k$ (all $H\times W$); Output: $X_k$ | [Eq. 2, Paper: PDF p. 3]; Ablation in Table 2 shows +DAPI/+transcripts boost Dice & ρ | Removal reduces Dice by ~4.4% (mask-only→mask+DAPI) and ρ by ~0.33 (mask-only→mask+DAPI), proving morphology is critical for ranking [Paper] [Paper: PDF p. 6, Table 2] |
| **U-Net encoder-decoder backbone** | Extracts hierarchical features and regresses dense $\hat{C}_k$ via skip connections | Captures multi-scale context (e.g., nuclear shape at high-res, tissue architecture at low-res); skip connections preserve boundary detail crucial for pixel-level support | Input: $X_k$; Output: logit map $Z_k$ → $\hat{C}_k = \sigma(Z_k)$ | [Sec 3.2, Paper: PDF p. 3]; Fig 2 shows architecture | Without skip connections, boundary localization degrades → lower Dice/IoU; FUCL’s foreground focus would under-constrain such a model |
| **Foreground-Union Consensus Loss (FUCL)** | Computes L1 loss only over union $U_k = F_k \cup C^{(-k)}$ of candidate and consensus foreground | Focuses gradient updates on regions where candidate and consensus disagree (i.e., ambiguous boundaries), preventing background noise from dominating training | Input: $\hat{C}_k, C^{(-k)}, U_k$; Output: scalar loss $L^{(k)}_{\text{FU}}$ | [Eq. 6–7, Paper: PDF p. 4]; Defined as mean absolute error clamped to $U_k$ | Using full-image L1 would dilute gradients on critical disagreement pixels → lower Dice & poorer cell-level correlation (as implied by FUCL’s design rationale [Paper] [Paper: PDF p. 4]) |
| **Cell-level aggregation (Eq. 8)** | Averages $\hat{C}_k$ over pixels assigned to each instance $c$ in $M_k$: $S_{k,c} = \frac{1}{\|M_k=c\|}\sum_{(x,y):M_k(x,y)=c} \hat{C}_k(x,y)$ | Converts dense spatial support into actionable, instance-level QC scores for manual review or downstream filtering | Input: $\hat{C}_k, M_k$; Output: vector $\{S_{k,c}\}$ | [Eq. 8, Paper: PDF p. 5]; Used for Spearman ρ calculation and Fig 3/4 visualization | Without aggregation, no cell-level ranking possible; candidate-copy baseline has constant $S_{k,c}$ → undefined ρ [Table 2, *] |

## 09 关键公式与符号  
论文未给出显式“算法公式”，但明确定义了以下关键符号与可核验公式：  
- $M_k$: 候选方法 $k$ 输出的带标签掩码（$H\times W$ 整数矩阵），$M_k(x,y)=c$ 表示像素 $(x,y)$ 属于细胞实例 $c$ [Eq. 1, Paper: PDF p. 3]。  
- $F_k$: $M_k$ 的二值前景图，$F_k(x,y)=1$ iff $M_k(x,y)>0$ [Eq. 1]。  
- $D, T$: 对齐的 DAPI 形态图与转录密度图（均为 $H\times W$ 实值图）[Paper] [Paper: PDF p. 3]。  
- $X_k = \text{concat}(D, T, F_k)$: 三通道模型输入 [Eq. 2]。  
- $\hat{C}_k = f_\theta(X_k) = \sigma(Z_k)$: 模型输出的连续共识支持图，经 sigmoid 映射至 $[0,1]$ [Eq. 3–4]。  
- $C^{(-k)} = \frac{1}{K-1}\sum_{j\neq k} F_j$: leave-one-method-out 共识伪目标（$K=4$，故为其余3法平均）[Eq. 5]。  
- $U_k(x,y) = \mathbb{I}[F_k(x,y)=1 \lor C^{(-k)}(x,y)>0]$: 前景并集掩码，定义 FUCL 作用域 [Eq. 6]。  
- $L^{(k)}_{\text{FU}} = \frac{1}{\|U_k\|_1}\sum_{x,y} U_k(x,y)\cdot|\hat{C}_k(x,y)-C^{(-k)}(x,y)|$: Foreground-Union Consensus Loss [Eq. 7]。  
- $S_{k,c} = \frac{1}{|\{(x,y):M_k(x,y)=c\}|}\sum_{(x,y):M_k(x,y)=c} \hat{C}_k(x,y)$: 细胞 $c$ 的共识支持分 [Eq. 8]。  
*Note*: 无公式 (7) 在文本中缺失（跳过编号7），但 FUCL 定义完整见 Eq. 7；Equation 8 是唯一明确写出的聚合公式。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|----------------------------------|--------|
| **Main evaluation (Table 1)** | MARC predicts explicit consensus targets ($C^{(-k)}$) with high fidelity | MARC vs. explicit $C^{(-k)}$ across 4 candidate methods; metrics: L1, Dice, IoU, Sensitivity, Precision, Cell Spearman ρ | Avg. Dice=0.9002, Avg. ρ=0.7905; best per-metric bolded | MARC closely approximates explicit cross-method consensus at both pixel and cell levels | MARC recovers biological ground truth (not claimed; authors explicitly state consensus is a surrogate [Paper] [Paper: PDF p. 7]) | [Table 1, Paper: PDF p. 4]; [Paper] [Paper: PDF p. 5, "MARC achieved mean...indicating that MARC closely reproduces the explicit consensus"] |
| **Input ablation (Table 2)** | DAPI morphology and transcript density provide complementary, non-redundant signals beyond candidate geometry | MARC variants: mask-only, mask+DAPI, mask+DAPI+transcripts; all trained/tested on same $C^{(-k)}$ targets | Adding DAPI boosts avg. Dice from 0.8565→0.8866 and ρ from 0.4228→0.7564; adding transcripts further to 0.9002/0.7905 | Morphology is the primary driver for cell-level ranking; transcripts add molecular specificity for pixel-level refinement | DAPI alone suffices for high-quality ranking (false: ρ=0.7564 < 0.7905 with transcripts) | [Table 2, Paper: PDF p. 6]; [Paper] [Paper: PDF p. 6, "The substantial increase in cell-level correlation after adding DAPI indicates that morphology provides the main additional signal..."] |
| **Target ablation (Sec 4.3)** | Mean-consensus supervision is more effective than STAPLE for preserving cell-level rankings | Two MARC models: mean-$C^{(-k)}$ vs. STAPLE-$C^{(-k)}$ targets; identical inputs/architecture/loss | Mean target: higher sensitivity (0.9168 vs 0.8860) and ρ (0.7905 vs 0.7491); STAPLE: higher precision (0.9128 vs 0.8843) | Mean consensus better captures fraction-of-support intuition and preserves ordering; STAPLE trades recall for precision | STAPLE is objectively more accurate (not supported: models evaluated against different targets) | [Paper] [Paper: PDF p. 5–6, "Mean-consensus and STAPLE supervision produced similar average Dice scores...but different trade-offs"] |
| **Qualitative analysis (Fig 4)** | MARC localises weakly supported regions spatially | Visual inspection of predicted $\hat{C}_k$ and $S_{k,c}$ on held-out test tiles | Bright $\hat{C}_k$ aligns with nuclear morphology & transcript density; dim regions correspond to candidate extensions into background or method-specific artifacts | MARC produces spatially varying, interpretable support maps that highlight ambiguity for review | MARC’s low-score regions perfectly match biological ground truth errors (Not assessable from supplied material; no ground truth provided) | [Fig 4, Paper: PDF p. 6]; [Paper] [Paper: PDF p. 7, "Lower consensus was observed where candidate masks extended into the background..."] |

## 11 对结论的正确理解  
MARC 的核心结论是：**在 SST 场景下，跨方法共识支持度是一个可被 U-Net 从候选掩码+形态+转录三元组中有效回归的稠密场，且该回归结果在像素重叠（Dice 0.90）和细胞排序（ρ 0.79）上高度逼近显式计算的 leave-one-method-out 共识**。这意味着：（1）共识蕴含的可靠性信号具有足够强的统计规律性，能被端到端模型捕获；（2）形态与分子上下文是解码该信号的关键，远超候选掩码自身几何信息；（3）FUCL 的前景并集约束是有效的训练偏置，引导模型关注歧义边界。但必须强调：该共识是**方法论共识（methodological agreement）**，非生物学共识（biological truth）；其价值在于提供一种**可扩展、可解释、与下游分析解耦的质量代理指标**，而非替代真值。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|---------------------------|----------------------------------------|--------|
| **Consensus as surrogate, not ground truth** | Failure modes common to multiple segmentation methods may be reinforced in the consensus target, leading to systematic bias | Acknowledge it's a pragmatic alternative to manual annotation; suggest orthogonal validation with membrane/protein markers | [Paper] [Paper: PDF p. 7, "A key limitation...failure modes across segmentation methods may be reinforced...incorporate orthogonal membrane or protein markers for validation"] |
| **Limited generalisability** | Evaluated only on Xenium renal cell carcinoma data; candidate methods share inputs from same assay, reducing independence | Future work will evaluate on additional tissues, platforms, and segmentation methods | [Paper] [Paper: PDF p. 7, "Another limitation is that the MARC was evaluated on a single Xenium renal cell carcinoma dataset...evaluate additional tissues, platforms, and segmentation methods"] |
| **Platform/method dependence** | Current setup assumes aligned DAPI and transcript maps; performance may degrade with poor registration or noisy transcript data | Not explicitly stated, but implied by reliance on "aligned" inputs in Methods [Sec 3.1] and ablation showing transcript density improves performance | [Paper] [Paper: PDF p. 3, "Let D ∈ R^{H×W} denote the aligned DAPI morphology image and T ∈ R^{H×W} the transcript-density image."; Table 2 shows transcript addition improves metrics] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|--------|
| MARC’s high cell-level Spearman ρ (0.79) relies on the *same* leave-one-method-out protocol for both training targets ($C^{(-k)}$) and evaluation reference ($C^{(-k)}$) | This creates an optimistic bias: the model is optimized to mimic a target defined by the very ensemble it’s meant to replace; real-world utility requires generalisation to unseen method combinations or new assays | Overstates practical deployability; if a new segmentation method is added, retraining MARC with updated $C^{(-k)}$ may be needed, reintroducing computational cost | Train MARC on subset of methods (e.g., 3 out of 4), then test its prediction against consensus including the held-out method; measure ρ drop | [Paper] [Paper: PDF p. 3, "For candidate method k, the consensus target is calculated as the mean binary foreground prediction of the remaining K−1 methods"; Table 1 evaluates exactly this same setup] |
| FUCL restricts loss to foreground union $U_k$, but $C^{(-k)}$ is a soft probability map (mean of binaries), while $\hat{C}_k$ is a sigmoid output — the L1 loss treats them as equally calibrated continuous values | The soft target $C^{(-k)} \in [0,1]$ represents fractional support, but FUCL’s L1 assumes linear correspondence; a KL divergence or focal loss might better handle the confidence calibration mismatch | Poor calibration could harm downstream tasks like active learning where absolute $\hat{C}_k$ thresholds matter (e.g., filtering cells with $\hat{C}_k<0.3$) | Compare FUCL with KL-divergence loss on same setup; calibrate $\hat{C}_k$ using isotonic regression against $C^{(-k)}$; report ECE (Expected Calibration Error) | [Eq. 5 defines $C^{(-k)}$ as arithmetic mean; Eq. 4 defines $\hat{C}_k$ as sigmoid; FUCL uses L1 without calibration discussion] |
| Input ablation shows transcript density boosts performance, but Table 2 reports lower ρ for BIDCell (0.6251) vs others (>0.81) despite using same transcript input | BIDCell itself is transcript-aware [Paper] [Paper: PDF p. 3], so its candidate mask $F_k$ may already encode transcript information, making the additional transcript channel $T$ redundant or even conflicting for this method | Suggests MARC’s modality fusion isn’t universally optimal; method-specific input gating or attention might improve robustness across heterogeneous candidates | Implement modality-gating modules per candidate method; ablate $T$ only for BIDCell input and compare to full model | [Paper] [Paper: PDF p. 3, "BIDCell uses biologically informed self-supervised learning to integrate morphological and transcript information"; Table 2 shows BIDCell row has lowest ρ=0.6251] |

## 14 学到的知识  
- **共识可学习性**：跨方法分割共识并非必须显式计算的刚性集成，而是一种可被深度网络从多模态上下文中回归的稠密语义场，其可学习性源于方法间错误的互补性（morphology vs. transcript errors）。  
- **FUCL 的设计智慧**：聚焦前景并集的损失函数是处理“弱监督代理目标”的关键——它将优化目标锚定在最具信息量的歧义区域（candidate-background boundary, candidate-overlap zone），避免背景噪声稀释梯度。  
- **形态的不可替代性**：在 SST 中，DAPI 形态对细胞级质量排序的贡献（Δρ≈0.33）远超转录密度（Δρ≈0.03），证实核结构仍是细胞身份与边界的最稳健先验，分子信号起校准与细化作用。  
- **伪标签的脆弱性**：leave-one-method-out 协议虽巧妙规避真值需求，但其有效性高度依赖候选方法的独立性；当方法共享底层假设（如均基于 Xenium 数据）时，共识可能收敛至局部最优而非全局可靠解。  
- **空间可解释性即生产力**：dense $\hat{C}_k$ 图不仅用于打分，其像素级热图可直接指导人工校正（如 Fig 4 中红框细胞的低支持区域），将 QC 从“整体可信度判断”升级为“精准干预定位”。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：MARC 的 leave-one-method-out 伪标签范式与 self-training、noisy student 等半监督方法同源，但创新点在于将“student”目标定义为跨方法共识而非单模型自洽；FUCL 的前景聚焦策略与医学图像分割中常用的 foreground-weighted Dice loss [18] 一脉相承，但更进一步限定于“candidate ∪ consensus”交集。  
- **候选连接/方法论连接**：其三通道输入（mask+DAPI+transcripts）与 multi-omics 表征学习中常见的模态拼接（如 scRNA+ATAC）思路一致，但 SST 的 spatial alignment 约束使其更接近 spatial omics 特定架构（如 SPATA [16]）；U-Net 结构选择印证了 biomedical AI 中编码器-解码器对空间关系建模的普适优势。  
- **候选连接/方法论连接**：cell-level aggregation (Eq. 8) 本质是 instance-aware pooling，与 graph neural networks 中的 readout 函数（如 sum/mean pooling over node features）功能相似，暗示可将候选细胞视为图节点，$\hat{C}_k$ 像素为邻居特征，探索 GNN-based consensus refinement。  
- **弱连接/方法论连接**：single-cell foundation models 通常面向 profile-level embedding，而 MARC 聚焦 segmentation-level spatial QC；但其输出 $\hat{C}_k$ 可作为细胞表型的 spatial reliability prior，注入 foundation model 的 spatial tokenization 阶段。  
- **弱连接/方法论连接**：perturbation prediction 在 SST 中常需 clean segmentation；MARC 提供的低共识细胞列表可作为 perturbation target 的 quality filter，避免在模糊边界上建模虚假扰动效应。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Consensus-Guided Active Learning for SST Annotation  
  **originating limitation/observation**: Authors note consensus is a surrogate and manual annotation is expensive [Paper] [Paper: PDF p. 1,7]; MARC identifies low-consensus cells (Fig 4) but doesn’t leverage them for annotation efficiency.  
  **core hypothesis**: Querying human annotators *only* on cells with MARC-predicted low consensus ($S_{k,c}<\tau$) yields higher annotation ROI than random or uncertainty-based sampling.  
  **delta from paper**: MARC is passive QC; this integrates it into an active loop where low-consensus predictions directly drive annotation budget allocation.  
  **initial method**: On Xenium data, simulate annotation budget B; compare: (a) random cell selection, (b) top-B cells by MARC’s $1-S_{k,c}$, (c) top-B by model uncertainty (if available). Measure annotation time saved & downstream task (e.g., cell-type clustering) accuracy gain.  
  **validation**: Annotation time per cell (expert timing), clustering ARI before/after adding B annotations.  
  **failure modes**: If low-consensus cells are systematically un-annotatable (e.g., due to imaging artifacts), ROI drops; if consensus correlates poorly with true difficulty, sampling is inefficient.  
  **innovation status**: unverified  

- **name**: Cross-Platform Consensus Distillation  
  **originating limitation/observation**: Authors admit limited generalisability to other platforms [Paper] [Paper: PDF p. 7]; MARC trained on Xenium may fail on Visium/Slide-seq due to resolution/signal differences.  
  **core hypothesis**: A small set of platform-aligned consensus targets (e.g., 100 tiles from Visium) can distill Xenium-trained MARC’s consensus knowledge to new platforms via feature-level adaptation, avoiding full retraining.  
  **delta from paper**: MARC is platform-specific; this proposes a lightweight transfer strategy leveraging its learned consensus representation.  
  **initial method**: Freeze MARC encoder; add platform-specific adapter (e.g., small CNN) before decoder; train adapter + decoder head on Visium consensus targets using FUCL; compare to full Visium retraining.  
  **validation**: Dice/ρ on Visium test set; parameter count/flops of adapter vs. full model.  
  **failure modes**: If platform shifts break fundamental morphology-transcript relationships (e.g., Visium’s spot-level vs Xenium’s subcellular resolution), adapter fails; if no Visium consensus targets exist, distillation impossible.  
  **innovation status**: unverified  

- **name**: Graph-Augmented Consensus Refinement  
  **originating limitation/observation**: MARC treats each candidate cell in isolation (Eq. 8); but SST cell boundaries are relational—consensus for cell c depends on neighbors’ morphology/transcript overlap [Paper] [Paper: PDF p. 1].  
  **core hypothesis**: Modeling candidate cells as nodes in a spatial graph (edges = proximity/overlap) and passing $\hat{C}_k$ messages enables contextual refinement of consensus scores, especially for touching cells.  
  **delta from paper**: MARC is CNN-based and local; this injects explicit relational reasoning via GNN.  
  **initial method**: Replace Eq. 8 aggregation with GNN readout: node features = $\{\text{mean}(\hat{C}_k \text{ on } c), \text{area}_c, \text{DAPI\_intensity}_c\}$; edges = spatial distance < r; output refined $S'_{k,c}$. Train end-to-end with FUCL.  
  **validation**: Dice/ρ on test set; visual inspection of touching cell pairs in Fig 4—do refined scores better separate merged instances?  
  **failure modes**: Graph construction sensitive to distance threshold r; if cell instances are highly irregular, fixed-radius graphs misrepresent topology; adds inference latency.  
  **innovation status**: unverified