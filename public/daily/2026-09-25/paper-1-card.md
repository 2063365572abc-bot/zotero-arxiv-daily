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
| Core task | Virtual spatial transcriptomics (virtual ST) prediction from H&E patches | [Paper] [Paper: PDF p. 2] |
| Benchmark name | STP-BENCH (comprising STP-BENCH-INTERNAL and STP-BENCH-EXTERNAL) | [Paper] [Paper: PDF p. 4] |
| Scale | 609,024 spots (INTERNAL), 185,831 spots (EXTERNAL), 6 cancer types, 2 platforms (Visium/Xenium) | [Paper] [Paper: PDF p. 4], [Figure 1b] |
| Models evaluated | 21 models: 14 regression-based, 4 bi-modal retrieval-based, 3 generative-based | [Paper] [Paper: PDF p. 6], [Figure 1c] |
| Key encoder | UNIv2 pathology foundation model (PFM), used as unified patch encoder where architecturally compatible | [Paper] [Paper: PDF p. 7], [Figure 2a] |
| Primary metric | Pearson Correlation Coefficient (PCC) per gene, averaged across spots → sections → folds | [Paper] [Paper: PDF p. 31], Equation 1 |
| Public release | Code and preprocessed data at https://github.com/NEXGEM/STP-Bench and Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结

STP-BENCH 是首个大规模、多平台、标准化的 virtual ST 系统性评测基准，通过统一使用病理基础模型（UNIv2）作为图像编码器，在 6 癌种 × 2 平台 × 21 模型上开展公平比较；它揭示了当前多数模型未超越线性探针基线、基因可预测性存在普适性天花板、且模型架构优势仅在特定生物学通路（如基质/免疫相关多尺度基因）中显现；该基准同时首次系统评估了虚拟 ST 在细胞类型去卷积与空间结构识别等下游任务中的生物学效用，并指出数据质量（如 Xenium 高计数）比模型复杂度更决定最终性能边界。[Paper] [Paper: PDF p. 2–3, 8–10, 14, 19]

## 03 研究问题

论文直面 virtual ST 领域长期存在的**评估不可靠性问题**：现有研究因依赖小规模异构数据集、不一致训练/推理流程、未解耦图像编码器与模型架构、且缺乏对生物学可解释性与鲁棒性的检验，导致模型性能排名失真、进步难以量化。[Paper] [Paper: PDF p. 2–3]  
→ 作者提出核心问题：**如何构建一个可控、可复现、多层次的 benchmark，以分离并量化图像编码器、模型架构、数据质量与生物学粒度对 virtual ST 性能的真实贡献？**  
→ 这一问题源于对领域发展瓶颈的诊断：若无法区分“是模型更好，还是编码器更强”，则方法学创新将陷入虚假竞争。[Paper] [Paper: PDF p. 3]  
→ 解决路径不是设计新模型，而是重构评估范式——通过统一编码器、扩大数据规模、分层验证指标，使 benchmark 成为可信赖的“标尺”。[Paper] [Paper: PDF p. 4]

## 04 研究背景与发展路径

virtual ST 的演进呈现三条技术主线：**回归式**（ST-Net → TRIPLEX/DeepSpot）、**双模态对齐式**（BLEEP/STco/mclSTExp）、**生成式**（STFlow/Stem），均受益于病理基础模型（PFM）的兴起。[Paper] [Paper: PDF p. 3]  
但评估实践严重滞后：Wang et al. 50 保留各模型原生编码器，混淆架构与编码器效应；HEST-1K 51 虽有大数据量，却仅用简单回归测试 PFM 嵌入，未评测完整模型族。[Paper] [Paper: PDF p. 3–4]  
→ STP-BENCH 的发展路径是**反向工程式补缺**：它不延续单点突破逻辑，而是识别出四大断裂带——数据规模不足、编码器未统一、评估粒度单一（仅基因平均）、鲁棒性未检验——并逐一缝合：用 600k+ spot 构建 INTERNAL，强制 UNIv2 替换兼容模型编码器，新增基因/基因集/细胞类型/空间域四层评估，引入跨机构/组织/平台三类泛化测试。[Paper] [Paper: PDF p. 4–5, 14–17]

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平** | 模型排名随编码器切换剧烈波动（如 CFANet 从第16跃至第6） | 各模型原生编码器预训练域、规模、范式差异巨大，性能增益常源于编码器而非架构 | [Paper] [Paper: PDF p. 9], [Figure 2b] |
| **生物学效用黑箱** | 高 PCC 不保证下游任务可用（如低计数 Visium 数据上 PCC≈0.2，但 Cell2location 相关性更低） | 虚拟 ST 的价值需在细胞组成、空间结构等生物学粒度上验证，而非仅 spot-level 数值拟合 | [Paper] [Paper: PDF p. 14], [Figure 4a–c] |
| **数据质量主导性能上限** | Xenium 数据（高计数）上 marker gene PCC 达 0.579，Visium（低计数）仅 0.191 | 基因表达检测的信噪比构成硬性瓶颈，模型无法补偿原始数据稀疏性 | [Paper] [Paper: PDF p. 10], [Figure 2c–d] |
| **泛化能力被高估** | 跨组织（Cross-Tissue）泛化 gap 达 −0.2~−0.35，远超跨机构（−0.05~−0.10） | 形态-表达映射高度组织特异性，简单跨癌种数据聚合引发负迁移 | [Paper] [Paper: PDF p. 17], [Figure 5b] |

