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
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-05 | [Paper: URL metadata] |
| Authors | Youngmin Chung et al. (21 authors, co-first and co-senior marked) | [Paper] [Paper: PDF p. 1] |
| Core contribution | First large-scale, standardized, multi-platform benchmark for virtual ST models, with unified PFM encoding, gene-level interpretability analysis, downstream biological utility evaluation, and robustness testing | [Paper] [Paper: PDF p. 2–4, Fig. 1] |
| Data scale | STP-BENCH-INTERNAL: 609,024 spots across 6 cancer types, 202 slides; STP-BENCH-EXTERNAL: 185,831 spots across same 6 types, 73 slides | [Paper] [Paper: PDF p. 4, Fig. 1b] |
| Models evaluated | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6, Fig. 1c] |
| Key metrics | PCC (Equation 1), MAE (Equation 2), SSIM | [Paper] [Paper: PDF p. 31–32] |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结

该论文提出了 STP-BENCH ——首个面向 virtual spatial transcriptomics（虚拟空间转录组）的统一、系统性基准，覆盖 Visium 和 Xenium 双平台、六种癌症的大规模数据（超 79 万 spots），强制统一使用 pathology foundation model（PFM）作为图像编码器以解耦架构与表征能力。其核心发现是：多数现有模型在统一编码下无法超越线性探针基线；基因可预测性存在强普适性天花板（某些基因对所有模型均难预测），而多尺度架构（如 TRIPLEX、DeepSpot）仅在特定生物学通路（如基质重塑、免疫浸润）上提供边际增益；下游任务（cell deconvolution、spatial domain ID）性能与 spot-level PCC 高度一致，且严重受限于原始 ST 数据质量（Xenium > Visium）。该工作不提出新模型，而是通过严格控制变量揭示领域真实瓶颈。

## 03 研究问题

论文直面 virtual ST 领域的评估危机：当不同研究采用异构小数据集、私有训练流程、混杂的图像编码器（ImageNet vs. pathology PFM）、且仅报告 aggregate PCC 时，模型进步是否真实？[Paper] [Paper: PDF p. 2–3] 这一问题背后隐含三个子问题：（1）若剥离图像编码器差异，哪些模型架构真正具备泛化优势？（2）spot-level 预测精度能否可靠传导至细胞类型丰度、空间结构等生物学粒度？（3）模型在跨机构、跨组织、跨平台等现实分布偏移下的鲁棒性边界何在？[Paper] [Paper: PDF p. 4, 14, 17] 论文将这些问题转化为可操作的 benchmark 设计目标，而非停留在方法论批评层面。

## 04 研究背景与发展路径

virtual ST 的发展已形成三条技术主线：回归式（ST-Net → TRIPLEX/DeepSpot）、双模态对齐式（BLEEP → mclSTExp）、生成式（Stem/STFlow）[Paper] [Paper: PDF p. 3, 6]。但评估始终滞后：Wang et al. 2024 [50] 用原生编码器评测，混淆了 encoder 与 architecture 贡献；HEST-1K [51] 构建了大规模配对数据，却仅用简单回归评测 PFM embedding 与基因的相关性，未覆盖主流模型家族 [Paper] [Paper: PDF p. 3–4]。STP-BENCH 的演进路径正是对这两条失败路径的修正——它继承 HEST-1K 的数据规模与多平台思想，但彻底重构评估范式：强制统一 encoder（UNIv2）、重实现全部 21 模型、引入基因级/通路级/下游任务级多维验证，并将“鲁棒性”从口号变为可量化的 cross-institution/tissue/platform 实验 [Paper] [Paper: PDF p. 4–5, Fig. 1]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **Evaluation unfairness** | Model rankings shift dramatically when swapping native encoders for UNIv2 (e.g., CFANet jumps from 16th to 6th) | Prior works conflate architectural innovation with image encoder quality; encoders differ in pretraining scale, domain, and paradigm [Paper] [Paper: PDF p. 3, 9] | Figure 2b shows rank reversal; [Paper] [Paper: PDF p. 9] states “evaluations in previous works [...] are likely unfair comparisons” |
| **Biological interpretability gap** | Aggregate PCC masks which genes/pathways are recoverable; marker genes (e.g., CD3E, PDCD1) show consistently lower predictability than HMHVGs | Morphology-to-expression mapping is gene-specific; some programs (e.g., immune checkpoints) depend on long-range tissue context invisible to local patches [Paper] [Paper: PDF p. 9, 13] | Figure 2a shows PCC ≈0.2 for markers vs. ≈0.4 for HMHVGs; Figure 3a heatmap reveals universal gene-wise concordance across models |
| **Downstream utility unverified** | Spot-level accuracy does not guarantee utility for cell-type deconvolution or spatial domain identification | Predicted profiles may preserve statistical correlation but lose spatial coherence or biological structure required by downstream tools [Paper] [Paper: PDF p. 14] | Figure 4a–c shows TRIPLEX/DeepSpot top-performing on Cell2location/SpaGCN, but performance drops sharply on Visium vs. Xenium cohorts, mirroring gene-level gap |
| **Robustness under domain shift poorly characterized** | Models trained on one institution/tissue/platform fail unpredictably on others; inter-cohort scaling causes negative transfer | Morphology-to-expression mappings are highly tissue-specific; simple data aggregation ignores biological heterogeneity [Paper] [Paper: PDF p. 17, 19] | Figure 5b shows cross-tissue gap up to −0.35 PCC; Figure 5d shows adding LUAD/PRAD to BRCA training *lowers* BRCA test performance |

