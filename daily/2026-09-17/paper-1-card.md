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
| Title | STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images | [Paper: PDF p. 1] |
| Authors | Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al. | [Paper: PDF p. 1] |
| Venue | arXiv | [Paper metadata] |
| Year | 2026 | [Paper metadata] |
| Core contribution | First large-scale, standardized, multi-platform benchmark (STP-BENCH) for virtual ST models, enabling controlled comparison of 21 architectures under unified PFM encoding, gene-level interpretability analysis, and downstream biological utility evaluation | [Paper: PDF p. 2–4, Fig. 1] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium+Xenium); STP-BENCH-EXTERNAL (185,831 spots, same 6 cancers, cross-institution/tissue/platform) | [Paper: PDF p. 4–5, Fig. 1b] |
| Evaluated models | 21 models: 14 regression-based (e.g., TRIPLEX, DeepSpot, CFANet), 4 bi-modal retrieval (e.g., BLEEP, mclSTExp), 3 generative (e.g., STFlow, Stem) | [Paper: PDF p. 6–7, Fig. 1c] |
| Primary encoder | UNIv2 pathology foundation model (PFM), used as default patch encoder where architecturally compatible; exceptions noted (e.g., OmiCLIP, M2OST, M2ORT, HistoSPACE, ST-Net) | [Paper: PDF p. 7–9, 22–23] |
| Main metrics | Pearson Correlation Coefficient (PCC) [Eq. 1], Mean Absolute Error (MAE) [Eq. 2], Structural Similarity Index Measure (SSIM) | [Paper: PDF p. 31–32, Eq. 1–2] |
| Gene sets | HMHVGs (200 high-mean highly-variable genes); 16 TME marker genes (e.g., CD3E, ACTA2, PDCD1) | [Paper: PDF p. 7, 33] |
| Downstream tasks | Cell type deconvolution (Cell2location), spatial domain identification (SpaGCN + ARI), gene set scoring (singscore) | [Paper: PDF p. 14–15, Fig. 4; p. 35–36] |
| Robustness axes | Cross-Institution, Cross-Tissue, Cross-Platform generalization; intra-/inter-cohort data scaling | [Paper: PDF p. 16–18, Fig. 5] |

## 02 一句话总结  
该论文构建了STP-BENCH——首个大规模、跨平台、标准化的虚拟空间转录组（virtual ST）系统性基准，覆盖Visium与Xenium双平台、6种癌症、超79万spots；通过统一采用UNIv2等病理基础模型（PFM）作为图像编码器，解耦了模型架构创新与图像表征能力，发现多数现有模型未超越线性探针基线；进一步揭示基因可预测性存在“形态学天花板”，且多尺度架构（如TRIPLEX、DeepSpot）在基质/免疫相关通路中展现出显著优势，为single-cell foundation models与spatial transcriptomics的交叉对齐提供了关键评估框架与实证约束。

## 03 研究问题  
论文直面虚拟ST领域长期存在的**评估不可靠性问题**：当不同研究使用异构小数据集、不一致训练流程、各自原生图像编码器（如ResNet50 vs ViT-L）、且仅报告平均基因精度时，模型性能比较本质上是混淆的。作者追问：若剥离图像编码器差异，真实架构贡献几何？哪些基因/通路可被可靠地从形态学推断？这种推断能否支撑下游生物学分析（如细胞类型反卷积）？模型在现实域偏移（跨医院、跨癌种、跨平台）下是否鲁棒？这些问题共同指向一个核心：**如何建立公平、可复现、多层次、生物学可解释的虚拟ST评估范式？**

