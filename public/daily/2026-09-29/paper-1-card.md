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
| Authors | Youngmin Chung et al. (21 authors, co-first and co-senior indicated) | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Year | 2026 | [Paper] [Paper: PDF p. 1] |
| Core contribution | STP-BENCH — a large-scale, standardized, multi-platform benchmark for virtual ST models, comprising STP-BENCH-INTERNAL (609,024 spots) and STP-BENCH-EXTERNAL (185,831 spots), with unified PFM encoding, multi-granularity evaluation, and robustness testing | [Paper] [Paper: PDF p. 4–5], [Figure 1b], [Paper] [Paper: PDF p. 21] |
| Key models benchmarked | 21 models: 14 regression-based (e.g., TRIPLEX, DeepSpot, CFANet), 4 bi-modal retrieval (e.g., BLEEP, mclSTExp), 3 generative (e.g., STFlow, Stem) | [Paper] [Paper: PDF p. 6], [Figure 1c], [Paper] [Paper: PDF p. 22–29] |
| Key datasets | Six cancer types (LUAD, BRCA, PDAC, GBM, PRAD, CCRCC); two platforms (Visium, Xenium); internal cohort spans 202 slides; external cohort spans 73 slides | [Paper] [Paper: PDF p. 4–5], [Figure 1b], [Paper] [Paper: PDF p. 21] |
| Primary metrics | Pearson Correlation Coefficient (PCC) [Equation 1], Mean Absolute Error (MAE) [Equation 2], Structural Similarity Index Measure (SSIM) | [Paper] [Paper: PDF p. 31–32], [Equation 1], [Equation 2] |
| Evaluation granularity | Spot-level (gene-wise PCC), gene-set-level (singscore), cell-type-level (Cell2location), spatial-domain-level (SpaGCN + ARI), robustness (cross-institution/tissue/platform) | [Paper] [Paper: PDF p. 7–16], [Figure 2–5], [Paper] [Paper: PDF p. 34–36] |
| Code & data release | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face (https://huggingface.co/datasets/nexgem/STP-Bench) | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结  
STP-BENCH 是首个面向 virtual spatial transcriptomics（vST）的系统性、标准化、大规模基准，它通过统一病理基础模型（PFM）编码器重置了21种主流vST模型的性能排序，揭示出图像编码器选择远比模型架构创新更具决定性；该基准同时证明：基因可预测性存在普遍上限（由形态-转录耦合强度决定），多尺度建模（如TRIPLEX/DeepSpot）仅对特定生物学程序（基质/免疫/上皮分化）带来边际增益，且平台数据质量（Xenium > Visium）是下游生物分析效用的共同瓶颈。其核心价值不在于提出新模型，而在于提供可复现、可解耦、可扩展的评估基础设施，直击当前领域“不公平比较”与“黑箱评估”的方法论危机。

## 03 研究问题  
论文试图回答：在 virtual ST 领域缺乏统一评估标准的背景下，**如何分离并量化模型架构创新与图像编码器能力对预测性能的真实贡献？** 进一步追问：若剥离编码器差异，现有模型是否仍具备超越简单线性探针（linear probing）的生物学价值？哪些基因/通路/细胞类型/空间结构能被可靠恢复？这种恢复能力在跨机构、跨组织、跨平台等现实域偏移下是否稳健？这些问题源于作者对领域进展可信度的根本性质疑——即过往报告的性能提升可能主要归因于更强的图像 backbone（如从 ResNet50 升级到 UNIv2），而非模型设计本身 [Paper] [Paper: PDF p. 3–4]。

## 04 研究背景与发展路径  
虚拟空间转录组学（virtual ST）旨在从常规H&E染色切片预测空间基因表达，以规避实验ST的高成本瓶颈 [Paper] [Paper: PDF p. 2]。该方向已衍生出三类主流范式：回归式（如ST-Net）、双模态对齐式（如BLEEP，受CLIP启发）、生成式（如STFlow，基于扩散/流匹配）[Paper] [Paper: PDF p. 3]。然而，评估实践严重滞后：早期工作（如Wang et al. 2024 [50]）使用各模型原生编码器，混淆架构与编码器效应；另一项（HEST-1K [51]）虽构建大规模配对数据，却仅用简单回归评估PFM嵌入，未覆盖vST全谱系模型 [Paper] [Paper: PDF p. 3–4]。STP-BENCH 的发展路径正是对这一断裂的系统性缝合：它不追求单点技术突破，而是构建一个“控制变量”的评估操作系统——强制统一PFM（UNIv2）作为视觉前端，重实现全部21种模型，并将评估维度从单一PCC拓展至基因集、细胞类型、空间域及鲁棒性 [Paper] [Paper: PDF p. 4–5]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|----------|-------------|---------------------------|-------------------------|
| **不公平的模型比较** | 不同研究使用不同图像编码器（ResNet50 vs. UNIv2），导致性能差异无法归因于模型架构 | “architectural innovations and image encoding have been conflated in previous evaluations”；CFANet在原生编码器下排第16，换UNIv2后跃升至第6 [Paper] [Paper: PDF p. 9] | [Figure 2b], [Paper] [Paper: PDF p. 9] |
| **评估粒度过于粗放** | 仅报告整体PCC，忽略哪些基因/通路可被恢复，以及预测结果能否支撑下游生物分析 | “leaving the biological reliability of virtual ST and model robustness under realistic distribution shifts largely unexamined” [Paper] [Paper: PDF p. 3] | [Figure 3a–e], [Figure 4a–c], [Paper] [Paper: PDF p. 11–14] |
| **数据规模与多样性不足** | 先前基准依赖小样本、单平台、单癌种数据，统计效力弱，泛化性存疑 | “prior studies rely on small, heterogeneous datasets”；STP-BENCH-INTERNAL每癌种≥30,000 spots & ≥15 slides [Paper] [Paper: PDF p. 2, 4] | [Figure 1b], [Paper] [Paper: PDF p. 4, 21] |
| **鲁棒性验证缺失** | 模型在跨机构（batch effect）、跨组织（biological heterogeneity）、跨平台（Visium→Xenium）等真实场景下的表现未知 | “model reliability under domain shifts and data scaling” was “largely unexamined” [Paper] [Paper: PDF p. 2] | [Figure 5a–b], [Paper] [Paper: PDF p. 17] |
| **数据质量影响被忽视** | Visium与Xenium平台间基因计数差异巨大，但评估未分层讨论其对预测上限的制约 | “the gap is largely driven by data sparsity rather than morphological uncoupling alone”；Xenium marker genes PCC≈0.58 vs. Visium≈0.19 [Paper] [Paper: PDF p. 10] | [Figure 2c–d], [Paper] [Paper: PDF p. 10] |

## 06 核心思想  
论文的核心思想是：**virtual ST 的评估必须解耦（disentangle）图像编码器能力与模型架构能力，才能获得可归因、可复现、可指导研发的科学结论。** 这一思想驱动了STP-BENCH的全部设计：它将PFM（UNIv2）视为“标准显微镜”，所有模型都必须适配这台显微镜来观察组织；在此前提下，性能差异才真正反映模型“解读显微镜图像”的能力。进一步，该思想延伸为一种评估哲学——拒绝单一指标幻觉，坚持多粒度验证：若一个模型不能在基因集层面恢复T细胞激活通路（Fig. 3e），或不能在空间域层面支持SpaGCN聚类（Fig. 4b-c），则其spot-level的PCC再高也缺乏生物学意义。最终，该思想指向一个务实结论：提升vST效用的关键路径，或许不是堆砌更复杂模型，而是获取更高信噪比的ST数据（如Xenium）或开发更鲁棒的跨平台对齐策略。

## 07 方法总览  
STP-BENCH 的方法论是一个三层评估栈：（1）**统一编码层**：强制所有兼容模型使用UNIv2（或Virchow2/H-Optimus1等）作为patch encoder，对不兼容模型（如M2OST/M2ORT）明确标注并保留原编码器 [Paper] [Paper: PDF p. 9, 22–23]；（2）**多粒度评估层**：在spot-level（PCC/MAE/SSIM）、gene-set-level（singscore）、cell-type-level（Cell2location）、spatial-domain-level（SpaGCN+ARI）四个层级同步评测 [Paper] [Paper: PDF p. 7, 14, 34–36]；（3）**鲁棒性验证层**：设计Cross-Institution（同癌种不同医院）、Cross-Tissue（不同癌种）、Cross-Platform（Visium→Xenium）三大泛化场景，量化generalization gap [Paper] [Paper: PDF p. 17, Figure 5a–b]。整个流程严格遵循patient-level cross-validation以避免数据泄露，并公开全部代码与预处理数据以确保可复现性 [Paper] [Paper: PDF p. 30, 37]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **Unified PFM Encoder** | Standardize histology feature extraction across all models | To isolate architectural contribution from encoder strength; prior work conflated them [Paper] [Paper: PDF p. 3–4] | Input: 224×224 H&E patch; Output: fixed-dim embedding (e.g., UNIv2 CLS token) | [Figure 2b], [Paper] [Paper: PDF p. 9], [Paper] [Paper: PDF p. 22–23] | Severe ranking distortion (e.g., CFANet drops from #6 to #16); many models fall below linear probing baseline [Figure 2a] |
| **Gene Set Scoring (singscore)** | Compute per-spot activity scores for GO Biological Process terms from predicted expression | To assess if vST preserves functional programs beyond individual genes | Input: spot×gene matrix (pred/gt); Output: spot×gene_set matrix; PCC computed per gene_set | [Figure 3c–e], [Paper] [Paper: PDF p. 13, 35] | Loss of biological interpretability: models may predict genes well but fail to reconstruct coherent pathways (e.g., T Cell Activation) [Figure 3e] |
| **Cell2location Deconvolution** | Estimate spatial abundance of major cell types (epithelial, T cells, etc.) from vST profiles | To test if vST supports downstream cellular inference, a key clinical use case | Input: spot×gene matrix (pred/gt); Output: spot×cell_type abundance matrix; PCC per cell type | [Figure 4a], [Paper] [Paper: PDF p. 14, 35] | Failure to recover rare populations (plasma/mast cells) or misalignment with ground truth would invalidate vST for tumor microenvironment analysis [Figure 4a] |
| **SpaGCN + ARI Evaluation** | Identify spatial domains from vST expression and compare to ground-truth annotations | To verify vST captures tissue-level spatial architecture, essential for spatial biology | Input: spot×gene matrix + coordinates; Output: domain labels; ARI computed vs. reference | [Figure 4b–c], [Paper] [Paper: PDF p. 14, 36] | Low ARI indicates vST fails to resolve macroscopic tissue structures (e.g., tumor core vs. invasive margin), limiting its utility for spatial domain discovery [Figure 4b–c] |
| **Cross-Platform Generalization Test** | Evaluate models trained on Visium data on Xenium test data (and vice versa) | To assess feasibility of leveraging cheaper Visium training data for higher-resolution Xenium applications | Input: Visium-trained model + Xenium test patches/expressions; Output: PCC/ARI on Xenium | [Figure 5a–b], [Paper] [Paper: PDF p. 17] | If gap is large/negative, it implies platform-specific biases dominate, demanding platform-adaptive fine-tuning or domain translation modules |

## 09 关键公式与符号  
论文中明确给出两个可核验公式：  
- **Equation 1**（Pearson Correlation Coefficient, PCC）：  
  $$
  \text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2}} \quad \text{[Paper] [Paper: PDF p. 31]}
  $$  
  符号：$\hat{y}_{i,g}$ 为spot $i$、gene $g$ 的预测log(1+x)表达值；$y_{i,g}$ 为对应ground-truth；$\bar{\hat{y}}_g$, $\bar{y}_g$ 为其均值；$N$ 为spots数。PCC是全文核心指标，用于spot/gene/gene_set/cell_type/domain所有层级的评估。  
