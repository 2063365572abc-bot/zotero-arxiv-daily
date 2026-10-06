> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: discovery  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions | [Paper] [Paper: PDF p. 1] |
| Authors | Zeyu Dong, Jiahui Zhong | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint | [Paper] [Paper: PDF p. 1] |
| URL | http://arxiv.org/abs/2609.23325v1 | [Paper meta] |
| PDF URL | https://arxiv.org/pdf/2609.23325v1 | [Paper meta] |
| Publication date | 2026-09-20 | [Paper meta] |
| Code availability | https://github.com/jz890/sc-imbalance | [Paper] [Paper: PDF p. 7] |
| Core datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 3] |
| Core backbones | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 3] |
| Evaluated losses | CE, weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 × 3 × 6 × 3) | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结

该论文系统评测了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/ Zheng68K/Pancreas）上的表现，发现整体准确率严重掩盖罕见细胞类别的系统性失效；这种失效可划分为两类：一类是“损失敏感型”（loss-sensitive），可通过重加权等损失设计显著改善；另一类是“严重纠缠型”（severely entangled），其失败根植于嵌入空间几何结构（如邻域吸收、高NC1值），无法被任何测试损失或架构缓解。论文由此提出首个可复现的scFM长尾基准，并给出基于嵌入几何先验（如NC1、最近邻混淆模式）的实操指南——例如优先选用class-balanced loss处理可恢复类，对严重纠缠类应转向数据增补或拒绝预测而非继续调损失。

## 03 研究问题

