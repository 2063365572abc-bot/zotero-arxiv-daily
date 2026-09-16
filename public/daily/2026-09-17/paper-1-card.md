> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: resource  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **Title**: STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images  
- **Authors**: Youngmin Chung, Ji Hun Ha, Andrew H. Song, Cristina Almagro-Pérez, Chaeyoung Seo, Won Jun Suh, Jeong Won Beom, Kyoung Bin Oh, Eytan Ruppin, Faisal Mahmood, Joo Sang Lee  
- **Source**: arXiv preprint (2026-09-05), arXiv:2609.05956v1  
- **URL**: https://arxiv.org/abs/2609.05956v1  
- **PDF URL**: https://arxiv.org/pdf/2609.05956v1  
- **Code & data**: Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face (https://huggingface.co/datasets/nexgem/STP-Bench) [Paper: PDF p. 37]  
- **Key datasets**: STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium/Xenium), STP-BENCH-EXTERNAL (185,831 spots, 6 cancer types) [Paper: PDF p. 4–5, Fig. 1b]  
- **Evaluated models**: 21 virtual ST models across three families — regression-based (n=14), bi-modal retrieval-based (n=4), generative-based (n=3) [Paper: PDF p. 6, Fig. 1c]  
- **Core encoder**: UNIv2 pathology foundation model (PFM) used as standardized patch encoder where architecturally compatible [Paper: PDF p. 7–8]  
- **Metrics**: Pearson Correlation Coefficient (PCC) [Eq. 1, p. 31], Mean Absolute Error (MAE) [Eq. 2, p. 32], Structural Similarity Index Measure (SSIM) [Paper: PDF p. 7, 32]  

## 02 一句话总结  
STP-BENCH 是首个大规模、跨平台、标准化的 virtual spatial transcriptomics（virtual ST）基准，通过统一使用 pathology foundation model（UNIv2）作为图像编码器，在 609,024 个 spot 的内部数据集（STP-BENCH-INTERNAL）和 185,831 个 spot 的外部数据集（STP-BENCH-EXTERNAL）上系统评估了 21 种模型；结果表明：多数模型未超越 UNIv2 线性探针基线，模型排名因统一编码器而显著重排，基因级可预测性具有跨模型一致性，且 multi-scale 架构（TRIPLEX/DeepSpot）在 stromal/immune 基因和下游生物学任务中表现最优 [Paper: PDF p. 8–19].

## 03 研究问题  
- 如何在公平、可控、可复现条件下系统评估 virtual ST 模型的真实架构贡献？[Paper: PDF p. 3–4]  
- 哪些基因或基因集能被可靠地从组织形态学（H&E）中恢复？其可预测性是否由模型架构主导，还是受形态-转录耦合本质限制？[Paper: PDF p. 11–13, Fig. 3a–e]  
- virtual ST 预测结果是否保留下游生物学分析所需的结构——包括细胞类型丰度估计（Cell2location）和空间结构域识别（SpaGCN）？[Paper: PDF p. 14–15, Fig. 4]  
- virtual ST 模型在跨机构、跨组织、跨平台等真实域偏移场景下的泛化鲁棒性如何？数据规模与多样性是否带来性能提升？[Paper: PDF p. 16–18, Fig. 5]  

