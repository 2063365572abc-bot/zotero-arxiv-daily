> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息  
- **Title**: OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning  
- **Authors**: Rabeya Tus Sadia, Qiang Ye, Qiang Cheng  
- **Affiliation**: Department of Computer Science / Mathematics, University of Kentucky  
- **Published**: arXiv preprint (2026-08-24), no formal journal/conference info provided in text [Paper: PDF p. 1]  
- **Code/data availability**: Not mentioned — “未核验”  
- **Core modalities**: RNA (gene expression), ADT (antibody-derived tags), histology (H&E image patches), spatial coordinates [Paper: PDF p. 3]  
- **Key datasets**: Four 10x Genomics CytAssist FFPE spatial proteomics benchmarks — Human Tonsil (4,194 spots), Human Breast Cancer (3,786), Human Glioblastoma (3,460), Human Tonsil with Add-on Antibodies (3,512) [Paper: PDF p. 11]  
- **Backbone**: KAN-GCN + CrossModalTransformer + UncertaintyMoE router [Paper: PDF p. 4–6]  
- **LLM**: Llama-3.3-70B via Groq API [Paper: PDF p. 9]  
- **Training objective**: End-to-end multi-task loss (reconstruction, contrastive, clustering, cell-type regularisation, imputation, uncertainty regularisation) [Equation 17, Paper: PDF p. 7]; OmicSync-R adds REINFORCE term [Equation 24, Paper: PDF p. 10]  

## 02 一句话总结  
OmicSync 是一个可靠性感知（reliability-aware）的空间多组学框架，通过联合建模软聚类分配、模态路由权重、MC-Dropout估计的表观路由不确定性（epistemic routing uncertainty）和空间邻域证据，生成结构化证据字典，并驱动五种策略的 Llama-3.3-70B 自然语言推理；其变体 OmicSync-R 进一步利用自动计算的推理质量分数（GR/CA/SC）作为 REINFORCE 奖励，闭环优化聚类潜表示，而无需反向传播至 LLM [Paper: PDF p. 1–2, 9–10].  

## 03 研究问题  
- 如何在空间多组学域发现（spatial domain discovery）中超越“黑箱式聚类分区”，提供每个 spot 级别可审计（auditable）、证据约束（evidence-constrained）的可靠性解释？[Paper: PDF p. 1]  
- 如何量化并解耦三种关键可靠性信号：软分配置信度（soft assignment confidence）、模态路由权重（modality-routing weights）、表观路由不确定性（epistemic routing uncertainty）？[Paper: PDF p. 2]  
- 能否将 LLM 推理质量（faithfulness）转化为非可微反馈信号，以闭环引导聚类潜空间学习，而不依赖梯度穿透语言模型？[Paper: PDF p. 9–10]  
- 在缺乏外部 ground-truth 细胞类型标注的临床 FFPE 数据上，如何设计伪标签正则化与跨模态对齐机制以提升鲁棒性？[Paper: PDF p. 4, 8]  

## 04 研究背景与发展路径  
- **起点**：现有空间多组学方法（如 GROVER、SpatialGlue、COSMOS）仅输出聚类分区，缺失可靠性指示、模态贡献归因与可解释性 [Paper: PDF p. 1–2].  
- **技术铺垫**：  
  - 图神经网络（GROVER 的 KAN-GCN）用于空间与特征邻接建模 [Paper: PDF p. 2–3];  
  - MoE 路由与 MC Dropout 已用于多模态融合与不确定性估计 [Paper: PDF p. 3];  
  - LLMs 在单细胞生物学中用于注释与摘要，但未与空间聚类模型耦合生成证据约束解释 [Paper: PDF p. 3].  
- **缺口识别**：无工作将模型内部可靠性信号（confidence/uncertainty/routing）结构化为 LLM 输入，并用其生成 spot-level 可验证解释；亦无工作将推理质量作为 RL 奖励闭环优化聚类 [Paper: PDF p. 3].  
- **本文路径**：以 GROVER 架构为基线 → 增加空间位置编码、跨模态 Transformer、不确定性 MoE、ClusteringHead/CellTypeHead/ImputationHeads → 提取三类可靠性信号 → 构建证据字典 → 驱动五策略 LLM 推理 → 设计 REINFORCE 奖励实现 OmicSync-R [Paper: PDF p. 4–10].  

