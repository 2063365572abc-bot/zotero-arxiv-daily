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
| Backbones evaluated | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 3] |
| Datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 3] |
| Loss functions benchmarked | Cross-entropy (CE), weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |
| Key metrics | Macro-F1, rare-class recall (Recall<sub>R</sub>), rare-class precision, rare-class macro-AUPRC, ∆F1<sub>c</sub>, NC1 | [Paper] [Paper: PDF p. 3–6] |

## 02 一句话总结

该论文系统评测了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/Zheng68K/Pancreas）上的表现，发现整体准确率严重掩盖罕见细胞类别的系统性失败；这种失败可划分为两类机制：一类是“损失敏感型”（loss-sensitive），其性能可通过重加权类损失显著提升，且提升幅度由**绝对训练样本数**而非相对频率决定；另一类是“严重纠缠型”（severely entangled），即使更换所有损失函数与架构，仍因嵌入几何结构缺陷（如邻域吸收、高NC1）而无法恢复，需通过线性探针验证信号是否尚存。该工作为scFM在疾病相关稀有细胞建模中提供了首个机制驱动的损失选择指南。

## 03 研究问题

论文直面一个被广泛忽视但临床关键的矛盾：单细胞基础模型（scFM）在细胞类型分类任务中报告高达97.5%的总体准确率，却对罕见、常具疾病意义的细胞亚群（如MS中的oligodendrocyte C、phagocyte）持续失效——而这些失效恰恰是长尾损失函数本应解决的核心问题。作者追问：（1）这种失效是模型预训练固有缺陷，还是数据结构或损失设计导致？（2）不同长尾损失函数在跨架构、跨数据集场景下的鲁棒性是否存在可预测的排序？（3）失效是否具有可诊断的几何表征？能否据此提前识别哪些罕见类“可救”、哪些“不可救”？（4）若可救，什么因素决定某类从重加权中获益的程度？这些问题共同指向一个更深层目标：将scFM长尾问题从经验调参层面，推进至机制可解释、证据可追溯、决策可指导的科学评估范式。

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer等）已成为细胞注释默认主干，但其高聚合准确率被证实由常见细胞主导，罕见细胞（如病理过渡态、早期病变亚群）常被系统性忽略 [Paper] [Paper: PDF p. 1]。此前工作已识别该现象：Alsabbagh et al. (2023) 在采样策略层面尝试缓解，Naziri et al. (2025) 揭示疾病亚组性能断崖式下降，Al Amin et al. (2025) 指出人口统计学不平衡亦有影响 [Paper] [Paper: PDF p. 1–2]。然而，损失函数这一核心干预轴尚未被系统检验——现有研究或聚焦特定新损失（Zhao et al. 2025）、或耦合采样与模型修改（Cheng et al. 2023）、或采用非标准协议（如冻结编码器+多专家头）[Paper] [Paper: PDF p. 2]。本文承接此空白，将长尾学习经典方法（Cui et al. 2019; Cao et al. 2019; Menon et al. 2021）首次完整迁移到scFM场景，严格控制变量（固定数据划分、批大小、优化器、微调协议），仅改变损失函数，从而隔离其独立效应。路径上，它从“是否有效”（Section 4）跃迁至“为何有效/无效”（Section 5），引入神经坍塌（neural collapse）理论与嵌入几何分析，将性能差异锚定到可计算的几何量（NC1、最近邻熵、UMAP空间吸收模式），完成从现象描述到机制诊断的闭环。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|--------------------------|
| **Aggregate metrics mask rare-class failure** | Overall accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 3] | Driven by dataset imbalance structure, not pretraining artifacts [Paper] [Paper: PDF p. 1, 3] | Figure 2 (left): consistent gap under plain CE; text states “this gap is present regardless of which foundation model is used” [Paper] [Paper: PDF p. 3] |
| **Loss-level interventions are insufficient for some rare classes** | Two MS classes (oligodendrocyte C, phagocyte) achieve near-zero F1 under *all* six losses and *all* three backbones [Paper] [Paper: PDF p. 5] | Too few training examples (n=3 each) to learn distinguishable representation; failure persists even in non-foundation baselines (5-NN, RF) [Paper] [Paper: PDF p. 5] | Figure 3 (left): darkest rows across all columns; Section 5.1: “both have only 3 training examples”; Table 1: CE F1 for these classes ≈0 [Paper] [Paper: PDF p. 5] |
| **Reweighting benefit is misattributed to relative frequency** | Weighted CE performs best on MS but worst on Zheng68K despite similar imbalance ratios [Paper] [Paper: PDF p. 4] | Benefit is predicted by *absolute* training-set size of rare class, not its share of dataset or global imbalance ratio [Paper] [Paper: PDF p. 1, 4] | Figure 3 (right): strong negative correlation (r=−0.77) between log(training size) and ∆F1<sub>c</sub>; MS rare classes have smallest absolute counts [Paper] [Paper: PDF p. 4] |
| **Loss functions make hidden trade-offs obscured by Macro-F1** | Logit adjustment boosts rare recall but incurs largest precision penalty among all six losses [Paper] [Paper: PDF p. 4] | It shifts decision thresholds rather than improving feature separability, leading to more false positives [Paper] [Paper: PDF p. 4] | Figure 2 (right): logit-adjusted point lies far below y=x line; text: “lowest rare-class precision of all six losses” [Paper] [Paper: PDF p. 4] |

