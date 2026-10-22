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
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-05 | [Paper] [Paper: PDF p. 1] |
| Core contribution | First large-scale, standardized, multi-platform benchmark for virtual ST models, enabling controlled comparison of architectures under unified PFM encoding and downstream biological evaluation | [Paper] [Paper: PDF p. 2–4] |
| Target task | Predicting spatial gene expression (spot-level) from H&E image patches ("virtual ST") | [Paper] [Paper: PDF p. 2, Fig. 1a] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium/Xenium); STP-BENCH-EXTERNAL (185,831 spots, same 6 cancers, cross-institution/tissue/platform) | [Paper] [Paper: PDF p. 4, Fig. 1b] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6, Fig. 1c] |
| Primary encoder | UNIv2 pathology foundation model (PFM), used as default where architecturally compatible | [Paper] [Paper: PDF p. 7–8, Fig. 2a] |
| Evaluation metrics | PCC (Equation 1), MAE (Equation 2), SSIM; plus downstream: Cell2location PCC, SpaGCN ARI | [Paper] [Paper: PDF p. 31–32, Fig. 4] |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结

STP-BENCH 是首个系统化、大规模、多平台的 virtual ST 统一基准，通过强制统一使用 UNIv2 等病理基础模型（PFM）作为图像编码器，剥离了图像表征能力对模型性能评估的干扰，揭示出多数现有架构并未超越线性探针基线；它进一步证明基因可预测性存在普适性天花板（由形态-转录耦合强度决定），而多尺度建模（如 TRIPLEX、DeepSpot）仅在特定生物学程序（基质重塑、免疫浸润）上带来边际增益；该基准覆盖从 spot-level 表达到 cell-type deconvolution 和 spatial domain identification 的完整生物推理链，但其效用高度依赖原始 ST 平台的数据质量（Xenium > Visium）。  

## 03 研究问题

论文直面 virtual ST 领域的核心方法论困境：**如何公平、可靠、生物学可解释地评估模型进步？**  
作者观察到，既有工作因三重缺陷导致结论不可靠——（1）数据层面：小规模、异构、单平台数据集（如仅 Visium）缺乏统计效力与泛化代表性；（2）方法层面：各模型捆绑私有图像编码器（ResNet50、CTransPath 等），使架构创新与编码器能力混杂，无法归因性能来源；（3）评估层面：仅报告 aggregate PCC，忽略 per-gene 可预测性、下游任务效用及鲁棒性。  
因此，研究问题被精炼为：**能否构建一个资源完备、协议统一、评估多维的基准，以解耦 encoder 与 architecture 的贡献，并实证刻画 virtual ST 的能力边界与生物学适用性？** [Paper] [Paper: PDF p. 2–4]

## 04 研究背景与发展路径

