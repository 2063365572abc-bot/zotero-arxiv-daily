> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning | [Paper] [Paper: PDF p. 1] |
| Authors | Rabeya Tus Sadia, Qiang Ye, Qiang Cheng | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv (preprint) | [Paper] [Paper: PDF p. 1] |
| Year | 2026 | [Paper] [Paper: PDF p. 1] |
| Core task | Spatial domain clustering + per-spot reliability auditing via evidence-constrained LLM reasoning | [Paper] [Paper: PDF p. 1–2] |
| Key innovation | Coupling of uncertainty-aware MoE routing, multi-strategy LLM reasoning, and REINFORCE-guided latent space refinement — all grounded in model-derived per-spot signals | [Paper] [Paper: PDF p. 2, 7, 9–10] |
| Target modalities | RNA (gene expression), ADT (surface proteins), histology (H&E image patches), spatial coordinates | [Paper] [Paper: PDF p. 3–5] |
| Datasets | Four 10x CytAssist FFPE spatial proteomics datasets: Human Tonsil, Human Breast Cancer, Human Glioblastoma, Human Tonsil with Add-on Antibodies | [Paper] [Paper: PDF p. 11] |
| Baselines | GROVER, MISO, SpatialGlue, COSMOS | [Paper] [Paper: PDF p. 11] |
| Evaluation metrics (Task A) | ARI, NMI, FMI, SilC, AMI, Jaccard, CHI, Purity, DBI | [Paper] [Paper: PDF p. 11] |
| Evaluation metrics (Task C) | Grounding Rate (GR), Confidence Alignment (CA), Spatial Consistency (SC) | [Paper] [Paper: PDF p. 9, 13] |
| Code/data availability | Not stated in text; no URL or repository mentioned | Not assessable from supplied material |

## 02 一句话总结

OmicSync 是首个将空间多组学聚类、模型内生可靠性信号提取（软分配置信度、模态路由权重、MC-Dropout 路由不确定性）、五策略证据约束型 LLM 推理、以及基于 REINFORCE 的推理质量反馈闭环训练（OmicSync-R）统一于单框架的可信空间域发现方法；它不追求“黑箱聚类+后验解释”，而是构建从聚类头输出到自然语言审计的可追溯证据链，使每个空间点的域分配具备可验证的分子依据、模态归因与空间支持；其局限在于推理不可微、奖励设计对 k 敏感、且仅在 Human Breast Cancer 上验证了闭环有效性。

## 03 研究问题

现有空间多组学聚类方法（如 GROVER、SpatialGlue）仅输出扁平化域划分，无法回答三个关键临床/分析级问题：（1）哪些spot的分配是可靠的？（2）哪个模态（RNA/ADT/图像）主导了该分配决策？（3）为何应信任该分配？——这导致下游分析（如差异表达、配体-受体推断）可能被边界spot或低质量数据引入的错误分配系统性污染。  
作者洞察到：可靠性不能仅靠聚类指标（如ARI）全局评估，而需在spot粒度上耦合**可计算的内部信号**（confidence, routing uncertainty, modality weight）与**可审计的外部表达**（LLM生成的自然语言报告）。  
因此，论文路径不是改进聚类算法本身，而是构建一个“聚类-信号提取-证据构造-推理生成-（可选）反馈优化”的全栈式可靠性增强范式。

## 04 研究背景与发展路径

