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
| Title | MARC: Morphology-Aware Regression of Consensus for Cell Segmentation in Subcellular Spatial Transcriptomics | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-12 | [Paper meta] |
| Authors | Xinyu Shu, Andrew Zhang, Jean Yang, Jinman Kim | [Paper] [Paper: PDF p. 1] |
| Core task | Pixel-level consensus-support regression for SST segmentation quality estimation | [Paper] [Paper: PDF p. 1–3] |
| Input modalities | Candidate mask $F_k$, DAPI morphology $D$, transcript-density map $T$ | [Eq. 2, Paper: PDF p. 3] |
| Output | Dense consensus-support map $\hat{C}_k \in [0,1]^{H\times W}$ → cell-level score $S_{k,c}$ | [Eq. 3, Eq. 8, Paper: PDF p. 3, 5] |
| Key loss | Foreground-Union Consensus Loss (FUCL) | [Sec 3.4, Eq. 7, Paper: PDF p. 4] |
| Supervision signal | Leave-one-method-out (LOMO) mean foreground consensus $C^{(-k)}$ | [Eq. 5, Paper: PDF p. 3] |
| Evaluation dataset | Xenium FFPE human renal cell carcinoma (4,642 held-out tiles) | [Paper] [Paper: PDF p. 5] |
| Candidate methods | Cellpose-SAM, BIDCell, ProSeg, Xenium 10x onboard | [Paper] [Paper: PDF p. 5] |
| Primary metrics | Foreground-union L1 ↓, Dice ↑, IoU ↑, cell-level Spearman ρ ↑ | [Table 1, Paper: PDF p. 4] |

## 02 一句话总结  
本文提出 MARC（Morphology-Aware Regression of Consensus），一个面向亚细胞空间转录组（SST）的轻量级质量评估框架，通过回归预测像素级多方法共识支持度，替代传统需运行全部分割流水线的显式共识构建；其核心价值在于：在无专家标注、不依赖特定分割模型内部结构的前提下，仅用单个候选掩码 + 对齐的 DAPI 形态图 + 转录密度图，即可逼近 leave-one-method-out 显式共识，支撑大规模 SST 数据的鲁棒性质检与低共识细胞筛选；但该共识仅为方法间一致性代理，非生物学真值，且当前验证局限于单一组织类型与平台。

## 03 研究问题  
SST 中细胞分割质量评估面临三重困境：① 缺乏可靠 ground truth（边界本身生物模糊，人工标注成本极高）[Paper] [Paper: PDF p. 1]；② 现有监督方法（如 SegQC）依赖专家修正掩码，不确定性方法（如 Bayesian）依赖生成模型内部输出，二者均无法泛化至外部候选掩码评估 [Paper] [Paper: PDF p. 3]；③ 显式多方法共识虽可作为实用代理，但需并行执行多个计算密集型 pipeline，难以扩展至全组织尺度 [Paper] [Paper: PDF p. 2]。因此，论文聚焦：**能否设计一个轻量、即插即用的模型，在推理时仅需单个候选掩码及基础模态输入，即可高保真地预测其在多方法共识中的像素/细胞级支持强度？** 这一问题直指 SST 分析链中“分割可信度量化”这一未被充分工程化的瓶颈环节。

