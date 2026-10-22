> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods/discovery  
> Secondary analytical lens: resource  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions | [Paper] [Paper: PDF p. 1] |
| Authors | Zeyu Dong, Jiahui Zhong | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (v1) | [Paper] [Paper: PDF p. 1] |
| URL | https://arxiv.org/abs/2609.23325 | [Input metadata] |
| PDF URL | https://arxiv.org/pdf/2609.23325v1 | [Input metadata] |
| Publication date | 2026-09-22 | [Input metadata] |
| Code availability | https://github.com/jz890/sc-imbalance (stated in [Paper] [Paper: PDF p. 7]) | [Paper] [Paper: PDF p. 7] |
| Data availability | Not explicitly stated; datasets named (MS, Zheng68K, Pancreas) but no URLs or accession IDs provided | Not assessable from supplied material |
| Pretrained models | scGPT (Cui et al. 2024), scBERT (Yang et al. 2022), Geneformer (Theodoris et al. 2023) | [Paper] [Paper: PDF p. 2–3] |
| Datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 2–3] |
| Loss functions benchmarked | Cross-entropy (CE), weighted CE, class-balanced loss (Cui et al. 2019), focal loss (Lin et al. 2017), LDAM (Cao et al. 2019), logit-adjusted softmax (Menon et al. 2021) | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结

该论文系统评估了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/ Zheng68K/ Pancreas）上的表现，揭示出“罕见细胞类型失败”并非单一现象，而是分裂为两类可诊断机制：一类是**损失敏感型**（loss-sensitive），其性能可通过重加权类损失显著提升；另一类是**严重纠缠型**（severely entangled），即使更换所有损失函数与架构也无法恢复，根源在于训练样本绝对数量过少（如仅3个细胞）与嵌入空间几何结构坍缩（如NC1异常、邻域吸收）。论文由此提出首个可复用的长尾基准框架，并给出基于嵌入几何（如NC1、最近邻混淆模式）的事前诊断指南——而非盲目尝试损失函数。

## 03 研究问题

论文直面一个被高精度指标掩盖的关键矛盾：单细胞基础模型在细胞类型分类任务中报告高达97.5%的总体准确率，但这一数字无法反映其对**疾病相关罕见细胞亚群**（如MS中的oligodendrocyte C、phagocyte）的系统性失效 [Paper] [Paper: PDF p. 1]。作者追问：这种失效是否源于预训练偏差？能否通过损失函数层面的干预统一解决？若不能，其边界与机制是什么？进一步，哪些损失函数最稳健？其有效性是否依赖于特定架构或数据集结构？这些问题共同指向一个核心科学判断：**长尾问题在单细胞基础模型中不是同质化挑战，而需按失效机制分层建模与干预**。

## 04 研究背景与发展路径

