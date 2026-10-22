> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: discovery  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|---------|
| Title | Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions | [Paper] [Paper: PDF p. 1] |
| Authors | Zeyu Dong, Jiahui Zhong | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint | [Paper] [Paper: PDF p. 1] |
| URL | http://arxiv.org/abs/2609.23325v1 | [Paper metadata] |
| PDF URL | https://arxiv.org/pdf/2609.23325v1 | [Paper metadata] |
| Publication date | 2026-09-20 | [Paper metadata] |
| Code availability | https://github.com/jz890/sc-imbalance | [Paper] [Paper: PDF p. 7] |
| Field | single-cell foundation models, long-tail learning, class imbalance, loss function design | [Paper] [Paper: PDF p. 1–2] |
| Core datasets | Multiple Sclerosis (MS), Zheng68K, human Pancreas | [Paper] [Paper: PDF p. 2–3] |
| Core backbones | scGPT, scBERT, Geneformer | [Paper] [Paper: PDF p. 2–3] |
| Evaluated losses | CE, weighted CE, class-balanced loss, focal loss, LDAM, logit-adjusted softmax | [Paper] [Paper: PDF p. 3] |
| Total runs | 162 (3 backbones × 3 datasets × 6 losses × 3 seeds) | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结

该论文系统评估了六种长尾损失函数在三种单细胞基础模型（scGPT/scBERT/Geneformer）和三个真实数据集（MS/Zheng68K/Pancreas）上的泛化能力，发现整体准确率严重掩盖罕见细胞类型（如疾病相关病理亚群）的系统性失败；作者揭示罕见类失败存在两种机制可区分的范式——“损失敏感型”（可通过损失选择恢复）与“严重纠缠型”（所有损失均失效），并证明前者收益由绝对训练样本数而非相对频率决定；该工作提供了首个可复现、机制驱动的单细胞长尾基准与实用指南，直击single-cell foundation models在临床级细粒度泛化中的关键瓶颈。

## 03 研究问题

论文聚焦于：**当单细胞基础模型在标准benchmark上报告高准确率（如97.5%）时，其对罕见细胞类型的分类失败是否具有系统性、可诊断、且可干预的机制？**  
作者不满足于观察“性能下降”的现象，而是追问：这种失败是源于预训练偏差、数据结构固有缺陷、还是损失函数设计失配？若可干预，哪些损失函数最鲁棒？其有效性是否依赖于特定架构？更重要的是，是否存在一种先验可判别的几何信号，能提前区分“换损失就能救”和“换啥损失都白搭”的两类罕见类？这些问题共同构成一个闭环：从现象→归因→诊断→干预→验证。

## 04 研究背景与发展路径