## 04 研究背景与发展路径  
SST 分析始于细胞分割，而分割质量直接决定下游细胞级转录分配的可靠性 [Paper] [Paper: PDF p. 1]。早期通用分割模型（U-Net、Mask R-CNN、HoVer-Net）未针对 SST 的形态-转录双信号耦合特性优化 [Paper] [Paper: PDF p. 2]；后续 SST 专用方法（BIDCell、ProSeg、Baysor）虽融合多模态，但彼此假设与输入差异导致结果冲突，尤其在致密组织或弱信号区 [Paper] [Paper: PDF p. 2–3]。质量评估随之分化为两条路径：一是基于专家标注的监督范式（不可扩展），二是基于模型自身不确定性的内部估计（绑定生成模型）[Paper] [Paper: PDF p. 3]。共识方法（如 STAPLE、多数投票）曾被用于整合多源分割，但其计算开销阻碍了日常质检 [Paper] [Paper: PDF p. 3]。MARC 的发展路径是：**将共识从“需执行的计算过程”重构为“可学习的映射函数”**——以 LOMO 共识为伪标签，训练一个 U-Net 变体直接从候选掩码+形态+转录中回归共识支持度，从而解耦评估与生成。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| Lack of scalable ground truth | Manual annotation is prohibitively time-consuming for large SST datasets; boundaries are biologically ambiguous and cannot be reliably inferred from incomplete signals | SST boundaries are inherently ambiguous due to weak morphological contrast, sparse/displaced transcripts, and cell overlap [Paper] [Paper: PDF p. 1, 3] | “reliable ground-truth boundaries are unavailable because they must be inferred from incomplete morphological and transcript signals” [Paper] [Paper: PDF p. 1]; “cell boundaries may be biologically ambiguous” [Paper] [Paper: PDF p. 3] |
| Incompatibility of existing QC methods | Supervised QC requires expert masks; uncertainty-based QC requires access to the generating model’s internals — neither supports evaluation of externally produced candidate masks | Existing approaches were not developed specifically for SST and assume either expert annotations or internal model access [Paper] [Paper: PDF p. 3] | “these approaches do not readily support the evaluation of candidate masks produced by different SST segmentation pipelines when expert annotations are unavailable” [Paper] [Paper: PDF p. 2]; “SegQC relies on expert-corrected masks, whereas Bayesian uncertainty methods require access to the model that generated the segmentation” [Paper] [Paper: PDF p. 3] |
| Computational bottleneck of explicit consensus | Constructing cross-method consensus requires configuring and running all contributing pipelines with method-specific inputs, making it computationally intensive and difficult to scale | Explicit consensus averages outputs from multiple segmentation pipelines using method-specific SST inputs [Paper] [Paper: PDF p. 2] | “explicit consensus construction requires executing multiple computationally intensive pipelines” [Paper] [Paper: PDF p. 1]; “this process is computationally intensive and difficult to scale, limiting its use for routine quality control” [Paper] [Paper: PDF p. 2] |

## 06 核心思想  
论文的核心洞察是：**多方法共识并非必须“执行”，而可被“建模”为一种可泛化的上下文感知映射关系**。具体而言，作者观察到：共识支持强度并非仅由候选掩码几何形状决定，而是强烈依赖于其与局部 DAPI 核形态、转录分子密度的空间一致性 [Paper] [Paper: PDF p. 6]；同时，不同方法的错误模式具有互补性（形态驱动 vs 转录驱动），使得它们的交集/并集区域蕴含丰富质量信号 [Paper] [Paper: PDF p. 2]。因此，MARC 将共识预测建模为一个稠密回归任务：给定候选掩码 $F_k$、DAPI 图 $D$、转录图 $T$，学习函数 $f_\theta$ 输出连续支持度图 $\hat{C}_k$，其目标是逼近 leave-one-method-out 共识 $C^{(-k)}$。该思想将 QC 从“后处理计算”升维为“前馈感知建模”，实现了评估效率与泛化能力的统一。