单细胞基础模型（scGPT等）已成为细胞类型注释默认主干，但已有研究（Alsabbagh et al. 2023；Naziri et al. 2025）已指出其在罕见/疾病亚群上性能骤降，且该问题无法被采样策略（如随机过采样）完全解决 [Paper] [Paper: PDF p. 1–2]。现有长尾学习方法（如focal loss、LDAM）多在CV领域验证，其在单细胞语境下的跨架构鲁棒性、与预训练表示的耦合关系、以及对生物特异性失效（如病理亚群转录相似性）的适配性均未系统检验 [Paper] [Paper: PDF p. 1–2]。本文承接Alsabbagh等人的采样轴工作，将研究维度推进至**损失函数轴**，并首次引入**嵌入几何诊断**（neural collapse, nearest-neighbor absorption）作为失效归因工具，从而将经验性调参升级为机制驱动的干预设计。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **Aggregated metrics mask rare-class failure** | Overall accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 3] | Dataset imbalance structure—not pretraining—drives the gap; rare classes are systematically underserved despite high aggregate scores [Paper] [Paper: PDF p. 1, 3] | Figure 2 (left): Pancreas has highest accuracy but largest accuracy-to-rare-recall drop; MS shows greatest reweighting benefit despite comparable imbalance ratio to Zheng68K [Paper] [Paper: PDF p. 3–4] |
| **Loss-level interventions are not universally effective** | Two rare classes (oligodendrocyte C, phagocyte in MS) achieve near-zero F1 under *all* six losses and *all* three backbones [Paper] [Paper: PDF p. 5] | Insufficient training samples (n=3 each) prevent learning discriminative representations; geometric signatures (NC1, neighbor absorption) confirm embedding-space collapse [Paper] [Paper: PDF p. 5–6] | Figure 3 (left): two darkest rows show near-zero F1 across all three backbone columns; Figure 4: UMAP shows 116 test cells of these classes absorbed into unrelated clusters under both CE and LDAM [Paper] [Paper: PDF p. 5, 7] |
| **Reweighting efficacy is misattributed to relative frequency** | Weighted CE performs best on MS (most imbalanced by ratio), yet worst on Zheng68K (less imbalanced) [Paper] [Paper: PDF p. 3–4] | Absolute training-set size—not class share or dataset imbalance ratio—predicts reweighting gain (r = −0.77, p < 0.001) [Paper] [Paper: PDF p. 4] | Figure 3 (right): ∆F1 strongly negatively correlated with log(training-set size); MS rare classes have smallest absolute counts, explaining its largest gain (+9.9%) [Paper] [Paper: PDF p. 4] |
| **Loss functions make hidden trade-offs obscured by Macro-F1** | Logit adjustment achieves highest rare-class recall on Zheng68K (0.685) but lowest rare-class precision among all six losses [Paper] [Paper: PDF p. 4] | It shifts decision thresholds rather than improving feature separability, increasing false positives [Paper] [Paper: PDF p. 4] | Figure 2 (right): logit-adjusted point lies far below y=x line; Table 1 shows its rare-class precision is lowest (0.632 vs. class-balanced’s 0.685) [Paper] [Paper: PDF p. 4, 5] |

## 06 核心思想

论文的核心洞见是：**单细胞长尾失效存在结构性二分法，必须解耦为“可优化”与“不可优化”两类问题**。前者（loss-sensitive）源于损失函数对少数类梯度的压制，可通过重加权（如class-balanced loss）或边界调整（LDAM）缓解；后者（severely entangled）则根植于数据稀缺导致的嵌入几何坍缩——即使最优损失也无法从3个样本中学习鲁棒表征，此时瓶颈不在优化目标，而在数据本身或分类器设计。因此，论文主张将“选择损失函数”升级为“诊断失效机制”：先用NC1、最近邻混淆等几何指标筛查严重纠缠类，再对剩余类施加损失优化。这一思想将长尾问题从统计偏差修正，转向对**表示空间拓扑完整性**的诊断与修复。

## 07 方法总览

