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
| Code URL | https://github.com/NEXGEM/STP-Bench | [Paper] [Paper: PDF p. 2] |
| Data URL | Hugging Face: https://huggingface.co/datasets/nexgem/STP-Bench | [Paper] [Paper: PDF p. 37] |
| Core contribution | First large-scale, multi-platform, standardized benchmark for virtual ST models with unified PFM encoding, gene-level interpretability, and downstream biological utility evaluation | [Paper] [Paper: PDF p. 2–4] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium/Xenium); STP-BENCH-EXTERNAL (185,831 spots, 6 cancer types) | [Paper] [Paper: PDF p. 4–5], [Figure 1b] |
| Evaluated models | 21 models across regression (n=14), bi-modal retrieval (n=4), generative (n=3) families | [Paper] [Paper: PDF p. 6], [Figure 1c] |
| Primary metric | Pearson Correlation Coefficient (PCC) per gene, averaged across spots → sections → folds | [Paper] [Paper: PDF p. 31], [Equation 1] |

## 02 一句话总结  
该论文构建了STP-BENCH——首个面向虚拟空间转录组学（virtual ST）的统一、大规模、多平台系统性基准，覆盖Visium与Xenium两种主流ST技术平台及六种癌症类型；其核心创新在于强制统一病理基础模型（PFM）作为图像编码器，从而解耦模型架构与图像表征能力，揭示多数现有模型未超越线性探针基线的本质问题；同时首次系统评估基因级可预测性、通路级恢复能力、细胞类型去卷积与空间结构识别等下游生物学效用，并量化跨机构/组织/平台泛化鲁棒性。该工作不提出新模型，而是为single-cell foundation models、spatial transcriptomics和multi-omics建模提供可复现、可归因、可迁移的评估基础设施。

## 03 研究问题  
虚拟ST领域缺乏公平、可控、可复现的基准：既有评估依赖小规模异质数据集、不一致训练/推理流程、未标准化图像编码器，导致模型性能差异无法归因于架构本身；更关键的是，评估长期局限于整体基因相关性，忽视哪些基因/通路真正可从形态学推断、预测结果能否支撑下游生物学分析（如细胞组成、空间域识别）、以及模型在真实分布偏移下的可靠性。因此，研究问题聚焦于：**如何构建一个能分离“图像编码能力”与“模型架构能力”的标准化基准，并系统刻画虚拟ST在分子、细胞、组织多尺度上的可解释性边界与泛化极限？**

