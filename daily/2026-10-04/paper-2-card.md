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
| Title | CellMSA: Context Modeling for Single-Cell Representation Learning | [Paper] |
| Venue | arXiv preprint (NeurIPS 2026 submission) | [Paper] [Paper: PDF p. 1] |
| Authors | Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie | [Paper] [Paper: PDF p. 1] |
| Publication date | 2026-09-30 | [Paper meta] |
| Pretraining scale | ~109M human cell observations (65.6M primary) | [Paper] [Paper: PDF p. 1, 3, 6] |
| Core analogy | Protein MSA → single-cell “MSA” context | [Paper] [Paper: PDF p. 2, Fig 1] |
| Key architecture modules | CellMSA-Module, GenePairformer | [Paper] [Paper: PDF p. 4, Fig 2] |
| Pretraining objectives | LMGM, LRec, LCCE | [Paper] [Paper: PDF p. 6] |
| Downstream tasks covered | Batch integration, cell type/state classification, perturbation prediction, interpretability | [Paper] [Paper: PDF p. 7–10] |
| Evaluation datasets | Tabula Sapiens (24 tissues), Kidney Atlas (PT states), Replogle (perturbations) | [Paper] [Paper: PDF p. 7–8, App C.2] |
| Code availability | https://github.com/PharMolix/CellMSA | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结  
CellMSA 提出一种受蛋白质多序列比对（MSA）启发的单细胞上下文建模范式，通过跨批次、跨细胞类型的邻近细胞构建“单细胞MSA”，并从中提炼基因对（gene-pair）表示以指导目标细胞编码；该方法在batch integration、cell state classification与perturbation prediction三大任务上系统性超越现有foundation models，且其gene-pair表示可解释疾病相关基因网络重编程。其核心价值在于将高维稀疏单细胞数据中隐含的细粒度基因共表达与状态依赖关系，从统计关联层面显式建模为context-aware gene-pair结构，而非仅依赖单细胞独立编码或粗粒度batch-level denoising。

## 03 研究问题  
单细胞基础模型为何难以捕获与细胞状态强相关的细粒度基因-基因依赖？现有方法（如独立编码、同批多细胞联合建模）虽缓解了技术噪声，但因上下文受限于局部实验条件（same-batch）或压缩损失基因分辨率，无法稳定提取跨批次一致、跨类型对比凸显的生物学信号；这导致模型表征缺乏对疾病状态、扰动响应等精细生物学变化的判别力。作者假设：引入类似AlphaFold中MSA的归纳偏置——即通过聚合跨样本的一致性与变异性来推断稳定结构约束——可使单细胞模型从细胞群中解耦出状态特异的基因共表达模式。