## 04 研究背景与发展路径  
虚拟ST起源于ST实验成本高昂的现实约束，其方法论已分化为三大流派：回归式（ST-Net→TRIPLEX/DeepSpot）、双模态对齐式（BLEEP→mclSTExp）、生成式（STFlow/Stem）。早期工作受限于小规模数据（如HEST-1K仅千级spots）和零散评估，导致结论不可比：Wang et al. [50] 保留各模型原生编码器，混淆架构与特征；HEST-1K [51] 仅用PFM嵌入+简单回归，未评估完整模型栈。STP-BENCH并非延续单点技术改进，而是**自上而下重构评估基础设施**——以“统一编码器+多平台大数据+多层次验证”为三支柱，将评估从“谁跑得快”升级为“谁真正理解形态-表达映射”。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|----------------------------|-------------------------|
| **Encoder-architecture confounding** | Model rankings shift dramatically when native encoders are replaced with UNIv2 (e.g., CFANet jumps from 16th to 6th) | Prior works inherit original image backbones trained on disparate domains/scales (ImageNet vs pathology WSIs), making architectural gains indistinguishable from feature quality | [Paper: PDF p. 9, Fig. 2b]; [Paper: PDF p. 18–19] |
| **Gene-level opacity** | Marker genes (e.g., CD3E, PDCD1) show consistently low PCC (~0.2) vs HMHVGs (~0.4), yet no prior work systematically dissected *which* genes are predictable | Evaluation focused on aggregate metrics obscures biological specificity; predictability is gene-intrinsic, not model-dependent | [Paper: PDF p. 9, Fig. 2a]; [Paper: PDF p. 11, Fig. 3a]; [Paper: PDF p. 19] |
| **Downstream irrelevance** | Models may fit gene expression but fail at cell-type deconvolution or spatial domain detection | Spot-level correlation ≠ biological utility; lack of validation on functional granularities limits translational credibility | [Paper: PDF p. 14–15, Fig. 4]; [Paper: PDF p. 19] |
| **Robustness illusion** | Cross-tissue generalization gaps reach −0.35 PCC, far worse than cross-institution (−0.10), yet most papers report only in-distribution performance | Morphology-to-expression mapping is highly tissue-specific; batch effects are secondary to biological heterogeneity | [Paper: PDF p. 17, Fig. 5b middle]; [Paper: PDF p. 19] |
| **Data scaling fallacy** | Inter-cohort scaling (BRCA+LUAD+PRAD) often *lowers* performance on target tissue (negative transfer) | Simple aggregation of heterogeneous tissues ignores tissue-specific morphological priors; “more data” ≠ “better data” without domain adaptation | [Paper: PDF p. 18, Fig. 5d]; [Paper: PDF p. 19] |

## 06 核心思想  
STP-BENCH的核心思想是**将评估本身升维为科学问题**：它拒绝将虚拟ST视为单一预测任务，而是定义为一个**多粒度验证管道**——从像素（patch encoder choice）、基因（HMHVG vs marker）、通路（GO gene sets）、细胞（Cell2location）、组织（SpaGCN domains）到系统（cross-tissue robustness）。其底层假设是：**真正的虚拟ST模型必须在所有层级上保持一致性**；若某模型在基因层面PCC高但细胞丰度相关性低，则其预测是统计幻觉而非生物学可信。因此，STP-BENCH不是提供“SOTA榜单”，而是绘制一张**可解释的性能地形图**，标定每个模型的能力边界与失效模式。

## 07 方法总览  
STP-BENCH的方法论是“控制变量+多轴验证”：（1）**统一编码器层**：强制UNIv2（或Virchow2/H-Optimus1等）作为patch encoder，仅对架构不兼容者（M2OST/M2ORT/OmiCLIP等）豁免；（2）**分层评估层**：① spot-level（PCC/MAE/SSIM），② gene-level（heatmap + margin analysis），③ gene-set-level（singscore），④ cellular-level（Cell2location PCC），⑤ tissue-level（SpaGCN ARI）；（3）**鲁棒性压力测试层**：Cross-Institution/Tissue/Platform三类域偏移 + intra-/inter-cohort数据缩放。整个流程确保任何性能差异都可归因于模型架构本身，而非数据或特征工程偏差。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **UNIv2-standardized patch encoder** | Extracts morphology-aware embeddings from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability; PFMs capture histomorphology better than ImageNet models | Input: H&E patch → Output: d-dim embedding (e.g., 1024-dim) | [Paper: PDF p. 7–10, Fig. 2e]; [Paper: PDF p. 22–23] | Severe ranking distortion (Fig. 2b); models like CFANet collapse without PFM [Paper: PDF p. 9] |
| **HMHVG + TME marker gene panel** | Defines evaluation targets: 200 highly expressed/variable genes + 16 biologically annotated markers | To move beyond arbitrary gene lists and probe specific biological programs (e.g., immune checkpoints) | Input: Gene symbols → Output: Two disjoint gene sets for stratified evaluation | [Paper: PDF p. 7, 33]; [Paper: PDF p. 9, Fig. 2a] | Loss of biological interpretability; inability to explain why marker genes underperform [Paper: PDF p. 9–10] |
| **Gene-wise PCC heatmap (Fig. 3a)** | Visualizes per-gene predictability across all 20 models | To identify intrinsic gene-level ceilings independent of architecture | Input: Predicted & ground-truth expression per spot → Output: 200×20 matrix of PCC values | [Paper: PDF p. 11, Fig. 3a]; [Paper: PDF p. 19] | Obscures universal predictability patterns; prevents discovery of stromal/immune gene advantages [Paper: PDF p. 13] |
| **Cell2location deconvolution pipeline** | Estimates spatial cell-type abundances from predicted expression matrices | To test if virtual ST preserves cellular composition structure, not just gene counts | Input: Virtual ST AnnData → Output: Per-spot cell-type abundance vectors → PCC vs ground-truth | [Paper: PDF p. 14–15, Fig. 4a]; [Paper: PDF p. 35] | Breaks downstream utility chain; TRIPLEX/DeepSpot superiority would remain invisible [Paper: PDF p. 14] |
| **Cross-Platform (Visium→Xenium) evaluation** | Tests generalization from spot-level (Visium) to single-molecule (Xenium) resolution | To assess if models trained on lower-resolution data can leverage higher-sensitivity platforms | Input: Visium-trained model → Output: PCC on Xenium pseudo-spots | [Paper: PDF p. 16–17, Fig. 5a right]; [Paper: PDF p. 22] | Masks platform-dependence of biological limits; fails to reveal Xenium’s superior signal-to-noise enables better marker prediction [Paper: PDF p. 10] |