## 06 核心思想

论文的核心思想是：**单细胞基础模型的长尾失效并非单一问题，而是由两种根本不同的机制驱动的双轨现象，必须用不同工具诊断与应对**。第一轨是“损失敏感型”失效：其根源在于标准交叉熵损失对小样本类的梯度压制，可通过重加权类损失（如class-balanced loss）有效缓解；关键洞见是，此类缓解效果不取决于“该类占多少比例”，而取决于“该类有多少个细胞”——绝对样本数越少，重加权增益越大（Figure 3右）。第二轨是“严重纠缠型”失效：其根源是极低样本数（n=3）导致嵌入空间中该类无法形成可分离簇，反而被吸收进邻近类的几何邻域（Figure 4），此时更换任何损失函数均无效；但线性探针证明判别信号仍存在于冻结嵌入中（Section 5.3），说明瓶颈在分类器训练而非表示坍塌，提示需转向解耦式校准（如Kang et al. 2020）或拒绝选项（reject-option）。这一双轨框架将经验性“试错调参”升维为基于几何证据（NC1、最近邻熵）和统计证据（∆F1 vs. log(size)）的理性决策流程。

## 07 方法总览

论文采用“控制变量+多维诊断”方法论：在162次受控训练中，固定所有超参数（学习率、批大小、优化器、微调协议、基因面板），仅系统替换损失函数，以纯净地量化损失效应。评估维度分三层：（1）**聚合层**：报告Macro-F1与Rare-class Recall（Eq. 1–2），揭示指标失真；（2）**细粒度层**：计算每类∆F1<sub>c</sub>（Eq. 3）并关联其训练样本数，定位可修复类；（3）**机制层**：对失效类进行嵌入几何分析——用NC1（Eq. 4）量化类内/类间散度，用UMAP可视化（Figure 4）与最近邻熵刻画吸收模式，并用线性探针（Section 5.3）区分“信号缺失”与“信号未利用”。整个方法链路清晰：从宏观性能差异（Fig 2）→ 到中观类级响应（Fig 3）→ 再到微观几何归因（Fig 4, Eq. 4），最终导向实践指南（Section 6）。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|---------------------|------------------------|-----------------------------------|
| **Loss-function grid** | Systematically evaluates 6 long-tail losses (CE, weighted CE, class-balanced, focal, LDAM, logit-adjusted) across all backbone-dataset combinations | Isolates loss effect from architecture/data confounders; tests off-the-shelf robustness of general-purpose losses | Input: logits + true labels; Output: scalar loss value per sample | Table 1 reports full results; Section 4.2 ranks losses by mean position across 9 cells [Paper] [Paper: PDF p. 3–4] | Without this grid, no cross-architecture comparison possible; conclusions about "most consistent" losses (class-balanced/LDAM) vanish [Analysis] |
| **Rare-class definition & metric suite** | Defines rare class as training frequency <5%; computes Recall<sub>R</sub> (Eq. 2), rare-precision, rare-macro-AUPRC | Exposes aggregate metric blindness; AUPRC avoids threshold-commitment bias inherent in F1 | Input: test predictions & labels; Output: scalar per metric | Figure 2 (right) plots precision vs. recall; Table 1 includes AUPRC; text notes logit adjustment’s AUPRC weakness despite F1 strength [Paper] [Paper: PDF p. 3–4] | Using only accuracy/Macro-F1 would hide logit adjustment’s precision-recall trade-off [Paper] [Paper: PDF p. 4] |
| **Per-class ∆F1<sub>c</sub> analysis** | Computes max<sub>ℓ∈L</sub> F<sup>(ℓ)</sup><sub>1,c</sub> − F<sup>(CE)</sup><sub>1,c</sub> (Eq. 3) for each rare class c | Tests hypothesis that reweighting benefit depends on absolute sample count, not relative frequency | Input: per-class F1 scores across all losses/seeds/backbones; Output: ∆F1<sub>c</sub> vector | Figure 3 (right) shows strong negative correlation (r=−0.77) with log(training size); text states “reintroducing severely entangled classes yields weaker but still significant correlation” [Paper] [Paper: PDF p. 4] | Removing this analysis would leave the key insight (“absolute count predicts gain”) unsupported; MS vs. Zheng68K performance difference remains unexplained [Analysis] |
| **Embedding geometry diagnostics** | Computes NC1 (Eq. 4), nearest-neighbor confusion entropy, UMAP visualization (Figure 4), linear probe on frozen embeddings | Distinguishes two failure regimes: “loss-sensitive” (fixable) vs. “severely entangled” (geometrically rooted) | Input: frozen test-set embeddings + labels; Output: NC1 scalar, entropy, probe F1 | Figure 4 shows absorption in UMAP; Section 5.2 reports NC1 values (e.g., oligodendrocyte C: 1.19–1.79); Section 5.3 shows probe F1 > trained F1 for entangled classes [Paper] [Paper: PDF p. 5–7] | Without geometry analysis, the “severely entangled” regime would be misattributed to loss choice; no basis for recommending data collection over loss engineering [Paper] [Paper: PDF p. 6] |