空间多组学分析已从单模态（RNA-only）[9] → 图神经网络整合空间邻域（STAGATE, GraphST）[10–11] → 多模态融合（GROVER, SpatialGlue, COSMOS）[5–8]，但所有阶段均止步于“聚类结果输出”。解释性仍停留在注意力热图或SHAP等特征归因层面 [12]，缺乏spot级、多信号协同、自然语言可读的因果性解释。LLM在单细胞中已有应用（细胞类型注释、通路摘要）[13–15]，但未与空间聚类模型耦合。OmicSync 的发展路径是：以 GROVER 的 KAN-GCN 骨干为基线 [5]，在其上叠加五大新组件——空间位置编码、跨模态Transformer、不确定性MoE路由、ClusteringHead/CellTypeHead/ImputationHeads三头结构、以及证据约束推理模块——从而将“鲁棒表征学习”升级为“鲁棒+可审计+可反馈”的闭环分析。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| Opaque clustering outputs | Downstream analyses treat all spot assignments as equally reliable, propagating errors into biological conclusions [Paper] [Paper: PDF p. 1] | Existing methods return only flat partitions without reliability indicators [Paper] [Paper: PDF p. 1] | [Paper] [Paper: PDF p. 1]: “most spatial domain discovery methods provide only cluster assignments, without indicating assignment reliability, modality contributions, or why a domain decision should be trusted.” |
| Lack of spot-level interpretability | No mechanism to explain *why* a specific spot is assigned to domain *k*, nor which molecular evidence supports it | Explainability remains underdeveloped; attention/SHAP reveal influential features but not spot-specific, multi-signal grounded explanations [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 3]: “they generally do not provide spot-specific explanations of clustering assignments grounded in multiple internal reliability signals.” |
| Modality contribution ambiguity | Cannot quantify how much RNA vs. ADT vs. histology contributed to a given assignment | Prior multimodal methods lack interpretable modality-routing mechanisms [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 4]: “modality-routing weights that indicate the relative weighting of RNA, ADT, and histology in the fused representation.” |
| Uncertainty unquantified per spot | No estimate of epistemic uncertainty for individual spot assignments, hindering trust calibration | Epistemic uncertainty estimation is computationally challenging in deep models [Paper] [Paper: PDF p. 3] | [Paper] [Paper: PDF p. 2]: “Quantifying how confident the model is in each assignment [...] is therefore not merely desirable but crucial [...]” |

## 06 核心思想

OmicSync 的核心思想是：**将聚类模型自身产生的中间信号（而非原始输入）作为唯一证据源，构造结构化证据字典，并以此严格约束LLM生成spot级可靠性报告；再将报告的质量（faithfulness）作为非可微奖励，通过REINFORCE反向塑造聚类头的latent representation**。  
这不是“用LLM解释黑箱”，而是“让聚类头显式产出可解释信号 → 让LLM只消费这些信号 → 让LLM的输出质量反过来优化聚类头”。其哲学基础是：**可审计性（auditability）必须源于信号可追溯性（traceability），而可追溯性要求证据源与推理目标在计算图中同构**。Figure 1 的架构图即体现此思想：所有箭头最终汇聚于“structured evidence dictionary”这一枢纽，再单向流向reasoning module。

## 07 方法总览