## 05 论文识别的核心痛点  

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|-----------------------------|--------------------------|
| Opaque clustering outputs | Flat partition without reliability indicators, modality attribution, or justification for trustworthiness [Paper: PDF p. 1] | Downstream analyses treat all assignments as equally reliable, propagating errors especially at boundaries or degraded spots [Paper: PDF p. 1] | Abstract: “most spatial domain discovery methods provide only cluster assignments, without indicating assignment reliability, modality contributions, or why a domain decision should be trusted” [Paper: PDF p. 1]; Introduction: “This limitation is consequential because downstream analyses that treat all spot assignments as equally reliable may propagate clustering errors into biological conclusions” [Paper: PDF p. 1] |
| Lack of evidence-grounded interpretability | Existing explainability (e.g., attention, SHAP) reveals influential features but not spot-specific, multi-signal explanations grounded in confidence/uncertainty/routing [Paper: PDF p. 3] | No prior work couples LLM with structured, model-derived evidence from a trained spatial clustering model [Paper: PDF p. 3] | Section 2.2: “To our knowledge, however, existing work has not coupled an LLM with a trained spatial clustering model through structured, model-derived evidence to generate reliability-aware explanations for individual spots” [Paper: PDF p. 3] |
| Unstable reasoning-clustering coupling | Base OmicSync’s Task C operates post-hoc with no feedback to clustering objective; OmicSync-R’s reward is k-sensitive and spatial consistency degrades late in training [Paper: PDF p. 17, 18] | REINFORCE reward is computed per-spot, not neighbourhood-aware; SC declines in late epochs as soft assignments sharpen and local composition exerts less influence [Paper: PDF p. 17] | Section 9.6: “Spatial consistency declines in the late training phase (mean SC = 0.21 over epochs 400–575), suggesting that neighbourhood composition becomes less predictive of the final assignments as the soft assignments continue to sharpen” [Paper: PDF p. 17]; Discussion: “Improving this component may require a graph-level or neighbourhood-aware reward formulation” [Paper: PDF p. 18] |

## 06 核心思想  
- **可靠性信号三位一体**：将聚类头（ClusteringHead）输出的软分配置信度 $c_i$、MoE 路由门在 MC-Dropout 下的方差 $u_i$、以及平均路由权重 $\bar{g}_i$ 作为三个正交但互补的 spot-level 可靠性指标，共同构成解释基础 [Equations 3,13,14; Paper: PDF p. 4,6].  
- **证据字典驱动推理**：不引入新可训练模块，而是将上述信号 + 优势模态 top marker + 5-近邻组成成分，封装为结构化 prompt 输入 Llama-3.3-70B，强制其仅基于供给证据生成解释（禁用外部知识、基因名、引用等）[Paper: PDF p. 8–9].  
- **五策略解释范式**：Standard（直接因果）、Stepwise（五阶段结构化）、Counterfactual（模态/特征/邻域扰动）、Contrastive（vs. runner-up domain）、Uncertainty（可信度分级决策），覆盖不同解释需求 [Paper: PDF p. 8].  
- **REINFORCE 闭环优化**：将 GR/CA/SC 加权和 $R_i$ 作为 reward，通过 policy gradient 更新 ClusteringHead 的 soft assignment 分布 $q_i$，使高 faithfulness 解释对应的分配概率上升，从而间接优化潜空间几何 [Equations 19–24; Paper: PDF p. 9–10].  

## 07 方法总览  
OmicSync 是端到端可训练的多任务框架：输入为 RNA ($X_1$), ADT ($X_2$), histology ($X_3$), spatial coordinates ($C$)；经预处理后，各模态特征被送入共享 KAN-GCN 编码器（作用于空间/特征邻接图），再经 intra-modality attention 合并；三模态嵌入堆叠为 token 序列，输入 CrossModalTransformer（含 modality-type embedding）；输出经 UncertaintyMoE（MC-Dropout $T=10$ 次采样）融合，生成共享潜表示 $Z$；$Z$ 同时服务五大 head：ClusteringHead（Student’s t-kernel）、CellTypeHead（MLP 伪标签分类）、三路 ImputationHead（模态重建）、以及提取可靠性信号；信号汇入 Task C 生成解释；OmicSync-R 在训练中周期性激活 REINFORCE 更新 [Paper: PDF p. 3–10; Figure 1].  

