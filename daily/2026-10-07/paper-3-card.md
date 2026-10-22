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
| Datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 3] |
| Backbones | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 3] |
| Losses evaluated | Cross-entropy (CE), weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |
| Key metrics | Macro-F1, rare-class recall (Recall<sub>R</sub>), rare-class precision, rare-class macro-AUPRC, ∆F1<sub>c</sub>, NC1 | [Paper] [Paper: PDF p. 3–6] |

## 02 一句话总结

该论文系统评测了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/ Zheng68K/Pancreas）上的表现，发现整体准确率严重掩盖罕见细胞类型（如疾病相关病理亚群）的系统性失败；这种失败可划分为两类：一类是“损失敏感型”（loss-sensitive），可通过重加权类平衡损失等方法显著提升性能；另一类是“严重纠缠型”（severely entangled），其根本瓶颈在于训练样本绝对数量过少（如仅3个细胞）与嵌入空间几何结构（如邻域吸收、高NC1）共同导致，现有损失函数均无法缓解。论文由此提出首个机制驱动的实践指南：用NC1与最近邻混淆模式预判失败类型，对可恢复类优先选用class-balanced loss或LDAM，对不可恢复类应转向数据增补或拒判策略，而非继续优化损失。

## 03 研究问题

论文直面单细胞基础模型在临床关键场景下的可信度断层：当模型报告97.5%的总体准确率时，是否仍会系统性漏检那些仅含个位数样本、却承载疾病早期信号的罕见细胞亚型？作者不满足于将问题归因为“数据不平衡”，而是追问更精细的机制问题：（1）不同长尾损失函数的收益是否依赖于特定骨干架构？（2）罕见类失败是统一现象，还是存在本质不同的子类型？（3）若存在可恢复子类型，决定其是否受益于重加权的关键变量是相对频率（如占比<5%），还是绝对样本量？（4）若存在不可恢复子类型，其失败根源是表征坍缩（representation collapse），还是分类器训练缺陷？这些问题共同构成对“长尾损失是否万能解药”的实证拷问。

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer）已成为细胞类型注释默认主干，但其高聚合准确率被证实由常见细胞主导，而罕见细胞（如MS中的病理寡突胶质细胞C、吞噬细胞）常被忽略 [Paper] [Paper: PDF p. 1]。此前工作已识别该问题：Alsabbagh et al. (2023) 发现随机过采样最稳健，但聚焦采样策略而非损失函数；Naziri et al. (2025) 在AML中观察到健康vs.复发样本F1骤降，归因于预训练偏差；Al Amin et al. (2025) 揭示人口统计学失衡亦影响微调。长尾学习领域已有成熟损失族（重加权、focal loss、LDAM、logit adjustment）[Paper] [Paper: PDF p. 2]，但其在单细胞基础模型上的系统性跨架构评估尚属空白。本文承接此缺口，将“损失函数选择”作为独立控制轴，在固定采样分布与批处理条件下，隔离考察其效应，从而补全从采样→表示→分类的完整干预谱系。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|----------------------------|--------------------------|
| **Aggregate metrics mask rare-class failure** | Accuracy > Macro-F1 > rare-class recall consistently across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 3] | Dataset structure (training-set scarcity), not pretraining bias, drives the gap [Paper] [Paper: PDF p. 1] | Figure 2 (left): Pancreas has highest accuracy but largest accuracy-to-rare-recall drop; Table 1 shows consistent ordering across datasets [Paper] [Paper: PDF p. 4–5] |
| **Loss-level interventions are insufficient for some rare classes** | Two MS classes (oligodendrocyte C, phagocyte) achieve near-zero F1 under *all* six losses and *all* three backbones [Paper] [Paper: PDF p. 5] | Training-set size too small (n=3 cells) to learn distinguishable representation; geometric absorption into unrelated classes’ neighborhoods [Paper] [Paper: PDF p. 5–6] | Figure 3 (left): two darkest rows across all columns; Figure 4: UMAP shows 116 test cells absorbed in CE/LDAM spaces; Section 5.1 confirms same failure in non-foundation baselines (5-NN, RF) [Paper] [Paper: PDF p. 5–7] |
| **Reweighting benefit is misattributed to relative imbalance** | Weighted CE performs best on MS (most imbalanced *ratio*), yet worst on Zheng68K (less imbalanced ratio but larger absolute rare-class counts) [Paper] [Paper: PDF p. 4] | Benefit is predicted by *absolute* training-set size of the rare class, not its share of dataset or overall imbalance ratio [Paper] [Paper: PDF p. 4] | Figure 3 (right): strong negative Pearson correlation (r = −0.77, p < 0.001) between log(training size) and ∆F1<sub>c</sub>; MS rare classes have smallest absolute counts [Paper] [Paper: PDF p. 4] |
| **Loss functions make hidden trade-offs obscured by Macro-F1** | Logit adjustment achieves highest rare-class recall on Zheng68K (+0.075 over CE) but lowest rare-class precision among all six losses [Paper] [Paper: PDF p. 4] | It shifts decision threshold rather than improving feature separability, increasing false positives [Paper] [Paper: PDF p. 4] | Figure 2 (right): logit-adjusted point lies far below y=x line; Table 1 shows its rare-class precision is lowest (0.632 vs. CE’s 0.650 on Zheng68K) [Paper] [Paper: PDF p. 4–5] |

