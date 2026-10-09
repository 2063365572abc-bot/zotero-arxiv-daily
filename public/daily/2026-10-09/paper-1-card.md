> Source coverage: Full paper  
> Extraction confidence: High  
> Locator mode: page-grounded  
> Primary analytical lens: methods  
> Secondary analytical lens: None  
> Context verification: Paper-only  
> Card completeness: Complete relative to supplied source  

## 01 基本信息

| Field | Value | Source |
|-------|--------|---------|
| Title | CellMSA: Context Modeling for Single-Cell Representation Learning | [Paper] [Paper: PDF p. 1] |
| Authors | Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (NeurIPS 2026 submission) | [Paper] [Paper: PDF p. 1] |
| Year | 2026 | [Paper] [Paper: PDF p. 1] |
| Core model | CellMSA (CellMSA-Module + GenePairformer) | [Paper] [Paper: PDF p. 4–5] |
| Key inspiration | Protein MSA context modeling (AlphaFold-style) | [Paper] [Paper: PDF p. 2, Fig. 1] |
| Pretraining scale | ~109M human cell observations (65.6M primary) | [Paper] [Paper: PDF p. 2, 3, 6, C.1] |
| Input modality | Discretized scRNA-seq gene expression (binned counts) | [Paper] [Paper: PDF p. 4] |
| Context composition | Same-batch + cross-batch + cross-type cells (N = 16+16+8) | [Paper] [Paper: PDF p. 4, 6] |
| Pretraining objectives | LMGM + LRec + LCCE (weighted joint loss) | [Paper] [Paper: PDF p. 6] |
| Downstream tasks | Batch integration, cell type/state classification, perturbation prediction | [Paper] [Paper: PDF p. 7–9] |
| Evaluation benchmarks | scib-metrics (batch), Tabula Sapiens, Kidney Atlas, Replogle | [Paper] [Paper: PDF p. 7–9, C.2] |
| Code availability | https://github.com/PharMolix/CellMSA | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结  
CellMSA 提出一种受蛋白质多序列比对（MSA）启发的单细胞上下文建模框架，通过为每个目标细胞检索跨批次、跨细胞类型的相似细胞构成“单细胞MSA”，并用CellMSA-Module提取上下文感知的基因对表示（gene-pair representation），再注入GenePairformer实现细粒度细胞表征学习；该设计显著提升了批效应校正、细胞状态分类与扰动响应预测能力，在Tabula Sapiens等大规模基准上全面超越现有foundation models。其核心价值在于将“跨样本一致性/变异性比较”这一生物信号提取范式从蛋白结构域迁移至单细胞转录组，且严格保持基因级分辨率，而非压缩式聚合。边界在于：所有上下文检索依赖标注（label-informed）或表达相似性（label-free），未建模空间或时序关系；预训练未覆盖perturbation任务本身，仅提供表征供下游STATE-ST模块调用。

## 03 研究问题  
**问题**：现有单细胞foundation models（如Geneformer、scGPT）普遍采用独立细胞编码或仅限同一批次多细胞联合建模，导致无法有效利用跨批次、跨细胞类型的生物学冗余与差异信号，从而难以捕获与细胞状态强相关的精细基因-基因依赖模式。  
**假设/洞察**：类比蛋白质MSA中通过多序列比对识别保守残基与共进化对以推断三维结构约束，单细胞场景下亦可通过聚合多个相似细胞（同型跨批、异型相关）的表达模式，识别marker基因与共表达网络，进而建模细胞状态特异的基因依赖关系。  
**方法路径**：不直接建模细胞间图结构或全局图神经网络，而是构造一个“伪MSA”输入矩阵（行=细胞，列=基因），在低维空间中迭代执行Outer-product Mean（聚合跨细胞共变）与Pair-weighted Averaging（反向调制基因表示），最终生成context-dependent gene-pair representation，并作为attention bias注入目标细胞Transformer编码器。

