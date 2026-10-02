> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: resource  
> Secondary analytical lens: methods  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | STP-BENCH: A Unified Systematic Benchmark for Virtual Spatial Transcriptomics from Histopathology Images | [Paper] [Paper: PDF p. 1] |
| Authors | Youngmin Chung, Ji Hun Ha, Andrew H. Song, et al. | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint | [Paper: URL] |
| Year | 2026 | [Paper: Published] |
| Core contribution | First large-scale, standardized benchmark for virtual ST models, enabling controlled comparison of architectures under unified PFM encoding, multi-granularity biological evaluation, and domain-shift robustness testing | [Paper] [Paper: PDF p. 2–4], [Paper] [Paper: PDF p. 5 Fig. 1], [Paper] [Paper: PDF p. 18–19] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium/Xenium); STP-BENCH-EXTERNAL (185,831 spots, same 6 cancers) | [Paper] [Paper: PDF p. 4], [Figure 1b], [Paper] [Paper: PDF p. 21] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6], [Figure 1c], [Paper] [Paper: PDF p. 22] |
| Primary metric | Pearson Correlation Coefficient (PCC) per gene, averaged across spots → sections → folds → datasets | [Equation 1], [Paper] [Paper: PDF p. 31], [Figure 2a] |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结

STP-BENCH 是首个面向 virtual spatial transcriptomics（vST）的系统性、大规模、标准化基准，它通过统一病理基础模型（PFM）编码器解耦架构创新与图像表征能力，揭示多数现有模型未超越线性探针基线；该基准不仅量化基因级预测精度，更首次在基因集、细胞类型丰度、空间结构域等多生物学粒度上评估下游效用，并系统刻画跨机构、跨组织、跨平台泛化鲁棒性。其核心价值在于提供可复现、可归因、可迁移的评估框架，而非提出新模型——这使其成为 single-cell foundation models、spatial transcriptomics 和 biomedical AI 领域方法验证与迭代的关键基础设施。边界明确：仅覆盖 spot-level vST（非 single-cell resolution），限于 6 种癌症和 2 种平台（Visium/Xenium），未涉及 perturbation prediction 或 cross-modal alignment 的显式建模。

## 03 研究问题

论文直面一个**评估失焦**问题：virtual ST 领域虽涌现大量模型（回归/检索/生成），但缺乏公平、可控、可复现的基准，导致无法判断性能提升源于架构创新还是图像编码器差异；进而引申出三个子问题：（1）当统一使用 UNIv2 等 PFM 作为 patch encoder 时，现有模型的真实架构优势是否仍成立？（2）哪些基因或基因集能被稳定地从形态学中恢复？这种可预测性是否具有生物学一致性？（3）vST 预测结果能否支撑下游生物分析任务（如 cell type deconvolution、spatial domain identification），且其可靠性是否随数据质量（如 Xenium vs Visium）和域偏移（cross-tissue）而系统性变化？这些问题共同指向一个根本目标：建立一个能分离“表征能力”与“建模能力”、连接“预测精度”与“生物效用”的评估范式。

## 04 研究背景与发展路径