## 06 核心思想

论文的核心思想是**将 benchmark 本身升维为一种方法论基础设施**：它不满足于报告“谁更好”，而致力于回答“**在什么条件下、对哪些生物学对象、经受何种扰动时，谁更好**”。[Paper] [Paper: PDF p. 4–5]  
→ 这一思想体现为三个解耦原则：**（1）编码器-架构解耦**：用 UNIv2 统一视觉前端，使模型比较聚焦于后端推理机制；[Paper] [Paper: PDF p. 7]  
→ **（2）数值-生物学解耦**：PCC 是入口，但必须延伸至基因集（singscore）、细胞丰度（Cell2location）、空间域（SpaGCN）三层生物学验证；[Paper] [Paper: PDF p. 11, 14]  
→ **（3）性能-鲁棒性解耦**：内部 PCC 高 ≠ 外部可靠，故设计 Cross-Institution/Tissue/Platform 三轴压力测试。[Paper] [Paper: PDF p. 17]  
→ 最终目标是让 STP-BENCH 成为 virtual ST 的“ICU监护仪”——不仅显示生命体征（PCC），更监测器官功能（下游任务）与应激反应（泛化性）。[Paper] [Paper: PDF p. 18–19]

## 07 方法总览

STP-BENCH 的方法框架是**三维正交控制实验设计**：  
- **维度一：数据控制** —— 构建 STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与 STP-BENCH-EXTERNAL（186k spots, 严格隔离）双数据集，确保统计效力与泛化检验独立性；[Paper] [Paper: PDF p. 4–5]  
- **维度二：模型控制** —— 对 21 个模型进行统一重实现，强制 UNIv2 编码器（除非架构不兼容，如 M2OST/M2ORT），所有模型输出加 Softplus 保证非负；[Paper] [Paper: PDF p. 22–29]  
- **维度三：评估控制** —— 实施四层评估：（i）spot-level：PCC/MAE/SSIM；（ii）gene-level：HMHVG vs marker genes 分析；（iii）gene-set-level：singscore 通路活性；（iv）biological-granularity：Cell2location（细胞丰度）、SpaGCN（空间域）；[Paper] [Paper: PDF p. 7, 11, 14, 34–36]  
→ 整个 pipeline 以 PyTorch 实现，固定随机种子，患者级交叉验证防泄漏，所有代码与预处理数据开源。[Paper] [Paper: PDF p. 30, 37]

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **UNIv2 Patch Encoder** | Extracts 1024-dim histology embeddings from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability; UNIv2 outperforms ResNet50/CTransPath on HMHVG+marker genes | Input: H&E patch; Output: PFM embedding | [Paper] [Paper: PDF p. 7–10], [Figure 2e], [Online Methods p. 23] | Severe ranking distortion (e.g., CFANet drops from 6th to 16th); most models fall below linear probe baseline [Figure 2b] |
| **TRIPLEX / DeepSpot Architecture** | Integrates local (target spot), neighborhood (surrounding spots), and global (whole-slide) morphological context via cross-attention (TRIPLEX) or deep-set aggregation (DeepSpot) | To capture long-range dependencies essential for stromal/immune gene prediction, which local patches alone cannot resolve | Input: Multi-scale PFM embeddings; Output: Gene expression vector | [Paper] [Paper: PDF p. 11, 19], [Online Methods p. 25–26], [Figure 3b] | Loss of top performance on stromal (COL1A1), immune (LAG3), and epithelial (AZGP1) genes; gene set scores for T Cell Activation drop significantly [Figure 3e] |
| **singscore Gene Set Scoring** | Computes per-spot gene set activity by ranking genes within spot, then averaging ranks of member genes | To bridge gene-level accuracy to functional pathway-level biological interpretability, avoiding aggregation bias of mean expression | Input: Predicted/ground-truth expression matrix; Output: Spot-by-gene-set score matrix | [Paper] [Paper: PDF p. 13], [Online Methods p. 35], [Figure 3c–e] | Inability to detect that TRIPLEX/DeepSpot preserve immune-related pathways better than others; gene set PCC would collapse to single scalar [Figure 3d] |
| **Cell2location Deconvolution** | Estimates spatial cell-type abundance from virtual ST profiles using scRNA-seq reference signatures | To validate whether predicted expression retains sufficient biological structure for clinical-grade downstream analysis | Input: Virtual ST expression (expm1-transformed); Output: Per-spot cell-type abundance matrix | [Paper] [Paper: PDF p. 14], [Online Methods p. 35], [Figure 4a] | Failure to reveal that high-PCC models (TRIPLEX/DeepSpot) also yield highest correlation with ground-truth T-cell/malignant epithelial abundances [Figure 4a] |
| **SpaGCN Spatial Domain Identification** | Clusters spots into spatial domains using gene expression + coordinates, then computes Adjusted Rand Index (ARI) against ground-truth annotations | To test if virtual ST preserves tissue-level architectural organization, beyond single-cell or spot-level signals | Input: Virtual ST expression; Output: Domain labels → ARI vs reference | [Paper] [Paper: PDF p. 14], [Online Methods p. 36], [Figure 4b–c] | Inability to show TRIPLEX achieves highest ARI on NCCHE-LUAD-Xenium (0.643), proving its superiority extends to macro-tissue patterning [Figure 4c] |

