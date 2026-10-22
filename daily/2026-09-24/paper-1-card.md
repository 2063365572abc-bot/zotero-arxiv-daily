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
| Venue | arXiv | [Paper] [Paper: PDF p. 1] |
| URL | https://arxiv.org/abs/2609.05956 | [Paper meta] |
| PDF URL | https://arxiv.org/pdf/2609.05956 | [Paper meta] |
| Publication date | 2026-09-05 | [Paper meta] |
| Core contribution | First large-scale, standardized benchmark for virtual ST; unifies encoder, evaluation granularity, biological utility metrics, and domain-shift robustness testing | [Paper] [Paper: PDF p. 2–4, Fig. 1] |
| Code & data release | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face (https://huggingface.co/datasets/nexgem/STP-Bench) | [Paper] [Paper: PDF p. 37] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium/Xenium); STP-BENCH-EXTERNAL (185,831 spots, 6 cancer types, cross-institution/tissue/platform) | [Paper] [Paper: PDF p. 4–5, Fig. 1b] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6, Fig. 1c] |
| Primary metric | Pearson Correlation Coefficient (PCC) per gene, averaged across spots → sections → folds | [Paper] [Paper: PDF p. 31, Eq. 1] |

## 02 一句话总结

该论文构建了STP-BENCH——首个面向虚拟空间转录组学（virtual ST）的统一、大规模、多维度系统性基准，覆盖6种癌症、双平台（Visium/Xenium）、超60万spots，并强制统一病理基础模型（PFM）作为图像编码器以解耦架构与表征影响。其核心发现是：多数现有模型在统一PFM下无法超越线性探针基线；基因可预测性存在强普适性天花板，而多尺度架构（如TRIPLEX、DeepSpot）仅对特定生物学程序（如基质重塑、免疫浸润）提供边际增益；平台间数据质量（如Xenium高计数）是下游生物效用的决定性瓶颈。该工作不提出新模型，而是为single-cell foundation models、spatial transcriptomics和multi-omics领域提供可复现、可归因、可迁移的黄金评估标尺。

## 03 研究问题

论文直面虚拟ST领域长期存在的**评估不可比性**问题：当不同研究使用异构数据集、私有训练流程、原生图像编码器及单一平均指标时，报告的“性能提升”究竟源于模型架构创新，还是图像表征能力差异？进一步地，若剥离编码器影响，模型是否真能可靠恢复特定生物学信号（如细胞类型丰度、空间结构域）？其泛化能力在跨机构、跨组织、跨平台等现实场景中如何变化？这些问题阻碍了领域从“工程调参”走向“机制理解”与“临床可部署”。

## 04 研究背景与发展路径

虚拟ST起源于ST实验成本高昂的现实约束，其技术谱系已分化为三支：（1）**回归式**（如ST-Net），将H&E patch到基因表达映射建模为多输出回归；（2）**双模态对齐式**（如BLEEP），借鉴CLIP范式学习形态-表达联合嵌入空间；（3）**生成式**（如STFlow），将预测建模为条件生成任务以捕获分布不确定性。尽管方法演进迅速，但评估始终滞后：Wang et al. [50] 未标准化编码器，导致架构与表征贡献混淆；HEST-1K [51] 虽规模大但仅测试简单回归器，未覆盖主流架构。STP-BENCH并非延续单点改进，而是重构评估范式——它将“公平比较”定义为**控制变量法**：固定PFM（UNIv2）、固定数据划分（患者级CV）、固定下游任务（Cell2location/SpaGCN）、固定指标体系（PCC/SSIM/MAE/ARI），从而将模型比较锚定在架构设计本身。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不公平** | 模型排名随图像编码器剧烈波动（如CFANet从第16跃至第6） | 原有研究混用ImageNet预训练、病理域微调、从头训练等异构编码器，性能差异实为表征能力差异 | [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **生物学效用黑箱** | 高PCC值无法保证下游分析可用（如Cell2location输入需count-scale整数） | 传统评估止步于spot-level相关性，忽略预测结果是否保留空间结构、细胞组成等生物学先验 | [Paper] [Paper: PDF p. 14–15, Fig. 4] |
| **泛化性未经检验** | 模型在内部验证集表现好，但在跨机构/组织/平台时性能断崖式下跌 | 现有基准缺乏外部独立测试集，且未系统设计domain shift场景（如Visium→Xenium） | [Paper] [Paper: PDF p. 17, Fig. 5a–b] |
| **数据质量影响被掩盖** | Xenium数据上所有模型PCC均显著高于Visium（+0.2–0.4），但原因未被归因 | Visium低计数（尤其marker genes）导致信噪比低，而Xenium高灵敏度补偿了domain shift损失 | [Paper] [Paper: PDF p. 10, Fig. 2c–d] |
| **基因级可解释性缺失** | “哪些基因易预测”无共识，模型优势是否集中于特定通路未知 | 以往工作仅报告平均PCC，未进行gene-wise heatmap或gene set scoring分析 | [Paper] [Paper: PDF p. 11–13, Fig. 3] |

## 06 核心思想

论文的核心思想是：**虚拟ST的评估必须从“单一数字竞赛”升维为“多粒度因果归因”**。这体现为三个递进层次：（1）**解耦归因**：通过强制统一PFM（UNIv2），将模型性能差异从“编码器能力”剥离，聚焦“架构设计”本身；（2）**生物学归因**：不仅测spot-level PCC，更测cell-type abundance（Cell2location）、spatial domain（SpaGCN）、gene set activity（singscore），验证预测是否承载真实生物学结构；（3）**鲁棒性归因**：设计Cross-Institution/Tissue/Platform三类domain shift，量化性能衰减是否由技术变异（可控）或生物异质性（本质）主导。最终，STP-BENCH不是静态榜单，而是诊断工具——它揭示了当前技术的真正瓶颈：不是架构复杂度，而是形态-表达映射的固有局限性与数据质量天花板。

## 07 方法总览

STP-BENCH的方法框架是“一基准、三支柱、五维度”：  
- **一基准**：STP-BENCH数据集，含INTERNAL（609k spots, 6 cancers, 2 platforms）与EXTERNAL（186k spots, 6 cancers, 3 generalization axes）；  
- **三支柱**：（i）**统一编码器**：UNIv2作为默认PFM，仅对架构不兼容模型（如M2OST/M2ORT）保留原编码器；（ii）**统一实现**：21模型全部重实现，统一训练超参（lr=1e-4, 200 epochs）、统一CV策略（患者级5-fold）、统一后处理（Softplus输出）；（iii）**统一评估协议**：所有指标（PCC/SSIM/MAE/ARI）计算逻辑严格标准化（[Paper] [Paper: PDF p. 31–32, Eq. 1–2]）；  
- **五维度**：（1）spot-level predictive accuracy（PCC on HMHVG/marker genes）；（2）gene-wise predictability heatmap；（3）gene set scoring（singscore on GO BP terms）；（4）biological granularities（Cell2location/SpaGCN）；（5）robustness & scalability（cross-domain gaps/data scaling curves）。整个流程确保任何性能差异均可追溯至具体设计选择。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **UNIv2 PFM Encoder** | Extracts 1024-d histology embeddings from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability; UNIv2 outperforms ResNet50/CTransPath in all settings | Input: H&E patch; Output: spot-level embedding vector | [Paper] [Paper: PDF p. 10, Fig. 2e]; [Paper] [Paper: PDF p. 25–26, TRIPLEX/DeepSpot implementation] | Severe ranking inversion (e.g., CFANet drops from 6th to 16th) and ~0.1–0.2 PCC drop for most models [Paper] [Paper: PDF p. 9, Fig. 2b] |
| **Gene Set Scoring (singscore)** | Computes per-spot gene set activity score via rank-based averaging of member genes | To bridge gene-level prediction to functional pathway recovery, beyond correlation | Input: predicted/ground-truth expression matrix; Output: spot-by-gene-set activity matrix | [Paper] [Paper: PDF p. 13, Fig. 3c–e]; [Paper] [Paper: PDF p. 35, Online Methods] | Loss of biological interpretability: model may predict genes well but fail to recover coherent pathways (e.g., T Cell Activation) [Paper] [Paper: PDF p. 13] |
| **Cell2location Deconvolution** | Estimates spatial cell-type abundance from expression matrix using scRNA-seq reference | To test if virtual ST preserves cellular composition structure required for clinical interpretation | Input: virtual ST expression (expm1-transformed, integer-clipped); Output: per-spot cell-type abundance vectors | [Paper] [Paper: PDF p. 14–15, Fig. 4a]; [Paper] [Paper: PDF p. 35, Online Methods] | Failure to recover rare populations (plasma/mast cells) would remain undetected without this module [Paper] [Paper: PDF p. 14] |
| **SpaGCN Spatial Clustering** | Identifies spatial domains via graph neural network on expression + coordinates | To verify if predicted expression retains tissue architecture topology (e.g., tumor core vs. stroma) | Input: virtual ST expression (expm1/clipped), spatial coordinates; Output: domain labels per spot | [Paper] [Paper: PDF p. 14–15, Fig. 4b–c]; [Paper] [Paper: PDF p. 36, Online Methods] | Without this, high PCC could mask spatial blurring (e.g., predicted expression smooths boundaries) [Paper] [Paper: PDF p. 14] |
| **Cross-Platform Generalization Test** | Evaluates Visium-trained models on Xenium external data (and vice versa) | To quantify impact of platform-specific technical artifacts (e.g., spot size, sensitivity) on real-world deployment | Input: model trained on Visium INTERNAL; Output: PCC on Xenium EXTERNAL | [Paper] [Paper: PDF p. 17, Fig. 5a–b right]; [Paper] [Paper: PDF p. 17, "cross-platform transfer"] | Would miss the key finding that Xenium's higher sensitivity compensates for domain shift, yielding near-zero generalization gap [Paper] [Paper: PDF p. 17] |

## 09 关键公式与符号

论文明确给出两个核心公式，均用于spot-level评估：  
- **Equation 1 (PCC)**: $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}} $ [Paper] [Paper: PDF p. 31]  
  - 符号：$ \hat{y}_{i,g} $: spot $ i $ 基因 $ g $ 的预测log(1+x)表达；$ y_{i,g} $: 对应真实值；$ \bar{\hat{y}}_g, \bar{y}_g $: 各自在spots上的均值；$ N $: spots数量。  
