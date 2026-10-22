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
| Publication date | 2026-09-05 | [Paper meta] |
| Authors | Youngmin Chung et al. (21 authors, multi-institutional) | [Paper] [Paper: PDF p. 1] |
| Core contribution | STP-BENCH — a large-scale, standardized benchmark for virtual ST models, comprising STP-BENCH-INTERNAL (609,024 spots) and STP-BENCH-EXTERNAL (185,831 spots), spanning 6 cancer types & 2 platforms (Visium/Xenium) | [Paper] [Paper: PDF p. 4–5], [Figure 1b] |
| Evaluated models | 21 models: 14 regression-based, 4 bi-modal retrieval, 3 generative | [Paper] [Paper: PDF p. 6], [Figure 1c] |
| Key metrics | PCC (Equation 1), MAE (Equation 2), SSIM | [Paper] [Paper: PDF p. 31–32], [Equation 1], [Equation 2] |
| Primary encoder | UNIv2 pathology foundation model (PFM), used as unified patch encoder where architecturally compatible | [Paper] [Paper: PDF p. 7–8], [Figure 2a–b] |
| Code & data | Publicly released at https://github.com/NEXGEM/STP-Bench; preprocessed datasets on Hugging Face | [Paper] [Paper: PDF p. 37] |

## 02 一句话总结  
本文提出了 STP-BENCH —首个面向 virtual spatial transcriptomics（从 H&E 图像预测空间基因表达）的统一、大规模、多维度系统性基准，覆盖 6 癌种、2 平台（Visium/Xenium）、超 79 万 spot，强制统一病理基础模型（UNIv2）作为图像编码器以解耦架构与表征贡献。它不仅报告平均 PCC，更深入揭示：① 基因级可预测性存在普适天花板（如 marker genes 普遍难预测），② 多尺度架构（TRIPLEX/DeepSpot）在 stromal/immune 基因上显著超越线性探针，③ Xenium 数据质量直接决定下游生物学效用上限。该工作本质是方法论审计工具，而非提出新模型。

## 03 研究问题  
- **核心问题**：当前 virtual ST 领域缺乏公平、可控、可复现的评估框架，导致模型性能比较失真、生物学解释力模糊、鲁棒性未知。  
- **驱动假设**：现有评估偏差主要源于三方面混杂——（1）各模型使用异构图像编码器（ImageNet vs. pathology PFMs），（2）仅报告 aggregate gene-level accuracy，忽略 per-gene 可预测性差异与生物学语义，（3）未验证预测结果能否支撑下游生物分析（如 cell deconvolution）。  
- **方法路径**：构建 STP-BENCH，通过三重控制实现归因分离：① 统一 PFM 编码器（UNIv2）剥离编码器效应；② 在基因、基因集、细胞类型、空间结构四层粒度评估；③ 设计 cross-institution/tissue/platform 外部测试验证泛化边界。

## 04 研究背景与发展路径  
虚拟 ST 的演进呈现“范式三分”：（1）**回归范式**（ST-Net → TRIPLEX/DeepSpot）：将 H&E patch 映射为基因向量，逐步引入邻域/全局上下文；（2）**双模对齐范式**（BLEEP → mclSTExp）：借鉴 CLIP，学习 morphology-expression 联合嵌入空间，依赖检索；（3）**生成范式**（STFlow/Stem）：建模条件分布，支持不确定性估计。但所有范式均日益依赖病理基础模型（PFM）提取形态特征 [Paper] [Paper: PDF p. 3]。然而，此前基准（Wang et al. 2024；HEST-1K）或未统一编码器 [Paper] [Paper: PDF p. 3]，或仅评估 PFM embedding 与基因的简单相关性 [Paper] [Paper: PDF p. 4]，无法回答“架构创新是否真实有效”这一根本问题。STP-BENCH 正是在此方法论真空处切入，将 benchmark 定位为“控制实验平台”。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **不公平模型比较** | 模型排名随编码器切换剧烈波动（如 CFANet 从第16跃至第6） | 各模型原生编码器差异巨大（ImageNet-pretrained ResNet50 vs. pathology PFMs），性能提升常源于编码器而非架构 | [Paper] [Paper: PDF p. 9], [Figure 2b]; “CFANet... jumped to 6th when using UNIv2” |
| **评估粒度粗放** | 报告平均 PCC 掩盖基因间巨大差异（HMHVG PCC≈0.4 vs. marker genes PCC≈0.2） | 未区分基因功能类别与表达丰度，无法判断模型是否捕获特定生物学程序 | [Paper] [Paper: PDF p. 9], [Figure 2a]; “marker genes showed remarkably lower predictability” |
| **生物学效用黑箱** | 高 PCC 不保证下游任务可用（如 Cell2location 输入需 count-scale 整数） | 未验证预测表达谱能否支撑 cell-type deconvolution 或 spatial domain identification 等实际分析流程 | [Paper] [Paper: PDF p. 14], [Figure 4a–c]; “TRIPLEX and DeepSpot consistently achieved the highest average correlation” with ground truth in deconvolution |
| **鲁棒性未经检验** | 模型在跨机构/组织/平台场景下性能断崖式下跌（cross-tissue gap up to −0.35 PCC） | 形态-表达映射高度组织特异性，现有训练数据未覆盖足够组织多样性 | [Paper] [Paper: PDF p. 17], [Figure 5b]; “cross-tissue generalization was challenging... gaps reaching −0.20 to −0.35” |
| **数据质量影响被忽视** | Visium 数据上 marker gene 预测普遍失败（PCC≈0.19），而 Xenium 上可达 0.58 | Visium 低基因计数（mean=0.9）导致信噪比不足，模型能力被数据瓶颈掩盖 | [Paper] [Paper: PDF p. 10], [Figure 2d]; “Visium-based datasets... marker-gene prediction was substantially weaker” |

