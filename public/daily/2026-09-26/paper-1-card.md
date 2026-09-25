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
| Title | STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images | [Paper] [Paper: PDF p. 1] |
| Authors | Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al. | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint | [Paper] [Paper: PDF p. 1] |
| Year | 2026 | [Paper] [Paper: PDF p. 1] |
| Core task | Virtual spatial transcriptomics (virtual ST): predicting spot-level gene expression from H&E image patches | [Paper] [Paper: PDF p. 2], [Figure 1a] |
| Benchmark name | STP-BENCH, comprising STP-BENCH-INTERNAL (609,024 spots) and STP-BENCH-EXTERNAL (185,831 spots) | [Paper] [Paper: PDF p. 4], [Figure 1b] |
| Cancer types | LUAD, BRCA, PRAD, CCRCC, GBM, PDAC (6 total) | [Paper] [Paper: PDF p. 21], [Figure 1b] |
| Platforms | 10x Genomics Visium and Xenium | [Paper] [Paper: PDF p. 4], [Figure 1b] |
| Evaluated models | 21 models across regression (n=14), bi-modal retrieval (n=4), generative (n=3) families | [Paper] [Paper: PDF p. 6], [Figure 1c] |
| Key encoder | UNIv2 pathology foundation model (PFM), used as unified patch encoder where architecturally compatible | [Paper] [Paper: PDF p. 7], [Figure 2a] |
| Primary metric | Pearson Correlation Coefficient (PCC) per gene, averaged across spots and folds | [Paper] [Paper: PDF p. 31], Equation 1 |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结  
本文提出了STP-BENCH——首个大规模、多平台、标准化的虚拟空间转录组（virtual ST）系统性基准，覆盖6种癌症、Visium与Xenium双平台、超79万spots；通过统一使用UNIv2等病理基础模型（PFM）作为图像编码器，发现多数现有模型无法超越线性探针基线，揭示了图像编码器选择对性能的主导性影响远超架构创新；进一步证明基因可预测性存在普适性天花板（如免疫/基质基因需多尺度建模），且下游生物任务（cell deconvolution、spatial domain ID）性能与spot-level PCC高度一致，直指数据质量（如Xenium高计数）是跨粒度性能的共同瓶颈。该工作不提出新模型，而是重构评估范式，为single-cell foundation models、spatial transcriptomics和cross-modal alignment提供可复现的方法论锚点。

## 03 研究问题  
论文直面虚拟ST领域长期存在的**评估不可比性**问题：不同研究使用异构小数据集、不一致训练/推理流程、各自原生图像编码器（ResNet50、ViT等），导致报告的“架构优势”实则混杂了编码器能力差异。由此衍生出三个递进问题：（1）当剥离编码器变量、统一使用强PFM（如UNIv2）时，现有21种模型的真实架构优劣排序是否发生根本性重排？（2）若排序重排，哪些模型模块真正贡献了超越线性基线的增量价值？其作用边界（如仅对高表达基因有效）是否可刻画？（3）spot-level预测精度的提升，能否稳健传导至更高生物学粒度（细胞类型丰度、空间结构域）？这些传导是否受平台（Visium vs Xenium）或组织类型（LUAD vs BRCA）制约？