- **Equation 2 (MAE)**: $ \text{MAE}_{g,s} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}| $ [Paper] [Paper: PDF p. 32]  
  - 符号：同上，衡量log-scale绝对误差。  
- 其他关键指标：SSIM（structural similarity index，[Paper] [Paper: PDF p. 32]）、ARI（Adjusted Rand Index，[Paper] [Paper: PDF p. 36]）、singscore（rank-based gene set scoring，[Paper] [Paper: PDF p. 13, 35]）。  
- 无其他可核验公式；所有模型架构细节见Online Methods，但未以公式形式呈现。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|------------------------------|--------|
| **Fig. 2a (INTERNAL HMHVG)** | Unified PFM reveals true architectural ranking | 21 models, UNIv2 encoder, 7 datasets, HMHVG genes | TRIPLEX/DeepSpot > linear probe (0.394/0.423 vs 0.378); most models < baseline | Multi-scale regression architectures outperform simple baselines under fair comparison | TRIPLEX is universally best (it underperforms on marker genes in some cohorts) | [Paper] [Paper: PDF p. 8, Fig. 2a top] |
| **Fig. 2c-d (Dataset-level stratification)** | Data sparsity, not morphology, drives marker gene gap | NCCHE-LUAD-Xenium (high counts) vs NCCHE-LUAD-Visium (low counts) | Xenium: PCC=0.579 (marker); Visium: PCC=0.191; Kruskal-Wallis p<1e-12 | Low transcript counts—not morphological uncoupling—limit marker gene prediction | All marker genes are inherently unpredictable from H&E | [Paper] [Paper: PDF p. 10, Fig. 2c–d] |
| **Fig. 3a (Gene-wise heatmap)** | Gene predictability is model-agnostic | 20 models, union of HMHVG+marker genes, INTERNAL | Smooth separation: genes easy/hard for one model are easy/hard for all | Existence of universal gene-level predictability ceiling tied to morphology-expression coupling | This ceiling is fixed; no architecture can overcome it for low-predictability genes | [Paper] [Paper: PDF p. 11, Fig. 3a] |
| **Fig. 4a (Cell2location)** | Virtual ST preserves cell-type composition structure | 6 models on 3 cohorts, Cell2location with matched scRNA-seq refs | TRIPLEX/DeepSpot achieve highest PCC for epithelial/T cells; plasma/mast cells low | Top-performing models retain coarse biological structure; rare populations remain challenging | Virtual ST enables clinical-grade deconvolution (not validated on clinical endpoints) | [Paper] [Paper: PDF p. 14–15, Fig. 4a] |
| **Fig. 5a (Cross-Tissue generalization)** | Biological heterogeneity dominates technical variation | Models trained on LUAD, tested on BRCA/PDAC/etc. | Spearman ρ=0.876 (p=1.87e-6) but generalization gap = -0.2 to -0.35 | Internal rankings generalize across tissues, but absolute performance drops sharply | Cross-tissue transfer is feasible with minor fine-tuning (gap too large for minor tuning) | [Paper] [Paper: PDF p. 17, Fig. 5a center] |

