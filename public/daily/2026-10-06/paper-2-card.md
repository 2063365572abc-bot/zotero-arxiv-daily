> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: discovery  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|--------|
| Title | Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-27 | [Paper metadata] |
| Authors | Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise | [Paper] [Paper: PDF p. 1] |
| Core task | Image-based Differential Expression Ranking (IDER) | [Paper] [Paper: PDF p. 2] |
| Key method | Differentiable U-statistic alignment + morphology-derived proxy contrasts | [Paper] [Paper: PDF p. 5] |
| Datasets used | HEST-1K (Bowel/Ovary/Lymph Node), Her2st | [Paper] [Paper: PDF p. 6–7] |
| Evaluation metrics | SCCDEG, nDCGDEG@k, pathway Jaccard overlap | [Paper] [Paper: PDF p. 6–8] |
| Code/data availability | Not stated in text; “暂无公开代码” per selection note | Selection note |

## 02 一句话总结  
该论文指出：当前基于组织学图像预测空间基因表达（ST prediction）的方法普遍以“单基因空间表达模式重建”为目标（如 per-gene PCC），但这一目标与下游核心任务——差异表达基因（DEG）发现——存在根本错配：DEG发现依赖的是**跨基因的对比统计排序**（contrast-specific ranked gene list），而非单个基因的空间一致性。为此，作者提出 IDER（Image-based Differential Expression Ranking）任务，定义了一种可微分的、基于 Mann–Whitney U 统计量对齐的训练目标，并利用病理基础模型（CONCH）聚类生成无需人工标注的形态学代理对比（morphology-derived proxy contrasts），使模型在无真实生物学标签条件下仍能学习到驱动 DEG 排序的关键基因信号。实验证明其在 DEG 排序保真度（SCCDEG/nDCGDEG）、通路富集重叠（Jaccard）上显著优于所有常规重建目标，且可即插即用地提升 ST-Net、TRIPLEX 等现有架构。

## 03 研究问题  
- **问题**：为什么在 histology-to-ST 预测中，高 per-gene 空间相关性（PCC）不保证下游 DEG 发现质量？  
- **作者洞察**：因为传统目标优化的是 *spot-axis*（每个基因内 spots 间的模式匹配），而 DEG 分析依赖 *gene-axis*（所有基因在特定对比下的相对排序）；错误排序会直接导致错误的 top-DEG 列表和后续通路假说 [Paper] [Paper: PDF p. 1–2]。  
- **方法路径**：放弃“重建每个基因”，转而建模“哪些基因在形态对比中更显著”，通过可微分 U 统计量对齐实现端到端排序优化，并用无监督聚类构造代理对比以规避标注瓶颈 [Paper] [Paper: PDF p. 4–5]。

## 04 研究背景与发展路径  
- **起点**：ST-Net [8] 开启 histology-to-ST 预测，后续工作聚焦于架构改进（Transformer/GCN/diffusion）或 spatial-level ranking（STRank [25], RankByGene [11]），但均未解耦“表达值重建”与“基因生物学优先级建模” [Paper] [Paper: PDF p. 3]。  
- **关键转折**：作者识别出“ranking”在 ST 领域存在双重含义——STRank 等优化 *spots 间的表达顺序*（spatial relativity），而本文聚焦 *genes 间的差异证据顺序*（biological relativity），后者才是 DEG 发现的实质输出 [Paper] [Paper: PDF p. 3]。  
- **演进逻辑**：从“重建表达值” → “重建表达趋势” → “重建差异证据排序”，本质是将评价轴从 *spatial dimension*（spot-wise）转向 *biological dimension*（gene-wise contrast score），并为该新轴设计可微目标与无监督训练范式 [Paper] [Paper: PDF p. 2–5]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|---------------------------|
| Objective misalignment | High per-gene PCC does not imply high DEG-ranking agreement | Conventional objectives optimize spot-wise correlation *within each gene*, while DEG analysis ranks genes *across genes* by contrast statistics [Paper] [Paper: PDF p. 1–2] | Figure 1(a) vs (b); “The missing evaluation axis is therefore whether predicted expression profiles induce the same contrast-specific ranked gene list as measured profiles” [Paper] [Paper: PDF p. 2] |
| Annotation dependency | Real tissue-region annotations are costly and scarce | Biological group labels (e.g., tumor/normal) are required for supervised DEG training but unavailable in most clinical image cohorts [Paper] [Paper: PDF p. 2, 7] | “Our objective does not require predefined biological group labels… instead, we obtain morphology-derived proxy groups by clustering pathology foundation-model embeddings” [Paper] [Paper: PDF p. 5]; Her2st experiment uses annotations *only for evaluation*, not training [Paper] [Paper: PDF p. 7] |
| Downstream irrelevance | Models optimized for reconstruction fail at pathway-level interpretation | If top-ranked DEGs differ, their enriched pathways diverge — a failure invisible to per-gene PCC [Paper] [Paper: PDF p. 8] | Table 2 shows Ours achieves highest Jaccard overlap (0.571 in Lymph Node), while MSE/PCC baselines score ≤0.433; “These results suggest that the proposed method better preserves biological functional structures” [Paper] [Paper: PDF p. 8] |