- **Equation 2**（Mean Absolute Error, MAE）：  
  $$
  \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^{N} |\hat{y}_{i,g} - y_{i,g}| \quad \text{[Paper] [Paper: PDF p. 32]}
  $$  
  符号同上。MAE在log-normalized空间计算，衡量绝对误差大小，与PCC互补。  
  *无其他可核验公式。关键指标SSIM在文本中描述为“skimage.metrics.structural_similarity”，但未给出数学定义 [Paper] [Paper: PDF p. 32]。*

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|---------------------------|--------|------------------------|-------------------------------|--------|
| **Internal Benchmark w/ UNIv2** | Unified PFM standardization reveals true architectural ranking | 21 models re-implemented with UNIv2 vs. native encoders; evaluated on STP-BENCH-INTERNAL (7 datasets) | Most models (e.g., ST-Net, BrSTNet) failed to beat linear probing baseline; TRIPLEX/DeepSpot consistently superior [Figure 2a] | PFM choice dominates performance; architectural gains are marginal and context-specific | That any single model is universally best across all genes/tasks | [Figure 2a], [Paper] [Paper: PDF p. 9] |
| **Gene-wise Stratification** | Gene predictability is universal across models | PCC computed per gene for 20 models; genes ranked by mean PCC across models into 5 bins | Strong concordance: genes hard for one model are hard for all; rankings stable across bins [Extended Data Fig. 1], [Figure 3a] | Predictability ceiling is governed by morphology-transcriptome coupling, not model design | That model architecture can overcome fundamental biological uncoupling | [Figure 3a], [Extended Data Fig. 1], [Paper] [Paper: PDF p. 11] |
| **Cross-Platform Generalization** | Xenium data quality compensates for domain shift | Models trained on Visium evaluated on Xenium (NCCHE-LUAD-Xenium); same models on Visium (NCCHE-LUAD-Visium) | Xenium PCC ≈0.58 (HMHVG), Visium PCC ≈0.09; gap primarily due to low counts in Visium [Figure 2c–d] | Platform-dependent data quality is a shared bottleneck for all granularities of analysis | That cross-platform transfer is inherently impossible | [Figure 2c–d], [Paper] [Paper: PDF p. 10] |
| **Multi-granularity Consistency** | Gene-level accuracy predicts downstream utility | Cell2location PCC and SpaGCN ARI computed for same 6 models across 3 cohorts | Rankings preserved: TRIPLEX/DeepSpot top in gene, cell-type, and domain tasks [Figure 4a–c] | Improvements in spot-level prediction translate to higher-order biological inference | That a model good at genes is automatically good at all downstream tasks (e.g., rare cell types) | [Figure 4a–c], [Paper] [Paper: PDF p. 14] |
| **Inter-cohort Scaling** | Aggregating diverse cancer types harms performance | WUSTL-BRCA trained alone vs. +NCCHE-LUAD vs. +HEST-PRAD; tested on Massey-BRCA | Performance decreased with each added tissue type [Figure 5d] | Simple data aggregation causes negative transfer due to tissue-specific morphology-expression mapping | That larger multi-tissue datasets always improve generalization | [Figure 5d], [Paper] [Paper: PDF p. 18] |

