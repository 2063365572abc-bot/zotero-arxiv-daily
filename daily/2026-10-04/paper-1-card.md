> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods/discovery  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions | [Paper] [Paper: PDF p. 1] |
| Authors | Zeyu Dong, Jiahui Zhong | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv | [Paper] [Paper: PDF p. 1] |
| URL | http://arxiv.org/abs/2609.23325v1 | [Paper meta] |
| PDF URL | https://arxiv.org/pdf/2609.23325v1 | [Paper meta] |
| Publication date | 2026-09-20 | [Paper meta] |
| Code URL | https://github.com/jz890/sc-imbalance | [Paper] [Paper: PDF p. 7] |
| Backbones | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 2] |
| Datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 2] |
| Losses evaluated | Cross-entropy (CE), weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |
| Key metrics | Macro-F1, rare-class recall (Recall<sub>R</sub>), rare-class precision, rare-class macro-AUPRC, ∆F1<sub>c</sub>, NC1 | [Paper] [Paper: PDF p. 3–6] |

## 02 一句话总结

该论文系统评测了六种长尾损失函数（CE、weighted CE、class-balanced loss、focal loss、LDAM、logit-adjusted softmax）在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/ Zheng68K/ Pancreas）上的表现，共162次受控训练；发现整体准确率严重掩盖罕见细胞类别的系统性失败，且该失败可划分为两类机制：一类是“loss-sensitive”（可通过损失函数优化恢复），另一类是“severely entangled”（所有损失与架构均失效，根植于嵌入几何结构）；作者进一步揭示：对可恢复类，重加权收益由**绝对训练样本数**而非相对频率决定；class-balanced loss 和 LDAM 是最稳健的选择，而 logit adjustment 实质上是以精度为代价换取召回。该工作不扩展至 spatial 或 multi-omics，但其 benchmark 设计可直接复用于用户 perturbation prediction 场景。

## 03 研究问题

论文直面一个被广泛忽视却临床关键的矛盾：单细胞基础模型（如 scGPT）在 cell-type annotation 上报告高达 97.5% 的 aggregate accuracy，但这一指标是否真实反映其对疾病相关罕见细胞亚群（如 MS 中的 oligodendrocyte C）的判别能力？[Paper] [Paper: PDF p. 1]  
作者质疑：当前主流假设——即“长尾损失函数能系统性缓解罕见类失败”——是否成立？该假设是否依赖特定 backbone 架构或数据集结构？[Paper] [Paper: PDF p. 1]  
更深层的问题是：当损失函数优化失效时，瓶颈究竟在数据稀缺性、表示坍缩（neural collapse）、还是分类器设计？能否通过嵌入几何特征（如 NC1、最近邻分布）在训练前预判某类是否“不可救”？[Paper] [Paper: PDF p. 5–6]

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer）已成为 cell-type annotation 默认 backbone，但其高 aggregate accuracy 被证实由常见类主导，罕见类（尤其疾病相关过渡态/病理态）持续被低估 [Paper] [Paper: PDF p. 1]；Alsabbagh et al. (2023) 已在采样策略层面验证此现象，但未系统考察损失函数轴 [Paper] [Paper: PDF p. 1–2]。  
既有长尾学习方法分三类：(1) 采样法（如 SMOTE、随机过采样），但会改变训练分布；(2) 表示解耦法（如 decoupled representation + classifier calibration），需额外训练阶段；(3) 损失重加权法（如 class-balanced loss、LDAM），可即插即用，但其在单细胞基础模型上的跨架构鲁棒性未知 [Paper] [Paper: PDF p. 2]。  
本文选择第三条路径，因其与用户研究方向（perturbation prediction、cell state representation）高度兼容：损失函数是轻量级、可迁移的干预模块，无需修改 backbone 或引入新架构，便于嵌入到用户现有 pipeline 中 [Paper] [Paper: PDF p. 2]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|----------------------------|--------------------------|
| Aggregate metrics mask rare-class failure | Accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings | Driven by dataset imbalance structure, not pretraining bias | [Paper] [Paper: PDF p. 3], Figure 2 (left), [Paper] [Paper: PDF p. 4] |
| Loss-level interventions are insufficient for some rare classes | Two MS classes (oligodendrocyte C, phagocyte) achieve near-zero F1 under *all* six losses and *all* three backbones | Too few training examples (n=3) + transcriptional overlap → embedding geometry failure, not classifier limitation | [Paper] [Paper: PDF p. 5], Figure 3 (left), Figure 4, [Paper] [Paper: PDF p. 6] |
| Reweighting benefit is misattributed to relative frequency | Weighted CE performs best on MS but worst on Zheng68K despite similar imbalance ratio | Benefit is predicted by *absolute* training-set size of rare class, not its share of dataset | [Paper] [Paper: PDF p. 4], Figure 3 (right), Equation 3, r = −0.77 (p < 0.001) |
| Loss functions make hidden trade-offs obscured by Macro-F1 | Logit adjustment boosts rare-class recall but *lowers* precision vs. CE | It shifts decision threshold rather than improving feature separability → more false positives | [Paper] [Paper: PDF p. 4], Figure 2 (right), Table 1 (precision column) |