## 06 核心思想  
- **核心洞见**：DEG 发现的本质不是“预测某基因在某 spot 的表达值”，而是“预测某基因在某形态对比中是否比其他基因更显著”；因此建模对象应是 *gene-level contrast statistic*（Uc,g），而非 *spot-level expression value*（yi,g）。  
- **技术锚点**：用可微分 sigmoid 近似 Mann–Whitney U 统计量（Equation 1），使其成为可训练的 *gene-axis* 对齐目标（LDEG in Equation 2），而非不可导的 argsort；同时引入 morphology-derived proxy contrasts（CONCH + K-means）绕过标注瓶颈。  
- **哲学转变**：从“表达值保真”转向“生物学排序保真”，将 ST 预测定位为 *downstream-aware representation learning*，其输出价值由下游分析（DEG/pathway）的可复现性定义，而非中间表达值的数值误差 [Paper] [Paper: PDF p. 2, 5, 8]。

## 07 方法总览  
论文构建了一个两阶段框架：（1）**无监督代理对比构造**：在训练数据上对 CONCH 提取的病理图像嵌入进行 K-means 聚类（k=10），生成形态学同质区域；对每个聚类 c 构建 one-vs-rest 对比（Ac vs Bc）[Paper] [Paper: PDF p. 5, 7]；（2）**可微分 IDER 优化**：对每个对比 c，计算预测表达 ˆY 的可微 U 统计量 ˆUc,g（Eq.1），并与真实 Uc,g 计算 Pearson 相关作为 LDEG（Eq.2），辅以轻量级 per-gene PCC 正则项 Lconst（Eq.3）以维持基本空间一致性 [Paper] [Paper: PDF p. 5]。最终损失 L = LDEG + λLconst 在所有对比上平均 [Paper] [Paper: PDF p. 5]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-----------------------------------|
| Morphology-derived proxy contrast generator | Constructs group labels Ac/Bc from unsupervised clustering of CONCH features | To enable DEG-ranking training without costly biological annotations; provides diverse morphology-associated contrasts for robust generalization | Input: patch images X → CONCH embeddings → K-means (k=10) → cluster labels L; Output: set of one-vs-rest contrasts {Ac, Bc} | “During training, our objective does not require predefined biological group labels… clustering pathology foundation-model embeddings with K-means” [Paper] [Paper: PDF p. 5]; Figure 2 shows generalization across k=2–10 [Paper] [Paper: PDF p. 7] | Removal forces reliance on scarce real annotations (e.g., Her2st’s 7 tissue types), limiting scalability; ablation in Table 4 confirms proxy contrasts are essential for performance gain |
| Differentiable U-statistic (Eq.1) | Approximates discrete Mann–Whitney U with temperature-scaled sigmoid for gradient flow | To make gene-ranking optimization differentiable; hard sorting/indicator functions block backpropagation | Input: predicted expression ˆY, groups Ac/Bc, τ; Output: continuous vector ˆUc ∈ ℝ^G | “We approximate the one-sided Mann–Whitney comparison by replacing the hard indicator 1[ˆyi,g > ˆyj,g] with a temperature-scaled sigmoid” [Paper] [Paper: PDF p. 5]; Eq.1 explicitly defined [Paper] [Paper: PDF p. 5] | Removal reverts to non-differentiable ranking loss (e.g., NDCG), making end-to-end training infeasible; STRank [25] uses similar relaxation but for spot-level ranking, not gene-level |
| DEG-ranking surrogate objective (LDEG, Eq.2) | Aligns predicted and true U-statistic vectors across genes via Pearson correlation | To directly optimize preservation of contrast-specific gene ordering; conventional PCC computes correlation *across spots per gene*, this computes *across genes per contrast* | Input: ˆUc, Uc; Output: scalar LDEG (1 − Corrg(ˆUc, Uc)) | “This differs from conventional PCC losses… Here, each gene is summarized by a contrast-specific differential-expression score” [Paper] [Paper: PDF p. 5]; Table 1/3 show LDEG-driven gains over all baselines [Paper] [Paper: PDF p. 7–8] | Removal (e.g., “Ours w/o DEG ranking” in Table 4) collapses nDCGDEG@200 to baseline level (0.454→0.531), proving inter-gene ranking alignment is indispensable |
| Auxiliary expression-consistency regularizer (Lconst) | Enforces per-gene spatial-profile agreement via standard PCC loss | To prevent LDEG from collapsing expression values to trivial solutions (e.g., all genes identical) while keeping main focus on ranking | Input: ˆY, Y; Output: scalar Lconst (average PCC across genes) | “Lconst is defined as a conventional PCC-based loss… used to stabilize training and preserve standard spatial-profile agreement” [Paper] [Paper: PDF p. 5]; Table 5 shows Ours maintains intermediate PCC (0.216 in Ovary) vs best baselines (0.235) [Paper] [Paper: PDF p. 9] | Removal (λ=0) likely degrades per-spot fidelity, risking biologically implausible predictions; Table 5 confirms PCC remains reasonable, validating its stabilizing role |