单细胞基础模型（scGPT/scBERT/Geneformer）已成为细胞类型注释默认主干，但其高聚合准确率被证实由常见细胞类型主导 [Paper] [Paper: PDF p. 1]；罕见细胞（如早期过渡态、病理亚群）的系统性失败已被多个研究记录（Alsabbagh et al. 2023; Naziri et al. 2025），但此前工作集中于采样策略（如随机过采样）或专用模型设计（Zhao et al. 2025），尚未在损失函数层面进行跨架构控制实验 [Paper] [Paper: PDF p. 1–2]。本文承接Alsabbagh等人的采样基准，将变量轴切换至损失函数，并固定采样分布与批次构成，以隔离损失选择的独立效应 [Paper] [Paper: PDF p. 2]；同时区别于Representation-level方法（如Weerasekara et al. 2026的post-pretraining原型重塑），本文专注loss-level干预——即直接替换分类头损失，与预训练主干无缝组合，提供更轻量、更易部署的实践路径 [Paper] [Paper: PDF p. 2]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|----------------------------|--------------------------|
| **Aggregate metrics mask rare-class failure** | Accuracy > Macro-F1 > rare-class recall across all 9 (backbone, dataset) settings [Paper] [Paper: PDF p. 3] | Dataset structure—not pretraining—drives the gap; common classes dominate accuracy while rare ones collapse [Paper] [Paper: PDF p. 1, 3] | Figure 2 (left): Pancreas shows highest accuracy but largest drop to rare-recall; Table 1 shows consistent ordering across all columns [Paper] [Paper: PDF p. 3–4] |
| **Loss functions fail on a subset of rare classes regardless of architecture** | Two MS classes (oligodendrocyte C, phagocyte) achieve near-zero F1 under *all* six losses and *all* three backbones [Paper] [Paper: PDF p. 5] | Insufficient training samples (n=3 each) + real transcriptional overlap (e.g., phagocyte ingests oligodendrocyte RNA) → geometric absorption into neighbor classes [Paper] [Paper: PDF p. 5–6] | Figure 3 (left): two darkest rows across all three backbone columns; Figure 4: UMAP shows both classes embedded inside unrelated classes’ neighborhoods; Section 5.1 confirms same failure in non-foundation baselines (5-NN, RF) [Paper] [Paper: PDF p. 5–7] |
| **Reweighting efficacy is misattributed to relative frequency** | Weighted CE performs best on MS (most imbalanced *ratio*) but worst on Zheng68K (less imbalanced ratio yet higher absolute rare-class counts) [Paper] [Paper: PDF p. 4] | Absolute training-set size—not class share or dataset imbalance ratio—predicts ∆F1 gain; smaller absolute n → larger reweighting benefit [Paper] [Paper: PDF p. 4] | Figure 3 (right): strong negative Pearson correlation (r = −0.77, p < 0.001) between log(training size) and ∆F1,c; MS rare classes have smallest absolute counts despite comparable ratio to Zheng68K [Paper] [Paper: PDF p. 4] |
| **Losses make hidden trade-offs obscured by Macro-F1** | Logit adjustment boosts rare-recall but incurs largest precision penalty among all six losses [Paper] [Paper: PDF p. 4] | It shifts decision thresholds rather than improving feature separability → more false positives [Paper] [Paper: PDF p. 4] | Figure 2 (right): logit-adjusted point lies far below y=x line; Table 1 shows it has lowest rare-precision (0.632 vs CE’s 0.664 on Zheng68K) despite highest rare-recall (0.685) [Paper] [Paper: PDF p. 4–5] |

## 06 核心思想

论文的核心思想是：**单细胞长尾泛化失败不是单一维度问题，而是一个具有可诊断几何根源的双模态现象，其干预策略必须分层设计——先用嵌入几何指标（如NC1、最近邻熵）预筛“可救”与“不可救”类，再对前者匹配损失函数，且该匹配应基于绝对样本数而非相对频率。**  
这一思想源于对现象的深度解耦：作者观察到Figure 3左图中F1热图呈现三段式分布（全黑→灰度渐变→全亮），进而提出假设：黑色区域反映数据稀缺+生物学纠缠的双重瓶颈，灰色区域反映损失函数与表示能力的错配，白色区域则说明CE已足够。后续Figure 4的UMAP可视化与Section 5.2的NC1量化分析共同验证了该假设——几何吸收（absorption）与神经坍缩（neural collapse）指标能提前标记出损失无效区，从而将“调参”升级为“诊断-决策”流程。

## 07 方法总览