## 04 研究背景与发展路径  
单细胞基础模型演进呈现两条主线：（1）**独立建模路线**（Geneformer/scGPT）：将每个细胞视为独立token，依赖大规模预训练学习通用表征，但受限于单细胞高稀疏性与技术噪声，难以区分生物变异与随机波动 [Paper] [Paper: PDF p. 1–2]；（2）**多细胞上下文路线**（CellPLM/STATE/Stack）：通过组织同批细胞为“句子”或“模块”增强denoising能力，但存在两大瓶颈——一是采用gene-weighted averaging/cell encoders等压缩策略丢失基因级细节 [Paper] [Paper: PDF p. 2]，二是上下文局限于same-batch same-type，缺乏跨批次稳定性验证与跨类型功能对比信号 [Paper] [Paper: PDF p. 2]。CellMSA定位为第三条路径：继承MSA范式中“跨同源序列聚合保守性与共进化”的思想，将其迁移至单细胞场景，构建包含same-batch、cross-batch、cross-type三类细胞的MSA-like context，以保留基因分辨率并注入生物学鲁棒性。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|------------------------------|--------------------------|
| **上下文信息贫瘠** | 模型无法区分技术噪声与真实生物变异，尤其在低测序深度或高dropout条件下 | 现有方法仅用单细胞输入或同批细胞，缺乏跨条件一致性验证信号 | “when the model relies on only a single observation… difficult to distinguish biological variation from stochastic noise” [Paper] [Paper: PDF p. 2] |
| **基因分辨率丢失** | 细粒度基因-基因依赖（如marker gene co-expression）建模能力弱 | 多细胞上下文方法采用gene-weighted averaging/cell encoders等压缩策略 | “such compression can discard gene-level information and therefore limit the model’s ability to capture fine-grained gene-gene dependencies” [Paper] [Paper: PDF p. 2] |
| **上下文生物学意义不足** | 上下文主要反映局部实验条件，难以支持跨批次泛化或疾病特异网络识别 | 上下文仅组织same-batch same-type细胞，未显式引入cross-batch（稳定性）与cross-type（功能对比）信号 | “such context mainly reflects shared patterns under local experimental conditions… may be less effective at improving robustness across batches” [Paper] [Paper: PDF p. 2] |
| **缺乏可解释的中间表示** | 模型输出为黑箱细胞向量，难追溯其对特定生物学过程（如肾损伤）的响应机制 | 现有foundation models未设计显式建模基因间关系的模块 | “CellMSA enables us to capture state-dependent gene-gene relationships at the single-cell level” [Paper] [Paper: PDF p. 9]; Fig 4 shows GO enrichment from head-specific gene-pair heatmaps |

## 06 核心思想  
CellMSA 的核心思想是将单细胞表征学习重构为一个**上下文驱动的基因对关系建模问题**：不直接优化细胞向量，而是先从跨批次、跨类型的细胞集合（MSA-like context）中，通过迭代交互（Outer-product Mean ↔ Pair-weighted Averaging）提炼出一个context-dependent gene-pair representation $P \in \mathbb{R}^{G \times G \times d_p}$；再将此$P$作为attention bias注入target-cell encoder（GenePairformer），使最终细胞表征$z_i$显式承载基因间依赖先验。该设计直击三大痛点：（1）MSA-like context提供跨条件一致性信号，提升噪声鲁棒性；（2）全程保持$G$维基因分辨率，避免压缩损失；（3）$P$本身即为可解释的生物学中间表示（如Fig 4中head 7捕获PT损伤网络）。