## 07 方法总览  
MARC 是一个端到端的 U-Net 风格回归器，其方法流严格遵循“输入→特征融合→稠密回归→细胞聚合”四步：① **输入构造**：对每个候选方法 $k$，拼接三通道张量 $X_k = \text{concat}(D, T, F_k)$ [Eq. 2, Paper: PDF p. 3]；② **特征编码-解码**：四层级 U-Net 提取多尺度形态-转录-掩码联合表征，最终输出单通道 logits $Z_k$，经 sigmoid 得 $\hat{C}_k \in [0,1]^{H\times W}$ [Eq. 3–4, Paper: PDF p. 3]；③ **监督构建**：采用 leave-one-method-out 策略，对方法 $k$，其伪标签为其余 $K-1=3$ 个方法前景图的算术平均 $C^{(-k)}$ [Eq. 5, Paper: PDF p. 3]；④ **损失与聚合**：使用 Foreground-Union Consensus Loss (FUCL) 聚焦于候选与共识前景的并集区域进行 L1 回归 [Eq. 6–7, Paper: PDF p. 4]，再按原始标签图 $M_k$ 对 $\hat{C}_k$ 像素取均值得到细胞级分数 $S_{k,c}$ [Eq. 8, Paper: PDF p. 5]。整个流程在推理时完全摆脱多方法 ensemble，仅需单次前向传播。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-----------------------------------|
| Leave-one-method-out (LOMO) pseudo-target construction | Generates consensus pseudo-label $C^{(-k)}$ by averaging binary foreground maps of all *other* $K-1$ methods | Avoids trivial self-agreement supervision; enables training without ground truth while preserving multi-method agreement semantics | Input: Set of $K=4$ binary foreground masks $\{F_j\}_{j=1}^4$; Output: $C^{(-k)} \in [0,1]^{H\times W}$ [Eq. 5] | “Excluding the candidate method from its own target prevents the model from receiving trivial self-agreement as supervision” [Paper] [Paper: PDF p. 3]; Table 1 uses this exact target for evaluation | Removal would cause degenerate learning (e.g., model collapses to identity mapping on $F_k$); no ablation reported but logically necessary for problem framing |
| Foreground-Union Consensus Loss (FUCL) | Computes mean absolute error between $\hat{C}_k$ and $C^{(-k)}$ only over pixels in union $U_k = F_k \cup C^{(-k)}$ | Focuses training signal on biologically meaningful regions (foreground) and disagreement zones where consensus is most informative; avoids dilution by background zeros | Input: $\hat{C}_k$, $C^{(-k)}$, $U_k$; Output: scalar loss $L^{(k)}_{\text{FU}}$ [Eq. 7] | “restricting the loss to $U_k$ focuses learning on foreground and disagreement regions” [Paper] [Paper: PDF p. 4]; Figure 2 architecture diagram includes FUCL as core component | Without $U_k$ masking, loss would be dominated by background pixels, degrading foreground precision; Table 2 shows sensitivity/precision trade-offs under different targets, implying foreground weighting matters |
| Morphology-transcript-mask tri-channel fusion | Concatenates aligned DAPI morphology $D$, transcript density $T$, and candidate foreground $F_k$ into $X_k \in \mathbb{R}^{3\times H\times W}$ | Provides complementary contextual cues beyond mask geometry; DAPI informs nuclear integrity, transcripts inform molecular content, jointly disambiguating weak boundaries | Input: $D$, $T$, $F_k$; Output: $X_k$ [Eq. 2] | Ablation in Table 2 shows adding DAPI boosts cell-level Spearman from 0.4228 to 0.7564, and adding transcripts further to 0.7905; Figure 4 qualitatively shows predictions align with morphology/transcript hotspots | Removing $D$ or $T$ degrades both pixel-level (Dice) and cell-level (ρ) metrics significantly (Table 2), confirming their non-redundant contribution |
| Cell-level aggregation via label-map averaging | For each cell instance $c$ in labelled mask $M_k$, computes $S_{k,c} = \frac{1}{\|M_k=c\|}\sum_{(x,y):M_k(x,y)=c} \hat{C}_k(x,y)$ | Converts dense pixel support into interpretable, rankable cell-level QC scores for manual review or filtering | Input: $\hat{C}_k$, $M_k$; Output: scalar $S_{k,c}$ per cell [Eq. 8] | “These scores can be used to rank cells for manual review, filtering, or downstream quality-control analysis” [Paper] [Paper: PDF p. 5]; Figure 3 plots $S_{k,c}$ vs target, showing monotonic relationship | Without aggregation, output remains pixel-level and lacks direct utility for cell-centric downstream tasks (e.g., perturbation response analysis); baseline candidate-copy produces constant scores, proving aggregation is essential for ranking |