## 06 核心思想

论文的核心思想不是“如何构建更好的 virtual ST 模型”，而是“如何科学地定义‘更好’”。其逻辑链为：**评估失准 → 归因混乱 → 解耦必要 → 多维验证 → 揭示本质瓶颈**。具体而言：（1）指出当前评估中 encoder choice 是主要混杂因子，故必须强制统一（UNIv2）以隔离 architecture effect；（2）发现 gene-wise predictability 具有跨模型强一致性，暗示瓶颈在于 morphology-gene biology coupling，而非模型 capacity；（3）证明下游任务性能是 spot-level PCC 的单调函数，且受原始 ST 平台质量（Xenium’s higher sensitivity）主导，从而将问题锚定在数据层而非算法层；（4）揭示跨组织泛化是最大挑战，反向提示未来工作需建模 tissue-aware morphological priors，而非追求通用架构 [Paper] [Paper: PDF p. 17–19]。

## 07 方法总览

STP-BENCH 的方法论是“控制变量 + 多维穿透”：在统一 PFM 编码（UNIv2）前提下，对 21 个代表性模型进行三层次评估：（1）**基础性能层**：在 STP-BENCH-INTERNAL 上用 PCC/MAE/SSIM 评测 HMHVGs 和 TME marker genes，识别 baseline vs. architecture gain；（2）**生物学解释层**：基因级 heatmap（Fig. 3a）、通路级 singscore（Fig. 3c–e）、下游任务（Cell2location/SpaGCN，Fig. 4）验证预测是否承载真实生物学信号；（3）**鲁棒性层**：在 STP-BENCH-EXTERNAL 上设计 cross-institution/tissue/platform 三类迁移实验（Fig. 5a–b），并量化 intra-/inter-cohort scaling 效应（Fig. 5c–d），将 benchmark 从静态评测升维为动态压力测试 [Paper] [Paper: PDF p. 4–5, Fig. 1]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|---------------------|------------------------|-----------------------------------|
| **Unified PFM Encoder (UNIv2)** | Extract fixed-dim histology embeddings from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability — the central confounder in prior work [Paper] [Paper: PDF p. 3, 7] | Input: H&E patch; Output: 1024-dim vector | Figure 2b shows rank reversal with native encoders; Figure 2e confirms UNIv2 > CTransPath > ResNet50 | Removal would revert to unfair comparison; models like CFANet would drop ~10 ranks (Fig. 2b) |
| **Gene Set Scoring (singscore)** | Compute per-spot activity score for GO Biological Process terms from predicted expression | To bridge gene-level accuracy and functional biology — aggregate PCC cannot reveal if immune pathways are preserved [Paper] [Paper: PDF p. 13] | Input: spot-by-gene matrix; Output: spot-by-gene-set matrix | Figure 3c–e shows TRIPLEX/DeepSpot top on T Cell Activation & Cell-Matrix Adhesion pathways; Spearman ρ=0.902 with gene-level PCC [Paper] [Paper: PDF p. 13] | Removal would leave evaluation at statistical correlation level, missing functional coherence validation |
| **Cross-Platform Pseudo-Spot Binning** | Aggregate Xenium single-molecule coordinates into 100µm×100µm pseudo-spots aligned with Visium grid | To enable fair benchmarking across Visium (spot-based) and Xenium (single-molecule) platforms — a key design for multi-platform validity [Paper] [Paper: PDF p. 22] | Input: Xenium transcript coords + registered H&E; Output: pseudo-spot expression + matching 224×224 patch | Figure 1b shows combined Visium/Xenium distribution; Online Methods details binning to match Visium spacing [Paper] [Paper: PDF p. 22] | Removal would exclude Xenium data, collapsing benchmark to single-platform and missing critical platform-gap insight (Fig. 2c vs. 2d) |
| **Downstream Task Pipeline (Cell2location/SpaGCN)** | Apply standard scRNA-seq reference-based deconvolution and spatial clustering to predicted profiles | To test if virtual ST outputs are *biologically actionable*, not just statistically correlated — the ultimate utility test [Paper] [Paper: PDF p. 14] | Input: predicted spot-by-gene matrix; Output: cell-type abundance / spatial domain labels | Figure 4a–c shows consistent ranking preservation (TRIPLEX/DeepSpot best) and Xenium>Visium performance gap mirroring Fig. 2 | Removal would render benchmark purely computational, unable to answer “does this help biologists?” |
| **Generalization Gap Quantification** | Compute ΔPCC = External_PCC − Internal_PCC for each model under cross-institution/tissue/platform | To move beyond “model A beats B” to “how fragile is A’s advantage?” — essential for real-world deployment guidance [Paper] [Paper: PDF p. 17] | Input: internal & external PCC scores; Output: scalar gap per model/scenario | Figure 5b visualizes gaps; text notes cross-tissue gap (−0.2 to −0.35) >> cross-institution (−0.05 to −0.10) [Paper] [Paper: PDF p. 17] | Removal would hide critical failure modes; e.g., inability to detect that cross-tissue is the dominant bottleneck |