## 09 关键公式与符号

- **No verifiable closed-form equations** are presented in the paper. All listed equations are definitions or computational summaries:
  - Equation 1: Macro-F1 = $\frac{1}{C}\sum_{c=1}^{C} F1_c$ — definition of unweighted mean F1 across $C$ classes [Paper] [Paper: PDF p. 3]
  - Equation 2: Rare-class recall = $\frac{1}{|R|}\sum_{c\in R} \text{Recall}_c$ — definition of macro-averaged recall over rare class set $R$ [Paper] [Paper: PDF p. 3]
  - Equation 3: $\Delta F1_c = \max_{\ell\in L} F1^{(\ell)}_c - F1^{(CE)}_c$ — definition of per-class F1 gain from best loss over CE [Paper] [Paper: PDF p. 4]
  - Equation 4: $NC1 = \frac{\text{tr}(\Sigma_W)}{\text{tr}(\Sigma_B)}$ — neural collapse trace ratio, where $\Sigma_W$ is average within-class scatter, $\Sigma_B$ is between-class scatter of centroids [Paper] [Paper: PDF p. 6]

- **Key symbols/variables**:
  - $R$: set of rare classes (training frequency <5%) [Paper] [Paper: PDF p. 3]
  - $F1_c$: F1 score of class $c$ [Paper] [Paper: PDF p. 3]
  - $\ell$: loss function from set $L$ (6 total) [Paper] [Paper: PDF p. 4]
  - $\Sigma_W$, $\Sigma_B$: within-class and between-class scatter matrices for NC1 computation [Paper] [Paper: PDF p. 6]
  - $NC1$: neural collapse indicator (lower = better separation) [Paper] [Paper: PDF p. 6]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|------------------------|----------------------------------|--------|