## 09 关键公式与符号  
论文未提供显式、独立的数学公式（如优化目标完整形式），但明确定义了以下关键符号与关系式：  
- $M_k$: 候选方法 $k$ 输出的带标签掩码（整数矩阵），$M_k(x,y)=c$ 表示像素 $(x,y)$ 属于细胞实例 $c$ [Paper] [Paper: PDF p. 3]；  
- $F_k$: $M_k$ 的二值前景图，$F_k(x,y) = \mathbb{I}(M_k(x,y)>0)$ [Eq. 1]；  
- $D, T$: 对齐的 DAPI 形态图像与转录密度图像（实值矩阵）[Paper] [Paper: PDF p. 3]；  
- $X_k = \text{concat}(D,T,F_k)$: 三通道输入张量 [Eq. 2]；  
- $\hat{C}_k = f_\theta(X_k) = \sigma(Z_k)$: MARC 输出的连续共识支持图，值域 $[0,1]$ [Eq. 3–4]；  
- $C^{(-k)} = \frac{1}{K-1}\sum_{j\neq k} F_j$: leave-one-method-out 共识伪标签（算术平均）[Eq. 5]；  
- $U_k = F_k \lor C^{(-k)}$: 前景并集掩码，用于 FUCL 区域约束 [Eq. 6]；  
- $S_{k,c} = \frac{1}{|\{(x,y):M_k(x,y)=c\}|}\sum_{(x,y):M_k(x,y)=c} \hat{C}_k(x,y)$: 细胞 $c$ 的共识支持得分 [Eq. 8]；  
- Metrics: Foreground-union L1 (↓), Dice (↑), IoU (↑), Sensitivity (↑), Precision (↑), Cell-level Spearman ρ (↑) [Table 1, Paper: PDF p. 4]。  
*No closed-form objective function is provided; training uses AdamW optimizer with FUCL loss.*

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|----------------------------------|--------|
| Main evaluation (Table 1) | MARC predicts explicit LOMO consensus with high fidelity at pixel and cell levels | MARC trained on 4 candidate methods (Cellpose-SAM, BIDCell, ProSeg, Xenium), evaluated on 4,642 held-out test tiles against $C^{(-k)}$ targets | Avg. Dice=0.9002, IoU=0.8186, cell ρ=0.7905; best per-method Dice up to 0.9127 (Xenium) | MARC closely approximates explicit cross-method consensus without multi-method inference | MARC achieves *biological ground truth* accuracy — paper explicitly states consensus is a surrogate, not ground truth [Paper] [Paper: PDF p. 7] | [Table 1, Paper: PDF p. 4]; [Paper] [Paper: PDF p. 5] |
| Input ablation (Table 2) | Morphology and transcript signals provide complementary information beyond candidate-mask geometry | Compared: (i) candidate-copy baseline (no learning), (ii) MARC with $F_k$ only, (iii) $F_k+D$, (iv) $F_k+D+T$; all evaluated on same $C^{(-k)}$ targets | Adding $D$ increased avg. Dice from 0.8565→0.8866 and ρ from 0.4228→0.7564; adding $T$ further improved Dice to 0.9002 and ρ to 0.7905 | DAPI morphology is the primary contextual cue for cell-level ranking; transcript density provides complementary molecular signal improving both pixel and cell metrics | Transcript density alone drives consensus prediction — ablation shows $F_k+T$ not tested, so $T$'s standalone contribution is Not assessable from supplied material | [Table 2, Paper: PDF p. 6]; [Paper] [Paper: PDF p. 6] |
| Target ablation (Sec 4.3) | Mean-consensus and STAPLE consensus targets yield comparable but distinct trade-offs | Two MARC models trained identically except supervision: (i) arithmetic mean $C^{(-k)}$, (ii) STAPLE-fused $C^{(-k)}$; evaluated against respective targets | Mean target: higher sensitivity (0.9168) and cell ρ (0.7905); STAPLE target: higher precision (0.9128) | Mean consensus better preserves cell-level rankings and captures more true positives; STAPLE yields tighter foreground localization | STAPLE target is *more accurate* — paper notes models evaluated against different targets, so no cross-target accuracy comparison is valid | [Paper] [Paper: PDF p. 5] |
| Qualitative analysis (Figure 4) | MARC localises weakly supported regions and produces spatially varying predictions | Visual inspection of predicted $\hat{C}_k$ maps alongside $D$, $T$, $F_k$ on held-out test region | High $\hat{C}_k$ in regions aligned with nuclear morphology and transcript density; low $\hat{C}_k$ where $F_k$ extends into background or disagrees with $D/T$ | MARC leverages multimodal context to identify ambiguous boundaries; output is spatially resolved and interpretable | MARC identifies *biologically erroneous* segmentations — paper attributes low scores to "method-specific detections with weak support", not biological error per se | [Figure 4, Paper: PDF p. 6]; [Paper] [Paper: PDF p. 7] |