## 09 关键公式与符号

论文明确给出两个核心公式，均用于 spot-level 评估：  
- **Equation 1 (PCC)**: $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}} $ [Paper] [Paper: PDF p. 31]  
  - 符号：$\hat{y}_{i,g}$ = predicted log-normalized expression of gene $g$ at spot $i$; $y_{i,g}$ = ground-truth; $\bar{\hat{y}}_g$, $\bar{y}_g$ = means across spots in section $s$.  
- **Equation 2 (MAE)**: $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}| $ [Paper] [Paper: PDF p. 32]  
  - 符号：同上，但 operates in log(1+x)-transformed space.  
- 其他关键指标：SSIM（structural similarity index，[Paper] [Paper: PDF p. 32]）、ARI（Adjusted Rand Index，[Paper] [Paper: PDF p. 36]）、singscore（[Paper] [Paper: PDF p. 13]）。  
- 无其他可核验公式；所有模型架构描述均为文字性（如 “TRIPLEX has three branches” [Paper] [Paper: PDF p. 25]），未提供数学形式化。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|-------------------------------|--------|
| **Figure 2a (Internal HMHVG/Marker PCC)** | Unified PFM standardization reveals true architectural ranking | 21 models, UNIv2 encoder (w/ PFM) vs. native encoders (w/o PFM), 7 datasets, HMHVGs (200 genes) vs. TME markers (16 genes) | Most models ≤ linear probing baseline (PCC≈0.4 for HMHVG, ≈0.2 for markers); TRIPLEX/DeepSpot top | PFM choice dominates architecture; marker genes are intrinsically harder to predict | “All marker genes are biologically uncoupled from morphology” — contradicted by high PCC in Xenium (Fig. 2c) | [Paper] [Paper: PDF p. 7–9, Fig. 2a] |
| **Figure 2c–d (Dataset-level stratification)** | Data sparsity (not morphology) drives marker gene gap | NCCHE-LUAD-Xenium (high counts) vs. NCCHE-LUAD-Visium (low counts), same models, same genes | Xenium: PCC≈0.58 for both HMHVG/marker; Visium: PCC≈0.19 for markers | Low transcript counts, not morphological invisibility, limit marker prediction | “Xenium eliminates all virtual ST limitations” — contradicted by persistent gene-wise ceiling (Fig. 3a) | [Paper] [Paper: PDF p. 9–10, Fig. 2c–d] |
| **Figure 3a (Gene-wise heatmap)** | Gene predictability is model-agnostic | 20 models, union of HMHVG+markers, STP-BENCH-INTERNAL | Smooth separation of high/low-PCC genes; consistent ordering across models | A universal morphology-gene coupling ceiling exists; architecture only shifts boundary marginally | “Architecture can overcome fundamental biological limits” — unsupported; gains are marginal (ΔPCC≥0.1 for only 8–85 genes/cohort) | [Paper] [Paper: PDF p. 11, Fig. 3a] |
| **Figure 4a–c (Downstream tasks)** | Spot-level PCC predicts downstream utility | Cell2location (Fig. 4a) and SpaGCN (Fig. 4b–c) applied to predicted profiles vs. ground truth, 3 cohorts | TRIPLEX/DeepSpot top on both tasks; Xenium cohorts >> Visium cohorts | Downstream utility is a direct function of spot-level accuracy and raw data quality | “Virtual ST enables novel biological discovery beyond measured ST” — unsupported; no new biology claimed, only fidelity assessment | [Paper] [Paper: PDF p. 14–15, Fig. 4] |
| **Figure 5a–b (Cross-domain generalization)** | Internal ranking preserves under domain shift | Cross-institution/tissue/platform transfers, STP-BENCH-EXTERNAL, UNIv2 encoder | Spearman ρ>0.86 for institution/tissue; cross-tissue gap up to −0.35 PCC | Architectural superiority is robust to technical batch effects but fragile to biological heterogeneity | “Cross-tissue generalization is solvable with bigger models” — contradicted by negative transfer in Fig. 5d | [Paper] [Paper: PDF p. 17, Fig. 5a–b] |