## 04 研究背景与发展路径  
单细胞foundation model演进呈现两条主线：（1）**独立编码路线**（Geneformer、scGPT）：将每个细胞视为独立token序列，依赖大规模预训练学习基因语义，但受限于单细胞稀疏性与噪声，难以区分生物变异与技术噪声 [Paper] [Paper: PDF p. 1–2]；（2）**局部上下文路线**（CellPLM、STATE、Stack）：引入同一批次内多细胞联合建模以提升去噪能力，但存在两大瓶颈——一是采用基因加权平均/模块压缩丢弃基因级细节 [Paper] [Paper: PDF p. 2]，二是上下文局限于同型同批，缺乏跨条件鲁棒性 [Paper] [Paper: PDF p. 2]。CellMSA定位为第三条路径：**跨条件、基因级、MSA式上下文建模**。它继承了Stack的“多细胞输入”形式，但摒弃其模块化压缩，转而借鉴AlphaFold中MSA模块的计算原语（Outer-product Mean / Pair-weighted Averaging）[Paper] [Paper: PDF p. 5, A.1]，将上下文作用机制从“统计降噪”升维至“状态特异关系发现”。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|----------------|------------------------------|--------------------------|
| **孤立细胞建模导致噪声敏感** | 单细胞表达高度稀疏、受测序深度/脱落/批次效应强烈干扰，独立编码难区分生物变异与随机噪声 | “when the model relies on only a single observation of a cell, it is often difficult to distinguish biological variation from stochastic noise” | [Paper] [Paper: PDF p. 2] |
| **现有上下文建模粒度粗、范围窄** | 跨细胞聚合常采用基因加权平均或细胞编码压缩，丢失基因对级别信息；上下文仅限同批同型，缺乏跨条件泛化能力 | “such compression can discard gene-level information… they do not explicitly exploit cross-batch signals or biologically related cell types” | [Paper] [Paper: PDF p. 2] |
| **缺乏状态特异的基因依赖建模机制** | 现有模型输出为细胞级向量，隐式包含基因关系，但不可解释、不可控、难迁移；无法显式建模如“PT损伤时CDH6-VIM共表达增强”此类病理网络 | “models can capture fine-grained gene-gene dependencies associated with cell states, which are essential for learning high-quality representations” | [Paper] [Paper: PDF p. 1, 2] |
| **上下文信息利用效率低** | 单纯增加上下文细胞数不必然提升性能，需结构化组织与高效计算机制 | “the ablation results demonstrate the performance gains resulting from incorporating the information-rich MSA context”；Fig. 5显示context size >40后收益饱和 | [Paper] [Paper: PDF p. 10, Fig. 5] |

## 06 核心思想  
CellMSA的核心思想是将**单细胞表征学习重构为一个“上下文驱动的关系发现”问题**，而非传统“特征提取”问题。其关键跃迁在于：（1）**上下文定义升维**：将上下文从“同批邻居”拓展为“same-batch + cross-batch + cross-type”三元组合，分别服务于局部去噪、跨批鲁棒性、功能对比增强 [Paper] [Paper: PDF p. 4]；（2）**关系建模解耦**：分离“关系发现”（CellMSA-Module，在低维d′空间用Outer-product Mean/PW-Avg迭代提炼gene-pair representation）与“主干编码”（GenePairformer，在高维d空间用pair-aware attention精调目标细胞），避免计算耦合导致的精度损失 [Paper] [Paper: PDF p. 5, A.2]；（3）**生物学先验注入**：通过relation-type embedding（same batch/cross batch/cross type）显式编码上下文来源的生物学意义，使模型能区分“技术相似”与“功能相关”信号 [Paper] [Paper: PDF p. 4]。