virtual ST 的演进呈现“范式并行、编码器跃迁”双主线：  
- **范式主线**：从早期回归模型（ST-Net）→ 引入邻域/全局上下文（TRIPLEX, DeepSpot）→ 多模态对齐（BLEEP, STco）→ 生成式建模（STFlow, Stem）[Paper] [Paper: PDF p. 3]；  
- **编码器主线**：从 ImageNet-CNN（ResNet50）→ 小规模病理 CNN → 大规模 ViT-based PFM（UNIv2, Virchow2）[Paper] [Paper: PDF p. 10]。  
然而，两条主线在评估中从未解耦：Wang et al. [50] 保留原生 encoder，混淆架构贡献；HEST-1K [51] 虽用大样本但仅测 PFM embedding 与基因的简单回归，未覆盖真实 virtual ST 架构。STP-BENCH 的发展路径正是对这一断裂的缝合：**以 PFMs 为统一接口，将全部 21 种架构“插拔”到同一表征层，再通过 multi-granularity 评估反推架构的真实附加值** [Paper] [Paper: PDF p. 4]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平** | 模型排名随 encoder 切换剧烈波动（如 CFANet 从第16跳至第6） | 各模型原生 encoder 在预训练域、规模、范式上差异巨大，性能提升可能源于 encoder 而非 architecture | [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **能力边界模糊** | HMHVGs 与 marker genes 预测性能悬殊（PCC≈0.4 vs ≈0.2），且跨模型一致性高 | 基因可预测性由形态-转录内在耦合强度决定，而非模型能力；低表达 marker genes 在 Visium 上信噪比过低 | [Paper] [Paper: PDF p. 9–10, Fig. 2a,c,d] |
| **下游效用存疑** | Cell2location 和 SpaGCN 性能在 Xenium 上显著优于 Visium，且与 spot-level PCC 高度相关 | 虚拟 ST 的生物学价值受原始 ST 数据质量（如 transcript counts）制约，非纯算法问题 | [Paper] [Paper: PDF p. 14–15, Fig. 4a–c] |
| **鲁棒性未经检验** | Cross-tissue 泛化 gap 达 −0.35，远超 cross-institution（−0.10） | 形态-表达映射具有强组织特异性，跨癌种迁移需克服生物学异质性，非技术 batch effect | [Paper] [Paper: PDF p. 17, Fig. 5b] |
| **扩展性误导** | Inter-cohort scaling（BRCA+LUAD+PRAD）导致负向迁移 | 简单拼接多癌种数据会引入冲突的形态先验，损害 tissue-specific mapping | [Paper] [Paper: PDF p. 18, Fig. 5d] |

## 06 核心思想

论文的核心思想是 **“解耦评估 + 边界测绘”**：  
- **解耦评估**：将 virtual ST 流程形式化为 `H&E patch → [PFM encoder] → [architecture head] → gene expression`，强制固定 `[PFM encoder]` 层（UNIv2），使所有比较聚焦于 `[architecture head]` 的增量价值，从而终结“是模型好还是 encoder 好”的归因混乱 [Paper] [Paper: PDF p. 7–9]；  
- **边界测绘**：不满足于 aggregate PCC，而是系统测绘三个维度的能力边界：（1）*基因维度*：识别哪些基因（如 COL1A1, LAG3）因依赖多尺度形态（纤维化梯度、淋巴聚集）而受益于 TRIPLEX/DeepSpot；（2）*生物学维度*：验证虚拟 profile 是否足以支撑 Cell2location（cell abundance）和 SpaGCN（spatial domains）等下游任务；（3）*鲁棒性维度*：量化 cross-institution（技术）、cross-tissue（生物）、cross-platform（技术+生物）三类迁移的性能衰减，揭示 tissue-specificity 是最大瓶颈 [Paper] [Paper: PDF p. 11–19]。

## 07 方法总览

STP-BENCH 的方法框架是 **“三支柱评估体系”**：  
1. **统一性能基准（Fig. 1d）**：在 STP-BENCH-INTERNAL 上，用 PCC/MAE/SSIM 评估 21 模型对 HMHVGs 和 16 TME marker genes 的预测；强制 UNIv2 编码器（w/ PFM），对比 native encoder（w/o PFM）以量化 encoder 贡献；  
2. **多粒度生物学分析（Fig. 1e–f）**：（i）*基因级*：绘制 gene-wise PCC heatmap（Fig. 3a），识别 margin-gain genes（Fig. 3b）；（ii）*基因集级*：用 singscore 计算 GO pathway activity PCC（Fig. 3c–e）；（iii）*细胞/组织级*：用 Cell2location（Fig. 4a）和 SpaGCN（Fig. 4b–c）评估虚拟 profile 的下游效用；  
3. **鲁棒性与可扩展性（Fig. 1g）**：在 STP-BENCH-EXTERNAL 上测试 cross-institution/tissue/platform 泛化（Fig. 5a–b），并进行 intra-/inter-cohort 数据缩放实验（Fig. 5c–d），检验 performance 是否随数据量/多样性单调提升。  

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **Unified PFM Encoder (UNIv2)** | Extracts histomorphological features from 224×224 H&E patches into fixed-dim embeddings | To isolate architecture contribution by eliminating encoder variability; UNIv2’s large-scale pathology pretraining provides superior morphological semantics | Input: H&E patch; Output: 1024-dim embedding | [Paper] [Paper: PDF p. 7–10, Fig. 2e shows UNIv2 > CTransPath > ResNet50] | Severe ranking inversion (e.g., CFANet drops from 6th to 16th) and overall performance collapse for w/o PFM models [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **Multi-scale Context Integration (TRIPLEX/DeepSpot)** | Fuses local (target spot), neighborhood (surrounding spots), and global (whole-slide) morphological context | To capture long-range dependencies (e.g., fibrosis gradients, immune fronts) that single-patch encoders miss | Input: UNIv2 embeddings of target/neighbor/global patches; Output: fused representation for regression | [Paper] [Paper: PDF p. 11, 13, 25–26; Fig. 3b shows largest ΔPCC for stromal/immune genes] | Loss of gain on stromal (COL1A1) and immune (LAG3) genes; gene set PCC for "T Cell Activation" drops significantly [Paper] [Paper: PDF p. 13, Fig. 3e] |
| **Bi-modal Contrastive Alignment (BLEEP/STco/mclSTExp)** | Learns joint embedding space for H&E patches and gene expression via contrastive loss | To enable retrieval-based inference and leverage spatial coordinate info (STco/mclSTExp) | Input: UNIv2 patch emb + gene expr vector (+ coords); Output: shared 512-dim space for nearest-neighbor retrieval | [Paper] [Paper: PDF p. 6, 26–27; Fig. 2a shows moderate PCC, outperformed by top regressors] | Reduced robustness to cross-tissue shift (lower Spearman ρ in Extended Data Fig. 5–6) and weaker gene set recovery [Paper] [Paper: PDF p. 17] |
| **Generative Conditional Modeling (STFlow/Stem)** | Models conditional distribution p(expr \| H&E) via flow matching/diffusion | To capture expression uncertainty and multimodality beyond point estimates | Input: UNIv2 patch emb (+ coords for STFlow); Output: sampled gene expression vector | [Paper] [Paper: PDF p. 6–7, 28–29; Fig. 2a shows lowest PCC among top performers] | Poorer downstream utility: lowest ARI in SpaGCN (Fig. 4c) and weakest cell abundance correlation (Fig. 4a) [Paper] [Paper: PDF p. 14] |
| **Downstream Task Pipeline (Cell2location/SpaGCN)** | Translates predicted gene expr into cell-type abundances or spatial domains | To assess if virtual ST preserves biologically meaningful structure beyond spot-level numbers | Input: predicted spot-by-gene matrix; Output: cell-type PCC or domain ARI | [Paper] [Paper: PDF p. 14–15, Fig. 4a–c; shows TRIPLEX/DeepSpot top performers] | If removed, evaluation reduces to purely statistical metrics (PCC), losing biological interpretability — a key stated limitation of prior work [Paper] [Paper: PDF p. 2–3] |

## 09 关键公式与符号

论文未提出新公式，但明确定义并使用了三个核心评估指标：  
- **Equation 1 (PCC)**：`PCCg,s = Σ(ŷi,g − ȳ̂g)(yi,g − ȳg) / √[Σ(ŷi,g − ȳ̂g)² · Σ(yi,g − ȳg)²]` [Paper] [Paper: PDF p. 31]  
  - `ŷi,g`, `yi,g`: predicted & ground-truth log-normalized expression of gene `g` at spot `i`  
  - `ȳ̂g`, `ȳg`: mean of predicted & ground-truth across all `N` spots in section `s`  
  - *Use*: Primary metric for spot-level accuracy; reported as mean across genes and folds.  
- **Equation 2 (MAE)**：`MAEg,s = (1/N) Σ|ŷi,g − yi,g|` [Paper] [Paper: PDF p. 32]  
  - *Use*: Quantifies absolute error magnitude in log-expression space; complements PCC.  
- **SSIM**: Computed via `skimage.metrics.structural_similarity` on spatial grids [Paper] [Paper: PDF p. 32]  
  - *Key symbols*: `data_range=1.0`, min-max normalized expression images, rescaled coordinates to discrete grid.  
  - *Use*: Captures spatial coherence of expression landscapes, beyond spot-wise correlation.  
- **Other critical symbols**:  
  - `HMHVG`: High-mean highly-variable genes (200 genes selected by rank-sum of mean & std) [Paper] [Paper: PDF p. 33]  
  - `TME markers`: 16 immune/stromal/epithelial checkpoint genes (e.g., `CD3E`, `ACTA2`, `PDCD1`) [Paper] [Paper: PDF p. 7, 33]  
  - `ARI`: Adjusted Rand Index for spatial domain agreement [Paper] [Paper: PDF p. 36]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|-------------------------------|--------|
| **Fig. 2a** | Unified PFM standardization reorders model rankings | 21 models on STP-BENCH-INTERNAL (7 datasets), w/ UNIv2 vs w/o PFM; evaluated on HMHVGs & marker genes | Most w/ PFM models < linear probing baseline; TRIPLEX/DeepSpot > baseline; w/o PFM models generally worse | UNIv2 encoder is dominant factor; architectural gains are marginal and model-specific | That any specific architecture is universally superior — rankings change with encoder [Paper] [Paper: PDF p. 9] | [Paper] [Paper: PDF p. 8–9, Fig. 2a] |
| **Fig. 2c-d** | Gene expression level (not morphology) drives predictability gap | NCCHE-LUAD-Xenium (high counts) vs NCCHE-LUAD-Visium (low counts); stratified by expression quantile | Xenium: PCC≈0.58 for both HMHVGs & markers; Visium: PCC≈0.4 vs ≈0.19; Kruskal-Wallis p<1e-12 | Low transcript counts in Visium, not inherent morphological uncoupling, limit marker gene prediction | That morphology cannot encode immune biology — it *can*, given sufficient signal (Xenium proves it) | [Paper] [Paper: PDF p. 10, Fig. 2c-d] |
| **Fig. 3a** | Gene-wise predictability is model-agnostic | Gene-wise PCC heatmap across 20 models (excluding zero-shot) on STP-BENCH-INTERNAL | Smooth separation: genes easy/hard for one model are easy/hard for all; curved boundary shows architectural shifts | Prediction ceiling is set by morphology-transcript coupling strength, not model capacity | That model design is irrelevant — TRIPLEX/DeepSpot *do* shift the boundary for specific genes [Paper] [Paper: PDF p. 11] | [Paper] [Paper: PDF p. 11, Fig. 3a] |
| **Fig. 4a-c** | Spot-level accuracy translates to downstream biological utility | Cell2location PCC & SpaGCN ARI on three cohorts (Xenium/Visium), using same six models | TRIPLEX/DeepSpot top in both tasks; Xenium cohorts >> Visium cohorts; rare cell types (plasma cells) poorly recovered | Virtual ST utility is platform-dependent and scales with spot-level PCC; major lineages (epithelial, T cells) are recoverable | That virtual ST can replace real ST for rare cell analysis — plasma/mast cells show low correlation [Paper] [Paper: PDF p. 14] | [Paper] [Paper: PDF p. 14–15, Fig. 4a–c] |
| **Fig. 5a-b** | Internal rankings generalize across domain shifts | Cross-institution/tissue/platform on STP-BENCH-EXTERNAL; Spearman ρ between internal & external PCC | ρ>0.86 for institution/tissue; ρ=0.62 for platform; cross-tissue gap (−0.35) >> cross-institution (−0.10) | Architectural superiority is robust to technical variation but fragile to biological heterogeneity | That cross-tissue generalization is feasible with current models — gap is too large for practical use | [Paper] [Paper: PDF p. 17, Fig. 5a-b] |

## 11 对结论的正确理解

- **“Most models fail to beat linear probing”** 意味着：在 UNIv2 提供强大形态表征的前提下，当前复杂架构（如多头注意力、图网络、生成式解码）未能提供足够增量价值，**并非模型无效，而是 UNIv2 已捕获大部分可预测信号**；TRIPLEX/DeepSpot’s gains confirm that *some* architectural innovations *do* matter for specific biological programs [Paper] [Paper: PDF p. 9, 11, 13].  
- **“Gene predictability is universal”** 指：PCC 高低排序在模型间高度一致，**反映的是形态-转录关联的客观强度分布，而非模型缺陷**；这为 prioritizing genes for wet-lab validation (e.g., high-margin COL1A1) is valid [Paper] [Paper: PDF p. 11].  
- **“Xenium > Visium in downstream tasks”** 表明：虚拟 ST 的生物学效用**受限于输入 ST 数据的质量下限**；提升虚拟 ST 不应只优化模型，更需推动高灵敏度 ST 技术（如 Xenium）普及 [Paper] [Paper: PDF p. 14–15, 19].  
- **“Cross-tissue gap is large”** 揭示：virtual ST 的临床落地需 **tissue-specific training or domain adaptation**, not generic multi-cancer models — simple data aggregation harms performance (Fig. 5d) [Paper] [Paper: PDF p. 17–19].  
- **“Rankings preserve under domain shift”** 说明：内部 benchmark 选出的 top models (TRIPLEX/DeepSpot) are reliable choices for deployment in new institutions, but **not for new cancer types** [Paper] [Paper: PDF p. 17].

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium) | Extend benchmark to additional tumor types, normal tissues, and emerging platforms (e.g., Stereo-seq, Slide-seq) | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analysis focused on HMHVGs (200 genes) and 16 TME markers; lowly expressed or functionally diverse genes unexamined | Systematically investigate low-abundance genes and broader functional categories (e.g., metabolic pathways) | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | All evaluations performed at spot-level (multi-cell aggregates); no single-cell ST or virtual scST evaluation | Extend benchmarking principles to single-cell resolution as scST datasets and models mature | [Paper] [Paper: PDF p. 20] |
| **No perturbation modeling** | Benchmark assesses steady-state prediction, not response to interventions (e.g., drug treatment, genetic knockdown) | Incorporate perturbation-response datasets to evaluate virtual ST for causal inference | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| **TRIPLEX/DeepSpot’s multi-scale advantage may be confounded by training data scale** | These models were trained on larger datasets (e.g., WUSTL-BRCA has 157k spots); their gain could stem from more data, not architecture | Over-attributing success to multi-scale design risks misguiding future architecture search; simpler models might match if given equal data | Re-train all models (including linear probe) on identical subset (e.g., 50k spots) of WUSTL-BRCA and re-evaluate gene-wise margins | [Paper] [Paper: PDF p. 21 states WUSTL-BRCA has 157,138 spots, largest in INTERNAL; TRIPLEX/DeepSpot top performers] |
| **The “universal gene predictability” pattern may break under extreme morphological divergence** | Gene concordance was observed across 6 cancers, but may vanish when comparing e.g., brain (GBM) vs. prostate (PRAD) due to fundamental tissue architecture differences | Assuming universality could lead to overconfidence in cross-tissue transfer; needs validation on truly divergent pairs | Compute gene-wise PCC correlation (Spearman) between GBM and PRAD cohorts specifically; if ρ < 0.5, universality fails | [Paper] [Paper: PDF p. 38 Extended Data Fig. 1 shows GBM and PRAD in same figure, but no direct cross-cohort gene correlation reported] |
| **Using expm1 + clip for Cell2location input discards count distribution information** | Clipping negative values after expm1 forces non-negativity but distorts zero-inflated, overdispersed ST count distributions that Cell2location expects | May artificially inflate Cell2location PCC for models predicting near-zero values, biasing downstream evaluation | Compare Cell2location results using raw predicted logits (no expm1/clip) vs. clipped counts; if PCC difference >0.1, clipping is problematic | [Paper] [Paper: PDF p. 35 states “rounded and clipped to non-negative integers”; Cell2location is designed for counts] |
| **SSIM computation ignores spatial sparsity** | SSIM treats expression as continuous image; but ST data is sparse (many zeros), and SSIM’s luminance/contrast terms may be unstable on degenerate constant images | Could misrepresent spatial coherence for low-expression genes; undermines SSIM’s value as complementary metric | Report SSIM only for genes with >10% non-zero spots; compare SSIM-PCC correlation with and without zero-filtering | [Paper] [Paper: PDF p. 32 says “NaN entries from degenerate constant images” are excluded, but no threshold for sparsity defined] |
| **Cross-platform (Visium→Xenium) “improvement” may reflect dataset imbalance** | Fig. 5b right panel shows some models above “No Gap” line; but STP-BENCH-EXTERNAL Xenium data may have higher quality/less noise than INTERNAL Xenium | Suggests cross-platform is “easy” when it may just be easier test set; misleads on true platform-agnostic capability | Evaluate cross-platform on held-out INTERNAL Xenium samples (not just EXTERNAL) to control for data quality | [Paper] [Paper: PDF p. 4–5 defines INTERNAL as 609k spots (incl. NCCHE-LUAD-Xenium), EXTERNAL as 185k spots (incl. other sources); no statement on quality parity] |

## 14 学到的知识

- **Encoder is king, architecture is niche**: For virtual ST, investing in a strong PFM (UNIv2/Virchow2) yields larger gains than complex architecture tweaks; TRIPLEX/DeepSpot’s edge is narrow (ΔPCC~0.1) and confined to stromal/immune genes requiring multi-scale context [Paper] [Paper: PDF p. 9–13].  
- **Data quality > algorithm**: Xenium’s higher transcript counts directly enable better marker gene prediction (PCC 0.58 vs 0.19) and downstream utility, proving that virtual ST’s ceiling is set by experimental ST, not computational limits [Paper] [Paper: PDF p. 10, 14–15].  
- **Biological granularity is hierarchical**: Spot-level PCC strongly predicts Cell2location PCC and SpaGCN ARI (concordance across Fig. 2/4), meaning improvements must start at the gene level; no “free lunch” for downstream tasks [Paper] [Paper: PDF p. 14, 19].  
- **Robustness is asymmetric**: Models generalize well across institutions (technical) but catastrophically fail across tissues (biological), demanding tissue-aware training strategies, not generic multi-task learning [Paper] [Paper: PDF p. 17–19].  
- **Negative transfer is real**: Adding LUAD/PRAD data to BRCA training *harms* BRCA performance (Fig. 5d), confirming that morphological priors are cancer-type-specific; data curation must prioritize homogeneity over volume [Paper] [Paper: PDF p. 18].  

## 15 与既有知识的连接

- **Candidate connection / methodological connection**: STP-BENCH’s multi-granularity evaluation (gene → gene set → cell type → spatial domain) mirrors the hierarchical validation framework used in single-cell foundation model benchmarks (e.g., scFoundation, scGPT), but adapts it to spatial context and spot-level constraints.  
- **Candidate connection / methodological connection**: The finding that multi-scale context (TRIPLEX) aids stromal gene prediction aligns with graph neural network (GNN) literature showing that aggregating neighborhood information (e.g., via GCNConv in SEPAL) improves prediction of spatially structured phenotypes — though STP-BENCH shows GNNs (SEPAL) underperform pure multi-scale regression.  
- **Candidate connection / methodological connection**: The emphasis on cross-platform (Visium↔Xenium) generalization connects to cross-modal alignment work in multi-omics, where bridging modalities with different noise profiles (e.g., scRNA-seq ↔ ATAC-seq) requires careful handling of technical artifacts — STP-BENCH confirms this challenge persists in spatial omics.  
- **Weak connection / methodological connection**: While STP-BENCH evaluates perturbation-agnostic prediction, user’s interest in *perturbation prediction* remains unaddressed; no datasets or models in STP-BENCH involve interventions, making direct transfer impossible.  
- **Weak connection / methodological connection**: User’s focus on *single-cell foundation models* is orthogonal; STP-BENCH operates at spot-level (10–100 cells), and its conclusions about PFM dominance do not extrapolate to single-cell resolution where cellular heterogeneity dominates.  

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **Name**: Tissue-Aware PFM Adapter (TAPA)  
  **Originating limitation/observation**: Cross-tissue generalization gap is severe (−0.35) and inter-cohort scaling causes negative transfer, indicating that a single PFM cannot encode all tissue morphologies [Paper] [Paper: PDF p. 17–18, Fig. 5b,d].  
  **Core hypothesis**: Lightweight, tissue-specific adapters grafted onto a frozen universal PFM (e.g., UNIv2) can learn tissue-invariant morphological representations without catastrophic forgetting.  
  **Delta from paper**: STP-BENCH uses *one fixed PFM*; TAPA introduces *learnable, low-rank adapters per tissue type* (e.g., BRCA-adapter, LUAD-adapter) while keeping UNIv2 backbone frozen.  
  **Initial method**: For each cancer type in STP-BENCH-INTERNAL, train a LoRA adapter on UNIv2’s last layer; freeze UNIv2; train adapter + TRIPLEX head end-to-end on that tissue’s data.  
  **Validation**: Test cross-tissue generalization (e.g., train BRCA-adapter+TRIPLEX on BRCA, test on LUAD) and compare ARI/PCC against vanilla UNIv2+TRIPLEX.  
  **Failure modes**: Adapter overfits to single tissue; adapters don’t compose (BRCA+LUAD adapter ≠ sum of individual adapters); adapter adds latency.  
  **Innovation status**: unverified  

- **Name**: Morphology-Guided Gene Set Prior (MGGP)  
  **Originating limitation/observation**: Gene set scoring (Fig. 3e) shows TRIPLEX/DeepSpot excel on immune/stromal pathways, but current models predict genes independently; no explicit gene set structure is enforced [Paper] [Paper: PDF p. 13].  
  **Core hypothesis**: Injecting gene set membership as an inductive bias (e.g., via graph edges in EGGN or attention masks in TRIPLEX) will improve coherence of predicted gene set activity, especially for low-expression markers.  
  **Delta from paper**: STP-BENCH evaluates gene sets *post-hoc*; MGGP modifies model architecture to *jointly predict genes within biologically coherent sets*.  
  **Initial method**: Modify TRIPLEX’s fusion encoder to include gene set adjacency matrix (from GO BP) as a structural prior in cross-attention; mask attention between unrelated gene sets.  
  **Validation**: Compare singscore PCC for “T Cell Activation” set on NCCHE-LUAD-Xenium between vanilla TRIPLEX and MGGP-TRIPLEX; require ΔPCC ≥0.05.  
  **Failure modes**: Over-smoothing kills gene-specific signals; prior matrix is noisy/incomplete; computational overhead.  
  **Innovation status**: unverified  

- **Name**: Sparse-ST Imputation Augmentation (SSIA)  
  **Originating limitation/observation**: Visium’s low marker gene counts cause poor prediction (PCC≈0.19), but this is a data deficiency, not a model failure; STP-BENCH offers no solution for low-count regimes [Paper] [Paper: PDF p. 10, Fig. 2d].  
  **Core hypothesis**: Augmenting Visium training data with *in silico* high-count pseudo-spots generated by a Xenium-trained STFlow model will boost Visium model performance without wet-lab cost.  
  **Delta from paper**: STP-BENCH treats platforms as separate; SSIA bridges them via *cross-platform generative augmentation*.  
  **Initial method**: Train STFlow on NCCHE-LUAD-Xenium; sample 100k pseudo-spots; add them to WUSTL-BRCA-Visium training set; retrain DeepSpot.  
  **Validation**: Measure PCC gain on Visium marker genes (e.g., CD3E, CD68); require gain >0.08 over baseline.  
  **Failure modes**: Domain gap causes pseudo-spot artifacts; augmentation dilutes Visium-specific features; STFlow’s own limitations propagate.  
  **Innovation status**: unverified