## 04 研究背景与发展路径  
虚拟ST起源于ST实验成本高昂的现实约束，早期以ST-Net为代表采用CNN回归框架；随后演进为三类范式：(1) 回归式（引入邻域上下文、多尺度、示例集、文本先验）；(2) 双模态对齐式（CLIP范式，学习形态-表达联合嵌入空间）；(3) 生成式（扩散/流匹配建模联合分布）。所有范式均日益依赖病理基础模型（PFM）提取形态特征，但此前评估中各模型沿用原生编码器（ResNet/ImageNet预训练/自建CNN），造成架构贡献与编码器贡献严重混淆。Wang et al. 2024仅用原生编码器评估两套Visium数据，而HEST-1K虽规模大却仅用PFM嵌入+简单回归器测试，未覆盖完整模型谱系。STP-BENCH正是在此断裂处切入：它不延续单点改进，而是重构评估范式——将PFM作为“公共接口”，使21种模型在相同形态语义输入下竞争，从而暴露架构的真实增量价值。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平性** | 模型排名随编码器切换剧烈变动（如CFANet从第16跃至第6）；多数模型未超UNIv2线性探针基线 | 原有评估混杂了图像编码器差异（预训练域/规模/范式）与模型架构差异，导致性能提升归属错误 | [Paper] [Paper: PDF p. 9], [Figure 2b], [Paper] [Paper: PDF p. 18] |
| **生物学效用黑箱** | 预测结果是否保留细胞类型丰度、空间结构等高阶生物信号未知 | 仅报告基因级PCC无法验证下游任务可行性；既往工作未在统一框架下测试Cell2location/SpaGCN等工具 | [Paper] [Paper: PDF p. 14], [Figure 4a–c], [Paper] [Paper: PDF p. 19] |
| **基因级可预测性模糊** | HMHVG与TME标记基因预测性能差距达2×（PCC≈0.4 vs ≈0.2），但成因不明 | 数据稀疏性主导（Xenium高计数时两者PCC均≈0.58）而非形态学不可解；低表达基因信噪比低，放大预测误差 | [Paper] [Paper: PDF p. 9–10], [Figure 2c–d], [Paper] [Paper: PDF p. 19] |
| **泛化机制不透明** | 跨组织泛化性能下降远超跨机构（gap −0.35 vs −0.1），但原因未解析 | 组织特异性形态-表达映射强于技术批次效应；简单多癌种数据融合反而引发负迁移 | [Paper] [Paper: PDF p. 17], [Figure 5b], [Paper] [Paper: PDF p. 19] |
| **平台依赖性未量化** | Xenium与Visium数据质量差异对预测上限的影响无定量证据 | Xenium更高灵敏度与转录本计数直接提升所有模型PCC，且下游任务性能同步提升，证明数据质量是共享瓶颈 | [Paper] [Paper: PDF p. 10], [Figure 2c–d], [Paper] [Paper: PDF p. 14], [Paper] [Paper: PDF p. 19] |

## 06 核心思想  
论文的核心思想是：**虚拟ST的性能天花板由“形态学信息含量”与“数据质量”共同决定，而非单纯由模型复杂度驱动；因此，评估必须解耦编码器与架构、穿透基因级可预测性、贯通下游生物学效用、并锚定真实世界分布偏移场景。** 这一思想体现为三大设计原则：(1) **强制统一PFM接口**——将UNIv2作为所有兼容模型的默认编码器，使架构比较在同一起跑线上；(2) **多粒度可解释性评估**——从单基因PCC热图→通路singscore→Cell2location丰度→SpaGCN空间域，形成证据链；(3) **鲁棒性压力测试**——定义Cross-Institution/Cross-Tissue/Cross-Platform三类泛化场景，量化gap并检验rank preservation。最终结论是：TRIPLEX/DeepSpot等多尺度架构的价值不在“绝对精度”，而在对stromal/immune等长程依赖基因的边际增益，这恰是single-cell foundation models需建模的关键跨尺度关联。

