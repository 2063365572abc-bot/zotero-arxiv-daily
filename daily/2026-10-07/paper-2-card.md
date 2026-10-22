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
| URL | http://arxiv.org/abs/2609.33928v1 | [Paper meta] |
| PDF URL | https://arxiv.org/pdf/2609.33928v1 | [Paper meta] |
| Publication date | 2026-09-27 | [Paper meta] |
| Core task | Image-based Differential Expression Ranking (IDER) | [Paper] [Paper: PDF p. 2] |
| Key metric | nDCGDEG@200, SCCDEG, pathway Jaccard overlap | [Paper] [Paper: PDF p. 6–8] |
| Primary datasets | HEST-1K (Bowel/Ovary/Lymph Node), Her2st | [Paper] [Paper: PDF p. 6–7] |
| Proxy contrast source | K-means clustering on CONCH embeddings | [Paper] [Paper: PDF p. 5, p. 6] |
| Model architecture | Frozen CONCH + 3-layer MLP | [Paper] [Paper: PDF p. 6] |

## 02 一句话总结  
该论文指出：当前基于组织学图像预测空间基因表达（ST prediction）的方法普遍采用“逐基因空间轮廓重建”目标（如PCC、MSE），但这一目标与下游核心任务——差异表达基因（DEG）发现——存在根本错配：DEG发现依赖的是**跨基因的对比统计排序**（contrast-specific ranked gene list），而非单个基因在空间上的表达拟合精度。为此，作者提出**Image-based Differential Expression Ranking (IDER)** 任务，并设计可微分的U-statistic对齐目标（Equation 1–2），利用形态学聚类生成的代理对比（proxy contrasts）进行无标注训练，使模型能直接优化DEG排序保真度。实验证明其在nDCGDEG@200和通路富集重叠（Jaccard）上显著优于所有常规重建目标，且可即插即用地提升ST-Net、TRIPLEX等现有架构；但其在传统per-gene PCC指标上表现中等，印证了“下游任务对齐”与“重建精度”的权衡本质。

## 03 研究问题  
- **核心问题**：为什么现有histology-to-ST模型在per-gene空间轮廓重建（如PCC）上表现良好，却无法可靠支持下游DEG发现？  
- **隐含假设**：常规重建目标（如PCC）虽能保证每个基因在空间维度上的表达趋势相似，但无法约束不同基因在**对比统计量（如U-stat）上的相对排序关系**，而该排序正是DEG报告、通路解释和生物学验证的起点。  
- **方法路径**：不改变模型结构，而是重构训练目标——从“最小化每个基因的空间误差”转向“最大化预测U-stat向量与真实U-stat向量在基因轴上的Pearson相关性（Equation 2）”，并辅以轻量级PCC正则项（Equation 3）维持基本空间一致性。