## 11 对结论的正确理解

论文结论必须严格限定于其证据范围：（1）“多数模型不超越线性探针”仅在**UNIv2编码器+HMHVG/marker基因+spot-level PCC**条件下成立，不否定其在其他编码器、其他基因集或生成式任务中的价值；（2）“基因预测天花板”指**200 HMHVG + 16 marker genes**的集合，未覆盖低表达基因或非GO BP通路；（3）“Xenium优势”源于其**更高计数**（mean counts=72.3 vs Visium’s 0.9 for markers），而非平台本身优越，若Visium数据质量提升，结论可能逆转；（4）“TRIPLEX/DeepSpot最优”是**综合PCC/gene set/cell-type/domain多维度**的观察，但其在Visium上对marker基因的PCC（0.191）仍远低于Xenium（0.579），说明平台依赖性是硬约束；（5）“负向迁移”指**inter-cohort scaling中BRCA+LUAD+PRAD训练导致BRCA测试性能下降**，但未证明所有多癌种训练均失败，可能因训练策略不当而非本质不可行。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | Only 6 cancer types (LUAD, BRCA, etc.) and 2 platforms (Visium/Xenium); no normal tissue or rare cancers | Extend benchmark to additional tumor types, tissue contexts, and emerging sequencing platforms (e.g., Stereo-seq) | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analysis limited to 200 HMHVGs and 16 TME markers; systematic investigation of lowly expressed or functionally diverse genes not performed | Systematic investigation of low-expression genes and broader functional gene sets | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluation performed at spot-level (aggregated multi-cell signals); no single-cell ST or virtual ST models evaluated | Extend principles to single-cell resolution as scST datasets and models become available | [Paper] [Paper: PDF p. 20] |
| **Encoder compatibility constraints** | 5 models (OmiCLIP, M2ORT, etc.) retained native encoders due to architectural incompatibility with PFM drop-in | Develop more modular, encoder-agnostic virtual ST architectures | [Paper] [Paper: PDF p. 9, 22–23] |
| **Downstream tool dependency** | Cell2location/SpaGCN performance depends on their own assumptions (e.g., scRNA-seq reference quality) | Integrate multiple deconvolution/clustering tools to assess robustness | [Paper] [Paper: PDF p. 35–36, Online Methods] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|----------------|--------|
| **UNIv2 as sole PFM may overfit to its pretraining bias** | UNIv2 was trained on large WSI collections, potentially overemphasizing global patterns while underrepresenting rare morphologies (e.g., necrosis, treatment effect). Other PFMs (Virchow2, H-Optimus1) show similar but not identical rankings [Paper] [Paper: PDF p. 17] | If UNIv2’s bias aligns fortuitously with ST prediction, conclusions about "architecture irrelevance" may not generalize to other PFMs or clinical edge cases | Re-run full benchmark with Virchow2 as primary PFM; compare ranking stability and gene-wise predictability shifts | [Paper] [Paper: PDF p. 17, Extended Data Fig. 5–6] |
| **singscore’s rank-based approach discards magnitude information** | singscore computes gene set scores by averaging ranks, ignoring absolute expression levels. A model could perfectly rank genes but mispredict magnitudes, yielding high singscore but poor biological utility | Downstream tasks like drug response prediction depend on absolute expression, not just rank order | Replace singscore with magnitude-aware metrics (e.g., GSVA, AUCell) and re-evaluate gene set PCC | [Paper] [Paper: PDF p. 13, 35] |
| **Cross-platform "negligible loss" conflates directionality** | Fig. 5b (right) shows small gaps, but Fig. 5a (right) reveals Visium→Xenium often gains while Xenium→Visium loses. The "negligible" label masks asymmetry | For clinical deployment, bidirectional transfer matters; a model trained on research-grade Xenium may fail on routine Visium | Report separate gaps for Visium→Xenium and Xenium→Visium directions in all cohorts | [Paper] [Paper: PDF p. 17] |
| **Inter-cohort negative transfer may stem from class imbalance, not tissue specificity** | When adding LUAD/PRAD to BRCA training, BRCA spots become minority. Performance drop could be due to optimization failure, not inherent tissue conflict | If imbalance is the cause, reweighting or oversampling BRCA spots could rescue performance | Train inter-cohort models with BRCA spot oversampling or class-balanced sampling; compare to original | [Paper] [Paper: PDF p. 18, Fig. 5d] |
| **Cell2location evaluation excludes samples with max PCC < 0.1** | This exclusion (stated in Online Methods [Paper] [Paper: PDF p. 35]) removes low-performance cases, potentially inflating reported correlations | Clinical samples often have low signal; excluding them biases assessment toward "easy" cases | Report full distribution of Cell2location PCC, including excluded samples, to quantify failure rate | [Paper] [Paper: PDF p. 35, Online Methods] |

