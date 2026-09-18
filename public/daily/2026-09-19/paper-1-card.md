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
| Core task | Virtual spatial transcriptomics (virtual ST): predicting spot-level gene expression from H&E image patches | [Paper] [Paper: PDF p. 2, 3] |
| Benchmark name | STP-BENCH, comprising STP-BENCH-INTERNAL (609,024 spots) and STP-BENCH-EXTERNAL (185,831 spots) | [Paper] [Paper: PDF p. 4, Fig. 1b] |
| Cancer types | LUAD, BRCA, PRAD, CCRCC, GBM, PDAC (6 total) | [Paper] [Paper: PDF p. 4, 21] |
| ST platforms | 10x Genomics Visium and Xenium | [Paper] [Paper: PDF p. 4, Fig. 1b] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval-based, 3 generative-based | [Paper] [Paper: PDF p. 6, Fig. 1c] |
| Key metrics | Pearson Correlation Coefficient (PCC), Mean Absolute Error (MAE), Structural Similarity Index Measure (SSIM), Adjusted Rand Index (ARI), singscore-based gene set PCC | [Paper] [Paper: PDF p. 7, 31–32, 35–36] |
| Patch encoder standardization | UNIv2 used as unified pathology foundation model (PFM) where architecturally compatible; exceptions: OmiCLIP, M2ORT, M2OST, HistoSPACE, ST-Net | [Paper] [Paper: PDF p. 7–9, 22–23] |

## 02 一句话总结  
该论文提出了STP-BENCH——首个面向virtual ST任务的、统一且系统化的基准框架，覆盖6种癌症、双平台（Visium/Xenium）、超80万spot的大规模数据，并强制统一使用UNIv2等病理基础模型作为图像编码器以解耦架构与表征能力。其核心发现是：多数现有模型在统一编码下无法超越线性探针基线，模型性能排序被图像编码器选择显著重构；基因可预测性存在普适性天花板，而多尺度架构（如TRIPLEX、DeepSpot）仅对特定生物学程序（如ECM重塑、免疫空间组织）带来边际增益。该工作不构建新模型，而是通过标准化评估揭示了当前领域方法论的根本偏差与数据质量瓶颈。

## 03 研究问题  
论文直面virtual ST领域长期存在的**评估不可比性**问题：不同研究采用异构小数据集、不一致训练/推理流程、各自原生图像编码器，导致报告的“架构优势”实为编码器差异的混杂效应。由此引出三个递进问题：（1）当剥离图像编码器变量后，现有21种模型的真实架构优劣排序是否发生系统性偏移？（2）哪些基因/基因集能稳定地从形态学中恢复？这种可预测性是否具有跨模型一致性？（3）spot-level预测精度能否可靠传导至下游生物学分析（如细胞类型反卷积、空间域识别）？这些问题共同指向一个更深层目标：建立可复现、可解耦、多粒度的评估范式，以区分“真架构创新”与“编码器红利”。