## 08 核心模块拆解  

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|---------------------|------------------------|-----------------------------------|
| SpatialPositionEncoder | Encodes absolute spot coordinates $(c_{i,x}, c_{i,y})$ into sinusoidal positional bias $PE_m(c_i)$ added to modality features before GCN | To distinguish spots with identical molecular profiles but different tissue locations (e.g., germinal center edge vs. center), incorporating architectural context beyond molecules | Input: $c_i \in \mathbb{R}^2$; Output: $PE_m(c_i) \in \mathbb{R}^{d_m}$ [Equation 7, Paper: PDF p. 5] | “This design allows the model to incorporate spatial context and tissue architecture that are not captured by molecular composition alone” [Paper: PDF p. 5] | Loss of spatial contextual discrimination; e.g., edge/center spots in homogeneous regions become indistinguishable, harming domain boundary resolution [Paper: PDF p. 5] |
| UncertaintyMoE | Fuses cross-modally enriched embeddings $e'_1,e'_2,e'_3$ via MC-Dropout gating network; outputs mean routing vector $\bar{g}_i$, epistemic uncertainty $u_i$, and fused latent $z_i$ | To enable interpretable modality attribution ($\bar{g}_i$) and quantifiable stability of that attribution ($u_i$), critical for evidence-constrained reasoning | Input: $\bar{e}_i = \frac{1}{3}\sum_{m=1}^3 e'_{m,i}$; Output: $\bar{g}_i \in [0,1]^3$, $u_i \in \mathbb{R}_{\geq0}$, $z_i \in \mathbb{R}^d$ [Equations 10–14, Paper: PDF p. 6] | “The mean gate values $\bar{g}_i$ ... are used as an interpretable proxy for the relative contribution... The scalar $u_i$ ... is defined as the epistemic routing uncertainty” [Paper: PDF p. 6] | Removal eliminates both modality-routing weights and epistemic uncertainty signals, breaking Task C evidence dictionary and disabling OmicSync-R reward; forces reliance on unimodal or heuristic fusion [Paper: PDF p. 6] |
| ClusteringHead | Projects $L2$-normalized latent $z_i$ onto $K$ learnable centroids $\{\mu_k\}$ using Student’s t-kernel to produce soft assignment $q_{ik}$ and confidence $c_i = \max_k q_{ik}$ | To provide probabilistic, differentiable clustering output essential for REINFORCE update and confidence-based reasoning | Input: $\hat{z}_i = z_i/\|z_i\|_2$; Output: $q_{ik} \in [0,1]$, $c_i \in [0,1]$ [Equation 15, Paper: PDF p. 7] | “The predicted domain for spot $i$ is $\hat{k}_i = \arg\max_k q_{ik}$, and the assignment confidence is defined as $c_i = \max_k q_{ik}$” [Paper: PDF p. 7] | Removes soft assignment distribution, making REINFORCE impossible; collapses confidence signal needed for CA metric and Stepwise/Uncertainty reasoning strategies [Paper: PDF p. 7, 9] |
| CellTypeHead | Two-layer MLP predicting pseudo-cell-type logits from $Z$, trained on Leiden-derived RNA community labels (70% used) | To act as semi-supervised regularizer preserving local pseudo-cell-type structure in shared latent space, improving robustness without external annotations | Input: $z_i$; Output: logits for $L$ pseudo-classes [Paper: PDF p. 7] | “We use a subset of these Leiden-derived labels as auxiliary training targets... serves as a semi-supervised consistency regularizer” [Paper: PDF p. 8] | Weakens latent space alignment to cellular organization; Table 2 shows maps exhibit “locally structured spatial patterns”, implying CellTypeHead contributes to spatial coherence [Paper: PDF p. 8, 13] |
| Task C Reasoning Module | Post-hoc evidence-constrained LLM module generating natural-language reports $J^{(r)}_i$ for queried spots $i \in S$ using five prompt templates | To translate quantitative reliability signals into human-auditable, spot-level justifications, enabling responsible interpretation | Input: Structured evidence dictionary (domain, $c_i$, $\bar{g}_i$, $u_i$, top markers, 5-NN composition); Output: $J^{(r)}_i$ [Paper: PDF p. 8] | “Task C aims to translate OmicSync’s quantitative spot-level outputs into human-readable explanations while preserving faithfulness to the underlying model evidence” [Paper: PDF p. 8] | Eliminates all natural-language explanations; renders OmicSync non-auditable at spot level, reverting to opaque clustering [Paper: PDF p. 8] |

## 09 关键公式与符号  