## 07 方法总览  
CellMSA是一个两阶段上下文感知编码框架：（1）**上下文关系提炼阶段**（CellMSA-Module）：以目标细胞+40个上下文细胞（16 same-batch + 16 cross-batch + 8 cross-type）构成MSA-like输入矩阵；通过LMSA层迭代执行Outer-product Mean（聚合跨细胞基因共变）与Pair-weighted Averaging（用更新后的gene-pair表示调制上下文基因表示），最终输出一个RG×G×dp维度的context-dependent gene-pair representation PLMSA；（2）**目标细胞精编阶段**（GenePairformer）：将PLMSA投影为head-specific pair representations R0，与目标细胞基因嵌入e1g共同输入LGPFLayer Transformer；在每层中，Rl被注入self-attention作为bias（RL+1,Huv = RL,Huv + QL,Hu(KL,Hv)⊤/√dH），实现gene-pair结构对序列编码的显式引导 [Paper] [Paper: PDF p. 5]。预训练采用三目标联合优化：LMGM（掩码基因预测）、LRec（细胞表达重建）、LCCE（细胞对比学习）[Paper] [Paper: PDF p. 6]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|-------------|-------------------|------------------------|-----------------------------------|
| **CellMSA-Module** | 从MSA-like上下文中提炼context-dependent gene-pair representation，捕捉跨细胞一致性/变异性 | 独立解决“如何从多细胞中高效提取基因对关系”问题，避免与高维目标编码耦合；低维d′设计降低计算开销 | Input: MSA-like input (S rows × G genes), Output: PLMSA ∈ RG×G×dp | Outer-product Mean & PW-Avg structures detailed in [Paper] [Paper: PDF p. 5, A.1]; complexity analysis shows O(SG²d′) cost [Paper] [Paper: PDF p. 16] | Removal causes >3% drop in PT state accuracy & >0.07 drop in Pearson Δ (Table 4); degenerates to standard Transformer [Paper] [Paper: PDF p. 10] |
| **GenePairformer** | 将gene-pair representation作为attention bias注入目标细胞编码，实现细粒度、关系引导的表征学习 | 需在保留目标细胞全基因分辨率前提下，融合外部关系信号；标准Transformer无此机制 | Input: target cell gene embeddings e1g, pair representations R0; Output: <cls> token embedding zi | Architecture diagram Fig. 2; pair-as-bias formula RL+1,Huv = RL,Huv + QL,Hu(KL,Hv)⊤/√dH [Paper] [Paper: PDF p. 5] | Without it, model loses ability to interpret disease networks (Fig. 4); ablation w/o CellMSA-Module confirms its necessity for pair-aware encoding [Paper] [Paper: PDF p. 10] |
| **MSA-like Context Construction** | 组织same-batch/cross-batch/cross-type三类细胞为结构化上下文，并添加relation-type embedding | 解决“上下文应包含什么生物学信号”问题；relation-type embedding enables model to distinguish noise-reduction vs. biology-enhancement contexts | Input: target cell ci; Output: Ni = Nsame batchi ∪ Ncross batchi ∪ Ncross typei, with rij ∈ {same batch, cross batch, cross type} | Section 3.1 formal definition [Paper] [Paper: PDF p. 4]; hierarchical clustering for cross-type neighbors described in [Paper] [Paper: PDF p. 6, C.1] | Ablation "Only Same-batch Context" drops PT accuracy by 2.9% and Pearson Δ by 0.033 vs full model (Table 4), proving cross-context value [Paper] [Paper: PDF p. 10] |
| **Three-Objective Pretraining** | LMGM (local fidelity) + LRec (global structure) + LCCE (biological discriminability) | 单一目标无法兼顾：LMGM易过拟合局部噪声，LRec易坍缩到细胞类型均值，LCCE易忽略状态内变异；三者协同平衡 | Joint loss L = LMGM + λ1LRec + λ2LCCE (λ1=0.01, λ2=10) | Section 3.3 & B.3 (Fig. A.5 shows trade-off visualization) [Paper] [Paper: PDF p. 6, 25] | Ablation in B.3 shows λ1=0 causes over-clustering by cell type (loss of state resolution), λ2=0 causes noise sensitivity [Paper] [Paper: PDF p. 25] |