背景始于 ST 技术的高成本瓶颈与 H&E 图像蕴含转录信息的生物学共识，催生了 virtual ST 这一计算替代路径。发展路径呈现两条交织线索：一是**模型范式演进**——从早期回归模型（ST-Net）扩展至融合邻域/全局上下文（TRIPLEX, DeepSpot）、引入 exemplar 检索（EGN）、CLIP 式双模对齐（BLEEP, STco）及生成建模（STFlow, Stem）；二是**评估范式退化**——既有工作（Wang et al. 2024; HEST-1K）或沿用原生 encoder 导致架构与编码器混淆 [Paper] [Paper: PDF p. 3–4]，或仅用简单回归器测试 PFM embedding 而忽略完整模型链路 [Paper] [Paper: PDF p. 3]，均未能实现“控制变量”式比较。STP-BENCH 的提出正是对这一评估断层的直接回应：它不延续单点模型优化路径，而是构建一个正交于模型开发的基础设施层，将评估本身升格为可被严格定义、测量和质疑的科学活动。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平性** | 模型排名高度依赖所用图像编码器，导致架构贡献被掩盖 | “architectural innovations and image encoding have been conflated in previous evaluations”；不同 encoder（ResNet50 vs UNIv2）使 CFANet 排名从第16跃至第6 [Paper] [Paper: PDF p. 2, 9] | [Paper] [Paper: PDF p. 2] “unified morphological encoding substantially re-orders model rankings”; [Figure 2b]; [Paper] [Paper: PDF p. 9] “CFANet... jumped to 6th when using UNIv2” |
| **评价维度单一** | 仅报告 aggregate gene-level PCC，忽略 per-gene 可预测性、基因集功能、下游任务效用 | Prior studies “leave the biological reliability... and model robustness... largely unexamined” [Paper] [Paper: PDF p. 3]; “evaluation has been confined to aggregate predictive accuracy” [Paper] [Paper: PDF p. 4] | [Paper] [Paper: PDF p. 3–4]; [Figure 1e-f]; [Paper] [Paper: PDF p. 11–14] gene-wise heatmap & gene set analysis; [Figure 4] cell type & domain evaluation |
| **鲁棒性未知** | 模型在真实场景（跨医院、跨癌种、跨平台）下的泛化能力未经系统检验 | “model robustness under realistic distribution shifts largely unexamined” [Paper] [Paper: PDF p. 3]; “no existing benchmark... assesses model reliability under domain shifts” [Paper] [Paper: PDF p. 4] | [Figure 5a-b]; [Paper] [Paper: PDF p. 17] “cross-institution”, “cross-tissue”, “cross-platform” transfer experiments; [Paper] [Paper: PDF p. 19] “cross-tissue generalization was challenging” |
| **数据驱动瓶颈** | 性能差异可能源于底层 ST 数据质量（如 transcript counts），而非模型能力 | “the quality of the underlying transcript detection plays a role in the model’s predictive performance” [Paper] [Paper: PDF p. 10]; “gene expression prediction gap between platforms” [Paper] [Paper: PDF p. 14] | [Figure 2c-d] NCCHE-LUAD-Xenium (high counts) vs NCCHE-LUAD-Visium (low counts); [Paper] [Paper: PDF p. 10] “marker-gene prediction was substantially weaker” in Visium; [Paper] [Paper: PDF p. 14] “concordance suggests that transcript-level data quality constitutes a key determinant” |

## 06 核心思想

论文的核心思想是：**virtual ST 的评估必须从“黑箱精度竞赛”转向“白盒能力解构”**。这体现为三个相互支撑的支柱：（1）**解耦原则**：强制统一 PFM（如 UNIv2）作为所有兼容模型的 patch encoder，将图像表征能力（encoder）与建模能力（architecture）分离，使模型比较真正反映后者价值；（2）**多粒度验证原则**：拒绝仅用 HMHVG 平均 PCC 定论，转而系统考察基因级（哪些基因可预测）、基因集级（哪些通路可恢复）、细胞级（cell abundance 是否准确）、组织级（spatial domains 是否可识别）的逐层效用，形成从分子到组织的证据链；（3）**现实鲁棒性原则**：将泛化性视为核心指标，设计 cross-institution/tissue/platform 三类域偏移实验，揭示模型优势的适用边界（如 multi-scale 架构在 cross-tissue 下失效），从而指导临床部署而非仅追求内参最优。

## 07 方法总览