| ID | Formula | Meaning | Key symbols | Source |
|----|---------|---------|-------------|--------|
| Eq. 2 | $\sum_{k=1}^K q_{ik} = 1, i = 1, \dots, N$ | Soft assignment matrix $Q$ rows sum to 1 (probability simplex) | $q_{ik}$: probability spot $i$ belongs to domain $k$ | [Paper: PDF p. 3] |
| Eq. 3 | $\hat{k}_i = \arg\max_{1\leq k\leq K} q_{ik},\ c_i = \max_{1\leq k\leq K} q_{ik}$ | Hard assignment $\hat{k}_i$ and assignment confidence $c_i$ | $c_i$: soft assignment confidence for spot $i$ | [Paper: PDF p. 4] |
| Eq. 4 | $\sum_{m=1}^3 G_{im} = 1, i = 1, \dots, N$ | Modality-routing matrix $G$ rows sum to 1 (simplex constraint) | $G_{im}$: routing weight for modality $m$ at spot $i$ | [Paper: PDF p. 4] |
| Eq. 7 | $PE_m(c_i) = W^{PE}_m [\sin(c_{i,x}f), \cos(c_{i,x}f), \sin(c_{i,y}f), \cos(c_{i,y}f)]^\top$ | Sinusoidal 2D positional encoding for spot $i$ | $f$: fixed log-spaced frequency vector; $W^{PE}_m$: learned projection | [Paper: PDF p. 5] |
| Eq. 11 | $g_{i,t} = \text{softmax}(W_g \cdot \text{Dropout}_t(\bar{e}_i)) \in [0,1]^3$ | Routing vector for spot $i$ at MC-Dropout trial $t$ | $\text{Dropout}_t$: stochastic mask; $\bar{e}_i$: averaged cross-modal token | [Paper: PDF p. 6] |
| Eq. 13 | $u_i = \sum_{m=1}^3 \text{Var}_{t=1,\dots,T}[g_{i,m,t}]$ | Epistemic routing uncertainty for spot $i$ | $g_{i,m,t}$: $m$-th component of $g_{i,t}$; $T=10$: number of MC samples | [Paper: PDF p. 6] |
| Eq. 14 | $\tilde{g}_i = \frac{\bar{g}_i \odot \mathbf{1}[\bar{g}_i \geq \tau]}{\|\bar{g}_i \odot \mathbf{1}[\bar{g}_i \geq \tau]\|_1}$ | Thresholded & normalized routing vector for fusion | $\tau = 0.3$: pruning threshold; $\odot$: element-wise product | [Paper: PDF p. 6] |
| Eq. 15 | $q_{ik} = \frac{(1 + \|\hat{z}_i - \mu_k\|^2_2)^{-1}}{\sum_{k'=1}^K (1 + \|\hat{z}_i - \mu_{k'}\|^2_2)^{-1}}$ | Student’s t-distribution kernel for soft assignment | $\hat{z}_i$: $L2$-normalized latent; $\mu_k$: learnable centroid | [Paper: PDF p. 7] |
| Eq. 18 | $GR_i = \frac{|M_i \cap J_i|}{|M_i|}$ | Grounding rate: fraction of supplied marker names ($M_i$) appearing in justification ($J_i$) | $M_i$: set of named marker features in evidence; $J_i$: set of marker names detected in $J^{(r)}_i$ | [Paper: PDF p. 9] |
| Eq. 19 | $a_i \sim \text{Categorical}(q_i)$ | Sampling candidate domain label $a_i$ from ClusteringHead’s soft distribution $q_i$ | $q_i \in [0,1]^K$: soft assignment for spot $i$ | [Paper: PDF p. 9] |
| Eq. 20 | $R_i = w_1 GR_i + w_2 CA_i + w_3 SC_i$ | Composite reasoning-quality reward for spot $i$ | $w_1=0.5, w_2=0.3, w_3=0.2$: weights; $CA_i, SC_i$: confidence alignment, spatial consistency | [Paper: PDF p. 9] |
| Eq. 22 | $b_t = \alpha b_{t-1} + (1-\alpha)\bar{R}_t,\ \alpha = 0.9$ | Exponential moving average baseline for REINFORCE variance reduction | $b_t$: baseline at epoch $t$; $\bar{R}_t$: mean reward over sample $S_R$ | [Paper: PDF p. 9] |
| Eq. 23 | $L_{\text{reinforce}} = -\frac{1}{|S_R|}\sum_{i \in S_R} \text{sg}(R_i - b_t) \log q_{i,a_i}$ | REINFORCE loss for ClusteringHead | $\text{sg}(\cdot)$: stop-gradient; $a_i$: sampled domain; $q_{i,a_i}$: probability of $a_i$ under $q_i$ | [Paper: PDF p. 10] |
| Eq. 24 | $L_{\text{OmicSync-R}} = L_{\text{OmicSync}} + \lambda_R L_{\text{reinforce}}$ | Extended training objective for OmicSync-R | $\lambda_R = 0.02$: weight of REINFORCE term | [Paper: PDF p. 10] |