## 04 研究背景与发展路径  
- **起点**：ST技术成本高、通量低，亟需用广泛存在的H&E图像预测空间基因表达（[Paper] [Paper: PDF p. 1]）。  
- **主流范式**：ST-Net [8]、TRIPLEX [4]、GCN/Transformer [6,38]、检索/扩散模型 [35,39] 均以**逐基因空间重建**为优化目标（MSE/PCC）或评估标准（Figure 1a）[Paper] [Paper: PDF p. 1–2]。  
- **瓶颈浮现**：RankByGene [11] 和 STRank [25] 已尝试引入排序思想，但聚焦于**空间位置间表达排序**（spot-wise ranking），而非**基因间差异证据排序**（gene-wise DEG ranking）[Paper] [Paper: PDF p. 3]。  
- **关键洞察跃迁**：作者识别出“评价轴错位”——重建目标沿空间轴（spot）求平均，而DEG分析沿基因轴（gene）做排序；因此必须将评价与优化轴统一到**基因维度**，即用U-stat向量间的相关性替代单基因PCC [Paper] [Paper: PDF p. 2, 4]。  
- **技术支点**：CONCH病理基础模型 [19] 提供鲁棒形态学表征，使其能通过无监督聚类生成可信的proxy contrasts，绕过对昂贵病理标注的依赖 [Paper] [Paper: PDF p. 5, 6]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|-------------|----------------------------|--------------------------|
| Objective misalignment | Models with high per-gene PCC (e.g., MSE/PCC baselines) show poor nDCGDEG@200 and low pathway Jaccard overlap | Conventional objectives optimize spatial-profile agreement *within each gene*, but DEG discovery depends on *cross-gene ranking by contrast statistics* [Paper] [Paper: PDF p. 1–2] | Table 5 shows MSE/PCC achieve highest PCC (0.235–0.345), yet Table 1/3 show they rank worst on nDCGDEG@200 (e.g., 0.434 vs. 0.531 for Ours); Table 2 shows their pathway Jaccard is lowest (0.326–0.345 vs. 0.381 for Ours) [Paper] [Paper: PDF p. 7–8] |
| Annotation bottleneck | Real tissue-region annotations (e.g., Her2st) are scarce, costly, and patient-specific, limiting generalizable DEG analysis | Biological group labels are often unavailable; morphology-derived proxy groups offer scalable, annotation-free alternatives [Paper] [Paper: PDF p. 6] | Section 7.1 explicitly constructs groups via K-means on CONCH features *without any annotation*, and Figure 2 shows strong generalization across k=2–10 clusters [Paper] [Paper: PDF p. 6–7] |
| Non-differentiability of ranking | Direct optimization of argsort-based DEG ranking (πc) is non-differentiable, blocking end-to-end training | Sorting and indicator functions (e.g., 1[yi,g > yj,g]) break gradient flow [Paper] [Paper: PDF p. 4–5] | Equation 1 replaces hard indicator with temperature-scaled sigmoid σ((ŷi,g−ŷj,g)/τ); Equation 2 uses Corrg over genes instead of discrete ranking loss [Paper] [Paper: PDF p. 5] |

## 06 核心思想  
论文的核心思想是**将ST预测的任务定义从“表达值重建”升维至“生物学决策保真”**：不再问“预测的每个基因表达值在空间上有多准”，而是问“预测的表达值能否导出与真实数据一致的、用于生物学发现的基因优先级列表”。这体现为三个递进层次：  
1. **评价升维**：用SCCDEG（Spearman across genes）和nDCGDEG@k（top-k recovery）替代传统PCC（Pearson across spots）；  
2. **目标可微化**：将非可微的Mann–Whitney U statistic离散比较（Equation in Sec. 4）替换为连续sigmoid近似（Equation 1），再以基因轴Pearson相关（Equation 2）作为排序保真代理损失；  
3. **监督弱化**：放弃对真实生物标签（如tissue region）的依赖，转而用CONCH特征聚类生成形态学proxy contrasts，在训练中动态采样one-vs-rest组别，使模型学习“哪些基因的表达变化最能区分形态差异”这一本质信号 [Paper] [Paper: PDF p. 5–6]。