## 07 方法总览  
STP-BENCH方法论是“评估即实验设计”：首先构建STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与STP-BENCH-EXTERNAL（186k spots, 6 cancers）双轨数据集，确保统计效力与泛化检验分离；其次对21个模型实施统一重实现，强制UNIv2编码（除架构不兼容者如M2OST/M2ORT）；接着执行三级评估：(1) **基础性能层**——HMHVG与16个TME标记基因的PCC/MAE/SSIM；(2) **生物学效用层**——Cell2location细胞丰度相关性、SpaGCN空间域ARI；(3) **鲁棒性层**——三类跨域泛化gap与data scaling（intra-/inter-cohort）分析。所有评估均基于spot-level配对（H&E patch ↔ ST spot），使用log1p归一化表达与标准增强流水线，确保可复现性。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **Unified PFM Encoder (UNIv2)** | Standardize morphological feature extraction across all compatible models | To isolate architectural contribution by eliminating encoder variability as confounder | Input: 224×224 H&E patch; Output: d-dim embedding vector | [Paper] [Paper: PDF p. 7–9], [Figure 2a,b,e], [Paper] [Paper: PDF p. 18] | Model rankings collapse (e.g., CFANet drops from 6th to 16th); most models fall below linear probe baseline [Paper] [Paper: PDF p. 9] |
| **Gene-level Stratification Pipeline** | Partition genes into predictability bins (Very Low to Very High) based on mean PCC across models | To test whether gene-level predictability is intrinsic (morphology-driven) rather than model-specific | Input: Gene-wise PCC matrix (genes × models); Output: 5 quantile bins | [Paper] [Paper: PDF p. 9], [Extended Data Fig. 1], [Figure 3a] | Loss of insight into universal predictability ceiling; inability to identify architecture-specific gains (e.g., TRIPLEX’s stromal gene advantage) [Paper] [Paper: PDF p. 11] |
| **Downstream Biological Utility Layer** | Apply Cell2location (cell abundance) and SpaGCN (spatial domains) to predicted expression matrices | To validate whether virtual ST preserves biologically meaningful structure beyond spot-level correlation | Input: Predicted spot×gene matrix; Output: Per-cell-type PCC (Cell2location), ARI (SpaGCN) | [Paper] [Paper: PDF p. 14–15], [Figure 4a–c], [Paper] [Paper: PDF p. 19] | Downstream performance decouples from gene-level PCC (e.g., STFlow low PCC but usable for deconvolution? Not assessed); no validation of clinical utility [Paper] [Paper: PDF p. 14] |
| **Cross-Domain Generalization Framework** | Define Cross-Institution (same cancer, different sites), Cross-Tissue (different cancers), Cross-Platform (Visium→Xenium) transfer tasks | To quantify real-world deployment reliability under technical/biological/platform shifts | Input: Model trained on INTERNAL; Output: PCC gap (EXTERNAL − INTERNAL) & Spearman ρ of rank preservation | [Paper] [Paper: PDF p. 17], [Figure 5a–b], [Paper] [Paper: PDF p. 19] | Inability to guide model selection for specific clinical settings (e.g., “use TRIPLEX for cross-tissue”); no mechanistic insight into why tissue shift hurts more than institution shift [Paper] [Paper: PDF p. 17] |
| **Multi-Scale Morphological Reasoning (TRIPLEX/DeepSpot)** | Integrate local patch + neighboring spots + whole-slide context (TRIPLEX) or spot/sub-spot/neighbor features (DeepSpot) | To capture long-range morphological dependencies (e.g., fibrosis gradients, immune fronts) invisible to local patches alone | Input: Local image embedding + neighbor embeddings + global slide embedding (TRIPLEX); Output: Gene expression vector | [Paper] [Paper: PDF p. 11, 19], [Figure 3b], [Paper: Online Methods p. 25–26] | Loss of marginal gain on stromal/immune genes (e.g., COL1A1, LAG3); gene set scores for T Cell Activation drop significantly [Paper] [Paper: PDF p. 11, 13] |

