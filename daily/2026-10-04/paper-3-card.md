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
| Authors | Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (cs.CV) | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-27 | [URL metadata] |
| Core task | Image-based Differential Expression Ranking (IDER) | [Paper] [Paper: PDF p. 2] |
| Key metric | nDCGDEG@200, SCCDEG, pathway Jaccard overlap | [Paper] [Paper: PDF p. 6–8] |
| Primary datasets | HEST-1K (Bowel/Ovary/Lymph Node), Her2st | [Paper] [Paper: PDF p. 6–7] |
| Model backbone | CONCH foundation model + frozen encoder + trainable 3-layer MLP | [Paper] [Paper: PDF p. 6] |
| Training signal | Morphology-derived proxy contrasts via K-means on CONCH features | [Paper] [Paper: PDF p. 5, p. 6] |
| Loss function | L = L<sub>DEG</sub> + λL<sub>const</sub>, where L<sub>DEG</sub> is gene-axis Pearson correlation of differentiable U-statistics | [Paper] [Paper: PDF p. 5, Eq. 3] |

## 02 一句话总结  
该论文指出：当前基于组织病理图像预测空间基因表达（ST prediction）的方法，普遍以“单基因空间表达模式重建”为优化目标（如 per-gene PCC），但这一目标与下游核心任务——差异表达基因（DEG）发现——存在根本错位：DEG发现依赖的是**跨基因的对比统计排序**（contrast-specific ranked gene list），而非单基因空间一致性。为此，作者提出 IDER（Image-based Differential Expression Ranking）新任务及可微分训练目标，用形态学聚类生成的代理对比组（morphology-derived proxy contrasts）驱动模型学习保留 DEG 排序能力，实验证明其在 DEG 排名一致性（nDCGDEG@200）、通路富集重叠（Jaccard）上显著优于所有常规重建目标，且可即插即用于 ST-Net、TRIPLEX 等现有架构。该工作不追求更高 per-gene PCC，而是明确将模型目标对齐生物发现流程，为 cross-modal alignment 提供了可解释、下游感知的对齐范式。

## 03 研究问题  
传统 ST 预测方法为何在“发现哪些基因最能区分组织区域/表型”这一关键下游任务上表现不佳？  
→ 作者洞察到：问题根源不在模型容量或数据质量，而在于**优化目标与下游分析逻辑脱节**——现有方法最小化每个基因在空间维度上的预测误差（spot-wise），却未建模基因在生物学对比维度上的相对重要性（gene-wise ranking）。  
→ 进一步追问：能否定义一个可计算、可微分、无需真实生物学标注的训练目标，使模型在仅见组织图像时，也能隐式习得“哪些基因的表达变化最敏感地响应形态学差异”？  
→ 最终聚焦：如何形式化“预测表达谱是否复现真实 DEG 排序”这一语义，并将其转化为端到端可优化的损失？