## 07 方法总览  
该方法是一个**目标函数即插即用框架**，不修改模型架构，仅替换训练损失：  
- **输入**：组织学图像块xi与对应spot真实表达yi（G维向量）；  
- **特征提取**：冻结CONCH模型提取图像嵌入，接3层MLP输出预测表达ŷi；  
- **代理对比构建**：对训练集CONCH嵌入做K-means（k=10），每轮随机选一簇为Ac（positive），其余为Bc（negative）；  
- **可微U-stat计算**：对每个对比c和基因g，按Equation 1计算∑i∈Ac∑j∈Bc σ((ŷi,g−ŷj,g)/τ)，得向量Ûc ∈ ℝ^G；  
- **主损失LDEG**：对每个c，计算Corrg(Ûc, Uc)（Uc为真实U-stat向量），取均值后用1−Corrg作为损失（Equation 2）；  
- **辅助损失Lconst**：标准per-gene PCC损失，加权λ=1.0（Equation 3）；  
- **输出**：预测表达ŷi → 可计算任意对比下的Ûc → argsort↓(Ûc)即为预测DEG排名。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| Morphology-derived proxy contrast generator | Generates K-means clusters on frozen CONCH embeddings to define Ac/Bc groups without biological labels | Enables training without costly pathologist annotations; provides diverse morphology-defined contrasts for robust DEG learning | Input: Training image patches xi → Output: Cluster assignments li ∈ {1,…,K} | Described in Sec. 5 & 7.1; used in all experiments (e.g., k=10 for training, k=2–10 for Figure 2) [Paper] [Paper: PDF p. 5–6] | Without it, model cannot train on unannotated data (e.g., HEST-1K); would require manual labels or fail in cluster-based setting |
| Differentiable U-stat approximator | Replaces hard indicator 1[ŷi,g > ŷj,g] with sigmoid σ((ŷi,g−ŷj,g)/τ) to compute Ûc,g | Makes Mann–Whitney U statistic differentiable for end-to-end optimization; τ controls gradient smoothness | Input: Predicted expression ŷi,g, τ → Output: Scalar Ûc,g | Equation 1 explicitly defined; τ is a tunable hyperparameter [Paper] [Paper: PDF p. 5] | Removal reverts to non-differentiable sorting; training fails as gradients vanish (not empirically tested but implied by design rationale) |
| DEG-ranking surrogate objective (LDEG) | Computes 1 − Corrg(Ûc, Uc) across genes to align predicted and true contrast statistics | Directly optimizes preservation of gene ordering by differential evidence, not raw expression values | Input: Vectors Ûc, Uc ∈ ℝ^G → Output: Scalar loss LDEG | Equation 2; ablation in Table 4 shows “Ours w/o DEG ranking” (MSE on U) performs worse than full LDEG [Paper] [Paper: PDF p. 5, 8] | Removal reduces nDCGDEG@200 by ~0.08 (Ovary) and SCCDEG by ~0.10 (Table 4), proving ranking alignment is essential |
| Auxiliary expression-consistency regularizer (Lconst) | Standard PCC loss averaged over genes, correlating ŷi,g and yi,g across spots | Prevents degeneration where Ûc,g aligns but individual gene spatial patterns collapse; stabilizes training | Input: Matrices Ŷ, Y ∈ ℝ^{N×G} → Output: Scalar Lconst | Equation 3; described as “lightweight” and used with λ=1.0 [Paper] [Paper: PDF p. 5] | Removal (tested implicitly via ablation “Baseline” in Table 4) yields lower SCCDEG (0.584 vs. 0.686) and much lower nDCGDEG (0.451 vs. 0.531), showing spatial consistency aids ranking |

## 09 关键公式与符号  
- **No verifiable closed-form equation beyond those provided**. The paper defines three core equations, all present in input:  
  - **Equation 1**: `Ûc,g = Σi∈Ac Σj∈Bc σ((ŷi,g − ŷj,g)/τ)` — differentiable U-stat approximation; `σ` = sigmoid, `τ` = temperature, `ŷi,g` = predicted expression of gene g at spot i.  
  - **Equation 2**: `LDEG = 1 − (1/|C|) Σc∈C Corrg(Ûc, Uc)` — DEG-ranking surrogate loss; `Corrg` = Pearson correlation computed *across genes* (g=1..G), not spots.  
  - **Equation 3**: `L = LDEG + λLconst` — overall loss; `Lconst` = conventional PCC loss (defined in Sec. 5 but not numbered).  