STP-BENCH 的方法论是一个**四层评估栈**：（1）**数据层**：构建 STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与 STP-BENCH-EXTERNAL（186k spots, strict train/test separation），统一预处理（Visium patch cropping, Xenium pseudo-spot binning）[Paper] [Paper: PDF p. 4–6, 21–22]；（2）**模型层**：重实现 21 个模型，按架构分为 Regression（14）、Bi-Retrieval（4）、Generative（3），对兼容者强制替换为 UNIv2 encoder [Paper] [Paper: PDF p. 6–7, 22–29]；（3）**度量层**：主用 PCC（Eq.1），辅以 MAE（Eq.2）和 SSIM，覆盖精度、误差、空间结构三维度 [Paper] [Paper: PDF p. 31–32]；（4）**分析层**：执行四大分析模块——内部性能基准（Fig.2）、基因/基因集剖析（Fig.3）、下游生物效用（Fig.4）、鲁棒性与可扩展性（Fig.5），每项均基于统一 pipeline 与 cross-validation [Paper] [Paper: PDF p. 7–18]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **Unified PFM Encoder (e.g., UNIv2)** | Standardizes histology feature extraction across all compatible models | To isolate architectural contribution from encoder quality; prior work conflated them [Paper] [Paper: PDF p. 2, 9] | Input: 224×224 H&E patch; Output: fixed-dim embedding vector | [Figure 2a-b], [Paper] [Paper: PDF p. 7–9], [Paper] [Paper: PDF p. 22–23] "image encoder of each model was replaced with a common PFM" | Model rankings collapse to noise; e.g., CFANet drops from top-6 to bottom-tier without UNIv2 [Figure 2b] |
| **Gene Set Scoring (singscore)** | Computes per-spot activity score for GO Biological Process terms from predicted expression | To bridge gene-level prediction to functional pathway recovery, beyond individual gene PCC | Input: predicted & ground-truth spot-by-gene matrix; Output: spot-by-gene-set correlation (PCC) | [Figure 3c-e], [Paper] [Paper: PDF p. 13], [Paper] [Paper: PDF p. 35] "gene set level prediction analysis using singscore" | Loss of biological interpretability; TRIPLEX/DeepSpot advantage over baseline would be invisible at gene-set level [Figure 3c] |
| **Cell Type Deconvolution (Cell2location)** | Estimates spatial abundance of cell types from vST profiles | To test if vST preserves cellular composition structure required for downstream analysis | Input: vST expression matrix; Output: per-spot cell-type abundance estimates (vs ground-truth) | [Figure 4a], [Paper] [Paper: PDF p. 14], [Paper] [Paper: PDF p. 35] "applied Cell2location to both true and model-predicted matrices" | Downstream utility claim becomes unsubstantiated; TRIPLEX/DeepSpot superiority in cell abundance correlation vanishes [Figure 4a] |
| **Spatial Domain Identification (SpaGCN)** | Clusters spots into spatially contiguous domains from vST profiles | To evaluate if vST captures tissue-level architectural organization, not just molecular signals | Input: vST expression + coordinates; Output: Adjusted Rand Index (ARI) vs reference domains | [Figure 4b-c], [Paper] [Paper: PDF p. 14], [Paper] [Paper: PDF p. 36] "applied SpaGCN to both ground-truth and model-predicted matrices" | Inability to validate spatial coherence; ARI scores for TRIPLEX/DeepSpot on Xenium would lack empirical support [Figure 4c] |
| **Cross-Tissue Generalization Test** | Evaluates model trained on one cancer type (e.g., LUAD) on another (e.g., BRCA) | To quantify the tissue-specificity of morphology-to-expression mapping, a key real-world constraint | Input: model checkpoint trained on source cancer; Output: PCC drop on target cancer (generalization gap) | [Figure 5b middle], [Paper] [Paper: PDF p. 17] "cross-tissue transfer... challenged models to generalize across different anatomical sites" | Over-optimistic deployment guidance; failure to reveal that cross-tissue gap (-0.2 to -0.35) dwarfs cross-institution gap (-0.05 to -0.10) [Figure 5b] |

## 09 关键公式与符号

论文明确给出两个可核验公式：  
- **Equation 1**（[Paper] [Paper: PDF p. 31]）：Pearson Correlation Coefficient (PCC)，用于 spot-level gene-wise prediction accuracy：  
  $$\text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2}}$$  
  符号：$\hat{y}_{i,g}$ 为 spot $i$ 上 gene $g$ 的预测 log-normalized 表达；$y_{i,g}$ 为 ground-truth；$\bar{\hat{y}}_g$, $\bar{y}_g$ 为其均值；$N$ 为 spots 数量。  