OmicSync 是端到端可训练框架，包含六大核心组件：（1）**预处理**：RNA（log-normalized PCA）、ADT（CLR-normalized PCA）、Histology（UNI ViT-L/16 embedding）；（2）**空间位置编码**：2D正弦位置编码注入坐标先验；（3）**KAN-GCN模态编码器**：对每个模态分别施加空间图卷积与特征图卷积，再经intra-modality attention融合；（4）**CrossModalTransformer**：将三模态token堆叠为序列，通过self-attention实现跨模态上下文富集；（5）**UncertaintyMoE**：MC-Dropout下评估gating network，输出mean routing vector（模态权重）与epistemic uncertainty（方差）；（6）**多头输出**：ClusteringHead（Student’s t-distribution soft assignment）、CellTypeHead（Leiden伪标签监督）、ImputationHeads（掩码重建自监督）。OmicSync-R 在此基础上，将ClusteringHead的soft assignment分布采样后送入reasoning module，用GR/CA/SC加权得分作为REINFORCE reward，更新ClusteringHead参数。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| SpatialPositionEncoder | 将2D坐标映射为4F维正弦编码并投影，加至各模态特征前 | 解决“相同分子谱但不同空间位置”（如生发中心边缘vs中心）的表示歧义，注入组织架构先验 | Input: spot coordinate *cᵢ* ∈ ℝ²; Output: *PEₘ(cᵢ)* ∈ ℝᵈᵐ | [Paper] [Paper: PDF p. 5]: “This design allows the model to incorporate spatial context and tissue architecture that are not captured by molecular composition alone.” | 移除将导致空间同质区域（如tonsil germinal center）内spot区分能力下降，ARI/SilC在homogeneous dataset上显著恶化 [Paper] [Paper: PDF p. 7] |
| UncertaintyMoE | MC-Dropout下运行gating network，输出mean routing vector *ḡᵢ* 和epistemic uncertainty *uᵢ* | 提供两个关键可靠性信号：模态贡献可解释性（*ḡᵢ*）与路由决策稳定性（*uᵢ*），二者均为Task C证据源 | Input: averaged cross-modal token *ēᵢ*; Output: *ḡᵢ* ∈ [0,1]³, *uᵢ* ∈ ℝ≥₀ | [Paper] [Paper: PDF p. 6–7]: “The mean gate values *ḡᵢ* ∈ [0,1]³ are thresholded [...] The scalar *uᵢ* [...] is defined as the epistemic routing uncertainty [...] Both *uᵢ* and *ḡᵢ* are provided as interpretable model outputs and used by Task C.” | 移除将丢失模态归因与不确定性估计，Task C无法生成modality-routing/uncertainty-focused解释；Table 3显示Uncertainty策略CA=1.00，证明其必要性 [Paper] [Paper: PDF p. 13] |
| ClusteringHead | Student’s t-kernel soft assignment + self-sharpening KL loss | 实现无监督域聚类，同时输出soft assignment *qᵢₖ*，用于计算confidence *cᵢ* 和runner-up margin Δᵢ ——二者为Task C核心证据 | Input: L2-normalized latent *ẑᵢ*; Output: *qᵢ* ∈ [0,1]ᴷ, *cᵢ* = maxₖ*qᵢₖ*, *k̂ᵢ* = argmaxₖ*qᵢₖ* | [Paper] [Paper: PDF p. 7]: “The predicted domain for spot *i* is *k̂ᵢ* = arg maxₖ*qᵢₖ*, and the assignment confidence is defined as *cᵢ* = maxₖ*qᵢₖ*.” | 移除则无聚类输出，整个框架失效；Table 5显示*cᵢ*与*uᵢ*负相关（r=−0.42），证明其作为独立可靠性维度的价值 [Paper] [Paper: PDF p. 15] |
| Evidence-Constrained Reasoning Module | 将Task A信号组装为结构化字典，驱动Llama-3.3-70B生成5种策略的自然语言报告 | 将量化信号转化为人类可理解、可审计的spot级理由，实现“从数字到叙事”的可信跃迁 | Input: *k̂ᵢ*, *cᵢ*, *Δᵢ*, *ḡᵢ*, *uᵢ*, top markers, 5-nearest neighbourhood; Output: *J⁽ʳ⁾ᵢ* ∈ ℕᴸ | [Paper] [Paper: PDF p. 8]: “This coupling is designed to make the explanations auditable, so that each generated justification can be traced back to the model-derived evidence supporting the corresponding spatial-domain assignment.” | 移除则退化为传统聚类；Figure 2与Table 2证明其能生成空间一致的pseudo-cell-type maps，表明信号有效 [Paper] [Paper: PDF p. 13–14] |
| OmicSync-R (REINFORCE loop) | 以GR/CA/SC加权得*Rᵢ*，作为reward优化ClusteringHead的*qᵢ*分布 | 解决base OmicSync中reasoning与clustering解耦问题，使LLM的“好理由”能正向塑造latent space | Input: *qᵢ*, sampled *aᵢ* ∼ Categorical(*qᵢ*); Output: *L_reinforce* = −∑ᵢ sg(*Rᵢ*−*bₜ*) log *qᵢ,ₐᵢ* | [Paper] [Paper: PDF p. 9–10]: “The REINFORCE loss applied to the assignment distribution is *L_reinforce* = −1/|S_R| ∑ᵢ∈S_R sg(*Rᵢ*−*bₜ*) log *qᵢ,ₐᵢ* [...] allowing reasoning coherence to shape the learned latent structure.” | 移除则无闭环；Table 7显示OmicSync-R在Human Breast Cancer上8/9指标提升，证明其有效性 [Paper] [Paper: PDF p. 17] |