## 11 对结论的正确理解  
论文结论**不可**被理解为“virtual ST 没有前途”或“所有模型都一样差”。正确理解是：（1）**评估范式必须升级**：在UNIv2等强PFM成为标配后，继续用PCC排名而不控制编码器已失去科学意义；（2）**生物学信号存在硬边界**：某些基因（如低表达marker）的预测上限由H&E图像信息量和ST数据质量共同决定，非模型能轻易突破；（3）**架构价值是条件性的**：TRIPLEX/DeepSpot的优势仅在需要整合多尺度形态（如基质纤维、免疫浸润前沿）时显现，对单纯上皮结构预测，线性探针已足够 [Paper] [Paper: PDF p. 11, 19]；（4）**鲁棒性需针对性设计**：跨组织泛化失败表明，通用形态表征不足，需引入组织感知（tissue-aware）或自适应（domain-adaptive）机制 [Paper] [Paper: PDF p. 19]。这些结论共同指向一个务实研发路径：与其追求更复杂模型，不如聚焦于高质量多平台数据共建、组织特异性表征学习、以及跨粒度验证闭环。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|------------------------|-------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium) | “Extending the benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms will be important for broader generalizability” | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analysis focused on HMHVGs (200 genes) and 16 TME markers; lowly expressed/functional diverse genes not systematically studied | “systematic investigation of lowly expressed or functionally diverse genes remains an open direction” | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluations performed at Visium/Xenium pseudo-spot level, not single-cell resolution | “future benchmarking efforts may extend these principles to evaluations at single-cell resolution” with emerging scST data/models | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|----------------|-------|
| **Linear probing baseline uses UNIv2, but its architecture is trivial (single linear layer)** | The "failure" of complex models to beat it may reflect insufficient training (e.g., early stopping, suboptimal hyperparameters) rather than fundamental architectural redundancy | If complex models are undertrained, their true potential is underestimated, misleading the field toward oversimplification | Re-run top models (TRIPLEX/DeepSpot) with extended epochs, varied learning rates, and architecture-specific hyperparameter sweeps; compare final performance to linear probe | [Paper] [Paper: PDF p. 30] states early stopping (patience=20) and fixed LR (1e-4) were used for all models, but no ablation on training budget is reported |
| **Gene set analysis uses singscore on union of HMHVGs+markers, but many GO terms require broader gene sets** | Restricting to 216 genes likely excludes key members of many GO Biological Process terms, artificially lowering gene-set PCC and masking true functional recovery | Underestimation of model capability for pathway-level inference could discourage development of models targeting functional coherence over spot-level accuracy | Repeat gene-set analysis using full dataset gene universe (where available) or curated pathway databases (e.g., MSigDB Hallmarks) with proper gene-set filtering | [Paper] [Paper: PDF p. 35] specifies gene-set filtering requires ≥5 overlapping genes and ≥10% coverage, but does not report how many GO terms were excluded due to this |
| **Cross-platform test (Visium→Xenium) shows near-zero gap, but Xenium has higher sensitivity** | The apparent success may be confounded by Xenium's higher transcript counts, not true domain alignment; a Visium→Visium test with matched depth would be more revealing | Overstating cross-platform compatibility could lead to premature deployment of Visium-trained models on Xenium, ignoring platform-specific biases | Conduct controlled experiment: downsample Xenium counts to match Visium median, then re-evaluate cross-platform PCC; compare to same-model Visium→Visium performance | [Paper] [Paper: PDF p. 10, 17] attributes Xenium's high PCC to “higher sensitivity and transcript counts”, but no count-matching ablation is shown |