- **Equation 2**（[Paper] [Paper: PDF p. 32]）：Mean Absolute Error (MAE)，用于量化预测误差幅度：  
  $$\text{MAE}_{g,s} = \frac{1}{N}\sum_{i=1}^{N}|\hat{y}_{i,g} - y_{i,g}|$$  
  符号同上。  
无其他可核验公式。关键指标符号：PCC（Pearson Correlation Coefficient）、SSIM（Structural Similarity Index Measure）、MAE（Mean Absolute Error）、ARI（Adjusted Rand Index）、HMHVG（high-mean highly-variable genes）、TME（tumor microenvironment）。所有指标均在 [Paper] [Paper: PDF p. 31–32] 明确定义。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| **UNIv2 vs Native Encoder (Fig.2b)** | Unified PFM standardization changes model rankings | Compare CFANet's rank with native encoder (linear projection) vs UNIv2; same dataset (STP-BENCH-INTERNAL), same HMHVG genes | CFANet rank jumps from 16th → 6th with UNIv2 | Encoder choice dominates reported architectural gains; fair comparison requires encoder standardization | UNIv2 is universally optimal encoder (not tested across all PFMs in this exp) | [Figure 2b], [Paper] [Paper: PDF p. 9] |
| **Gene Expression Level Stratification (Fig.2c-d)** | Prediction accuracy depends on basal transcript count | Stratify genes into 5 bins by mean expression; compute PCC per bin for NCCHE-LUAD-Xenium/Visium | Strong correlation (p<1e-12) between expression level and PCC; Xenium (high counts) achieves PCC≈0.58, Visium (low counts) PCC≈0.19 for markers | Data quality (transcript count) is a primary bottleneck, not just model architecture | All low-expression genes are inherently unpredictable (not tested; some may be predictable with better models) | [Figure 2c-d], [Paper] [Paper: PDF p. 10] |
| **Multi-scale Architecture Advantage (Fig.3b)** | TRIPLEX/DeepSpot gain over linear probe is gene-category specific | Compute ∆PCC = PCC<sub>model</sub> - PCC<sub>LinearProb</sub> for genes with PCC≥0.4 & ∆PCC≥0.1 | Top gains in stromal (COL1A1), immune (LAG3), epithelial (AZGP1) genes; TRIPLEX/DeepSpot dominate | Multi-scale context (local+neighbor+global) is critical for genes dependent on meso/macro-scale morphology | This advantage extends to single-cell resolution (not evaluated; STP-BENCH is spot-level) | [Figure 3b], [Paper] [Paper: PDF p. 11–13] |
| **Downstream Utility (Fig.4a)** | vST profiles preserve cell-type spatial organization | Apply Cell2location to vST profiles; correlate predicted vs ground-truth cell abundance per cell type | TRIPLEX/DeepSpot achieve highest avg PCC; malignant epithelial/T cells well-recovered, plasma/mast cells poorly recovered | Gene-level accuracy translates to cellular granularity; vST utility is hierarchical | vST can replace true ST for clinical cell typing (not validated; rare populations show low correlation) | [Figure 4a], [Paper] [Paper: PDF p. 14] |
| **Cross-Tissue Generalization (Fig.5b middle)** | Morphology-to-expression mapping is highly tissue-specific | Train model on LUAD, test on BRCA; measure PCC drop (generalization gap) | Gap reaches -0.20 to -0.35, far larger than cross-institution gap (-0.05 to -0.10) | Cross-tissue transfer is the most challenging real-world scenario; simple data aggregation harms performance | Domain adaptation can fully close this gap (not tested; inter-cohort scaling showed negative transfer [Fig.5d]) | [Figure 5b], [Paper] [Paper: PDF p. 17] |

## 11 对结论的正确理解