## 14 学到的知识

- **评估即设计**：STP-BENCH证明，严谨的benchmark不是事后验证，而是前置设计——它要求明确定义控制变量（如UNIv2）、多维指标（PCC+ARI+singscore）、现实挑战（cross-tissue）、以及失败模式（negative transfer）。这对用户设计single-cell foundation model benchmark极具启发：必须定义“什么是公平比较”，例如统一scRNA-seq pretraining corpus、统一cell type ontology、统一batch correction强度。  
- **数据质量是天花板**：Xenium的高计数直接拉升所有模型PCC 0.2–0.4，说明在virtual ST中，“better model”常是“better data”的代理。这对用户perturbation prediction研究警示：若扰动响应信号微弱（如CRISPR KO后log2FC<0.5），再优架构也难突破信噪比瓶颈，应优先优化湿实验检测灵敏度。  
- **多尺度 ≠ 多参数**：TRIPLEX/DeepSpot胜出非因参数量大，而因显式建模局部（spot）、邻域（3×3 grid）、全局（WSI）形态上下文。这对用户graph neural networks研究提示：在spatial transcriptomics GNN中，应设计多跳邻居聚合（local）、跨区域图卷积（regional）、全图池化（global）三级结构，而非堆叠层数。  
- **生物学效用需闭环验证**：仅PCC高不等于可用；必须通过Cell2location（细胞组成）、SpaGCN（空间结构）、singscore（通路活性）三重验证。这对用户cross-modal alignment研究意味着：alignment loss最小化不保证下游任务成功，必须设计task-specific validation modules。  
- **负向迁移是警钟**：简单拼接多癌种数据损害性能，暗示morphology-to-expression mapping高度组织特异。这对用户multi-omics研究启示：跨组织整合不能靠数据拼接，需引入tissue-aware adapters或domain-specific bottlenecks。