- **Key symbols**:  
  - `Uc,g`: True one-sided Mann–Whitney U statistic for gene g under contrast c (Sec. 4).  
  - `πc = argsort↓g(Uc,g)`: Reference DEG ranking list for contrast c (Sec. 4).  
  - `SCCDEGc = Spearmang(Uc, Ûc)`: Spearman rank correlation between true/predicted U-stat vectors (Eq. 4).  
  - `nDCGDEGc@k`: Normalized Discounted Cumulative Gain for top-k DEGs (Eq. 5).  
  - `Ac, Bc`: Positive/negative spot sets in one-vs-rest contrast (Sec. 4 & 5).

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|---------------------------|--------|------------------------|------------------------------|--------|
| Cluster-based DEG (Table 1, Figure 2) | IDER objective improves DEG ranking under morphology-derived contrasts | All methods trained on HEST-1K (Ovary/Lymph Node/Bowel); groups from K-means (k=10); evaluation on nDCGDEG@50/100/200 & SCCDEG | Ours achieves highest scores across all metrics and datasets (e.g., nDCGDEG@200: 0.531 vs. 0.453 for MSE&PCC in Ovary) | Morphology-derived proxy contrasts + IDER objective enable superior DEG ranking vs. reconstruction objectives | Not claimed: superiority generalizes to *all* ST datasets or clinical cohorts (only public benchmarks tested) | [Paper] [Paper: PDF p. 7], Table 1, Figure 2 |
| Real annotation-based DEG (Table 3) | IDER-trained model generalizes to pathologist-annotated tissue regions without seeing labels during training | Trained on Her2st using proxy clusters; evaluated on real annotations (adipose, connective, etc.) | Ours outperforms all baselines on SCCDEG/nDCGDEG for every tissue type (e.g., SCCDEG=0.475 for connective tissue vs. 0.317 for MSE&PCC) | Proxy contrasts capture morphology-biology associations sufficiently to transfer to real annotations | Not claimed: performance matches expert-level annotation quality; no human-in-the-loop validation | [Paper] [Paper: PDF p. 7–8], Table 3 |
| Pathway enrichment overlap (Table 2) | IDER preserves downstream functional interpretation | Top-200 DEGs from predicted/measured profiles fed to Reactome/KEGG; Jaccard index computed | Ours achieves highest Jaccard across all datasets (e.g., 0.571 for Lymph Node vs. 0.443 for NB) | Better DEG ranking → better pathway-level biological signal recovery | Not claimed: recovered pathways are experimentally validated; no wet-lab confirmation | [Paper] [Paper: PDF p. 8], Table 2 |
| Ablation (Table 4) | Inter-gene ranking alignment (not just U-stat magnitude) is critical | “Ours w/o DEG ranking” adds MSE loss on Uc but no Corrg; “Baseline” uses only PCC | Removing ranking alignment drops nDCGDEG@200 by 0.08 (Ovary) and SCCDEG by 0.10 | Optimizing *relative order* of U-stat values matters more than absolute U-stat fidelity | Not claimed: Corrg is optimal choice; other ranking losses (e.g., ListNet) were not compared | [Paper] [Paper: PDF p. 8], Table 4 |
| Plug-in (Table 6) | IDER objective is architecture-agnostic | Applied to ST-Net and TRIPLEX on Her2st; same training protocol | Both architectures show large nDCGDEG@200 gains (e.g., ST-Net: 0.073 → 0.247) | IDER loss can be adopted as a drop-in replacement for existing ST models | Not claimed: gains scale linearly with model size; no test on foundation-scale models | [Paper] [Paper: PDF p. 9], Table 6 |

## 11 对结论的正确理解  
- **核心结论成立**：IDER目标确实提升了DEG排序保真度（nDCGDEG@200）、全局排序一致性（SCCDEG）及下游通路解释力（Jaccard），且该提升独立于模型架构（plug-in results）和对比来源（proxy vs. real annotations）。  
- **边界清晰**：提升是**相对的**——相比MSE/PCC等基线，而非绝对完美（e.g., nDCGDEG@200 max=1.0, Ours=0.595）；提升是**task-specific**——在per-gene PCC上逊于专用重建模型（Table 5），证明其牺牲部分重建精度换取下游任务对齐。  
- **机制可信**：Ablation（Table 4）证实ranking alignment（Corrg）比U-stat magnitude fitting（MSE on U）更关键；generalization across k=2–10 clusters (Figure 2) confirms proxy contrasts encode robust morphology signals.  
- **不可外推**：未证明该方法在single-cell resolution、multi-omics integration或perturbation prediction场景有效；未验证其在临床诊断级WSI或跨机构泛化能力。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|-------------------------------------|--------|
| Dependence on morphology-derived proxy contrasts | Proxy groups may not fully capture biologically meaningful tissue states (e.g., subtle molecular subtypes) | Explore integration with weak supervision from limited expert annotations or multi-modal signals (e.g., proteomics) [Paper] [Paper: PDF p. 9] | [Paper] [Paper: PDF p. 9] (end of Sec. 7.3) |
| Evaluation limited to bulk-spot ST | Current setup assumes spot-level expression; does not address single-cell deconvolution or sub-spot heterogeneity | Extend IDER to single-cell resolution by defining contrasts at cellular level or leveraging cell-type priors | [Paper] [Paper: PDF p. 9] (end of Sec. 7.3) |
| No clinical outcome correlation | DEG ranking improvement not linked to patient survival, treatment response, or diagnostic accuracy | Future work should correlate IDER performance with clinical endpoints in retrospective cohorts | [Paper] [Paper: PDF p. 9] (end of Sec. 7.3) |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|------------------------------------------|----------------|----------------|-------|
| Proxy contrasts rely on CONCH embeddings, which are trained on generic pathology tasks, not ST-specific morphology | CONCH may miss ST-relevant histological nuances (e.g., stromal-tumor interface patterns critical for DEG) → proxy groups could misalign with true biology | If proxy groups poorly reflect biological contrasts, IDER optimization may learn spurious correlations, harming generalization to real annotations | Compare IDER performance when proxy groups are generated by ST-specialized foundation models (e.g., HistoST) vs. CONCH on Her2st; analyze cluster purity w.r.t. real annotations | [Paper] [Paper: PDF p. 5–6] states use of CONCH but no ablation on embedding source; Her2st annotations exist but weren’t used for proxy generation |
| nDCGDEG@k focuses only on top-k recovery, ignoring ranking quality in mid/lower tiers | A model could “game” nDCG by boosting top-k genes while scrambling the rest, yielding high nDCG but poor overall biological utility | Downstream analyses (e.g., pathway enrichment) depend on broader gene sets; over-optimizing top-k may neglect functionally coherent modules outside top-200 | Report nDCG@500 or Kendall’s tau for full ranking; correlate full Ûc vector with pathway membership (e.g., via GSEA) instead of binary top-k relevance | [Paper] [Paper: PDF p. 6] defines nDCGDEG@k but only reports @50/100/200; Table 2 uses top-200 for pathways, suggesting sensitivity to cutoff |
| Auxiliary Lconst uses simple PCC, which is known to be sensitive to outliers and zero-inflation in ST data | Outlier spots (e.g., necrotic regions) could dominate Lconst, pulling optimization away from DEG-critical morphology | Compromised spatial consistency might degrade DEG ranking in morphologically ambiguous regions (e.g., tumor margins) | Replace Lconst with robust correlation (e.g., Spearman) or zero-inflated loss (e.g., ZINB) and measure impact on nDCGDEG@200 | [Paper] [Paper: PDF p. 5] calls Lconst “lightweight” but gives no justification for PCC choice; ST data is known to be sparse/outlier-prone [24] |