## 09 关键公式与符号  
论文未提出新公式，但明确定义并使用三个核心评估指标：  
- **Pearson Correlation Coefficient (PCC)**: $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}} $ [Equation 1, Paper: PDF p. 31] —— 主要指标，计算每个基因 $g$ 在切片 $s$ 上预测 $\hat{y}$ 与真值 $y$ 的线性相关性。  
- **Mean Absolute Error (MAE)**: $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}| $ [Equation 2, Paper: PDF p. 32] —— 衡量预测误差绝对值，在log1p归一化空间计算。  
- **Structural Similarity Index Measure (SSIM)**: 使用 `skimage.metrics.structural_similarity` 计算，输入为二维空间网格上的预测/真值表达矩阵，考虑局部亮度、对比度与结构 [Paper] [Paper: PDF p. 32]。  
**关键符号**:  
- $ \hat{y}_{i,g}, y_{i,g} $: spot $i$ 上 gene $g$ 的预测/真值表达（log1p归一化）  
- $ \bar{\hat{y}}_g, \bar{y}_g $: gene $g$ 在所有spots上的预测/真值均值  
- HMHVG: High-Mean Highly-Variable Genes (200 genes)  
- TME markers: 16 tumor microenvironment marker genes (e.g., CD3E, ACTA2, PDCD1)  
- PFM: Pathology Foundation Model (e.g., UNIv2, Virchow2)  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|----------------------------------|--------|
| **UNIv2 vs native encoders** | Unified PFM eliminates encoder confounding | Compare CFANet/HisToGene using native encoder vs UNIv2; same training protocol | CFANet jumps from 16th to 6th; HisToGene improves markedly | Encoder choice dominates reported architectural gains; prior comparisons are unfair | UNIv2 is universally optimal (not tested against all PFMs in all scenarios) | [Paper] [Paper: PDF p. 9], [Figure 2b] |
| **HMHVG vs TME marker prediction** | Performance gap stems from data sparsity, not morphology uncoupling | Evaluate both gene sets on NCCHE-LUAD-Xenium (high counts) vs NCCHE-LUAD-Visium (low counts) | Xenium: HMHVG PCC=0.586, Marker PCC=0.579; Visium: HMHVG PCC=0.191, Marker PCC=0.191 | Gap is driven by low transcript counts in Visium, not inherent unpredictability of immune genes | All TME markers are equally predictable if counts are sufficient (not gene-specific analysis) | [Paper] [Paper: PDF p. 10], [Figure 2c–d] |
| **Gene-wise predictability concordance** | Some genes are intrinsically hard/easy across all models | Compute PCC per gene across 20 models; cluster genes by mean PCC | Smooth separation in heatmap; high Spearman correlation of gene ranks across models | Gene-level predictability is governed by morphology-expression coupling strength, not model architecture | This coupling is deterministic (no stochastic modeling of uncertainty assessed) | [Paper] [Paper: PDF p. 11], [Figure 3a], [Extended Data Fig. 1] |
| **Multi-scale models on stromal genes** | TRIPLEX/DeepSpot gain stems from long-range context integration | Identify genes with ΔPCC ≥0.1 over linear probe; manually annotate functional categories | Top gains: COL1A1, SPARC, LAG3 (stromal/immune); all require meso-macro scale patterns | Multi-scale reasoning captures tissue-level organization beyond local patches | This mechanism generalizes to single-cell resolution (not tested) | [Paper] [Paper: PDF p. 11, 13], [Figure 3b], [Paper] [Paper: PDF p. 19] |
| **Cross-tissue generalization** | Biological heterogeneity harms more than technical variation | Train on LUAD, test on BRCA/PRAD; compare gap to cross-institution (same cancer, different sites) | Cross-tissue gap: −0.20 to −0.35; Cross-institution gap: −0.05 to −0.10 | Morphology-to-expression mapping is highly tissue-specific; simple data fusion causes negative transfer | Domain adaptation strategies (e.g., tissue-aware fine-tuning) would resolve this (not implemented/tested) | [Paper] [Paper: PDF p. 17], [Figure 5b], [Paper] [Paper: PDF p. 19] |

