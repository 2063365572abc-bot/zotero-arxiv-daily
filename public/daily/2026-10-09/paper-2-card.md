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
| Datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 2–3] |
| Backbones | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 2] |
| Losses benchmarked | Cross-entropy (CE), weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |
| Rare-class definition | Training-split frequency < 5% per domain experience | [Paper] [Paper: PDF p. 3] |

## 02 一句话总结

该论文系统性地评测了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/ Zheng68K/Pancreas）上的表现，发现：整体准确率严重掩盖罕见细胞类型的失败，而这种失败可被划分为两类机制——**损失敏感型**（可通过损失函数选择显著改善）与**严重纠缠型**（所有损失均失效，根源于嵌入几何结构与极低样本量）；其中，**绝对训练样本数而非相对频率**是预测重加权收益的关键指标，且**class-balanced loss 和 LDAM 是最稳健的选择**。该工作不追求新模型，而是为单细胞基础模型在临床相关稀有细胞类型上的可靠部署提供了可复现的基准、可解释的几何判据与实操指南。

## 03 研究问题

论文直面一个被广泛忽视但临床关键的矛盾：单细胞基础模型（scFM）在细胞类型注释任务中报告高达97.5%的总体准确率，却系统性地在罕见、疾病相关细胞亚群上失效；而当前主流假设——“换一个长尾损失函数即可缓解”——缺乏跨架构、跨数据集的实证支撑。因此，核心问题有三：（1）不同长尾损失函数在固定预训练scFM上的有效性是否一致？是否存在普适最优解？（2）罕见类失败是统一现象，还是存在不同成因的子类型？能否在训练前识别其可修复性？（3）影响损失函数收益的关键因素是什么——是数据集整体不平衡比、罕见类占比，还是更底层的样本绝对数量或嵌入几何特性？这些问题共同指向一个方法论缺口：缺乏机制驱动的、损失函数层面的系统性基准。

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer等）已成为细胞类型注释默认主干，但其高聚合准确率被常见细胞类型主导，罕见细胞（如早期病理态、过渡态）常被忽略 [Paper] [Paper: PDF p. 1]。此前工作已确认该问题：Alsabbagh et al. (2023) 在采样策略层面验证随机过采样最稳健；Naziri et al. (2025) 在AML数据上揭示健康预训练偏差导致复发样本F1骤降；Al Amin et al. (2025) 指出人群构成失衡亦影响微调效果 [Paper] [Paper: PDF p. 1–2]。然而，这些研究聚焦于数据分布或预训练偏差，**未隔离损失函数这一独立干预轴**。本文承接此空白，将长尾学习中成熟的损失族（Cui et al. 2019; Lin et al. 2017; Cao et al. 2019; Menon et al. 2021）首次系统引入scFM场景，通过控制变量法（固定backbone fine-tuning protocol、固定基因面板、固定split）剥离其他混杂因素，从而纯化损失函数效应，建立首个scFM长尾损失基准。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **Aggregate metrics mask rare-class failure** | Accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 4] | Dataset imbalance structure dominates over backbone architecture or pretraining bias | Figure 2 (left): consistent gap under plain CE; text states “gap is present regardless of which foundation model is used” [Paper] [Paper: PDF p. 4] |
| **Loss-level interventions are not universally effective** | Two rare classes (oligodendrocyte C, phagocyte) show near-zero F1 under *all* six losses and *all* three backbones on MS [Paper] [Paper: PDF p. 5] | Insufficient training samples (n=3) + transcriptional overlap → embedding geometry collapse, not classifier calibration failure | Figure 3 (left): two darkest rows; Section 5.1: “both have only 3 training examples”; Figure 4: UMAP shows absorption into unrelated classes; Section 5.3: linear probe recovers signal, confirming bottleneck is in classifier head, not representation [Paper] [Paper: PDF p. 5–7] |
| **Reweighting benefit is misattributed to relative frequency** | Weighted CE performs best on MS (most imbalanced by ratio), but worst on Zheng68K (less imbalanced ratio) despite similar relative rarity [Paper] [Paper: PDF p. 4] | Absolute training-set size, not relative share or dataset imbalance ratio, predicts ∆F1 gain | Figure 3 (right): strong negative Pearson correlation (r = −0.77, p < 0.001) between log(training size) and ∆F1,c; Section 4.3 explicitly states “absolute training-set size, rather than its share… predicts reweighting benefit” [Paper] [Paper: PDF p. 4] |
| **Loss functions make hidden trade-offs obscured by Macro-F1** | Logit adjustment achieves highest rare-recall on Zheng68K but has lowest rare-precision among all six losses [Paper] [Paper: PDF p. 4] | It shifts decision threshold rather than improving feature separability → more false positives | Figure 2 (right): logit-adjusted point lies far below y=x line; Section 4.4: “achieves its recall gains primarily by shifting the decision threshold” [Paper] [Paper: PDF p. 4] |