论文采用**控制变量+多维诊断**方法论：（1）构建162-run正交实验矩阵（3 backbones × 3 datasets × 6 losses × 3 seeds），所有超参取默认值以评估off-the-shelf鲁棒性 [Paper] [Paper: PDF p. 3]；（2）定义严格评估协议：使用10%训练数据作验证集选checkpoint，测试集仅评估一次，罕见类定义为训练集频率<5% [Paper] [Paper: PDF p. 3]；（3）引入三类互补诊断工具：a) 几何分析（UMAP可视化、NC1 trace ratio、最近邻熵）定位嵌入空间失败模式 [Paper] [Paper: PDF p. 6–7]；b) 线性探针（linear probe）在冻结嵌入上独立训练，分离表示能力与分类器训练瓶颈 [Paper] [Paper: PDF p. 6]；c) 跨架构一致性检验（如phagocyte在scGPT/scBERT/Geneformer下均被oligodendrocyte A误判）排除架构特异性噪声 [Paper] [Paper: PDF p. 6]。整个方法链路清晰指向机制归因，而非经验调优。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|-------------------|------------------------|-----------------------------------|
| **Loss-function grid** | Systematically compare six long-tail losses (CE, weighted CE, class-balanced, focal, LDAM, logit-adjusted) | Isolate loss-axis effect from sampling/architecture confounders; test off-the-shelf robustness without hyperparameter tuning | Input: logits + ground truth; Output: scalar loss per sample | Table 1 reports rankings; Section 4.2 identifies class-balanced/LDAM as most consistent [Paper] [Paper: PDF p. 3–4] | Would collapse study to single baseline (CE), losing ability to distinguish loss-sensitive vs. entangled regimes (Figure 3 left) [Paper] [Paper: PDF p. 5] |
| **Embedding geometry analyzer** | Compute NC1 = tr(ΣW)/tr(ΣB), nearest-neighbor entropy, and UMAP visualization on frozen test embeddings | Diagnose whether rare-class failure stems from representation collapse (high NC1) or classifier miscalibration (low NC1 but high confusion) | Input: frozen test-set embeddings + labels; Output: NC1 per class, entropy per class, visual clusters | Figure 4 shows absorption; Section 5.2 reports oligodendrocyte C’s high NC1 (1.19–1.79) vs. phagocyte’s low NC1 (0.17–0.32) [Paper] [Paper: PDF p. 6–7] | Without NC1/nearest-neighbor analysis, “severely entangled” would remain anecdotal; no basis to claim geometric signature precedes loss choice [Paper] [Paper: PDF p. 6] |
| **Linear probe module** | Fit class-balanced logistic regression on frozen CE-fine-tuned embeddings (5-fold CV) | Decouple representation quality from classifier training dynamics; test if discriminative signal exists but is unused | Input: frozen embeddings + labels; Output: CV-F1 per class | Section 5.3: probe achieves F1=0.175–0.465 on entangled classes, exceeding best trained head (0.000–0.329) [Paper] [Paper: PDF p. 6] | Removal would leave bottleneck attribution ambiguous—could not conclude failure lies in loss design rather than data scarcity alone [Paper] [Paper: PDF p. 6] |
| **Absolute-size correlator** | Correlate ∆F1,c = max<sub>ℓ</sub> F<sup>(ℓ)</sup><sub>1,c</sub> − F<sup>(CE)</sup><sub>1,c</sub> with log(training size) per rare class | Challenge assumption that reweighting benefit scales with relative frequency; identify actionable predictor for loss selection | Input: per-class ∆F1,c and training count; Output: Pearson r, p-value | Figure 3 (right): r = −0.77 (p < 0.001) for n=19 recoverable classes [Paper] [Paper: PDF p. 4] | Without this analysis, guideline “use class-balanced loss for rare classes” remains generic; no basis to prioritize which rare classes to target first [Paper] [Paper: PDF p. 4] |

## 09 关键公式与符号

- **No verifiable closed-form equations are presented in the paper.** All listed equations are partial fragments extracted from context, lacking full derivation or standalone definition:
  - Equation 1: `Macro-F1 = 1/C Σ_{c=1}^C F1,c` — standard macro-averaged F1 definition [Paper] [Paper: PDF p. 3]
  - Equation 2: `Recall_R = 1/|R| Σ_{c∈R} Recall_c` — rare-class macro-recall over set R of rare classes (defined as training frequency <5%) [Paper] [Paper: PDF p. 3]
  - Equation 3: `∆F1,c = max_{ℓ∈L} F^{(ℓ)}_{1,c} − F^{(CE)}_{1,c}` — per-class F1 gain from best loss over CE [Paper] [Paper: PDF p. 4]
  - Equation 4: `NC1 = tr(Σ_W) / tr(Σ_B)` — neural collapse trace ratio; Σ_W = average within-class scatter, Σ_B = between-class scatter of centroids [Paper] [Paper: PDF p. 6]
- **Key symbols/variables:**
  - `R`: set of rare classes (training frequency <5%) [Paper] [Paper: PDF p. 3]
  - `L`: set of six evaluated losses {CE, weighted CE, class-balanced, focal, LDAM, logit-adjusted} [Paper] [Paper: PDF p. 4]
  - `NC1`: lower values indicate tighter, better-separated clusters; used to quantify embedding geometry [Paper] [Paper: PDF p. 6]
  - `∆F1,c`: per-class F1 improvement metric central to Section 4.3’s core finding [Paper] [Paper: PDF p. 4]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|------------------------------|--------|