论文采用**控制变量+多维诊断**范式：固定数据划分、预处理、微调协议（除scBERT冻结策略外），系统遍历3 backbone × 3 dataset × 6 loss × 3 seed = 162次训练；评估指标覆盖宏观（accuracy, Macro-F1）、罕见类专属（rare-class recall/precision/AUPRC）及几何（NC1, nearest-neighbor entropy）；诊断路径为三阶递进：(1) 统计失效（Figure 2/3）→ (2) 几何归因（Figure 4, Equation 4, Section 5.2）→ (3) 信号定位（linear probe in Section 5.3）。关键创新在于将神经坍缩理论（Papyan et al. 2020）的NC1指标直接应用于冻结测试嵌入，使其成为事前可计算的失效预警信号，而非事后解释工具。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-------------------------------------|
| **Loss-function grid** | Systematically compare six long-tail losses (CE, weighted CE, class-balanced, focal, LDAM, logit-adjusted) | To isolate loss-level effects from architecture/dataset confounds and identify most robust choices | Input: logits + labels; Output: scalar loss per sample | Table 1 reports Macro-F1/rare-recall per loss; Figure 2 (right) plots precision-recall trade-offs [Paper] [Paper: PDF p. 3–5] | Without this grid, claims about "class-balanced loss being most consistent" (mean rank 2.4) would be unsubstantiated [Paper] [Paper: PDF p. 3] |
| **Embedding geometry analyzer** | Compute NC1 (Equation 4), nearest-neighbor confusion patterns, and linear probe F1 on frozen embeddings | To distinguish data-scarcity-driven failure (geometric collapse) from optimization-driven failure (suboptimal loss) | Input: frozen test-set embeddings + true labels; Output: NC1 scalar, confusion matrix, probe F1 | Figure 4 visualizes absorption; Equation 4 defines NC1; Section 5.2–5.3 report NC1 values (e.g., oligodendrocyte C: 1.19–1.79) and probe gains (e.g., +13.6 F1 points) [Paper] [Paper: PDF p. 6–7] | Removing this module would conflate "unrecoverable" and "loss-sensitive" classes, invalidating the two-regime conclusion [Paper] [Paper: PDF p. 5] |
| **Rare-class definition & filtering** | Define rare classes as those with <5% training frequency; exclude classes with mean F1<0.2 under best loss for regression | To separate severely entangled classes (floor performance) from recoverable ones for clean correlation analysis | Input: training-set class counts; Output: set R of rare classes, filtered subset for ∆F1 regression | Section 3 defines R; Section 4.3 excludes n=4 classes with mean F1<0.2 before computing r=−0.77 correlation [Paper] [Paper: PDF p. 3, 4] | Without filtering, the ∆F1 vs. size correlation weakens (r=−0.53), obscuring the core predictive relationship [Paper] [Paper: PDF p. 4] |
| **Cross-architecture agreement checker** | Analyze misclassification patterns across scGPT/scBERT/Geneformer for same rare classes | To confirm failure is data-driven (transcriptional overlap) not architecture-specific artifact | Input: per-backbone confusion matrices; Output: dominant confusion partners (e.g., phagocyte→oligodendrocyte A) | Section 5.2: "Oligodendrocyte A and mixed glial type jointly account for 91–97% of all phagocyte misclassifications across all three backbones" [Paper] [Paper: PDF p. 6] | Without cross-architecture validation, observed confusion could be dismissed as scGPT-specific bug, not biological signal [Paper] [Paper: PDF p. 6] |

## 09 关键公式与符号

- **No verifiable closed-form equations are presented in the paper.** All equation identifiers (Equation 1–4) are fragments embedded in text without full derivation or standalone presentation.
- Key symbols/variables extracted:
  - `C`: total number of classes [Paper] [Paper: PDF p. 3]
  - `R ⊆ {1,…,C}`: set of rare classes (training frequency <5%) [Paper] [Paper: PDF p. 3]
  - `F1,c`: F1 score for class `c` [Paper] [Paper: PDF p. 3]
  - `Recallc`: recall for class `c` [Paper] [Paper: PDF p. 3]
  - `∆F1,c = max_ℓ∈L F^(ℓ)_1,c − F^(CE)_1,c`: gain in class-c F1 from best loss over CE [Paper] [Paper: PDF p. 4, Eq. 3]
  - `NC1 = tr(ΣW)/tr(ΣB)`: neural collapse trace ratio; ΣW = avg within-class scatter, ΣB = between-class scatter of centroids [Paper] [Paper: PDF p. 6, Eq. 4]
  - `AUPRC`: area under precision-recall curve, macro-averaged over rare classes [Paper] [Paper: PDF p. 3]