## 04 研究背景与发展路径  
背景层：ST 技术成本高、通量低，而病理图像（H&E）广泛可得；因此 histology-to-ST 预测被视为扩展分子分析的关键路径 [Paper] [Paper: PDF p. 1]。  
技术演进层：从早期 CNN（ST-Net [8]）→ Transformer/GCN 捕获长程依赖 [6,27,38] → 检索/生成范式（diffusion/flow matching [39,10]）→ 排序增强（STRank [25] 关注 spot-level 相对排序）；但所有工作均未突破“per-gene reconstruction”范式。  
认知跃迁层：作者跳出“重建精度”框架，转向“下游分析保真度”视角——受 differential expression analysis 标准流程启发（U-statistic → gene ranking → pathway enrichment），提出 IDER 是连接图像与生物学发现的**语义接口**，而非技术中间件。该路径本质是从 signal fidelity（信号保真）转向 biological utility fidelity（生物学效用保真）。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| Objective misalignment | High per-gene PCC does not guarantee high DEG-ranking agreement (e.g., Ours ranks lower on Table 5 but higher on Table 1/3) | Conventional objectives optimize spatial-profile agreement *within each gene*, while DEG discovery requires agreement *across genes* in their contrast-specific ranking order [Paper] [Paper: PDF p. 1–2] | Table 5 shows Ours has lower per-gene PCC than MSE/PCC baselines, yet Table 1/3 show it dominates on nDCGDEG@200 and SCCDEG; [Paper] [Paper: PDF p. 9] explicitly states “Methods with higher per-gene spatial PCC do not necessarily achieve better DEG-ranking agreement” |
| Annotation dependency bottleneck | Real tissue-region annotations are costly, sparse, and unavailable for most cohorts | Biological group labels (e.g., “invasive cancer”) are required for conventional DEG analysis but impractical for large-scale training [Paper] [Paper: PDF p. 7] | Her2st experiment uses annotations *only for evaluation*, not training; training relies solely on unsupervised K-means clustering of CONCH features [Paper] [Paper: PDF p. 7] |
| Ranking non-differentiability | Direct optimization of argsort-based ranking (π<sub>c</sub>) is non-differentiable, blocking end-to-end learning | The core IDER output π<sub>c</sub> = argsort↓(U<sub>c,g</sub>) involves discrete sorting and hard comparisons [Paper] [Paper: PDF p. 4–5] | Section 5 explicitly states “directly optimizing this ranking is not differentiable” and introduces sigmoid-smoothed U-statistic (Eq. 1) as surrogate [Paper] [Paper: PDF p. 5] |
| Inter-gene relationship neglect | Baselines treat genes independently; no mechanism to preserve relative ordering between genes | Conventional losses (MSE, PCC, Poisson) compute scalar errors per gene and average — no cross-gene constraint on ranking structure [Paper] [Paper: PDF p. 4, p. 8] | Ablation in Table 4 shows “Ours w/o DEG ranking” (which applies MSE to U-statistic vector but ignores inter-gene ranking) fails to improve nDCGDEG@200 consistently, proving ranking relationships matter [Paper] [Paper: PDF p. 8] |

## 06 核心思想  
核心不是“预测更准”，而是“排序更对”——将 ST 预测的目标函数从**空间保真**（reconstructing where each gene is expressed）升维至**生物学保真**（preserving which genes are most discriminative for a given morphological contrast）。  
这一升维通过三重解耦实现：  
① **任务解耦**：分离“评估什么”（IDER：对比统计排序一致性）与“如何训练”（不同iable U-statistic alignment）；  
② **标注解耦**：用无监督形态学聚类（CONCH + K-means）生成 proxy contrasts，规避对病理专家标注的依赖；  
③ **优化解耦**：主损失 L<sub>DEG</sub> 专注基因轴相关性（Corr<sub>g</sub>），辅损失 L<sub>const</sub> 稳定空间表达基础，二者权重 λ=1.0 平衡（Eq. 3）。  
本质是构建了一个“形态学差异 → 基因表达差异强度 → 基因排序”的可微分因果链，使模型内化生物学发现逻辑。