## 14 学到的知识  
- **评估即基建**：一个领域成熟度的标志不是模型数量，而是是否存在像STP-BENCH这样控制变量、多粒度、可复现的基准；它能暴露领域共识（如PFM主导性）与盲区（如跨组织泛化失败）。  
- **形态-转录耦合有谱系**：并非所有基因平等可预测；基质/ECM（COL1A1）、免疫（LAG3）、上皮分化（SFTPC）基因受益于多尺度建模，因其依赖宏观组织架构，而单纯上皮基因（KRT5）局部patch即可较好预测 [Paper] [Paper: PDF p. 13, 19]。  
- **数据质量是共同瓶颈**：Xenium与Visium的PCC差距（0.58 vs. 0.09）贯穿所有评估层级（gene→cell→domain），证明提升ST实验技术比优化vST模型更能释放下游潜力 [Paper] [Paper: PDF p. 10, 14, 19]。  
- **负迁移是现实风险**：简单拼接多癌种数据（BRCA+LUAD+PRAD）导致性能下降，说明组织特异性形态-表达映射强大，未来需组织感知预训练或元学习策略 [Paper] [Paper: PDF p. 18–19]。  
- **鲁棒性可解耦验证**：Cross-institution（ρ=0.86）与cross-tissue（ρ=0.62）的Spearman相关性差异，清晰量化了技术变异与生物变异对模型的挑战程度，为部署提供决策依据 [Figure 5a]。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：STP-BENCH 的“统一编码器+多粒度评估”范式，与计算机视觉中ImageNet之后的评估演进（如WILDS for distribution shift, MMLU for language modeling）逻辑同源，均强调控制变量与任务多样性。  
- **候选连接/方法论连接**：其对“多尺度形态整合”（TRIPLEX/DeepSpot）的验证，呼应了single-cell foundation models中对多分辨率输入（e.g., scGPT’s multi-scale tokenization）与图神经网络（GNN）融合的探索，暗示跨模态对齐需兼顾局部细节与全局上下文。  
- **候选连接/方法论连接**：跨平台泛化分析（Visium↔Xenium）为multi-omics对齐提供了新视角：当模态间分辨率/灵敏度差异巨大时，传统对抗训练或对比学习可能失效，需借鉴spatial transcriptomics中新兴的“平台感知”对齐策略（如Xenium-specific adapter）。  
- **弱连接/方法论连接**：虽未直接使用graph neural networks，但EGGN/SEPAL等模型的图结构设计（window-exemplar-graph, spatial ego-graph）及其在STP-BENCH中的表现（EGGN ranks mid-tier），为用户研究中GNN在spatial omics中的架构选择提供了实证参考。  
- **弱连接/方法论连接**：perturbation prediction与cell state representation的连接较弱：STP-BENCH聚焦稳态组织预测，未涉及扰动（如药物、KO）或动态细胞状态建模，其结论不能直接外推至这些任务。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware Adapter for Cross-Tissue vST  
  **originating limitation/observation**: Inter-cohort scaling shows negative transfer when aggregating BRCA/LUAD/PRAD; cross-tissue generalization gap is large (−0.2 to −0.35 PCC) [Figure 5b, Paper: PDF p. 18].  
  **core hypothesis**: A lightweight, tissue-specific adapter module inserted between PFM encoder and vST head can absorb tissue-specific morphology-transcriptome mapping, enabling positive transfer.  
  **delta from paper**: STP-BENCH treats tissue as a nuisance variable; this idea treats it as a learnable parameter.  
  **initial method**: For each tissue type (BRCA/LUAD/PRAD), train a separate adapter (e.g., 2-layer MLP) that modulates UNIv2 features before feeding to TRIPLEX head; freeze UNIv2 and TRIPLEX weights, only update adapters.  
  **validation**: Train adapters on BRCA+LUAD, test zero-shot on PRAD; compare PCC to vanilla TRIPLEX and naive fine-tuning.  
  **failure modes**: Adapter overfits to source tissues, degrades intra-tissue performance; fails to generalize to unseen tissues (e.g., GBM).  
  **innovation status**: unverified  