## 06 核心思想  
论文的核心思想是：**virtual ST 的评估必须从“单一数字竞赛”转向“多维归因审计”**。其逻辑链为：（1）先解耦——用统一 PFM（UNIv2）作为所有兼容模型的“标准显微镜”，使架构差异成为唯一变量；（2）再分层——在基因（which genes?）、基因集（which pathways?）、细胞类型（which populations?）、空间结构（which domains?）四个生物学粒度上量化预测保真度；（3）最后压力测试——在跨机构（technical）、跨组织（biological）、跨平台（modality）三大现实域偏移下检验鲁棒性。最终发现：架构优势仅在特定基因子集（stromal/immune）和高质量数据（Xenium）上显现，且跨组织泛化是最大瓶颈。

## 07 方法总览  
STP-BENCH 是一个三层评估框架：（1）**统一数据层**：构建 STP-BENCH-INTERNAL（609k spots, 6 cancers, 2 platforms）与 STP-BENCH-EXTERNAL（186k spots, strict train/test separation），对 Visium/Xenium 采用不同预处理（spot cropping vs. pseudo-spot binning）[Paper] [Paper: PDF p. 4–6], [Figure 1b]; （2）**统一模型层**：重实现 21 模型，强制 UNIv2 作为 patch encoder（除非架构不兼容，如 M2OST/M2ORT）[Paper] [Paper: PDF p. 22–28]; （3）**统一评估层**：在基因级（PCC/MAE/SSIM）、基因集级（singscore）、细胞级（Cell2location）、空间级（SpaGCN+ARI）四维度打分，并设计 cross-institution/tissue/platform 外部测试 [Paper] [Paper: PDF p. 7–16], [Figure 1d–g]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|---------------------|------------------------|-----------------------------------|
| **UNIv2 Standardized Encoder** | Extracts 1024-dim pathology-aware features from 224×224 H&E patches | To isolate architectural contribution by eliminating encoder variability; UNIv2 outperforms ResNet50/CTransPath on HMHVG+marker genes [Paper] [Paper: PDF p. 10], [Figure 2e] | Input: H&E patch; Output: PFM embedding vector | [Paper] [Paper: PDF p. 7–10], [Figure 2a–e]; “UNIv2, Virchow2, and H-Optimus1 achieved the highest... performance” | Severe ranking distortion (e.g., CFANet drops from 6th to 16th) and inflated baseline failure rate [Paper] [Paper: PDF p. 9], [Figure 2b] |
| **Multi-granularity Evaluation Pipeline** | Computes PCC at gene, gene-set (singscore), cell-type (Cell2location), and spatial-domain (SpaGCN+ARI) levels | To test if spot-level correlation translates to biological utility; reveals platform-dependent ceiling (Xenium > Visium) [Paper] [Paper: PDF p. 14–15], [Figure 4] | Input: Predicted & ground-truth expression matrices; Output: PCC (gene/gene-set), Pearson corr (cell abundance), ARI (domain) | [Paper] [Paper: PDF p. 14–16], [Figure 4a–c]; “TRIPLEX and DeepSpot consistently achieved the highest average correlation” in deconvolution across cohorts | Loss of biological interpretability: high gene-PCC but low ARI would indicate spatial structure collapse [Paper] [Paper: PDF p. 14] |
| **Cross-Domain Generalization Suite** | Evaluates models on STP-BENCH-EXTERNAL under Cross-Institution (same cancer, different site), Cross-Tissue (different cancer), Cross-Platform (Visium→Xenium) | To quantify real-world deployment risk; identifies tissue-specificity as dominant barrier [Paper] [Paper: PDF p. 17], [Figure 5a–b] | Input: Model trained on INTERNAL; Output: External PCC & generalization gap (External−Internal) | [Paper] [Paper: PDF p. 17], [Figure 5a–b]; “cross-tissue generalization was challenging... gaps reaching −0.20 to −0.35” | Over-optimistic internal validation: models ranking #1 internally may fail catastrophically on new tissue [Paper] [Paper: PDF p. 17] |
| **Gene-Level Stratification Engine** | Groups genes into 5 quantiles by mean PCC across models, then analyzes performance per bin | To reveal universal predictability patterns (e.g., “genes hard for one model are hard for all”) and identify architecture-specific gains [Paper] [Paper: PDF p. 11], [Extended Data Fig. 1] | Input: Gene-wise PCC matrix; Output: Bins (Very Low to Very High) & margin analysis (∆PCC over linear probe) | [Paper] [Paper: PDF p. 11], [Figure 3a], [Extended Data Fig. 1]; “smooth separation of high- and low-performing genes across models” | Obscures gene-category biases: without stratification, stromal gene failure would be masked by epithelial gene success [Paper] [Paper: PDF p. 11] |