## 04 研究背景与发展路径  
虚拟ST起源于ST技术高成本阻碍临床规模应用的现实约束，其方法学演进呈现三条并行路径：（1）**回归路径**（如ST-Net→TRIPLEX→DeepSpot），从单patch局部特征扩展至邻域+全片多尺度上下文；（2）**双模态对齐路径**（如BLEEP→STco→mclSTExp），借鉴CLIP范式，将H&E图像与基因表达映射到联合嵌入空间，依赖检索机制；（3）**生成路径**（如STFlow→Stem），将预测建模为条件生成过程（flow matching/diffusion），输出分布而非点估计。三类方法均日益依赖病理基础模型（PFM）提取形态语义，但此前评估未控制此变量。作者指出，Wang et al. 2024 [50] 保留各模型原生编码器，而HEST-1K [51] 仅用PFM嵌入+简单回归，二者均未实现“架构vs编码器”的解耦评估。STP-BENCH正是为填补这一方法论缺口而设计：它不是增量改进某条路径，而是构建一个控制变量的“评估操作系统”，强制所有兼容模型共享同一PFM输入，从而将比较焦点真正回归到模型架构本身。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平** | 模型排名在不同研究间不可比，宣称的“SOTA”可能源于编码器优势而非架构创新 | 各研究使用不同预训练图像编码器（ImageNet ResNet50 vs pathology ViT），其表征能力差异巨大，且编码器与架构耦合训练，无法分离贡献 | [Paper] [Paper: PDF p. 3] “prior studies typically inherit each model’s original image encoder rather than standardizing it… reported gains may therefore reflect feature extraction as much as model design”; [Figure 2b] CFANet排名从16→6，BrSTNet性能跃升，均因换用UNIv2 |
| **评价维度单一** | 仅报告整体PCC，忽略基因特异性、生物学可解释性及鲁棒性 | 早期工作聚焦aggregate accuracy，未探究“哪些基因可被预测”、“预测结果能否支撑下游分析”、“模型在跨机构/跨组织时是否可靠” | [Paper] [Paper: PDF p. 3] “evaluation has been confined to aggregate predictive accuracy, leaving the biological reliability… and model robustness… largely unexamined”; [Figure 3a] 基因层面PCC存在强一致性，[Figure 4] 下游任务性能与spot-level PCC高度相关 |
| **数据瓶颈模糊** | 性能差异归因于模型，但未量化底层数据质量（如基因计数）的制约作用 | Visium与Xenium平台间基因检测灵敏度差异巨大，低计数基因（如marker genes in Visium）的预测本质上受限于信噪比，非模型缺陷 | [Paper] [Paper: PDF p. 9–10] NCCHE-LUAD-Xenium marker gene PCC=0.579 vs NCCHE-LUAD-Visium PCC=0.191; [Figure 2c-d] 表达水平分层分析显示PCC随mean counts显著升高（p<1e-12） |
| **泛化性黑箱** | 模型在内部验证集表现好，但跨机构/跨组织/跨平台时性能骤降，原因不明 | 技术批次效应（institution）相对温和，而生物异质性（tissue）构成更大障碍；跨平台（Visium→Xenium）性能未降反升，暗示Xenium高灵敏度可补偿域偏移 | [Paper] [Paper: PDF p. 17] Cross-tissue gap (−0.2 to −0.35) > cross-institution gap (−0.05 to −0.10); [Figure 5b] Cross-platform gap near zero; [Paper] [Paper: PDF p. 19] “biological heterogeneity due to different cancer morphologies presents far greater obstacles than technical variability” |

## 06 核心思想  
论文的核心思想是**将虚拟ST评估从“模型竞赛”升维为“评估基础设施建设”**：其创新不在于提出新算法，而在于确立一套控制变量、多粒度、可复现的评估协议。关键洞察有三：（1）**编码器是性能主效应源**——UNIv2等PFM提供的形态表征质量，远超多数专用架构的设计增益，因此必须将其标准化为评估基底；（2）**基因可预测性存在普适性结构**——某些基因（如ECM、免疫标记）的预测难度由其生物学本质（依赖长程组织结构）决定，而非模型缺陷，这定义了虚拟ST的能力边界；（3）**spot-level精度是下游任务的充分必要条件**——cell deconvolution与spatial domain ID的性能与spot-PCC呈强线性相关，且二者在Xenium上同步优于Visium，证实数据质量是贯穿所有粒度的瓶颈。该思想将虚拟ST定位为一个“数据-表征-架构”三层耦合系统，而STP-BENCH正是解耦并量化这三层关系的实验框架。