## 14 学到的知识  
- **任务定义升维是关键创新点**：将ST预测从“reconstruction”重新定义为“downstream decision fidelity”（IDER），直击领域痛点，比单纯改进模型架构更具范式意义。  
- **可微排序代理的设计智慧**：用温度控制的sigmoid近似U-stat + 基因轴Pearson相关，巧妙绕过argsort不可微困境，比listwise ranking losses（如ListMLE）更契合DEG分析的统计本质。  
- **代理监督的价值被低估**：K-means on CONCH features generates surprisingly effective proxy contrasts—no ground-truth labels needed, yet generalizes to real annotations (Table 3) and varying granularities (Figure 2).  
- **下游指标与上游目标必须对齐**：Table 5 proves that high PCC ≠ good DEG ranking; thus，评估必须匹配最终用途，而非沿用历史惯性指标。  
- **模块化即插即用潜力**：Table 6显示IDET loss boosts ST-Net/TRIPLEX without architecture changes—为快速迭代ST模型提供新范式。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：  
  - 与**single-cell foundation models**：IDER’s use of morphology-derived proxy contrasts parallels scFoundation’s use of cell-type priors for contrastive learning; both avoid hard labels by leveraging unsupervised structure.  
  - 与**spatial transcriptomics**：IDER directly addresses the “spatial DEG detection” gap in ST analysis tools (e.g., SPARK, SpatialDE) by making prediction DEG-aware.  
  - 与**graph neural networks**：GNN-based ST models (e.g., [6,38]) could integrate IDER loss to enhance neighborhood-aware DEG ranking, as current GNNs focus on spatial smoothing, not cross-gene prioritization.  
  - 与**multi-omics**：IDER’s contrast-centric view aligns with multi-omics integration frameworks (e.g., MOFA+) that seek joint latent spaces preserving contrast-specific signals across modalities.  
  - 与**biomedical AI**：IDER exemplifies “clinical-task-aligned AI”—prioritizing decision outputs (DEG lists) over intermediate representations (expression matrices), resonating with diagnostic AI principles.  