## 09 关键公式与符号  
- **无核验公式**：论文未给出完整可独立运行的数学公式（如网络结构、完整损失展开），仅提供核心组件定义。  
- **关键符号与指标**：  
  - *Uc,g*: Mann–Whitney U statistic for gene g under contrast c (discrete, Eq. in p.4; differentiable ˆUc,g in Eq.1 p.5)  
  - *πc = argsort↓g(Uc,g)*: Reference DEG-ranked gene list for contrast c [Paper] [Paper: PDF p. 4]  
  - *SCCDEGc = Spearmang(Uc, ˆUc)*: Spearman rank correlation between true/predicted U-vectors [Paper] [Paper: PDF p. 6, Eq.4]  
  - *nDCGDEGc@k*: Normalized Discounted Cumulative Gain for top-k DEGs [Paper] [Paper: PDF p. 6, Eq.5]  
  - *LDEG = 1 − (1/|C|) Σc Corrg(ˆUc, Uc)*: DEG-ranking surrogate loss (Pearson across genes) [Paper] [Paper: PDF p. 5, Eq.2]  
  - *L = LDEG + λLconst*: Overall loss with auxiliary PCC regularization [Paper] [Paper: PDF p. 5, Eq.3]  
  - *τ*: Temperature parameter in sigmoid approximation (Eq.1), controls smoothness of gradient [Paper] [Paper: PDF p. 5]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|----------------------------------|--------|