## 07 方法总览  
整体为 encoder-predictor 架构：输入 H&E patch → CONCH 提取 frozen 特征 → 3-layer MLP 回归 G 维表达向量 ŷ<sub>i</sub>。训练目标非拟合 y<sub>i</sub>，而是拟合其诱导的**对比统计结构**。流程分三步：  
① **Proxy contrast construction**：对训练集 CONCH 特征做 K-means（k=10），每簇视为 morphology-defined group；采用 one-vs-rest scheme，每次随机选一簇为 A<sub>c</sub>（positive），其余为 B<sub>c</sub>（negative）[Paper] [Paper: PDF p. 6]；  
② **Differentiable U-statistic computation**：对每个 contrast c 和 gene g，用温度 τ-sigmoid 替换硬比较，计算 ˆU<sub>c,g</sub> = Σ<sub>i∈A<sub>c</sub></sub> Σ<sub>j∈B<sub>c</sub></sub> σ((ŷ<sub>i,g</sub>−ŷ<sub>j,g</sub>)/τ) [Paper] [Paper: PDF p. 5, Eq. 1]；  
③ **Ranking-aware optimization**：对每个 c，计算 ˆU<sub>c</sub> 与真实 U<sub>c</sub> 的 gene-axis Pearson correlation，取负为 L<sub>DEG</sub>；叠加 per-gene PCC 正则项 L<sub>const</sub>，总损失 L = L<sub>DEG</sub> + λL<sub>const</sub> [Paper] [Paper: PDF p. 5, Eq. 3]。  
整个设计确保：模型无需知道“invasive cancer”标签，却能学会哪些基因的表达变化最稳定地区分癌组织与间质——这正是病理医生依赖的直觉。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|---------------------|------------------------|-----------------------------------|
| Morphology-derived proxy contrast generator | Converts unlabeled histology features into biologically plausible group definitions for DEG computation | To enable training without costly expert annotations; leverages morphology as proxy for biology [Paper] [Paper: PDF p. 5, p. 6] | Input: CONCH embeddings of training patches; Output: K cluster assignments → {A<sub>c</sub>, B<sub>c</sub>} for each c | Described in Sec 5 & 7.1; used in all experiments including Her2st (where annotations are withheld from training) [Paper] [Paper: PDF p. 5, p. 7] | Removal forces reliance on real annotations (infeasible for scale); ablation not done, but paper states this is core to annotation-free generalization [Paper] [Paper: PDF p. 6] |
| Differentiable U-statistic calculator | Approximates non-differentiable Mann–Whitney U test with smooth sigmoid to enable gradient flow | To make gene-ranking objective trainable; hard indicator 1[·] blocks backpropagation [Paper] [Paper: PDF p. 4–5] | Input: predicted expression matrix Ŷ (N×G), groups A<sub>c</sub>/B<sub>c</sub>; Output: ˆU<sub>c</sub> ∈ ℝ<sup>G</sup> | Eq. 1 defined on p.5; τ controls smoothness; tie term omitted as network outputs continuous [Paper] [Paper: PDF p. 5] | Removal reverts to non-differentiable ranking → no end-to-end training possible; confirmed by explicit statement [Paper] [Paper: PDF p. 5] |
| Gene-axis correlation loss L<sub>DEG</sub> | Aligns relative magnitudes of differential-expression scores across genes, preserving ranking order | To directly optimize for DEG list agreement (π<sub>c</sub> ≈ ˆπ<sub>c</sub>); conventional spot-axis PCC cannot capture cross-gene ordering [Paper] [Paper: PDF p. 4–5] | Input: ˆU<sub>c</sub>, U<sub>c</sub> (both G-dim vectors); Output: scalar L<sub>DEG</sub> = 1 − Corr<sub>g</sub>(ˆU<sub>c</sub>, U<sub>c</sub>) [Paper] [Paper: PDF p. 5, Eq. 2] | Table 4 shows “Ours w/o DEG ranking” (using MSE on U instead of Corr<sub>g</sub>) fails to boost nDCGDEG@200, proving correlation over genes is essential [Paper] [Paper: PDF p. 8] | Removal reduces to “Ours w/o DEG ranking” → performance collapse in nDCGDEG@200 (Table 4: 0.494→0.491 on Bowel) |
| Auxiliary PCC regularizer L<sub>const</sub> | Constrains per-gene spatial profile fidelity as a stabilizing prior | To prevent degenerate solutions where ˆU<sub>c,g</sub> aligns but individual ŷ<sub>i,g</sub> are meaningless; ensures basic spatial consistency [Paper] [Paper: PDF p. 5] | Input: Ŷ, Y (both N×G); Output: scalar L<sub>const</sub> = 1 − mean<sub>g</sub>[Corr<sub>i</sub>(ŷ<sub>•,g</sub>, y<sub>•,g</sub>)] [Paper] [Paper: PDF p. 5] | Table 5 shows Ours maintains intermediate per-gene PCC (e.g., 0.322 on Bowel vs 0.345 for MSE), confirming L<sub>const</sub> preserves baseline spatial fidelity [Paper] [Paper: PDF p. 9] | Removal (λ=0) likely degrades spatial profile quality; not ablated, but paper states it’s for “stabilizing training” [Paper] [Paper: PDF p. 5] |