## 09 关键公式与符号  
论文未提出新公式，但明确定义并使用了三个核心评估指标：  
- **Pearson Correlation Coefficient (PCC)**：Equation 1（[Paper] [Paper: PDF p. 31]）  
  $ \text{PCC}_{g,s} = \frac{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)(y_{i,g} - \bar{y}_g)}{\sqrt{\sum_{i=1}^{N}(\hat{y}_{i,g} - \bar{\hat{y}}_g)^2 \cdot \sum_{i=1}^{N}(y_{i,g} - \bar{y}_g)^2}} $  
  其中 $\hat{y}_{i,g}$ 和 $y_{i,g}$ 分别为 spot $i$、gene $g$ 的预测与真实 log-normalized 表达值；$\bar{\hat{y}}_g$, $\bar{y}_g$ 为其均值。NaN（零方差基因）置零。  
- **Mean Absolute Error (MAE)**：Equation 2（[Paper] [Paper: PDF p. 32]）  
  $ \text{MAE}_{g,s} = \frac{1}{N}\sum_{i=1}^{N}|\hat{y}_{i,g} - y_{i,g}| $  
  在 log(1+x)-transformed 表达空间计算，反映绝对误差大小。  
- **Key symbols**:  
  - `HMHVG`: High-mean highly-variable genes (200 genes selected via rank-sum of mean & std) [Paper] [Paper: PDF p. 33]  
  - `TME markers`: 16 tumor microenvironment marker genes (e.g., CD3E, ACTA2, PDCD1) [Paper] [Paper: PDF p. 7]  
  - `PCC`, `MAE`, `SSIM`: Primary evaluation metrics [Paper] [Paper: PDF p. 7]  
  - `STP-BENCH-INTERNAL/EXTERNAL`: Internal training/validation cohort (609k spots) and external test cohort (186k spots) [Paper] [Paper: PDF p. 4–5], [Figure 1b]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|-------------------------|-------------------------------|--------|