## 15 与既有知识的连接

- **候选连接/方法论连接**：与single-cell foundation models（如scGPT、CellLM）的连接在于**评估范式迁移**——STP-BENCH的“统一encoder+多粒度验证”可直接迁移到scRNA-seq foundation model benchmark中，例如：固定scGPT作为encoder，评估下游cell type annotation、trajectory inference、drug response prediction。  
- **候选连接/方法论连接**：与spatial transcriptomics的连接在于**数据构造逻辑**——STP-BENCH将Xenium单分子坐标binning为Visium-scale pseudo-spots（[Paper] [Paper: PDF p. 22]），此策略可复用于用户将MERFISH/seqFISH+数据对齐至Visium坐标系，构建跨模态训练集。  
- **候选连接/方法论连接**：与graph neural networks的连接在于**架构启示**——SEPAL（[Paper] [Paper: PDF p. 24]）的“local prediction + GNN residual correction”范式，可启发用户设计GNN for perturbation prediction：以基因共表达图作骨架，用GNN学习扰动传播残差，替代纯MLP。  
- **弱连接/方法论连接**：与biomedical AI的连接限于**鲁棒性测试框架**——STP-BENCH的cross-institution/tissue/platform三轴泛化测试，可抽象为通用医疗AI鲁棒性协议，但未涉及临床终点（如生存预测），故非直接临床连接。  
- **弱连接/方法论连接**：与cell state representation的连接在于**评价粒度**——STP-BENCH的gene set scoring（singscore）本质上是cell state proxy，但未像cellxgene那样定义离散state，故属弱连接。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware Adapter for Multi-Cancer Virtual ST  
  **originating limitation/observation**: Inter-cohort scaling causes negative transfer because morphology-expression mapping is tissue-specific [Paper] [Paper: PDF p. 18, Fig. 5d]  
  **core hypothesis**: Injecting lightweight, tissue-specific adapters into a shared backbone (e.g., TRIPLEX) will enable positive transfer across cancers without sacrificing per-tissue performance.  
  **delta from paper**: STP-BENCH uses monolithic models per dataset; this adds learnable tissue tokens and adapter layers.  
  **initial method**: For each cancer type, add a 64-d tissue token concatenated to PFM embedding; insert LoRA adapters (r=4, α=8) into TRIPLEX’s fusion encoder. Train end-to-end on BRCA+LUAD+PRAD with tissue-token gating.  
  **validation**: Compare PCC on BRCA test set vs. STP-BENCH’s BRCA-only and BRCA+LUAD+PRAD baselines; ablate tissue tokens/adapters.  
  **failure modes**: Adapter overfitting to tissue noise; token collapse (all cancers share same token); increased inference latency.  
  **innovation status**: unverified  