## 07 方法总览  
CellMSA 流程分三阶段：（1）**MSA-like context construction**：对每个target cell $c_i$，检索三组邻居——$N^{\text{same batch}}_i$（同批同型，denoising）、$N^{\text{cross batch}}_i$（跨批同型，稳定性）、$N^{\text{cross type}}_i$（跨型，功能对比），并为每类邻居添加relation-type embedding [Paper] [Paper: PDF p. 4]；（2）**Context-aware gene-pair learning**：CellMSA-Module在低维空间$d'$中交替更新context gene reps $m^l$与gene-pair rep $P^l$，通过Outer-product Mean聚合跨细胞共变、Pair-weighted Averaging反馈pair信息到gene reps [Paper] [Paper: PDF p. 5, App A.1]；（3）**Target-cell encoding with pair bias**：GenePairformer将最终$P^{L_{\text{MSA}}}$投影为head-specific $R^0$，并在self-attention中将其作为bias（$R^{L+1,H}_{uv} = R^{L,H}_{uv} + Q^{L,H}_u (K^{L,H}_v)^\top / \sqrt{d_H}$），实现pair-aware序列建模 [Paper] [Paper: PDF p. 5]。预训练采用三目标联合优化：LMGM（masked gene modeling）、LRec（cell reconstruction）、LCCE（cell contrastive learning）[Paper] [Paper: PDF p. 6]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **CellMSA-Module** | 从MSA-like context中提取context-dependent gene-pair representation $P$ | 解决“上下文信息贫瘠”与“基因分辨率丢失”：需在不压缩基因维度前提下，聚合跨细胞一致性/变异性 | Input: target cell + $N_i$ neighbors (S rows × G genes); Output: $P^{L_{\text{MSA}}} \in \mathbb{R}^{G \times G \times d_p}$ | Fig 2 shows $P^0$→$P^{L_{\text{MSA}}}$ flow; Eq in [Paper] [Paper: PDF p. 5] defines Outer-product Mean & Pair-weighted Averaging | Ablation in Table 4: w/o CellMSA-Module drops PT accuracy from 0.958→0.854 & Pearson Δ from 0.433→0.355 [Paper] [Paper: PDF p. 10] |
| **GenePairformer** | 将$P$注入target-cell编码，生成pair-aware cell representation $z_i$ | 解决“缺乏可解释中间表示”：需将$P$转化为下游可用的细胞向量，同时保留$P$的生物学语义 | Input: target cell gene embeddings $e_{1g}$, $P^{L_{\text{MSA}}}$; Output: $z_i \in \mathbb{R}^d$ (cls token projection) | Fig 2 shows $h^0$→$h^L$ & $R^0$→$R^L$ joint update; Eq in [Paper] [Paper: PDF p. 5] defines attention bias injection | If replaced by standard Transformer (w/o $R$), loses gene-pair guidance → ablation shows performance collapse [Paper] [Paper: PDF p. 10] |
| **MSA-like context retrieval** | 构建包含same-batch/cross-batch/cross-type三类细胞的context | 解决“上下文生物学意义不足”：same-batch denoise, cross-batch enforce stability, cross-type enable functional contrast | Input: target cell $c_i$; Output: $N_i = N^{\text{same batch}}_i \cup N^{\text{cross batch}}_i \cup N^{\text{cross type}}_i$ | Sec 3.1 [Paper] [Paper: PDF p. 4] details sampling strategy; Appendix C.1 shows hierarchical clustering for cross-type selection [Paper] [Paper: PDF p. 26–27] | Ablation in Table 4: w/o Context drops PT accuracy to 0.878 & Pearson Δ to 0.389; Only Same-batch Context achieves 0.929/0.400 < Full Model 0.958/0.433 [Paper] [Paper: PDF p. 10] |
| **Pretraining objectives (LMGM/LRec/LCCE)** | 协同优化局部基因预测、全局细胞重建、生物判别性 | 防止representation collapse：LMGM ensures local fidelity, LRec preserves cell-specificity, LCCE enforces biological grouping | Joint loss $L = L_{\text{MGM}} + \lambda_1 L_{\text{Rec}} + \lambda_2 L_{\text{CCE}}$ | Sec 3.3 [Paper] [Paper: PDF p. 6] defines all three losses; Fig A.5 [Paper] [Paper: PDF p. 25] shows λ balance effect on PT UMAP | Fig A.5 [Paper] [Paper: PDF p. 25]: λ₂=0 (no LCCE) → over-separation by cell state; λ₁=0 (no LRec) → noisy embedding → empirical λ₁=0.01, λ₂=10 chosen |