- Metrics reported: Accuracy, Macro-F1 (Eq. 1), rare-class recall (Eq. 2), rare-class precision, rare-class macro-AUPRC.

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|-------------------------|----------------------------------|--------|
| **162-run benchmark** | Which loss function is most robust across architectures and datasets? | 3 backbones × 3 datasets × 6 losses × 3 seeds; all other hyperparameters fixed per backbone [Paper] [Paper: PDF p. 2–3] | Class-balanced loss (mean rank 2.4) and LDAM (2.6) most consistent; weighted CE best on MS (0.721), LDAM best on Pancreas (0.819) [Paper] [Paper: PDF p. 3, Table 1] | Class-balanced loss and LDAM are top-tier generalists for rare-class recovery | That either loss is universally superior—weighted CE outperforms both on MS Macro-F1 [Paper] [Paper: PDF p. 3, Table 1] | [Paper] [Paper: PDF p. 3, Table 1] |
| **∆F1 vs. training size regression** | Does absolute sample count predict reweighting gain better than relative frequency? | Correlate ∆F1,c (Eq. 3) with log(training-set size) for all rare classes; exclude floor-performance classes (n=4) [Paper] [Paper: PDF p. 4] | Strong negative Pearson correlation (r=−0.77, p<0.001, n=19); robust to exclusion thresholds [Paper] [Paper: PDF p. 4, Figure 3 (right)] | Absolute training-set size—not imbalance ratio—drives reweighting efficacy | That this holds for *all* rare classes—excluded 4 severely entangled classes show no such trend [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4, Figure 3 (right)] |
| **UMAP + linear probe on frozen embeddings** | Is discriminative signal present for severely entangled classes? | Fit class-balanced logistic regression on frozen CE-fine-tuned embeddings (5-fold CV); compare to best trained classifier F1 [Paper] [Paper: PDF p. 6] | Probe recovers non-trivial F1 (0.175–0.465) exceeding best trained classifier (0.000–0.329) for oligodendrocyte C/phagocyte [Paper] [Paper: PDF p. 6] | Signal exists in representation but is unused by current loss+classifier pipelines | That a nonlinear probe would close the gap—no test of nonlinear classifiers performed [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6] |
| **NC1 computation on rare classes** | Does neural collapse geometry differ between severely entangled and other rare classes? | Compute NC1 (Eq. 4) on MS rare classes’ frozen CE embeddings across all three backbones [Paper] [Paper: PDF p. 6] | Oligodendrocyte C shows high NC1 (1.19–1.79, 2nd highest); phagocyte shows low NC1 (0.17–0.32, 8th of 11) [Paper] [Paper: PDF p. 6] | NC1 distinguishes geometric failure modes: oligodendrocyte C lacks tight clustering; phagocyte suffers from small-sample absorption | That NC1 alone suffices for diagnosis—phagocyte requires nearest-neighbor entropy to reveal concentrated absorption [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6, Eq. 4] |

## 11 对结论的正确理解