## 04 研究背景与发展路径  
- **技术动因**：Spatial transcriptomics（ST）实验成本高，催生 virtual ST（从 H&E 预测空间基因表达）计算范式 [Paper: PDF p. 2]。  
- **方法演进**：三大建模范式并行发展：(1) 回归式（如 ST-Net → TRIPLEX/DeepSpot），直接映射 patch→expression；(2) 双模态对齐式（如 BLEEP/STco/mclSTExp），借鉴 CLIP 范式学习 joint embedding space；(3) 生成式（如 STFlow/Stem），建模 conditional distribution via diffusion/flow matching [Paper: PDF p. 3–6]。  
- **瓶颈识别**：既有评估存在三重缺陷：(i) 数据小、异质、不统一（如 Wang et al. 2024 仅用 2 个 Visium 数据集；HEST-1K 仅评估 PFM embedding + 简单回归）；(ii) 图像编码器未标准化（native encoders 混淆 architecture vs. encoder 贡献）；(iii) 评估止步于 aggregate gene-level PCC，忽略 per-gene reliability、gene-set activity、下游 utility 和鲁棒性 [Paper: PDF p. 3–4]。  
- **解决方案路径**：构建 STP-BENCH —— 大规模（>30k spots/dataset）、多平台（Visium+Xenium）、多癌种（6）、统一 PFM 编码、全栈重实现、多粒度评估（gene → gene set → cell type → domain → robustness）[Paper: PDF p. 4–5]。  

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **Unfair architectural comparison** | Model rankings inconsistent when native vs. unified (UNIv2) encoders used (e.g., CFANet jumps from 16th to 6th) [Paper: PDF p. 9] | Prior works inherit original image encoders differing in pretraining domain/scale/paradigm; performance gains may reflect feature extraction, not model design [Paper: PDF p. 3–4] | Fig. 2b shows rank reversal; “CFANet … jumped to 6th when using UNIv2” [Paper: PDF p. 9]; “evaluations in previous works … are likely unfair comparisons” [Paper: PDF p. 9] |
| **Aggregate evaluation obscures biological utility** | High average PCC on HMHVGs masks poor recovery of TME marker genes (PCC≈0.2 vs. 0.4) and fails to reveal which biological programs are recoverable [Paper: PDF p. 9] | Evaluation confined to “average predictive accuracy on highly variable genes”, neglecting per-gene reliability, gene-set coherence, and downstream task fidelity [Paper: PDF p. 2–4] | Fig. 2a shows HMHVG vs. marker gene gap; Fig. 3a heatmap shows gene-wise concordance; “genes that are difficult … remain similarly challenging across diverse models” [Paper: PDF p. 11] |
| **Lack of robustness assessment under real-world shifts** | No systematic evaluation of cross-institution, cross-tissue, or cross-platform generalization [Paper: PDF p. 4] | Prior benchmarks do not assess model reliability under domain shifts or data scaling — critical for clinical deployment [Paper: PDF p. 2–4] | Fig. 5a–b quantifies generalization gaps; “cross-tissue generalization was challenging … gaps reaching −0.20 to −0.35” [Paper: PDF p. 17]; “cross-platform transfer … showed negligible performance loss” [Paper: PDF p. 17] |
| **Unclear data quality dependence** | Performance varies drastically between Visium (low counts) and Xenium (high counts) datasets, but cause is unexamined [Paper: PDF p. 10] | Gene expression prediction quality is confounded by underlying transcript detection sensitivity and signal-to-noise ratio, not just morphology [Paper: PDF p. 10, 19] | Fig. 2c-d: NCCHE-LUAD-Xenium (mean counts=52.1/72.3) achieves PCC≈0.58 vs. NCCHE-LUAD-Visium (mean counts=9.2/0.9) at PCC≈0.20; “gap is largely driven by data sparsity rather than morphological uncoupling alone” [Paper: PDF p. 10] |

## 06 核心思想  
- **核心主张**：virtual ST 领域的进展被不严谨的基准评估所掩盖；真正的架构创新必须在统一图像编码器（PFM）下被隔离评估，否则报告的增益可能完全源于 encoder 差异而非模型设计 [Paper: PDF p. 3–4, 9, 18].  
- **关键洞见 1（Encoder Dominance）**：patch encoder 的选择是性能的主导因素；UNIv2 等大规模 PFM 使多数复杂模型无法超越其线性探针基线，挑战了“架构复杂性驱动性能”的默认假设 [Paper: PDF p. 8–9].  
- **关键洞见 2（Gene-level Universality）**：基因可预测性具有跨模型强一致性（Fig. 3a），表明 morphology–expression coupling 是数据固有属性，而非模型可塑性；architecture 的作用在于将预测边界向更难基因（如 stromal/immune markers）轻微右移 [Paper: PDF p. 11, 19].  
- **关键洞见 3（Multi-scale Advantage）**：能整合局部、邻域、全局形态上下文的架构（TRIPLEX, DeepSpot）在 stromal/ECM、immune/inflammation、specialized epithelial 基因上取得最大 margin，因其依赖 meso-to-macro scale tissue patterns invisible to local patches alone [Paper: PDF p. 11–13, 19].  
- **关键洞见 4（Platform-dependence）**：virtual ST 的生物学效用上限由底层 ST 平台的数据质量（transcript counts, SNR）决定；Xenium 的高灵敏度使 downstream tasks (Cell2location, SpaGCN) perform substantially better than Visium, confirming a shared data-quality bottleneck [Paper: PDF p. 14–15, 19].  