- **name**: SingScore-Guided Gene Selection for Perturbation Prediction  
  **originating limitation/observation**: singscore reveals that immune/stromal genes benefit most from multi-scale reasoning [Paper] [Paper: PDF p. 13, Fig. 3e], suggesting gene sets—not individual genes—are the meaningful units for morphology-driven prediction.  
  **core hypothesis**: Selecting genes based on their singscore predictability (rather than variance/mean) will improve perturbation response prediction from histology.  
  **delta from paper**: STP-BENCH uses HMHVG/marker genes; this proposes a new gene selection criterion grounded in functional coherence.  
  **initial method**: On LUAD-Xenium, compute singscore PCC for all genes; select top-100 high-singscore genes. Train perturbation classifier (e.g., CRISPR KO vs control) using only these genes’ expression predicted from H&E.  
  **validation**: Compare AUROC on held-out perturbations vs. HMHVG-selected and random gene sets.  
  **failure modes**: singscore’s rank-based nature loses magnitude info critical for perturbation effect size; low-coverage genes excluded despite biological relevance.  
  **innovation status**: unverified  

- **name**: SSIM-Regularized Diffusion for Spatially Coherent Virtual ST  
  **originating limitation/observation**: SSIM correlates with PCC but captures spatial structure [Paper] [Paper: PDF p. 11, Extended Data Fig. 3]; yet generative models (STFlow/Stem) are trained only on MSE/KL, not structural loss.  
  **core hypothesis**: Adding SSIM as an auxiliary loss during diffusion training will improve spatial domain identification (ARI) without harming spot-level PCC.  
  **delta from paper**: STP-BENCH evaluates SSIM post-hoc; this integrates it into training objective.  
  **initial method**: Modify STFlow’s denoising loss: $ \mathcal{L} = \lambda_{\text{MSE}} \mathcal{L}_{\text{MSE}} + \lambda_{\text{SSIM}} \mathcal{L}_{\text{SSIM}} $, where $ \mathcal{L}_{\text{SSIM}} $ computed on 2D expression grids. Tune λ on NCCHE-LUAD-Xenium.  
  **validation**: Measure ARI on Fig. 4b-c and PCC on Fig. 2c; compare to vanilla STFlow.  
  **failure modes**: SSIM optimization may conflict with MSE, causing blurry predictions; GPU memory overflow from grid computation.  
  **innovation status**: unverified  

- **name**: Cross-Platform Calibration Layer for Visium→Xenium Transfer  
  **originating limitation/observation**: Cross-platform transfer shows negligible gap, but analysis is asymmetric and ignores quantification bias [Paper] [Paper: PDF p. 17]  
  **core hypothesis**: A lightweight calibration layer (e.g., affine transform) applied to Visium-predicted expression can correct for platform-specific biases, enabling zero-shot Xenium deployment.  
  **delta from paper**: STP-BENCH treats platforms as separate domains; this proposes explicit bias correction.  
  **initial method**: Train a 2-layer MLP on paired Visium/Xenium spots (same tissue) to map Visium-predicted expression → Xenium ground truth. Apply to TRIPLEX outputs.  
  **validation**: Compare PCC/ARI on Xenium test set before/after calibration; ablate MLP layers.  
  **failure modes**: Requires paired Visium/Xenium data (rare); calibration may overfit to specific cancer types.  
  **innovation status**: unverified