## 07 方法总览  
STP-BENCH的方法论骨架由三大支柱构成：（1）**统一数据协议**：构建STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与STP-BENCH-EXTERNAL（186k spots, 6 cancers, independent cohorts），对Visium/Xenium采用统一patch裁剪（224×224@0.5µm/pixel）与pseudo-spot聚合策略，确保跨平台可比性；（2）**统一编码器协议**：对16/21个模型强制替换为UNIv2 PFM作为patch encoder（其余5个因架构不兼容保留原encoder），消除编码器混杂效应；（3）**多维评估协议**：超越spot-PCC，新增基因级热图（Fig.3a）、基因集singscore（Fig.3c-e）、下游cell deconvolution（Cell2location, Fig.4a）与spatial domain ID（SpaGCN+ARI, Fig.4b-c）、鲁棒性分析（cross-institution/tissue/platform, Fig.5a-b）及数据缩放律（Fig.5c-d）。整个流程以PyTorch实现，所有模型在相同硬件（RTX A5000）、相同CV策略（patient-level 5-fold）、相同随机种子下运行，确保结果可复现。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-----------------------------------|
| **UNIv2 PFM Encoder** | Extracts 1024-dim morphology embeddings from 224×224 H&E patches | To disentangle image representation quality from model architecture; serves as common "perception layer" for fair comparison | Input: H&E patch; Output: PFM embedding vector | [Paper] [Paper: PDF p. 7] “standardized the patch encoders to UNIv2… to isolate and assess the effects of architectural advantages”; [Figure 2b] Ranking reversal proves its dominance | Removal would revert to unfair comparisons (e.g., CFANet drops from 6th to 16th), collapsing all models to their native encoder's capability ceiling |
| **Multi-scale Context Integration (TRIPLEX/DeepSpot)** | Fuses local patch + neighbor spots + whole-slide global context | To capture morphological dependencies beyond isolated patches (e.g., fibrosis gradients, immune fronts) that single-scale models miss | Input: Local, neighbor, global PFM embeddings; Output: Fused representation for regression | [Paper] [Paper: PDF p. 19] “genes encoding stromal and ECM-remodeling programs… benefited most from multi-scale reasoning”; [Figure 3b] TRIPLEX/DeepSpot show largest ∆PCC on stromal/immune genes | Removal (e.g., using only local branch) would collapse performance on stromal/immune genes (COL1A1, LAG3) to baseline level, widening the gene-wise predictability gap |
| **Gene Set Scoring (singscore)** | Computes per-spot activity score for GO Biological Process terms from predicted expression | To bridge from individual gene prediction to functional pathway recovery, testing if virtual ST preserves biological coherence | Input: Predicted spot×gene matrix; Output: Spot×gene_set matrix of ranks-based scores | [Paper] [Paper: PDF p. 13] “gene set scoring performance was substantially higher on NCCHE-LUAD-Xenium… mirroring the gene-level prediction gap”; [Figure 3c] TRIPLEX/DeepSpot top performers on gene sets too | Removal would leave evaluation blind to functional interpretability; e.g., high PCC on CD3E alone doesn’t guarantee T-cell activation pathway is recovered |
| **Cross-Platform Pseudo-spot Alignment (Xenium→Visium)** | Aggregates Xenium single-molecule transcripts into 100µm×100µm bins matching Visium spacing | To enable direct comparison between Visium (spot-based) and Xenium (single-molecule) data within same benchmark | Input: Xenium transcript coordinates + registered H&E; Output: Pseudo-spot expression matrix + aligned 224×224 patches | [Paper] [Paper: PDF p. 22] “Xenium preprocessing: transcripts aggregated into spatially regular bins… comparable to Visium inter-spot spacing”; [Figure 1b] Both platforms included in same STP-BENCH distribution | Removal would exclude Xenium data, eliminating critical test of platform generalization and masking the finding that Xenium’s higher sensitivity boosts performance across all tasks ([Paper] [Paper: PDF p. 14,19]) |
| **Downstream Task Evaluation (Cell2location/SpaGCN)** | Applies Cell2location for cell-type abundance estimation and SpaGCN for spatial domain clustering on predicted expression | To validate if virtual ST profiles retain sufficient biological structure for real-world analysis workflows, beyond statistical correlation | Input: Predicted spot×gene matrix; Output: Cell-type abundance matrix (Cell2location) or spatial domain labels (SpaGCN) | [Paper] [Paper: PDF p. 14] “TRIPLEX and DeepSpot consistently achieved the highest average correlation with the ground truth” in deconvolution; [Figure 4a-b] Performance hierarchy preserved across tasks | Removal would render benchmark irrelevant to end-users; e.g., a model with high PCC but failing Cell2location cannot be deployed for tumor microenvironment analysis |