## 09 关键公式与符号  
论文未给出可核验的完整公式体系，但明确定义了以下关键符号与操作：  
- **MSA-like context**: $N_i = N^{\text{same batch}}_i \cup N^{\text{cross batch}}_i \cup N^{\text{cross type}}_i$ [Paper] [Paper: PDF p. 4]  
- **Outer-product Mean update**: $p^{l+1}_{uv} = p^{l}_{uv} + W^l_p \left( \frac{1}{S} \sum_{s=1}^S a^l_{su} \otimes b^l_{sv} \right)$, where $a^l_{su}, b^l_{sv}$ are linear projections of $m^l_{su}, m^l_{sv}$, $\otimes$ is outer product [Paper] [Paper: PDF p. 5]  
- **Pair-weighted Averaging update**: $m^{l+1}_{su} = m^{l}_{su} + W^l_o \left( \gamma^{l,h}_{su} \odot \sum_v \text{softmax}_v \left( W^{l,h}_b p^{l+1}_{uv} \right) v^{l,h}_{sv} \right)$ [Paper] [Paper: PDF p. 5]  
- **GenePairformer attention bias**: $R^{L+1,H}_{uv} = R^{L,H}_{uv} + \frac{Q^{L,H}_u (K^{L,H}_v)^\top}{\sqrt{d_H}}$ [Paper] [Paper: PDF p. 5]  
- **Pretraining loss**: $L = L_{\text{MGM}} + \lambda_1 L_{\text{Rec}} + \lambda_2 L_{\text{CCE}}$, with $L_{\text{MGM}} = \frac{1}{|\Omega|} \sum_{g \in \Omega} \text{CrossEntropy}(x_{i,g}, \hat{x}_{i,g})$ [Paper] [Paper: PDF p. 6]  
- **Key metrics**: Pearson Δ (perturbation), NMI/ARI (clustering), BRAS/iLISI/kBET (batch correction), ASW/cLISI (bio-conservation) [Paper] [Paper: PDF p. 30]  

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|-----------------------------|--------|------------------------|-------------------------------|--------|
| **Batch integration (Tabula Sapiens)** | CellMSA improves batch mixing while preserving biology better than baselines | Label-informed context (CellMSA/Stack vs. scVI/scGPT/Geneformer/STATE-SE); scib-metrics benchmark | CellMSA achieves highest total score (0.736), NMI (0.895), ARI (0.805), BRAS (1.000), iLISI (0.242), kBET (0.627) [Table 1] | CellMSA’s MSA context yields superior integration quality under label-informed setting | Cannot claim superiority in label-free setting without direct comparison—though CellMSA still leads (0.688 vs Stack 0.600) [App B.1.1, Table A.27] | [Paper] [Paper: PDF p. 7, Table 1, App B.1] |
| **Cell state classification (Kidney Atlas PT)** | CellMSA captures fine-grained disease-associated transcriptional states | PT cell states (aPT/dPT/dPT/DTL); 5-run MLP on embeddings; donor-split train/val/test | CellMSA achieves highest accuracy (0.958±0.004), macro-F1 (0.931±0.006), weighted-F1 (0.958±0.004) [Table 2] | CellMSA representations resolve subtle intra-lineage disease states better than alternatives | Does not prove causality—only correlation between representation and labels | [Paper] [Paper: PDF p. 8, Table 2] |
| **Perturbation prediction (Replogle)** | CellMSA provides more robust latent space for modeling cellular transitions | Combined with STATE-ST module; Pearson Δ, PRAUC, Spearman-FC, DE Overlap | CellMSA+STATE-ST achieves highest Pearson Δ (0.433), PRAUC (0.334), Spearman-FC (0.431), DE Overlap (0.215) [Table 3] | CellMSA’s context-aware representations improve perturbation effect prediction fidelity | Not validated on non-Replogle perturbations or in vivo settings | [Paper] [Paper: PDF p. 9, Table 3] |
| **Interpretability (Fig 4)** | Gene-pair representations encode disease-associated network reconfiguration | Head-wise differential hub scores & GO enrichment on PT healthy vs disease | Head 7 shows strongest disease-associated shifts; GO terms include ECM reorganization, integrin signaling, cellular dedifferentiation [Fig 4c] | CellMSA’s gene-pair representations are biologically interpretable and anchored in pathological signals | Does not prove these are causal regulatory networks—authors explicitly state they reflect statistical associations [Paper] [Paper: PDF p. 10] | [Paper] [Paper: PDF p. 9, Fig 4] |
| **Ablation (Table 4)** | Performance gains stem from MSA context & CellMSA-Module | w/o CellMSA-Module, w/o Context, Only Same-batch Context on PT classification & perturbation | Full model consistently best; removing CellMSA-Module causes largest drop (Δacc=0.104, ΔPearson=0.078) [Table 4] | CellMSA-Module and multi-source context are essential components | “Cross-type” context alone insufficient—requires full tripartite design | [Paper] [Paper: PDF p. 10, Table 4] |