## 06 核心思想

论文核心洞察是：**罕见类失败不是单一现象，而是具有可诊断的双重机制**——这直接挑战了“换一个更好的损失函数就能解决所有长尾问题”的简化假设。  
第一重机制（loss-sensitive regime）源于训练信号不足但尚可补救：此类别在嵌入空间中仍保有线性可分性（linear probing 可恢复非零 F1），其性能提升与绝对样本数强负相关（Figure 3 right），故重加权有效；这支持用户在 perturbation prediction 中对低丰度 perturbation 响应细胞采用 class-balanced loss。  
第二重机制（severely entangled regime）是结构性失败：极少数样本（n=3）导致嵌入点被完全吸收进无关类邻域（Figure 4），NC1 几何指标与最近邻熵可提前预警；此时损失函数优化无效，瓶颈在数据本身或表示学习阶段，提示用户对极稀有 perturbation 状态应优先考虑数据增广或 abstention 策略，而非调参。  
该二分法将“是否值得投入损失工程”转化为一个可量化、可预测的决策问题，而非经验试错。

## 07 方法总览

论文采用**控制变量+多维诊断**范式：固定 backbone 微调协议、数据预处理、split 划分，仅系统性遍历 loss 函数轴（6 losses × 3 backbones × 3 datasets × 3 seeds = 162 runs）；评估指标覆盖 aggregate（accuracy）、平衡（Macro-F1）、长尾专用（Recall<sub>R</sub>, AUPRC）三层；诊断层则引入：(1) per-class ∆F1 分析（Equation 3）定位可恢复类；(2) UMAP + nearest-neighbor + NC1（Equation 4）刻画嵌入几何；(3) linear probe 在 frozen embeddings 上测试 discriminative signal 是否残留。整个流程不引入新模型或数据，纯粹通过严谨 benchmark 揭示现有工具链的边界与机制。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|-------------------|----------------------|-----------------------------------|
| **Loss-function grid** | Systematically compare 6 long-tail losses under identical conditions | Isolate loss-axis effect from architecture/data confounders; test off-the-shelf robustness | Input: logits + labels; Output: scalar loss | [Paper] [Paper: PDF p. 3], Table 1, Figure 2 | Without this grid, no cross-loss ranking (e.g., class-balanced loss rank 2.4) or trade-off quantification (e.g., logit adjustment’s precision penalty) possible |
| **Per-class ∆F1 analysis** (Eq. 3) | Quantify gain of best loss over CE for each rare class c | Test hypothesis that reweighting benefit depends on absolute sample count, not relative frequency | Input: F1<sub>c</sub> under each loss; Output: ∆F1<sub>c</sub> scalar | [Paper] [Paper: PDF p. 4], Figure 3 (right), r = −0.77 correlation | Without per-class ∆F1, the key insight “absolute count predicts benefit” would be invisible; dataset-level averages (Table 1) hide this trend |
| **Embedding geometry diagnostics** (NC1, nearest-neighbor entropy) | Detect "severely entangled" classes before training | Distinguish data-scarcity failure (fixable by more data) from classifier failure (fixable by loss) | Input: frozen test-set embeddings; Output: NC1 ratio (Eq. 4), neighbor entropy | [Paper] [Paper: PDF p. 6], Figure 4, NC1 values for oligodendrocyte C (1.19–1.79) vs. phagocyte (0.17–0.32) | Without NC1/neighbor analysis, Figure 4’s visual absorption would remain anecdotal; no quantitative signature to trigger "abstain" recommendation in Section 6 |
| **Linear probe on frozen embeddings** | Test whether discriminative signal exists *in representation* despite classifier failure | Localize bottleneck: if probe outperforms trained head, issue is classifier training, not representation collapse | Input: frozen embeddings + labels; Output: CV-F1 score | [Paper] [Paper: PDF p. 6], probe F1 > trained F1 for oligodendrocyte C (0.465 vs. 0.329) and phagocyte (0.462 vs. 0.000) | Without linear probe, conclusion “loss design leaves signal unused” [Paper] [Paper: PDF p. 6] would lack direct evidence; could wrongly blame pretraining |