- “Class-balanced loss is most consistent” means it ranks near the top across *all nine* (backbone, dataset) combinations—not that it wins every column (weighted CE wins MS Macro-F1; LDAM wins Pancreas Macro-F1) [Paper] [Paper: PDF p. 3, Table 1].
- “Severely entangled classes are unrecoverable” refers specifically to the *six evaluated losses* and *three architectures*; it does not preclude recovery via other methods (e.g., generative replay [Li et al. 2026], contrastive learning [Zhai et al. 2024], or decoupled calibration [Kang et al. 2020]) [Paper] [Paper: PDF p. 5, 7].
- “Absolute training-set size predicts reweighting gain” is an empirical correlation (r=−0.77) for *recoverable* rare classes—not a causal law applicable to all regimes [Paper] [Paper: PDF p. 4]. The four severely entangled classes (n=3 samples) lie outside this trend.
- “Logit adjustment trades precision for recall” is demonstrated *only for rare classes*; non-rare class precision/recall vary by <2.1 points across losses, confirming the trade-off is rare-class specific [Paper] [Paper: PDF p. 4].

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|----------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer tested; scFoundation and CellPLM untested [Paper] [Paper: PDF p. 7] | Extend benchmark to other existing single-cell foundation models (scFoundation, CellPLM) [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Classifier expressivity ceiling** | Linear probe on frozen embeddings recovers signal unused by trained heads, suggesting current losses+linear heads may be suboptimal [Paper] [Paper: PDF p. 6] | Test more expressive, nonlinear classifier heads beyond the six losses evaluated [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Isolated imbalance axis** | Study focuses solely on cell-type class imbalance; ignores compounding variables like demographic composition or batch effects [Paper] [Paper: PDF p. 7] | Investigate interactions between cell-type imbalance and demographic composition (Al Amin et al. 2025) or batch effects (Maan et al. 2024) [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|---------------------------------------------|----------------|----------------|-------|
| The paper attributes phagocyte’s misclassification to "ingested myelin/oligodendrocyte RNA" (Schirmer et al. 2019), but this biological explanation is not validated against gene expression profiles (e.g., myelin gene enrichment in phagocyte vs. oligodendrocyte A) | Misclassification could stem from technical artifacts (e.g., ambient RNA contamination during droplet-based sequencing) rather than true transcriptional overlap | Confusing technical noise with biology risks misdirecting therapeutic targeting or data curation efforts | Re-analyze raw counts (not HVG-filtered) for phagocyte: quantify % reads mapping to myelin genes (e.g., MBP, PLP1) and compare to oligodendrocyte A; simulate ambient RNA contamination to see if it reproduces absorption pattern | [Paper] [Paper: PDF p. 6] cites Schirmer et al. 2019 for biological interpretation but provides no direct transcriptomic evidence in this work |
| NC1 is computed only on *frozen test-set embeddings*, yet the paper uses it to diagnose *training-data scarcity*. However, NC1 reflects final representation geometry, which integrates both pretraining and fine-tuning effects | High NC1 for oligodendrocyte C could arise from poor pretraining (e.g., insufficient myelin-related context in scGPT’s corpus) rather than just n=3 training samples | Attributing failure solely to data scarcity overlooks opportunities to improve pretraining for disease-relevant states | Fine-tune scGPT on a synthetic MS lesion dataset (enriched for myelin/phagocytosis genes) and recompute NC1 for oligodendrocyte C; if NC1 drops, pretraining matters | [Paper] [Paper: PDF p. 6] computes NC1 post-fine-tuning but interprets it as evidence of training-data insufficiency without isolating pretraining contribution |
| The linear probe uses *class-balanced logistic regression*, but the paper does not test whether standard (unbalanced) logistic regression or SVMs yield different recovery rates for severely entangled classes | Class-balancing in the probe itself may artificially inflate apparent signal detectability, masking true linear separability limits | Overstating residual signal could delay adoption of necessary architectural changes (e.g., contrastive learning) | Run identical linear probes with unbalanced logistic regression and RBF-SVM; compare F1 gain over trained heads; if gains vanish, class-balancing—not signal—is the driver | [Paper] [Paper: PDF p. 6] specifies "class-balanced logistic regression" for probes but doesn’t justify this choice or test alternatives |

## 14 学到的知识

- **长尾失效必须分层诊断**：不能只看Macro-F1或accuracy；需结合罕见类专属指标（recall/precision/AUPRC）与嵌入几何（NC1、最近邻熵）区分“可优化”与“不可优化”两类。
- **绝对样本量比相对频率更关键**：对可优化类，重加权收益由训练集绝对大小（而非占比）决定——这提示在数据收集阶段应优先补足绝对数量极低的类（如<10 cells），而非追求整体平衡。
- **损失函数有隐性trade-off**：Macro-F1 hides precision-recall conflicts; logit adjustment boosts recall at precision cost, while class-balanced loss improves both—choosing requires clinical context (e.g., false negative cost > false positive cost).
- **几何指标可事前预警**：NC1和最近邻混淆模式在CE训练后即可计算，无需重训所有损失；它们是比重新训练更快的失效筛查工具。
- **信号存在≠被利用**：线性探针在冻结嵌入上恢复性能，证明当前损失+分类器组合未充分利用表示能力——这为解耦表示学习与分类器校准（Kang et al. 2020）提供了强实证支持。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的“嵌入几何诊断”（NC1, nearest-neighbor absorption）与计算机视觉中神经坍缩（neural collapse）理论（Papyan et al. 2020）、不平衡学习的几何分析（Fang et al. 2021）形成跨领域呼应，但首次将其锚定于单细胞生物学语境下的病理亚群。
- **候选连接/方法论连接**：线性探针验证残余信号的思路，直接继承自Alain & Bengio (2017)，但本文将其用于诊断长尾瓶颈，而非仅解释中间层功能。
- **候选连接/方法论连接**：将“绝对样本量”作为预测因子，呼应通用长尾学习中的effective-number-of-samples框架（Cui et al. 2019）和医学影像研究（Buda et al. 2018），但首次在单细胞基础模型上实证。
- **弱连接/方法论连接**：与用户研究方向中“cell state representation”和“perturbation prediction”存在方法论接口——本文揭示的几何坍缩（如oligodendrocyte C的高NC1）可能泛化至扰动响应状态空间，提示需在扰动建模中显式约束嵌入几何。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometry-Guided Data Augmentation for Severely Entangled Classes  
  **originating limitation/observation**: Severely entangled classes (e.g., oligodendrocyte C, n=3) fail due to geometric collapse (high NC1, neighbor absorption), and linear probes confirm signal exists but is unused [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: Synthetic augmentation that preserves the *embedding geometry* of the dominant confusion partner (e.g., oligodendrocyte A) will teach the classifier to disentangle transcriptionally overlapping states without introducing artificial signals.  
  **delta from paper**: Paper identifies the problem and confirms signal exists; this idea proposes a geometry-aware augmentation strategy instead of accepting data scarcity as fatal.  
  **initial method**: Use scGPT’s frozen encoder to embed oligodendrocyte A cells; apply PCA to their embedding subspace; generate synthetic oligodendrocyte C cells by perturbing oligodendrocyte A embeddings along directions orthogonal to the oligodendrocyte A centroid-subspace, scaled by the distance to phagocyte’s centroid.  
  **validation**: Train class-balanced loss on augmented MS dataset; measure ∆F1 for oligodendrocyte C vs. baseline (no aug) and vs. SMOTE; compute NC1 reduction.  
  **failure modes**: Augmentation may amplify ambient RNA artifacts; orthogonality constraint may not capture true biological transition paths.  
  **innovation status**: unverified  

- **name**: NC1-Aware Loss Scheduling  
  **originating limitation/observation**: NC1 is computed post-hoc on frozen embeddings, but loss choice is made pre-training; no mechanism links geometry to dynamic loss adaptation [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: Monitoring NC1 *during training* (on validation embeddings) enables adaptive loss switching—e.g., start with CE, switch to LDAM when NC1 exceeds threshold, then to logit adjustment if recall plateaus.  
  **delta from paper**: Paper uses NC1 for *diagnosis*; this idea uses it for *online control* of optimization dynamics.  
  **initial method**: Compute NC1 on validation embeddings every 2 epochs; define thresholds τ₁ (switch to LDAM), τ₂ (switch to logit adjustment); implement in PyTorch Lightning callback.  
  **validation**: Compare final rare-class F1 and training stability (epoch-to-epoch NC1 variance) against fixed-loss baselines on MS dataset.  
  **failure modes**: NC1 estimation noise on small validation sets may trigger premature switching; thresholds may not generalize across datasets.  
  **innovation status**: unverified  

- **name**: Cross-Dataset Entanglement Transfer  
  **originating limitation/observation**: Severely entangled classes recur across datasets (MS, Zheng68K, Pancreas) with similar geometric signatures (e.g., low sample count + high NC1) [Paper] [Paper: PDF p. 5, Figure 3 (right)] — suggesting shared failure mechanisms.  
  **core hypothesis**: Entanglement patterns (e.g., phagocyte↔oligodendrocyte A absorption) learned on one dataset can be transferred as *geometric priors* to improve rare-class recovery on another, even without shared cell types.  
  **delta from paper**: Paper observes cross-dataset recurrence but treats datasets in isolation; this idea exploits recurrence for knowledge transfer.  
  **initial method**: Extract the nearest-neighbor confusion matrix for severely entangled classes on MS; use it to regularize the classifier head’s weight matrix on Zheng68K (e.g., penalize logits for classes that are top-2 neighbors in MS).  
  **validation**: Measure ∆F1 for rare classes on Zheng68K with/without MS-derived regularization; ablate by shuffling the MS confusion matrix.  
  **failure modes**: Confusion patterns may be dataset-specific (e.g., driven by platform effects); regularization may over-constrain non-entangled classes.  
  **innovation status**: unverified