## 11 对结论的正确理解

论文结论必须严格限定在其实证范围内：（1）“多数模型不超越线性探针”仅在 **UNIv2 编码、HMHVG/marker 基因集、spot-level PCC** 下成立；若换用更难基因集或单细胞分辨率，结论可能不同 [Paper] [Paper: PDF p. 20]；（2）“基因可预测性天花板”指 **200 HMHVG + 16 markers 在当前数据和评估协议下的跨模型一致性**，不否定未来发现新 morphology-sensitive genes 的可能性；（3）“Xenium 优于 Visium”是 **针对所用 cohort 的 transcript count 和 SNR 差异**，非平台绝对优劣；（4）“负向迁移”指 **在 Fig. 5d 的特定 inter-cohort scaling 协议下（BRCA→+LUAD→+PRAD）**，不否定 domain-adaptive 或 tissue-aware 训练策略的有效性 [Paper] [Paper: PDF p. 19]。所有结论均基于统计显著性（p<10⁻⁵ for ρ, Kruskal-Wallis p<10⁻¹²）和多数据集复现（7 internal datasets, 3 external cohorts）。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 ST platforms (Visium/Xenium) | Extend benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms | [Paper] [Paper: PDF p. 20] |
| **Restricted gene set analysis** | Evaluations focused only on HMHVGs (200 genes) and 16 TME markers; lowly expressed or functionally diverse genes not systematically assessed | Systematic investigation of low-expression genes and broader functional categories | [Paper] [Paper: PDF p. 20] |
| **Spot-level granularity** | All evaluations performed at spot-level (aggregated transcripts), not single-cell resolution | Future benchmarking efforts should extend to single-cell ST datasets and virtual ST models | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|------------------|--------|
| **UNIv2 as sole PFM may overstate encoder dominance** | Using only UNIv2 ignores potential complementarity between encoder families (e.g., Virchow2’s superior cross-tissue rank preservation in Extended Data Fig. 5–6) [Paper] [Paper: PDF p. 17] | Over-reliance on one PFM could mask encoder-specific strengths for certain tasks (e.g., tissue generalization), leading to suboptimal model selection | Re-run core experiments (Fig. 2a, 5a) with Virchow2 and H-Optimus1 as primary encoders; compare rank correlation across encoders | [Paper] [Paper: PDF p. 17] states Virchow2/H-Optimus1 “maintained moderate-to-strong correlations” under tissue shift while ResNet/CTransPath did not |
| **singscore-based gene set scoring conflates ranking with magnitude** | singscore uses gene ranks within each spot, discarding absolute expression levels — may inflate scores for genes with flat but correctly ranked profiles | Downstream utility claims (e.g., “immune programs recovered”) may be overstated if predictions capture rank order but not dynamic range | Replace singscore with GSVA or AUCell (which use expression magnitudes) and recompute Fig. 3c–e; compare correlation with spot-level PCC | [Paper] [Paper: PDF p. 13] explicitly states singscore computes “averaging the ranks of member genes”, and Online Methods confirms rank-based implementation |
| **Cross-platform transfer (Visium→Xenium) confounds platform difference with data quality** | Performance “improvement” in Fig. 5b (right) likely stems from Xenium’s higher sensitivity, not model capability to bridge platforms | Misattribution could misdirect engineering effort toward platform-agnostic architectures instead of data-quality-aware modeling | Train models *only on Xenium* and test on Visium (reverse direction); if asymmetry persists, it confirms data-quality bias | [Paper] [Paper: PDF p. 17] admits “higher sensitivity and transcript counts from Xenium dataset compensating for the domain shift”, but does not test reverse direction |
| **Negative transfer in inter-cohort scaling may reflect poor cohort alignment, not inherent incompatibility** | The BRCA→+LUAD→+PRAD sequence in Fig. 5d uses raw cohorts without harmonization (e.g., batch correction, platform normalization) | Concluding “simple aggregation is detrimental” overlooks preprocessing as a confounder; harmonized multi-tissue training might succeed | Apply ComBat or BBKNN to harmonize expression matrices across cohorts before training; compare Fig. 5d results | [Paper] [Paper: PDF p. 22] describes preprocessing per-cohort but no cross-cohort harmonization step; Online Methods lacks batch correction mention |