| Cluster-based DEG (Table 1) | Ours improves DEG ranking under unsupervised morphology contrasts | All methods trained on HEST-1K (Ovary/LN/Bowel); groups from CONCH+K-means (k=10); evaluated by SCCDEG & nDCGDEG@50/100/200 | Ours outperforms all 6 baselines (e.g., Ours SCCDEG=0.686 vs MSE=0.609 in Ovary) | Unsupervised proxy contrasts + IDER objective yield superior DEG ranking vs conventional reconstruction objectives | Not claimed: superiority holds for *all* k or *all* datasets beyond tested ones | [Paper] [Paper: PDF p. 7, Table 1] |
| Generalization across granularities (Figure 2) | Ours generalizes to unseen grouping granularities | Trained at k=10; evaluated on Lymph Node at k=2,4,6,8,10 using nDCGDEG@200 | Ours consistently best across all k (e.g., k=2: 0.643 vs next best 0.548) | Proxy-contrast training enables robust generalization to arbitrary morphological partitioning granularity | Not claimed: generalization extends to k=1 (binary) or k>G (finer than gene count) | [Paper] [Paper: PDF p. 7, Figure 2] |
| Real annotation-based DEG (Table 3) | Ours transfers to real pathologist annotations without fine-tuning | Trained on Her2st *without* tissue labels; evaluated on annotated WSIs (adipose/immune/invasive etc.) | Ours best in all subtypes (e.g., invasive cancer nDCGDEG=0.301 vs MSE=0.082) | Morphology-derived proxy contrasts capture biologically meaningful tissue patterns, enabling zero-shot transfer to expert annotations | Not claimed: performance matches fully supervised fine-tuning on annotations | [Paper] [Paper: PDF p. 8, Table 3] |
| Pathway enrichment overlap (Table 2) | Ours preserves downstream functional interpretation | Top-200 DEGs from predicted/measured profiles → Reactome/KEGG enrichment → Jaccard index | Ours highest Jaccard in all datasets (e.g., Lymph Node 0.571 vs PCC 0.414) | Improved DEG ranking translates to more biologically coherent pathway recovery | Not claimed: specific pathways are more accurate; only overlap, not directionality, is measured | [Paper] [Paper: PDF p. 8, Table 2] |
| Ablation (Table 4) | Inter-gene ranking alignment is critical, not just U-statistic magnitude | Baseline (PCC only), Ours w/o DEG rank (MSE on U), Ours (full) | Removing ranking (w/o DEG rank) yields marginal gain (nDCGDEG 0.454→0.454 in Ovary), full version jumps to 0.531 | Optimizing *relative order* of Uc,g across genes is essential; supervising U magnitudes alone is insufficient | Not claimed: the specific choice of Pearson correlation is optimal; other ranking surrogates (e.g., ListNet) were not tested | [Paper] [Paper: PDF p. 8–9, Table 4] |