论文结论必须被精确限定在其实证范围内：（1）“多数模型未超越线性探针”仅指在**UNIv2 编码器下、spot-level HMHVG/Marker 基因 PCC** 这一特定评估设置中，不否定其在其他 encoder、其他基因集、其他任务（如 retrieval）上的价值；（2）“multi-scale 架构优势”特指对**stromal/immune/epithelial 基因**的预测增益，源于其对 meso/macro-scale 形态的建模能力，而非普适性架构优越；（3）“Xenium 数据质量更高”是**经验观察**（NCCHE-LUAD-Xenium 平均计数 52.1 vs Visium 9.2），支撑了“数据质量是瓶颈”的推论，但未证明 Xenium 在所有癌种/平台对比中均优；（4）“cross-tissue 泛化最难”是基于**6 癌种间转移**的实证，不意味着所有跨组织场景均不可行，亦不排除 tissue-aware 方法的潜力；（5）“negative transfer in inter-cohort scaling”指在**BRCA→LUAD→PRAD 顺序添加**时性能下降，不否定其他数据混合策略（如 curriculum learning）的有效性。所有结论均锚定于 STP-BENCH 的具体设计，不可外推至 single-cell 或非-ST 领域。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer types & platforms** | STP-BENCH covers only 6 cancers and 2 ST platforms (Visium/Xenium), constraining generalizability | Extend benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Gene-level analyses focused only on HMHVGs and 16 TME markers; systematic investigation of lowly expressed or functionally diverse genes remains open | Systematic investigation of lowly expressed or functionally diverse genes | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution** | Evaluations performed at spot-level (aggregating multiple cells), not single-cell resolution | Future benchmarking efforts may extend these principles to single-cell ST datasets and models | [Paper] [Paper: PDF p. 20] |
| **No single-cell ST integration** | Benchmark does not incorporate single-cell ST data or models, despite increasing availability | Not explicitly stated as future direction, but implied by the limitation on resolution | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|------------------------------------------|----------------|----------------|-------|
| **TRIPLEX/DeepSpot's multi-scale advantage may conflate architecture with training data scale** | These top performers were trained on the largest internal datasets (e.g., WUSTL-BRCA: 157k spots); their edge could stem from data volume, not architectural design per se | Misattribution could misguide architecture search; users might over-invest in complex multi-scale models when data scaling suffices | Re-train TRIPLEX/DeepSpot on smaller subsets (e.g., 33% of WUSTL-BRCA) and compare to simpler models (e.g., LinearProb) trained on same subset; control for data volume | [Figure 5c] shows intra-cohort scaling yields only marginal gains, but doesn't isolate architecture × data interaction; [Paper] [Paper: PDF p. 21] notes WUSTL-BRCA is largest cohort |
| **The "universal gene-wise predictability" pattern may be dataset-dependent** | The high concordance across models (Fig.3a) is observed on STP-BENCH-INTERNAL, but its stability across vastly different tissue architectures (e.g., brain vs skin) or pathological states (e.g., treatment-naive vs resistant) is untested | If predictability is not universal, gene selection for clinical vST assays must be context-specific, undermining the benchmark's generalizability claim | Evaluate the same 20 models on an external, highly distinct dataset (e.g., melanoma or sarcoma) and compute gene-wise PCC correlation across models; compare to STP-BENCH's ρ | [Paper] [Paper: PDF p. 11] "gene-wise concordance was consistently observed across additional datasets (Extended Data Fig. 4a)", but those are all within the 6-cancer STP-BENCH scope |
| **Using UNIv2 as the sole PFM for "unified" evaluation ignores encoder heterogeneity** | While UNIv2 is state-of-the-art, other PFMs (Virchow2, H-Optimus1) show comparable performance (Fig.2e); ranking models solely on UNIv2 may not reflect their true potential with a better-matched encoder | For users with domain-specific PFMs, STP-BENCH rankings may be suboptimal; benchmark should report encoder × model interaction | Report full 5×21 matrix of PCC for all 5 encoders (Fig.2e) across all 21 models, not just top-10; perform ANOVA to test encoder × model interaction significance | [Figure 2e] shows 5 encoders' performance, but only for 10 models; [Paper] [Paper: PDF p. 10] notes Virchow2/H-Optimus1 "achieved the highest and broadly comparable performance" |
| **Cell2location deconvolution on vST may inherit its own biases** | Cell2location assumes a linear mixing model and relies on scRNA-seq references; if vST predictions have systematic biases (e.g., over-smoothing), deconvolution errors may reflect the tool's limitations, not vST quality | Downstream utility claims become confounded; a poor Cell2location result doesn't necessarily mean vST failed to capture cell composition | Replace Cell2location with orthogonal deconvolution methods (e.g., SPOTlight, RCTD) and compare correlation trends; or use simulated ground-truth with known cell mixtures | [Paper] [Paper: PDF p. 35] specifies Cell2location parameters but no validation against alternative tools; [Paper] [Paper: PDF p. 20] admits "limitations inherent to deconvolution-based estimation" |