## 09 关键公式与符号

论文未提供完整可核验的单一主公式，但明确定义了以下关键符号与公式（全部可溯源至PDF页码）：  
- **Soft assignment & confidence**: *qᵢₖ* = (1 + ‖*ẑᵢ* − *μₖ*‖²)⁻¹ / Σₖ′(1 + ‖*ẑᵢ* − *μₖ′*‖²)⁻¹ [Equation 15, p.7]; *cᵢ* = maxₖ*qᵢₖ* [Equation 3, p.4]  
- **Modality routing & uncertainty**: *ḡᵢ* = (1/*T*)Σₜ*gᵢ,ₜ*, *uᵢ* = Σₘ Varₜ[*gᵢ,ₘ,ₜ*] [Equations 12–13, p.6]  
- **Grounding Rate (GR)**: *GRᵢ* = \|*Mᵢ* ∩ *Jᵢ*\| / \|*Mᵢ*\|, where *Mᵢ* = supplied marker set, *Jᵢ* = markers mentioned in *Jᵢ* [Equation 18, p.9]  
- **Confidence Alignment (CA)**: Binary metric assessing match between *uᵢ* tier (LOW/MEDIUM/HIGH) and hedging language in *Jᵢ* [Paper] [Paper: PDF p.9]  
- **Spatial Consistency (SC)**: Binary metric assessing whether *Jᵢ* correctly references dominant neighbourhood composition [Paper] [Paper: PDF p.9]  
- **REINFORCE reward**: *Rᵢ* = *w₁GRᵢ* + *w₂CAᵢ* + *w₃SCᵢ*, with *w₁*=0.5, *w₂*=0.3, *w₃*=0.2 [Equation 20, p.9]  
- **OmicSync-R objective**: *L_OmicSync-R* = *L_OmicSync* + *λ_R L_reinforce* [Equation 24, p.10]  
- **Key variables**: *Z* ∈ ℝᴺˣᵈ (shared latent), *Q* ∈ [0,1]ᴺˣᴷ (soft assignment), *G* ∈ [0,1]ᴺˣ³ (modality-routing matrix), *u* ∈ ℝᴺ (epistemic uncertainty vector), *c* ∈ [0,1]ᴺ (confidence vector) [Paper] [Paper: PDF p.3–4]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|-------------------------------|--------|
| Table 1 (Clustering rank) | OmicSync achieves superior clustering quality across heterogeneous benchmarks | Compared against GROVER, MISO, SpatialGlue, COSMOS on 4 CytAssist FFPE datasets using same *K* range (6–10) and pseudo-reference labels | Best avg. rank on Tonsil (1.44), Glioblastoma (1.78), Tonsil Add-on (1.22); 2nd on Breast Cancer (2.33); best ARI on all four | OmicSync learns more biologically coherent latent representations than baselines, especially on datasets with richer protein panels (Add-on) or homogeneous structure (Tonsil) | Not that OmicSync is universally superior — its Purity < GROVER on Tonsil suggests trade-off between cluster compactness and label purity | [Paper] [Paper: PDF p.12] |
| Figure 2 & Table 2 (Task B) | CellTypeHead with Leiden pseudo-labels regularises latent space to preserve local cell-type organisation | Qualitative visualisation of pseudo-cell-type maps; no external ground-truth used | Maps show locally structured patterns (e.g., large coherent regions in Glioblastoma, fine-grained mixing in Tonsil) | Semi-supervised pseudo-label regularisation encourages latent space to retain local cellular hierarchy, even without true annotations | Not that CellTypeHead achieves accurate cell-type classification — authors explicitly state it’s not a benchmark [Paper] [Paper: PDF p.13] | [Paper] [Paper: PDF p.13–14] |
| Table 3 & Figure 3A (Reasoning strategy) | Stepwise prompting yields highest joint faithfulness | Five strategies (Standard, Stepwise, Counterfactual, Contrastive, Uncertainty) evaluated on same 40 spots | Stepwise: GR=1.00, CA=1.00, SC=0.975; Uncertainty: GR=0.074, CA=1.00 | Structured, stage-wise prompting maximally leverages all supplied evidence types; Uncertainty strategy trades GR for CA by design | Not that Stepwise is optimal for all use cases — e.g., Uncertainty strategy is best when confidence calibration is primary goal | [Paper] [Paper: PDF p.13, 21] |
| Table 4 & Figure 3B,C (Dataset-level reasoning) | Reasoning quality correlates with dataset properties (e.g., antibody panel size, tissue homogeneity) | Aggregated GR/CA/SC across 5 strategies per dataset | Tonsil Add-on: highest SC (0.84), lowest *u* (0.0526); Tonsil: highest CA (0.94); Breast Cancer: lowest SC (0.58) | Dataset-level reasoning fidelity reflects underlying data quality and biological heterogeneity — e.g., richer ADT panel reduces routing uncertainty | Not that reasoning quality directly measures biological truth — it measures alignment with *model’s own evidence*, which may contain upstream bias | [Paper] [Paper: PDF p.13, 21] |
| Table 5 (Reliability audit) | High-confidence spots exhibit lower uncertainty and higher spatial homogeneity | Three-tier split (*cᵢ* ≥0.35, 0.20–0.35, <0.20) on 40 explained spots | High-*c*: *u̅*=0.034, spatial hom.=75.6%; Low-*c*: *u̅*=0.111 (3.3×), spatial hom.=60.0% | The two core reliability signals (*cᵢ*, *uᵢ*) capture meaningful, complementary aspects of assignment stability and local support | Not that *cᵢ* and *uᵢ* are interchangeable — they’re moderately anti-correlated (r=−0.42), confirming distinct roles | [Paper] [Paper: PDF p.15, 21] |
| Table 6 & 7 (OmicSync-R) | REINFORCE reward improves clustering metrics on challenging dataset | OmicSync-R vs base OmicSync on Human Breast Cancer (*k*=10); 22 reasoning updates over epochs 50–575 | ARI +0.99 (45.73→46.72); 8/9 metrics improved; GR≈0.98, CA peaked at 0.775 | Reasoning-quality feedback can serve as effective auxiliary signal for latent space refinement, particularly on datasets where base model underperforms | Not that OmicSync-R is robust across *k* — benefit is concentrated at *k*=10; *k*=6–9 yield ARI <28 [Paper] [Paper: PDF p.17] | [Paper] [Paper: PDF p.16–17] |

## 11 对结论的正确理解

OmicSync 的核心贡献是**构建了一个从聚类输出到自然语言审计的可追溯证据链**，而非宣称其聚类性能绝对最优。其“best rank”是相对于所选四个基线在特定评估协议（*K*=6–10, pseudo-reference labels）下的相对优势，且存在trade-off（如Tonsil上Purity更低）。Task C的“faithfulness”指标（GR/CA/SC）衡量的是LLM生成文本与**模型自身输出信号**的一致性，而非与ground-truth生物学事实的一致性——例如GR=1.00仅表示LLM提到了所有供给的marker名，不保证这些marker确为生物学关键驱动因子。OmicSync-R的成功（+0.99 ARI）证明了“reasoning coherence”可作为latent space的有用正则项，但其效果受限于reward设计（k-sensitive）、计算开销（220 LLM calls）和dataset scope（仅1/4验证）。Figure 2的pseudo-cell-type maps是**定性正则化效果的间接证据**，而非细胞类型预测的定量结果——作者反复强调Task B是semi-supervised regulariser，非benchmark [Paper] [Paper: PDF p.8,13]。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Post-hoc nature of base Task C | “does not backpropagate into the clustering objective; it explains rather than optimises the partition” [Paper] [Paper: PDF p.18] | Addressed by OmicSync-R via REINFORCE [Paper] [Paper: PDF p.18] | [Paper] [Paper: PDF p.18] |
| OmicSync-R resource intensity | “requires repeated LLM-based explanation generation and reward evaluation during training [...] more resource-intensive than base OmicSync” [Paper] [Paper: PDF p.10,11] | Explore “amortised reward models, cached reasoning evaluations, and smaller verifier models” [Paper] [Paper: PDF p.18] | [Paper] [Paper: PDF p.10,11,18] |
| Reward sensitivity to *k* | “The benefit [...] is concentrated at *k* = 10. For *k* = 6–9, OmicSync-R yields ARI values [...] substantially below its ARI of 46.72 at *k* = 10” [Paper] [Paper: PDF p.17] | Investigate “reward annealing or multi-*k* training to reduce *k*-sensitivity” [Paper] [Paper: PDF p.18] | [Paper] [Paper: PDF p.17,18] |
| Task B pseudo-label limitation | “Task B pseudo-labels are RNA-derived, so the reported analysis evaluates the regularisation benefit [...] rather than external classification accuracy” [Paper] [Paper: PDF p.18] | Not explicitly proposed, but implies need for multi-modal ground-truth or better pseudo-label strategies | [Paper] [Paper: PDF p.18] |
| Reasoning module scope constraint | “its explanations are limited to the five supplied evidence types [...] and inherit any upstream uncertainty in those signals” [Paper] [Paper: PDF p.18] | Extend to “additional modalities, such as ATAC-seq chromatin accessibility and spatial metabolomics” [Paper] [Paper: PDF p.18] | [Paper] [Paper: PDF p.18] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|--------|
| The “Stepwise” strategy achieves perfect GR/CA but SC=0.975 < 1.00, while “Contrastive” has SC=0.650 — yet both use identical evidence dictionary. This suggests SC metric may conflate *neighbourhood composition reporting* with *correct interpretation of its relevance*. | SC evaluates whether *Jᵢ* “correctly references” neighbourhood composition, but does not assess whether that reference is *biologically meaningful*. E.g., stating “5 neighbours are Vascular” is SC=1.00, but failing to link it to vascular biology is undetected. | Over-reliance on SC could mislead: high SC may reflect rote copying of evidence, not insightful reasoning. This undermines the claim that Stepwise is “most faithful” overall. | Redesign SC to require *causal linking*: e.g., “Vascular neighbours support vascular assignment because...” — scored by biomedical expert or LLM verifier. Compare SC scores before/after adding this requirement. | [Paper] [Paper: PDF p.9,13]: SC definition is purely referential (“correctly references”), not inferential. Table 3 shows Stepwise SC=0.975, not 1.00, implying some failures in referencing. |
| OmicSync-R’s reward weights (*w₁*=0.5, *w₂*=0.3, *w₃*=0.2) are fixed and unvalidated. GR dominates, yet Table 3 shows Uncertainty strategy has GR=0.074 by design — meaning its reward is almost entirely driven by CA/SC, which are less stable (see Table 6: CA drops to 0.313 at epoch 425). | Fixed weights may over-prioritise GR (easily gamed by LLM listing all markers) while under-weighting harder-to-optimize SC, whose late-training decline (mean SC=0.21 after epoch 400) suggests fundamental misalignment between neighbourhood evidence and final assignments. | If reward is skewed, OmicSync-R may optimize for “marker-listing ability” rather than true reasoning coherence, limiting generalizability. This questions the validity of using *Rᵢ* as a proxy for holistic “reasoning quality”. | Conduct ablation: train OmicSync-R with *w₁*=0.2, *w₂*=0.4, *w₃*=0.4; compare final ARI and SC trajectory. Also, correlate *Rᵢ* with human expert rating of *Jᵢ* faithfulness on subset. | [Paper] [Paper: PDF p.9]: weights are stated without justification. Table 6 shows SC degrades late, suggesting it’s the bottleneck. Equation 20 fixes weights. |
| The adaptive *nₕₒₚₛ* mechanism uses RNA neighbour similarity >0.6 to define “homogeneous tissue”, but this threshold is arbitrary and dataset-specific. Figure 3C shows Tonsil Add-on has lowest *u* (0.053) and best rank (1.22), yet its *nₕₒₚₛ* is 2 — same as standard Tonsil (rank 1.44, *u*=0.088). This weakens the claimed causal link between *nₕₒₚₛ* and performance. | *nₕₒₚₛ* may be a proxy for other factors (e.g., ADT panel richness), not tissue homogeneity per se. Using RNA similarity to decide spatial exclusion for *all* modalities ignores modality-specific spatial scales (e.g., protein gradients may be sharper than RNA). | If *nₕₒₚₛ* is not the true driver, the “adaptive spatial smoothing” contribution is overstated, and the mechanism may not generalize to non-RNA-centric modalities like ATAC or metabolomics. | Replace RNA-based *nₕₒₚₛ* selection with modality-agnostic graph metrics (e.g., spatial entropy of *Ḡ*), or learn *nₕₒₚₛ* per modality. Compare ARI on Breast Cancer (where *nₕₒₚₛ*=1) under both schemes. | [Paper] [Paper: PDF p.7]: *nₕₒₚₛ* threshold is ad hoc. Figure 3C shows Add-on’s superiority correlates with ADT panel, not *nₕₒₚₛ*. |

## 14 学到的知识

- **可靠性信号必须可计算、可分离、可组合**：OmicSync 显式定义了三种正交信号——assignment confidence（分布锐度）、epistemic routing uncertainty（MC-Dropout方差）、modality-routing weights（gating均值）——它们分别捕获不同维度的不确定性，且均可直接用于Task C证据构造。这提示我们在设计single-cell foundation models时，应避免单一“confidence score”，而应解耦出distributional、epistemic、aleatoric等分量。  
- **LLM推理必须被证据严格约束，而非自由发挥**：OmicSync 的“evidence-constrained”设计（禁止引入未供给的基因名/蛋白名/文献）确保了审计可追溯性。这对perturbation prediction任务极具启发：可将扰动响应预测（如Δgene expression）作为证据，约束LLM生成“why this gene changes”而非泛泛而谈。  
- **REINFORCE是连接不可微LLM与可微模型的务实桥梁**：OmicSync-R 不尝试微调LLM，而是将其视为black-box reward generator。这为multi-omics中使用大模型（如BioMedLM）提供范式：用其输出质量（而非梯度）指导foundation model训练。  
- **模态路由（MoE）不仅是融合工具，更是可解释性接口**：UncertaintyMoE 输出的 *ḡᵢ* 直接成为Task C的“which modality drove this?”答案，且Figure 3E显示不同疾病有不同模态偏好（Glioblastoma RNA-dominant），这比attention权重更易解读。  
- **空间邻域一致性（SC）是最难优化的指标**：Table 6显示SC在训练后期崩溃，暗示当前spot-level reward不足以建模空间图结构。这提示在spatial transcriptomics中，graph-level rewards（如subgraph homogeneity）可能比spot-level更有效。  
- **伪标签（pseudo-label）的正则化价值不亚于真标签**：Task B虽无ground-truth，但Leiden RNA pseudo-labels成功引导latent space产生空间连贯的pseudo-cell-type maps（Figure 2），证明高质量unsupervised signals可作为强归纳偏置。

## 15 与既有知识的连接

- **候选连接/方法论连接**：OmicSync 的“KAN-GCN backbone + spatial position encoding”与 STAGATE/GraphST 一脉相承，但前者将空间信息注入各模态特征层（而非仅图卷积），更契合multi-omics异构性。  
- **候选连接/方法论连接**：UncertaintyMoE 的MC-Dropout设计直接受 Gal & Ghahramani (2016) [17] 启发，但将其应用于模态路由（而非全网络），创造了新的可解释性维度。  
- **候选连接/方法论连接**：REINFORCE loop 与 Williams (1992) [18] 经典policy gradient一致，但创新在于reward由自动faithfulness metrics构成，规避了人工reward engineering。  
- **候选连接/方法论连接**：Evidence dictionary 构造逻辑类似 SHAP 的“feature attribution + context”，但扩展至多信号（confidence + uncertainty + modality + neighbourhood），更适配spatial omics的复杂因果。  
- **弱连接/方法论连接**：与single-cell foundation models（如scGPT, scFoundation）相比，OmicSync 未使用大规模预训练，而是聚焦于小样本、多模态、空间约束下的联合学习，其“reliability-aware”设计可迁移至scGPT的cell state representation微调中。  
- **弱连接/方法论连接**：cross-modal alignment 思路与 SpatialGlue 的cross-attention相似，但OmicSync 用CrossModalTransformer在token级融合，再经UncertaintyMoE路由，提供了更细粒度的模态控制。  
- **弱连接/方法论连接**：perturbation prediction 可借鉴其证据构造：将扰动前后表达变化ΔX、关键TF活性、chromatin accessibility变化作为证据字典，约束LLM生成机制解释。

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: SpatialGraph-REINFORCE  
  **originating limitation/observation**: SC metric degrades late in OmicSync-R training (Table 6), suggesting spot-level rewards fail to capture spatial graph coherence [Analysis].  
  **core hypothesis**: A graph-level reward, computed over k-hop neighbourhood subgraphs, will better align latent space with tissue topology than spot-level SC.  
  **delta from paper**: Replaces spot-level *SCᵢ* with *SC_subgraph* = fraction of nodes in *k*-hop subgraph assigned to same domain as center node, averaged over all subgraphs.  
  **initial method**: For each reasoning update, sample 10 subgraphs; compute *SC_subgraph*; use as reward component in *Rᵢ*.  
  **validation**: Compare SC trajectory and final ARI on Human Breast Cancer vs. base OmicSync-R.  
  **failure modes**: Subgraph sampling may be noisy; *k* must be tuned per dataset.  
  **innovation status**: unverified  

- **name**: MultiModal-PseudoLabel Fusion  
  **originating limitation/observation**: Task B uses RNA-only Leiden pseudo-labels, ignoring ADT/histology signals for supervision [Paper] [Paper: PDF p.18].  
  **core hypothesis**: Fusing pseudo-labels from all three modalities (e.g., ensemble Leiden on RNA/ADT/histology embeddings) will yield more robust CellTypeHead regularization.  
  **delta from paper**: Replace single RNA-derived *Y* with *Y_fused* = argmax over ensemble soft assignments from modality-specific Leiden.  
  **initial method**: Run Leiden on *X₁*, *X₂*, *X₃* separately; average soft assignments; threshold to get pseudo-labels.  
  **validation**: Compare pseudo-cell-type map coherence (Figure 2) and Task A ARI on all four datasets.  
  **failure modes**: Modality imbalance (e.g., sparse ADT) may dominate fusion; requires modality-specific resolution tuning.  
  **innovation status**: unverified  

- **name**: PerturbReasoner  
  **originating limitation/observation**: OmicSync’s evidence dictionary includes “top evidence features” — directly transferable to perturbation contexts where Δfeatures are known [Paper] [Paper: PDF p.8].  
  **core hypothesis**: Constraining LLM to reason *only* about supplied perturbation-induced Δfeatures, modality weights, and neighbourhood shifts will yield more actionable mechanistic hypotheses than free-form prediction.  
  **delta from paper**: Input to reasoning module includes: perturbed gene set, Δexpression vector, dominant modality post-perturbation, pre/post neighbourhood composition shift.  
  **initial method**: Apply OmicSync pipeline to perturbation datasets (e.g., CROP-seq); construct evidence dictionary with perturbation-specific signals.  
  **validation**: Human expert assessment of generated hypotheses’ biological plausibility vs. baseline (e.g., scGPT + prompt).  
  **failure modes**: Requires high-quality perturbation response data; may not generalize to partial/indirect perturbations.  
  **innovation status**: unverified