## 09 关键公式与符号  
论文未给出可核验的完整数学公式（如端到端损失函数闭式），但明确定义了所有核心符号与模块计算逻辑：  
- **MSA-like context**: Ni = Nsame batchi ∪ Ncross batchi ∪ Ncross typei [Paper] [Paper: PDF p. 4]  
- **Relation-type embedding**: rij ∈ {same batch, cross batch, cross type}, encoded as Erel(rs) [Paper] [Paper: PDF p. 4]  
- **Outer-product Mean update**: pl+1uv = pluv + Wlp(1/S Σs=1S alsu ⊗ blsv) [Paper] [Paper: PDF p. 5, A.1]  
- **Pair-weighted Averaging update**: ml+1su = mlsu + Wlo(Concath γl,hsu ⊙ Σv Al,huv vl,hs v) [Paper] [Paper: PDF p. 5]  
- **GenePairformer attention bias**: RL+1,Huv = RL,Huv + QL,Hu(KL,Hv)⊤/√dH [Paper] [Paper: PDF p. 5]  
- **Pretraining loss**: L = LMGM + λ1LRec + λ2LCCE [Paper] [Paper: PDF p. 6]  
- **Hub score**: Hc,s,h(g) = 1/(G−1) Σj≠g P̄(h)c,s(g,j) [Paper] [Paper: PDF p. 24]  
- **Delta-hub score**: HΔabsc,h(g) = 1/(G−1) Σj≠g |P̄(h)c,disease(g,j) − P̄(h)c,healthy(g,j)| [Paper] [Paper: PDF p. 25]  
*注：所有公式符号均来自原文，无虚构；dp, d′, d, G, S等维度参数在附录C.2中明确给出（e.g., dp=8, d′=128, d=512, G=61982, S=41）[Paper] [Paper: PDF p. 28]*

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|-------------------------|----------------------------------|--------|
| **Batch integration (Table 1)** | CellMSA achieves superior batch mixing while preserving biology | Label-informed context: CellMSA vs Stack/scGPT/Geneformer/scVI/PC-HVG on Tabula Sapiens (24 tissues); metrics: NMI/ARI/ASW/cLISI (bio), BRAS/iLISI/kBET/Conn/PCR (batch) | CellMSA: Total score 0.736 > Stack 0.663 > scVI 0.600; highest NMI (0.895), ARI (0.805), ASW (0.699), iLISI (0.242), kBET (0.627) | CellMSA's MSA context improves both batch correction and biological conservation simultaneously under label-informed setting | That CellMSA dominates *all* baselines in *all* individual metrics (e.g., scVI has higher BRAS=1.000) | [Paper] [Paper: PDF p. 7, Table 1] |
| **Cell state classification (Table 2)** | CellMSA captures fine-grained disease-associated transcriptional states | PT cell state (aPT/dPT/dPT/DTL) on Kidney Atlas; 5-run avg; vs CellPLM/Stack/STATE-SE/scGPT/scVI | CellMSA: Accuracy 0.958±0.004, Macro F1 0.931±0.006 > CellPLM 0.794±0.012, Stack 0.909±0.009 | CellMSA's context modeling enables discrimination of subtle injury states within same epithelial lineage | That this superiority generalizes to *all* kidney cell types (only PT tested) | [Paper] [Paper: PDF p. 8, Table 2] |
| **Perturbation prediction (Table 3)** | CellMSA provides more robust latent space for perturbation response modeling | Using STATE-ST module on Replogle dataset (4 cell lines, 100 perturbations); vs Expression+STATE-ST/STATE-SE+STATE-ST/Stack+STATE-ST | CellMSA+STATE-ST: Pearson Δ 0.433 > Stack 0.358 (+8.8%), PRAUC 0.334 > Stack 0.293 | CellMSA's representations encode perturbation-relevant regulatory logic better than alternatives | That CellMSA alone (without STATE-ST) can predict perturbations (it's used as encoder only) | [Paper] [Paper: PDF p. 9, Table 3] |
| **Ablation study (Table 4)** | Performance gains stem from MSA context & CellMSA-Module | PT state classification & perturbation prediction; ablations: w/o CellMSA-Module, w/o Context, Only Same-batch Context | Full model best in all metrics; w/o CellMSA-Module drops Macro F1 by 2.0% (0.931→0.811) and Pearson Δ by 0.078 (0.433→0.355) | The CellMSA-Module and its MSA context are necessary and sufficient for observed gains | That other architectural choices (e.g., number of layers) are unimportant (not tested) | [Paper] [Paper: PDF p. 10, Table 4] |
| **Label-free integration (Table A.27)** | CellMSA retains advantage without cell-type labels | Bladder dataset; context via HVG-PCA-KNN (no labels); vs scGPT/Geneformer/Stack | CellMSA label-free total 0.688 > Stack 0.600; label-informed boosts to 0.748 | CellMSA's context mechanism works even without annotations, but labels provide additional benefit | That label-free CellMSA matches label-informed Stack (0.688 < 0.698) | [Paper] [Paper: PDF p. 22, Table A.27] |