## 09 关键公式与符号  
论文未给出完整可核验的闭式公式（如网络结构），但明确定义了以下关键符号与可验证操作：  
- **U<sub>c,g</sub>**: 真实 one-sided Mann–Whitney U statistic for gene g under contrast c (one-vs-rest), computed as sum over i∈A<sub>c</sub>, j∈B<sub>c</sub> of indicator 1[y<sub>i,g</sub> > y<sub>j,g</sub>] + 0.5·1[y<sub>i,g</sub> = y<sub>j,g</sub>] [Paper] [Paper: PDF p. 4]  
- **ˆU<sub>c,g</sub>**: Differentiable approximation: Σ<sub>i∈A<sub>c</sub></sub> Σ<sub>j∈B<sub>c</sub></sub> σ((ŷ<sub>i,g</sub> − ŷ<sub>j,g</sub>)/τ), where σ is sigmoid, τ is temperature [Paper] [Paper: PDF p. 5, Eq. 1]  
- **π<sub>c</sub>**: Reference ranked gene list = argsort↓<sub>g</sub>(U<sub>c,g</sub>) [Paper] [Paper: PDF p. 4]  
- **ˆπ<sub>c</sub>**: Predicted ranked gene list = argsort↓<sub>g</sub>(ˆU<sub>c,g</sub>) [Paper] [Paper: PDF p. 4]  
- **L<sub>DEG</sub>**: DEG-ranking loss = 1 − (1/|C|) Σ<sub>c∈C</sub> Corr<sub>g</sub>(ˆU<sub>c</sub>, U<sub>c</sub>) [Paper] [Paper: PDF p. 5, Eq. 2]  
- **L = L<sub>DEG</sub> + λL<sub>const</sub>**: Overall loss, with λ=1.0 [Paper] [Paper: PDF p. 5, Eq. 3]  
- **SCCDEG<sub>c</sub>**: Spearman rank correlation between U<sub>c</sub> and ˆU<sub>c</sub> across genes [Paper] [Paper: PDF p. 6, Eq. 4]  
- **nDCGDEG<sub>c</sub>@k**: Normalized Discounted Cumulative Gain for top-k DEGs, using binary relevance rel<sub>c</sub>(g) = 1[g ∈ top-k of π<sub>c</sub>] [Paper] [Paper: PDF p. 6, Eq. 5]  
No other equations are formally defined beyond these.

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|-------------------------------|--------|
| Cluster-based DEG (Table 1) | Our IDER objective improves DEG ranking over conventional objectives when groups are morphology-derived | All methods trained on HEST-1K (Ovary/Lymph Node/Bowel); groups from K-means (k=10) on CONCH features; evaluated on nDCGDEG@50/100/200 & SCCDEG | Ours achieves highest scores across all datasets/metrics (e.g., nDCGDEG@200: 0.595 vs 0.546 for NB on Bowel) | Morphology-derived proxy contrasts + IDER loss enable superior DEG ranking even without biological labels | Not that IDER works for *all* morphological granularities — tested only at k=10 during training | [Paper] [Paper: PDF p. 7, Table 1] |
| Generalization to grouping granularity (Figure 2) | Model trained at fixed granularity (k=10) generalizes to unseen coarser groupings | Evaluated on Lymph Node with k=10,8,6,4,2 clusters; same trained model, no finetuning | Ours consistently best across all k (nDCGDEG@200: 0.643 at k=10 → 0.601 at k=2) | IDER-trained models encode morphology-DEG associations robustly across scales, enabling flexible downstream analysis | Not that generalization holds for k>10 or pathological extremes (e.g., k=100) | [Paper] [Paper: PDF p. 7, Figure 2] |
| Real annotation-based DEG (Table 3) | IDER-trained model transfers to expert-annotated tissue regions without seeing annotations | Trained on Her2st using morphology clusters; evaluated on pathologist-annotated regions (adipose, connective, etc.) | Ours outperforms all baselines on all subtypes (e.g., invasive cancer: nDCGDEG=0.301 vs 0.176 for MSE) | Morphology-derived proxy groups capture biologically meaningful tissue variation, enabling zero-shot transfer to pathology annotations | Not that model understands pathology semantics — it learns statistical associations, not causal mechanisms | [Paper] [Paper: PDF p. 8, Table 3] |
| Pathway enrichment overlap (Table 2) | Improved DEG ranking translates to better preservation of functional interpretation | Top-200 DEGs from predicted/measured profiles fed to Reactome/KEGG; Jaccard index computed on top-200 enriched pathways | Ours achieves highest Jaccard across all datasets (e.g., 0.571 on Lymph Node vs 0.443 for NB) | IDER preserves downstream biological utility — predicted DEG lists yield more concordant pathway hypotheses | Not that individual pathway predictions are accurate; Jaccard measures set overlap, not directionality or significance | [Paper] [Paper: PDF p. 8, Table 2] |
| Ablation (Table 4) | Inter-gene ranking optimization (Corr<sub>g</sub>) is critical, not just DEG signal presence | “Ours w/o DEG rank.” replaces L<sub>DEG</sub> with MSE on U-vector; same architecture/data | Removing ranking component drops nDCGDEG@200 sharply (e.g., 0.595→0.491 on Bowel) | Gene-axis correlation is necessary to capture ranking structure; MSE on U alone is insufficient | Not that Corr<sub>g</sub> is the only viable ranking surrogate — alternatives (e.g., NDCG loss) untested | [Paper] [Paper: PDF p. 8, Table 4] |
| Plug-in to ST-Net/TRIPLEX (Table 6) | IDER objective is architecture-agnostic and modular | ST-Net and TRIPLEX trained with original loss vs + Ours loss on Her2st | Both gain substantially (e.g., ST-Net nDCGDEG@200: 0.073→0.247) | IDER can be adopted as a drop-in replacement for any ST predictor, enhancing its biological utility | Not that plug-in works for *all* architectures — only tested on ST-Net and TRIPLEX | [Paper] [Paper: PDF p. 9, Table 6] |