## 14 学到的知识

- **评估即设计**：一个高质量 benchmark 不是数据集堆砌，而是包含数据构造（STP-BENCH-INTERNAL/EXTERNAL 分离）、模型重实现（21 模型统一 pipeline）、度量定义（PCC/SSIM/MAE 三级指标）、分析维度（gene/gene-set/cell/domain/robustness）的完整工程。用户可直接复用其 `HESTData` 兼容格式与 `singscore` 基因集分析流程。
- **PFM 是 vST 的“新基座”**：UNIv2 等 PFM 的引入，使图像编码器从模型附属品升格为独立可评估组件。其性能（Fig.2e）与鲁棒性（Extended Data Fig.5-6）直接决定下游任务上限，提示用户在 single-cell foundation models 中应优先验证 PFM 的跨组织泛化性。
- **基因可预测性存在生物学层级**：并非所有基因同等可预测。Stromal/ECM、immune/inflammation、specialized epithelial 基因构成“高价值靶标”，因其依赖 multi-scale 形态，这为用户设计 perturbation prediction 模型提供了先验知识——应显式建模空间上下文。
- **数据质量是隐性天花板**：Xenium 与 Visium 的性能鸿沟（Fig.2c-d, Fig.4）表明，vST 的终极瓶颈可能不在算法，而在底层 ST 技术的灵敏度。这警示用户：在 multi-omics 整合中，需对不同模态的数据质量进行校准，而非简单拼接。
- **鲁棒性比精度更具部署价值**：Cross-tissue 泛化失败（Fig.5b）远比内部 PCC 差异更致命。用户若构建 spatial transcriptomics 工具，应将 cross-tissue/cross-platform 测试纳入标准开发流程，而非仅优化内参。

## 15 与既有知识的连接

- **候选连接/方法论连接**：STP-BENCH 的 multi-granularity 评估框架（gene → gene-set → cell → domain）与 single-cell foundation models 的 hierarchical representation learning（如 cell-type → tissue-context）理念相通，但 STP-BENCH 尚未在 single-cell resolution 上验证，故为候选连接。
- **候选连接/方法论连接**：其 cross-platform (Visium→Xenium) 泛化实验与 spatial transcriptomics 领域对 multi-resolution data 对齐（如 Visium spot vs Xenium cell）的需求一致，但 STP-BENCH 仅做 pseudo-spot 转换，未涉及真正的 multi-resolution graph neural networks 建模，故为候选连接。
- **候选连接/方法论连接**：基因集分析（singscore）和下游任务（Cell2location, SpaGCN）的评估逻辑，可迁移到 multi-omics 领域的 cross-modal alignment 评估中——例如，不只看 omics embedding 的 cosine similarity，更要看 alignment 后能否支撑 pathway enrichment 或 cell-type annotation。
- **弱连接/方法论连接**：论文未涉及 perturbation prediction（如 drug response）或 cell state representation（如 trajectory inference），这些是 biomedical AI 的前沿方向，但 STP-BENCH 提供的 robustness analysis（Fig.5）和 gene-set scoring（Fig.3）可作为其评估子模块。
- **弱连接/方法论连接**：其对 encoder-architecture 解耦的强调，与 graph neural networks 中 message-passing mechanism 与 node embedding initialization 的分离思想类似，但未在图结构数据上实践，故为弱连接。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware PFM Adapter for Cross-Tissue vST  
  **originating limitation/observation**: Cross-tissue generalization gap is severe (Fig.5b), and inter-cohort scaling harms performance (Fig.5d), suggesting tissue-specific morphology-to-expression mappings [Paper] [Paper: PDF p. 17, 19].  
  **core hypothesis**: A lightweight, tissue-specific adapter module inserted between a frozen PFM and the vST predictor can recalibrate morphology features for a target tissue, outperforming both fine-tuning and naive multi-tissue training.  
  **delta from paper**: STP-BENCH treats tissue as a domain shift to be measured; this idea treats it as a modality to be adapted, adding a learnable tissue-conditioned adapter.  
  **initial method**: For each target tissue (e.g., BRCA), add a small MLP adapter (2 layers, 128 dim) to UNIv2 embeddings, conditioned on tissue ID embedding; train only adapter + predictor head on target tissue data.  
  **validation**: Compare adapter vs full fine-tuning vs zero-shot on STP-BENCH-EXTERNAL cross-tissue tasks (Fig.5b); metrics: PCC, ARI, cell abundance PCC.  
  **failure modes**: Adapter overfits to small tissue cohorts; fails when tissue ID embedding lacks discriminative power.  
  **innovation status**: unverified  