## 11 对结论的正确理解  
CellMSA的结论必须置于其**特定实验设定与评估协议**中理解：（1）**上下文依赖性**：所有SOTA结果（Table 1/2/3）均基于label-informed context retrieval（使用cell-type标签构建上下文），这并非模型内在能力，而是数据利用策略；label-free版本（Table A.27）性能下降证实此点；（2）**下游任务耦合性**：perturbation预测（Table 3）完全依赖STATE-ST模块，CellMSA仅提供表征，其优势反映的是表征质量，而非端到端预测能力；（3）**生物学解释的限定性**：Figure 4的GO富集分析（ECM重组、dedifferentiation）是基于Head 7的delta-hub基因集，属**相关性解释**，作者明确声明“mainly reflect statistical associations rather than explicit causal regulatory relationships” [Paper] [Paper: PDF p. 10]；（4）**规模效应边界**：109M预训练规模带来收益，但附录C.1指出“109 million denotes observations rather than unique biological cells”，存在重复采样风险，且未验证scaling law。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|----------------------------------------|--------|
| **Statistical vs. causal interpretation** | Gene-pair representations reflect statistical associations, not causal regulatory mechanisms | Incorporate prior knowledge of gene regulation and causal machine learning methods | [Paper] [Paper: PDF p. 10] |
| **Context retrieval dependency** | Performance gain relies on access to cell-type labels or high-quality expression-based neighbors | Not explicitly stated, but label-free ablation (Table A.27) implies need for robust unsupervised context construction | [Paper] [Paper: PDF p. 22, Table A.27] |
| **Computational cost of CellMSA-Module** | Complexity dominated by O(SG²d′) term, scaling quadratically with gene count G | Not proposed, but Appendix A.2 notes design choice to keep CellMSA-Module in low-d′ space to mitigate cost | [Paper] [Paper: PDF p. 16] |
| **Limited modality scope** | Model operates solely on scRNA-seq; no integration with spatial, multi-omics, or protein data | Not proposed, but broader impacts section notes potential for "multi-omics" extension | [Paper] [Paper: PDF p. 31] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|-------------------------|-------------------------------------------|----------------|----------------|--------|
| **Context composition may introduce confounding** | Same-batch context (Nsame batch) includes cells from identical experimental conditions, potentially amplifying batch-specific technical artifacts rather than biological signals | Could degrade cross-batch robustness if model overfits to shared noise; contradicts stated goal of "encouraging biologically meaningful patterns stable across batches" | Train ablation using only cross-batch + cross-type context (exclude same-batch), evaluate on scib-metrics batch correction scores (iLISI/kBET) | [Paper] [Paper: PDF p. 4] defines Nsame batch for "local similarity and support denoising", but does not validate its net effect on batch robustness |
| **Gene-pair representation lacks directional validation** | Figure 4b shows gene-pair heatmap for PT markers, but no test confirms if learned pairs (e.g., CDH6-VIM) align with known physical interactions (e.g., STRING) beyond the KDR validation in Appendix B.2.4 | Weak external validation undermines claims of "biologically interpretable latent modes"; current KDR overlap (52%) is descriptive, not statistically significant | Compute precision@K for top-ranked pairs against gold-standard interaction databases (STRING, HIPPIE) across multiple query genes (not just KDR), report enrichment p-values | [Paper] [Paper: PDF p. 25, B.2.4] reports only descriptive overlap for KDR, states "without claiming statistically significant enrichment" |
| **Pretraining objectives may conflate cell identity and state** | LCCE uses cell-type labels, potentially forcing representations to collapse to type-level centroids, conflicting with PT state classification goal (same type, different states) | Risks undermining fine-grained state resolution; Figure A.5c shows balanced setting, but no ablation tests state-level discriminability under LCCE dominance | Ablate LCCE during pretraining, then evaluate PT state classification accuracy and UMAP separation of aPT/dPT/dPT/DTL clusters | [Paper] [Paper: PDF p. 25, B.3] visualizes UMAP under λ2=1 (LCCE dominant) showing "overemphasize cell-type identity", but does not quantify state separation |
| **Cross-type neighbor selection may be brittle** | Hierarchical clustering of cell types (818 types → 28 clusters) uses mean expression vectors; rare cell types or batch-specific biases could distort cosine similarity | May yield biologically implausible cross-type contexts (e.g., linking unrelated lineages), harming contrastive signal | Sample 10 random query cell types, manually inspect top-5 neighbors in Table A.31 for biological plausibility; compute average cluster purity using ontology hierarchies | [Paper] [Paper: PDF p. 26–27, C.1] describes clustering but provides no validation of cluster biological coherence beyond average cosine similarity (0.845 vs 0.581) |