## 06 核心思想

论文的核心思想不是“设计新损失”，而是**建立一个诊断性框架，将罕见类失败解耦为可修复与不可修复两类，并为每类提供可操作的判别标准与干预路径**。其洞察源于对失败机制的分层归因：第一层是数据层面——若某类训练样本绝对数量极低（如≤3），则任何损失函数都无法克服信息匮乏，表现为嵌入空间中该类样本被完全吸收进其他类的邻域（Figure 4），且NC1指标异常升高（oligodendrocyte C）或异常降低（phagocyte）[Paper] [Paper: PDF p. 6]；第二层是算法层面——对于其余“损失敏感型”类，其可修复性由绝对样本量线性预测，而非相对频率，这解释了为何MS（小绝对数）比Zheng68K（大绝对数）从重加权中获益更多；第三层是评估层面——Macro-F1等单一指标会掩盖precision-recall权衡，必须通过散点图（Figure 2 right）与AUPRC等阈值无关指标揭示真实trade-off。该思想将长尾问题从“如何调参”升维至“何时放弃调参”。

## 07 方法总览

论文采用**控制变量+多尺度诊断**方法论：（1）**系统性基准构建**：在3 backbone × 3 dataset × 6 loss × 3 seed = 162次运行中，严格固定数据划分、基因面板、优化器超参、批大小等所有非损失变量，仅改变损失函数，以隔离其效应 [Paper] [Paper: PDF p. 3]；（2）**双轨评估体系**：既报告宏观指标（Macro-F1, Recall<sub>R</sub>），也深入微观层面——按类分析∆F1<sub>c</sub>（Eq. 3）、绘制F1热图（Figure 3 left）、计算NC1（Eq. 4）与最近邻熵 [Paper] [Paper: PDF p. 4–6]；（3）**机制验证实验**：引入非基础模型基线（5-NN, RF）验证失败非预训练特有；用线性探针（linear probe）在冻结嵌入上测试判别信号是否残留，定位瓶颈在分类器训练而非表示坍缩 [Paper] [Paper: PDF p. 6]；（4）**几何可视化**：UMAP投影（Figure 4）直观呈现“吸收”现象，将抽象失败转化为可观察的空间关系。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|-------------------|------------------------|-----------------------------------|
| **Rare-class definition & metric suite** | Define rare classes (training freq < 5%), compute Recall<sub>R</sub>, precision<sub>R</sub>, macro-AUPRC, ∆F1<sub>c</sub> | To move beyond aggregate accuracy and quantify failure on clinically relevant subpopulations | Input: per-class true labels/predictions; Output: scalar metrics per rare class/dataset | Section 3 defines R ⊆ {1,…,C}; Eq. 2 defines Recall<sub>R</sub>; Table 1 reports all metrics [Paper] [Paper: PDF p. 3–5] | Without this, Figure 2 (right) and Figure 3 (right) would be impossible; conclusions about "loss-sensitive" regime vanish. |
| **Per-class ∆F1<sub>c</sub> analysis (Eq. 3)** | Quantify gain of best loss over CE for each rare class c | To test whether reweighting benefit is uniform or concentrated, and identify predictors (e.g., absolute count) | Input: F1<sub>c</sub> under each loss ℓ; Output: ∆F1<sub>c</sub> = max<sub>ℓ∈L</sub> F<sup>(ℓ)</sup><sub>1,c</sub> − F<sup>(CE)</sup><sub>1,c</sub> | Eq. 3 explicitly defined; Figure 3 (right) plots ∆F1<sub>c</sub> vs. log(training size) [Paper] [Paper: PDF p. 4] | Without Eq. 3, the central finding that absolute count predicts benefit (r=−0.77) could not be established. |
| **Neural Collapse Geometry (NC1, Eq. 4)** | Quantify embedding tightness/separability via trace ratio tr(Σ<sub>W</sub>)/tr(Σ<sub>B</sub>) | To distinguish geometric causes of failure: high NC1 → poor within-class cohesion; low NC1 + absorption → small cluster embedded in another class | Input: frozen test-set embeddings per class; Output: scalar NC1 per class | Eq. 4 defined; Section 5.2 reports NC1 values for oligodendrocyte C (1.19–1.79) and phagocyte (0.17–0.32) [Paper] [Paper: PDF p. 6] | Without NC1, the geometric signature difference between the two severely entangled classes (Figure 4) remains qualitative, not quantifiable. |
| **Linear probe on frozen embeddings** | Test if discriminative signal exists *in the representation* independent of classifier training | To determine if failure is due to lack of signal (data scarcity) or inability of loss functions to exploit it | Input: frozen CE-fine-tuned embeddings; Output: F1/recall/precision of logistic regression probe | Section 5.3 describes probe; results show probe F1 > best trained F1 for entangled classes (e.g., scGPT/oligodendrocyte C: 0.465 vs. 0.329) [Paper] [Paper: PDF p. 6] | Without probe, conclusion that "bottleneck is partly in loss design, not solely data scarcity" [Paper] [Paper: PDF p. 6] lacks direct evidence. |
| **UMAP visualization with selective highlighting (Figure 4)** | Visualize spatial relationship of severely entangled classes' test cells in embedding space | To provide intuitive, geometric evidence of "neighborhood absorption" that precedes any loss choice | Input: scGPT test embeddings; Output: 2D plot with 116 rare cells highlighted | Figure 4 caption and description; shows same 116 cells misclassified in CE and LDAM spaces [Paper] [Paper: PDF p. 7] | Without Figure 4, the claim of "absorption into unrelated classes' neighborhoods" [Paper] [Paper: PDF p. 5] is abstract; visualization makes it concrete and verifiable. |