## 11 对结论的正确理解  
- **IDER 是任务定义，不是模型**：论文贡献首先是形式化 IDER 任务（Fig.1b），其次才是提供可微分实现；任何能优化 DEG 排序的方法都属 IDER 范畴。  
- **“Better DEG ranking” ≠ “Better gene expression”**：Table 5 explicitly shows Ours trades off per-gene PCC for ranking quality — this is intentional design, not deficiency.  
- **Proxy contrasts are sufficient, not perfect**：K-means on CONCH features approximates biology but doesn’t replicate ground-truth pathology; success in Her2st (Table 3) shows sufficiency for transfer, not equivalence.  
- **Pathway overlap is emergent, not engineered**：No pathway priors are injected (unlike PEaRL [20]); improved Jaccard (Table 2) is a *consequence* of better DEG ranking, validating biological relevance.  
- **Generalization is empirical, not theoretical**：Figure 2 shows robustness across k=2–10, but makes no claim about extrapolation beyond this range or to unseen tissue types.  
- **Plug-in success requires compatible output**：The method assumes predictor outputs ŷ<sub>i</sub> ∈ ℝ<sup>G</sup>; it wouldn’t apply to generative models outputting distributions without modification.

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|--------------------------|----------------------------------------|--------|
| Dependence on foundation model quality | Performance tied to CONCH feature quality; if CONCH fails on novel tissue, proxy groups degrade | Explore alternative foundation models or self-supervised histology encoders | [Paper] [Paper: PDF p. 6] states CONCH is used, but no robustness analysis against encoder failure |
| Limited evaluation on rare cell types | In Her2st, classes with <10 spots/patient excluded due to unreliable statistics | Develop DEG ranking metrics robust to ultra-sparse groups (e.g., single-cell aware) | [Paper] [Paper: PDF p. 7] notes exclusion of small classes; no proposal for sparse-group adaptation |
| No explicit handling of batch effects | Training uses single-dataset splits; no multi-center or stain-variance robustness test | Integrate stain-normalization or domain-adversarial components into IDER framework | Not mentioned in limitations section; absence implies unstudied |
| Static contrast construction | Proxy groups fixed at training time; cannot adapt to user-defined contrasts at inference | Enable on-the-fly contrast definition (e.g., user scribbles) with lightweight fine-tuning | [Paper] [Paper: PDF p. 5] describes offline clustering; no inference-time contrast flexibility discussed |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|--------|
| IDER’s success may stem from implicit spatial regularization in U-statistic computation, not pure ranking alignment | The double sum Σ<sub>i∈A</sub>Σ<sub>j∈B</sub> inherently aggregates spatial neighborhood information; high nDCGDEG@200 could reflect better spatial coherence rather than true DEG prioritization | Confounds interpretation: Is improvement due to better biological signal or better spatial smoothing? This affects trust in DEG lists for validation | Train a control model that computes U-statistic on *spatially shuffled* ŷ<sub>i,g</sub> (breaking spatial structure but preserving marginal distributions) and compare nDCGDEG | U-statistic definition depends on pairwise spot comparisons [Paper] [Paper: PDF p. 4], so spatial arrangement is baked in; no ablation tests spatial vs ranking contribution |
| nDCGDEG@200 may overemphasize top-200 while ignoring long-tail biological signals | Many disease-relevant genes reside outside top-200; SCCDEG (Spearman) captures global order but is less used in practice | Clinical utility depends on actionable top hits; if IDER distorts mid-rank genes, pathway analysis (Table 2) could be misleading despite high Jaccard | Report nDCG@50, @100, @200 separately (done in Table 1) AND analyze precision@k for k=10,20,50 on known marker genes from literature | Table 1 reports @50/@100/@200, showing consistent gains, but no marker-specific validation is performed [Paper] [Paper: PDF p. 7] |
| Pathway Jaccard overlap (Table 2) conflates sensitivity and specificity | High Jaccard could arise from both methods missing the same pathways, not recovering correct ones | For biomedical AI, false positives in DEG lists are costly; Jaccard alone doesn’t reveal whether recovered pathways are biologically plausible | Compute pathway-level precision/recall against gold-standard disease pathways (e.g., Hallmark sets) instead of just set overlap | Paper uses Reactome/KEGG but no external validation against curated disease pathways [Paper] [Paper: PDF p. 8] |
| Plug-in gains (Table 6) might be attributable to increased training stability from L<sub>const</sub>, not IDER’s ranking objective | L<sub>const</sub> is retained in plug-in; its PCC term could simply improve convergence, making STRank/ST-Net train better | Undermines the core claim that IDER objective is the driver; confounds architectural vs objective contribution | Run plug-in ablation: ST-Net + L<sub>const</sub> only (no L<sub>DEG</sub>) vs ST-Net + full L — compare nDCGDEG@200 | Paper adds full L = L<sub>DEG</sub> + λL<sub>const</sub> in plug-in [Paper] [Paper: PDF p. 9], but no ablation isolates L<sub>const</sub>’s role |