## 14 学到的知识  
- **MSA式建模可迁移至单细胞**：Protein MSA的核心洞见——“跨样本一致性/变异性蕴含结构约束”——可成功映射为“跨细胞一致性/变异性蕴含状态特异基因依赖”，且无需修改计算原语（Outer-product Mean/PW-Avg）[Paper] [Paper: PDF p. 2, 5, A.1]。  
- **上下文结构化优于数量堆砌**：Figure 5证明context size >40后收益饱和，而Table 4显示“Only Same-batch Context”性能显著低于Full Model，说明**上下文的生物学多样性（cross-batch/cross-type）比单纯增加数量更重要**。  
- **关系发现与主干编码解耦是关键**：CellMSA-Module在低维d′空间处理S×G输入，GenePairformer在高维d空间仅处理单细胞G×d输入，这种分离设计使模型能以可控成本获得gene-pair级别的关系感知能力 [Paper] [Paper: PDF p. 16, A.2]。  
- **预训练目标需协同制衡**：LMGM/LRec/LCCE三者存在天然张力——LCCE推动类型聚类，LRec preserves cell uniqueness，LMGM ensures local fidelity；λ1=0.01, λ2=10的平衡点（Fig. A.5c）是经验性选择，非理论最优 [Paper] [Paper: PDF p. 25, B.3]。  
- **解释性需多尺度验证**：CellMSA的interpretability（Fig. 4）结合了head-level delta hub scores、GO富集、以及外部STRING验证（B.2.4），形成“计算信号→功能注释→外部数据库”三级证据链，为单细胞模型解释性树立了新范式。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：CellMSA的MSA-inspired design与作者团队前期工作Stofm（spatial transcriptomics foundation model）[Paper] [Paper: PDF p. 13, Ref 32]共享“多源上下文建模”思想，但Stofm处理空间邻域，CellMSA处理跨批次/跨类型细胞邻域，二者构成“多尺度上下文建模范式”的互补实例。  
- **候选连接/方法论连接**：CellMSA的GenePairformer中pair-as-attention-bias机制，与Uni-Mol [Paper] [Paper: PDF p. 13, Ref 30] 和多尺度蛋白语言模型 [Paper] [Paper: PDF p. 13, Ref 31] 的pair-aware设计同源，表明“pair representation注入Transformer”已成为跨模态（分子/细胞）关系建模的通用原语。  
- **候选连接/方法论连接**：上下文三元分组（same-batch/cross-batch/cross-type）与graph neural networks中neighbor sampling策略（e.g., Cluster-GCN, GraphSAINT）理念相通，均强调对邻居进行语义分层采样，但CellMSA不构建显式图，而是通过relation-type embedding隐式编码。  
- **弱连接/方法论连接**：perturbation prediction依赖STATE-ST模块，与用户研究方向“perturbation prediction”构成工具链连接（CellMSA提供表征，STATE-ST完成预测），但CellMSA自身未建模扰动动态过程。  
- **弱连接/方法论连接**：cross-type neighbor construction via hierarchical clustering of cell-type embeddings预示了与“cell state representation”研究的潜在接口——若将cell state（而非cell type）作为聚类单元，可自然延伸至状态空间建模。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Cross-State MSA for Dynamic Cell State Trajectories  
  **originating limitation/observation**: CellMSA’s cross-type context uses static cell-type ontology, but user’s focus is on *cell state* (e.g., perturbation-induced transitions); current design cannot model continuous state drift [Paper] [Paper: PDF p. 10, limitation on statistical vs causal].  
  **core hypothesis**: Replacing cross-type neighbors with *temporally adjacent states* (e.g., pre-/post-perturbation cells, healthy/injured PT) will enable explicit modeling of state transition dynamics, improving perturbation prediction beyond static representations.  
  **delta from paper**: Replace hierarchical clustering of cell types with trajectory-aligned clustering of cell states (e.g., using RNA velocity or pseudotime embeddings), and define cross-state context as cells at similar pseudotime positions across different trajectories.  
  **initial method**: On Replogle dataset, compute Monocle3 pseudotime for each perturbation trajectory; cluster cells by pseudotime bin + perturbation type; sample cross-state context from same-bin cells across different perturbations. Pretrain CellMSA with modified context and add a trajectory reconstruction objective.  
  **validation**: Perturbation prediction (Pearson Δ, DE Overlap) on held-out perturbations; UMAP visualization of state progression smoothness.  
  **failure modes**: Pseudotime estimation noise may corrupt context; limited to perturbations with clear temporal ordering.  
  **innovation status**: unverified  