## 11 对结论的正确理解  
论文结论应被精确理解为：**MARC 是一个高效的、共识代理（consensus proxy）学习器，而非真值逼近器（ground-truth approximator）**。其成功体现在两个层面：① *技术有效性*：在给定 LOMO 共识定义下，MARC 能以高精度（Dice≈0.90）和强排序保真度（ρ≈0.79）再生显式共识，且推理开销极低（单次前向）；② *实用价值*：生成的像素/细胞级支持图可直接用于定位低共识区域、排序细胞以供人工复核、或作为下游分析的置信加权因子。但必须强调：所有结论均锚定于“共识即代理”的前提；论文从未声称 MARC 输出反映生物学真实边界，也未证明其能泛化至未见组织/平台/方法组合。Figure 3 和 Table 1 的相关性/重叠指标，衡量的是与 *LOMO 共识* 的一致性，而非与未知真值的一致性。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Consensus as surrogate, not ground truth | Failure modes common across segmentation methods may be reinforced in consensus, leading to systematic bias | Acknowledge usefulness despite limitation; suggest orthogonal validation with membrane/protein markers | [Paper] [Paper: PDF p. 7] |
| Limited generalisability | Evaluated only on single Xenium renal cell carcinoma dataset; candidate methods share inputs from same assay, reducing independence | Evaluate on additional tissues, platforms, and segmentation methods; incorporate orthogonal markers (e.g., membrane) for validation | [Paper] [Paper: PDF p. 7] |
| Platform/method dependence | Candidate methods (Cellpose-SAM, BIDCell, etc.) are all trained on or applied to Xenium data, potentially sharing assay-specific biases | Future work will evaluate additional platforms and segmentation methods beyond Xenium ecosystem | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| MARC’s high cell-level Spearman (ρ=0.79) may partly reflect input leakage: since $F_k$ is directly concatenated, the model could learn to upscale $F_k$’s shape rather than infer consensus from $D/T$ context | The observed gain from adding $D$ and $T$ (Table 2) might stem from morphology/transcript-guided *refinement* of $F_k$ geometry, not genuine consensus *inference* from multimodal disagreement patterns | If true, MARC’s “consensus awareness” is superficial — it wouldn’t generalize to candidate masks with fundamentally wrong topology (e.g., severe over/under-segmentation), undermining its QC utility | Train MARC variants with $F_k$ replaced by *distance-transformed* or *skeletonized* versions of $F_k$; if performance drops sharply, original $F_k$ geometry is critical; if stable, true multimodal reasoning is occurring | [Eq. 2] uses raw $F_k$; Table 2 shows $F_k$-only baseline achieves Dice=0.8565, suggesting strong baseline from geometry alone |
| FUCL’s focus on foreground union $U_k$ may under-penalize errors in *consensus-only* regions (where $C^{(-k)}>0$ but $F_k=0$), as these pixels are included in $U_k$ but contribute less to Dice/IoU after thresholding | Low Dice/Precision in Table 1 for some methods (e.g., ProSeg Precision=0.8626) could indicate FUCL insufficiently constrains false negatives in $C^{(-k)}$-only areas, allowing $\hat{C}_k$ to ignore them | This would compromise MARC’s ability to flag candidate masks that *miss* cells strongly supported by other methods — a critical QC failure mode | Compute per-pixel confusion matrix on $U_k$; specifically analyze false negative rate in $C^{(-k)}=1 \land F_k=0$ regions; compare with standard BCE loss on same region | [Eq. 6] defines $U_k$ inclusively; [Paper] [Paper: PDF p. 4] states FUCL “focuses learning on foreground and disagreement regions”, but disagreement includes $C^{(-k)}$-only areas |
| The choice of arithmetic mean for $C^{(-k)}$ assumes equal reliability of all $K-1$ methods, but methods like BIDCell (self-supervised) and Xenium (onboard) likely have different error profiles | Table 1 shows BIDCell has lowest cell ρ (0.6251) and highest L1 (0.1060), suggesting mean consensus may misrepresent its reliability; STAPLE ablation showed different trade-offs but wasn’t adopted | Using unweighted mean could bias MARC’s learning toward majority-vote artifacts rather than robust agreement, limiting transfer to methods with heterogeneous performance | Retrain MARC with STAPLE-derived $C^{(-k)}$ as primary target and evaluate on *same* mean-consensus test set; if performance improves, weighted consensus is superior | [Paper] [Paper: PDF p. 5] reports STAPLE achieved lower ρ (0.7491 vs 0.7905) but higher precision, yet retains mean due to interpretability (“fraction of supporting methods”) |