| **Aggregate metric gap analysis** | Aggregate accuracy masks rare-class failure across architectures | Compare accuracy, Macro-F1, rare-recall under plain CE across all 9 (backbone, dataset) cells | Accuracy > Macro-F1 > rare-recall in all 9 cases (e.g., scBERT/MS: 0.858 > 0.639 > 0.596) | Gap is inherent to data imbalance structure, not backbone-specific | That pretraining is irrelevant—authors note variance arises from config differences, not pretraining bias [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3], Figure 2 (left), Table 1 |
| **Loss ranking by Macro-F1 & rare-AUPRC** | Class-balanced loss and LDAM are most consistent generalists | Rank each loss by mean position across 9 (backbone, dataset) cells; also rank by rare-class macro-AUPRC | Class-balanced: mean rank 2.4 (F1), 0.734 (AUPRC); LDAM: 2.6 (F1), 0.690 (AUPRC); logit-adjusted: 5.2 (F1), 0.700 (AUPRC) | Class-balanced is strongest balanced performer; LDAM trades calibration for boundary shaping | That LDAM is universally superior—it underperforms on AUPRC and shows dataset-specific variance [Paper] [Paper: PDF p. 3–4] | [Paper] [Paper: PDF p. 3–4], Table 1 |
| **∆F1,c vs. log(training size) regression** | Absolute training-set size predicts reweighting benefit | Correlate ∆F1,c with log(count) for all rare classes (n=19 recoverable + 4 entangled) | Strong negative correlation: r = −0.77 (p < 0.001, n=19); robust to exclusion thresholds | Benefit scales with scarcity, not relative frequency; explains why MS gains more than Zheng68K | That this holds for *all* rare classes—4 entangled classes break the trend and are excluded from primary fit [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 3 (right) |
| **Logit adjustment precision-recall trade-off** | Logit adjustment trades rare-class precision for recall | Plot rare-precision vs. rare-recall for all losses (averaged over 9 cells); compute spreads | Logit-adjusted has lowest precision (0.632) but highest recall (0.685) on Zheng68K; 10.6-point spread in rare-precision vs. 5.9-point in rare-recall | Trade-off is loss-specific and concentrated in rare classes; not an artifact of threshold choice | That it degrades non-rare performance—non-rare precision/recall spreads are only 1.1/2.1 points [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 4], Figure 2 (right), Table 1 |
| **Linear probe on frozen embeddings** | Discriminative signal exists for entangled classes but is unused by trained heads | Fit class-balanced logistic regression on frozen CE embeddings (5-fold CV); compare to best trained F1 | Probe achieves F1=0.175–0.465 on oligodendrocyte C/phagocyte, exceeding best trained head (0.000–0.329) | Bottleneck is in classifier training (loss design), not representation collapse | That nonlinear probes would close the gap—no test of expressive classifiers beyond linear [Paper] [Paper: PDF p. 6] | [Paper] [Paper: PDF p. 6], Section 5.3 |

## 11 对结论的正确理解

论文结论**不可简化为“换损失就能提升罕见类性能”**。正确理解必须包含三层限定：（1）**适用范围限定**：结论仅适用于“损失敏感型”罕见类（Figure 3左图中非全黑行），对“严重纠缠型”（两全黑行）完全不适用，后者需数据增补或拒判（reject-option）；（2）**预测依据限定**：重加权收益由绝对训练样本数预测（Figure 3右图），而非相对频率或数据集不平衡比——这意味着在Zheng68K中训练数≈70的罕见类，其收益远低于MS中训练数=3的同类，即使前者相对频率更低；（3）**指标解读限定**：Macro-F1提升不等于均衡改善，logit调整的F1增益伴随精度显著下降（Figure 2右图），其本质是阈值偏移而非特征解耦。因此，“class-balanced loss is recommended” 的真正含义是：在损失敏感型、绝对样本稀疏（<50）的罕见类上，它提供最稳健的F1与精度-召回平衡。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| **Limited backbone coverage** | Only scGPT, scBERT, Geneformer evaluated; scFoundation and CellPLM untested | Extend benchmark to other existing single-cell foundation models (scFoundation, CellPLM) [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Classifier expressivity ceiling** | Linear probe outperforms trained heads on entangled classes, suggesting room for improvement with more expressive classifiers | Test nonlinear classifier heads (beyond linear probe) to extract additional signal from frozen representations [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |
| **Isolated imbalance axis** | Study focuses solely on cell-type class imbalance; ignores compounding variables like demographic composition or batch effects | Investigate interactions between class imbalance and demographic composition (Al Amin et al. 2025) or batch effects (Maan et al. 2024) [Paper] [Paper: PDF p. 7] | [Paper] [Paper: PDF p. 7] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| **NC1’s sensitivity to small-n classes may confound interpretation** | Phagocyte’s low NC1 (0.17–0.32) is attributed to tight clustering inside another class, but NC1 denominator tr(Σ_B) shrinks when centroid distances collapse—low NC1 could reflect global embedding collapse, not local absorption | Misattribution could lead to false confidence in representation quality for tiny classes; undermines NC1’s use as a standalone diagnostic | Compute NC1 on subsampled versions of larger classes (e.g., downsample oligodendrocyte A to n=3) and compare NC1 distributions; or use alternative metrics like Silhouette score per class | [Paper] [Paper: PDF p. 6]: “phagocyte’s small cell count means a handful of tightly clustered cells embedded inside another class’s region can produce low within-class scatter despite total confusability” — acknowledges small-n bias but doesn’t validate NC1’s robustness |
| **Linear probe’s 5-fold CV may overestimate separability** | Probe is trained/tested on *frozen test-set embeddings*, meaning no train/test split—CV internal to test set measures memorization capacity, not generalization | If probe overfits test embeddings, its superior F1 doesn’t prove signal is generalizable; weakens claim that “bottleneck is in loss design” | Repeat probe on *train-set embeddings only*, using standard train/test split, and report generalization gap (test F1 vs. CV F1); compare to trained head’s test F1 | [Paper] [Paper: PDF p. 6]: “measuring CV-internal separability, not train/test generalization” — explicitly states limitation but doesn’t quantify its impact |
| **“Severely entangled” label conflates data scarcity and biology** | Oligodendrocyte C’s confusion with excitatory neurons is attributed to shared self-antigen presentation (B2M, HLA-C), yet its n=3 makes it impossible to disentangle whether biology or scarcity dominates | Blurring these causes risks misallocating resources—e.g., prioritizing wet-lab validation of biological overlap over data collection | Synthesize additional oligodendrocyte C cells via generative models (e.g., scGen) and retrain; if F1 improves significantly, scarcity dominates; if confusion persists, biology dominates | [Paper] [Paper: PDF p. 6]: “oligodendrocyte C is an MS-specific pathological subcluster; its confusion... reflects shared self-antigen-presentation” — cites biology but provides no ablation of scarcity |

## 14 学到的知识

- **单细胞长尾失败是双模态的**：不能笼统说“罕见类性能差”，必须区分“损失敏感型”（换LDAM/class-balanced可救）与“严重纠缠型”（所有损失均失效），后者需几何诊断先行。
- **绝对样本数是关键预测器**：在单细胞场景中，重加权收益由罕见类的绝对训练样本数（而非占比）决定，这颠覆了传统长尾学习中强调“有效样本数”相对比例的直觉，对实验设计有直接指导意义——优先为n<10的类收集数据。
- **几何指标可前置诊断**：NC1 trace ratio与最近邻熵能在不训练任何分类器前，从冻结嵌入中识别出注定失败的类（如oligodendrocyte C的NC1=1.79），使计算资源聚焦于可优化区域。
- **Macro-F1是危险的平滑器**：它掩盖了logit调整“用精度换召回”的本质（Figure 2右图），实践中必须联合查看精度-召回曲线或AUPRC。
- **线性探针是解耦利器**：在冻结嵌入上独立训练线性分类器，能清晰分离表示能力（probe性能）与分类器训练瓶颈（trained head性能），本文用此证明损失设计是主要瓶颈。

## 15 与既有知识的连接

- **候选连接/方法论连接**：本文的“损失敏感 vs. 严重纠缠”二分法，与Kang et al. (2020)提出的representation-classifier decoupling框架高度呼应——前者对应classifier calibration failure（可解耦优化），后者对应representation failure（需新数据或新预训练）。本文用线性探针实证了该框架在单细胞领域的适用性 [Paper] [Paper: PDF p. 6]。
- **候选连接/方法论连接**：NC1计算直接继承自Papyan et al. (2020)的neural collapse理论，并首次将其应用于单细胞长尾诊断，将经典模式识别指标（Fisher ratio）与现代foundation model瓶颈关联 [Paper] [Paper: PDF p. 6]。
- **候选连接/方法论连接**：绝对样本数预测∆F1,c的发现，与Cui et al. (2019)的effective-number-of-samples框架形成张力——后者强调相对频率修正，本文证明在单细胞小样本 regime 下，绝对计数更具判别力，提示该框架需针对生物数据特性校准 [Paper] [Paper: PDF p. 4]。
- **弱连接/方法论连接**：用户研究方向中的graph neural networks与spatial transcriptomics未被本文覆盖，但其几何诊断思路（如UMAP、NC1）可迁移至空间图嵌入的neighborhood absorption分析；multi-omics对齐亦可借鉴“冻结表示+线性探针”范式解耦模态特异性瓶颈。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Geometry-Guided Loss Selection Pipeline  
  **originating limitation/observation**: Authors show NC1 and nearest-neighbor entropy diagnose “severely entangled” classes pre-training, but don’t integrate this into automated loss selection [Paper] [Paper: PDF p. 6–7].  
  **core hypothesis**: A pipeline that first computes NC1/entropy on frozen backbone embeddings, then routes classes to loss functions (e.g., class-balanced for NC1 < 0.8, abstain for NC1 > 1.5), will outperform uniform loss application.  
  **delta from paper**: Adds conditional routing layer atop the static loss grid; uses geometry as gatekeeper.  
  **initial method**: On MS dataset, compute NC1 per class on scGPT CE embeddings; assign class-balanced loss to classes with NC1 < 0.8, LDAM to 0.8–1.5, and reject-option (output “insufficient data”) to NC1 > 1.5; evaluate rare-class F1 gain vs. uniform class-balanced.  
  **validation**: Compare rare-class F1 and precision-recall curves; measure % of entangled classes correctly routed to reject.  
  **failure modes**: NC1 threshold may not generalize across datasets/backbones; reject-option lacks clinical utility without uncertainty quantification.  
  **innovation status**: unverified  

- **name**: Absolute-Count Adaptive Reweighting  
  **originating limitation/observation**: Paper finds absolute training size predicts ∆F1,c, but all reweighting losses use fixed formulas (e.g., inverse-frequency) not tuned to absolute n [Paper] [Paper: PDF p. 4].  
  **core hypothesis**: A reweighting scheme where class weight = f(n_c) with f learned from the ∆F1,n curve (Figure 3 right) will outperform static reweighting.  
  **delta from paper**: Replaces hand-designed weight functions (e.g., Cui et al. 2019) with data-driven, absolute-count-aware weights.  
  **initial method**: Fit a spline to Figure 3’s (log n_c, ∆F1,c) points; use predicted ∆F1,c as weight multiplier in loss; train on MS and test generalization to Zheng68K.  
  **validation**: Compare Macro-F1 and rare-AUPRC against class-balanced loss; check if weight distribution correlates with actual ∆F1 gain.  
  **failure modes**: Overfitting to MS’s specific n_c distribution; fails if ∆F1,n relationship is dataset-specific.  
  **innovation status**: unverified  

- **name**: Entanglement-Aware Perturbation Prediction  
  **originating limitation/observation**: “Severely entangled” classes (e.g., oligodendrocyte C) show transcriptional overlap with confusers (excitatory neurons) due to shared stress markers (B2M, HLA-C) [Paper] [Paper: PDF p. 6]; user’s perturbation prediction interest aligns with modeling such biological entanglement.  
  **core hypothesis**: Modeling the entanglement as a latent perturbation (e.g., “myelin stress → oligodendrocyte C → excitatory neuron marker expression”) enables synthetic data generation that improves classification.  
  **delta from paper**: Shifts from diagnosing failure to generating corrective interventions using biological priors.  
  **initial method**: Train a VAE on oligodendrocyte C and excitatory neuron cells; use latent space interpolation to generate hybrid cells; augment MS training set and retrain scGPT with class-balanced loss.  
  **validation**: Measure F1 gain on oligodendrocyte C; verify generated cells express expected stress markers (B2M) via gene-level metrics.  
  **failure modes**: Generated cells may not capture true biological transitions; VAE may collapse to mean.  
  **innovation status**: unverified