## 10 实验设计与证据链  

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|-------------------------|-------------------------------|--------|
| Table 1 clustering rank | OmicSync achieves superior unsupervised spatial domain clustering across four CytAssist FFPE datasets | Compared to GROVER, MISO, SpatialGlue, COSMOS on ARI/NMI/FMI/SilC/AMI/Jaccard/CHI/Purity/DBI; best result over $K \in \{6,\dots,10\}$ reported; uses curated pseudo-reference labels from GROVER [Paper: PDF p. 11] | Best avg. rank on Tonsil (1.44), Glioblastoma (1.78), Tonsil Add-on (1.22); 2nd on Breast Cancer (2.33); best ARI on all four | OmicSync learns latent representations better aligned with reference partitions and exhibiting improved intrinsic cluster separation (higher CHI, lower DBI) | That OmicSync generalizes to non-FFPE or higher-resolution platforms (Xenium/MERFISH) — not evaluated [Paper: PDF p. 18] | [Paper: PDF p. 12] |
| Table 2 & Figure 2 | CellTypeHead provides effective semi-supervised regularisation, not standalone annotation | CellTypeHead trained on 70% Leiden-derived RNA pseudo-labels; maps visualised qualitatively; no external ground-truth used | Maps show locally structured patterns: Glioblastoma (coherent regions), Tonsil (mixed domains), Tonsil Add-on (fine-grained) | Auxiliary classification encourages shared latent space to retain local pseudo-cell-type organisation | That CellTypeHead achieves high accuracy on true cell-type labels — explicitly stated as not evaluated [Paper: PDF p. 8, 13] | [Paper: PDF p. 13] |
| Table 3 & Figure 3A | Stepwise reasoning strategy yields highest joint faithfulness | Five strategies (Standard, Stepwise, Counterfactual, Contrastive, Uncertainty) evaluated on same 40 spots (10/dataset); metrics GR/CA/SC computed automatically | Stepwise: GR=1.00, CA=1.00, SC=0.975; Uncertainty: GR=0.074, CA=1.00 | Structured five-stage format effectively anchors LLM to all supplied evidence types | That Stepwise is universally optimal across all future datasets or modalities — only tested on four FFPE datasets | [Paper: PDF p. 13, 21] |
| Table 4 & Figure 3B,C | Dataset-level reasoning quality correlates with clustering performance | Aggregated GR/CA/SC/Avg. unc. across five strategies per dataset (10 spots/dataset) | Tonsil Add-on: highest SC (0.84), lowest Avg. unc. (0.0526), best rank (1.22); Tonsil: highest CA (0.94) | Stronger clustering structure (low uncertainty, high rank) associates with more spatially consistent and well-calibrated explanations | That low Avg. unc. *causes* high SC — correlation ≠ causation; Tonsil has high unc. but strong rank [Paper: PDF p. 15] | [Paper: PDF p. 13, 21] |
| Table 5 | High-confidence spots exhibit lower uncertainty and higher spatial homogeneity | Three-tier audit: High ($c_i \geq 0.35, n=9$), Medium ($0.20\leq c_i<0.35, n=23$), Low ($c_i<0.20, n=8$) | High tier: Avg. unc.=0.034, Spatial hom.=75.6%; Low tier: Avg. unc.=0.111 (3.3×), Spatial hom.=60.0% | Numerical reliability signals reflect meaningful variation in assignment stability and local spatial support | That confidence $c_i$ and uncertainty $u_i$ are interchangeable — authors note moderate negative correlation ($r=-0.42$), confirming they are distinct [Paper: PDF p. 15] | [Paper: PDF p. 15, 21] |
| Table 6 & 7 | OmicSync-R’s REINFORCE reward improves clustering on challenging dataset | OmicSync-R trained on Human Breast Cancer only; 22 reasoning-update steps (epochs 50–575); compared to base OmicSync and GROVER at $k=10$ | ARI: 45.73→46.72 (+0.99); improves 8/9 metrics; surpasses GROVER on 6/9 | Reasoning-quality scores can serve as usable non-differentiable auxiliary training signal for spatial clustering | That OmicSync-R is universally beneficial — k-sensitivity shown (benefit concentrated at $k=10$); not evaluated on other datasets [Paper: PDF p. 17] | [Paper: PDF p. 16–17] |