## 14 学到的知识  
- **下游对齐设计原则**：当模型输出需服务于特定下游分析（如 DEG ranking → pathway enrichment），应直接优化该分析的中间产物（U-statistic vector），而非原始输出（expression matrix）；这是比“post-hoc correction”更根本的对齐。  
- **代理对比组（proxy contrast）是一种通用范式**：在缺乏黄金标注时，用无监督特征聚类生成对比组，可作为生物学差异的廉价代理；该思路可迁移到 single-cell foundation models 中的 condition-aware representation learning。  
- **排名可微分化的工程选择**：温度控制的 sigmoid 平滑（Eq. 1）比 soft-sort 或 neural sort 更轻量，且 τ 可调——大 τ 适合稳定训练，小 τ 逼近离散排序；这对 perturbation prediction 中的 top-K gene selection有直接启示。  
- **评价指标必须与目标同构**：用 nDCGDEG@200 评价 DEG discovery 是因为临床关注 top hits；若目标是 biomarker panel discovery, 应设计 panel-level metrics (e.g., Jaccard of top-10 gene sets)。  
- **模块化即插即用的价值**：L<sub>DEG</sub> + L<sub>const</sub> 损失可无缝替换任何回归头，证明“下游感知”不必重构整个模型——这对用户现有 spatial transcriptomics pipeline 的升级极为友好。  
- **形态学-基因关联的鲁棒性**：CONCH 聚类生成的 proxy groups 能泛化到 Her2st 真实标注（Table 3），说明现代病理 foundation models 已编码足够强的 morphology-biology mapping，可作为 biomedical AI 的可靠中间表示。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：  
  - 与 *single-cell foundation models*：IDER 的 proxy contrast idea maps to scFoundation’s “condition-aware masking” —— 两者均用无监督 grouping 替代稀疏标注，但 IDER 将 grouping 用于 ranking alignment，scFoundation 用于 masked reconstruction。  
  - 与 *spatial transcriptomics*：本文的 U-statistic over spots parallels spatial DEG tools like SPARK-X, but IDER lifts it to image-conditioned prediction; Table 5’s per-gene PCC trade-off echoes debates in ST denoising about spatial fidelity vs biological signal.  
  - 与 *graph neural networks*：虽然本文未用 GNN，但 Fig.1b 的 “U-statistic → ranking” 流程可自然嵌入 spatial graph：A<sub>c</sub>/B<sub>c</sub> 定义图节点子集，U<sub>c,g</sub> 成为图级 readout，为 GNN-based ST predictors 提供新监督信号。  
  - 与 *multi-omics*：IDER 的核心是 cross-modal alignment (image ↔ expression) via downstream task —— 这与 multi-omics integration 中“alignment via shared biological function”（如 MOFA+）理念一致，但 IDER 用可微分 ranking 替代 latent space correlation。  
  - 与 *perturbation prediction*：IDER 的 contrast-specific ranking is analogous to perturbation-response ranking (e.g., “which genes most change after drug X?”); the differentiable U-statistic could replace current rank-losses in perturbation models.  
  - 与 *cell state representation*：π<sub>c</sub> = argsort↓(U<sub>c,g</sub>) defines a “morphology-responsive gene signature” —— this is a functional cell-state representation grounded in image-derived context, complementary to PCA/UMAP embeddings.  