- **name**: Gene-Set Guided Contrastive Learning for vST  
  **originating limitation/observation**: Bi-modal retrieval models (BLEEP, STco) use CLIP-style contrastive loss on spot-level vectors, but gene-set analysis shows functional programs (e.g., T Cell Activation) are recoverable (Fig.3e), suggesting loss should operate at functional level.  
  **core hypothesis**: Replacing spot-level contrastive loss with gene-set-level contrastive loss will improve recovery of biologically coherent pathways, especially for low-expression marker genes.  
  **delta from paper**: STP-BENCH evaluates gene-set recovery post-hoc; this idea integrates gene-set semantics into the training objective itself.  
  **initial method**: For each spot, compute singscore for top K GO terms; use these scores as "functional embeddings"; align H&E patch embeddings with functional embeddings via contrastive loss, alongside original spot-level alignment.  
  **validation**: Train BLEEP variants on STP-BENCH-INTERNAL; evaluate on gene-set PCC (Fig.3c) and marker gene PCC (Fig.2a); ablate functional vs spot-level loss components.  
  **failure modes**: Functional embeddings are noisy for sparse genes; loss conflicts with spot-level alignment, causing optimization instability.  
  **innovation status**: unverified  

- **name**: Spatial Graph Refinement for Spot-Level vST Predictions  
  **originating limitation/observation**: Models like SEPAL use spatial graphs for refinement, but STP-BENCH shows spatial domain identification (SpaGCN) is highly sensitive to data quality (Fig.4c); current graph construction (e.g., hexagonal neighbors) may be too rigid for irregular tissue boundaries.  
  **core hypothesis**: A dynamic, morphology-aware spatial graph—where edges are learned from H&E patches rather than fixed geometry—will yield more robust spatial refinement, especially on low-quality Visium data.  
  **delta from paper**: STP-BENCH uses fixed neighbor graphs (e.g., "six neighbors for hexagonal Visium geometry" [Paper] [Paper: PDF p. 25]); this replaces it with a learnable, vision-conditioned graph.  
  **initial method**: Replace SEPAL's fixed neighbor graph with a GNN that takes UNIv2 embeddings of center + candidate neighbor spots as input, and predicts edge weights via MLP; use top-k weighted edges for graph convolution.  
  **validation**: Implement in SEPAL; compare on STP-BENCH-INTERNAL Visium cohorts (e.g., NCCHE-LUAD-Visium) for PCC and ARI (Fig.4c); visualize learned adjacency vs ground-truth tissue boundaries.  
  **failure modes**: Graph learning adds significant compute; may overfit to artifact-prone regions.  
  **innovation status**: unverified