## 06 核心思想

论文的核心洞见是：**单细胞长尾失败不是单一问题，而是一个具有可诊断几何签名的二分现象**。作者观察到，罕见类失败并非均匀分布，而是自然聚类为两个机制迥异的子集：一类（如microglial cell）对损失函数高度敏感，其性能可随loss选择从F1=0跃升至>0.8，表明瓶颈在于分类器优化不足；另一类（oligodendrocyte C/phagocyte）则在所有loss和backbone下均崩溃，其测试嵌入在UMAP中被完全吸收进无关类簇（Figure 4），且线性探针能恢复部分F1（Section 5.3），证明信号尚存但现有loss无法利用——这指向损失函数设计本身存在结构性盲区。由此，作者提出一个**诊断先行（diagnosis-first）范式**：先用NC1比值、最近邻混淆模式等嵌入几何指标，在训练前识别“严重纠缠类”，再决定是投入数据采集（data-centric）还是探索新loss（model-centric）。这一思想将长尾问题从“如何选loss”的经验主义，升级为“何时需loss、何时需数据”的机制驱动决策。

## 07 方法总览

本研究采用**全因子控制实验设计**：3个backbone（scGPT/scBERT/Geneformer）× 3个dataset（MS/Zheng68K/Pancreas）× 6个loss（CE/weighted CE/class-balanced/focal/LDAM/logit-adjusted）× 3个seed = 162次独立训练。所有实验严格控制变量：（1）基因面板统一为top-3000 HVG，基于训练集计算并固定应用于测试集；（2）fine-tuning protocol按各backbone原始设定执行（如scBERT冻结大部分encoder）；（3）batch size、optimizer、lr等超参沿用Alsabbagh et al. (2023) 的per-backbone协议；（4）loss计算依赖全局预计算的训练集统计量，与batch composition无关。评估指标聚焦于**罕见类特异性度量**：Macro-F1（Eq. 1）、罕见类召回率Recall_R（Eq. 2）、罕见类宏平均AUPRC，并辅以每类∆F1（Eq. 3）进行细粒度归因。诊断分析则引入嵌入几何量化工具：NC1比值（Eq. 4）衡量类内/类间散度，结合UMAP可视化（Figure 4）与最近邻混淆分析，实现失败机制的可解释解耦。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **Rare-class geometric diagnostic module** | Computes NC1 ratio (Eq. 4) and nearest-neighbor confusion patterns on frozen test embeddings *before* loss selection | To distinguish "loss-sensitive" vs. "severely entangled" rare classes *a priori*, enabling targeted intervention | Input: frozen test embeddings (e.g., scGPT/CE); Output: NC1 scalar per class, ranked confusion partners | Figure 4 (UMAP absorption), Section 5.2 (NC1 values: oligodendrocyte C high, phagocyte low), Section 5.1 (cross-backbone confusion agreement) [Paper] [Paper: PDF p. 5–6] | Without this, practitioners would waste compute on loss tuning for fundamentally unfixable classes (e.g., n=3 samples), misallocating effort; benchmark would lack mechanistic insight. |
| **Per-class ∆F1 regression module** | Correlates each rare class’s F1 gain from best loss over CE (∆F1,c, Eq. 3) with its absolute training-set size | To test whether reweighting benefit stems from relative frequency (common assumption) or absolute scarcity (novel hypothesis) | Input: per-class ∆F1,c vector, per-class training count vector; Output: Pearson r and p-value | Figure 3 (right): strong negative correlation (r=−0.77); Section 4.3 conclusion: “absolute training-set size… predicts reweighting benefit” [Paper] [Paper: PDF p. 4] | If removed, the paper could not refute the dominant "relative frequency" narrative and would miss the key design principle for loss selection (e.g., prioritize classes with <10 samples). |
| **Linear probe module** | Fits class-balanced logistic regression on *frozen* test embeddings to assess intrinsic separability of severely entangled classes | To determine if failure is due to absent signal (data scarcity) or unused signal (loss limitation) | Input: frozen test embeddings + true labels; Output: CV-F1 score for probe vs. trained classifier | Section 5.3: probe F1 > best trained F1 for oligodendrocyte C/phagocyte (e.g., scGPT/oligodendrocyte C: probe 0.465 vs. best trained 0.329); text states “discriminative signal therefore survives” [Paper] [Paper: PDF p. 6] | Without probe, the claim that “bottleneck is partly in loss design” would be unsupported speculation; it provides causal evidence that current losses are suboptimal, not just insufficient data. |
| **Loss-function comparison module** | Reports mean rank of each loss across all 9 (backbone, dataset) cells, plus rare-class precision/recall trade-off plot (Figure 2 right) | To identify robust generalists (high rank consistency) vs. specialists (high peak but volatile), and expose trade-offs masked by Macro-F1 | Input: 9×3=27 F1/recall scores per loss; Output: mean rank table (Table 1), precision-recall scatter | Table 1: class-balanced (rank 2.4) and LDAM (2.6) most consistent; Figure 2 (right): logit-adjusted trades precision for recall [Paper] [Paper: PDF p. 3–4] | Without cross-backbone ranking, conclusions would be dataset-specific (e.g., “LDAM best on Pancreas”) and lack generalizability; without precision-recall plot, the critical trade-off would remain invisible. |