## 11 对结论的正确理解  
论文结论必须严格限定于其证据范围：(1) “多数模型未超线性探针”仅指在UNIv2编码下对HMHVG/TME基因的PCC评估，不否定其在其他任务（如分割、分类）或特定基因子集上的优势；(2) “基因可预测性具有一致性”指200个HMHVG+16个marker基因在20个模型间的相对排序稳定，但未涵盖全转录组（尤其低表达/ubiquitous基因）；(3) “TRIPLEX/DeepSpot优势在多尺度”证据仅来自其对stromal/immune基因的ΔPCC增益及下游任务表现，未证明其内部机制（如cross-attention）是唯一有效路径；(4) “Xenium数据质量提升上限”基于其更高平均计数与同步提升的PCC/Cell2location/SpaGCN性能，但未控制其他变量（如RNA integrity、library prep）；(5) “跨组织泛化难”结论基于Visium→Visium转移，未测试Xenium→Xenium或跨平台→跨组织复合场景。所有结论均指向**评估范式革新**，而非否定模型架构价值。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|--------------------------------------|--------|
| **Cancer type & platform scope** | Limited to 6 cancer types and 2 ST platforms (Visium/Xenium) | Extend to additional tumor types, tissue contexts, and emerging sequencing platforms | [Paper] [Paper: PDF p. 20] |
| **Gene panel restriction** | Analyses restricted to HMHVGs (200 genes) and 16 TME markers | Systematic investigation of lowly expressed or functionally diverse genes remains open | [Paper] [Paper: PDF p. 20] |
| **Spot-level granularity** | Evaluation performed at spot-level (aggregated multi-cell signals) | Future benchmarking should extend to single-cell ST datasets and virtual ST models | [Paper] [Paper: PDF p. 20] |
| **Downstream task coverage** | Only Cell2location (deconvolution) and SpaGCN (spatial domains) evaluated | Broader assessment of other tools (e.g., spatial DE, trajectory inference) needed | [Paper] [Paper: PDF p. 14–15] |
| **Zero-shot model comparability** | OmiCLIP/STPath evaluated without fine-tuning, unlike others | Develop unified protocols for fair zero-shot vs fine-tuned comparison | [Paper] [Paper: PDF p. 22], [Online Methods p. 29–30] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| **Linear probe baseline uses UNIv2, but its "simplicity" is misleading** | UNIv2 itself is a massive ViT trained on >1M slides; linear probing leverages immense pre-trained knowledge, not just "simplicity". A true null model might be random projection or shallow CNN. | Overstates the "failure" of complex models; conflates architectural complexity with computational cost/interpretability trade-offs. | Replace UNIv2 linear probe with: (a) ResNet50 linear probe, (b) Random Gaussian projection, (c) Shallow 2-layer MLP on raw pixels. Compare ranking shifts. | [Paper] [Paper: PDF p. 9], [Figure 2a], [Paper] [Paper: PDF p. 10] |
| **Gene set analysis uses singscore on union of HMHVG+markers** | This gene set is biased toward high-expression/high-variability genes; singscore may perform poorly on sparse or low-variance genes common in scRNA-seq. | Underestimates ability of virtual ST to recover subtle regulatory programs; limits relevance to single-cell foundation models targeting rare cell states. | Re-run singscore on full gene universe (where available) or use AUCell; compare with scRNA-seq-derived gene sets (e.g., from PanglaoDB). | [Paper] [Paper: PDF p. 13], [Online Methods p. 35] |
| **Cross-platform transfer (Visium→Xenium) shows "negligible loss"** | This is likely because Xenium's higher sensitivity compensates for domain shift, not because models are platform-agnostic. The reverse (Xenium→Visium) may fail catastrophically. | Misleads about true platform interoperability; critical for users planning multi-platform studies. | Explicitly test Xenium→Visium transfer on same cohorts; measure gap asymmetry and whether fine-tuning on small Xenium→Visium adapter bridges it. | [Paper] [Paper: PDF p. 17], [Figure 5b right], [Paper] [Paper: PDF p. 18] |
| **"Negative transfer" in inter-cohort scaling attributed to tissue heterogeneity** | Could also stem from batch effects (e.g., HEST-PRAD vs WUSTL-BRCA staining protocols) or annotation inconsistencies, not pure biology. | Obscures whether the problem is biological (tissue-specificity) or technical (batch correction failure); impacts design of multi-omics alignment strategies. | Apply ComBat/Harmony to harmonize expression matrices before training; re-run scaling experiments. If negative transfer persists, tissue-specificity is confirmed. | [Paper] [Paper: PDF p. 18], [Figure 5d], [Online Methods p. 21] |
| **Robustness analysis uses Spearman ρ of rank preservation** | High ρ means top models stay top, but says nothing about absolute performance degradation magnitude or which models fail hardest. | Insufficient for clinical deployment where even small PCC drop in key markers (e.g., PD-L1) matters. | Report model-specific gap distributions (Fig. 5b) alongside clinical impact metrics (e.g., % samples with PCC < 0.3 for CD274). | [Paper] [Paper: PDF p. 17], [Figure 5b], [Paper] [Paper: PDF p. 19] |