## 11 对结论的正确理解  
- OmicSync 的“可靠性感知”指同时输出三类**正交信号**：$c_i$（分配分布尖锐度）、$\bar{g}_i$（模态权重分布）、$u_i$（路由决策稳定性），三者共同构成解释基础，而非单一“可信度分数” [Paper: PDF p. 2, 4, 6].  
- Task C 的“证据约束”是**严格的操作定义**：LLM 仅接收模型导出的五类证据（domain, $c_i$, $\bar{g}_i$, $u_i$, markers, 5-NN），且系统提示禁止引入任何未供给的实体（基因名、蛋白名、文献等），故 GR 可自动计算 [Paper: PDF p. 8–9].  
- OmicSync-R 的 REINFORCE 更新**不修改 LLM 或 prompt**，仅调整 ClusteringHead 的 $q_i$ 分布，使高 $R_i$ 的 $a_i$ 更可能被采样；reward 是标量，不涉及文本梯度 [Equation 23; Paper: PDF p. 9–10].  
- 所有评估均基于**curated pseudo-reference labels**（源自 GROVER），非专家手工标注，故 ARI/NMI 等反映与该特定参考分区的一致性，非绝对生物学真值 [Paper: PDF p. 11].  
- “Best average rank” is computed across **nine metrics**, not a single score; OmicSync wins on ARI universally but trades off Purity on Tonsil (57.71 vs. GROVER’s 69.4), interpreted as favoring compact clusters over majority-label dominance [Paper: PDF p. 12].  

## 12 作者明确承认的限制  

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Post-hoc nature of base Task C | “Task C operates post hoc: it consumes model-derived evidence but provides no feedback to the clustering objective” [Paper: PDF p. 9] | OmicSync-R addresses this via REINFORCE, but its reward is limited to three computable metrics and is k-sensitive [Paper: PDF p. 18] | [Paper: PDF p. 18] |
| REINFORCE reward limitations | Reward exhibits sensitivity to number of clusters $k$ (benefit concentrated at $k=10$); spatial consistency (SC) degrades late in training; requires repeated LLM calls, making it resource-intensive | Investigate graph-level or neighbourhood-aware reward formulations; explore reward annealing or multi-$k$ training; develop amortised reward models or smaller verifier models to reduce cost [Paper: PDF p. 18] | [Paper: PDF p. 18] |
| Pseudo-label dependency of Task B | “Task B pseudo-labels are RNA-derived, so the reported analysis evaluates the regularisation benefit... rather than external classification accuracy” [Paper: PDF p. 18] | Extend framework to additional modalities (ATAC-seq, spatial metabolomics) and higher-resolution platforms (Xenium, MERFISH) [Paper: PDF p. 18] | [Paper: PDF p. 18] |
| Evidence scope constraint | “The reasoning module is constrained by the evidence supplied by the model, so its explanations are limited to the five supplied evidence types... and inherit any upstream uncertainty in those signals” [Paper: PDF p. 18] | Future work will extend OmicSync-R to all four datasets and investigate improved reward formulations [Paper: PDF p. 18] | [Paper: PDF p. 18] |
| Resource intensity of OmicSync-R | “Because OmicSync-R requires repeated LLM-based explanation generation and reward evaluation during training, this reasoning-guided variant is more resource-intensive than base OmicSync” [Paper: PDF p. 11] | Use cached reasoning evaluations, smaller verifier models, or amortised reward models to reduce computational cost [Paper: PDF p. 18] | [Paper: PDF p. 11, 18] |