## 09 关键公式与符号  
论文未提出新公式，但严格定义并依赖三个核心指标：  
- **Pearson Correlation Coefficient (PCC)** [Eq. 1, p.31]:  
  $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}} $  
  其中 $\hat{y}_{i,g}, y_{i,g}$ 是spot $i$、gene $g$ 的log-normalized预测/真值；$\bar{\hat{y}}_g, \bar{y}_g$ 为其均值。用于spot/gene/section/dataset各级评估。  
- **Mean Absolute Error (MAE)** [Eq. 2, p.32]:  
  $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}| $  
  在log(1+x)-transformed space计算，量化绝对误差幅度。  
- **Structural Similarity Index Measure (SSIM)** [p.32]:  
  非公式化定义，但明确用于评估预测表达图谱的空间结构保真度（luminance, contrast, structure），输入为二维空间网格上的归一化表达矩阵。  
**关键符号**: HMHVG (high-mean highly-variable genes), TME (tumor microenvironment), PFM (pathology foundation model), ARI (Adjusted Rand Index), SSIM (Structural Similarity Index Measure), singscore (gene set activity scoring method).

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|-------------------------------|--------|
| **UNIv2 vs native encoder (Fig. 2b)** | Unified encoder changes model rankings | CFANet with native ResNet50 vs UNIv2; same training protocol | CFANet rank: 16th → 6th | Encoder choice dominates reported architectural gains | "CFANet architecture is superior" — unsupported without UNIv2 | [Paper: PDF p. 9, Fig. 2b] |
| **HMHVG vs marker genes (Fig. 2a)** | Gene category dictates predictability ceiling | Same models, same datasets, two gene sets | HMHVG PCC ≈0.4; marker PCC ≈0.2 | Predictability is gene-intrinsic; markers are harder due to sparsity | "All genes are equally predictable" — falsified | [Paper: PDF p. 9, Fig. 2a] |
| **Xenium vs Visium (Fig. 2c-d)** | Platform resolution affects marker prediction | NCCHE-LUAD-Xenium (high counts) vs NCCHE-LUAD-Visium (low counts) | Xenium marker PCC=0.579; Visium=0.191 | Data quality (transcript count) is a key bottleneck for low-abundance genes | "Morphology cannot encode immune states" — contradicted by Xenium success | [Paper: PDF p. 10, Fig. 2c-d] |
| **Multi-scale models on stromal genes (Fig. 3b)** | Architectures integrating multi-scale context gain on ECM/immune genes | TRIPLEX/DeepSpot vs LinearProb on COL1A1, LAG3, etc. | ΔPCC ≥0.1 for 8–85 genes across cohorts | Multi-scale reasoning captures meso/macro tissue patterns (fibrosis, lymphoid aggregates) | "Any deep model suffices for stroma" — false; linear probe fails | [Paper: PDF p. 11–13, Fig. 3b] |
| **Cell2location on virtual ST (Fig. 4a)** | Virtual ST preserves cell-type spatial structure | Cell2location applied to TRIPLEX/DeepSpot predictions vs ground-truth | TRIPLEX/DeepSpot achieve highest PCC for epithelial/T cells | Top gene-level performers translate to top cellular-level performers | "Virtual ST enables rare cell detection" — unsupported (plasma/mast cells low PCC) | [Paper: PDF p. 14, Fig. 4a] |
| **Cross-Tissue generalization (Fig. 5b middle)** | Biological heterogeneity harms generalization more than technical variation | Models trained on LUAD tested on BRCA/CCRCC | Generalization gap: −0.20 to −0.35 PCC | Morphology-to-expression mapping is highly tissue-specific | "A universal virtual ST model exists" — contradicted | [Paper: PDF p. 17, Fig. 5b middle] |
| **Inter-cohort scaling (Fig. 5d)** | Aggregating diverse cancers causes negative transfer | Training on BRCA → BRCA+LUAD → BRCA+LUAD+PRAD | Performance on BRCA test set decreases with added cancers | Simple data mixing is detrimental without tissue-aware learning | "More multi-cancer data always helps" — falsified | [Paper: PDF p. 18, Fig. 5d] |