## 09 关键公式与符号

- **Equation 1**: Macro-F1 = $\frac{1}{C}\sum_{c=1}^{C} F1_c$ —— 所有 $C$ 个类别的F1分数的未加权平均；用于评估整体分类质量，但会掩盖罕见类表现 [Paper] [Paper: PDF p. 3]。
- **Equation 2**: Rare-class recall = $\frac{1}{|R|}\sum_{c\in R} \text{Recall}_c$ —— 仅对罕见类集合 $R$（训练频次<5%）计算的宏平均召回率；核心评估指标，直接反映对关键稀有细胞的捕获能力 [Paper] [Paper: PDF p. 3]。
- **Equation 3**: $\Delta F1_c = \max_{\ell\in L} F1^{(\ell)}_c - F1^{(CE)}_c$ —— 罕见类 $c$ 从CE切换至最佳loss所能获得的F1提升；用于量化每个类别的重加权收益，并关联至其绝对训练样本数 [Paper] [Paper: PDF p. 4]。
- **Equation 4**: $NC1 = \frac{\text{tr}(\Sigma_W)}{\text{tr}(\Sigma_B)}$ —— 神经坍缩迹比，$\Sigma_W$ 为类内散度矩阵均值，$\Sigma_B$ 为类间散度矩阵；NC1越小表示类簇越紧致、分离越好；用于几何诊断，如oligodendrocyte C的高NC1（1.19–1.79）表明其嵌入结构松散 [Paper] [Paper: PDF p. 6]。
- **Key symbols**: $C$ = 总类别数；$R$ = 罕见类集合；$L$ = 六种损失函数集合；$F1_c$ = 第$c$类的F1分数；$\text{Recall}_c$ = 第$c$类的召回率；$\Sigma_W$, $\Sigma_B$ = 类内/类间散度矩阵；$NC1$ = 几何判据指标。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|------------------------|----------------------------------|--------|
| **Aggregate metric gap analysis** | Plain CE exhibits consistent performance gap (Accuracy > Macro-F1 > rare-recall) across architectures | Mean of 9 backbone×seed runs per dataset (Figure 2 left) | Gap present for all three datasets, regardless of backbone | Gap is driven by dataset imbalance structure, not backbone-specific artifacts | Gap is *caused* by pretraining bias (authors attribute it to data structure, not pretraining) | [Paper] [Paper: PDF p. 4], Figure 2 (left) |
| **Loss ranking by mean position** | Class-balanced loss and LDAM are the most consistent performers | Rank each loss within each (backbone, dataset) cell, then average rank across all 9 cells | Class-balanced (2.4), LDAM (2.6) top two; weighted CE best on MS but worst overall rank (2.78) | These two losses generalize best across diverse (backbone, dataset) pairs | Either is universally superior to all others on every single setting (Table 1 shows weighted CE best on MS F1) | [Paper] [Paper: PDF p. 3], Table 1 |
| **∆F1 vs. training size correlation** | Absolute training-set size, not relative frequency, predicts reweighting gain | Regress ∆F1,c (Eq. 3) against log(training count) for all rare classes (n=19 recoverable) | Strong negative Pearson r = −0.77, p < 0.001 | Reweighting benefit scales inversely with absolute sample count | This relationship holds for *all* rare classes including severely entangled ones (authors exclude them first, then show robustness with inclusion) | [Paper] [Paper: PDF p. 4], Figure 3 (right) |
| **Logit adjustment precision-recall trade-off** | Logit adjustment improves rare recall at the cost of precision | Plot rare-class precision vs. recall for all six losses (Figure 2 right) | Logit-adjusted point lies far below y=x line; lowest precision among all six | It achieves recall via threshold shift, not improved separability | Its precision penalty is *unavoidable* (no experiment tests modified logit adjustment) | [Paper] [Paper: PDF p. 4], Figure 2 (right) |
| **Linear probe on frozen embeddings** | Severely entangled classes retain discriminative signal unused by trained classifiers | Fit class-balanced logistic regression on frozen test embeddings (5-fold CV) | Probe F1 > best trained F1 for oligodendrocyte C/phagocyte (e.g., scGPT/oligodendrocyte C: 0.465 > 0.329) | Bottleneck is in classifier training/loss design, not representation collapse | A more complex nonlinear probe (e.g., MLP) would close the gap entirely (not tested) | [Paper] [Paper: PDF p. 6], Section 5.3 |