- **弱连接/方法论连接**：  
  - *biomedical AI*：IDER provides a concrete, evaluable definition of “biological utility”, moving beyond accuracy metrics toward clinical actionability — highly relevant for FDA-cleared AI tools.  
  - *cross-modal alignment*：IDER is a task-driven alignment paradigm: instead of maximizing image-expression similarity in embedding space (e.g., CLIP-style), it aligns their *downstream analytical consequences* — a more rigorous form of alignment.

## 16 研究想法

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Morphology-Guided Perturbation Prioritization  
  **originating limitation/observation**: IDER uses static morphology-derived groups, but perturbation experiments (e.g., drug treatment) define dynamic, intervention-specific contrasts [Analysis] — current proxy groups cannot capture treatment-induced morphological shifts.  
  **core hypothesis**: Fine-tuning IDER’s contrast generator on pre/post-perturbation image pairs enables discovery of genes whose expression changes most sensitively to intervention, outperforming static morphology groups.  
  **delta from paper**: Replace offline K-means with contrast-aware adapter on CONCH, trained on paired pre/post images to predict perturbation-responsive groups.  
  **initial method**: Given pre-treatment image x<sub>pre</sub> and post-treatment x<sub>post</sub>, train adapter to output group assignment δ(x<sub>pre</sub>,x<sub>post</sub>) that maximizes U-statistic separation for known responsive genes (e.g., from LINCS).  
  **validation**: On CMap or DrugCell datasets, compare nDCG@50 of predicted top-responsive genes against ground-truth perturbation signatures.  
  **failure modes**: Adapter overfits to technical artifacts (stain drift); pre/post pairs too scarce for stable contrast learning.  
  **innovation status**: unverified  