## 09 关键公式与符号

- **Equation 1**（Pearson Correlation Coefficient, PCC）：  
  $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}} $  
  [Paper] [Paper: PDF p. 31]  
  - 符号：$\hat{y}_{i,g}$ = spot $i$ gene $g$ 预测值（log1p-normalized）；$y_{i,g}$ = ground-truth；$\bar{\hat{y}}_g$, $\bar{y}_g$ = 各自均值；$N$ = spots in section.  
- **Equation 2**（Mean Absolute Error, MAE）：  
  $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}| $  
  [Paper] [Paper: PDF p. 32]  
  - 符号：同上，但操作于 log1p-transformed space.  
- **无显式公式**：论文未给出 singscore、Cell2location、SpaGCN 或 SSIM 的推导公式，仅引用其标准实现（singscore 84, TorchMetrics, skimage.metrics）。关键指标符号：PCC（Pearson Correlation Coefficient）、MAE（Mean Absolute Error）、SSIM（Structural Similarity Index Measure）、ARI（Adjusted Rand Index）、HMHVG（high-mean highly-variable genes）、TME（tumor microenvironment）。[Paper] [Paper: PDF p. 31–32, 34–36]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|-------------------------------|--------|
| **UNIv2 vs Native Encoders** | Unified encoding changes model rankings | Compare CFANet/HisToGene with native (ResNet50/scratch) vs UNIv2 encoder on HMHVG | CFANet jumps from 16th→6th; HisToGene gains 0.12 PCC | Encoder choice dominates architectural gain; prior comparisons are unfair | UNIv2 is universally optimal (not tested on all PFMs simultaneously) | [Paper] [Paper: PDF p. 9], [Figure 2b] |
| **Xenium vs Visium Prediction** | Data quality (transcript count) limits performance ceiling | Evaluate same models on NCCHE-LUAD-Xenium (mean counts=52.1) vs NCCHE-LUAD-Visium (mean counts=9.2) for marker genes | Marker gene PCC: 0.579 (Xenium) vs 0.191 (Visium) | Low-count Visium data imposes hard floor on predictability; model design cannot overcome it | All genes are equally limited by count (but HMHVG less so: 0.586 vs 0.571) | [Paper] [Paper: PDF p. 10], [Figure 2c–d] |
| **Gene-wise Stratification** | Genes have intrinsic predictability independent of model | Rank 200 HMHVGs by mean PCC across 20 models → split into 5 quantiles → compute PCC per bin per model | Rankings stable across bins; TRIPLEX/DeepSpot gain >0.1 only in top bins | Universal gene-level ceiling exists; architecture shifts boundary but doesn’t eliminate it | Any model can be tuned to beat ceiling (no evidence) | [Paper] [Paper: PDF p. 9], [Extended Data Fig. 1] |
| **Cell2location on Virtual ST** | Virtual ST preserves cell-type spatial organization | Apply Cell2location to TRIPLEX/DeepSpot predictions vs ground-truth on NCCHE-LUAD-Xenium | TRIPLEX achieves highest avg PCC (0.643) for malignant epithelial & T cells | Top gene-level performers retain biological fidelity at cellular granularity | Rare populations (plasma cells) are recoverable (they show low PCC) | [Paper] [Paper: PDF p. 14], [Figure 4a] |
| **Cross-Tissue Generalization** | Morphology-expression mapping is tissue-specific | Train on BRCA-Visium, test on LUAD-Visium; measure PCC gap | Gap = −0.20 to −0.35, worse than cross-institution (−0.05 to −0.10) | Simple multi-tissue training harms performance; tissue-aware strategies needed | Cross-tissue failure is due to encoder weakness (but Virchow2 shows similar gap) | [Paper] [Paper: PDF p. 17], [Figure 5b] |