## 07 方法总览  
STP-BENCH 是一个端到端 benchmarking framework，包含三大支柱：  
1. **Comprehensive performance evaluation**：在 STP-BENCH-INTERNAL 上，以 UNIv2 为统一 patch encoder，评估 21 模型在 HMHVGs（200 genes）和 TME marker genes（16 genes）上的 PCC/MAE/SSIM；对比 native vs. unified encoder；进行 gene-wise 和 gene-set（singscore）分析 [Paper: PDF p. 7–13, Fig. 2–3].  
2. **Multi-granularity biological utility evaluation**：在三个 cohort（NCCHE-LUAD-Xenium/Visium, WUSTL-BRCA-Visium）上，使用 Cell2location 评估 predicted profiles 对 cell type abundance 的重建能力（PCC per cell type），使用 SpaGCN + ARI 评估 spatial domain identification fidelity [Paper: PDF p. 14–15, Fig. 4].  
3. **Robustness & scalability assessment**：在 STP-BENCH-EXTERNAL 上，测试 cross-institution/cross-tissue/cross-platform generalization（Spearman ρ of internal vs. external PCC）；进行 intra-cohort（data volume）和 inter-cohort（tissue diversity）scaling 实验 [Paper: PDF p. 16–18, Fig. 5].  
所有模型均 re-implemented in PyTorch with patient-level 5-fold CV (except HEST-bench), fixed seed (2021), and standardized preprocessing (224×224 patches, log1p normalization, ImageNet norm) [Paper: PDF p. 30–31, 34].  

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **UNIv2 PFM Encoder** | Extracts 1024-dim histology embeddings from 224×224 H&E patches | To disentangle encoder contribution from architectural innovation; enables fair comparison across models [Paper: PDF p. 7–9] | Input: H&E patch (224×224); Output: 1024-dim vector [Paper: PDF p. 25–26] | Fig. 2b shows rank reversal when swapping native↔UNIv2; “unified morphological encoding substantially re-orders model rankings” [Paper: PDF p. 2] | Removal (i.e., reverting to native encoders) would reintroduce unfair comparisons and obscure true architectural effects, as shown in Fig. 2b [Paper: PDF p. 9] |
| **HMHVG + Marker Gene Panel** | Defines evaluation gene set: 200 high-mean highly-variable genes + 16 TME markers (e.g., CD3E, ACTA2, PDCD1) [Paper: PDF p. 7, 33] | To move beyond arbitrary gene sets and focus on biologically interpretable, clinically relevant targets spanning epithelial/stromal/immune lineages [Paper: PDF p. 7, 33] | Input: Raw ST count matrices; Output: Subsetted gene expression matrix [Paper: PDF p. 33] | Fig. 2a shows performance gap between HMHVGs (PCC≈0.4) and markers (PCC≈0.2); Fig. 3e shows immune gene sets (T Cell Activation) recovered by top models [Paper: PDF p. 13] | Removal would eliminate biological interpretability anchor; using only HMHVGs would miss the critical challenge of predicting low-abundance, functionally important markers [Paper: PDF p. 9] |
| **singscore-based Gene Set Scoring** | Computes per-spot gene set activity score by ranking genes within spot and averaging ranks of member genes [Paper: PDF p. 13, 35] | To evaluate whether virtual ST preserves functional pathway activity, not just individual gene levels; enables efficient computation across thousands of spots [Paper: PDF p. 13] | Input: Predicted/ground-truth expression matrix (spots × genes); Output: Spot × gene_set matrix of scores [Paper: PDF p. 13] | Fig. 3c–e show TRIPLEX/DeepSpot top-performing on immune/stromal gene sets; “gene set scoring performance was substantially higher on NCCHE-LUAD-Xenium” mirroring gene-level gap [Paper: PDF p. 13] | Removal would reduce evaluation to spot-level only, missing functional coherence; using simple mean expression instead of rank-based singscore would be sensitive to batch effects and violate assumptions of ST data sparsity [Paper: PDF p. 13] |
| **Cell2location Deconvolution** | Estimates spatial cell type abundance from ST expression using scRNA-seq reference (e.g., LuCA for LUAD) [Paper: PDF p. 35] | To test if virtual ST profiles retain sufficient biological structure for clinically relevant downstream analysis (cell composition mapping) [Paper: PDF p. 14] | Input: Predicted/ground-truth ST matrix (spots × genes); Output: Spots × cell_types abundance matrix [Paper: PDF p. 35] | Fig. 4a shows TRIPLEX/DeepSpot achieve highest PCC with ground-truth abundances; “major cell populations … were generally well-recovered, whereas rare … populations … exhibited lower correlations” [Paper: PDF p. 14] | Removal would leave evaluation at molecular level only; using a simpler deconvolution method (e.g., CIBERSORTx) without spatial priors would underestimate the value of spatially coherent predictions [Paper: PDF p. 35] |
| **SpaGCN Spatial Clustering** | Identifies spatial domains from ST expression + coordinates using graph neural network (no histology input) [Paper: PDF p. 36] | To test if virtual ST preserves spatially organized tissue architecture, independent of morphology priors [Paper: PDF p. 14] | Input: Predicted/ground-truth ST matrix + spot coordinates; Output: Domain labels per spot [Paper: PDF p. 36] | Fig. 4b–c show TRIPLEX/DeepSpot top-performing on ARI; “both downstream tasks yielded substantially higher performance for Xenium-based than Visium-based cohorts” [Paper: PDF p. 14] | Removal would omit validation of spatial coherence; using k-means instead of SpaGCN would ignore spatial graph structure and fail to capture domain boundaries [Paper: PDF p. 36] |

