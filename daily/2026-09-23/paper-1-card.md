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
| Venue | arXiv (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-05 | [Paper] [Paper: PDF p. 1] |
| Core contribution | A standardized, large-scale benchmark (STP-BENCH) for virtual ST models, with unified PFM encoding, multi-granularity evaluation (gene/gene-set/cell-type/domain), and robustness analysis across cross-institution/tissue/platform shifts | [Paper] [Paper: PDF p. 2–4], [Paper] [Paper: PDF p. 5 Fig.1], [Paper] [Paper: PDF p. 18–19] |
| Key datasets | STP-BENCH-INTERNAL (609,024 spots, 6 cancer types, Visium+Xenium); STP-BENCH-EXTERNAL (185,831 spots, same 6 cancers, independent sources) | [Paper] [Paper: PDF p. 4], [Figure 1b], [Paper] [Paper: PDF p. 21] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6], [Figure 1c], [Paper] [Paper: PDF p. 22] |
| Primary encoder | UNIv2 pathology foundation model (PFM), used as default where architecturally compatible | [Paper] [Paper: PDF p. 7], [Figure 2a], [Paper] [Paper: PDF p. 22–23] |
| Main metrics | Pearson Correlation Coefficient (PCC) [Equation 1], Mean Absolute Error (MAE) [Equation 2], SSIM | [Paper] [Paper: PDF p. 31–32], [Paper] [Paper: PDF p. 7] |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench and Hugging Face (https://huggingface.co/datasets/nexgem/STP-Bench) | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结

该论文构建了STP-BENCH——首个统一、大规模、多维度的虚拟空间转录组（virtual ST）系统性基准，覆盖6种癌症、2种平台（Visium/Xenium）、超79万spots；它通过强制统一病理基础模型（UNIv2）作为图像编码器，剥离了编码器性能对架构评估的干扰，揭示多数复杂模型未超越线性探针基线；进一步从基因级可预测性、通路级功能保真度、细胞类型丰度推断、空间结构识别及跨域泛化能力五个层面，系统刻画了当前方法的能力边界与根本瓶颈。其核心价值在于将“benchmarking”从零散报告升维为可控实验范式，为single-cell foundation models、spatial transcriptomics和multi-omics建模提供了可复现的评估基础设施。

## 03 研究问题

论文直面虚拟ST领域长期存在的**评估失焦问题**：当不同研究使用异构数据集、私有训练流程、混杂的图像编码器（如ResNet50 vs. UNIv1）时，模型性能比较失去可比性。作者追问：若剥离图像编码器差异，真实架构创新是否仍具优势？哪些基因/通路/生物学粒度能被可靠恢复？模型在真实临床场景（跨机构、跨组织、跨平台）中是否鲁棒？这些问题无法由单个模型论文回答，必须通过受控的系统性基准实验来检验。

## 04 研究背景与发展路径

虚拟ST技术演进呈现“三支并行”格局：（1）**回归类**（如ST-Net→TRIPLEX→DeepSpot），从局部patch预测扩展至多尺度上下文融合；（2）**双模态对齐类**（如BLEEP→STco→mclSTExp），借鉴CLIP范式学习形态-表达联合嵌入空间；（3）**生成类**（如STFlow→Stem），用扩散/流匹配建模表达分布而非点估计。但评估始终滞后：Wang et al. [50] 保留原生编码器导致架构与编码器效应混淆；HEST-1K [51] 仅测试PFM嵌入与简单回归器的关联，未覆盖完整模型族。STP-BENCH正是对这一断裂的修复——它不提出新模型，而是构建一个“控制变量”的评估实验室，将PFM作为公共接口，让所有模型在相同输入表征上竞争，从而锚定真正可迁移的架构知识。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **评估不可比** | 模型排名随所用图像编码器剧烈波动（如CFANet从第16跃至第6） | 原有工作未标准化编码器，而PFM性能主导下游表现 | [Paper] [Paper: PDF p. 9], [Figure 2b], [Paper] [Paper: PDF p. 18] |
| **生物学解释性缺失** | 报告平均PCC掩盖基因级差异：HMHVGs（PCC≈0.4）与TME marker genes（PCC≈0.2）预测难度悬殊 | 数据稀疏性（尤其Visium低计数）与形态-表达耦合强度共同限制 | [Paper] [Paper: PDF p. 9–10], [Figure 2a,c,d], [Paper] [Paper: PDF p. 10 box plots] |
| **下游效用验证空白** | 虚拟ST是否支持Cell2location或SpaGCN等真实分析工具？现有工作未检验 | 仅spot-level指标无法保证生物学结构保真；需在细胞组成、空间域等粒度验证 | [Paper] [Paper: PDF p. 14], [Figure 4a–c], [Paper] [Paper: PDF p. 19] |
| **鲁棒性未经检验** | 模型在跨机构（batch effect）、跨组织（morphology shift）、跨平台（Visium→Xenium）下性能崩溃或不稳定 | 形态-表达映射高度组织特异性；平台间技术差异（如Xenium更高灵敏度）引入非平稳性 | [Paper] [Paper: PDF p. 17], [Figure 5a–b], [Paper] [Paper: PDF p. 19] |
| **数据扩展悖论** | 增加训练数据量（intra-cohort）收益递减；跨癌种聚合（inter-cohort）常致负迁移 | 组织特异性形态特征主导预测，简单拼接破坏特征分布一致性 | [Paper] [Paper: PDF p. 18], [Figure 5c–d], [Paper] [Paper: PDF p. 19] |

## 06 核心思想

论文的核心思想是：**虚拟ST的评估必须解耦“形态表征力”与“架构推理力”，并将评价尺度从统计指标延伸至生物学效用与现实鲁棒性**。它拒绝将高PCC等同于高价值，转而主张：（1）UNIv2等PFM是当前形态理解的“天花板”，模型应在此基础上证明增量；（2）基因级可预测性存在普适排序（e.g., COL1A1易预测，CD19难预测），反映形态信息固有上限；（3）真正的进步体现在能否提升对空间结构敏感通路（如ECM remodeling, T-cell activation）的恢复能力，而非平均分提升；（4）鲁棒性不是附加项，而是部署前提——跨组织泛化失败暴露了当前模型对组织特异性先验的过度依赖。

## 07 方法总览

STP-BENCH是一个三层评估框架：（1）**统一表征层**：强制使用UNIv2（或Virchow2等）提取spot级H&E patch嵌入，消除编码器偏差；（2）**多粒度验证层**：除spot-level PCC/MAE/SSIM外，新增gene-set（singscore）、cell-type abundance（Cell2location）、spatial domain（SpaGCN+ARI）三级验证；（3）**鲁棒性压力测试层**：设计Cross-Institution（同癌种不同医院）、Cross-Tissue（LUAD→BRCA）、Cross-Platform（Visium→Xenium）三类泛化任务，并量化generalization gap。所有21模型均按此协议重实现，确保比较公平。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| **UNIv2 PFM Encoder** | Extracts morphology-aware embeddings from 224×224 H&E patches | To isolate architectural contribution by standardizing input representation; UNIv2 outperforms ResNet50/CTransPath on HMHVG+marker genes | Input: H&E patch; Output: d-dim vector (d=1024) | [Paper] [Paper: PDF p. 10], [Figure 2e], [Paper] [Paper: PDF p. 22–23] | Severe ranking inversion (e.g., CFANet drops from #6 to #16) and ~0.2 PCC drop for most models [Figure 2b] |
| **Gene Set Scoring (singscore)** | Computes per-spot activity score for GO Biological Process terms via rank-based aggregation | To test if gene-level predictions preserve functional coherence beyond individual genes | Input: spot×gene matrix; Output: spot×gene_set matrix | [Paper] [Paper: PDF p. 13], [Figure 3c–e], [Paper] [Paper: PDF p. 35] | Loss of biological interpretability: TRIPLEX/DeepSpot’s advantage on immune/stromal pathways would be invisible [Figure 3e] |
| **Cell2location Deconvolution** | Estimates spatial cell-type abundances from expression matrix using scRNA-seq reference | To validate if virtual ST supports downstream cellular inference, not just gene recovery | Input: spot×gene matrix + scRNA ref; Output: spot×cell_type matrix | [Paper] [Paper: PDF p. 14], [Figure 4a], [Paper] [Paper: PDF p. 35] | Failure to detect architecture superiority: TRIPLEX/DeepSpot lead in epithelial/T-cell abundance correlation, but linear probe fails on rare populations (plasma/mast cells) [Figure 4a] |
| **SpaGCN Spatial Clustering** | Identifies spatial domains via graph neural network on expression+coordinates | To assess preservation of tissue-level spatial organization | Input: spot×gene matrix + coordinates; Output: domain labels per spot | [Paper] [Paper: PDF p. 14], [Figure 4b–c], [Paper] [Paper: PDF p. 36] | Collapse of spatial structure fidelity: STFlow shows lowest ARI, consistent with its weak gene-level PCC [Figure 4c] |
| **Cross-Tissue Generalization Protocol** | Trains on LUAD-Visium, tests on BRCA-Visium (or vice versa) | To stress-test morphological generalizability beyond technical batch effects | Input: train set (cancer A), test set (cancer B); Output: PCC gap | [Paper] [Paper: PDF p. 17], [Figure 5a–b], [Paper] [Paper: PDF p. 19] | Masking of tissue-specificity bottleneck: Cross-tissue gap (−0.2 to −0.35) is 3× larger than cross-institution gap, revealing fundamental limitation [Figure 5b middle] |

## 09 关键公式与符号

论文明确给出两个核心公式：  
- **Equation 1**（[Paper] [Paper: PDF p. 31]）：Pearson Correlation Coefficient (PCC) for gene *g* in section *s*:  
  $$\text{PCC}_{g,s} = \frac{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^N (\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^N (y_{i,g} - \bar{y}_g)^2}}$$  
  其中 $\hat{y}_{i,g}, y_{i,g}$ 为spot *i* 上 gene *g* 的预测与真实 log-normalized 表达值；$\bar{\hat{y}}_g, \bar{y}_g$ 为其均值。PCC 是全文主指标，用于 gene-level、section-level、dataset-level 逐级聚合。  

- **Equation 2**（[Paper] [Paper: PDF p. 32]）：Mean Absolute Error (MAE) for gene *g* in section *s*:  
  $$\text{MAE}_{g,s} = \frac{1}{N}\sum_{i=1}^N |\hat{y}_{i,g} - y_{i,g}|$$  
  MAE 在 log(1+x)-transformed 空间计算，反映绝对误差大小，与 PCC 互补。  

其他关键符号：  
- **HMHVG**: High-Mean Highly-Variable Genes (200 genes selected by joint rank-sum of mean & std) [Paper] [Paper: PDF p. 33]  
- **TME markers**: 16 marker genes (e.g., CD3E, ACTA2, PDCD1) covering epithelial/stromal/immune lineages [Paper] [Paper: PDF p. 7, 33]  
- **STP-BENCH-INTERNAL/EXTERNAL**: Internal training/validation cohort (609k spots) vs. external test cohort (186k spots), strictly disjoint [Paper] [Paper: PDF p. 4, 21]  
- **PCC gap**: External PCC − Internal PCC, quantifying generalization degradation [Figure 5b]  
- **singscore**: Rank-based gene set scoring method used for functional analysis [Paper] [Paper: PDF p. 13, 35]  

无其他可核验公式；所有模型架构细节见 Online Methods，但未以公式形式呈现。

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|------------------------------|--------|-------------------------|-------------------------------|--------|
| **UNIv2 vs Native encoders** | Standardizing encoder reshapes model rankings | Compare PCC of 21 models using their original encoder vs. UNIv2 on STP-BENCH-INTERNAL (HMHVG+markers) | CFANet jumps from #16 to #6; many w/o PFM models fall below linear probe baseline | Encoder choice dominates reported architectural gains; prior comparisons are confounded | UNIv2 is universally optimal — Virchow2/H-Optimus1 show comparable performance [Figure 2e] | [Paper] [Paper: PDF p. 9], [Figure 2b], [Paper] [Paper: PDF p. 10] |
| **Gene-level predictability stratification** | Genes exhibit universal predictability ranking across models | Compute PCC per gene for 20 models; bin genes into 5 quantiles by mean PCC; compare model rankings within bins | Rankings stable across all bins (e.g., TRIPLEX/DeepSpot top in "Very High" and "Medium"); Kruskal-Wallis p<1e-12 for expression-level effect | Predictability is gene-intrinsic, not model-dependent; morphology-expression coupling strength is primary constraint | All genes are equally predictable — low-expression genes (e.g., CD19) consistently underperform [Figure 2c-d, 38] | [Paper] [Paper: PDF p. 9], [Figure 2c-d], [Extended Data Fig.1] |
| **Multi-scale models on stromal/immune genes** | Architectures integrating multi-scale context gain on spatially structured programs | Select genes with ΔPCC≥0.1 over linear probe & PCC≥0.4; manually annotate functional categories | Top gains for COL1A1/COL3A1 (stromal), LAG3/IGKC (immune), SFTPC (epithelial); TRIPLEX/DeepSpot dominate | Multi-scale reasoning (neighbor/global branches) is necessary for genes requiring meso-macro scale morphology | Single-scale models are useless — some (e.g., EGN) still beat baseline marginally [Figure 3b] | [Paper] [Paper: PDF p. 11–13], [Figure 3b] |
| **Cell2location on virtual ST** | Virtual ST profiles support cell-type deconvolution | Apply Cell2location to ground-truth vs. predicted matrices (6 models × 3 cohorts); compute PCC per cell type | TRIPLEX/DeepSpot achieve highest avg PCC; malignant epithelial/T-cells well-recovered; plasma/mast cells poorly recovered | Gene-level accuracy translates to cellular inference; rare populations remain challenging | Virtual ST enables clinical-grade deconvolution — performance on rare cells is near-random [Figure 4a] | [Paper] [Paper: PDF p. 14], [Figure 4a], [Paper] [Paper: PDF p. 35] |
| **Cross-tissue generalization** | Morphology-to-expression mapping is highly tissue-specific | Train on NCCHE-LUAD-Visium, test on WUSTL-BRCA-Visium; compute PCC gap | Gap = −0.20 to −0.35; Spearman ρ=0.876 for internal vs external ranking preservation | Architectural superiority generalizes, but absolute performance plummets due to tissue heterogeneity | Cross-tissue transfer is feasible with fine-tuning — no such experiment performed | [Paper] [Paper: PDF p. 17], [Figure 5a–b middle], [Paper] [Paper: PDF p. 19] |

## 11 对结论的正确理解

论文结论**不可简化为“现有模型都不行”**，而应精确理解为：（1）在UNIv2统一表征下，**多数模型的架构增益有限且高度条件依赖**——TRIPLEX/DeepSpot仅在特定基因（stromal/immune）、特定平台（Xenium高计数）、特定下游任务（domain identification）上稳定胜出；（2）**预测瓶颈本质是生物学的，而非纯工程的**：HMHVGs与marker genes的PCC差距（0.4 vs 0.2）主要源于Visium数据稀疏性，而非模型缺陷；当Xenium提供更高计数时，两者PCC均升至0.58+ [Figure 2c]；（3）**鲁棒性失效揭示了根本假设冲突**：当前模型隐含“形态-表达映射跨组织通用”，但跨组织泛化失败证明该映射是组织特异的，需新范式（如tissue-aware adaptation）；（4）**STP-BENCH本身是方法论贡献**：它定义了虚拟ST评估的黄金标准——必须包含multi-granularity validation与cross-domain stress testing，否则任何PCC报告都缺乏临床意义。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium), missing rarer cancers and emerging modalities (e.g., Stereo-seq) | Extend benchmark to additional tumor types, tissue contexts, and sequencing platforms for broader generalizability | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focus on HMHVGs (200 genes) and 16 TME markers; lowly expressed or functionally diverse genes not systematically evaluated | Systematic investigation of low-expression genes and broader functional gene sets remains an open direction | [Paper] [Paper: PDF p. 20] |
| **Spot-level resolution only** | Evaluation is at Visium/Xenium pseudo-spot level (aggregating multiple cells), not single-cell resolution | Future benchmarking efforts should extend principles to single-cell ST datasets and virtual ST models as they become available | [Paper] [Paper: PDF p. 20] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|--------|
| **UNIv2 as “ground truth” encoder may mask modality-specific biases** | UNIv2 is trained on generic H&E WSIs; its features might underrepresent cancer-specific morphologies (e.g., necrosis, mitotic figures) critical for certain genes | If UNIv2 misses cancer-relevant features, even perfect architectures would fail, falsely attributing failure to model design | Train cancer-type-specific PFMs (e.g., LUAD-UNIv2) and re-run STP-BENCH; compare ranking stability | [Paper] [Paper: PDF p. 10] notes UNIv2/Virchow2/H-Optimus1 perform similarly, but all are generalist PFMs |
| **singscore-based gene set analysis ignores gene-gene correlations** | singscore uses rank-based averaging, discarding co-expression structure; a model could recover ranks but miss functional modules requiring covariance | Overestimates functional fidelity: high singscore PCC doesn’t guarantee recovered pathways behave coherently in downstream perturbation simulations | Replace singscore with PCA-based pathway scores or GSEA-like enrichment; correlate pathway loadings between true/predicted matrices | [Paper] [Paper: PDF p. 13] states singscore is "well suited for efficient computation", but doesn't validate its biological fidelity vs. correlation-aware methods |
| **Cross-platform (Visium→Xenium) "improvement" may reflect data quality, not model capability** | Figure 5b right shows some models have positive gaps; this likely stems from Xenium's higher sensitivity (more transcripts), not better generalization | Misleadingly suggests models bridge platform gaps, when in reality they merely benefit from richer targets | Control for transcript count: subsample Xenium to Visium-level depth and re-evaluate; or use spike-in normalized metrics | [Paper] [Paper: PDF p. 10] explicitly links prediction quality to "basal gene expression levels" and "transcript detection quality" |
| **Negative transfer in inter-cohort scaling assumes homogeneous mixing** | Figure 5d shows BRCA+LUAD+PRAD hurts BRCA performance; but this assumes naive concatenation, not domain-adaptive weighting | Overlooks viable solutions: domain-aware sampling or adversarial domain alignment could mitigate negative transfer | Implement domain classifier-guided loss weighting during inter-cohort training; compare to naive mixing on STP-BENCH-EXTERNAL | [Paper] [Paper: PDF p. 19] calls for "domain-adaptive or tissue-aware learning strategies" but doesn't test any |

## 14 学到的知识

- **评估即设计**：STP-BENCH证明，严谨的基准设计（统一编码器、多粒度验证、鲁棒性压力测试）本身就是对领域认知的深化，其价值不亚于新模型。
- **形态表征是瓶颈天花板**：UNIv2等PFM已逼近H&E图像蕴含的形态信息上限；后续创新必须聚焦于如何更高效地利用这些表征（如TRIPLEX的跨尺度融合），而非堆砌编码器。
- **基因可预测性存在普适谱系**：COL1A1（stromal）> CD3E（T-cell）> CD19（B-cell）的预测难度排序在所有模型和数据集中稳定，表明这是形态-表达耦合的固有属性，可指导靶向优化。
- **下游效用是终极标尺**：Cell2location和SpaGCN的性能与spot-level PCC强相关（Spearman=0.902），证实提升基因预测质量是解锁生物学价值的必要条件。
- **组织特异性是泛化核心障碍**：Cross-tissue gap（−0.35）远大于cross-institution gap（−0.10），说明解决跨组织泛化需重构模型先验（如引入组织类型嵌入），而非调优超参。

## 15 与既有知识的连接

- **候选连接/方法论连接**：STP-BENCH的“统一编码器+多粒度验证”范式，与single-cell foundation models（如scGPT、CellLM）的评估逻辑一致——均强调在固定表征上测试下游任务能力，而非端到端训练。但本文未引用或对比任何scFM工作，故为弱连接。
- **候选连接/方法论连接**：其跨平台（Visium↔Xenium）分析与spatial transcriptomics中multi-resolution integration（如SPATA、SpatialGLM）目标相通，均需处理不同分辨率/灵敏度数据的对齐，但本文未采用图神经网络（GNN）或几何深度学习技术，故为弱连接。
- **候选连接/方法论连接**：对multi-omics的启示在于：STP-BENCH揭示了“模态对齐”的脆弱性——当形态（H&E）与表达（ST）的耦合强度随组织变化时，简单对比学习（BLEEP）失效；这警示multi-omics对齐需显式建模模态间关系的条件性，而非全局对齐。
- **候选连接/方法论连接**：其发现的“组织特异性瓶颈”直接关联biomedical AI中的domain generalization挑战；论文提议的“tissue-aware learning”与现有医学AI的domain adaptation方法（如DANN、MMD）形成方法论呼应，但未实证对比。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware Adapter for Cross-Tissue Virtual ST  
  **originating limitation/observation**: Cross-tissue generalization gap is severe (−0.35) and stems from tissue-specific morphology-expression mappings [Paper] [Paper: PDF p. 17, 19]  
  **core hypothesis**: Injecting lightweight, tissue-type-specific adapters into UNIv2 encoder outputs can recalibrate morphology representations for each tissue, enabling knowledge transfer without full fine-tuning  
  **delta from paper**: STP-BENCH identifies the problem but proposes no solution; this adds parameter-efficient adapters (LoRA-style) conditioned on tissue label  
  **initial method**: For each tissue *t*, learn adapter $A_t$ that transforms UNIv2 embedding $z$: $z' = z + A_t(z)$. Train $A_t$ on tissue-specific data with frozen UNIv2 and TRIPLEX backbone  
  **validation**: Test on STP-BENCH cross-tissue tasks (e.g., LUAD→BRCA); measure PCC gap reduction vs. baseline TRIPLEX  
  **failure modes**: Adapter overfitting to small tissue cohorts; inability to generalize to unseen tissues  
  **innovation status**: unverified  

- **name**: SingScore-Guided Gene Selection for Virtual ST Training  
  **originating limitation/observation**: HMHVGs and marker genes show divergent predictability; current gene panels are static and ignore functional coherence [Paper] [Paper: PDF p. 7, 9]  
  **core hypothesis**: Optimizing training loss to maximize singscore PCC on key pathways (e.g., T-cell activation) yields better downstream utility than maximizing average gene PCC  
  **delta from paper**: STP-BENCH evaluates singscore post-hoc; this integrates it into training objective  
  **initial method**: Replace MSE loss with hybrid loss: $\mathcal{L} = \lambda \cdot \text{MSE} + (1-\lambda) \cdot (1 - \text{singscore\_PCC})$. Optimize $\lambda$ on validation set  
  **validation**: Compare Cell2location PCC and SpaGCN ARI of models trained with hybrid vs. MSE loss on STP-BENCH-INTERNAL  
  **failure modes**: Degraded performance on individual genes not in top pathways; increased training instability  
  **innovation status**: unverified  

- **name**: Graph-Augmented Spot Context for Sparse Marker Gene Prediction  
  **originating limitation/observation**: Marker genes (e.g., CD19) suffer from low counts in Visium, causing poor prediction; their spatial expression is highly correlated with neighbors [Paper] [Paper: PDF p. 10, Figure 2d]  
  **core hypothesis**: Modeling spot-level expression as a graph signal (using spatial adjacency) improves prediction of sparse genes more than patch-level regression alone  
  **delta from paper**: STP-BENCH uses spot-level features but not explicit graph structure for regression; this adds GNN layers to DeepSpot’s neighbor branch  
  **initial method**: Extend DeepSpot’s neighbor branch with GraphSAGE layer over spatial ego-graph (6-hop Visium neighbors); fuse with target/sub-spot embeddings  
  **validation**: Evaluate on Visium-based cohorts (NCCHE-LUAD-Visium, WUSTL-BRCA-Visium) for marker gene PCC; compare to original DeepSpot  
  **failure modes**: Over-smoothing on sparse graphs; computational overhead for large cohorts  
  **innovation status**: unverified  

- **name**: Foundation Model Distillation for Lightweight Virtual ST  
  **originating limitation/observation**: UNIv2 is large (ViT-L); deploying TRIPLEX/DeepSpot with it is costly; STP-BENCH shows smaller PFMs (CTransPath) underperform [Figure 2e]  
  **core hypothesis**: Distilling UNIv2’s morphology knowledge into a smaller student model (e.g., ViT-T) preserves most predictive power while enabling edge deployment  
  **delta from paper**: STP-BENCH compares PFMs but doesn’t attempt distillation  
  **initial method**: Train ViT-T student to mimic UNIv2’s patch embeddings on STP-BENCH-INTERNAL patches using MSE + KL divergence on attention maps  
  **validation**: Plug distilled encoder into TRIPLEX; compare PCC on STP-BENCH-INTERNAL vs. UNIv2-TRIPLEX; measure latency/FLOPs  
  **failure modes**: Distillation collapse losing fine-grained morphology; poor generalization to external cohorts  
  **innovation status**: unverified