## 11 对结论的正确理解

- **“多数模型未超越线性探针”** 指在 UNIv2 统一编码下，14/21 模型的 HMHVG PCC 低于 UNIv2+LinearProb 基线（0.376），**并非否定模型价值**，而是说明：当编码器足够强时，复杂架构的边际增益有限，尤其对易预测基因；其真实价值体现在难预测基因（如 LAG3）和下游任务（Cell2location ARI）。[Paper] [Paper: PDF p. 9, 14]  
- **“基因可预测性具普适性”** 指 COL1A1 在所有模型上 PCC 均 >0.5，而 CD274 均 <0.2，**不意味形态-表达关系完全由基因决定**，而是反映当前 H&E 图像信息对特定生物学过程（如纤维化梯度）的承载能力上限。[Paper] [Paper: PDF p. 11], [Figure 3a]  
- **“Xenium 数据性能更高”** 是因更高分子计数提升信噪比，**非 Xenium 技术本身优越**；论文未声称 Xenium 应取代 Visium，而是强调 benchmark 必须涵盖多平台以检验泛化性。[Paper] [Paper: PDF p. 10, 14]  
- **“跨组织泛化差”** 指模型在 BRCA 训练后直接用于 LUAD 测试时性能骤降，**不否定迁移学习潜力**；作者明确建议未来工作采用 domain-adaptive 策略。[Paper] [Paper: PDF p. 19]  
- **“负迁移现象”** 指 BRCA+LUAD 联合训练反而降低 BRCA 测试性能，**不证明多癌种数据无用**，而是警示简单拼接有害，需更智能的数据融合机制。[Paper] [Paper: PDF p. 18], [Figure 5d]

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 ST platforms; generalizability to rare cancers or emerging platforms (e.g., Stereo-seq) untested | Extend benchmark to additional tumor types, tissue contexts, and sequencing platforms | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focused on HMHVGs (200 genes) and 16 TME markers; lowly expressed or functionally diverse genes not systematically investigated | Systematic investigation of low-expression and functionally diverse gene categories | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluation performed at Visium/Xenium pseudo-spot level (multi-cell aggregates); single-cell ST virtual prediction not benchmarked | Extend principles to single-cell resolution as scST datasets and models mature | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|--------------------------|-------------------------------------------|----------------|----------------|-------|
| **TRIPLEX/DeepSpot dominance may stem from data leakage in multi-scale inputs** | TRIPLEX uses neighbor spot embeddings; DeepSpot uses sub-spot grids — both require spatial proximity info. If neighbor/sub-spot patches overlap with target patch (e.g., due to 224×224 crop at 0.5µm/pixel), model may exploit trivial pixel correlations rather than true morphology | Overestimates architectural advantage; undermines claim of "multi-scale reasoning" | Re-run TRIPLEX/DeepSpot with non-overlapping neighbor patches (e.g., 100µm offset) and compare PCC drop on stromal genes | [Online Methods p. 25–26] describes neighbor patch extraction but not spatial offset guarantee |
| **singscore-based gene set evaluation ignores gene-gene correlations** | singscore ranks genes per spot then averages ranks; it discards co-expression structure critical for pathway activity (e.g., correlated upregulation of COL1A1/COL3A1) | May underestimate preservation of coordinated biological programs; TRIPLEX's stromal advantage could be amplified by correlation-aware metrics | Replace singscore with GSVA or PLAGE and recompute gene set PCC; check if TRIPLEX/DeepSpot gap widens | [Paper] [Paper: PDF p. 13] cites singscore for efficiency but acknowledges alternatives exist |
| **Cross-platform (Visium→Xenium) "improvement" likely confounded by higher Xenium counts** | Figure 5b right panel shows some models (e.g., TRIPLEX) with positive gap; but Xenium has ~5× higher mean counts (52.1 vs 9.2), making prediction easier | Misattributes performance gain to cross-platform robustness rather than data quality boost | Train all models on Visium, test on *downsampled* Xenium (to match Visium count distribution); re-evaluate gap | [Paper] [Paper: PDF p. 10] explicitly links count to performance, but cross-platform test uses full Xenium |
| **Cell2location validation uses expm1 + clipping, risking information loss** | Converting log1p-predictions back to integers via expm1+clip discards fractional counts and negative values (though Softplus ensures non-negativity) | May degrade deconvolution accuracy, especially for low-abundance cell types; masks true predictive fidelity | Test Cell2location on raw log1p predictions (with appropriate preprocessing) or use log-normalized input mode if supported | [Online Methods p. 35] mandates expm1+clip, citing Cell2location requirements, but doesn't validate impact |