## 14 学到的知识

- **评估优先级重排**：在 virtual ST 中，选择强大的 pathology foundation model（如 UNIv2）比设计复杂架构更能提升性能；benchmark 必须强制统一 encoder 才能公平比较 [Paper] [Paper: PDF p. 7–9]。  
- **生物学瓶颈定位**：基因可预测性存在强普适性（Fig. 3a），提示瓶颈在 morphology-gene biology coupling（如 stromal/immune genes needing macro-scale context），而非模型 capacity — 这直接支持用户研究中 **cell state representation** 应融合多尺度 spatial context（graph + image patches）。  
- **下游任务是终极验证**：Cell2location/SpaGCN 性能与 spot-level PCC 高度一致（Fig. 4），证明 **cross-modal alignment** 的价值不在 pixel-level fidelity，而在 preserving spatial biological structure for downstream inference。  
- **鲁棒性真相**：跨机构（technical）泛化稳健，跨组织（biological）泛化脆弱（Fig. 5b），说明 **multi-omics** 或 **perturbation prediction** 模型必须显式建模 tissue-specific morphological priors, not assume universality。  
- **数据质量即天花板**：Xenium 与 Visium 的性能鸿沟（Fig. 2c vs. 2d）贯穿所有层级（gene → pathway → cell type），警示 **spatial transcriptomics** benchmarking 必须报告原始数据质量指标（mean counts, detection rate）。  

## 15 与既有知识的连接