## 14 学到的知识  
- **评估基础设施优先级高于模型创新**：在数据/标注/协议不统一的领域（如spatial transcriptomics），构建STP-BENCH这类基准比提出单个SOTA模型更具杠杆效应；其代码/数据开源直接加速整个社区进展。  
- **PFM是虚拟ST的“操作系统”**：UNIv2/Virchow2等PFM已将形态表征能力推至瓶颈，后续架构创新必须聚焦于如何**有效利用**这些高质量特征（如TRIPLEX的跨尺度融合），而非重复优化底层编码。  
- **基因级可预测性是硬边界**：200个HMHVG+16个marker的PCC热图显示，约30%基因在所有模型上PCC<0.1，构成形态学信息天花板；这为single-cell foundation models的预训练目标（如masking策略）提供实证约束——应优先学习可预测基因的调控逻辑。  
- **下游效用是终极验证**：Cell2location/SpaGCN性能与基因PCC高度一致（Spearman=0.902），证明spot-level精度是必要条件；但若某模型PCC中等却显著提升特定细胞类型丰度（如Tregs），则提示其捕捉了独特生物学信号。  
- **泛化需分层诊断**：Cross-Institution（技术）gap小，说明模型对染色/scan变异鲁棒；Cross-Tissue（生物）gap大，揭示形态-表达映射的组织特异性本质；这对multi-omics对齐中“跨组织先验”的设计具有直接指导意义。  
- **数据质量是隐性瓶颈**：Xenium与Visium的性能鸿沟贯穿所有层级（基因→通路→细胞→空间），表明提升测序深度/灵敏度可能比模型改进带来更大收益；这为perturbation prediction等任务的数据采集标准提供依据。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：STP-BENCH的“统一编码器+多粒度评估”范式可直接迁移到single-cell foundation models评估——例如，将scFoundation或scGPT的细胞嵌入作为“PFM”，在统一嵌入空间内评估不同下游任务（cell type annotation, trajectory inference, perturbation response）的性能，解耦表征质量与任务头设计。  
- **候选连接/方法论连接**：其gene-wise PCC热图与singscore通路分析，为multi-omics中cross-modal alignment提供了可量化的目标函数——例如，在graph neural networks对齐scRNA-seq与spatial proteomics时，可最大化对齐后嵌入在STP-BENCH基因集上的PCC一致性。  
- **候选连接/方法论连接**：TRIPLEX的“local+neighbor+global”三支路设计，启发了spatial transcriptomics中GNN架构的升级——例如，在cell state representation中，可构建三级图：节点=cell，边=spatial proximity（local）、kNN in expression space（neighbor）、tissue-level region membership（global）。  
- **弱连接/方法论连接**：其跨平台（Visium↔Xenium）泛化分析，与biomedical AI中domain adaptation研究弱连接——但STP-BENCH发现简单数据融合有害，暗示需要更精细的adapter（如LoRA）或tissue-aware contrastive learning，而非传统DA方法。  
- **弱连接/方法论连接**：对低表达基因预测失败的归因（数据稀疏性），与perturbation prediction中“rare cell state response”建模困难形成呼应——二者均指向需提升底层数据质量或开发对稀疏性鲁棒的损失函数（如zero-inflated objectives）。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Morphology-Guided Gene Prioritization for scFoundation Pretraining  
  **originating limitation/observation**: STP-BENCH reveals ~30% of HMHVG+marker genes are intrinsically unpredictable (PCC<0.1) across all models, suggesting their expression is weakly coupled to morphology; conversely, top-predictable genes (e.g., COL1A1, LAG3) reflect strong morphology-program coupling [Paper] [Paper: PDF p. 11, 13], [Figure 3b].  
  **core hypothesis**: Pretraining single-cell foundation models on gene subsets prioritized by STP-BENCH predictability will yield representations more transferable to spatial tasks than uniform masking.  
  **delta from paper**: STP-BENCH identifies *which* genes are morphology-informative; this idea leverages that list to *curate pretraining objectives*, moving from evaluation to generative modeling.  
  **initial method**: Use STP-BENCH gene-wise PCC (averaged across models/datasets) as weights for gene masking probability in scGPT pretraining; compare against uniform masking and expression-variance-based masking.  
  **validation**: Fine-tune on STP-BENCH tasks (virtual ST prediction, Cell2location) and benchmark on independent spatial datasets (e.g., SRT-Atlas); measure gain on low-PCC genes.  
  **failure modes**: If morphology-predictable genes are highly co-expressed, masking them may not improve generalization; if they are technical artifacts (e.g., ribosomal), benefit vanishes.  
  **innovation status**: unverified  