## 09 关键公式与符号  
- **Equation 1 (PCC)**:  
  \[
  \text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2}} \quad \text{[Paper: PDF p. 31]}
  \]  
  - \( \hat{y}_{i,g}, y_{i,g} \): predicted and ground-truth log-normalized expression of gene \( g \) at spot \( i \)  
  - \( \bar{\hat{y}}_g, \bar{y}_g \): means over all spots in section \( s \)  
  - Used as primary metric for spot-level gene prediction accuracy; NaN for zero-variance genes set to 0 [Paper: PDF p. 31].  

- **Equation 2 (MAE)**:  
  \[
  \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^{N} |\hat{y}_{i,g} - y_{i,g}| \quad \text{[Paper: PDF p. 32]}
  \]  
  - Measures absolute deviation in log(1+x)-transformed expression space.  
  - Aggregated same as PCC: gene-wise → section-wise → dataset-wise mean ± std [Paper: PDF p. 32].  

- **Other key symbols**:  
  - **HMHVG**: High-mean highly-variable genes (200 selected via rank-sum of mean expression and variability) [Paper: PDF p. 33].  
  - **TME markers**: 16 curated genes (e.g., CD3E, ACTA2, PDCD1) representing epithelial/stromal/immune lineages [Paper: PDF p. 7, 33].  
  - **ARI**: Adjusted Rand Index for spatial domain agreement between predicted and ground-truth labels [Paper: PDF p. 15, 36].  
  - **SSIM**: Structural Similarity Index Measure for spatial expression map coherence [Paper: PDF p. 32].  

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|-------------------------|-------------------------------|--------|
| **Fig. 2a (Internal PCC)** | Unified PFM standardization reveals true architectural ranking | 21 models evaluated on STP-BENCH-INTERNAL with UNIv2 (w/ PFM) vs. native encoders (w/o PFM); HMHVGs and 16 markers | Most w/ PFM models < linear probing baseline (UNIv2 LP); TRIPLEX/DeepSpot > baseline; w/o PFM models mostly < baseline | UNIv2 linear probing is a strong baseline; multi-scale regression models (TRIPLEX/DeepSpot) have genuine architectural advantage | "All other models are useless" — false, as some (e.g., Path2Space, EGN) marginally surpass baseline [Paper: PDF p. 9] | [Paper: PDF p. 8–9, Fig. 2a] |
| **Fig. 2c-d (Expression level stratification)** | Prediction accuracy is driven by transcript abundance, not inherent unpredictability | PCC computed per gene quantile (Very Low to Very High) on NCCHE-LUAD-Xenium (high counts) vs. NCCHE-LUAD-Visium (low counts) | Strong correlation between expression level and PCC (p<1e-12); Xenium achieves PCC≈0.58 for markers, Visium only ≈0.19 | Data sparsity (low transcript counts) is a major bottleneck for marker gene prediction, not morphology uncoupling | "Morphology contains no signal for immune genes" — false, as Xenium shows high predictability [Paper: PDF p. 10] | [Paper: PDF p. 10, Fig. 2c-d] |
| **Fig. 3a (Gene-wise heatmap)** | Gene predictability is universal across models | PCC computed per gene across 20 models (excluding zero-shot OmiCLIP/STPath) on union of HMHVGs+markers | Smooth separation of high/low-performing genes; consistent ordering across models; curved boundary indicates architecture shifts predictability threshold | Gene-level predictability is governed by morphology-expression coupling, not model choice; architectures shift the boundary, not the fundamental ceiling | "Architecture determines *which* genes are predictable" — overstates; it shifts margin, but core easy/hard genes are shared [Paper: PDF p. 11] | [Paper: PDF p. 11, Fig. 3a] |
| **Fig. 4a (Cell2location)** | Virtual ST preserves cell-type spatial organization | Cell2location applied to ground-truth vs. predicted ST; PCC computed per cell type (e.g., malignant epithelial, T cells) | TRIPLEX/DeepSpot achieve highest PCC; major populations well-recovered, rare populations (plasma/mast cells) poorly recovered | Top-performing gene-level models translate to superior cell deconvolution; platform quality (Xenium > Visium) limits upper bound | "Virtual ST enables clinical-grade cell typing" — unsupported, as rare populations fail [Paper: PDF p. 14] | [Paper: PDF p. 14–15, Fig. 4a] |
| **Fig. 5a (Cross-tissue generalization)** | Internal rankings predict external performance under biological shift | Spearman ρ between internal PCC and external PCC averaged across all cross-tissue dataset pairs (e.g., train on LUAD, test on BRCA) | ρ = 0.876 (p=1.87e-6), strong rank preservation despite large absolute drop (gap ≈−0.2 to −0.35) | Architectural superiority is generalizable across tissues; cross-tissue shift is harder than cross-institution | "Models trained on one cancer generalize to all cancers" — false, as absolute performance drops severely [Paper: PDF p. 17] | [Paper: PDF p. 16–17, Fig. 5a] |