## 14 学到的知识

- **评估即设计**：benchmark 不是模型性能的被动记录者，而是主动定义领域进步标准的“元工具”；STP-BENCH 证明，强制统一编码器、分层验证、多轴泛化测试，能颠覆既往认知（如“CFANet 架构弱”实为“其编码器弱”）。[Paper] [Paper: PDF p. 9, 18]  
- **生物学粒度决定评估深度**：spot-level PCC 是必要但不充分条件；只有当虚拟 ST 能支撑 Cell2location（细胞丰度）和 SpaGCN（空间域）等下游任务时，才具备临床转化潜力；且这些任务性能与 PCC 高度协同（Spearman ρ=0.902），证实了评估链的内在一致性。[Paper] [Paper: PDF p. 13–14]  
- **数据质量是隐性天花板**：Xenium 的高计数使 marker gene PCC 从 0.191（Visium）跃至 0.579，证明**算法改进无法替代实验技术升级**；benchmark 必须包含多平台数据以暴露此瓶颈。[Paper] [Paper: PDF p. 10]  
- **基因可预测性具有“光谱性”**：并非所有基因都同等可预测；TRIPLEX/DeepSpot 的优势集中在 stromal (COL1A1), immune (LAG3), epithelial (AZGP1) 基因，揭示了多尺度架构对长程组织模式（如纤维化梯度、淋巴聚集）的特异性解码能力。[Paper] [Paper: PDF p. 11, 19], [Figure 3b]  
- **负迁移是多组织建模的警钟**：简单合并 BRCA/LUAD/PRAD 数据导致性能下降，表明 morphology-expression 映射高度组织特异；未来工作需 domain-adaptive 或 tissue-aware learning，而非粗暴数据堆砌。[Paper] [Paper: PDF p. 18–19], [Figure 5d]

## 15 与既有知识的连接