## 09 关键公式与符号  
论文未提出新公式，但明确定义并使用了三个核心评估指标：  
- **Pearson Correlation Coefficient (PCC)**: 定义为 Equation 1:  
  $$\text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}}$$  
  其中 $\hat{y}_{i,g}$ 和 $y_{i,g}$ 分别为spot $i$ 上基因 $g$ 的预测与真实log-normalized表达值；$\bar{\hat{y}}_g$, $\bar{y}_g$ 为其均值；$N$ 为spots数。[Paper] [Paper: PDF p. 31]  
- **Mean Absolute Error (MAE)**: 定义为 Equation 2:  
  $$\text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}|$$  
  在log(1+x)-transformed表达空间计算，反映绝对误差大小。[Paper] [Paper: PDF p. 32]  
- **Structural Similarity Index Measure (SSIM)**: 用于评估预测表达图的空间结构保真度，基于spot坐标重采样为2D网格后计算，参数为 `data_range=1.0`（默认）。[Paper] [Paper: PDF p. 32]  
**关键符号**:  
- `HMHVG`: High-mean highly-variable genes (200 genes selected by rank-sum of mean & std) [Paper] [Paper: PDF p. 33]  
- `TME markers`: 16 tumor microenvironment marker genes (e.g., CD3E, ACTA2, PDCD1) [Paper] [Paper: PDF p. 7]  
- `STP-BENCH-INTERNAL/EXTERNAL`: 内部训练/验证集与外部独立测试集 [Paper] [Paper: PDF p. 4]  
- `PCC`, `MAE`, `SSIM`: 主要评估指标 [Paper] [Paper: PDF p. 31–32]  
- `ARI`: Adjusted Rand Index, 用于量化spatial domain ID的一致性 [Paper] [Paper: PDF p. 36]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|----------------------------------|--------|
| **Unified PFM vs Native Encoders** | Standardizing image encoder reshapes model rankings | Compare PCC of 21 models using their original encoders vs UNIv2; evaluated on STP-BENCH-INTERNAL HMHVGs | CFANet jumps from 16th→6th; BrSTNet shows large gain; rankings inconsistent between native/unified [Figure 2b] | Encoder choice dominates over architecture in many cases; prior SOTA claims may be encoder artifacts | UNIv2 is universally optimal encoder — not tested against other PFMs in this experiment (though Fig.2e shows Virchow2/H-Optimus1 similar) | [Paper] [Paper: PDF p. 9], [Figure 2b] |
| **Gene Expression Level Stratification** | Prediction accuracy is driven by underlying transcript detection quality | Stratify genes into 5 quantiles by mean expression; compute PCC per quantile for models on NCCHE-LUAD-Xenium/Visium | Strong positive correlation: PCC ↑ as mean counts ↑ (p<1e-12); gap between HMHVG/marker genes vanishes in high-count Xenium | Data quality (transcript count/SNR) is a fundamental bottleneck, not model limitation | All low-expression genes are inherently unpredictable — contradicted by some high-PCC low-count genes in Fig.3b (e.g., AZGP1) | [Paper] [Paper: PDF p. 10], [Figure 2c-d] |
| **Multi-scale Models on Gene Subsets** | Architectures integrating multi-scale context provide targeted gains for specific biology | Compute ∆PCC (vs linear probe) for genes with PCC≥0.4 & ∆PCC≥0.1; assign genes to functional categories | TRIPLEX/DeepSpot dominate gains on stromal (COL1A1), immune (LAG3), epithelial (AZGP1) genes [Figure 3b-c] | Multi-scale reasoning is necessary for genes dependent on meso-/macro-scale tissue organization | Multi-scale is sufficient for all hard-to-predict genes — not tested; e.g., stress genes (FOS) also benefit but mechanism differs | [Paper] [Paper: PDF p. 11–13], [Figure 3b-c] |
| **Downstream Task Correlation** | Spot-level PCC predicts utility for biological analysis | Compute PCC for Cell2location abundance & ARI for SpaGCN domains; correlate with spot-PCC rankings | TRIPLEX/DeepSpot top in all tasks; performance hierarchy preserved; Xenium > Visium across all granularities [Figure 4a-c] | Spot-level accuracy is a reliable proxy for downstream utility; data quality is a shared bottleneck | Spot-PCC is the *only* determinant of downstream success — confounded by potential model-specific biases in Cell2location/SpaGCN inputs | [Paper] [Paper: PDF p. 14], [Figure 4] |
| **Cross-Tissue Generalization** | Biological heterogeneity is harder to generalize across than technical variation | Evaluate models trained on one cancer type (e.g., LUAD) on external test of another (e.g., BRCA); compute generalization gap | Cross-tissue gap (−0.2 to −0.35) >> cross-institution gap (−0.05 to −0.10); Spearman ρ=0.876 for rank preservation [Figure 5a-b] | Morphology-to-expression mapping is highly tissue-specific; internal rankings remain predictive externally | Cross-tissue transfer is impossible — contradicted by non-zero external PCC and preserved ranking | [Paper] [Paper: PDF p. 17], [Figure 5a-b] |