- **候选连接/方法论连接**：STP-BENCH 的 multi-granularity evaluation (gene → gene set → cell type → spatial domain) mirrors the hierarchical validation strategy in single-cell foundation model papers (e.g., scGPT, scFoundation), but adapts it to spatial context — suggesting user’s **single-cell foundation models** work could adopt similar downstream task pipelines (e.g., spatial deconvolution as a fine-tuning objective).  
- **候选连接/方法论连接**：TRIPLEX/DeepSpot 的多尺度架构 (local + neighbor + global patches) conceptually aligns with graph neural networks (**graph neural networks**) where nodes are spots and edges encode spatial proximity — user’s GNN work could formalize this as a heterogeneous graph (spot nodes + exemplar nodes + coordinate nodes) inspired by EGGN [Paper] [Paper: PDF p. 24].  
- **候选连接/方法论连接**：singscore-based gene set scoring (Fig. 3c–e) provides a lightweight, scalable alternative to heavy permutation-based methods for **biomedical AI**, directly applicable to user’s **cross-modal alignment** projects where gene set activity is a natural alignment target between modalities.  
- **弱连接/方法论连接**：论文未涉及 perturbation prediction 或 explicit cell state dynamics, 但其揭示的“morphology-to-expression mapping is tissue-specific”（Fig. 5b）为用户 **perturbation prediction** 研究提供了关键约束：任何 perturbation model must be conditioned on tissue context.  

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware PFM Adapter  
  **originating limitation/observation**: Cross-tissue generalization gap is severe (Fig. 5b, −0.35 PCC), and PFMs like Virchow2 show better rank preservation than ResNet (Paper: PDF p. 17) — suggesting encoder adaptation matters.  
  **core hypothesis**: Lightweight, tissue-specific adapters grafted onto frozen UNIv2 can preserve cross-tissue ranking while avoiding full encoder retraining.  
  **delta from paper**: STP-BENCH uses static UNIv2; this inserts trainable LoRA-style adapters per tissue type.  
  **initial method**: For each cancer type, add two 8-rank LoRA layers to UNIv2’s last transformer block; freeze UNIv2 backbone; train adapters + TRIPLEX head end-to-end.  
  **validation**: Test on cross-tissue transfer (e.g., train on LUAD, test on BRCA); metric: Spearman ρ of model rankings vs. internal validation.  
  **failure modes**: Adapter overfitting to tissue-specific noise; no improvement if tissue differences are orthogonal to UNIv2’s learned features.  
  **innovation status**: unverified  

- **name**: Gene-Set Guided Contrastive Learning  
  **originating limitation/observation**: Retrieval models (BLEEP/mclSTExp) underperform on immune/stromal genes (Fig. 3a,b), yet these genes form coherent pathways (Fig. 3e) — suggesting contrastive loss should operate at pathway level, not spot level.  
  **core hypothesis**: Aligning histology patches with *gene set activity vectors* (not raw expression) in contrastive space improves recovery of biologically structured programs.  
  **delta from paper**: STP-BENCH uses spot-level expression vectors for BLEEP/mclSTExp; this replaces them with singscore-derived pathway vectors.  
  **initial method**: Precompute singscore for 50 GO pathways per spot; use these 50-dim vectors as contrastive targets; modify BLEEP’s spot projection head to output 50-dim pathway embeddings.  
  **validation**: Compare pathway-level PCC (Fig. 3c) and downstream Cell2location performance (Fig. 4a) against original BLEEP.  
  **failure modes**: Pathway vectors may be too coarse, losing gene-specific signal; singscore noise amplifies in contrastive loss.  
  **innovation status**: unverified  

- **name**: SSIM-Guided Diffusion Refinement  
  **originating limitation/observation**: Generative models (STFlow/Stem) have lower spot-level PCC (Fig. 2a) but SSIM is consistent with PCC (Paper: PDF p. 11) — suggesting they capture spatial structure better than regression models, but current metrics don’t reward this.  
  **core hypothesis**: Incorporating SSIM as an auxiliary loss during diffusion training steers generated expression toward spatially coherent patterns, improving downstream spatial tasks.  
  **delta from paper**: STP-BENCH evaluates SSIM post-hoc; this integrates it into STFlow’s training objective.  
  **initial method**: Add SSIM loss term (weighted 0.1) to STFlow’s hybrid MSE+KL loss; compute SSIM on 2D spatial grids of predicted vs. ground-truth expression per gene.  
  **validation**: Measure ARI on SpaGCN (Fig. 4b–c) and SSIM itself; compare against vanilla STFlow.  
  **failure modes**: SSIM optimization may degrade spot-level PCC (trade-off); computational overhead of grid projection.  
  **innovation status**: unverified