## 11 对结论的正确理解  
CellMSA 的成功源于其**上下文构造范式与基因对表示机制的协同**：它并非简单增加训练数据量，而是通过精心设计的MSA-like context（same/cross-batch/type）和CellMSA-Module（Outer-product/Pair-weighted Averaging），将原本隐含在细胞群体中的基因共表达模式显式蒸馏为可计算、可注入、可解释的$P$。因此，其优势具有明确的因果链条——Table 4 ablation证实移除CellMSA-Module导致性能断崖式下跌，Fig 4证明$P$能富集已知病理通路，Table 1/2/3显示该设计在多个正交任务上泛化。但必须注意：所有结论均基于作者定义的benchmark与metric，其生物学解释力限于统计关联层面（作者明确承认），且预训练数据规模（109M）虽大，但可能隐含atlas-level偏差（Appendix C.1提及“overrepresenting particular cells”）。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **Statistical vs. causal interpretation** | Gene-pair representations reflect statistical associations, not explicit causal regulatory relationships | Incorporate prior knowledge of gene regulation and causal machine learning methods | [Paper] [Paper: PDF p. 10] |
| **Dependence on cell-type annotations for context** | Label-informed context retrieval requires high-quality cell-type labels, limiting applicability to poorly annotated datasets | The label-free ablation (App B.1.1) shows CellMSA still outperforms Stack without labels, but gap narrows (0.688 vs 0.600) | [Paper] [Paper: PDF p. 7, App B.1.1] |
| **Computational cost of CellMSA-Module** | Complexity scales quadratically with gene count ($O(SG^2d_p^2)$), potentially limiting scalability to ultra-large gene vocabularies | Not explicitly proposed, but Appendix A.2 notes design choice to keep CellMSA-Module in low-dim $d'$ while GenePairformer operates in full $d$ | [Paper] [Paper: PDF p. 16, App A.2] |
| **Pretraining data composition bias** | Corpus includes non-primary observations (re-aggregations), risking overrepresentation of specific atlas structures | Audit indicates most non-primary obs come from same-study re-aggregations; contextual distinction mitigates but doesn’t eliminate risk | [Paper] [Paper: PDF p. 26, App C.1] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|-------|
| [Analysis] CellMSA’s “cross-type” context relies on hierarchical clustering of mean expression profiles, which may conflate developmental lineage with functional similarity | Cell types clustered together (e.g., CD4+ T cell & monocyte in same cluster, Table A.31) may share technical artifacts (e.g., similar dissociation protocols) rather than true biological relatedness, leading to spurious gene-pair signals | If context similarity stems from batch effects而非biology, CellMSA may learn batch-correlated patterns masquerading as biological ones, undermining its claimed robustness | Re-run clustering using batch-corrected expression or integrate chromatin accessibility data to validate functional relatedness; compare CellMSA performance on datasets with known batch-confounded clusters | [Paper] [Paper: PDF p. 26–27, App C.1, Table A.31] |
| [Analysis] The GenePairformer’s attention bias injection uses $R^{L+1,H}_{uv} = R^{L,H}_{uv} + Q^{L,H}_u (K^{L,H}_v)^\top / \sqrt{d_H}$, but this treats gene-pair $R$ as additive to standard attention logits—no gating or normalization mechanism prevents $R$ from dominating early layers | Uncontrolled $R$ magnitude could destabilize training or suppress learned sequence features, especially if $R$ contains noisy context signals | This architectural choice risks making the model overly dependent on context quality; poor context retrieval would degrade all downstream tasks uniformly | Ablate with $R$ scaled by learnable $\alpha^L$ or apply softmax over $R$ before addition; monitor gradient norms of $R$ vs $Q/K/V$ during training | [Paper] [Paper: PDF p. 5, Eq]; no discussion of $R$ scaling in text or appendix |
| [Analysis] Perturbation prediction evaluation uses STATE-ST module trained on top of frozen CellMSA embeddings, but STATE-ST itself has capacity to learn context—so improvement may reflect STATE-ST’s adaptation to CellMSA’s representation space, not intrinsic superiority of CellMSA | The gain in Pearson Δ (0.433 vs 0.358 for Stack) could be partly due to better alignment between CellMSA’s latent space and STATE-ST’s inductive bias, rather than CellMSA encoding more biological signal | This confounds attribution: is CellMSA better, or is STATE-ST just better tuned to it? Without end-to-end training or alternative decoders, causal claim about CellMSA’s representation quality is weakened | Train identical decoder architectures (e.g., simple MLP) on all embeddings; or perform ablation where STATE-ST is replaced by same architecture across all encoders | [Paper] [Paper: PDF p. 8–9, Sec 4.4]; STATE-ST is fixed across comparisons |