## 11 对结论的正确理解  
论文结论必须严格限定于其证据范围：（1）**“多数模型未超线性基线”** 指在UNIv2统一编码器下，对HMHVG/marker genes的spot-PCC平均值未显著超越LinearProb，**不意味着这些模型无用**——TRIPLEX/DeepSpot在特定基因（stromal/immune）和下游任务（Cell2location）上仍具显著优势；（2）**“基因可预测性存在天花板”** 指观察到的基因间PCC差异具有跨模型一致性（Fig.3a），**并非断言某些基因绝对不可预测**，而是强调当前H&E图像信息量与现有架构对此类基因的捕获存在系统性局限；（3）**“Xenium性能更优”** 源于其更高基因计数（Fig.2c-d），**不等于Xenium数据“更好”**，而是其技术特性（单分子灵敏度）缓解了Visium的低信噪比瓶颈，这恰恰凸显了虚拟ST对底层数据质量的依赖；（4）**“跨组织泛化难”** 是指性能下降幅度大，**但排名稳定性高（ρ=0.876）**，说明模型相对优劣在新组织中依然可靠，这对临床部署是利好而非利空。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium), lacking rarer tumors and emerging platforms (e.g., Stereo-seq, Slide-seq) | “Extending the benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms will be important for broader generalizability” | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analysis focused on HMHVGs (200 genes) and 16 TME markers; lowly expressed and functionally diverse genes not systematically investigated | “Systematic investigation of lowly expressed or functionally diverse genes remains an open direction” | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluations performed at spot-level (aggregating multiple cells), not single-cell resolution, despite growing availability of scST data | “Future benchmarking efforts may extend these principles to evaluations at single-cell resolution” | [Paper] [Paper: PDF p. 20] |
| **No perturbation modeling** | Benchmark does not include datasets with genetic/pharmacological perturbations, limiting assessment of virtual ST for causal inference | Not explicitly stated, but implied by the “Risk” note in user input: “Risk: 聚焦histo-to-ST，未显式建模perturbation或cell state动态” — this is an unaddressed gap | [User input metadata] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|--------------------------|-------------------------------------------|----------------|----------------|--------|
| **TRIPLEX/DeepSpot’s multi-scale advantage may conflate architecture with training data scale** | These top performers were trained on the largest datasets (e.g., WUSTL-BRCA-Visium has 157k spots); their edge could stem from data volume, not multi-scale design per se | Over-attributing success to architecture risks misguiding future model design; simpler models might match performance with sufficient data | Re-train TRIPLEX/DeepSpot on smaller subsets (e.g., 33% of WUSTL-BRCA) and compare to equally-sized LinearProb; if gap vanishes, data scale dominates | [Paper] [Paper: PDF p. 18] “Intra-cohort scaling yielded only marginal performance gains”, but this was for *all* models together; no per-model ablation shown |
| **The “universal gene predictability” pattern (Fig.3a) may be dataset-dependent** | The heatmap aggregates results across 7 diverse datasets; a gene hard to predict in LUAD-Xenium might be easy in BRCA-Visium, but averaging masks this heterogeneity | Assuming universality could lead to overlooking tissue-contextual predictors; e.g., a breast-specific marker may be predictable only in BRCA data | Compute gene-wise PCC correlation *between pairs* of datasets (e.g., LUAD-Xenium vs BRCA-Visium); low inter-dataset correlation would refute universality | [Paper] [Paper: PDF p. 11] “gene-wise concordance was consistently observed across additional datasets (Extended Data Fig. 4a)”, but Extended Data Fig. 4a is not provided in input |
| **Using Cell2location/SpaGCN as downstream validators assumes their robustness to prediction noise** | These tools were designed for ground-truth ST; their performance degradation on noisy virtual ST may reflect tool limitations, not virtual ST failure | Blaming virtual ST for poor Cell2location results ignores that the tool itself may amplify errors; this conflates model quality with downstream tool suitability | Benchmark Cell2location/SpaGCN on *noisy ground-truth* (e.g., add Gaussian noise to real ST) and compare degradation patterns to virtual ST results | [Paper] [Paper: PDF p. 35–36] Describes Cell2location/SpaGCN usage but no validation of their noise robustness |
| **The negative transfer in inter-cohort scaling (Fig.5d) may stem from label misalignment, not tissue heterogeneity** | When merging BRCA+LUAD+PRAD, the “same” gene (e.g., KRT5) may have different biological roles; training on mixed labels could confuse the model | Attributing failure to tissue heterogeneity overlooks data curation issues; better harmonization (e.g., batch correction, tissue-aware labels) might resolve it | Apply ComBat or tissue-specific normalization before merging; re-run inter-cohort scaling and check if negative transfer persists | [Paper] [Paper: PDF p. 19] “simple aggregation of the heterogeneous sources could be detrimental”, but no test of harmonization methods |