- **name**: Spatial-MSA Fusion for Multi-Modal Alignment  
  **originating limitation/observation**: CellMSA operates solely on scRNA-seq; user’s interest in spatial transcriptomics requires cross-modal alignment, but paper offers no spatial interface [Paper] [Paper: PDF p. 31, broader impacts mentions "multi-omics" but no implementation].  
  **core hypothesis**: Integrating spatial coordinates as an additional relation-type embedding (e.g., "same-spot", "adjacent-spot", "distant-spot") into CellMSA’s context construction will enable joint learning of expression and spatial constraints, improving spatial domain prediction.  
  **delta from paper**: Extend relation-type embedding set from {same batch, cross batch, cross type} to include spatial relations; modify CellMSA-Module to accept coordinate-aware positional encoding.  
  **initial method**: On spatial datasets (e.g., STARmap mouse brain), treat each spot as a "cell" with spatial coordinates; construct context using k-NN in spatial coordinates; train with masked spot prediction + spatial proximity contrastive loss.  
  **validation**: Spot-level domain annotation accuracy; correlation between learned gene-pair representations and known spatial gene co-expression patterns (e.g., ligand-receptor pairs).  
  **failure modes**: Sparse spatial data may yield insufficient context; coordinate systems vary across platforms.  
  **innovation status**: unverified  

- **name**: Causal-Pair Refinement via Regulatory Prior Injection  
  **originating limitation/observation**: Authors explicitly state gene-pair representations reflect statistical associations, not causal regulation [Paper] [Paper: PDF p. 10], limiting biological utility for perturbation prediction.  
  **core hypothesis**: Injecting curated regulatory priors (e.g., TF-target from DoRothEA, kinase-substrate from KinaseNet) as hard constraints or soft biases into the Outer-product Mean module will steer gene-pair learning toward causally plausible relationships, improving DE gene prediction.  
  **delta from paper**: Modify Outer-product Mean’s weight matrix Wlp to be maskable by prior confidence scores; add a regularization term penalizing pair representations inconsistent with high-confidence priors.  
  **initial method**: Extract top 10K high-confidence TF-target pairs from DoRothEA; during CellMSA-Module training, apply binary mask to Wlp for non-prior pairs, and add L2 penalty on prior-violating entries.  
  **validation**: DE Overlap and PRAUC on perturbation tasks; GO enrichment of top-ranked pairs for regulatory process terms.  
  **failure modes**: Prior incompleteness may prune true novel interactions; over-regularization may harm generalization.  
  **innovation status**: unverified