## 11 对结论的正确理解

论文结论必须置于其**严格控制的实验边界**内理解：（1）“class-balanced loss 和 LDAM 最一致”仅指在所评测的3 backbone × 3 dataset × 6 loss组合中，其平均排名最高，**不意味着它们在所有未来scFM或数据集上都最优**；（2）“绝对样本数预测收益”是针对该基准中定义的罕见类（<5%）得出的强相关性，**不否定相对频率在其他场景（如极端长尾）的作用**；（3）“严重纠缠类无法通过loss修复”是基于六种标准loss的实证，**不等于证明任何loss都无法修复**——线性探针的成功恰恰暗示了设计新loss的空间；（4）“几何诊断可预测失败”指NC1和最近邻模式在CE嵌入上即显现，**但该诊断的有效性依赖于backbone产生有意义的嵌入**，若backbone本身坍缩（如所有类嵌入重合），则诊断失效。总之，所有结论都是**条件性、可证伪、面向实践的工程指南**，而非普适数学定理。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer evaluated; other models like scFoundation and CellPLM remain untested | “Other existing single-cell foundation models… remain untested” and call for future evaluation | [Paper] [Paper: PDF p. 7] |
| **Classifier head expressivity ceiling** | Linear probe outperforms trained classifier heads on severely entangled classes, suggesting current loss functions may not fully exploit available signal | “A more expressive, nonlinear classifier head might extract additional signal beyond what the six losses we test currently achieve” | [Paper] [Paper: PDF p. 7] |
| **Isolated imbalance axis** | Study focuses solely on cell-type class imbalance; confounding factors like demographic composition (Al Amin et al. 2025) or batch effects (Maan et al. 2024) are not considered | “Compounding variables such as demographic composition… or batch effects… require future investigation” | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| The paper attributes the uniform failure of oligodendrocyte C/phagocyte to “too few training examples (n=3)” and transcriptional overlap, but does not rule out that their extreme rarity makes them *out-of-distribution* for the pretrained encoder’s tokenization or positional encoding scheme. | Pretrained encoders (e.g., scGPT’s CLS token, Geneformer’s rank-based tokenizer) may be fundamentally biased toward common cell types’ expression patterns; n=3 samples may be insufficient to fine-tune away this bias, even with optimal loss. | If true, the bottleneck is deeper than loss design—it’s in the pretraining objective itself. This would shift focus to pretraining strategies (e.g., rare-cell-aware masking) rather than just loss engineering. | Fine-tune the same backbones on a synthetic dataset where oligodendrocyte C/phagocyte are *abundant* (e.g., 100+ samples) but otherwise identical; if performance recovers, pretraining bias is unlikely; if not, encoder architecture may be the root cause. | [Paper] [Paper: PDF p. 5] notes “failure is not specific to pretrained representations” based on non-foundation baselines failing too, but those baselines operate on raw counts, not learned embeddings—so encoder-specific OOD remains untested. |
| The linear probe uses class-balanced logistic regression on *frozen* embeddings, yet the paper concludes “bottleneck is in classifier training”. However, the probe’s CV-F1 is measured *within the test set*, not on held-out train/test splits, so it conflates separability with generalization. | A high probe CV-F1 could reflect memorization of test-set idiosyncrasies (e.g., batch artifacts) rather than genuine linear separability of the underlying biology. This inflates confidence in the existence of usable signal. | Overstating signal availability could misdirect efforts toward loss redesign when the real issue is data quality or distribution shift. | Repeat the probe with strict train/test split: fit probe only on frozen *train* embeddings, evaluate on frozen *test* embeddings. Compare its F1 to the original CV-F1; a large drop would indicate the CV result was optimistic. | [Paper] [Paper: PDF p. 6] states “5-fold stratified cross-validation *within the frozen test-set embeddings*”, explicitly limiting generalization assessment to test set only. |
| The geometric signature (NC1, nearest neighbors) is computed on CE-fine-tuned embeddings, but the paper uses it to predict failure under *all* losses. Yet LDAM and logit adjustment explicitly modify decision boundaries—could they reshape the embedding manifold? | While losses don’t directly alter frozen embeddings, their gradients during fine-tuning *do* update encoder weights. Thus, LDAM’s margin enforcement or logit adjustment’s bias correction might induce subtle but consequential changes in the final embedding geometry compared to CE. | Relying solely on CE geometry for universal prediction risks missing loss-specific geometric effects, weakening the diagnostic’s universality. | Compute NC1 and nearest-neighbor confusion for *each* loss’s fine-tuned embeddings (e.g., scGPT/LDAM, scGPT/logit-adjusted) and compare to scGPT/CE. If NC1 distributions shift significantly, the CE-only diagnostic is incomplete. | [Paper] [Paper: PDF p. 6] computes NC1 for “MS’s 11 rare classes under plain CE” and compares across backbones, but does not report NC1 for other losses, leaving this unverified. |