## 14 学到的知识  
- **评估即基建**：构建高质量benchmark（如STP-BENCH）的科研价值不亚于提出新模型；其核心是控制变量（如统一PFM）、多维验证（spot→gene set→cell→domain）、开放共享（code/data fully public）。  
- **编码器是虚拟ST的“第一性原理”**：UNIv2等PFM提供的形态表征质量，是当前所有架构的性能上限；后续工作应优先优化PFM（如更大规模、更多模态预训练），而非堆砌复杂head。  
- **基因可预测性具有生物学根源**：ECM/immune基因的预测难度源于其依赖长程组织结构（fibrosis gradients, immune fronts），这定义了虚拟ST的**能力边界**，而非待攻克的“难题”。  
- **数据质量是跨粒度性能的“阿喀琉斯之踵”**：Xenium的高计数不仅提升spot-PCC，还同步改善Cell2location和SpaGCN结果，证明数据质量是所有下游分析的共同瓶颈。  
- **鲁棒性≠性能，而是排名稳定性**：跨组织泛化虽导致PCC下降，但模型相对排名高度稳定（ρ=0.876），这对临床部署是关键利好——用户只需选择内部验证最强的模型即可。  
- **负向结果极具指导价值**：Intra-cohort scaling饱和、inter-cohort scaling负迁移、多数模型不超线性基线，这些“失败”现象比单纯提升PCC更能揭示领域本质规律。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：本文的“统一PFM评估范式”可直接迁移到**single-cell foundation models**研究中，解决scRNA-seq模型评估中同样存在的encoder混杂问题（如使用不同scBERT变体）；其multi-granularity评估（gene→cell type→tissue domain）为**spatial transcriptomics**的benchmark设计树立了新标准。  
- **候选连接/方法论连接**：STP-BENCH中对多尺度上下文（TRIPLEX）和图结构（EGGN, SEPAL）的验证，为**graph neural networks**在空间组学中的应用提供了实证依据——图结构确能提升对空间邻域依赖基因的预测。  
- **候选连接/方法论连接**：其跨平台（Visium↔Xenium）和跨组织（LUAD↔BRCA）的泛化分析框架，可被**multi-omics**整合研究借鉴，用于评估multi-omics融合模型在不同数据模态/组织来源间的鲁棒性。  
- **候选连接/方法论连接**：对基因集（singscore）和通路（GO BP）的评估，为**biomedical AI**的可解释性研究提供了路径——将模型输出映射到已知生物学功能，而非仅依赖attention可视化。  
- **弱连接/方法论连接**：本文未涉及**perturbation prediction**或**cell state representation**，因其聚焦静态H&E→ST映射，而非动态扰动响应或单细胞状态建模；但其spot-level评估协议可作为未来perturbation benchmark的spot-level基线模块。  
- **弱连接/方法论连接**：虽使用了SpatialFormer [97]进行位置编码，但未将**cross-modal alignment**作为核心创新点；其alignment仅服务于retrieval models（BLEEP/STco），而非作为通用对齐框架。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware PFM Adapter  
  **originating limitation/observation**: Inter-cohort scaling shows negative transfer when mixing BRCA/LUAD/PRAD; cross-tissue generalization gap is large (−0.2 to −0.35) [Paper] [Paper: PDF p. 17,19], suggesting tissue-specific morphology-to-expression mappings.  
  **core hypothesis**: A lightweight, tissue-specific adapter module inserted between a frozen universal PFM (e.g., UNIv2) and the ST predictor head can capture tissue-invariant morphology while adapting to tissue-specific expression patterns, outperforming both naive fine-tuning and multi-task learning.  
  **delta from paper**: STP-BENCH uses *frozen* UNIv2; this idea proposes *adapting* UNIv2 via tissue-conditioned adapters, moving beyond static encoding.  
  **initial method**: For each tissue type (BRCA/LUAD/PRAD), train a small LoRA adapter on UNIv2's last layer; condition adapter selection on tissue label or inferred tissue embedding; use tissue label during training/inference.  
  **validation**: On STP-BENCH-EXTERNAL cross-tissue transfer (e.g., train on LUAD, test on BRCA); compare PCC and ARI against baseline UNIv2 + TRIPLEX and full fine-tuning.  
  **failure modes**: Adapter overfitting to small tissue cohorts; inability to generalize to unseen tissues; increased inference latency.  
  **innovation status**: unverified  