## 09 关键公式与符号

- **No verifiable closed-form equations are presented in the paper.** All listed equations are definitions or computational recipes, not derived theoretical formulas.
- **Equation 1**: `Macro-F1 = 1/C ∑_{c=1}^C F1,c` — Definition of unweighted mean F1 score across C classes [Paper] [Paper: PDF p. 3]. Symbol `F1,c` denotes F1 score for class `c`.
- **Equation 2**: `Recall_R = 1/|R| ∑_{c∈R} Recall_c` — Definition of macro-averaged recall over rare-class set `R` [Paper] [Paper: PDF p. 3]. Symbol `R` denotes set of rare classes (training freq < 5%).
- **Equation 3**: `∆F1,c = max_{ℓ∈L} F^{(ℓ)}_{1,c} − F^{(CE)}_{1,c}` — Definition of per-class F1 gain from best loss over cross-entropy [Paper] [Paper: PDF p. 4]. Symbol `L` denotes set of six losses; `F^{(ℓ)}_{1,c}` is class `c`'s F1 under loss `ℓ`.
- **Equation 4**: `NC1 = tr(Σ_W) / tr(Σ_B)` — Neural collapse trace ratio, where `Σ_W` is average within-class scatter, `Σ_B` is between-class scatter of centroids [Paper] [Paper: PDF p. 6]. Lower NC1 indicates tighter, better-separated clusters.
- **Key metrics**: `Accuracy`, `Macro-F1`, `Recall_R`, `Precision_R`, `macro-AUPRC`, `∆F1,c`, `NC1`.
- **Key sets**: `R` (rare classes), `L` (loss set), `C` (total classes).
- **Not assessable from supplied material**: No derivation, proof, or theoretical justification of any equation is provided.

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|----------------------|------------------------------|--------|
| **162-run benchmark (Table 1, Fig 2 left)** | Aggregate metrics mask rare-class failure across architectures | CE vs. 5 other losses; 3 backbones × 3 datasets × 3 seeds; fixed data splits, gene panels, optimizers | Accuracy > Macro-F1 > Recall_R consistently across all 9 (backbone, dataset) cells | Gap is inherent to dataset imbalance structure, not backbone-specific | That pretraining is irrelevant — authors note variance arises from config differences [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3–5], Table 1, Figure 2 left |
| **∆F1,c vs. log(training size) (Fig 3 right)** | Absolute training-set size, not relative frequency, predicts reweighting benefit | Correlation of ∆F1,c (Eq. 3) with log(count) for 19 recoverable rare classes | Strong negative Pearson r = −0.77 (p < 0.001); robust to exclusion thresholds | Reweighting efficacy is determined by absolute sample count | That this holds for *all* rare classes — 4 severely entangled classes were excluded [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 3 right |
| **UMAP + linear probe (Fig 4, Sec 5.3)** | Severely entangled classes retain discriminative signal in frozen embeddings | Linear probe (class-balanced logistic regression) on CE-fine-tuned frozen embeddings vs. best trained classifier F1 | Probe F1 exceeds best trained F1 for oligodendrocyte C (0.465 vs 0.329) and phagocyte (0.462 vs 0.000) | Bottleneck is in classifier training/loss design, not representation collapse | That a more complex nonlinear probe would close the gap — not tested [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6–7], Figure 4, Section 5.3 |
| **Non-foundation baselines (Sec 5.1)** | Failure is not specific to pretrained representations | 5-NN and class-balanced RF on raw gene expression vs. foundation models | Both baselines yield F1=0 on oligodendrocyte C/phagocyte, matching foundation models | Failure stems from data scarcity & geometry, not pretraining artifacts | That these baselines are universally weak — they achieve Macro-F1=0.28/0.65 on MS overall [Paper] [Paper: PDF p. 5] | [Paper] [Paper: PDF p. 5], Section 5.1 |
| **NC1 & nearest-neighbor analysis (Sec 5.2)** | Two distinct geometric signatures distinguish severely entangled classes | NC1 computed on MS rare classes; nearest-neighbor entropy calculated for phagocyte/oligodendrocyte C | Phagocyte: low NC1 (0.17–0.32), high concentration (entropy 0.71); Oligo-C: high NC1 (1.19–1.79), high dispersion (entropy 0.90) | Failure modes are geometrically distinct, requiring different diagnostics | That NC1 alone suffices for diagnosis — authors use it *with* nearest-neighbor patterns [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6], Section 5.2 |

## 11 对结论的正确理解

论文结论**不可简化为“class-balanced loss is best”或“loss functions don’t work”**。正确理解需把握三层限定：（1）**适用范围限定**：class-balanced loss 和 LDAM 是“最一致的通用选择”（mean rank 2.4/2.6），但并非在所有数据集上都最优（e.g., weighted CE wins on MS Macro-F1, LDAM wins on Pancreas Macro-F1）[Paper] [Paper: PDF p. 3]；（2）**问题域限定**：结论仅针对“细胞类型级”类别不平衡，明确排除了人口统计学失衡、批次效应等混杂变量 [Paper] [Paper: PDF p. 6]；（3）**机制限定**：“损失无效”仅适用于“严重纠缠型”类（如MS中n=3的两类），其失效根源是数据稀缺与几何吸收，而非损失函数本身缺陷；对“损失敏感型”类（如microglial cell），class-balanced loss确实能将其F1从0（scBERT）提升至0.86–0.92 [Paper] [Paper: PDF p. 6]。因此，核心贡献是提供了一个**条件化决策树**：先用NC1/UMAP诊断失败类型，再决定是换损失（可恢复）还是补数据（不可恢复）。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer evaluated; scFoundation and CellPLM remain untested [Paper] [Paper: PDF p. 6] | Test other existing single-cell foundation models (scFoundation, CellPLM) [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6] |
| **Classifier expressivity ceiling** | Linear probe reveals unused discriminative signal in frozen embeddings, suggesting current losses may not fully exploit it [Paper] [Paper: PDF p. 6] | Explore more expressive, nonlinear classifier heads beyond the six losses tested [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6] |
| **Isolated imbalance axis** | Study focuses solely on cell-type class imbalance; does not address compounding variables like demographic composition or batch effects [Paper] [Paper: PDF p. 6] | Investigate interactions with demographic composition (Al Amin et al. 2025) and batch effects (Maan et al. 2024) [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| **The "severely entangled" regime is defined by near-zero F1 across *all* losses, but F1=0 may reflect label noise or annotation ambiguity rather than pure data scarcity** | The MS dataset retains "two ambiguous MS labels as defined in the source atlas" [Paper] [Paper: PDF p. 3]; oligodendrocyte C and phagocyte may be biologically ill-defined or mislabeled, making them inherently non-separable regardless of samples or loss. | If true, the "data scarcity" interpretation is incomplete; the bottleneck may be ontological (label quality) rather than statistical (sample count). This affects whether data collection or label curation is the priority. | Re-annotate the 3 training cells for oligodendrocyte C/phagocyte using orthogonal modalities (e.g., spatial transcriptomics or protein markers) and re-run experiments. Compare F1 before/after. | [Paper] [Paper: PDF p. 3] states ambiguous labels exist; [Paper] [Paper: PDF p. 6] notes phagocyte is identified by ingested myelin RNA, suggesting biological heterogeneity. |
| **NC1 is computed on *frozen test-set embeddings*, but the paper attributes geometric failure to training dynamics** | NC1 measures static geometry post-training; however, neural collapse theory (Papyan et al. 2020) links NC1 to *training trajectory*. Computing it only on test embeddings misses whether collapse occurs during fine-tuning or is inherited from pretraining. | Misattribution could lead to wrong interventions (e.g., blaming fine-tuning loss when pretraining already induced collapse). For user's sc foundation model work, this affects whether to modify pretraining or fine-tuning. | Compute NC1 at multiple fine-tuning epochs (e.g., epoch 1, 5, 10, 15) and compare to pretraining checkpoint. Plot NC1 trajectory for oligodendrocyte C vs. other classes. | [Paper] [Paper: PDF p. 6] cites Papyan et al. 2020 on neural collapse but applies NC1 only to frozen test embeddings, not dynamics. |
| **The linear probe uses class-balanced logistic regression, but the "best loss" comparison includes non-calibrated losses (e.g., LDAM)** | Probe performance is measured by F1, while LDAM is designed to shape decision boundaries, not calibrate probabilities. A probe using LDAM's margin-aware objective might show different signal recovery. | This creates an apples-to-oranges comparison: probe evaluates separability, but losses optimize different objectives. It may underestimate what LDAM *could* extract if properly tuned. | Train linear probes using each of the six loss functions (not just logistic regression) on the same frozen embeddings and compare their F1. | [Paper] [Paper: PDF p. 6] uses "class-balanced logistic regression" for probe, while losses like LDAM and logit adjustment have fundamentally different objectives. |

## 14 学到的知识

- **诊断先行，干预后置**：在单细胞长尾任务中，不应直接尝试所有损失函数，而应先用NC1（Eq. 4）和UMAP最近邻分析（Figure 4）对罕见类进行“几何体检”，区分可修复（loss-sensitive）与不可修复（severely entangled）两类。
- **绝对数量胜于相对比例**：决定重加权效果的关键变量是罕见类的**绝对训练样本数**（如3 vs. 70），而非其在数据集中的占比（如1% vs. 5%）。这解释了为何MS（小绝对数）比Zheng68K（大绝对数）获益更大，颠覆了“不平衡比率决定一切”的直觉。
- **Macro-F1是危险的简化器**：Figure 2 (right) 清晰显示，logit adjustment虽提升recall，却大幅牺牲precision，而Macro-F1无法揭示此trade-off。必须辅以precision-recall散点图与macro-AUPRC。
- **失败可溯源至几何**：严重纠缠类的失败不是黑箱，而是可观测的空间现象——其测试样本在UMAP中被完全吸收进其他类的邻域（Figure 4），且NC1指标呈现特征性偏移（高或低），这为调试提供了具体靶点。
- **信号未消失，只是未被利用**：线性探针证明，即使仅有3个训练样本，判别性信号仍线性可分地存在于冻结嵌入中（Section 5.3）。这表明当前损失函数的设计存在表达能力缺口，为用户设计新损失（如结合margin与calibration）提供了强动机。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的“两阶段诊断框架”（先几何分析，再损失选择）与Kang et al. (2020) 提出的“解耦表示学习与分类器校准”思想高度一致，均主张将表征质量与决策边界优化分离；本文用NC1和UMAP实现了该思想在单细胞领域的可操作化落地。
- **候选连接/方法论连接**：对“绝对样本量预测重加权收益”的发现，与计算机视觉中Buda et al. (2018) 和Saini & Susan (2023) 的结论形成跨模态呼应，证实了“有效样本数”（effective-number-of-samples）框架在单细胞领域的普适性。
- **候选连接/方法论连接**：使用UMAP可视化嵌入空间吸收现象（Figure 4），与用户研究方向中“spatial transcriptomics”的空间邻域概念存在方法论共鸣——两者均强调细胞/spot在低维流形中的相对位置与生物学意义的关联。
- **候选连接/方法论连接**：线性探针揭示未被利用的信号（Section 5.3），为用户“perturbation prediction”方向提供启示：若基础模型嵌入中已蕴含扰动响应信号（如药物处理后的状态偏移），但当前分类头未能提取，则可借鉴此探针范式，设计专用扰动解码头。
- **弱连接/方法论连接**：本文聚焦单模态（scRNA-seq）细胞类型分类，与用户“multi-omics”方向无直接交集；但其“几何诊断”思路可迁移至多组学对齐后的联合嵌入空间，用于识别跨模态对齐失败的罕见亚群。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometric-aware Loss Gating  
  **originating limitation/observation**: Severely entangled classes exhibit distinct NC1 signatures (high vs. low) and nearest-neighbor entropy, yet all losses fail uniformly [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: A loss function should *adapt its objective* based on the geometric profile of each class — e.g., apply large-margin constraints for high-NC1 classes (poor cohesion) and density-aware reweighting for low-NC1 classes (absorption).  
  **delta from paper**: Paper treats loss choice as global; this proposes per-class, geometry-conditioned loss selection or interpolation.  
  **initial method**: For each class c, compute NC1<sub>c</sub> and neighbor entropy H<sub>c</sub> on frozen embeddings; define gating weight g<sub>c</sub> = σ(α·NC1<sub>c</sub> + β·H<sub>c</sub>); blend LDAM (for high NC1) and class-balanced (for low NC1) via g<sub>c</sub>.  
  **validation**: Train on MS; compare F1 for oligodendrocyte C (high NC1) and phagocyte (low NC1) vs. baseline LDAM/class-balanced.  
  **failure modes**: Gating weights may be unstable with tiny n; requires reliable NC1 estimation from few samples.  
  **innovation status**: unverified  

- **name**: Probe-guided Loss Synthesis  
  **originating limitation/observation**: Linear probe recovers non-trivial F1 on entangled classes, exceeding best trained classifiers, proving signal exists but is unused [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: The gradient update direction of standard losses misaligns with the direction of maximal separability revealed by the probe; synthesizing a loss that directly minimizes the probe's classification error on frozen embeddings will close the gap.  
  **delta from paper**: Paper uses probe for diagnosis; this uses probe gradients to *design* a new loss term.  
  **initial method**: Extract frozen embeddings Z; train linear probe w<sup>*</sup> = argmin<sub>w</sub> ℓ<sub>probe</sub>(w<sup>T</sup>Z, y); define new loss ℓ<sub>new</sub> = ℓ<sub>CE</sub> + λ·ℓ<sub>probe</sub>(w<sup>*</sup><sup>T</sup>Z, y), where ℓ<sub>probe</sub> is hinge or logistic loss.  
  **validation**: On MS oligodendrocyte C, measure if ℓ<sub>new</sub> lifts F1 above probe's 0.465.  
  **failure modes**: w<sup>*</sup> is fixed; may not generalize to unseen samples; adds computational overhead.  
  **innovation status**: unverified  

- **name**: Spatial-Anchor Contrastive Alignment  
  **originating limitation/observation**: Phagocyte's confusion with oligodendrocyte A reflects real transcriptional overlap from ingested myelin RNA [Paper] [Paper: PDF p. 6], suggesting biological proximity should inform loss design.  
  **core hypothesis**: Incorporating spatial transcriptomics priors (e.g., from Visium) as contrastive anchors can disentangle transcriptionally overlapping but spatially segregated rare classes, mitigating absorption.  
  **delta from paper**: Paper uses only scRNA-seq; this fuses spatial context to reshape embedding geometry *during* fine-tuning.  
  **initial method**: For MS, obtain spatial data; identify oligodendrocyte A and phagocyte spots; use their averaged spatial gene expression as positive anchors in a contrastive loss alongside scRNA-seq embeddings.  
  **validation**: Train scGPT on MS with/without spatial anchors; compare NC1 and UMAP absorption (Figure 4) for phagocyte.  
  **failure modes**: Requires matched spatial data for rare classes; anchor quality depends on spot purity.  
  **innovation status**: unverified