- **name**: Graph-Regularized IDER for Spatial Context  
  **originating limitation/observation**: IDER computes U-statistic over spot pairs but ignores spatial adjacency — a gene highly expressed in adjacent tumor spots should contribute more to U<sub>c,g</sub> than distant ones [Analysis].  
  **core hypothesis**: Incorporating spatial graph structure (e.g., Visium spot neighbors) into U-statistic weighting improves localization of morphology-associated DEGs.  
  **delta from paper**: Modify Eq. 1 to ˆU<sub>c,g</sub> = Σ<sub>i∈A<sub>c</sub></sub> Σ<sub>j∈B<sub>c</sub></sub> w<sub>ij</sub> · σ((ŷ<sub>i,g</sub>−ŷ<sub>j,g</sub>)/τ), where w<sub>ij</sub> is adjacency weight from spatial graph.  
  **initial method**: Build k-nearest neighbor graph on spot coordinates; set w<sub>ij</sub> = exp(−d<sub>ij</sub><sup>2</sup>/σ<sup>2</sup>) for neighbors, 0 otherwise; integrate into loss L<sub>DEG</sub>.  
  **validation**: Compare nDCGDEG@200 on Her2st with/without graph weighting; inspect top-ranked genes for spatial coherence (e.g., enriched in contiguous tumor regions).  
  **failure modes**: Graph construction sensitive to spot density; weighting may suppress long-range biological signals (e.g., immune infiltration).  
  **innovation status**: unverified  

- **name**: Cross-Modal Alignment via Shared DEG Manifold  
  **originating limitation/observation**: IDER aligns image-predicted and measured U-vectors, but multi-omics data (e.g., ATAC+RNA) have their own DEG rankings — no mechanism to align *across modalities* [Analysis].  
  **core hypothesis**: Jointly optimizing IDER losses for image→RNA and ATAC→RNA predictions forces their U-statistic vectors to lie on a shared “DEG manifold”, improving cross-modal interpretability.  
  **delta from paper**: Extend L<sub>DEG</sub> to L<sub>DEG</sub><sup>img</sup> + L<sub>DEG</sub><sup>atac</sup> + λ<sub>align</sub>·||U<sub>c</sub><sup>img</sup> − U<sub>c</sub><sup>atac</sup>||<sub>2</sub><sup>2</sup>, where U<sup>atac</sup> is ATAC-derived contrast score.  
  **initial method**: On matched multi-omics ST data (e.g., 10x Multiome), compute ATAC-based U-statistic using chromatin accessibility peaks as proxy for gene regulation; add alignment term.  
  **validation**: Measure correlation of top-100 DEGs between modalities; assess if joint training improves pathway Jaccard over single-modality IDER.  
  **failure modes**: ATAC-RNA coupling weak in some tissues; U-statistic may not be appropriate for sparse ATAC data.  
  **innovation status**: unverified