- **name**: Cross-Tissue Adapter for Spatial Multi-Omics Alignment  
  **originating limitation/observation**: STP-BENCH shows cross-tissue generalization gap is severe (−0.35) and negative transfer occurs when naively merging cancer types [Paper] [Paper: PDF p. 17, 19], [Figure 5b,d], implying tissue-specific morphology-expression manifolds.  
  **core hypothesis**: A lightweight, tissue-conditioned adapter module inserted between PFM encoder and ST predictor can align tissue-specific manifolds without full retraining.  
  **delta from paper**: STP-BENCH diagnoses the problem (tissue specificity); this idea proposes a *modular solution* compatible with existing STP-BENCH models (e.g., TRIPLEX), enabling plug-and-play cross-tissue deployment.  
  **initial method**: For each tissue type, learn a tissue-specific adapter (2-layer MLP) that transforms UNIv2 embeddings; train adapters end-to-end with frozen backbone on multi-tissue data, using contrastive loss to pull same-tissue embeddings closer.  
  **validation**: Test adapter on STP-BENCH cross-tissue tasks (e.g., LUAD→BRCA); compare gap reduction vs full fine-tuning; ablate adapter to confirm necessity.  
  **failure modes**: Adapter may overfit to small tissue cohorts; if tissue manifolds are non-linearly separable, MLP fails; requires tissue label at inference.  
  **innovation status**: unverified  

- **name**: SSIM-Guided Diffusion for Spatial Structure Preservation  
  **originating limitation/observation**: STP-BENCH uses SSIM as secondary metric but finds it trends consistently with PCC [Paper] [Paper: PDF p. 10, 11]; however, generative models (STFlow/Stem) are evaluated only on PCC/MAE, ignoring their structural advantage [Paper] [Paper: PDF p. 6, 28–29].  
  **core hypothesis**: Incorporating SSIM as an explicit loss term during diffusion training will improve spatial coherence of generated expression maps, particularly for long-range patterns (e.g., tumor-stroma boundaries).  
  **delta from paper**: STP-BENCH *measures* spatial structure via SSIM; this idea *optimizes for it* in generative modeling, bridging the gap between evaluation metric and training objective for spatial transcriptomics.  
  **initial method**: Modify STFlow’s denoising objective to include weighted SSIM loss between predicted and ground-truth spatial grids, alongside MSE; tune weight to balance fidelity and structure.  
  **validation**: Compare SSIM scores of STFlow variants on STP-BENCH; test downstream impact on SpaGCN ARI and visual inspection of boundary sharpness.  
  **failure modes**: SSIM optimization may degrade spot-level PCC; grid rescaling (p.32) introduces interpolation artifacts; SSIM is sensitive to normalization choices.  
  **innovation status**: unverified