## 14 学到的知识  
- **MSA范式的可迁移性**：蛋白质MSA中“跨同源序列聚合保守性与共进化”的思想，可严格映射为单细胞中“跨相似细胞聚合一致性与变异性以提取marker gene与co-expression”，且需配套设计（如三源context、pair representation、bias injection）才能落地，非简单类比。  
- **上下文构造的生物学先验**：same-batch（denoise）、cross-batch（stability）、cross-type（contrast）三元划分，是比单纯增加邻居数量更高效的上下文设计原则，直接对应不同层次的生物学需求。  
- **基因对表示（gene-pair representation）作为中间接口的价值**：它既是可解释的生物学模块（Fig 4），又是可注入的结构先验（GenePairformer bias），更是可ablate的模块化组件（Table 4），为foundation model提供了比cell vector更细粒度的调控杠杆。  
- **预训练目标的互补性平衡**：LMGM（local）、LRec（global）、LCCE（discriminative）三目标存在张力（Fig A.5），需经验调优λ权重；其中LCCE对batch robustness贡献显著，而LRec防collapse，二者缺一不可。  
- **评估需正交分解**：scib-metrics将batch correction与bio-conservation分离打分（Table 1），避免单一指标掩盖缺陷；perturbation metrics区分整体effect（Pearson Δ）与DE gene ranking（PRAUC/DE Overlap），揭示模型不同能力维度。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：CellMSA的MSA-like context与spatial transcriptomics中neighbor graph construction（如STAGATE、SpaGCN）共享“利用空间邻域聚合信号”思想，但CellMSA将邻域扩展至跨批次/跨类型，突破空间局限；其gene-pair representation与graph neural networks中edge-level modeling（如GAT edge features）形式相似，但CellMSA的$P$由跨细胞统计生成，非learned edge weights。  
- **候选连接/方法论连接**：CellMSA的tripartite context retrieval（same/cross-batch/type）可启发multi-omics整合——例如将“cross-omics”作为第三类context，用scRNA-seq细胞检索匹配的scATAC-seq或CITE-seq细胞，构建跨模态MSA。  
- **候选连接/方法论连接**：GenePairformer的attention bias机制与biomedical AI中prompt tuning或adapter-based fine-tuning有形式共性，均将外部知识（$P$或prompt）注入主干网络而不修改其参数。  
- **弱连接/方法论连接**：CellMSA的interpretability pipeline（head-wise differential hub scores → GO enrichment）为cell state representation研究提供了标准化可复现框架，但未与具体perturbation prediction模型（如scGen、DeepDR）直接集成。  
- **弱连接/方法论连接**：其pretraining corpus规模（109M）与single-cell foundation models（如scGPT、CellPLM）处于同一量级，但context-aware design使其在相同数据上获得更高下游性能，提示架构创新可部分替代数据量增长。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Cross-modal MSA for spatial-transcriptomic alignment  
  **originating limitation/observation**: CellMSA’s success relies on biologically meaningful context, but spatial transcriptomics lacks explicit “cross-type” analogues beyond tissue architecture; current spatial methods use kNN graphs ignoring molecular similarity [Analysis]  
  **core hypothesis**: Spatial spots from different modalities (e.g., Visium + Xenium) or same modality across donors can form a “cross-modal MSA” where consistency reveals spatially conserved gene programs, and variation highlights modality-specific artifacts  
  **delta from paper**: Replace $N^{\text{cross type}}_i$ with spots from complementary modalities (e.g., Visium spot $i$ retrieves Xenium spots with similar HVG expression), and add modality embedding to relation-type $r_{ij}$  
  **initial method**: Pretrain on paired spatial datasets (e.g., SPOTlight, Xenium-Visium cohorts); use spatial coordinates as additional input to CellMSA-Module; evaluate on cross-modal imputation (Xenium→Visium)  
  **validation**: Quantify imputation fidelity (SSIM, gene-wise correlation) and spatial pattern preservation (Moran’s I); compare to baseline spatial alignment (Harmony, Seurat)  
  **failure modes**: Modality-specific dropout patterns may dominate $P$; lack of ground-truth matched spots limits supervision  
  **innovation status**: unverified  