## 11 对结论的正确理解  
- **"Most models don't beat linear probing"** 意味着在UNIv2编码下，复杂架构未带来显著增益，**不等于模型无效**——TRIPLEX/DeepSpot仍稳定优于基线，且在下游任务中表现突出；这反映的是当前架构对PFM特征的利用效率瓶颈，而非虚拟ST范式失败。  
- **"Gene predictability is universal"** 指同一基因在所有模型中PCC排序高度一致（Fig. 3a），**不等于所有基因都难预测**——8–85个基因在特定 cohorts中PCC≥0.4且ΔPCC≥0.1，证实形态学确能编码特定程序。  
- **"Cross-platform transfer is stable"** （Fig. 5b right）指Visium→Xenium无显著性能损失，**不等于Visium→Xenium可逆**——论文未测试Xenium→Visium，且Xenium更高灵敏度可能补偿了域偏移。  
- **"Negative transfer in inter-cohort scaling"** 揭示组织特异性，**不等于跨癌种学习不可能**——恰说明需domain-adaptive策略（如tissue-aware adapters），而非放弃多癌种数据。  
- **"Performance concordance across granularities"** （gene→cell→domain）表明虚拟ST质量具有一致性，**不等于所有下游 tasks同等鲁棒**——Cell2location和SpaGCN均显示Xenium数据显著优于Visium，提示平台选择影响最终应用。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 ST platforms (Visium/Xenium) | Extend benchmark to additional tumor types, tissue contexts (e.g., normal, inflamed), and emerging platforms (e.g., Stereo-seq, Slide-seq) | [Paper: PDF p. 20] |
| **Restricted gene set analysis** | Evaluations focus only on HMHVGs and 16 TME markers; lowly expressed or functionally diverse genes unexamined | Systematically investigate low-abundance genes, non-coding RNAs, and broader functional categories beyond current panels | [Paper: PDF p. 20] |
| **Spot-level granularity** | All evaluations are at the spot level (aggregated multi-cell signals), not single-cell resolution | Extend principles to single-cell ST datasets and virtual ST models as they become available | [Paper: PDF p. 20] |
| **Lack of wet-lab validation** | Predictions are validated computationally against ground-truth ST, not via orthogonal experimental assays (e.g., ISH, IHC) | Future work should integrate computational predictions with targeted spatial proteomics or multiplexed imaging for biological confirmation | [Paper metadata selection note: "virtual prediction's biological validity still requires wet experiment verification"] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| **TRIPLEX/DeepSpot superiority may stem from training stability, not multi-scale design** | These models use ensemble strategies (e.g., 10 ϕspot modules for DeepSpot [p.26]) and auxiliary losses (TRIPLEX [p.25]), which improve optimization, not necessarily biological fidelity | Attributing gains solely to "multi-scale reasoning" overestimates architectural insight; could be an implementation artifact | Re-implement TRIPLEX/DeepSpot *without* ensembles/auxiliary losses but with identical hyperparameters; compare to linear probe | [Paper: PDF p. 25–26, Online Methods] |
| **Gene set scoring (singscore) may mask anti-correlated predictions** | singscore uses rank-based averaging; a model predicting *inverted* expression ranks (e.g., high→low) could yield high PCC despite biological implausibility | High gene-set PCC doesn't guarantee directional correctness of pathway activity (activation vs suppression) | Compute Spearman correlation on *signed* gene set scores (e.g., using GSVA) and compare to singscore results | [Paper: PDF p. 35, Online Methods] |
| **Cross-platform "stability" conflates improvement with compensation** | Fig. 5b right shows negligible loss, but Xenium's higher sensitivity may *mask* true domain shift degradation | Over-optimistic view of cross-platform utility could mislead clinical deployment where Visium remains dominant | Test on *matched* Visium/Xenium pairs from same tissue section; compute PCC drop *within* same biological sample, not across cohorts | [Paper: PDF p. 17, Fig. 5b right] |
| **Cell2location evaluation excludes low-PCC samples** | Samples with max model PCC <0.1 are excluded [p.35], potentially biasing toward "easier" tissues | Underestimates real-world failure modes in noisy/low-quality data; limits generalizability claim | Report full distribution of Cell2location PCC, including failed samples, and correlate with ST data QC metrics (e.g., spot QC score, library size) | [Paper: PDF p. 35, Online Methods] |
| **"Universal gene predictability" ignores spatial context dependence** | Fig. 3a shows gene-wise consistency, but a gene may be predictable only in specific spatial niches (e.g., tumor core vs invasive margin) | Gene-level PCC averages over all spots, hiding context-specific failures critical for precision oncology | Stratify PCC by spatial domain (e.g., tumor, stroma, immune infiltrate) using ground-truth annotations; compute domain-specific PCC | [Paper: PDF p. 11, Fig. 3a] |