## 09 关键公式与符号

- **No verifiable closed-form equations** are presented in the paper beyond definitions. All listed equations are metric definitions or geometric ratios, not learned models or algorithmic formulas.  
- **Equation 1**: Macro-F1 = $\frac{1}{C}\sum_{c=1}^{C} F1_c$ — unweighted mean of per-class F1 scores across $C$ classes [Paper] [Paper: PDF p. 3].  
- **Equation 2**: Rare-class recall = $Recall_R = \frac{1}{|R|}\sum_{c\in R} Recall_c$ — macro-average restricted to rare class set $R$ [Paper] [Paper: PDF p. 3].  
- **Equation 3**: Per-class gain = $\Delta F1_c = \max_{\ell\in L} F1^{(\ell)}_c - F1^{(CE)}_c$ — best-loss improvement over CE for class $c$, used for correlation with sample count [Paper] [Paper: PDF p. 4].  
- **Equation 4**: Neural collapse trace ratio = $NC1 = \frac{\text{tr}(\Sigma_W)}{\text{tr}(\Sigma_B)}$ — ratio of within-class to between-class scatter; lower = tighter clusters [Paper] [Paper: PDF p. 6].  
- **Key symbols**: $R$ = set of rare classes (training frequency < 5%) [Paper] [Paper: PDF p. 3]; $L$ = set of six losses [Paper] [Paper: PDF p. 4]; $\Sigma_W$, $\Sigma_B$ = within-class and between-class scatter matrices [Paper] [Paper: PDF p. 6].

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|---------------------------|--------|----------------------|-------------------------------|--------|
| **Aggregate metrics gap** | CE’s accuracy > Macro-F1 > rare-class recall holds across architectures | Mean over 9 (backbone×seed) runs per dataset; same train/test split, preprocessing | Gap consistent for all three datasets (Figure 2 left) | Dataset imbalance structure, not backbone choice, drives the gap | That pretraining has *no* role — authors note variance in scBERT’s CE Macro-F1 vs. Alsabbagh et al. due to config differences [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3], Figure 2 (left) |
| **Loss ranking by Macro-F1** | Class-balanced loss & LDAM are most consistent | Rank each loss within each (backbone, dataset) cell, then average rank across 9 cells | Class-balanced loss mean rank 2.4, LDAM 2.6 (Table 1) | These two are top generalists; weighted CE wins on MS but fails on Zheng68K | That they are universally optimal — weighted CE beats them on MS Macro-F1 (0.721 vs. 0.716) | [Paper] [Paper: PDF p. 3], Table 1 |
| **Logit adjustment trade-off** | Logit adjustment trades rare-class precision for recall | Plot rare-class precision vs. recall for all losses (Figure 2 right) | Logit adjustment has highest recall gain (+0.055) but lowest precision (−0.031 vs. CE) | Its gain comes from threshold shift, not improved separability | That it harms non-rare classes — non-rare precision spread is only 1.1 points [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 2 (right), Table 1 |
| **∆F1 vs. absolute sample count** | Absolute training-set size predicts reweighting gain | Pearson correlation of log(sample count) vs. ∆F1<sub>c</sub> for rare classes (excluding severely entangled) | r = −0.77, p < 0.001 (n = 19) [Paper] [Paper: PDF p. 4] | Gain is driven by absolute scarcity, not relative imbalance | That the relationship is causal — authors state correlation, not causation | [Paper] [Paper: PDF p. 4], Figure 3 (right) |
| **Linear probe on frozen embeddings** | Discriminative signal exists for severely entangled classes | Fit class-balanced logistic regression on CE-frozen test embeddings, 5-fold CV | Probe F1 > best trained F1 for oligodendrocyte C (0.465 vs. 0.329) and phagocyte (0.462 vs. 0.000) | Bottleneck is classifier training, not representation collapse | That a nonlinear probe would close the gap — not tested | [Paper] [Paper: PDF p. 6] |

## 11 对结论的正确理解

- “Class-balanced loss is most consistent” 意味着它在 9 个 (backbone, dataset) 组合中平均排名最高（2.4），**并非**在每个组合中都排名第一（weighted CE beats it on MS Macro-F1）；其优势在于稳定性，适合用户在未知数据上快速部署。  
- “Logit adjustment trades precision for recall” 是一个**定量结论**：它在 Table 1 中 rare-class precision 列数值最低（0.650 for MS），同时 recall 列较高（0.632），图 2 右侧点位于 y=x 线下方，表明其设计本质是校准阈值而非增强特征。  
- “Severely entangled classes are unrecoverable” 是指在当前实验设置下（6 losses, 3 backbones, fixed fine-tuning protocol），它们的 F1 始终接近零；但 linear probe 证明信号存在，因此“unrecoverable”特指**所测试的损失函数族无法利用该信号**，而非绝对不可分。  
- “Absolute sample count predicts gain” 是一个**empirical regularity**（r = −0.77），适用于该 benchmark 的三个数据集，但未声称是普适物理定律；用户在自己的 perturbation 数据上需重新验证该相关性。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| Limited backbone coverage | Only scGPT, scBERT, Geneformer tested; scFoundation and CellPLM untested | Extend benchmark to other foundation models (scFoundation, CellPLM) | [Paper] [Paper: PDF p. 7] |
| Classifier head expressivity | Linear probe recovers signal missed by trained heads, suggesting current heads may be insufficiently expressive | Test more expressive classifier heads (e.g., MLPs) beyond linear probes | [Paper] [Paper: PDF p. 7] |
| Isolated imbalance axis | Study focuses solely on cell-type class imbalance; ignores compounding factors like demographic composition or batch effects | Investigate interactions between class imbalance and demographic/batch variables | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|----------------|--------|
| The “severely entangled” regime is defined by near-zero F1 under all losses, but the linear probe shows non-trivial F1 (0.175–0.465). This suggests the failure is not in the *representation*, but in the *training dynamics* of the classifier head (e.g., gradient starvation, poor initialization). | The linear probe uses class-balanced logistic regression with CV, while the trained heads use standard CE-based optimization. The gap may reflect optimization pathology (e.g., vanishing gradients for rare classes) rather than an inherent limitation of loss functions. | If true, the bottleneck is engineering (optimizer, learning rate schedule) not algorithmic (loss design), shifting focus to training stability. | Replace the linear probe with a *retrained* classifier head using the same loss but with modified optimization (e.g., rare-class-specific learning rates, gradient clipping) and compare F1. | [Paper] [Paper: PDF p. 6]: “Discriminative signal therefore survives... placing the bottleneck partly in loss design rather than solely in data scarcity.” — authors acknowledge loss design as *part* of bottleneck, leaving room for optimization factors. |
| NC1 is computed on *frozen test-set embeddings*, but the paper claims it “predicts which rare classes will fail regardless of loss choice” [Paper] [Paper: PDF p. 7]. However, NC1 is a static geometric measure; it cannot capture how different losses reshape the embedding manifold during training (e.g., LDAM’s margin may alter Σ<sub>W</sub>/Σ<sub>B</sub>). | NC1 on CE embeddings may not generalize to LDAM or logit-adjusted embeddings. A class with high NC1 under CE might have low NC1 under LDAM, making the “prediction” invalid for losses that actively modify geometry. | Over-reliance on CE-only NC1 could mislead users into abandoning loss engineering for classes that *are* recoverable under geometry-aware losses. | Compute NC1 separately for each (backbone, loss) combination (e.g., scGPT/CE, scGPT/LDAM) and correlate with ∆F1; test if CE-NC1 remains predictive across losses. | [Paper] [Paper: PDF p. 6]: NC1 values reported only for CE embeddings (“under plain CE”, “restricted to MS’s 11 rare classes under plain CE”). No NC1 values shown for other losses. |
| The study uses fixed, globally precomputed training-set statistics for all losses (e.g., class frequencies for weighting). In real-world perturbation prediction, class distributions may shift dynamically (e.g., time-series perturbations), making static statistics suboptimal. | Static weighting assumes stationary class priors, violating the non-stationary nature of many biological perturbations (e.g., drug response kinetics). This could explain why gains are modest on Zheng68K (less imbalanced but more dynamic?). | For user’s perturbation prediction work, static loss functions may need adaptation to temporal or conditional priors. | Implement online estimation of class frequencies during training (e.g., exponential moving average) and benchmark against static version on a simulated time-series perturbation dataset. | [Paper] [Paper: PDF p. 2]: “Every loss under test computes its class-level term from fixed, globally precomputed training-set statistics”. No discussion of non-stationary extensions. |

## 14 学到的知识

- **Loss selection is not one-size-fits-all**: class-balanced loss is the safest default for rare-class recovery, but logit adjustment is a precision-recall dial — useful when false negatives are catastrophic (e.g., missing a pathogenic perturbation state), even if it increases false positives.  
- **Per-class diagnosis beats aggregate metrics**: Reporting a single “rare-class recall” number (e.g., 0.632) obscures whether it’s driven by one recoverable class gaining +0.2 or ten entangled classes stuck at 0.0 — Figure 3’s heatmap and ∆F1 plot are essential for debugging.  
- **Geometry-first debugging works**: Before tuning any hyperparameter, compute NC1 and nearest-neighbor entropy on frozen embeddings — if NC1 > 1.0 and neighbor entropy > 0.85 for a rare class, prioritize data collection or abstention over loss engineering.  
- **Absolute count > relative frequency**: When designing experiments for low-abundance perturbation responses (e.g., < 10 cells), expect diminishing returns from reweighting; invest instead in deeper sequencing or targeted enrichment.  
- **Linear probing is a powerful sanity check**: If a simple logistic regression on frozen embeddings outperforms your fancy fine-tuned head, your bottleneck is likely training instability or head architecture, not the backbone or loss.

## 15 与既有知识的连接

- **Candidate connection / methodological connection**: 该工作与用户研究方向中 **perturbation prediction** 的连接是方法论级的：它提供了一套可即插即用的 loss-function benchmark protocol (162-run grid) and diagnostic toolkit (NC1, ∆F1, linear probe) that can be directly applied to evaluate how well scGPT/scBERT handle rare perturbation states (e.g., “early apoptosis” or “drug-resistant subclone”) without modifying the backbone.  
- **Candidate connection / methodological connection**: 对 **cell state representation** 的启示在于：论文证明“severely entangled”类的失败源于嵌入几何（Figure 4），而非表示能力缺失（linear probe recovers signal），这支持用户采用 post-hoc representation refinement (e.g., prototype-guided alignment [Weerasekara et al. 2026]) rather than discarding the foundation model.  
- **Candidate connection / methodological connection**: 与 **graph neural networks** 的潜在接口在于：论文中 nearest-neighbor absorption (e.g., phagocyte → oligodendrocyte A) resembles graph neighborhood mixing; future work could replace k-NN with GNN-based neighborhood aggregation to mitigate absorption.  
- **Weak connection / methodological connection**: 与 **spatial transcriptomics** 和 **multi-omics** 的连接目前为弱连接 —— 论文未涉及空间坐标或多组学模态，但其核心诊断框架（geometry-first, per-class ∆F1）可迁移；例如，在 spatial data中，可定义“spatially rare”类（e.g., niche-specific cells）并计算 spatial-NC1。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Dynamic Loss Scheduler for Perturbation Time Series  
  **originating limitation/observation**: Static, globally precomputed class weights fail under non-stationary perturbation dynamics [Paper] [Paper: PDF p. 2]  
  **core hypothesis**: Online estimation of class frequencies (e.g., exponential moving average over time bins) will improve rare-perturbation recall in time-series scRNA-seq.  
  **delta from paper**: Replaces fixed statistics with adaptive, temporal statistics; integrates with existing loss families (e.g., class-balanced loss with EMA weights).  
  **initial method**: On simulated perturbation time series (e.g., 0h/6h/24h drug treatment), compute class frequency per time bin, apply EMA (α=0.9), use smoothed frequencies for loss weighting.  
  **validation**: Compare rare-class recall of dynamic vs. static weighting on time-series benchmarks (e.g., Perturb-seq datasets); ablate α.  
  **failure modes**: Over-smoothing (α too high) masks rapid transitions; under-smoothing (α too low) adds noise.  
  **innovation status**: unverified  

- **name**: Geometry-Guided Loss Selection  
  **originating limitation/observation**: NC1 computed only on CE embeddings may not predict performance under geometry-modifying losses like LDAM [Analysis]  
  **core hypothesis**: A lightweight geometric predictor (e.g., NC1 + neighbor entropy) trained on CE embeddings can forecast which loss will maximize ∆F1 for a given rare class.  
  **delta from paper**: Moves from descriptive diagnosis (NC1 tells you *if* a class is hard) to prescriptive recommendation (NC1 + entropy tells you *which loss* to pick).  
  **initial method**: Extract NC1 and normalized neighbor entropy for all rare classes in MS/ Zheng68K/ Pancreas under CE; train a small MLP to predict best-loss rank (1–6) from these two features.  
  **validation**: Test predictor on held-out rare classes; measure accuracy of top-2 loss recommendation.  
  **failure modes**: Poor generalization to new datasets with different geometric distributions; fails if NC1/entropy are collinear.  
  **innovation status**: unverified  

- **name**: Entanglement-Aware Abstention  
  **originating limitation/observation**: Severely entangled classes (e.g., oligodendrocyte C) have near-zero F1 but non-zero linear probe F1, indicating signal exists but is hard to extract [Paper] [Paper: PDF p. 6]  
  **core hypothesis**: An ensemble of linear probes (one per rare class) on frozen embeddings can serve as a low-cost, high-recall “abstention gate”: if probe F1 < threshold, defer prediction to expert review or data augmentation.  
  **delta from paper**: Turns linear probe from a diagnostic tool into an operational safety mechanism.  
  **initial method**: For each rare class c, train class-balanced logistic probe on frozen CE embeddings; at inference, compute probe confidence; if confidence < 0.3, output “ABSTAIN”.  
  **validation**: Measure abstention rate vs. rare-class recall gain on test set; compare F1 of “abstain + human review” pipeline vs. full automation.  
  **failure modes**: High abstention rate on borderline cases; probe confidence poorly calibrated for out-of-distribution samples.  
  **innovation status**: unverified