- **name**: Causal-pair refinement of CellMSA  
  **originating limitation/observation**: Authors explicitly state gene-pair representations reflect statistical associations, not causal relationships [Paper] [Paper: PDF p. 10]  
  **core hypothesis**: Integrating causal discovery priors (e.g., PC algorithm constraints, TF-target databases) into CellMSA-Module’s Outer-product Mean can bias $P$ toward directed regulatory edges  
  **delta from paper**: Replace vanilla outer product $a^l_{su} \otimes b^l_{sv}$ with masked version where $M_{uv}=0$ if $u$→$v$ is forbidden by prior knowledge (e.g., TF→target), and add KL divergence loss between $P$ and causal graph prior  
  **initial method**: Use DoRothEA TF-target database to construct mask $M$; modify Eq in [Paper] [Paper: PDF p. 5] to $p^{l+1}_{uv} = p^{l}_{uv} + W^l_p \left( \frac{1}{S} \sum_s a^l_{su} \otimes b^l_{sv} \cdot M_{uv} \right)$; add $L_{\text{causal}} = \text{KL}(P \| P_{\text{prior}})$  
  **validation**: Test on perturbation datasets (Replogle) — do refined $P$ better predict knockdown effects? Compare inferred TF→target edges against gold-standard CRISPR screens  
  **failure modes**: Prior knowledge incompleteness may prune true edges; KL loss may conflict with LMGM objective  
  **innovation status**: unverified  

- **name**: Lightweight CellMSA for rare cell types  
  **originating limitation/observation**: CellMSA requires ≥40 context cells (Fig 5) and hierarchical clustering of 818 cell types (App C.1), making it infeasible for rare or newly discovered cell types with few observations  
  **core hypothesis**: A “few-shot CellMSA” can leverage cross-species or cross-condition transfer: pretrain on abundant cell types, then adapt context retrieval for rare types using zero-shot gene set alignment (e.g., ortholog mapping, pathway enrichment)  
  **delta from paper**: Replace $N^{\text{cross type}}_i$ for rare type $c_i$ with cell types from other species (mouse/human) or conditions (healthy/disease) sharing top enriched pathways, retrieved via semantic similarity of GO term vectors  
  **initial method**: Compute GO term vector for rare type $c_i$ (from limited obs); find top-k matching types in pretraining corpus using cosine similarity; retrieve $N^{\text{cross type}}_i$ from matches  
  **validation**: Benchmark on rare immune subsets (e.g., tissue-resident memory T cells) in Tabula Sapiens; measure classification F1 gain vs standard CellMSA  
  **failure modes**: GO term sparsity for rare types; cross-species expression divergence may misalign contexts  
  **innovation status**: unverified