| **Unified encoder benchmark** | Standardizing image encoder reshapes model rankings | Compare 21 models using native encoders vs. UNIv2; evaluate on HMHVG & marker genes across 7 datasets | UNIv2 standardization caused large ranking shifts (e.g., CFANet +10 ranks); most models failed to beat linear probe baseline | Encoder choice dominates reported architectural gains; prior comparisons are unfair | UNIv2 is universally optimal — CTransPath/Virchow2 show comparable performance [Paper] [Paper: PDF p. 10], [Figure 2e] | [Paper] [Paper: PDF p. 7–9], [Figure 2a–b] |
| **Gene-level stratification** | Gene predictability is largely model-agnostic but architecture can shift boundaries | Compute gene-wise PCC for 20 models; group genes into 5 bins by mean PCC; calculate ∆PCC over linear probe | Strong concordance across models (genes hard for one are hard for all); TRIPLEX/DeepSpot show largest ∆PCC for stromal/immune genes | Universal gene-level ceiling exists; multi-scale architectures provide targeted gains | All genes can be predicted well with sufficient architecture complexity — low-PCC genes remain low across all models [Paper] [Paper: PDF p. 11], [Figure 3a] | [Paper] [Paper: PDF p. 11], [Figure 3a], [Extended Data Fig. 1] |
| **Downstream utility test** | Spot-level PCC predicts utility for biological tasks | Apply Cell2location (cell abundance) and SpaGCN+ARI (spatial domains) to predicted profiles; compare to ground-truth results | TRIPLEX/DeepSpot top-ranked in both tasks; performance strongly correlates with gene-PCC and is higher on Xenium than Visium | Gene-level accuracy directly enables downstream inference; data quality (Xenium) is a shared bottleneck | Predicted profiles are interchangeable with ground-truth for all downstream tools — Cell2location requires count-scale input, necessitating expm1+clip [Paper] [Paper: PDF p. 35] | [Paper] [Paper: PDF p. 14–15], [Figure 4a–c] |
| **Cross-tissue generalization** | Morphology-to-expression mapping is highly tissue-specific | Train models on one cancer type (e.g., LUAD), test on another (e.g., BRCA); compute generalization gap (External−Internal PCC) | Cross-tissue gap (−0.20 to −0.35) far exceeds cross-institution gap (−0.05 to −0.10); Spearman ρ=0.876 for rank preservation | Tissue context is the dominant constraint on generalization; simple data aggregation harms performance | Domain adaptation can fully bridge cross-tissue gap — inter-cohort scaling showed negative transfer [Paper] [Paper: PDF p. 19], [Figure 5d] | [Paper] [Paper: PDF p. 17], [Figure 5a–b] |
| **Data scaling analysis** | More training data always improves performance | Intra-cohort: train on 33%/66%/100% of WUSTL-BRCA-Visium spots; Inter-cohort: add LUAD/PRAD to BRCA training | Intra-cohort: marginal gains beyond 66%; Inter-cohort: performance often decreased (negative transfer) | Models saturate quickly on H&E information; tissue heterogeneity harms rather than helps | Scaling laws from LLMs apply — no such law observed [Paper] [Paper: PDF p. 18], [Figure 5c–d] | [Paper] [Paper: PDF p. 18], [Figure 5c–d] |