## 14 学到的知识  
- **共识可学习性**：多方法共识支持度不是必须计算的产物，而是可被 U-Net 类模型从候选掩码+形态+转录三元组中直接回归的稠密场，FUCL 损失设计是实现此学习的关键；  
- **模态贡献分层**：在 SST QC 中，候选掩码几何提供基础结构，DAPI 形态是提升细胞级排序能力的主因（ρ +0.33），转录密度起精细校准作用（ρ +0.03），印证了“形态主导、分子微调”的双信号协同范式；  
- **轻量 QC 的可行性**：无需访问分割模型内部状态或专家标注，仅需对齐的三模态输入，即可实现接近显式 ensemble 的共识保真度（Dice 0.90），为大规模 SST 数据质控提供了新工程路径；  
- **代理目标的务实价值**：当 ground truth 不可得时，精心设计的代理目标（如 LOMO 共识）结合恰当的损失（FUCL），仍能产出高度实用的中间表示（$\hat{C}_k$），支撑下游决策（如低共识细胞筛选）；  
- **评估指标的语境敏感性**：同一模型在 Dice/IoU（阈值化）与 Spearman ρ（连续值）上表现不同，提示在 QC 任务中需同时关注像素重叠精度与细胞级排序保真度，二者不可相互替代。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：MARC 的“共识代理学习”思路与 multi-omics 整合中的 latent consensus modeling（如 MOFA+ 的 shared factor learning）存在方法论共鸣，均试图从多源不一致观测中推断稳健潜变量；  
- **候选连接/方法论连接**：其三模态输入（$F_k,D,T$）与 spatial transcriptomics 中 cell state representation 的多尺度建模（核形态+膜蛋白+转录）逻辑一致，暗示 $\hat{C}_k$ 可作为细胞状态置信度的代理嵌入；  
- **候选连接/方法论连接**：U-Net 架构与 graph neural networks 的结合点在于：Figure 1(a) 的显式 consensus 可视为在方法图（methods as nodes, agreement as edges）上的消息传递，而 MARC 将此图计算压缩为单跳节点特征融合，为 GNN-based consensus modeling 提供简化基线；  
- **弱连接/方法论连接**：虽不直接支持 perturbation prediction 或 cross-modal alignment，但其生成的 $\hat{C}_k$ 场可作为 perturbation 响应分析的协变量（例如，比较扰动前后 consensus 支持度变化），或作为 multi-omics alignment 的置信加权因子（例如，在转录-蛋白共配准中降权低 $\hat{C}_k$ 区域）。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: MARC-Align: Consensus-Guided Cross-Modal Alignment  
  **originating limitation/observation**: MARC currently operates on aligned $D$ and $T$, but real-world SST often suffers from modality misalignment; authors note future work should incorporate orthogonal markers [Paper] [Paper: PDF p. 7], yet alignment uncertainty is unmodeled.  
  **core hypothesis**: Consensus support $\hat{C}_k$ is sensitive to spatial misregistration; optimizing alignment to maximize $\hat{C}_k$ over a candidate cell should yield biologically more plausible registration than intensity-based metrics.  
  **delta from paper**: Extends MARC from QC to active alignment tool; replaces fixed alignment with differentiable spatial transformer conditioned on $\hat{C}_k$.  
  **initial method**: For a candidate cell $c$, define alignment loss $L_{\text{align}} = -\frac{1}{|c|}\sum_{(x,y)\in c} \hat{C}_k(x,y)$; optimize transformer parameters via gradient ascent on $L_{\text{align}}$.  
  **validation**: Compare alignment accuracy (vs. ground-truth landmarks) of MARC-Align vs. elastix/ANTs on simulated misaligned Xenium tiles; measure downstream cell-type annotation consistency.  
  **failure modes**: May overfit to consensus artifacts if $C^{(-k)}$ contains systematic biases; requires careful initialization to avoid local maxima in $\hat{C}_k$ landscape.  
  **innovation status**: unverified  