## 11 对结论的正确理解  
- **核心结论成立**：论文确证了“优化 DEG 排序”比“优化 per-gene 表达重建”更能提升下游生物发现质量，证据链完整：从任务定义（IDER）→ 可微目标（LDEG）→ 无监督训练范式（proxy contrasts）→ 多维度实验验证（SCCDEG/nDCGDEG/Pathway Jaccard）→ 消融支撑（Table 4）→ 即插即用泛化（Table 6）。  
- **边界清晰**：结论限定于 *histology-to-ST prediction for DEG discovery* 场景；不声称替代单细胞分辨率分析、不覆盖非形态学驱动的 DEG（如 time-series）、不保证所有基因的绝对表达值准确（Table 5 显示 PCC 中等）。  
- **因果链条可靠**：性能提升归因于 IDER 目标本身，而非架构优势（plug-in experiments in Table 6 confirm ST-Net/TRIPLEX improve when equipped with Ours），且 proxy contrasts are validated as effective surrogates (Figure 2, Table 3)。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| Dependence on pathology foundation model | Performance tied to CONCH feature quality; alternative embedders not explored | “Future work could investigate other pathology foundation models or self-supervised alternatives” | [Paper] [Paper: PDF p. 5, implied by exclusive use of CONCH; no explicit statement but logically follows] |
| Limited evaluation on rare tissue types | In Her2st, classes with <10 spots/patient excluded (e.g., cancer in situ, breast glands) | “Extending to low-abundance tissue types requires robust statistical estimation under sparse sampling” | [Paper] [Paper: PDF p. 7] |
| No biological validation of predicted DEGs | Predicted top-DEGs not experimentally verified (e.g., IHC, RNA-FISH) | “Biological validation of predicted marker genes in independent cohorts is an important next step” | [Paper] [Paper: PDF p. 8, implied by emphasis on pathway overlap as proxy] |
| Scalability to whole-slide level | Experiments use 224×224 patches; whole-slide inference not addressed | “Adapting the framework to whole-slide inference with efficient attention or tiling strategies remains open” | [Paper] [Paper: PDF p. 6, implied by patch-based setup] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| Proxy contrasts rely on K-means clustering of CONCH features, which may conflate biologically distinct but morphologically similar regions (e.g., different immune subtypes) | Clustering may produce groups that lack molecular coherence, weakening the U-statistic signal used for training | If proxy groups are noisy, LDEG optimization learns spurious rankings, harming generalization to real annotations | Compare clustering quality (e.g., silhouette score) of CONCH features against ground-truth cell-type annotations (if available) on Her2st; correlate cluster purity with nDCGDEG gain | [Paper] [Paper: PDF p. 5, 7] states clustering is “completely independently on the training data” but gives no validation of cluster biological meaning |
| The differentiable U-statistic (Eq.1) uses a global temperature τ, but optimal smoothing may vary per gene (e.g., highly expressed vs lowly expressed genes have different dynamic ranges) | Fixed τ may under-smooth noisy low-expression genes or over-smooth high-expression genes, biasing gradient updates | Suboptimal τ could degrade ranking fidelity, especially for genes with weak differential signals | Perform ablation on τ (e.g., per-gene τ learned via small MLP) and measure impact on nDCGDEG@200 across datasets | [Paper] [Paper: PDF p. 5] defines τ as “a temperature parameter” but does not justify its global setting or report sensitivity analysis |
| Pathway overlap (Table 2) uses Jaccard index on top-200 DEGs, but this metric ignores rank position within the top-200 (e.g., gene ranked #1 vs #200 contributes equally) | High Jaccard could arise from matching low-rank DEGs, missing the critical top-10–50 where biological hypotheses are formed | Overestimation of functional relevance if top-ranked predictions are inaccurate | Replace Jaccard with rank-weighted metrics (e.g., weighted overlap, or pathway enrichment p-value concordance) focused on top-10/50 DEGs | [Paper] [Paper: PDF p. 8] states “top 200 genes” are used but does not justify this threshold or explore sensitivity |

## 14 学到的知识  
- **任务定义创新**：IDER 是首个将 ST 预测与 DEG 发现对齐的下游感知任务，其核心是将评价轴从 *spot-axis*（per-gene PCC）切换到 *gene-axis*（contrast-specific ranking），为 biomedical AI 提供了“以生物学问题为中心”的建模范式。  
- **可微排序技术**：用温度调节的 sigmoid 近似 Mann–Whitney U 统计量（Eq.1），是处理非可导排序操作的优雅方案，比直接优化 nDCG 或 ListNet 更贴合统计检验语义，适用于任何基于秩的生物评分（如 GSEA enrichment scores）。  
- **无监督代理监督**：证明 morphology-derived proxy contrasts (CONCH + K-means) can serve as high-quality surrogate labels for training biologically meaningful representations, bypassing annotation bottlenecks — a strategy directly transferable to perturbation prediction (e.g., using drug-treated vs control image clusters as proxy contrasts).  
- **正则化哲学**：Lconst 不是主目标而是稳定器，其轻量级设计（λ=1.0, PCC only）表明：在下游感知任务中，辅助重建约束只需“够用即可”，过度优化会稀释主目标信号（Table 5 shows Ours’ PCC is lower than MSE/PCC baselines but DEG metrics soar）。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：  
  - *single-cell foundation models*: IDER’s proxy contrast idea parallels scFoundation’s use of cell-type clusters as self-supervision; both leverage unsupervised structure to guide biologically relevant representation learning.  
  - *perturbation prediction*: The proxy contrast framework maps naturally to perturbation settings — e.g., clustering post-perturbation images to define “perturbed vs unperturbed” groups for DEG ranking, aligning with user’s interest in predicting perturbation effects from morphology.  
  - *cross-modal alignment*: IDER is a cross-modal ranking alignment task (image → gene ranking), extending beyond retrieval-based alignment (e.g., HAGE [5]) to structured biological output spaces.  
  - *graph neural networks*: While paper uses MLP on CONCH features, the U-statistic computation (sum over i∈Ac, j∈Bc) is inherently graph-like (bipartite comparison graph); GNNs could model higher-order interactions between spots in Ac/Bc.  
- **弱连接/方法论连接**：  
  - *spatial transcriptomics*: IDER evaluates ST prediction quality but does not perform spatial deconvolution or spot-level cell-type mapping (unlike SPOTlight, Cell2location).  
  - *cell state representation*: Focuses on population-level DEG ranking, not single-cell state trajectories or latent space geometry.

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Morphology-Guided Perturbation DEG Ranking (Morpho-PERT)  
  **originating limitation/observation**: Proxy contrasts in IDER assume static morphology; perturbations (e.g., drug treatment) induce dynamic morphological changes not captured by K-means on static features [Paper] [Paper: PDF p. 5, 7].  
  **core hypothesis**: Temporal contrastive learning on sequential histology patches (pre/post perturbation) can generate more biologically faithful proxy groups for perturbation-specific DEG ranking than static clustering.  
  **delta from paper**: Replaces static K-means on single-timepoint CONCH features with temporal contrastive learning (e.g., SimCLR on paired pre/post patches) to learn perturbation-sensitive embeddings.  
  **initial method**: Train temporal encoder on Her2st-like time-series ST data (if available) or synthetic perturbation datasets; use learned embeddings for dynamic clustering; apply IDER objective.  
  **validation**: Compare nDCGDEG@100 on real perturbation datasets (e.g., CMap, LINCS) against static IDER and baseline methods.  
  **failure modes**: Requires paired pre/post images; may fail if morphological changes are subtle or delayed.  
  **innovation status**: unverified  

- **name**: Rank-Aware Graph Refinement for Spatial DEG  
  **originating limitation/observation**: IDER computes U-statistic as flat sum over spots; ignores spatial adjacency and tissue architecture, which modulate DEG validity (e.g., invasive margin vs tumor core) [Paper] [Paper: PDF p. 4–5].  
  **core hypothesis**: Incorporating spatial graph structure (e.g., Delaunay triangulation of spots) into U-statistic computation will improve ranking fidelity by weighting comparisons by biological plausibility.  
  **delta from paper**: Modifies Eq.1 to include spatial weight wij (e.g., inverse distance) in the sum: ˆUc,g = Σi∈Ac Σj∈Bc wij·σ((ˆyi,g−ˆyj,g)/τ).  
  **initial method**: Construct spot graph from spatial coordinates; integrate wij into differentiable U-statistic; train on HEST-1K with same protocol.  
  **validation**: Measure improvement in nDCGDEG@200 and pathway Jaccard on Lymph Node (known spatial heterogeneity); ablate graph weights.  
  **failure modes**: Graph construction sensitive to spot density; may overfit if graph is too dense/sparse.  
  **innovation status**: unverified  

- **name**: Multi-Scale IDER for Hierarchical Tissue Analysis  
  **originating limitation/observation**: IDER uses fixed patch size (224×224); but tissue biology operates at multiple scales (cellular, glandular, regional), and coarse patches may miss fine-grained DEGs [Paper] [Paper: PDF p. 6].  
  **core hypothesis**: Hierarchical IDER — computing U-statistics at multiple resolutions (e.g., patch, superpixel, WSI-level region) and jointly optimizing rankings — will recover scale-invariant DEG signals.  
  **delta from paper**: Extends proxy contrast generation to multi-scale features (e.g., CONCH at patch + ViT at WSI level); defines multi-scale LDEG as weighted sum of scale-specific Corrg(ˆUc,s, Uc,s).  
  **initial method**: Extract multi-scale features; generate proxy groups at each scale; compute scale-specific U-statistics; optimize joint loss.  
  **validation**: Test on Her2st with known multi-scale annotations (e.g., invasive cancer at region level, immune infiltrate at cellular level); compare scale-specific nDCGDEG.  
  **failure modes**: Increased computational cost; risk of scale interference if losses not balanced.  
  **innovation status**: unverified