- **弱连接/方法论连接**：  
  - **perturbation prediction**：IDER’s contrast statistics resemble perturbation response signatures; adapting IDER to predict gene ranking shifts under drug/CRISPR perturbations is plausible but untested.  
  - **cell state representation**：The Ûc vector per contrast acts as a morphology-conditioned cell-state signature; could be used as input to cell-state classifiers, but paper doesn’t explore this.  
  - **cross-modal alignment**：IDER aligns histology (image) and transcriptomics (U-stat) at the *decision level* (ranking), offering an alternative to feature-level alignment (e.g., CLIP-style); however, no explicit cross-modal loss is defined.

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Morphology-Guided Perturbation DEG Ranking (MorphoPert)  
  **originating limitation/observation**: Proxy contrasts in IDER are static (K-means on baseline images), but perturbation responses (e.g., drug treatment) induce dynamic morphology changes not captured by baseline clustering [Analysis in Sec. 13].  
  **core hypothesis**: Learning perturbation-specific proxy contrasts—by clustering histology features *after* in silico perturbation simulation or using time-series WSI—will improve prediction of perturbation-induced DEG rankings.  
  **delta from paper**: Replaces static K-means with perturbation-conditioned contrast generation (e.g., GAN-based morphological perturbation + contrastive clustering).  
  **initial method**: Train a conditional GAN to simulate drug-treated histology from baseline WSI; extract features from perturbed images; cluster to get Ac/Bc (treated/untreated); apply IDER loss on simulated contrasts.  
  **validation**: Test on CMap or LINCS perturbation datasets with matched histology + RNA-seq; compare nDCGDEG@200 for predicted vs. measured perturbation DEGs.  
  **failure modes**: GAN artifacts dominate clustering; perturbation morphology too subtle for CONCH to resolve; lack of paired perturbed histology-RNA-seq data.  
  **innovation status**: unverified  

- **name**: Graph-Aware IDER (GraphIDER)  
  **originating limitation/observation**: IDER treats spots as independent in U-stat computation (Σi∈Ac Σj∈Bc), ignoring spatial adjacency and tissue graph structure known to modulate DEG signals [Paper] [Paper: PDF p. 3 cites GCN works].  
  **core hypothesis**: Constraining U-stat comparisons to spatially adjacent spot pairs (i,j) within and across Ac/Bc will yield more biologically grounded DEG rankings, especially for locally interacting tissues (e.g., tumor-stroma interface).  
  **delta from paper**: Modifies Equation 1 to sum only over spatially neighboring (i,j) pairs, weighted by graph adjacency matrix Aij.  
  **initial method**: Build spatial graph from Visium spot coordinates (k-NN); replace Σi∈Ac Σj∈Bc with Σi∈Ac Σj∈Bc Aij · σ((ŷi,g−ŷj,g)/τ); retain Corrg(Ûc,Uc) as LDEG.  
  **validation**: Apply to Her2st with known tumor/stroma boundaries; compare nDCGDEG@200 for stroma-enriched genes (e.g., COL1A1) vs. baseline IDER.  
  **failure modes**: Over-smoothing in dense graphs; loss of long-range contrast signals; increased computational cost.  
  **innovation status**: unverified  

- **name**: Cross-Modal Alignment via DEG Ranking (CM-ALIGN)  
  **originating limitation/observation**: IDER aligns histology→transcriptomics, but multi-omics studies need alignment across modalities (e.g., histology + proteomics + methylation); current IDER is unimodal [Paper] [Paper: PDF p. 3 mentions multi-omics briefly].  
  **core hypothesis**: Jointly optimizing DEG rankings across two modalities (e.g., histology-predicted and proteomics-predicted expression) using shared contrast statistics will enforce cross-modal biological consistency.  
  **delta from paper**: Extends IDER to dual-modality: compute Ûc,hist and Ûc,prot for same contrast c; add loss term Corrg(Ûc,hist, Ûc,prot) to align rankings across modalities.  
  **initial method**: Use paired histology-proteomics dataset (e.g., CPTAC); train separate predictors f_hist, f_prot; for each contrast c, compute Ûc,hist and Ûc,prot; minimize 1−Corrg(Ûc,hist, Ûc,prot) alongside individual IDER losses.  
  **validation**: On CPTAC breast cancer cohort; assess if CM-ALIGN improves concordance of top DEGs between predicted proteomics and measured transcriptomics.  
  **failure modes**: Modality-specific noise dominates alignment; lack of large-scale paired multi-omics ST datasets; domain gap between histology and proteomics feature spaces.  
  **innovation status**: unverified