- **name**: SSIM-Guided Multi-Scale Fusion  
  **originating limitation/observation**: TRIPLEX/DeepSpot excel on stromal/immune genes by integrating multi-scale context, but current fusion (cross-attention, max-pooling) is heuristic [Paper] [Paper: PDF p. 13, 25–26].  
  **core hypothesis**: Optimizing for spatial structural similarity (SSIM) during fusion, rather than just spot-level PCC, will yield more biologically coherent multi-scale representations.  
  **delta from paper**: STP-BENCH uses SSIM as a *metric*, not as a *training objective*; this idea makes SSIM a direct loss signal.  
  **initial method**: Replace TRIPLEX’s cross-attention fusion with a differentiable SSIM loss term added to main PCC loss; use SSIM computed on 32×32 spatial grids of predicted/true expression.  
  **validation**: Compare gene-wise PCC and SSIM on NCCHE-LUAD-Xenium for stromal genes (COL1A1) vs. epithelial genes (KRT5); assess if SSIM gain transfers to Cell2location PCC.  
  **failure modes**: SSIM optimization degrades spot-level PCC for high-variance genes; increased training instability.  
  **innovation status**: unverified  

- **name**: PFM-Enhanced Exemplar Retrieval for Low-Count Genes  
  **originating limitation/observation**: Marker gene prediction is poor on Visium (PCC≈0.19) due to low counts, but exemplar-guided models (EGN/EGGN) show promise [Figure 2d, Paper: PDF p. 10].  
  **core hypothesis**: Using UNIv2’s rich semantic embeddings for exemplar retrieval (vs. L1 distance on raw features) will improve retrieval of morphologically similar spots, boosting low-count gene prediction.  
  **delta from paper**: EGN already uses PFM for retrieval, but STP-BENCH doesn’t analyze *how* retrieval quality correlates with gene count; this idea proposes a retrieval-quality-aware refinement.  
  **initial method**: In EGN, replace L1-based exemplar selection with cosine similarity in UNIv2 space; add a confidence-weighted aggregation where retrieved exemplars’ contributions are scaled by their similarity score.  
  **validation**: On NCCHE-LUAD-Visium, measure correlation between exemplar similarity score and marker gene PCC; compare refined EGN vs. baseline on low-count (≤1 count) vs. high-count (≥10 counts) genes.  
  **failure modes**: High-similarity exemplars may be morphologically identical but transcriptionally divergent (e.g., same tumor region, different immune infiltration); confidence weighting amplifies bias.  
  **innovation status**: unverified