| **Aggregate metric gap (Fig 2 left)** | Plain CE produces consistent gap: Accuracy > Macro-F1 > Rare-recall across all architectures/datasets | Mean of 9 backbone×seed runs per dataset bar; same train/test splits, hyperparameters | Gap present in all 3 datasets, regardless of backbone (e.g., scBERT MS CE Macro-F1=0.639) [Paper] [Paper: PDF p. 3] | Gap is inherent to data imbalance structure, not backbone-specific artifact | That pretraining has *no* role — authors note variance vs. Alsabbagh et al. arises from config differences [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3], Figure 2 (left) |
| **Loss ranking (Table 1)** | Class-balanced loss and LDAM are most consistent across 9 (backbone, dataset) cells | Rankings computed within each (backbone, dataset) cell before averaging; mean rank over 9 cells | Class-balanced: mean rank 2.4; LDAM: 2.6; both outperform others in consistency [Paper] [Paper: PDF p. 3] | These two losses offer best general-purpose robustness for scFM long-tail tasks | That they are universally optimal — e.g., weighted CE beats them on MS Macro-F1 [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3], Table 1 |
| **∆F1 vs. training size (Fig 3 right)** | Reweighting benefit (∆F1<sub>c</sub>) is predicted by absolute training-set size, not relative frequency | Pearson correlation of log(training size) with ∆F1<sub>c</sub> across 19 recoverable rare classes | Strong negative correlation (r=−0.77, p<0.001); robust to exclusion thresholds [Paper] [Paper: PDF p. 4] | Absolute sample count is the primary predictor of reweighting efficacy in scFM | That relative frequency is irrelevant — authors test multiple cutoffs and find trend holds [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 3 (right) |
| **Logit adjustment trade-off (Fig 2 right)** | Logit adjustment trades rare-class precision for recall | Plot of rare-precision vs. rare-recall for all 6 losses, averaged over 9 settings | Logit-adjusted point lies far below y=x line; lowest precision, highest recall gain among losses [Paper] [Paper: PDF p. 4] | Its recall gains stem from threshold shift, not improved separability | That it harms non-rare classes — text notes their precision/recall spreads are small (1.1/2.1 pts) [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 2 (right) |
| **Linear probe on frozen embeddings (Sec 5.3)** | Severely entangled classes retain discriminative signal unused by trained classifiers | Logistic regression probe on CE-fine-tuned frozen embeddings, 5-fold CV | Probe F1 exceeds best trained F1 for oligodendrocyte C/phagocyte (e.g., scGPT: 0.465 vs. 0.329); smaller margin for microglial cell [Paper] [Paper: PDF p. 6] | Bottleneck is classifier training, not representation collapse | That a nonlinear probe would close the gap — authors explicitly state this as future work [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 6], Section 5.3 |

## 11 对结论的正确理解

论文结论必须置于其严格控制的实验边界内理解：（1）“Class-balanced loss and LDAM are most consistent”指在**所测试的6种损失、3种架构、3个数据集、3个随机种子**条件下，其平均排名最高，**不意味着它们在所有可能损失或新数据集上最优**；（2）“Reweighting benefit predicted by absolute size”是针对**可修复的罕见类**（即排除4个严重纠缠类后n=19的回归），**不否定相对频率在其他场景（如采样策略）的作用**；（3）“Severely entangled classes are unrecoverable by loss choice”特指**本文评估的6种损失及3种架构**，**不排除未来设计的新损失（如结合几何约束的损失）能缓解**；（4）“Signal exists in frozen embeddings”由线性探针证实，**但该信号是否足够支持高精度临床决策，未被验证**；（5）所有结论基于**细胞类型分类任务**，**不直接推广至cell state representation、perturbation prediction或cross-modal alignment等用户研究方向**，属弱连接/方法论连接。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer evaluated; other models (scFoundation, CellPLM) remain untested | “Other existing single-cell foundation models, such as scFoundation and CellPLM [...] remain untested” [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Classifier head expressivity** | Linear probe recovers signal unused by trained heads, suggesting current losses may not fully exploit discriminative capacity | “A more expressive, nonlinear classifier head might extract additional signal beyond what the six losses we test currently achieve” [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Isolated imbalance axis** | Study focuses solely on cell-type class imbalance; ignores compounding variables like demographic composition or batch effects | “Compounding variables such as demographic composition [...] or batch effects [...] require future investigation” [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| **NC1 interpretation conflates scarcity and geometry** | Phagocyte’s low NC1 (0.17–0.32) is attributed to tight clustering inside another class, but could also reflect high intra-class homogeneity due to biological uniformity (e.g., all phagocytes ingest identical myelin fragments) rather than data scarcity | Misattribution could lead to wrong intervention (e.g., collecting more phagocyte samples when biology dictates uniformity) | Compute NC1 on synthetic phagocyte-like clusters with controlled homogeneity vs. scarcity; compare to real data | [Paper] [Paper: PDF p. 6]: “its small cell count means a handful of tightly clustered cells embedded inside another class’s region can produce low within-class scatter” — this is an *assumption*, not proven |
| **Linear probe uses same embeddings as trained head, but different optimization** | Probe uses stratified CV on frozen embeddings, while trained head uses end-to-end fine-tuning with gradient updates — the gap may reflect optimization difficulty (e.g., vanishing gradients for rare classes) rather than loss design flaw | If true, focus should shift to optimizer modifications (e.g., rare-class-specific learning rates) rather than new loss functions | Replace linear probe with a shallow MLP head trained *only on frozen embeddings* (same loss, same optimizer) and compare F1 to full fine-tuning | [Paper] [Paper: PDF p. 6]: “Since the probe and the model’s classifier head are fit on the same fine-tuned embeddings, this localizes the bottleneck to classifier training” — but training dynamics differ |
| **Rare-class definition (<5%) is arbitrary and dataset-dependent** | Using fixed 5% threshold ignores dataset-specific distributions (e.g., Zheng68K’s smallest class has ~70 cells vs. MS’s single digits); may misclassify “moderately rare” classes as common | Could dilute ∆F1 correlations or mask finer-grained regimes (e.g., ultra-rare vs. moderately rare) | Repeat ∆F1 analysis with adaptive thresholds (e.g., top-k rarest classes per dataset) and test correlation stability | [Paper] [Paper: PDF p. 3]: “A class is considered rare if its training-split frequency is below 5% per domain experience” — no justification for 5% or validation of its universality |

## 14 学到的知识

- **指标陷阱警示**：Macro-F1和accuracy在长尾场景下具有欺骗性；必须强制报告**per-class metrics**（F1, recall, precision）和**threshold-free metrics**（AUPRC）才能暴露真实失效模式。
- **绝对数量优先**：在scFM微调中，罕见类的可修复性由其**绝对训练样本数**（而非占比或全局不平衡比）主导，这颠覆了传统长尾学习中“相对频率决定权重”的直觉，提示数据收集应聚焦于填补绝对空缺。
- **几何先于损失**：嵌入空间的几何属性（NC1、最近邻熵、UMAP吸收）可在训练前或训练初期诊断失效类型，是比盲目尝试损失函数更高效的调试路径。
- **损失即权衡**：长尾损失不是“增强器”，而是“调节器”——logit adjustment提升recall以牺牲precision为代价，class-balanced loss则平衡提升两者，选择需匹配下游任务成本（如漏诊vs误诊代价）。
- **信号存在≠可用**：线性探针证明，即使在严重纠缠类中，判别信号仍线性可分，说明当前损失函数家族未能充分激发该信号，为设计新损失（如几何感知损失）提供明确靶点。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的“双轨失效”框架（loss-sensitive vs. severely entangled）与计算机视觉中“minority collapse”理论（Fang et al. 2021）形成呼应，但将其首次实证落地于单细胞领域，并赋予生物学解释（如phagocyte的myelin ingestion导致转录重叠）。
- **候选连接/方法论连接**：使用NC1量化嵌入几何，直接继承Papyan et al. (2020) 的神经坍塌理论，但创新性地将其应用于scFM长尾诊断，而非仅作为训练动态观察。
- **候选连接/方法论连接**：线性探针验证信号存在，延续Alain & Bengio (2017) 的probe范式，但将其用于区分“数据稀缺”与“损失设计不足”，拓展了probe在生物AI中的诊断价值。
- **候选连接/方法论连接**：强调绝对样本数而非相对频率，与Buda et al. (2018) 在CV中发现的“effective number of samples”框架一致，证实该规律跨模态稳健，但在scFM中首次量化验证。
- **弱连接/方法论连接**：虽未涉及spatial transcriptomics、graph neural networks或multi-omics，但其几何诊断方法（UMAP/NC1/nearest-neighbor）可直接迁移至空间转录组嵌入分析；其损失比较框架可扩展至多组学融合模型的模态不平衡处理。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometric-aware loss reweighting  
  **originating limitation/observation**: NC1 and nearest-neighbor entropy diagnose entanglement but current losses ignore geometry [Paper] [Paper: PDF p. 6]; linear probe shows signal exists but is unused [Paper] [Paper: PDF p. 6]  
  **core hypothesis**: Incorporating NC1 and neighbor entropy into loss weighting (e.g., down-weighting classes with high NC1 or high absorption entropy) will improve recovery of severely entangled classes without harming others  
  **delta from paper**: Replaces static class-frequency weights with dynamic geometry-aware weights computed from frozen embeddings  
  **initial method**: For each class c, compute weight w<sub>c</sub> = α × exp(−β × NC1<sub>c</sub>) + γ × exp(−δ × entropy<sub>c</sub>); use w<sub>c</sub> in class-balanced loss formulation  
  **validation**: Train scGPT on MS with new loss; compare F1 for oligodendrocyte C/phagocyte vs. baseline class-balanced loss; ablate α, β, γ, δ  
  **failure modes**: Over-smoothing (w<sub>c</sub> → 0 for all c) if β/δ too large; instability if NC1/entropy noisy on small n  
  **innovation status**: unverified  

- **name**: Entanglement-aware data augmentation  
  **originating limitation/observation**: Severely entangled classes have n=3 samples, causing geometric absorption [Paper] [Paper: PDF p. 5]; synthetic oversampling (Bej et al. 2021) is generic, not geometry-informed  
  **core hypothesis**: Augmenting rare classes by interpolating toward their dominant confusion partners (e.g., phagocyte → oligodendrocyte A) will create geometrically plausible synthetic samples that break absorption  
  **delta from paper**: Moves beyond random/synthetic oversampling to biologically grounded, geometry-targeted augmentation  
  **initial method**: For phagocyte (n=3), generate 10 synthetic cells via convex combination with oligodendrocyte A centroid (weight 0.7) and phagocyte centroid (weight 0.3); add to training set  
  **validation**: Compare F1 for phagocyte under augmented vs. non-augmented training with class-balanced loss; verify reduced absorption in UMAP (Figure 4)  
  **failure modes**: Overfitting to interpolation direction; creating samples that reinforce wrong biology (e.g., if oligodendrocyte A is not true biological parent)  
  **innovation status**: unverified  

- **name**: Multi-loss ensemble for rare-class calibration  
  **originating limitation/observation**: Different losses trade precision/recall differently (Fig 2 right) [Paper] [Paper: PDF p. 4]; no single loss dominates all rare classes (Table 1)  
  **core hypothesis**: Ensembling predictions from multiple losses (e.g., class-balanced for precision, logit-adjusted for recall) with class-specific gating will outperform any single loss on rare-class AUPRC  
  **delta from paper**: Shifts from selecting one best loss to dynamically combining complementary losses per class  
  **initial method**: Train 6 models (one per loss); for each rare class c, learn gating weights via logistic regression on validation set to maximize c’s F1; apply gated average at test time  
  **validation**: Measure rare-class macro-AUPRC on MS test set; compare to best single loss (class-balanced: 0.734)  
  **failure modes**: Gating overfits to validation set; increased inference latency; no guarantee of monotonic AUPRC improvement  
  **innovation status**: unverified