- **候选连接/方法论连接**：STP-BENCH 的“统一编码器+分层验证”范式，与 vision-language benchmarking（如 GLUE, VQA-v2）中解耦 backbone 与 head 的思想同源，但首次将其系统应用于 spatial omics。[Paper] [Paper: PDF p. 4, 18]  
- **候选连接/方法论连接**：其 gene-wise predictability analysis（Figure 3a）呼应了 single-cell foundation model 研究中“gene importance scoring”概念（如 scGPT），但 STP-BENCH 证明该重要性在 virtual ST 中由形态可读性（morphological informativeness）而非转录调控强度决定。[Paper] [Paper: PDF p. 11]  
- **候选连接/方法论连接**：Cell2location 和 SpaGCN 的下游验证，将 virtual ST 与 spatial transcriptomics 生态中的标准分析工具链（如 Squidpy, Scanpy）显式对接，为用户将 virtual ST 集成到现有 single-cell/spatial pipelines 提供了可复现接口。[Paper] [Paper: PDF p. 14, 35–36]  
- **弱连接/方法论连接**：虽涉及 graph neural networks（SEPAL, EGGN），但 STP-BENCH 未评估 GNN 架构变体（如 GAT vs GCN）或图构建策略（k-NN vs spatial radius）的影响，仅将其作为模型组件之一；用户若专注 GNN 设计，需自行扩展 benchmark。[Paper] [Paper: PDF p. 24–25]  
- **弱连接/方法论连接**：perturbation prediction 与 cross-modal alignment 未被直接探索；STP-BENCH 聚焦于 steady-state prediction，未模拟基因敲除或药物扰动下的虚拟 ST 变化，亦未对齐 H&E 与 multi-omics（如 proteomics）模态。[Paper] [Paper: PDF p. 2–3]

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Morphology-Guided Gene Prioritization for Virtual ST  
  **originating limitation/observation**: Gene-wise analysis reveals universal predictability ceiling, but TRIPLEX/DeepSpot gain >0.1 only on specific genes (e.g., COL1A1, LAG3); current HMHVG/marker selection is heuristic, not morphology-aware. [Paper] [Paper: PDF p. 11, 19], [Figure 3b]  
  **core hypothesis**: Genes whose expression correlates with long-range morphological gradients (e.g., fibrosis, immune infiltration) are intrinsically more predictable; a morphology-guided gene selection policy will outperform HMHVG/marker panels.  
  **delta from paper**: STP-BENCH uses fixed gene sets; this idea proposes *learnable, morphology-conditioned gene prioritization* during training/inference.  
  **initial method**: Train a lightweight ViT to predict gene-wise PCC from H&E patches; use its attention maps to identify morphological regions driving prediction; select top-K genes whose expression gradients align with these regions.  
  **validation**: Compare PCC on STP-BENCH-INTERNAL using morphology-prioritized vs HMHVG gene sets; test generalization to STP-BENCH-EXTERNAL.  
  **failure modes**: Attention maps may not localize biologically meaningful regions; gradient alignment may be noisy.  
  **innovation status**: unverified  

- **name**: Tissue-Aware Adapter for Cross-Tissue Virtual ST  
  **originating limitation/observation**: Cross-tissue generalization gap is severe (−0.2~−0.35); simple data mixing causes negative transfer, suggesting tissue-specific morphology-expression mappings. [Paper] [Paper: PDF p. 17–19], [Figure 5b,d]  
  **core hypothesis**: A lightweight, tissue-type-specific adapter module inserted between PFM encoder and ST predictor can absorb tissue-specific biases without full model retraining.  
  **delta from paper**: STP-BENCH treats tissue as a domain shift to be measured; this idea treats it as a *structured bias to be corrected*.  
  **initial method**: For each tissue type (BRCA, LUAD, etc.), train a small adapter (e.g., 2-layer MLP) that modulates UNIv2 embeddings; freeze PFM and predictor, only update adapters per tissue.  
  **validation**: Train adapters on BRCA, test zero-shot on LUAD; compare PCC gap reduction vs fine-tuning full model.  
  **failure modes**: Adapter may overfit to small tissue cohorts; may not generalize to unseen tissues.  
  **innovation status**: unverified  

- **name**: SSIM-Guided Diffusion for Spatial Coherence  
  **originating limitation/observation**: Generative models (STFlow/Stem) underperform regression models on PCC, but SSIM results (Extended Data Fig. 3) suggest they may better preserve spatial structure; current evaluation weights PCC > SSIM. [Paper] [Paper: PDF p. 11]  
  **core hypothesis**: Optimizing diffusion models explicitly for SSIM (not just MSE) will improve spatial coherence of predicted expression landscapes, benefiting downstream tasks like SpaGCN.  
  **delta from paper**: STP-BENCH uses SSIM as secondary metric; this idea proposes *SSIM as primary optimization objective* in flow-matching/diffusion.  
  **initial method**: Modify STFlow’s denoising objective to include SSIM loss term (λ·SSIM + (1−λ)·MSE); tune λ on STP-BENCH-INTERNAL.  
  **validation**: Compare SpaGCN ARI on STP-BENCH-EXTERNAL; check if SSIM-optimized STFlow closes gap with TRIPLEX/DeepSpot.  
  **failure modes**: SSIM optimization may degrade spot-level PCC; may increase training instability.  
  **innovation status**: unverified