## 13 批判性分析  

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| The "epistemic routing uncertainty" $u_i$ is computed solely from variance of MoE gate outputs under MC-Dropout, but the gate network itself is not end-to-end trained for uncertainty calibration; it's a byproduct of dropout applied to a deterministic router | $u_i$ may correlate poorly with true epistemic uncertainty if the gate network lacks proper Bayesian priors or if dropout rate/depth is suboptimal; high $u_i$ could reflect model confusion rather than genuine uncertainty about modality relevance | Misleading uncertainty estimates undermine the core reliability claim and compromise Uncertainty strategy explanations and CA metric | Calibrate $u_i$ against held-out perturbation experiments (e.g., ablate RNA/ADT/histology and measure assignment shift) or compare with ensemble-based uncertainty estimates | [Paper: PDF p. 3, 6]; Section 2.3 cites MC Dropout as approximation, but no calibration evidence provided |
| The adaptive $n_{\text{hops}}$ mechanism (2 for homogeneous, 1 for heterogeneous tissue) relies on precomputed RNA neighbor similarity >0.6, but this threshold is arbitrary and not validated across diverse tissue architectures | Threshold of 0.6 may misclassify tissues; e.g., inflamed stroma might have high RNA similarity but require fine-grained boundaries, leading to over-smoothing | Suboptimal $n_{\text{hops}}$ harms contrastive learning: too large excludes true negatives in heterogeneous regions, too small treats similar spots as negatives in homogeneous regions | Sweep $n_{\text{hops}}$ and RNA similarity thresholds on validation splits; report ARI/SilC trade-off curves; test on synthetic spatial data with known ground-truth heterogeneity | [Paper: PDF p. 7]; described as heuristic, no ablation or sensitivity analysis shown |
| OmicSync-R’s reward $R_i$ weights grounding (GR) most heavily (0.5), but GR is only defined for RNA/ADT markers, excluding histology evidence which dominates some cases (e.g., Tonsil Spot 420) | For image-dominant spots, GR is undefined or excluded, making $R_i$ unreliable and potentially biasing REINFORCE toward RNA/ADT-driven assignments | Undermines fairness across modalities and risks degrading performance on histology-critical tasks (e.g., tumor grading) | Report $R_i$ breakdown per modality dominance group; design modality-aware reward weights; or develop image-feature grounding metric (e.g., patch similarity) | [Paper: PDF p. 9, 13, 15]; Table 3 shows Uncertainty strategy has GR=0.074 by design, yet receives full CA=1.00, highlighting GR’s modality limitation |
| The five-nearest-spot neighbourhood for SC metric and evidence composition is computed in physical space, but spatial coordinates are subject to registration errors in FFPE tissue, and biological neighbourhood may be better defined by transcriptomic similarity | Physical 5-NN may include transcriptionally dissimilar spots due to tissue distortion, causing SC to penalize correct assignments based on flawed spatial definition | Compromises validity of SC metric and weakens the spatial consistency signal used in Stepwise/Uncertainty strategies | Compare SC computed on physical vs. transcriptomic (e.g., RNA k-NN) neighbourhoods; report correlation between physical distance and RNA similarity per dataset | [Paper: PDF p. 8, 9]; Section 4.1.1 notes FFPE preprocessing but no discussion of coordinate uncertainty |

## 14 学到的知识  
- **可靠性信号工程**：软分配置信度（$c_i$）、模态路由权重（$\bar{g}_i$）、表观路由不确定性（$u_i$）可被解耦设计并联合用于解释，其中 $u_i$ 通过 MC-Dropout 在 MoE 门上估计，是轻量级贝叶斯近似实践 [Paper: PDF p. 2, 6].  
- **证据约束 LLM 的可行架构**：无需微调 LLM，仅通过严格 prompt engineering (forbid external entities) + structured evidence dictionary + automatic faithfulness metrics (GR/CA/SC) 即可实现可审计的自然语言解释 [Paper: PDF p. 8–9].  
- **REINFORCE for multimodal representation learning**：将不可微的下游 task（reasoning quality）作为 reward 优化上游 encoder/clustering head 是可行的，且能提升 clustering metrics (ARI+0.99)，关键在于 reward design (weighted GR/CA/SC) 和 baseline (EMA) [Paper: PDF p. 9–10, 17].  
- **Adaptive spatial contrastive learning**：根据组织同质性（RNA neighbor similarity）动态设置 contrastive exclusion radius ($n_{\text{hops}}$) 可缓解 ARI/SilC 权衡，比固定 radius 更鲁棒 [Paper: PDF p. 7].  
- **Pseudo-label regularisation efficacy**：即使无真实细胞类型标签，Leiden-derived RNA pseudo-labels used in auxiliary CellTypeHead improve latent space coherence, evidenced by structured spatial prediction maps (Fig. 2) [Paper: PDF p. 8, 13].  

## 15 与既有知识的连接  
- **single-cell foundation models**: OmicSync’s UNI histology encoder and RNA/ADT PCA preprocessing align with scFoundation practices; however, it lacks explicit foundation model fine-tuning or masked autoencoding pretraining, focusing instead on supervised multi-head fusion [Paper: PDF p. 5, 7].  
- **spatial transcriptomics**: Directly extends ST methods (e.g., STAGATE, GraphST) by adding protein/histology modalities and reliability signals, but unlike BayesSpace or spatial deep learning, it prioritizes cross-modal alignment over probabilistic spatial priors [Paper: PDF p. 2, 11].  
- **graph neural networks**: Builds on GROVER’s KAN-GCN backbone, confirming KAN’s efficacy for spatial/feature graphs; OmicSync’s contribution is adding spatial position encoding (Eq. 7) and UncertaintyMoE, not novel GNN architecture [Paper: PDF p. 2–3, 5].  
- **multi-omics**: Advances beyond MISO (multi-scale) and SpatialGlue (cross-attention) by introducing uncertainty-aware MoE routing and evidence-constrained reasoning, addressing the “why” beyond “what” of multi-omics integration [Paper: PDF p. 2, 4].  
- **biomedical AI**: Embodies responsible AI principles (auditability, uncertainty quantification) for clinical FFPE data, but unlike diagnostic AI, it targets domain discovery, not disease classification; weak connection to perturbation prediction (no perturbation modeling) [Paper: PDF p. 1, 11].  
- **perturbation prediction / cell state representation / cross-modal alignment**: No direct implementation; OmicSync infers static domains, not dynamic states or perturbations; cross-modal alignment is achieved via CrossModalTransformer and MoE, but not evaluated on alignment metrics (e.g., CCA, RV coefficient) — weak connection/methodology connection.  