- **name**: Gene-Specific Uncertainty Quantification (GSUQ)  
  **originating limitation/observation**: Gene-wise PCC heatmaps (Fig.3a) reveal consistent predictability ceilings, yet current models output point estimates only; STFlow offers stochastic sampling but lacks gene-specific calibration.  
  **core hypothesis**: Modeling per-gene epistemic uncertainty (via ensemble or Bayesian layers) and aleatoric uncertainty (via heteroscedastic loss) will improve downstream task reliability (e.g., Cell2location confidence scores) and identify genes where virtual ST is clinically actionable.  
  **delta from paper**: STP-BENCH evaluates point estimates (PCC/MAE); GSUQ adds calibrated uncertainty, enabling risk-aware deployment.  
  **initial method**: Modify TRIPLEX/DeepSpot to output gene-wise variance predictions; train with heteroscedastic MSE loss; calibrate using quantile regression on held-out STP-BENCH-INTERNAL.  
  **validation**: Correlate predicted gene-wise uncertainty with actual PCC on STP-BENCH-EXTERNAL; test if filtering high-uncertainty genes improves Cell2location ARI.  
  **failure modes**: Uncertainty miscalibration; computational overhead; no improvement on high-count genes where uncertainty is low anyway.  
  **innovation status**: unverified  

- **name**: Cross-Modal Contrastive Pretraining (CMCP) for Perturbation Response  
  **originating limitation/observation**: STP-BENCH lacks perturbation data [User input metadata]; current virtual ST is static, but clinical need is for predicting treatment response (e.g., post-chemo H&E → residual tumor ST).  
  **core hypothesis**: Jointly pretraining a PFM on paired H&E images and *perturbed* ST (e.g., drug-treated vs control) using contrastive learning (inspired by BLEEP) will learn perturbation-invariant morphology features and perturbation-sensitive expression shifts, enabling virtual ST for treatment response prediction.  
  **delta from paper**: Extends STP-BENCH’s contrastive paradigm (BLEEP/STco) from static alignment to *dynamic* perturbation modeling.  
  **initial method**: Collect/curate paired pre-/post-treatment H&E+ST datasets; use CMCP to align H&E patches with perturbation-delta ST vectors (post−pre); fine-tune on STP-BENCH for response prediction.  
  **validation**: On simulated or real perturbation datasets (e.g., breast cancer neoadjuvant therapy), measure PCC of predicted delta-ST vs ground-truth delta-ST.  
  **failure modes**: Scarce real perturbation ST data; difficulty defining meaningful delta-ST representations; domain shift between training perturbations and clinical scenarios.  
  **innovation status**: unverified