- **name**: Perturb-MARC: Consensus-Aware Perturbation Response Modeling  
  **originating limitation/observation**: Paper states risk “Not explicit support for perturbation” [Selection reason]; current MARC treats each tile independently, ignoring temporal or treatment-condition context crucial for perturbation studies.  
  **core hypothesis**: Perturbation-induced boundary instability manifests as reduced consensus support $\hat{C}_k$ in affected cells; aggregating $\hat{C}_k$ changes across conditions reveals spatially resolved perturbation sensitivity.  
  **delta from paper**: Adds condition-aware encoding (e.g., treatment vector) to MARC input and trains on paired pre/post-perturbation tiles to predict *change in consensus support* $\Delta \hat{C}_k$ instead of absolute $\hat{C}_k$.  
  **initial method**: Extend $X_k$ to $X_k^{\text{cond}} = \text{concat}(D, T, F_k, \text{treatment\_emb})$; train to regress $\Delta C^{(-k)} = C^{(-k)}_{\text{post}} - C^{(-k)}_{\text{pre}}$ using FUCL variant on difference map.  
  **validation**: Apply to published perturbation SST datasets (e.g., drug-treated organoids); correlate $\Delta \hat{C}_k$ hotspots with known pathway activity (e.g., phospho-proteomics) and differential expression.  
  **failure modes**: Requires paired consensus targets, which are expensive to generate; may conflate technical perturbation (e.g., fixation artifact) with biological effect.  
  **innovation status**: unverified  

- **name**: Graph-MARC: Consensus Propagation over Cell Graphs  
  **originating limitation/observation**: MARC scores cells independently, but cell boundaries are topologically coupled; low-consensus cells often cluster spatially [Figure 4], suggesting graph-based smoothing could improve robustness.  
  **core hypothesis**: Consensus support is not isolated but propagates through cell adjacency graphs; incorporating neighbor-aware aggregation ($S_{k,c}^{\text{graph}} = \alpha S_{k,c} + (1-\alpha)\frac{1}{|\mathcal{N}(c)|}\sum_{c'\in\mathcal{N}(c)} S_{k,c'}$) enhances detection of locally ambiguous regions.  
  **delta from paper**: Replaces simple mean aggregation [Eq. 8] with graph convolutional layer on Delaunay triangulation of cell centroids, using $\hat{C}_k$ as node features.  
  **initial method**: Build cell graph $\mathcal{G}$ from $M_k$; apply one-layer GCN to $\hat{C}_k$ pixels pooled per cell; recompute $S_{k,c}^{\text{graph}}$ as smoothed node values.  
  **validation**: Compare precision/recall of low-consensus cell detection (using manual review as gold) between vanilla MARC and Graph-MARC on Figure 4-like examples; measure spatial clustering of detected low-$\hat{C}_k$ cells.  
  **failure modes**: Graph construction depends on $M_k$ quality — if $M_k$ has severe over-segmentation, $\mathcal{G}$ becomes noisy; adds computational overhead.  
  **innovation status**: unverified