## 16 研究想法  

- **name**: Histology-anchored uncertainty calibration  
  **originating limitation/observation**: $u_i$ is computed from MoE gate variance but may not reflect true uncertainty for histology-dominant spots where GR is undefined and SC relies on physical NN [Paper: PDF p. 9, 13, 15]; Table 3 shows Uncertainty strategy sacrifices GR for CA, exposing modality gap.  
  **core hypothesis**: Epistemic uncertainty for histology should be calibrated against image-patch reconstruction fidelity or UNI embedding stability under perturbations (e.g., noise, occlusion), not just gate variance.  
  **delta from paper**: Replace scalar $u_i$ with modality-specific uncertainty: $u_i^{\text{hist}}$ from UNI embedding variance under patch corruption, $u_i^{\text{RNA/ADT}}$ from MoE gate variance.  
  **initial method**: For histology patches, apply random masking (20%) and compute variance of UNI CLS embeddings across 10 corruptions; fuse with MoE $u_i$ via weighted average.  
  **validation**: Test on Tonsil Spot 420 (image-dominant): higher $u_i^{\text{hist}}$ should correlate with lower SC and CA in Uncertainty strategy; ablate corruption to confirm necessity.  
  **failure modes**: Corruption may not mimic real FFPE artifacts (e.g., folding, staining variation); UNI may be insensitive to subtle morphological changes.  
  **innovation status**: unverified  

- **name**: Neighborhood-aware REINFORCE reward  
  **originating limitation/observation**: SC degrades late in OmicSync-R training because reward is per-spot, ignoring spatial context; authors propose “graph-level or neighbourhood-aware reward formulation” [Paper: PDF p. 17, 18].  
  **core hypothesis**: A reward computed over local neighbourhoods (e.g., agreement of $R_i$ within 5-NN) will better preserve spatial coherence than per-spot $R_i$.  
  **delta from paper**: Replace $R_i$ with $R_i^{\text{nb}} = \frac{1}{5}\sum_{j \in \mathcal{N}_5(i)} R_j$, where $\mathcal{N}_5(i)$ is physical 5-NN; use $R_i^{\text{nb}}$ in Eq. 23.  
  **initial method**: During REINFORCE update, for each $i \in S_R$, compute $R_i^{\text{nb}}$ using current $R_j$ of its 5 neighbours; apply same EMA baseline.  
  **validation**: On Human Breast Cancer, monitor SC trajectory: expect sustained high SC (>0.4) throughout training vs. current decline to 0.21; check if ARI gain persists.  
  **failure modes**: May over-smooth, reducing fine-grained domain resolution at tumour-stroma boundaries; requires careful NN definition (physical vs. transcriptomic).  
  **innovation status**: unverified  

- **name**: Cross-modal alignment verifier  
  **originating limitation/observation**: Task C explanations inherit upstream uncertainty; no mechanism verifies if $\bar{g}_i$ truly reflects modality contribution, only that it’s used as a proxy [Paper: PDF p. 13, 18]; “modality-routing weights are used as proxies rather than causal measures” [Paper: PDF p. 13].  
  **core hypothesis**: A lightweight verifier model (e.g., 2-layer MLP) trained to predict $\bar{g}_i$ from cross-modal embedding similarities can detect misaligned routing and flag low-faithfulness spots.  
  **delta from paper**: Add verifier head that takes $e'_1,e'_2,e'_3$ and outputs $\hat{g}_i$; minimize $\|\hat{g}_i - \bar{g}_i\|_1$; use verifier confidence as additional reliability signal.  
  **initial method**: Train verifier on frozen OmicSync features; threshold verifier loss to define “high-faithfulness routing” spots for targeted reasoning.  
  **validation**: On 40 explained spots, correlate verifier loss with GR/SC: high loss should predict low GR for RNA/ADT spots and low SC for image spots.  
  **failure modes**: Verifier may overfit to training data; adds computational overhead, countering goal of lightweight reliability.  
  **innovation status**: unverified