## 14 学到的知识  
- **评估即建模**：STP-BENCH证明，严谨的benchmark设计本身就能驱动领域认知升级——它迫使社区正视“encoder-architecture confounding”这一隐藏变量，并催生“morphology-to-expression ceiling”的新概念。  
- **多尺度是解药，非万能**：TRIPLEX/DeepSpot的成功不在于堆叠更多层，而在于显式建模局部（spot）、邻域（3×3 grid）、全局（WSI）形态梯度，这对解析基质重塑（COL1A1）、免疫空间组织（LAG3）至关重要，但对上皮标记（KRT5）提升有限。  
- **数据质量 > 数据量**：Xenium的高计数直接拉升marker基因PCC至0.58，而Visium的低计数将其压至0.19；这警示single-cell foundation models若仅在低-depth data上预训练，将继承并放大信号噪声比缺陷。  
- **负迁移是信号，非噪音**：Inter-cohort scaling失败（Fig. 5d）不是实验缺陷，而是强证据——它量化了组织特异性壁垒，为设计tissue-aware adapters或multi-task pretraining提供了明确目标。  
- **下游验证是终极裁判**：Cell2location和SpaGCN结果与基因PCC高度一致（Spearman=0.902 [p.13]），证实spot-level metrics *can* proxy biological utility—但仅当评估覆盖足够广的生物学粒度时成立。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：STP-BENCH的“统一编码器+多粒度验证”范式可直接迁移到**single-cell foundation models**——例如，在scFoundation或CellLM上，可设计类似pipeline：固定scRNA encoder（如scGPT），在multi-dataset scRNA+spatial alignment任务中，评估基因/通路/cluster-level一致性。  
- **候选连接/方法论连接**：其**cross-tissue generalization failure**为**graph neural networks**在multi-omics中的应用敲响警钟：若GNN在BRCA图上学习的边权重（e.g., gene-gene co-expression）无法泛化到LUAD，需引入tissue-invariant graph construction或meta-learning。  
- **候选连接/方法论连接**：**perturbation prediction**任务（如CROP-seq）可借鉴其robustness分析——测试模型在perturbed vs control tissue morphologies下的预测稳定性，定义“perturbation robustness gap”。  
- **弱连接/方法论连接**：**cross-modal alignment**（如H&E↔RNA）的评估常止步于embedding similarity（e.g., CLIP loss），STP-BENCH证明必须延伸至functional alignment（e.g., gene set PCC, cell type PCC），否则alignment无生物学意义。  
- **弱连接/方法论连接**：**biomedical AI**的临床落地常卡在“黑箱可信度”，STP-BENCH的gene-wise heatmap（Fig. 3a）提供了一种可解释性模板：不解释单个预测，而解释“模型能/不能做什么”，这对监管审批更实用。