## 14 学到的知识

- **诊断优先范式**：在应用任何损失函数前，应先用NC1比值和最近邻混淆分析检查罕见类的嵌入几何——若NC1异常高或混淆模式跨backbone一致，则大概率属于“严重纠缠”，此时损失调优收效甚微，应转向数据增强或主动学习。
- **绝对数量法则**：对于“损失敏感”类，其从重加权中获得的F1增益主要由其**绝对训练样本数**（而非占比）决定；实践中，应优先为训练样本<10的罕见类定制损失，而非盲目应用全局重加权。
- **Trade-off显影术**：Macro-F1是危险的单一指标；必须同步绘制罕见类的precision-recall散点图（Figure 2右），以识别logit adjustment这类“以精度换召回”的损失，避免在临床场景中因高召回率误判其鲁棒性。
- **信号存在性验证**：当某类在所有loss下均失败时，用线性探针在冻结嵌入上测试其可分性——若probe F1显著高于训练模型，证明信号存在，瓶颈在loss/分类器；若probe F1也接近零，则指向数据或预训练根本缺陷。
- **计算效率无负担**：损失级重加权（如class-balanced）引入的计算开销可忽略（<3.2% wall-clock time），远小于backbone选择的影响（scBERT比Geneformer慢18倍），故应无顾虑地将其作为默认选项。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的“损失敏感 vs. 严重纠缠”二分法，与Kang et al. (2020) 提出的“representation learning vs. classifier calibration decoupling”思想高度契合——前者对应calibration可修复，后者对应representation-level failure，而线性探针正是decoupling的实证工具。
- **候选连接/方法论连接**：NC1比值（Eq. 4）直接继承自Papyan et al. (2020) 的神经坍缩理论，并在不平衡学习中被Fang et al. (2021) 等用于分析“minority collapse”，本文将其首次迁移到单细胞嵌入空间，为scFM失败提供理论锚点。
- **候选连接/方法论连接**：将绝对样本数作为重加权收益预测因子，呼应了Cui et al. (2019) 的“effective number of samples”框架，但本文在scFM场景中证实了其比相对频率更具解释力，为该理论提供了新的生物医学证据。
- **候选连接/方法论连接**：UMAP可视化（Figure 4）与混淆模式分析，与Weerasekara et al. (2026) 的“prototype guided post-pretraining”形成方法论互补——后者试图修正嵌入几何，本文则先诊断几何，再决定是否需要此类修正。
- **弱连接/方法论连接**：用户研究方向中的“spatial transcriptomics”和“multi-omics”虽未在本文出现，但其数据天然具有更极端的长尾（如spot-level稀有细胞），本文的诊断框架（NC1, probe）可直接迁移；而“graph neural networks”在单细胞中常用于构建cell-cell graphs，其节点分类同样面临长尾，本文的loss benchmark设计可复用。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometry-Guided Loss Synthesis for Severely Entangled Classes  
  **originating limitation/observation**: Linear probe recovers signal on frozen embeddings of severely entangled classes, but no evaluated loss exploits it; NC1 and nearest-neighbor diagnostics identify these classes *a priori* [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: A loss function that explicitly penalizes embedding points of severely entangled classes for being too close to the centroids of their dominant confusion partners (e.g., oligodendrocyte C → excitatory neurons) will improve separability beyond current losses.  
  **delta from paper**: Replaces generic reweighting/margin with *geometry-aware* penalty derived from diagnostic outputs (confusion partners, centroid distances).  
  **initial method**: For class $c$ diagnosed as severely entangled, add term $\lambda \cdot \frac{1}{N_c} \sum_{x_i \in c} \min_{k \in \mathcal{C}_c} \|f(x_i) - \mu_k\|^2$ to loss, where $\mathcal{C}_c$ is its top-2 confusion partners from diagnostic, $\mu_k$ is their centroid, $f$ is embedding.  
  **validation**: Train on MS; compare F1 of oligodendrocyte C/phagocyte vs. class-balanced/LDAM; ablate geometry term to confirm contribution.  
  **failure modes**: Over-penalizing may distort global embedding structure; requires accurate centroid estimation (sensitive to small $N_c$).  
  **innovation status**: unverified  

- **name**: Absolute-Count Adaptive Reweighting Scheduler  
  **originating limitation/observation**: Absolute training count predicts ∆F1, but current losses use static weights (e.g., fixed β in class-balanced); no mechanism adapts weighting strength *during training* based on per-class scarcity [Paper] [Paper: PDF p. 4].  
  **core hypothesis**: Dynamically increasing the reweighting coefficient for a class as its effective sample count (e.g., via EMA of gradient norm) falls below a threshold tuned to absolute count will better match the empirical ∆F1 vs. count curve.  
  **delta from paper**: Moves from static, dataset-level reweighting (e.g., Cui et al. 2019) to dynamic, class-level, count-adaptive scheduling.  
  **initial method**: For class $c$, define effective count $n_c^{\text{eff}}(t) = \beta \cdot n_c^{\text{eff}}(t-1) + (1-\beta) \cdot \|\nabla_\theta \ell_c\|$, then set weight $w_c(t) \propto (1 - \exp(-n_c^{\text{eff}}(t)/\tau))^{-1}$, where $\tau$ is a learnable threshold.  
  **validation**: On Zheng68K, compare microglial cell F1 gain vs. standard class-balanced; monitor weight evolution per class.  
  **failure modes**: Unstable $n_c^{\text{eff}}$ estimation for tiny classes (n=3); added hyperparameter $\tau$ requires tuning.  
  **innovation status**: unverified  

- **name**: scFM-Aware Rare-Class Data Augmentation via Embedding Interpolation  
  **originating limitation/observation**: Severely entangled classes fail due to n=3 samples, but synthetic oversampling (e.g., SMOTE) on raw counts ignores scFM’s tokenization and may generate biologically implausible sequences [Paper] [Paper: PDF p. 2].  
  **core hypothesis**: Interpolating *in the frozen scFM embedding space* between real samples of a severely entangled class and its *least confusing* partner (e.g., oligodendrocyte C ↔ astrocyte, not excitatory neuron) will yield more plausible augmentations than raw-space methods.  
  **delta from paper**: Leverages scFM’s learned representation for augmentation, unlike Bej et al. (2021) or Cheng et al. (2023) which operate on raw counts or gene graphs.  
  **initial method**: For class $c$, select real samples $x_i, x_j$; find partner $p$ with lowest confusion rate to $c$; generate $x_{\text{aug}} = \alpha f(x_i) + (1-\alpha) f(p)$, then invert $f^{-1}$ (via simple decoder or nearest-neighbor in training set) to get count-like vector.  
  **validation**: Add 5–10 aug samples to MS oligodendrocyte C; measure F1 gain under class-balanced loss vs. baseline.  
  **failure modes**: $f^{-1}$ is ill-posed; interpolation may create hybrid phenotypes with no biological meaning.  
  **innovation status**: unverified