## 11 对结论的正确理解  
- **“Most models fail to beat linear probe”** 意味着：在 UNIv2 提供强大形态表征前提下，当前复杂架构（如 Transformer、GNN）并未带来普适性增益，其价值仅体现在特定基因子集（stromal/immune）和高质量数据（Xenium）上，而非整体性能跃升。  
- **“Universal gene-level ceiling”** 指：基因可预测性由形态-表达内在关联强度决定，TRIPLEX/DeepSpot 的 ∆PCC >0.1 仅出现在约 8–85 个基因（依队列而定），其余基因对所有模型均难预测，提示存在形态学不可见的调控层。  
- **“Xenium > Visium”** 是数据质量现象，非模型缺陷：Xenium 更高基因计数（e.g., marker genes mean=72.3 vs. 0.9）直接提升信噪比，使相同模型在 Xenium 上 PCC 提升近 3×，表明虚拟 ST 的终极瓶颈可能是实验技术分辨率。  
- **“Cross-tissue gap is largest”** 揭示生物学本质：不同癌种的形态-表达映射函数差异远大于技术批次效应，因此跨组织泛化需组织感知建模，而非简单数据增强。  
- **“Negative transfer in inter-cohort scaling”** 并非数据无效，而是警示：盲目混合异质组织会稀释组织特异性信号，未来需 tissue-aware learning 或 modular architecture。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Limited cancer/tissue scope** | STP-BENCH covers only 6 cancer types and 2 platforms (Visium/Xenium); lacks rare cancers, normal tissues, or emerging platforms (e.g., Stereo-seq) | Extend benchmark to additional tumor types, tissue contexts, and sequencing platforms for broader generalizability | [Paper] [Paper: PDF p. 20] |
| **Restricted gene panel** | Analyses focused on HMHVGs (200 genes) and 16 TME markers; systematic investigation of lowly expressed or functionally diverse genes remains open | Systematic investigation of lowly expressed or functionally diverse genes as an open direction | [Paper] [Paper: PDF p. 20] |
| **Spot-level granularity** | Evaluations performed at spot-level (aggregating multiple cells); cannot assess single-cell resolution prediction | Extend principles to evaluations at single-cell resolution with emerging sc-ST datasets and models | [Paper] [Paper: PDF p. 20] |
| **Encoder compatibility constraints** | 5 models (OmiCLIP, M2OST, etc.) retained native encoders due to architectural incompatibility with PFM drop-in | Develop more flexible encoder-agnostic architectures to enable full standardization | [Paper] [Paper: PDF p. 22–23], [Online Methods] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| **TRIPLEX/DeepSpot superiority is platform-contingent** | Their multi-scale design excels on Xenium’s high-count data but shows diminishing returns on Visium (Fig. 2c-d). This may reflect overfitting to Xenium’s technical characteristics (e.g., spot size, resolution), not inherent biological advantage. | If true, their “multi-scale” benefit is dataset-specific artifact, not general principle — misguiding architecture design for Visium-dominated clinical archives. | Re-train TRIPLEX/DeepSpot on Visium-only data with identical hyperparameters; ablate neighbor/global branches on Visium vs. Xenium to isolate scale contribution. Compare feature importance maps (e.g., Grad-CAM) on same tissue. | [Paper] [Paper: PDF p. 10], [Figure 2c–d]; “NCCHE-LUAD-Xenium... PCC = 0.579 for marker genes” vs. “NCCHE-LUAD-Visium... PCC = 0.191” |
| **singscore gene-set analysis ignores gene-gene correlations** | singscore computes rank-based scores per spot, discarding co-expression structure. A model could perfectly rank genes but fail to capture pathway-level covariance (e.g., immune activation signature). | Downstream tasks like pathway enrichment rely on correlation structure; high singscore PCC may not translate to functional coherence. | Replace singscore with PCA-based pathway scores or MOFA+ latent factors; compute correlation of predicted vs. true pathway loadings. Test enrichment of predicted signatures in known disease modules. | [Paper] [Paper: PDF p. 13]; “singscore... computes gene set activity independently for each spot” — no mention of covariance preservation. |
| **Cross-platform “improvement” may stem from metric bias** | Fig. 5b (right) shows some models gaining PCC in Cross-Platform (Visium→Xenium). But PCC is sensitive to dynamic range; Xenium’s higher counts may inflate correlation artificially. | Reporting PCC gain could mislead users into thinking Visium-trained models generalize *up* to Xenium, when they merely benefit from Xenium’s better signal. | Report MAE/SSIM alongside PCC for cross-platform; compute normalized root mean square error (NRMSE); visualize scatter plots (predicted vs. true) for matched genes across platforms. | [Paper] [Paper: PDF p. 32]; MAE defined but not shown in Fig. 5; SSIM used but not in robustness section [Paper] [Paper: PDF p. 11]. |
| **Cell2location evaluation uses expm1+clip, losing uncertainty** | Predicted log-expression is inverse-transformed, rounded, and clipped to integers before Cell2location, discarding probabilistic outputs from generative models (STFlow/Stem). | This nullifies the key advantage of generative models (uncertainty quantification), unfairly penalizing them in downstream tasks. | Feed generative model’s mean + variance to Cell2location’s probabilistic inference; or use ensemble predictions (e.g., 5 STFlow samples) as input. | [Paper] [Paper: PDF p. 35]; “predicted expression matrices were inverse-transformed using expm1... rounded and clipped to non-negative integers” — no handling of uncertainty. |

## 14 学到的知识  
- **评估即设计**：benchmark 的结构（统一 encoder、多粒度、跨域测试）本身就是最强的方法论启示——它迫使研究者思考“我的模型真正解决了什么问题”，而非追逐单一指标。  
- **基因是天然探针**：基因级 PCC 热图（Fig. 3a）比任何消融实验都更能揭示模型能力边界；stromal/immune genes are the litmus test for multi-scale reasoning.  
- **数据质量是隐性天花板**：Xenium 的 72.3 mean counts vs. Visium’s 0.9 for marker genes explains >80% of PCC difference (Fig. 2c-d) — investing in wet-lab tech may yield larger ROI than model architecture.  
- **鲁棒性有层级**：cross-institution ≈ manageable (ρ=0.86), cross-tissue ≈ hard (gap=−0.35), cross-platform ≈ unpredictable (mixed gains/losses) — guides deployment strategy.  
- **负迁移是常态**：inter-cohort scaling hurts performance (Fig. 5d) — future work must prioritize tissue-aware learning (e.g., adapters, mixture-of-experts) over brute-force data mixing.