## 11 对结论的正确理解  
- **"Most models fail to beat linear probing"** means that, under unified UNIv2 encoding, the incremental gain of complex architectures (e.g., Transformers, GNNs, contrastive alignment) over a simple linear map from PFM features is often marginal or negative — *not* that these models are useless, but that their reported gains in prior work were likely inflated by superior native encoders [Paper: PDF p. 8–9].  
- **"Gene predictability is universal"** means that the *ranking* of genes by ease-of-prediction (e.g., COL1A1 easy, PDCD1 hard) is consistent across all 20+ models — *not* that all models achieve identical PCC for each gene, but that the relative difficulty landscape is data-intrinsic [Paper: PDF p. 11, Fig. 3a].  
- **"TRIPLEX/DeepSpot are best"** is context-dependent: they lead on HMHVGs, markers, gene sets, Cell2location, and SpaGCN *within this benchmark*, but their advantage is most pronounced for stromal/immune genes requiring multi-scale reasoning; they do not dominate on all metrics (e.g., SSIM trends are similar but not shown as top) [Paper: PDF p. 11–15].  
- **"Xenium > Visium"** reflects platform-specific technical advantages (higher sensitivity, more transcripts), not a fundamental limitation of virtual ST — *it means the ceiling of what morphology can predict is raised by better ground-truth data quality* [Paper: PDF p. 10, 14, 19].  
- **"Negative transfer in inter-cohort scaling"** means adding BRCA+LUAD+PRAD training data *harms* BRCA test performance — *not* that multi-cancer training is always bad, but that naive aggregation without tissue-aware adaptation is detrimental due to morphological specificity [Paper: PDF p. 18, Fig. 5d].  

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium); lacks rare tumors, normal tissues, and emerging platforms (e.g., Stereo-seq) [Paper: PDF p. 20] | Extend benchmark to additional tumor types, tissue contexts, and sequencing platforms for broader generalizability [Paper: PDF p. 20] | [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focused on HMHVGs (200) and 16 TME markers; systematic investigation of lowly expressed, housekeeping, or functionally diverse genes is absent [Paper: PDF p. 20] | Systematic investigation of lowly expressed or functionally diverse genes remains an open direction [Paper: PDF p. 20] | [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluations performed at spot-level (aggregates multiple cells); single-cell ST and virtual ST models are emerging but not benchmarked [Paper: PDF p. 20] | Future benchmarking efforts may extend principles to single-cell resolution as data and models mature [Paper: PDF p. 20] | [Paper: PDF p. 20] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| **Linear probing baseline uses UNIv2, but its architecture is not "zero-parameter"** — it includes Softplus output activation and log1p normalization, while some models (e.g., retrieval-based) have no such constraints [Paper: PDF p. 23, 31]. | The baseline may be artificially advantaged by domain-appropriate output constraints (non-negativity) and preprocessing, making it harder for other models to beat. A truly minimal baseline (e.g., linear + identity) might yield different rankings. | Overstating the strength of the baseline could misattribute architectural weakness; fairness requires matching *all* components, not just the encoder. | Re-run Fig. 2a with a stripped-down linear probe: no Softplus, raw counts (no log1p), and compare. If rankings shift (e.g., more models beat it), the current baseline is inflated. | [Paper: PDF p. 23 (Softplus), p. 31 (log1p), p. 8 (baseline definition)] |
| **Gene set analysis (Fig. 3e) uses singscore on HMHVG+marker union, but many GO terms have poor overlap with this limited panel** — filtering retained only gene sets with ≥5 overlapping genes covering ≥10% of original set [Paper: PDF p. 35]. | This stringent filtering may exclude biologically relevant pathways (e.g., metabolism, DNA repair) simply because their genes weren't in the HMHVG/marker panel, creating a biased view of "recoverable biology". | Conclusions about "which biological programs are recoverable" are constrained by the evaluation gene set, not morphology. It risks conflating panel incompleteness with biological irrecoverability. | Expand gene panel to include broad functional categories (e.g., Hallmark gene sets) and recompute singscore. If new pathways (e.g., OxPhos) show high PCC, current conclusions are panel-limited. | [Paper: PDF p. 35 (filtering criteria), p. 13 (singscore rationale)] |
| **Cross-platform transfer (Visium→Xenium) shows "negligible loss" (Fig. 5b right), but Xenium has higher transcript counts — the gain may reflect easier prediction on higher-SNR data, not true cross-platform robustness** [Paper: PDF p. 17]. | The apparent success masks a confound: models aren't generalizing *across platforms*, but benefiting from Xenium's superior data quality. A true test would be Xenium→Visium, which likely shows larger degradation. | Misinterpreting this as "platform-agnostic" could mislead developers into ignoring platform-specific calibration needs for clinical deployment. | Conduct reverse transfer (Xenium-trained → Visium-test) and report gap. If gap is large (e.g., >−0.2), the current "robustness" claim is asymmetric and context-dependent. | [Paper: PDF p. 17 ("Visium →Xenium"), p. 10 (Xenium counts > Visium)] |
| **Inter-cohort scaling shows negative transfer (Fig. 5d), but the experiment adds LUAD then PRAD — the order may matter**. Adding a more morphologically similar cancer first (e.g., BRCA→other breast subtypes) might avoid negative transfer. | The conclusion "simple aggregation is detrimental" is overly broad; it depends on the *pairwise morphological distance* between cancers, not just count. A tissue-aware curriculum (similar→dissimilar) might help. | Overgeneralizing could discourage multi-cancer training; a nuanced view would guide better data curation strategies (e.g., cluster cancers by morphology before merging). | Cluster cancers by histological similarity (e.g., using PFM embeddings), then test scaling order: similar→dissimilar vs. random. If similar-first improves BRCA performance, negative transfer is order-dependent. | [Paper: PDF p. 18 (scaling order: BRCA→LUAD→PRAD), p. 19 ("tissue-specific nature")] |

## 14 学到的知识  
- **Benchmarking hygiene is non-negotiable**: Standardizing the image encoder (PFM) is essential to isolate architectural contributions; prior field progress was likely overestimated due to encoder heterogeneity [Paper: PDF p. 3–4, 9, 18].  
- **virtual ST has a "morphology ceiling"**: Gene predictability is largely universal across models, implying that the limit is set by how much transcriptional information morphology *actually contains*, not by current model capacity [Paper: PDF p. 11, 19].  
- **Multi-scale context is irreplaceable for microenvironment biology**: Stromal (COL1A1), immune (LAG3), and specialized epithelial (SFTPC) genes require integration beyond local patches — architectures like TRIPLEX (target+neighbor+global branches) or DeepSpot (spot+sub-spot+neighbor) are uniquely suited [Paper: PDF p. 11–13, 19].  
- **Data quality is the master variable**: Xenium’s higher transcript counts lift performance across *all* levels (gene PCC, gene-set scores, Cell2location, SpaGCN), proving that virtual ST’s ultimate utility is gated by experimental ST platform quality, not just algorithmic ingenuity [Paper: PDF p. 10, 14, 19].  
- **Robustness is hierarchical**: Cross-institution shifts (technical) preserve rankings well (ρ>0.86); cross-tissue shifts (biological) preserve rankings but with large absolute drops (gap≈−0.3); cross-platform shifts are unstable and model-specific — guiding deployment: prioritize tissue-matched models [Paper: PDF p. 16–17, Fig. 5].  

## 15 与既有知识的连接  
- **single-cell foundation models**: STP-BENCH operates at spot-level, not single-cell; however, its finding that morphology-to-expression coupling is intrinsic (not model-dependent) [Paper: PDF p. 11] suggests single-cell virtual ST may face even stricter ceilings due to greater cellular heterogeneity within spots — motivating future single-cell extension [Paper: PDF p. 20].  
- **spatial transcriptomics**: Directly addresses ST’s cost barrier; validates that Xenium’s technical superiority translates to virtual ST utility [Paper: PDF p. 10, 14], reinforcing ST platform choice as a key experimental design factor.  
- **graph neural networks**: Models like EGGN and SEPAL use GNNs for spatial refinement [Paper: PDF p. 24–25], but STP-BENCH shows their spot-level PCC (Fig. 2a) lags behind TRIPLEX/DeepSpot — suggesting that pure spatial graph reasoning without explicit multi-scale morphology integration is insufficient.  
- **multi-omics**: STP-BENCH is inherently multi-omics (histology + transcriptomics); its conclusion that encoder choice dominates architecture [Paper: PDF p. 9] implies that for other multi-omics pairs (e.g., genomics+transcriptomics), representation learning quality may similarly eclipse fusion architecture.  
- **biomedical AI**: Provides a template for rigorous benchmarking in biomedical AI: large-scale, standardized, multi-metric, and biologically grounded — moving beyond "SOTA chasing" to understanding fundamental limits [Paper: PDF p. 2–4].  
- **perturbation prediction / cell state representation / cross-modal alignment**: Weak connection/methodological connection. STP-BENCH does not address perturbations (e.g., drug treatment), latent cell states, or explicit cross-modal alignment beyond CLIP-style contrastive learning (BLEEP/STco) — those are distinct problem formulations not evaluated here [Paper: PDF p. 3–6].  

## 16 研究想法  

- **name**: Morphology-Informed Gene Set Prioritization (MIGSP)  
  **originating limitation/observation**: Gene set analysis (Fig. 3e) is constrained by the HMHVG+marker panel; many biologically relevant pathways are excluded due to poor overlap [Paper: PDF p. 35].  
  **core hypothesis**: Morphology-informed gene set selection — prioritizing gene sets whose member genes are individually predictable from H&E (high gene-wise PCC) — will yield more robust and biologically coherent virtual ST predictions than fixed panels.  
  **delta from paper**: Instead of predefining panels, dynamically select gene sets based on empirical predictability (e.g., top 10% of genes by median PCC across models), then compute singscore only on those.  
  **initial method**: On STP-BENCH-INTERNAL, compute gene-wise PCC for all models; for each GO term, calculate mean PCC of its members; retain top-k terms by mean PCC; re-run gene-set scoring (Fig. 3e) on this morphology-prioritized set.  
  **validation**: Compare ARI (Fig. 4c) and Cell2location PCC (Fig. 4a) using morphology-prioritized vs. fixed (GO BP 2023) gene sets; expect higher downstream fidelity for prioritized sets.  
  **failure modes**: If morphology-prioritized sets are too narrow (e.g., only ECM genes), they may lack functional diversity; if predictability is noisy, selection may overfit.  
  **innovation status**: unverified  

- **name**: Tissue-Aware Multi-Cancer Training (TAMCT)  
  **originating limitation/observation**: Inter-cohort scaling shows negative transfer (Fig. 5d) because naive aggregation of BRCA+LUAD+PRAD harms BRCA performance [Paper: PDF p. 18].  
  **core hypothesis**: Learning tissue-specific adapter modules (e.g., LoRA layers) on top of a shared backbone, conditioned on tissue-type embeddings, will enable positive transfer across cancers without sacrificing tissue-specific fidelity.  
  **delta from paper**: Replace uniform training on merged data (Fig. 5d) with a modular architecture: shared encoder + tissue-specific adapters + tissue-type token input.  
  **initial method**: Modify TRIPLEX/DeepSpot to accept tissue-type ID; add trainable LoRA adapters to key layers; train on BRCA+LUAD+PRAD with tissue ID; evaluate BRCA test performance vs. baseline (Fig. 5d).  
  **validation**: If TAMCT achieves BRCA PCC > baseline (Fig. 5d) and maintains LUAD/PRAD performance, negative transfer is mitigated.  
  **failure modes**: Adapter overfitting to small tissue cohorts; increased inference latency; need for tissue-ID at test time.  
  **innovation status**: unverified  

- **name**: Cross-Platform Calibration via Latent Alignment (CPLA)  
  **originating limitation/observation**: Cross-platform transfer (Visium→Xenium) shows model-specific gains/losses (Fig. 5b right), suggesting platform mismatch is not handled uniformly [Paper: PDF p. 17].  
  **core hypothesis**: Aligning the latent spaces of Visium and Xenium expression profiles (e.g., via adversarial domain adaptation on PFM-conditioned embeddings) will stabilize cross-platform generalization.  
  **delta from paper**: Add a domain alignment module between the PFM encoder and the ST predictor, trained to minimize Visium-Xenium distribution divergence in the prediction head's input space.  
  **initial method**: For TRIPLEX trained on Visium, add a gradient reversal layer before the fusion encoder; train with Visium (source) and Xenium (target) pseudo-spot embeddings to confuse a domain classifier.  
  **validation**: Test calibrated model on STP-BENCH-EXTERNAL cross-platform pairs; expect reduced variance in Fig. 5b right and higher mean PCC than uncalibrated.  
  **failure modes**: Alignment may erase biologically meaningful platform differences; requires paired Visium/Xenium data for stable training.  
  **innovation status**: unverified