论文直面一个关键矛盾：单细胞基础模型（scFM）在细胞类型标注任务中报告高达97.5%的总体准确率，但这一指标是否可靠？尤其当罕见细胞类型（如疾病早期过渡态、病理亚群）恰恰是临床与机制研究的核心目标时，模型是否在“看不见的地方”持续失败？  
→ 作者假设：这种失败并非随机噪声，而是由数据内在不平衡结构驱动的、可诊断的系统性现象，且其可修复性取决于两个正交维度：一是训练样本的绝对稀缺程度（而非相对频率），二是嵌入空间中类间几何关系（如类中心距离、簇内紧致度）。  
→ 方法路径：通过控制变量实验（固定backbone fine-tuning protocol、固定基因panel、固定split策略），解耦损失函数选择的影响，再结合线性探针、UMAP可视化、NC1几何度量与跨架构混淆分析，将“为什么某些类永远失败”从经验观察升维为机制可解释的诊断框架。

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer）已成为细胞类型标注默认主干，但已有工作（Alsabbagh et al. 2023; Naziri et al. 2025）指出其在罕见子群上性能骤降，且该问题被聚合指标（如accuracy）系统性掩盖。现有缓解策略分三类：采样法（oversampling）、表示法（post-pretraining prototype shaping）、损失法（reweighting/margin adjustment）。其中，损失法因部署轻量、兼容预训练范式而具工程优势，但缺乏跨架构、跨数据集的系统性验证——Alsabbagh et al. (2023) 聚焦采样，Zhao et al. (2025) 提出专用损失+新预训练数据，均未在统一框架下横向比较通用长尾损失。本文填补此空白：以“损失函数”为单一干预轴，在保持所有其他条件（backbone config、data split、tokenization）不变前提下，构建162-run控制实验，将长尾问题从“是否有效”的粗粒度判断，推进到“何时有效、为何无效、如何预判”的细粒度机制理解。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **Aggregate metrics mask rare-class failure** | Accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 3] | Driven by dataset imbalance structure, not backbone pretraining [Paper] [Paper: PDF p. 1] | Figure 2 (left): consistent gap under plain CE; text states "this gap is present regardless of which foundation model is used" [Paper] [Paper: PDF p. 3] |
| **Loss-level interventions are insufficient for some rare classes** | Two MS classes (oligodendrocyte C, phagocyte) achieve near-zero F1 under *all* 6 losses & 3 backbones [Paper] [Paper: PDF p. 5] | Too few training examples (n=3 each) + transcriptional overlap causing neighborhood absorption in embedding space [Paper] [Paper: PDF p. 5–6] | Figure 3 (left): darkest rows across all three backbone columns; Figure 4: UMAP shows 116 test cells absorbed into unrelated classes; Section 5.1: "both have only 3 training examples" [Paper] [Paper: PDF p. 5] |
| **Reweighting benefit is misattributed to relative frequency** | Weighted CE performs best on MS but worst on Zheng68K despite similar imbalance ratios [Paper] [Paper: PDF p. 3] | Benefit depends on *absolute* training-set size of rare class, not its share of dataset or overall imbalance ratio [Paper] [Paper: PDF p. 1, 4] | Figure 3 (right): strong negative correlation (r=−0.77) between log(training size) and ΔF1; Section 4.3: "MS, whose rare classes have the fewest training examples in absolute terms [...] exhibits the greatest benefit" [Paper] [Paper: PDF p. 4] |
| **Losses make hidden trade-offs obscured by Macro-F1** | Logit adjustment boosts rare recall but incurs largest precision penalty among 6 losses [Paper] [Paper: PDF p. 4] | It shifts decision threshold rather than improving feature separability, increasing false positives [Paper] [Paper: PDF p. 4] | Figure 2 (right): logit-adjusted point lies far below y=x line; Table 1: lowest rare-class precision (0.632 vs CE's 0.648); text: "achieves its recall gains primarily by shifting the decision threshold" [Paper] [Paper: PDF p. 4] |

## 06 核心思想

论文核心思想是**将单细胞基础模型的长尾失效解构为两个正交可诊断的机制层**：第一层是**数据层瓶颈**（data scarcity），表现为极低训练样本数（如n=3）导致嵌入空间中类中心无法形成可区分簇，进而引发“邻域吸收”（neighborhood absorption）——即少数样本被完全吞没进其他类的嵌入邻域；第二层是**优化层瓶颈**（optimization mismatch），指即使存在判别性信号（linear probe可验证），当前损失函数家族仍无法有效引导分类器头利用该信号，根源在于损失设计未适配单细胞嵌入的几何特性（如类间边界模糊、类内异质性高）。  
→ 这一思想直接颠覆了“重加权总能改善罕见类性能”的隐含假设，指出**损失选择的有效性必须以前置几何诊断为前提**：NC1值过高或跨架构一致混淆模式，即为“严重纠缠”信号，此时调损失是徒劳的；而ΔF1与log(absolute count)的强负相关，则为“损失敏感”类提供了可量化的收益预测器。最终，论文将长尾问题从超参调优任务，重构为一个**基于嵌入几何先验的决策流程**（diagnostic → predict → select loss → validate）。

## 07 方法总览

方法采用严格的控制变量范式：在3个backbone（scGPT/scBERT/Geneformer）、3个dataset（MS/Zheng68K/Pancreas）、6个loss（CE/weighted CE/class-balanced/focal/LDAM/logit-adjusted）的全因子组合中，对每个单元执行3次随机种子训练（共162 run）；所有实验共享同一套预处理（scanpy HVG selection, ln(1+x) transform, gene panel fixed per dataset）与评估协议（validation checkpoint selected by Macro-F1, test evaluation by argmax）。关键创新在于**多尺度诊断闭环**：（1）宏观：用Macro-F1与rare-class recall/AUPRC量化损失效果；（2）中观：用per-class ΔF1与log(training size)回归定位可恢复类；（3）微观：用UMAP可视化（Figure 4）、NC1几何度量（Equation 4）、跨架构混淆矩阵（Section 5.2）和线性probe（Section 5.3）解析失败根源。整个流程不修改backbone结构或预训练，纯粹考察损失函数作为“接口层”的能力边界。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **Controlled loss benchmark grid** | Isolate loss-function effect by holding backbone, data split, preprocessing constant | To disentangle loss efficacy from architecture-specific biases or data leakage artifacts | Input: fixed train/test splits, frozen backbone encoder outputs; Output: per-(backbone,dataset,loss) Macro-F1/rare-recall | Section 3: "holding sample distribution and batch composition fixed throughout to isolate the effect of the loss-function axis" [Paper] [Paper: PDF p. 1]; Table 1 reports aggregated results [Paper] [Paper: PDF p. 5] | Would confound loss comparison with backbone variance (e.g., scBERT’s frozen encoder vs scGPT’s full FT) — see Section 3 protocol details [Paper] [Paper: PDF p. 2] |
| **Per-class ΔF1 analysis** | Quantify gain from switching loss for each rare class c: ΔF1,c = max<sub>ℓ∈L</sub> F<sup>(ℓ)</sup><sub>1,c</sub> − F<sup>(CE)</sup><sub>1,c</sub> | To test whether reweighting benefit is driven by absolute sample count, not relative frequency | Input: per-class F1 scores across all losses/seeds/backbones; Output: scalar ΔF1,c per rare class | Equation 3 [Paper] [Paper: PDF p. 4]; Figure 3 (right): scatter plot of ΔF1,c vs log(training size) with r=−0.77 [Paper] [Paper: PDF p. 4] | Would obscure the key insight that "MS benefits most because its rare classes have smallest *absolute* counts", leading to incorrect generalization about imbalance ratio [Paper] [Paper: PDF p. 4] |
| **Embedding geometry diagnostic (NC1 + nearest-neighbor)** | Measure cluster tightness (NC1 = tr(Σ<sub>W</sub>)/tr(Σ<sub>B</sub>)) and confusion topology | To distinguish "severely entangled" classes (high NC1 or concentrated neighbor absorption) from "loss-sensitive" ones | Input: frozen test-set embeddings (scGPT/scBERT/Geneformer under CE); Output: NC1 value per class, rank-1 neighbor class per entangled cell | Equation 4 [Paper] [Paper: PDF p. 6]; Section 5.2: "oligodendrocyte C shows substantially higher NC1 [...] quantitatively confirming it lacks tight clustering" [Paper] [Paper: PDF p. 6]; Figure 4 visualization [Paper] [Paper: PDF p. 7] | Would leave "why some classes never recover" as anecdotal; NC1 provides quantitative, backbone-invariant signature of geometric failure [Paper] [Paper: PDF p. 6] |
| **Linear probe on frozen embeddings** | Test whether discriminative signal exists *in the representation* independent of classifier head training | To localize bottleneck: is failure due to poor representation (pretrain issue) or poor classifier optimization (loss issue)? | Input: frozen CE-fine-tuned embeddings; Output: 5-fold CV F1 of class-balanced logistic regression | Section 5.3: probe achieves higher F1 than any trained head for oligodendrocyte C/phagocyte (e.g., scGPT probe 0.465 vs best trained 0.329) [Paper] [Paper: PDF p. 6] | Would falsely attribute failure to representation collapse; probe proves signal exists but is unused, implicating loss design [Paper] [Paper: PDF p. 6] |

## 09 关键公式与符号

- **No verifiable closed-form equation is presented in the paper.** All listed equations are descriptive definitions or computational recipes, not derived models.
- **Equation 1**: `Macro-F1 = 1/C ∑_{c=1}^C F1,c` — Definition of unweighted mean F1 across C classes [Paper] [Paper: PDF p. 3]. Symbol `F1,c` denotes F1 score of class `c`.
- **Equation 2**: `Recall_R = 1/|R| ∑_{c∈R} Recall_c` — Definition of macro-averaged recall over rare-class set `R` [Paper] [Paper: PDF p. 3]. `R` is defined as classes with training frequency <5% [Paper] [Paper: PDF p. 3].
- **Equation 3**: `ΔF1,c = max_{ℓ∈L} F^{(ℓ)}_{1,c} − F^{(CE)}_{1,c}` — Definition of per-class F1 gain from optimal loss over CE [Paper] [Paper: PDF p. 4]. `L` is the set of six losses.
- **Equation 4**: `NC1 = tr(Σ_W) / tr(Σ_B)` — Neural collapse trace ratio [Paper] [Paper: PDF p. 6]. `Σ_W`: average within-class scatter matrix; `Σ_B`: between-class scatter matrix of class centroids around global mean. Lower NC1 indicates better separation.
- **Key symbols**: `R` (rare-class set), `F1,c` (class-wise F1), `Recall_c` (class-wise recall), `NC1` (geometry metric), `L` (loss set), `ΔF1,c` (reweighting gain).

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|-------------------------|----------------------------------|--------|
| **Aggregate metric gap (Fig 2 left)** | Plain CE yields consistent accuracy > Macro-F1 > rare-class recall across all architectures | Mean over 9 (backbone×seed) runs per dataset; same CE loss, fixed protocol | Gap present for all 3 datasets, regardless of backbone [Paper] [Paper: PDF p. 3] | Gap is inherent to data imbalance structure, not backbone-specific | That pretraining causes the gap — authors explicitly state "driven by dataset structure rather than pretraining" [Paper] [Paper: PDF p. 1] | [Paper] [Paper: PDF p. 3], Figure 2 |
| **Loss ranking (Table 1)** | Class-balanced loss & LDAM are most consistent across datasets | Mean rank computed within each (backbone, dataset) cell before averaging | Class-balanced mean rank 2.4, LDAM 2.6 (out of 6) [Paper] [Paper: PDF p. 3] | These two losses generalize best to unseen dataset imbalances | That they are universally optimal — weighted CE tops MS Macro-F1 (0.721), LDAM tops Pancreas (0.819) [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3], Table 1 |
| **ΔF1 vs log(size) regression (Fig 3 right)** | Reweighting benefit is predicted by absolute training-set size | Pearson correlation of ΔF1,c with log(training size) across 19 recoverable rare classes | r = −0.77, p < 0.001 [Paper] [Paper: PDF p. 4] | Absolute count, not relative frequency, governs reweighting ROI | That this holds for *all* rare classes — 4 severely entangled classes excluded (n=3 samples) [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 3 |
| **Logit adjustment trade-off (Fig 2 right)** | Logit adjustment trades rare-class precision for recall | Plot of rare-class precision vs recall for all 6 losses, averaged over 9 settings | Logit-adjusted point lies far below y=x line; lowest precision (0.632) despite high recall (0.685) [Paper] [Paper: PDF p. 4] | Its recall gain stems from threshold shift, not improved separability | That it harms non-rare classes — non-rare precision spread is only 1.1 points vs 10.6 for rare [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 2 |
| **Linear probe on frozen embeddings (Sec 5.3)** | Discriminative signal exists for severely entangled classes | Class-balanced logistic regression on frozen CE embeddings, 5-fold CV | Probe F1 exceeds best trained head F1 for oligodendrocyte C (0.465 vs 0.329) and phagocyte (0.462 vs 0.329) [Paper] [Paper: PDF p. 6] | Bottleneck is in classifier training/loss design, not representation collapse | That a nonlinear probe would close the gap — authors note this as future work [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 6], Section 5.3 |

## 11 对结论的正确理解

- **"Class-balanced loss and LDAM are most consistent"** 意味着它们在9个(backbone, dataset)组合中平均排名最高（2.4/2.6），但**不意味着它们在每个组合中都最优**——例如weighted CE在MS上Macro-F1最高（0.721），LDAM在Pancreas上最高（0.819）[Paper] [Paper: PDF p. 3]。一致性指鲁棒性，非绝对优越性。
- **"Reweighting benefit predicted by absolute count"** 是一个统计规律（r=−0.77），适用于"recoverable"类（即排除n=3样本的严重纠缠类后），**不能外推至n<5的极端稀缺场景**——论文明确将n=3类标记为"severely entangled"并从回归中剔除[Paper] [Paper: PDF p. 4]。
- **"Logit adjustment trades precision for recall"** 是基于其在rare-class precision-recall图中位于y=x线下方的观测，**不意味着它降低整体精度**——非罕见类的precision spread仅1.1点，表明其影响高度集中在罕见类[Paper] [Paper: PDF p. 4]。
- **"Failure rooted in embedding geometry"** 由多重证据支撑：UMAP显示116细胞被吸收（Figure 4）、跨架构混淆模式一致（Section 5.2）、NC1值异常（oligodendrocyte C高，phagocyte低但邻域集中）[Paper] [Paper: PDF p. 6–7]，**但几何失败本身由数据稀缺（n=3）触发，非模型固有缺陷**。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|----------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer evaluated; other models (scFoundation, CellPLM) remain untested | "Other existing single-cell foundation models [...] remain untested" [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Classifier head expressivity ceiling** | Linear probe recovers signal unused by trained heads, suggesting current losses may not fully exploit representation | "A more expressive, nonlinear classifier head might extract additional signal beyond what the six losses we test currently achieve" [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Isolated imbalance axis** | Study focuses solely on cell-type frequency imbalance; ignores compounding factors like demographic composition or batch effects | "Compounding variables such as demographic composition [...] or batch effects [...] require future investigation" [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|---------------------------------------------|----------------|----------------|-------|
| **NC1's sensitivity to small-n classes** | Phagocyte (n=3) has low NC1 (0.17–0.32) not because it's well-separated, but because tiny n makes Σ<sub>W</sub> artificially small — a known statistical artifact in scatter-matrix estimation | Misinterpreting low NC1 as "good geometry" could wrongly classify phagocyte as recoverable, delaying correct diagnosis of data scarcity | Compute NC1 with bootstrap resampling (n=100) on phagocyte's 3 samples to assess variance; compare to synthetic n=3 clusters from Gaussian mixture | Section 5.2: "its small cell count means a handful of tightly clustered cells embedded inside another class’s region can produce low within-class scatter despite total confusability" [Paper] [Paper: PDF p. 6] |
| **Linear probe's CV setup** | Probe uses 5-fold stratified CV *within test-set embeddings*, measuring internal separability, not train/test generalization — yet conclusions treat it as evidence of "unused signal" | If the probe overfits the test set (despite stratification), the "signal exists" claim weakens; true test requires held-out validation | Repeat probe on *held-out validation set* (10% of training data, as used for checkpoint selection) and compare F1 to trained head's validation F1 | Section 5.3: "5-fold stratified cross-validation within the frozen test-set embeddings (measuring CV-internal separability, not train/test generalization)" [Paper] [Paper: PDF p. 6] |
| **UMAP's role in Figure 4** | UMAP is a stochastic, non-linear projection; visual "absorption" in Figure 4 may not reflect true high-dimensional geometry, especially for n=3 clusters | Over-reliance on UMAP could lead to false geometric conclusions; the core claim (neighborhood absorption) is better supported by centroid distances and NC1 | Replace UMAP with t-SNE (different stochasticity) and PCA (linear) for same scGPT embeddings; verify if oligodendrocyte C/phagocyte still embed near confusion partners | Figure 4 caption: "UMAP (Healy and McInnes 2024) of MS test-set embeddings (scGPT)" — no robustness check reported [Paper] [Paper: PDF p. 7] |

## 14 学到的知识

- **长尾失效不是单一层级问题，而是数据层（n=3样本）与优化层（loss无法引导利用信号）的双重瓶颈**：前者需数据工程（如主动学习标注），后者需损失/分类器协同设计。
- **Macro-F1是危险的汇总指标**：它掩盖了logit adjustment这类"recall-for-precision"的隐性权衡，必须辅以precision-recall曲线或AUPRC分析。
- **嵌入几何可作为损失选择的前置诊断器**：NC1 >1.0 或跨架构一致混淆（如phagocyte→oligodendrocyte A）是"放弃调损失、转向数据补全"的强信号；而ΔF1与log(absolute count)的负相关，则为"值得尝试class-balanced loss"提供量化依据。
- **线性probe是解耦瓶颈的黄金工具**：当probe F1 ≫ trained head F1，说明问题在分类器训练（loss/optimizer），而非表示学习（pretrain）——这对用户做perturbation prediction时诊断"是表征不对还是head不会用"极具价值。
- **计算开销几乎为零**：所有重加权损失增加的训练时间 <3.2%，远小于backbone选择差异（scBERT比Geneformer慢18×）[Paper] [Paper: PDF p. 4]，故无理由不默认启用class-balanced loss。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的"embedding geometry diagnostic"（NC1 + nearest-neighbor）与用户研究方向中的**cell state representation**和**perturbation prediction**高度契合——若扰动后细胞状态在嵌入空间中发生"邻域吸收"（如treated cell被吸收进control cluster），同样可用NC1突变或最近邻分布偏移来量化扰动效应的可检测性。
- **候选连接/方法论连接**：论文揭示的"绝对样本数决定重加权收益"规律，可迁移至用户**multi-omics**场景：当整合scRNA+scATAC时，若某稀有细胞类型的ATAC peak覆盖度极低（n=3 peaks），其跨模态对齐可能同样陷入"严重纠缠"，需优先提升该模态测序深度而非调alignment loss。
- **候选连接/方法论连接**：Figure 4的UMAP可视化策略（highlight rare cells against gray background）可直接复用于用户**spatial transcriptomics**研究——例如在Visium切片UMAP中高亮病灶区稀有细胞，观察其是否被吸收进邻近正常组织簇，从而判断空间微环境是否掩盖病理信号。
- **弱连接/方法论连接**：论文使用的scGPT/scBERT/Geneformer均为序列化建模（gene token order），与用户关注的**graph neural networks**无直接接口，但其"几何诊断"思想可启发GNN：用节点嵌入的类内/类间距离比（类似NC1）替代UMAP，诊断图结构对稀有细胞类型判别性的贡献。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometry-Guided Reject Option for scFM  
  **originating limitation/observation**: Authors identify "severely entangled" classes via NC1 and nearest-neighbor patterns, and recommend "abstaining" rather than loss engineering [Paper] [Paper: PDF p. 7]. But no operational reject threshold is provided.  
  **core hypothesis**: A joint threshold on NC1 > τ₁ AND top-3 nearest neighbors belonging to the same non-self class with entropy < τ₂ predicts unrecoverable classes with >95% precision.  
  **delta from paper**: Paper diagnoses but doesn’t automate rejection; this defines precise, geometry-based rejection criteria.  
  **initial method**: On MS test embeddings, sweep τ₁ (NC1) and τ₂ (neighbor entropy) to maximize precision of "reject" label (true if F1<0.1 under all losses). Validate on Zheng68K/Pancreas.  
  **validation**: Reject rate vs. rare-class recall trade-off curve; compare to baseline rejection by training size <5.  
  **failure modes**: Over-rejection if τ thresholds too loose; under-rejection if NC1 estimation unstable for n<10.  
  **innovation status**: unverified  

- **name**: Perturbation-Aware NC1 for Spatial Transcriptomics  
  **originating limitation/observation**: Paper uses NC1 on scRNA embeddings to diagnose rare-class failure; spatial data has inherent neighborhood structure (spots), but NC1 assumes i.i.d. samples.  
  **core hypothesis**: Spatially constrained NC1 — where Σ<sub>W</sub> includes only spots within 3-neighbor radius — better captures microenvironment-driven entanglement in spatial data.  
  **delta from paper**: Adapts NC1 from i.i.d. scRNA to graph-structured spatial data by incorporating spatial adjacency.  
  **initial method**: Build spot graph from Visium coordinates; compute spatial-NC1 = tr(Σ<sub>W,spatial</sub>)/tr(Σ<sub>B</sub>) where Σ<sub>W,spatial</sub> averages scatter only over spatial neighbors. Correlate with perturbation prediction error.  
  **validation**: On simulated perturbation (e.g., cytokine-treated spots), test if spatial-NC1 drop predicts successful recovery better than vanilla NC1.  
  **failure modes**: Requires accurate spatial graph construction; sensitive to spot density variation.  
  **innovation status**: unverified  

- **name**: Multi-Omics Entanglement Transfer  
  **originating limitation/observation**: Paper finds n=3 training samples cause entanglement in scRNA; in multi-omics, one modality (e.g., scATAC) may have even lower coverage for rare cells.  
  **core hypothesis**: Entanglement status (recoverable vs. severely entangled) transfers across modalities — if a rare cell type is severely entangled in scRNA, its scATAC embedding will show similarly high spatial-NC1.  
  **delta from paper**: Extends entanglement diagnosis from single-modality to cross-modality consistency check.  
  **initial method**: For rare classes in matched scRNA+scATAC, compute NC1 on both modalities' embeddings; measure correlation of NC1 values and confusion patterns.  
  **validation**: Train modality-specific classifiers; test if "entangled in RNA" predicts "entangled in ATAC" for same class.  
  **failure modes**: Modality-specific batch effects may dominate entanglement signal.  
  **innovation status**: unverified