## 16 研究想法  

- **name**: Tissue-Aware Adapter for Virtual ST  
  **originating limitation/observation**: Inter-cohort scaling causes negative transfer (Fig. 5d); cross-tissue generalization gap is large (Fig. 5b middle)  
  **core hypothesis**: Injecting lightweight, tissue-specific adapters into frozen PFM encoders can preserve morphology knowledge while adapting to tissue-specific expression priors  
  **delta from paper**: STP-BENCH identifies the problem but does not propose a solution; this adds trainable LoRA-style adapters per tissue type, conditioned on organ ontology embeddings  
  **initial method**: For each tissue (BRCA/LUAD/PRAD), add two 64-dim adapter layers after UNIv2's final layer; train adapters + final regressor head only; freeze UNIv2 backbone  
  **validation**: Compare adapter vs fine-tuning on cross-tissue transfer (LUAD→BRCA); metric: PCC on marker genes and Cell2location PCC  
  **failure modes**: Adapters overfit to small tissue cohorts; fail to generalize to unseen tissues (e.g., new cancer type)  
  **innovation status**: unverified  

- **name**: Morphology-Guided Gene Set Prior  
  **originating limitation/observation**: Gene set scoring (Fig. 3e) shows TRIPLEX/DeepSpot excel on immune/stromal pathways, but current models treat all genes equally  
  **core hypothesis**: Incorporating prior knowledge of gene co-regulation (e.g., from SCENIC or DoRothEA) as a structural constraint during training improves pathway-level fidelity  
  **delta from paper**: STP-BENCH *measures* gene set performance but doesn’t *leverage* it in modeling; this adds a graph-regularized loss where edges represent TF-target relationships  
  **initial method**: Construct gene co-expression graph from public scRNA; use GraphSAGE to embed genes; add loss term: MSE between predicted and ground-truth gene set scores (singscore)  
  **validation**: On NCCHE-LUAD-Xenium, compare gene set PCC (Fig. 3e) and ARI (Fig. 4c) vs baseline TRIPLEX  
  **failure modes**: Prior knowledge incompleteness biases predictions; graph sparsity hurts low-degree genes  
  **innovation status**: unverified  

- **name**: Spatially-Stratified Gene Predictability Atlas  
  **originating limitation/observation**: Gene-wise PCC (Fig. 3a) is averaged over all spots, masking spatial-context dependence (e.g., LAG3 predictable only in immune niches)  
  **core hypothesis**: Partitioning tissue into spatial domains (e.g., tumor/stroma/immune) and computing domain-specific PCC reveals context-dependent morphology-encoding capacity  
  **delta from paper**: STP-BENCH computes global PCC; this introduces spatial stratification *before* aggregation  
  **initial method**: Use SpaGCN (Fig. 4b) to segment each tissue; compute PCC for each gene *within each domain*; build atlas of "predictable genes per domain"  
  **validation**: Correlate domain-specific PCC with histopathology features (e.g., fibrosis score, immune infiltration density) from pathologist annotations  
  **failure modes**: Domain segmentation noise propagates to PCC estimates; small domains yield unstable PCC  
  **innovation status**: unverified  

- **name**: Single-Cell Resolution Virtual ST Benchmark Extension  
  **originating limitation/observation**: Authors explicitly note spot-level limitation and call for single-cell extension (p.20)  
  **core hypothesis**: STP-BENCH principles (unified encoder, multi-granularity, robustness) scale to single-cell ST, but require new metrics for sub-spot heterogeneity  
  **delta from paper**: This proposes concrete extensions: (1) replace spot-level PCC with cell-type-specific PCC using scRNA reference; (2) add sub-spot spatial variance metrics (e.g., entropy of predicted cell types within spot)  
  **initial method**: Leverage Xenium single-molecule data; define "virtual scST" as per-cell prediction; use CellTypist for cell-type annotation; compute PCC per cell type  
  **validation**: Benchmark existing scST models (e.g., scGPT-ST, SpaFormer) on STP-BENCH-EXTERNAL single-cell subsets  
  **failure modes**: Ground-truth scST data scarcity; ambiguity in cell-type assignment affects PCC reliability  
  **innovation status**: unverified