## 15 与既有知识的连接  
- **候选连接/方法论连接**：本文的“统一 encoder + 多粒度评估”范式可直接迁移到 single-cell foundation models（如 scFoundation, scGPT）的 benchmarking 中，解决当前 scRNA-seq foundation model 评估同样存在的 encoder混杂、粒度粗放问题。  
- **候选连接/方法论连接**：TRIPLEX 的“local+neighbor+global”三支路设计为 spatial transcriptomics 中的 graph neural networks 提供了新思路——可将 neighbor branch 替换为 E(2)-invariant GNN（如 STFlow 使用），global branch 替换为 tissue-level attention，形成 hybrid GNN-Transformer 架构。  
- **候选连接/方法论连接**：STP-BENCH 的 cross-tissue generalization failure motivates perturbation prediction research: if morphology→expression mapping is tissue-specific, then *perturbation response* (e.g., drug effect) may be even more so — requiring tissue-contextualized perturbation models.  
- **弱连接/方法论连接**：本文强调的“morphology informs stromal/immune programs”与 cell state representation 领域的“morphological niches define cell states”假说一致，但未提供单细胞 resolution 证据，故为弱连接。  
- **弱连接/方法论连接**：multi-omics alignment 的挑战（e.g., H&E + proteomics）可借鉴本文的 cross-platform evaluation 设计，但本文未涉及多组学，故为弱连接。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Tissue-Aware Adapter for Virtual ST  
  **originating limitation/observation**: Inter-cohort scaling causes negative transfer (Fig. 5d); cross-tissue generalization gap is largest (Fig. 5b).  
  **core hypothesis**: A lightweight, tissue-specific adapter module inserted into a frozen backbone (e.g., TRIPLEX) can absorb tissue-specific morphology-expression mappings without disrupting shared features.  
  **delta from paper**: STP-BENCH uses fixed models per tissue; this adds learnable, low-rank tissue adapters (LoRA-style) to a unified backbone.  
  **initial method**: For each cancer type, train a 64-dim adapter (linear layer) on the fusion encoder output of TRIPLEX; freeze all other weights; optimize adapter + final head.  
  **validation**: Test zero-shot generalization to unseen tissue (e.g., train on LUAD+BRCA, test on GBM); compare to vanilla TRIPLEX and fine-tuned TRIPLEX.  
  **failure modes**: Adapter overfits to small tissue cohorts; fails to generalize to rare tissues with <10 slides.  
  **innovation status**: unverified  

- **name**: Morphology-Guided Gene Set Prior  
  **originating limitation/observation**: singscore ignores gene-gene correlations (Section 13); stromal genes (COL1A1, SPARC) are co-predicted (Fig. 3b), suggesting shared morphological drivers.  
  **core hypothesis**: Injecting known pathway structure (e.g., GO terms) as a prior into the loss function will improve gene-set level coherence without hurting gene-level PCC.  
  **delta from paper**: STP-BENCH evaluates gene sets post-hoc; this modifies training to explicitly optimize pathway-level agreement.  
  **initial method**: Add a loss term: $ \mathcal{L}_{\text{pathway}} = \sum_{\text{GO term } t} \text{MSE}(\text{pred\_scores}_t, \text{true\_scores}_t) $, where scores computed via singscore on mini-batches.  
  **validation**: Compare singscore PCC and pathway enrichment (GSEA) of predicted profiles on NCCHE-LUAD-Xenium; ensure gene-level PCC doesn’t drop >0.02.  
  **failure modes**: Prior dominates loss, collapsing gene-level diversity; computationally expensive for large GO libraries.  
  **innovation status**: unverified  

- **name**: Uncertainty-Aware Cell Deconvolution Interface  
  **originating limitation/observation**: Generative models’ uncertainty is discarded during Cell2location input (Section 13); their stochastic outputs are clipped to integers.  
  **core hypothesis**: Feeding generative model’s posterior samples (e.g., 5 STFlow outputs) as an ensemble to Cell2location will improve cell abundance estimation robustness.  
  **delta from paper**: STP-BENCH uses single-point predictions; this leverages generative models’ native uncertainty.  
  **initial method**: For each spot, run STFlow 5 times; feed the 5 expression vectors as “pseudo-replicates” to Cell2location’s batch inference; aggregate posterior abundances.  
  **validation**: Compare variance of cell abundance estimates (vs. ground truth) between ensemble and single-prediction; test on rare populations (plasma cells) where uncertainty matters most.  
  **failure modes**: Ensemble increases compute 5×; Cell2location may not be designed for replicate inputs, causing convergence issues.  
  **innovation status**: unverified