## 04 研究背景与发展路径  
virtual ST起源于ST实验成本高昂的现实约束，其技术谱系已分化为三支：（1）**回归式**（如ST-Net），将H&E patch直接映射为基因表达向量；（2）**双模态对齐式**（如BLEEP），借鉴CLIP范式学习形态-表达联合嵌入空间；（3）**生成式**（如STFlow），建模条件分布以支持不确定性估计。尽管模型演进迅速，但评估始终滞后：Wang et al. [50] 保留各模型原生编码器，混淆架构与编码器贡献；HEST-1K [51] 虽具大规模数据，却仅用简单回归器测试PFM嵌入与基因的相关性，未评估完整模型架构。STP-BENCH正是对这一断裂的修复——它不延续“单点突破”路径，而是构建基础设施级基准，强制统一编码器、统一实现、统一评估协议，使比较回归到模型设计本身。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不可比性** | 模型排名随所用图像编码器剧烈波动（如CFANet从第16跃至第6） | 各研究使用不同预训练域、规模、范式的编码器（ImageNet vs. pathology WSIs），性能差异可能源于特征提取而非模型设计 | [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **评价维度单一** | 仅报告平均PCC，忽略基因特异性、生物学功能可解释性、下游任务实用性 | 早期工作聚焦aggregate accuracy，忽视virtual ST需服务于具体生物学推断（如TME解析） | [Paper] [Paper: PDF p. 3, 4] |
| **数据质量影响被掩盖** | Marker基因预测性能远低于HMHVG（PCC≈0.2 vs. 0.4），且Visium数据上性能普遍更低 | 数据稀疏性（低计数）主导预测上限，而非形态-表达解耦；Xenium高灵敏度数据可显著提升所有模型性能 | [Paper] [Paper: PDF p. 9–10, Fig. 2c-d] |
| **泛化性验证缺失** | 缺乏跨机构、跨组织、跨平台的系统性鲁棒性测试 | 现有评估多限于同源数据内交叉验证，无法反映真实临床部署中的域偏移挑战 | [Paper] [Paper: PDF p. 17, Fig. 5] |
| **缩放规律不明** | 增加训练数据量（intra-cohort）收益递减，跨癌种聚合（inter-cohort）甚至导致负迁移 | 形态-表达映射高度组织特异性，简单数据堆砌无法泛化，亟需组织感知的训练策略 | [Paper] [Paper: PDF p. 18, Fig. 5c-d] |

## 06 核心思想  
STP-BENCH的核心思想是**将评估本身升格为第一性问题**：不是问“哪个模型最好”，而是问“在控制关键混杂变量（尤其是图像编码器）后，我们能可靠地测量什么？”。其方法论基石是**三重解耦**：（1）**编码器-架构解耦**：用UNIv2等PFM统一替换兼容模型的图像编码器，使性能差异归因于模型结构本身；（2）**精度-效用解耦**：不仅测spot-level PCC，更延伸至cell-type deconvolution（Cell2location）和spatial domain identification（SpaGCN）等下游任务；（3）**数据-模型解耦**：通过跨平台（Visium→Xenium）与跨组织（LUAD→BRCA）测试，分离模型固有鲁棒性与数据质量依赖性。这一思想将benchmark从“排行榜”转变为“诊断工具”。

## 07 方法总览  
STP-BENCH方法论由三大支柱构成：（1）**数据层**：构建STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与STP-BENCH-EXTERNAL（186k spots, 6 cancers, 4 sources），严格分离训练/测试集，并对Visium/Xenium数据实施统一patch裁剪与pseudo-spot pooling [Paper] [Paper: PDF p. 4–6, 21–22]；（2）**模型层**：重实现21个代表模型，按架构家族分组（regression/bi-retrieval/generative），强制UNIv2编码器（除非架构不兼容），并统一训练超参（lr=1e-4, 200 epochs, patient-level CV）[Paper] [Paper: PDF p. 6–7, 22–28]；（3）**评估层**：实施四维评测——① spot-level PCC/MAE/SSIM；② gene-wise & gene-set-wise PCC（via singscore）；③ downstream utility（Cell2location ARI, SpaGCN ARI）；④ robustness/scalability（cross-institution/tissue/platform, intra/inter-cohort scaling）[Paper] [Paper: PDF p. 7, 11–18, 31–36]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **UNIv2-standardized patch encoder** | Extracts morphology-aware embeddings from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability; UNIv2 outperforms ResNet50/CTransPath on HMHVG+marker genes | Input: H&E patch → Output: d-dim embedding (d=1024) | [Paper] [Paper: PDF p. 9–10, Fig. 2e] shows UNIv2/Virchow2/H-Optimus1 yield highest & comparable performance; ResNet50 lowest | Removal would revert to prior unfair comparisons; models like CFANet would drop from rank 6 to 16 [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **Multi-granularity evaluation pipeline** | Computes PCC at gene, gene-set, cell-type abundance, and spatial domain levels | To test whether spot-level accuracy translates to biologically meaningful utility; reveals data quality bottlenecks | Input: predicted & ground-truth expression matrices → Output: gene-PCC, gene-set-PCC (singscore), Cell2location PCC per cell type, SpaGCN ARI | [Paper] [Paper: PDF p. 11–15, Fig. 3–4] shows TRIPLEX/DeepSpot top-ranked across all granularities; performance gap Xenium > Visium consistent across levels | Removal would mask that low Visium counts degrade *all* downstream tasks equally, conflating model failure with data limitation [Paper] [Paper: PDF p. 14, 19] |
| **Cross-domain generalization tester** | Quantifies performance drop under cross-institution (same cancer), cross-tissue (different cancer), cross-platform (Visium→Xenium) shifts | To assess real-world deployability; reveals tissue-specificity as dominant barrier vs. technical batch effects | Input: model trained on INTERNAL → tested on EXTERNAL subsets → Output: internal vs. external PCC, generalization gap (ΔPCC), Spearman ρ of ranking preservation | [Paper] [Paper: PDF p. 17, Fig. 5a-b] shows ρ>0.86 for cross-institution/tissue, but ΔPCC = -0.2 to -0.35 for cross-tissue; cross-platform shows negligible loss | Removal would hide that cross-tissue generalization is the hardest challenge, misguiding development toward technical robustness over biological generalization [Paper] [Paper: PDF p. 19] |
| **Intra-/Inter-cohort scaling analyzer** | Trains models on increasing subsets (33%/66%/100% spots) or merged cohorts (BRCA→+LUAD→+PRAD) | To probe data efficiency and multi-tissue learning strategies; tests if “more data” always helps | Input: varying training sets → Output: PCC on fixed test set (Massey-BRCA) | [Paper] [Paper: PDF p. 18, Fig. 5c-d] shows intra-cohort scaling yields marginal gains; inter-cohort scaling causes negative transfer (performance ↓ with added tissues) | Removal would obscure that simple data aggregation harms performance, missing the need for domain-adaptive or tissue-aware architectures [Paper] [Paper: PDF p. 19] |

## 09 关键公式与符号  
论文未提出新公式，但明确定义并使用了三个核心评估指标：  
- **Pearson Correlation Coefficient (PCC)**: $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2} $ [Paper] [Paper: PDF p. 31, Eq. 1]，其中 $\hat{y}_{i,g}, y_{i,g}$ 为spot $i$、gene $g$ 的预测与真实log-normalized表达值。  
- **Mean Absolute Error (MAE)**: $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^{N} |\hat{y}_{i,g} - y_{i,g}| $ [Paper] [Paper: PDF p. 32, Eq. 2]，在log(1+x)-transformed空间计算。  
- **Adjusted Rand Index (ARI)**: 用于量化SpaGCN聚类结果与ground-truth空间域标注的一致性 [Paper] [Paper: PDF p. 36]。  
**关键符号**: HMHVG (high-mean highly-variable genes), TME (tumor microenvironment), PFM (pathology foundation model), SSIM (Structural Similarity Index Measure), singscore (gene set activity scoring method)。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|-------------------------|-------------------------------|--------|
| **UNIv2 vs native encoders** | Unified encoding reorders model rankings | Compare CFANet/HisToGene/BrSTNet using native encoder vs UNIv2 on STP-BENCH-INTERNAL (HMHVG+marker) | CFANet jumps from rank 16 to 6; BrSTNet improves significantly | Encoder choice dominates reported "architectural gains"; prior comparisons are confounded | UNIv2 is universally optimal — CTransPath shows only marginal gain, ResNet50 worst [Paper] [Paper: PDF p. 10, Fig. 2e] | [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **Gene expression level stratification** | Prediction accuracy depends on basal transcript count | Stratify genes into 5 quantiles by mean expression; compute PCC per quantile on NCCHE-LUAD-Xenium/Visium | Strong correlation: higher expression → higher PCC (p<1e-12); Xenium (mean=52.1) outperforms Visium (mean=9.2) | Data sparsity, not morphological uncoupling, is primary bottleneck for marker genes | All genes are equally predictable given sufficient depth — low-expression genes remain hard even in Xenium [Paper] [Paper: PDF p. 10, Fig. 2c-d] | [Paper] [Paper: PDF p. 10, Fig. 2c-d] |
| **Gene-wise concordance analysis** | Predictability is gene-intrinsic, not model-dependent | Compute PCC per gene across 20 models; cluster genes by predictability | Smooth separation: genes easy/hard for one model are easy/hard for all; curved boundary shows architecture shifts threshold | Universal gene-level ceiling exists; morphology-expression correlation governs limit, not architecture | Architecture can overcome the ceiling — no model achieves PCC>0.7 for low-predictability genes [Paper] [Paper: PDF p. 11, Fig. 3a; p. 38, Extended Data Fig. 1] | [Paper] [Paper: PDF p. 11, Fig. 3a] |
| **Downstream utility (Cell2location)** | Spot-level PCC predicts cell-type deconvolution fidelity | Apply Cell2location to predicted profiles; correlate inferred abundances with ground-truth | TRIPLEX/DeepSpot top-ranked for epithelial/T-cell abundance; rare cells (plasma/mast) poorly recovered | Gene-level superiority translates to coarser biological inference; data quality (Xenium > Visium) is shared bottleneck | Virtual ST enables rare cell detection — plasma/mast cell PCC remains low across all models [Paper] [Paper: PDF p. 14, Fig. 4a] | [Paper] [Paper: PDF p. 14, Fig. 4a] |
| **Cross-tissue generalization** | Models fail to generalize across anatomical sites | Train on LUAD, test on BRCA (cross-tissue); compare to cross-institution (same cancer) | Cross-tissue ΔPCC ≈ -0.25 to -0.35; cross-institution ΔPCC ≈ -0.05 to -0.10 | Biological heterogeneity is harder barrier than technical batch effects; tissue-specificity is fundamental | Cross-tissue transfer is feasible with more data — inter-cohort scaling worsens performance [Paper] [Paper: PDF p. 18, Fig. 5d] | [Paper] [Paper: PDF p. 17, Fig. 5b] |

## 11 对结论的正确理解  
论文结论必须置于其**严格限定的评估框架**内理解：（1）“多数模型未超越线性探针”仅指在UNIv2编码器下对HMHVG+marker基因的spot-level PCC，不否定其在其他任务（如生成不确定性）或数据（如全转录组）上的价值；（2）“基因可预测性具普适性”指在STP-BENCH的6癌种2平台数据上观察到的跨模型一致性，不意味着该规律适用于所有基因（如低表达基因未系统评估）或所有组织（如非肿瘤组织未覆盖）；（3）“跨组织泛化差”是基于Visium→Xenium等特定转移场景的实证，不等于否定多组织预训练的价值，而恰恰提示需更精细的组织感知机制。所有结论均锚定在STP-BENCH的规模、组成与协议上，不可外推至未覆盖的平台（如Slide-seq）、分辨率（如single-cell ST）或任务（如perturbation prediction）。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 ST platforms | Extend benchmark to additional tumor types, normal tissues, and emerging platforms (e.g., Stereo-seq, DBiT-seq) | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focused on HMHVGs (200 genes) and 16 TME markers | Systematically investigate lowly expressed genes and functionally diverse gene families beyond current panel | [Paper] [Paper: PDF p. 20] |
| **Spot-level granularity** | Evaluation performed at spot-level (multi-cell aggregates) | Extend principles to single-cell ST datasets and virtual ST models as they become available | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|--------|
| **UNIv2 standardization may over-correct** | Forcing UNIv2 onto architectures designed for specific encoders (e.g., M2OST’s multi-scale streams) discards their intended inductive bias, potentially penalizing valid design choices | Risks misclassifying architecturally sound models as inferior due to implementation mismatch, not intrinsic weakness | Re-implement M2OST with UNIv2-derived multi-scale features (e.g., via feature pyramid) and compare to original; assess if performance gap narrows | [Paper] [Paper: PDF p. 28, M2OST section] states multi-scale input is "structurally incompatible" with single PFM, but no ablation tests this claim |
| **"Negative transfer" in inter-cohort scaling may reflect label misalignment** | Adding LUAD/PRAD to BRCA training may introduce systematic biases if TME marker definitions or cell-type signatures differ across cancers, not just tissue morphology | Could misattribute failure to tissue-specificity when it stems from inconsistent biological annotation, undermining guidance for multi-tissue training | Re-run inter-cohort scaling using harmonized cell-type signatures (e.g., pan-cancer scRNA ref) and standardized marker panels; measure if negative transfer persists | [Paper] [Paper: PDF p. 35] uses LuCA for LUAD and HBCA for BRCA — different refs may encode inconsistent biology |
| **Downstream utility metrics conflate prediction error with tool limitations** | Low Cell2location PCC for rare cells (plasma/mast) may reflect Cell2location’s inherent sensitivity limits on sparse signals, not virtual ST’s failure | Overestimates virtual ST’s inadequacy for rare populations, potentially discouraging development for clinically critical minority cell types | Benchmark same predicted profiles with alternative deconvolution tools (e.g., SPOTlight, RCTD) and single-cell resolution methods (e.g., Tangram); compare PCC distributions | [Paper] [Paper: PDF p. 35] uses only Cell2location, with no validation against other tools |

## 14 学到的知识  
- **评估即设计**：构建STP-BENCH的过程本身揭示了virtual ST的核心挑战——不是模型容量不足，而是评估协议缺陷导致信号淹没。标准化编码器、多粒度指标、域偏移测试是任何严肃benchmark的必备要素。  
- **数据质量是隐性天花板**：Xenium的高灵敏度使所有模型PCC提升0.2+，证明算法进步常被数据瓶颈掩盖；未来工作应优先优化ST数据生成与预处理。  
- **多尺度≠全局**：TRIPLEX/DeepSpot的优势集中于ECM/immune基因，这些依赖宏观组织模式（纤维化梯度、淋巴聚集），证实局部patch不足以捕获长程形态依赖。  
- **组织特异性是硬约束**：跨组织泛化失败程度远超跨机构，暗示morphology-to-expression mapping是器官级现象，通用模型需显式建模组织上下文。  
- **缩放悖论**：增加同质数据（intra-cohort）收益饱和，而增加异质数据（inter-cohort）反而有害，表明virtual ST需要的是“组织感知”的数据融合，而非简单拼接。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：STP-BENCH的“编码器-架构解耦”范式与NLP中BERT-large vs RoBERTa的公平比较逻辑一致，均强调控制预训练变量；其多粒度评估（spot→gene set→cell type→domain）呼应了生物医学AI中从分子到组织的层级验证需求。  
- **候选连接/方法论连接**：跨平台（Visium→Xenium）鲁棒性测试与multi-omics整合中处理技术批次效应（如scRNA vs snRNA）的方法论相通，均需区分技术噪声与生物学信号。  
- **弱连接/方法论连接**：虽未直接使用graph neural networks，但EGGN/SEPAL等模型的图结构设计（window-exemplar-graph, spatial ego-graph）为用户研究中构建cell-graph或tissue-graph提供了可复用的邻域聚合范式。  
- **弱连接/方法论连接**：singscore基因集评分与用户关注的cross-modal alignment任务共享目标——将低维预测（virtual ST）映射到高维功能空间（GO terms），其rank-based策略可启发对齐损失的设计。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware Encoder Adapter (TAEA)  
  **originating limitation/observation**: Cross-tissue generalization fails catastrophically (ΔPCC ≈ -0.3) while cross-institution succeeds, indicating encoder representations lack tissue context [Paper] [Paper: PDF p. 17, Fig. 5b].  
  **core hypothesis**: Injecting lightweight, tissue-specific adapters into a frozen PFM backbone will preserve universal morphology features while enabling tissue-adaptive decoding, improving cross-tissue transfer without sacrificing within-tissue performance.  
  **delta from paper**: STP-BENCH uses *fixed* UNIv2; TAEA introduces *learnable*, tissue-conditioned adapter modules (e.g., LoRA layers) on top of UNIv2, trained end-to-end with virtual ST loss.  
  **initial method**: For each cancer type, train a 2-layer adapter (dim=64) on UNIv2 CLS token; use tissue ID embedding to gate adapter weights. Evaluate on STP-BENCH cross-tissue transfer (LUAD→BRCA).  
  **validation**: Compare ΔPCC reduction vs. baseline UNIv2; ensure within-tissue PCC on LUAD/BRCA remains ≥ UNIv2 baseline.  
  **failure modes**: Adapter overfits to tissue ID, harming unseen tissues; adapter collapses to identity, no gain.  
  **innovation status**: unverified  

- **name**: Sparse-Expression Imputation Pretraining (SEIP)  
  **originating limitation/observation**: Marker gene prediction fails on Visium (PCC≈0.2) due to low counts, not morphology; STP-BENCH confirms data sparsity is primary bottleneck [Paper] [Paper: PDF p. 10, Fig. 2d].  
  **core hypothesis**: Pretraining a virtual ST model on synthetic low-count data (e.g., Poisson-sampled high-count Xenium) will teach it to recover signal from noise, boosting Visium performance without requiring new wet-lab data.  
  **delta from paper**: STP-BENCH treats data as fixed; SEIP modifies the *pretraining objective* to explicitly target sparsity robustness.  
  **initial method**: Take Xenium data (high-count), downsample to Visium-like depth (Poisson λ=5–10), train TRIPLEX on this synthetic low-count data, then fine-tune on real Visium.  
  **validation**: Test on STP-BENCH-INTERNAL Visium datasets (NCCHE-LUAD-Visium, WUSTL-BRCA-Visium); target PCC gain >0.05 on marker genes vs. standard TRIPLEX.  
  **failure modes**: Model learns downsampling artifacts, not biological signal; pretraining hurts high-count performance.  
  **innovation status**: unverified  

- **name**: Gene-Set Guided Contrastive Learning (GSGCL)  
  **originating limitation/observation**: Bi-modal models (BLEEP/STco) underperform on immune gene sets despite strong spot-level PCC; their contrastive loss optimizes per-spot alignment, not functional program coherence [Paper] [Paper: PDF p. 13, Fig. 3e].  
  **core hypothesis**: Augmenting contrastive loss with a gene-set-level alignment term—forcing embeddings of spots with similar GO term activity to cluster—will improve recovery of biologically coherent programs.  
  **delta from paper**: STP-BENCH evaluates gene-set recovery post-hoc; GSGCL integrates gene-set structure *into training*.  
  **initial method**: For BLEEP, compute singscore for top 50 GO terms per spot; add triplet loss pulling together spots with high similarity in top-k gene-set scores, pushing apart dissimilar ones.  
  **validation**: On STP-BENCH-INTERNAL, measure PCC gain on immune-related gene sets (e.g., "T Cell Activation") vs. baseline BLEEP; ensure spot-level PCC doesn’t degrade.  
  **failure modes**: Gene-set scores are noisy, destabilizing training; loss dominates, collapsing spot embeddings.  
  **innovation status**: unverified