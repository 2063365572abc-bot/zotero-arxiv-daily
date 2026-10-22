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
| Title | CellMSA: Context Modeling for Single-Cell Representation Learning | [Paper] [Paper: PDF p. 1] |
| Venue | arXiv preprint (NeurIPS 2026 submission) | [Paper] [Paper: PDF p. 1] |
| Authors | Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie | [Paper] [Paper: PDF p. 1] |
| Pretraining scale | ~109 million human cell observations (65.6M primary) | [Paper] [Paper: PDF p. 1, 3, 6, 26] |
| Core architecture | MSA-inspired context modeling → CellMSA-Module → GenePairformer | [Paper] [Paper: PDF p. 4–5, Fig. 2] |
| Key datasets | Tabula Sapiens (24 tissues), Kidney Atlas (PT states), Replogle (perturbations) | [Paper] [Paper: PDF p. 7–9, 28] |
| Evaluation metrics | NMI/ARI/ASW/cLISI (bio), BRAS/iLISI/kBET/Conn/PCR (batch), Pearson ∆/PRAUC (perturbation) | [Paper] [Paper: PDF p. 7, 9, 30–31] |
| Code availability | https://github.com/PharMolix/CellMSA | [Paper] [Paper: PDF p. 1] |

## 02 一句话总结  
CellMSA 提出一种受蛋白质多序列比对（MSA）启发的单细胞上下文建模范式，通过跨批次、跨细胞类型的“细胞级MSA”构建基因对（gene-pair）表示，显式建模细胞状态依赖的基因共表达与调控依赖关系；该设计显著提升单细胞表征在批效应校正、细粒度细胞状态分类与扰动响应预测上的鲁棒性与生物学可解释性，且其基因对表示可直接映射至疾病相关通路（如肾小管损伤中的ECM重塑），为cell state representation提供新范式。其核心价值在于将传统独立细胞编码范式升级为“目标细胞+结构化上下文”的pair-aware建模，而非仅扩大模型容量或数据规模。

## 03 研究问题  
现有单细胞基础模型（如Geneformer、scGPT）普遍采用单细胞独立编码或同批多细胞压缩建模，导致两个根本缺陷：（1）无法区分技术噪声与真实生物学变异（因单细胞表达高度稀疏且受测序深度/批次影响）[Paper] [Paper: PDF p. 2]；（2）丢失基因层面细粒度依赖关系（因压缩策略如基因加权平均会抹除基因对特异性）[Paper] [Paper: PDF p. 2]。由此引发的核心问题是：**如何在不牺牲基因分辨率的前提下，系统性利用跨批次、跨细胞类型的细胞间一致性与变异性，学习细胞状态特异的基因-基因依赖关系？** 作者假设：类比AlphaFold中MSA用于提取残基共进化信号，单细胞场景下“细胞MSA”可聚合相似细胞的表达模式，从而识别marker基因与状态特异的基因共表达模块。

## 04 研究背景与发展路径  
单细胞基础模型演进呈现两条主线：（1）**独立建模路线**（Geneformer/scGPT）：将细胞视为独立token，依赖大规模预训练学习通用表征，但受限于单细胞稀疏性与噪声敏感性；（2）**局部上下文路线**（CellPLM/STATE/Stack）：引入同批细胞作为上下文，但存在两大瓶颈——CellPLM用“组织作为句子”导致基因分辨率丢失 [Paper] [Paper: PDF p. 3]，STATE与Stack虽支持跨条件建模，但Stack采用基因模块块压缩 [Paper] [Paper: PDF p. 3]，STATE未显式建模基因对关系 [Paper] [Paper: PDF p. 8]。CellMSA的突破在于将蛋白质MSA的归纳偏置迁移至单细胞领域：不追求更大模型或更多数据，而是重构输入结构——将目标细胞与三类生物学意义明确的上下文细胞（同批、跨批同型、跨型相关）组织成MSA-like矩阵，使模型能像AlphaFold解析残基对一样解析基因对 [Paper] [Paper: PDF p. 2–4, Fig. 1]。

## 05 论文识别的核心痛点

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|------------|---------------|------------------------------|--------------------------|
| **单细胞独立编码的噪声脆弱性** | 模型难以区分生物学变异与技术噪声（如dropout、批次效应），导致细粒度基因依赖建模失败 | 单细胞转录组高度稀疏，且表达值强依赖测序深度与实验条件 [Paper] [Paper: PDF p. 2] | 引言段明确指出：“when the model relies on only a single observation of a cell, it is often difficult to distinguish biological variation from stochastic noise” [Paper] [Paper: PDF p. 2] |
| **现有上下文方法的基因分辨率损失** | 压缩策略（如基因加权平均、细胞编码器、基因模块）丢弃基因级信息，限制细粒度基因-基因依赖捕获 | 多细胞联合建模需降低计算开销，现有方法选择牺牲基因粒度换取效率 [Paper] [Paper: PDF p. 2] | 方法部分强调：“such compression can discard gene-level information and therefore limit the model’s ability to capture fine-grained gene-gene dependencies” [Paper] [Paper: PDF p. 2] |
| **上下文生物学信息贫乏** | 同批同型细胞上下文仅反映局部实验条件，缺乏跨批次稳定性信号与跨细胞类型对比信号 | 现有方法未显式利用跨批次细胞（稳定生物信号）与生物相关细胞类型（功能对比信号） [Paper] [Paper: PDF p. 2] | Figure 1对比图显示：蛋白MSA含conserved residues与co-evolution，而单细胞对应物需包含marker genes与gene co-expression；正文指出：“they do not explicitly exploit cross-batch signals or biologically related cell types” [Paper] [Paper: PDF p. 2] |

## 06 核心思想  
CellMSA的核心思想是**将单细胞表征学习重构为“上下文驱动的基因对关系建模”问题**：不直接优化细胞嵌入，而是先从结构化上下文中提炼基因对表示（gene-pair representation），再将其作为注意力偏置注入目标细胞编码器。这一设计实现三重解耦：（1）**上下文解耦**——三类上下文（same-batch/cross-batch/cross-type）分别承载去噪、跨批次鲁棒性、功能对比信号；（2）**粒度解耦**——CellMSA-Module在低维空间（d′ < d）高效聚合跨细胞统计，避免高维Transformer全量计算；（3）**任务解耦**——基因对表示专精于建模依赖关系，目标细胞编码器专精于整合该关系生成最终表征。本质是用“关系先验”替代“独立表征”，使模型具备类似生物学家的推理能力：通过比较相似细胞来推断基因功能关联。

## 07 方法总览  
CellMSA采用三级流水线：（1）**MSA-like上下文构建**：对每个目标细胞ci，检索Ni = N<sup>same batch</sup><sub>i</sub> ∪ N<sup>cross batch</sup><sub>i</sub> ∪ N<sup>cross type</sup><sub>i</sub> 共40个细胞（16+16+8），并为每类邻居添加relation-type embedding [Paper] [Paper: PDF p. 4]；（2）**CellMSA-Module**：在低维空间对上下文进行迭代更新——Outer-product Mean模块聚合基因对跨细胞协变，Pair-weighted Averaging模块用更新后的基因对表示调制上下文基因表示 [Paper] [Paper: PDF p. 5, App. A.1]；（3）**GenePairformer**：将最终基因对表示PL<sup>MSA</sup>投影为注意力偏置，注入标准Transformer的目标细胞编码器，使自注意力显式感知基因对依赖 [Paper] [Paper: PDF p. 5]。预训练采用三目标联合优化：LMGM（掩码基因预测）、LRec（细胞表达重建）、LCCE（细胞对比学习）[Paper] [Paper: PDF p. 6]。

## 08 核心模块拆解

| Module | Function | Why needed | Input and output | Supporting evidence | Known or expected effect of removal |
|--------|----------|------------|------------------|----------------------|-----------------------------------|
| **CellMSA-Module** | 从MSA-like上下文提取context-dependent gene-pair representation PL<sup>MSA</sup> | 解决独立编码无法建模基因对依赖的问题；低维设计（d′）保障计算可行性 | Input: 上下文细胞基因嵌入ms<sub>g</sub> ∈ ℝ<sup>d</sup>；Output: PL<sup>MSA</sup> ∈ ℝ<sup>G×G×d<sub>p</sub></sup> | Fig. 2箭头标注“summarizes cross-cell patterns into context-dependent gene-pair representation”；Table 4 ablation显示移除后PT分类准确率下降10.4%（0.958→0.854） [Paper] [Paper: PDF p. 4, 10] | GenePairformer退化为标准Transformer，丧失基因对建模能力，导致所有下游任务性能显著下降（Table 4） |
| **GenePairformer** | 将PL<sup>MSA</sup>作为attention bias注入目标细胞编码，生成最终细胞嵌入zi | 实现基因对关系到细胞表征的端到端传递；避免关系建模与表征生成耦合 | Input: 目标细胞嵌入e<sub>1g</sub>，PL<sup>MSA</sup>；Output: zi ∈ ℝ<sup>d</sup> | Fig. 2明确标注“incorporated into the encoding of the target cell as an attention bias”；公式RL+1,H<sub>uv</sub> = RL,H<sub>uv</sub> + QL,H<sub>u</sub>(KL,H<sub>v</sub>)<sup>⊤</sup>/√d<sub>H</sub>定义bias注入机制 [Paper] [Paper: PDF p. 4–5] | 若仅保留CellMSA-Module输出PL<sup>MSA</sup>而不注入编码器，则无法生成细胞嵌入，整个框架失效 |
| **Three-objective pretraining** | LMGM（局部重建）、LRec（全局保真）、LCCE（生物判别）协同优化 | 单一目标无法兼顾：LMGM易过拟合噪声，LRec易坍缩至细胞类型均值，LCCE易忽略状态内变异 | Input: 掩码基因位置Ω、重建基因子集Γ、对比正负样本；Output: 联合损失L = LMGM + λ<sub>1</sub>LRec + λ<sub>2</sub>LCCE | Appendix B.3图A.5显示：λ<sub>1</sub>=0时UMAP中PT三种状态混叠（过强调细胞类型），λ<sub>2</sub>=0时状态分离但噪声大（过强调个体差异） [Paper] [Paper: PDF p. 25–26] | 移除任一目标均导致性能下降：Table A.32显示λ<sub>1</sub>=0.01/λ<sub>2</sub>=10为经验最优平衡点 |

## 09 关键公式与符号  
论文未给出可核验的完整公式体系，但明确定义以下关键符号与操作：  
- **MSA-like context**: Ni = N<sup>same batch</sup><sub>i</sub> ∪ N<sup>cross batch</sup><sub>i</sub> ∪ N<sup>cross type</sup><sub>i</sub> [Paper] [Paper: PDF p. 4]  
- **Outer-product Mean update**: p<sup>l+1</sup><sub>uv</sub> = p<sup>l</sup><sub>uv</sub> + W<sup>l</sup><sub>p</sub> (1/S Σ<sub>s=1</sub><sup>S</sup> a<sup>l</sup><sub>su</sub> ⊗ b<sup>l</sup><sub>sv</sub>)，其中a,b为线性投影，⊗为外积 [Paper] [Paper: PDF p. 5, App. A.1]  
- **Pair-weighted Averaging update**: m<sup>l+1</sup><sub>su</sub> = m<sup>l</sup><sub>su</sub> + W<sup>l</sup><sub>o</sub> (γ<sup>l,h</sup><sub>su</sub> ⊙ Σ<sub>v</sub> softmax<sub>v</sub>(W<sup>l,h</sup><sub>b</sub> p<sup>l+1</sup><sub>uv</sub>) v<sup>l,h</sup><sub>sv</sub>) [Paper] [Paper: PDF p. 5]  
- **GenePairformer attention bias**: RL+1,H<sub>uv</sub> = RL,H<sub>uv</sub> + QL,H<sub>u</sub>(KL,H<sub>v</sub>)<sup>⊤</sup>/√d<sub>H</sub> [Paper] [Paper: PDF p. 5]  
- **Pretraining loss**: L = LMGM + λ<sub>1</sub>LRec + λ<sub>2</sub>LCCE，其中LMGM为掩码基因交叉熵，LRec为重建交叉熵，LCCE为InfoNCE对比损失 [Paper] [Paper: PDF p. 6]  
- **Key metrics**: Pearson ∆（扰动效果一致性）、NMI/ARI（生物保守性）、BRAS/iLISI/kBET（批效应校正）[Paper] [Paper: PDF p. 7, 9, 30–31]

## 10 实验设计与证据链

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|------------|--------------|----------------------------|--------|------------------------|------------------------------|--------|
| **Batch integration (Tabula Sapiens)** | CellMSA的上下文建模提升批效应校正与生物结构保留能力 | CellMSA vs. PC-HVG/scVI/scGPT/Geneformer/STATE-SE/Stack；label-informed context retrieval | CellMSA总分0.736，显著高于Stack（0.663）与次优基线（0.600）；NMI 0.895，ARI 0.805，BRAS 0.740，kBET 0.242 [Paper] [Paper: PDF p. 7, Table 1] | CellMSA在严格保持生物结构前提下实现最优批混合，验证MSA上下文对跨批次鲁棒性的贡献 | 不能推断CellMSA在所有数据集上均绝对最优（如Bladder label-free setting中CellMSA 0.688 vs Stack 0.600） | [Paper] [Paper: PDF p. 7, Table 1; App. B.1.1 Table A.27] |
| **PT cell state classification (Kidney Atlas)** | 细胞上下文增强细粒度疾病状态区分能力 | CellMSA vs. scVI/scGPT/Geneformer/STATE-SE/Stack/CellPLM；5-run平均 | CellMSA宏F1 0.931±0.006，显著优于CellPLM（0.794±0.012）与Stack（0.909±0.009） [Paper] [Paper: PDF p. 8, Table 2] | CellMSA能分辨同一细胞类型（PT）内的三级疾病状态（aPT/dPT/dPT/DTL），证明上下文建模捕获病理细微差异 | 不能声称CellMSA泛化至所有疾病状态（仅验证PT，未测试其他肾细胞类型） | [Paper] [Paper: PDF p. 8, Table 2] |
| **Perturbation prediction (Replogle)** | 基因对表示提升扰动响应预测 fidelity | CellMSA+STATE-ST vs. Expression+STATE-ST/STATE-SE+STATE-ST/Stack+STATE-ST | CellMSA Pearson ∆ 0.433，较最强基线STATE-SE（0.353）提升8.8%；DE Overlap 0.215，显著高于STATE-SE（0.180） [Paper] [Paper: PDF p. 9, Table 3] | CellMSA的latent space更鲁棒地建模扰动诱导的转录变化，支持其基因对表示蕴含调控逻辑 | 不能断言CellMSA直接学习因果调控（作者明确限定为统计关联） | [Paper] [Paper: PDF p. 9, Table 3] |
| **Ablation study (Table 4)** | 性能增益源于MSA上下文的有效利用 | w/o CellMSA-Module / w/o Context / Only Same-batch Context vs. Full Model | Full Model在PT分类（0.958）与扰动预测（0.433）上全面领先；仅同批上下文时Pearson ∆降至0.400 | 三类上下文（跨批、跨型）共同贡献性能，非单一组件主导 | 不能归因于某单一超参数（如context size=40为饱和点，Fig. 5） | [Paper] [Paper: PDF p. 10, Table 4; Fig. 5] |

## 11 对结论的正确理解  
CellMSA的结论必须置于其**方法论边界**内理解：（1）其优势建立在“label-informed context retrieval”基础上（Table 1脚注），当标签不可用时（App. B.1.1），CellMSA仍优于Stack但绝对分数下降（0.748→0.688），说明上下文质量高度依赖生物学注释；（2）基因对表示（Fig. 4）揭示的是**统计关联模式**（“statistical associations rather than explicit causal regulatory relationships” [Paper] [Paper: PDF p. 10]），GO富集分析（Fig. 4c）验证其生物学锚定性，但不等价于因果推断；（3）性能提升具有**任务特异性**：在batch integration（+13.6%总分）、PT状态分类（+2.8%宏F1）、perturbation预测（+8.8% Pearson ∆）中显著，但在CellPLM擅长的cell type annotation中仅微弱领先（0.912 vs 0.906宏F1），表明其核心价值在细粒度状态建模而非粗粒度分类。

## 12 作者明确承认的限制

| Limitation | Specific manifestation | Future direction proposed by authors | Source |
|------------|-------------------------|--------------------------------------|--------|
| **统计关联非因果关系** | 学习的基因对模式反映统计共现，而非直接因果调控；可能混淆相关性与因果性 | “incorporate prior knowledge of gene regulation and causal machine learning methods”以增强生物学 grounding | [Paper] [Paper: PDF p. 10] |
| **依赖高质量细胞类型注释** | label-informed context retrieval需可靠cell-type labels；在注释缺失或噪声大时性能下降 | 未提出具体方案，但label-free实验（App. B.1.1）暗示需开发无监督上下文检索机制 | [Paper] [Paper: PDF p. 7, App. B.1.1] |
| **计算复杂度随context size增长** | CellMSA-Module时间复杂度O(SG²d²<sub>p</sub>)，S为上下文大小；Fig. 5显示>40 cells后收益饱和 | 未明确提及，但Fig. 5隐含优化context size以平衡效率与性能 | [Paper] [Paper: PDF p. 10, Fig. 5; App. A.2] |

## 13 批判性分析

| [Analysis] Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|------------------------|-------------------------------------------|----------------|----------------|-------|
| CellMSA在PT状态分类中表现优异（Table 2），但CellPLM在此任务上大幅落后（0.794 vs 0.931宏F1），而CellPLM在cell type annotation中反超（0.906 vs 0.912） | CellPLM可能过度适配粗粒度细胞类型信号，导致细粒度状态区分能力不足；CellMSA的跨型上下文（N<sup>cross type</sup><sub>i</sub>）可能意外引入PT相关细胞（如近端小管祖细胞）增强状态判别 | 若CellMSA优势源于特定上下文选择而非架构，则其泛化性存疑；需验证上下文构成对性能的贡献权重 | 在Kidney Atlas中消融N<sup>cross type</sup><sub>i</sub>（仅保留same/cross batch），观察PT分类性能变化；或替换N<sup>cross type</sup><sub>i</sub>为无关细胞类型（如神经元）测试性能衰减 | [Paper] [Paper: PDF p. 4, 8; Table 2] |
| Figure 4c的GO富集显示ECM重组等通路，但STRING验证仅52% KDR互作基因重叠（App. B.2.4） | CellMSA学习的基因对可能包含大量假阳性关联，尤其在低表达基因或稀疏区域；52%重叠率提示半数关联缺乏外部数据库支持 | 过度解读可解释性结果可能导致生物学误判；需区分“模型可解释”与“生物学确证” | 对Figure 4b中head 7高连接基因进行CRISPR筛选，验证其在肾损伤中的功能必要性；或使用SCENIC推断调控网络进行交叉验证 | [Paper] [Paper: PDF p. 9, App. B.2.4] |
| 预训练数据含65.6M primary observations，但109M总数中包含大量非primary数据（App. C.1） | 非primary数据（如atlas整合）可能引入批次间系统性偏差，使模型学到整合伪影而非生物学信号 | 若模型鲁棒性源于对整合噪声的适应，其在原始数据上的泛化能力可能被高估 | 在纯primary数据子集上重新预训练CellMSA，比较其在Tabula Sapiens上的batch integration性能 | [Paper] [Paper: PDF p. 6, 26, App. C.1] |

## 14 学到的知识  
- **MSA范式的单细胞迁移关键在结构化上下文设计**：非简单复制AlphaFold架构，而是将“同源序列”映射为“生物学相关细胞集合”，并赋予三类上下文明确语义（same-batch去噪、cross-batch鲁棒、cross-type对比）；  
- **基因对表示（gene-pair representation）是解耦建模的有效载体**：CellMSA-Module在低维空间（d′）处理上下文，GenePairformer在高维空间（d）编码目标细胞，实现计算效率与建模精度的平衡；  
- **预训练目标需协同设计**：LMGM保证局部重建，LRec防止表征坍缩，LCCE注入生物学判别信号，三者权重（λ₁=0.01, λ₂=10）需经验调优（Fig. A.5）；  
- **可解释性需多层次验证**：Figure 4结合差分hub score（a）、基因对热图（b）、GO富集（c）与STRING外部验证（App. B.2.4），构成从计算信号到生物学机制的证据链；  
- **上下文规模存在收益饱和点**：Fig. 5证实context size >40 cells后性能不再提升，提示实际部署中可压缩计算开销。

## 15 与既有知识的连接  
- **候选连接/方法论连接**：CellMSA的“目标细胞+上下文”范式与graph neural networks（GNNs）中中心节点+邻居聚合思想相通，但CellMSA显式建模基因对而非节点对，且上下文非图结构而是MSA-like矩阵；  
- **候选连接/方法论连接**：其跨模态对齐思路（Figure 1蛋白MSA↔单细胞MSA）可延伸至spatial transcriptomics，例如将空间邻域像素/spot作为上下文，学习空间-基因对关系；  
- **候选连接/方法论连接**：CellMSA-Module的Outer-product Mean与Pair-weighted Averaging模块（App. A.1）为multi-omics融合提供新接口——可将不同组学数据（ATAC、methylation）作为额外上下文行输入；  
- **弱连接/方法论连接**：perturbation prediction中将perturbation-defined states视为“cross-type”（App. C.3），此思路可迁移至biomedical AI的疾病亚型建模，但需解决临床标签稀疏性问题；  
- **弱连接/方法论连接**：其cell state representation聚焦于基因共表达模式，与用户研究方向中“cell state representation”强契合，但未涉及动态轨迹建模（如RNA velocity）。

## 16 研究想法  

[Hypothesis] 以下研究想法为基于论文证据和局限的可检验假设，不代表论文作者已验证。

- **name**: Cross-modal CellMSA for spatial-transcriptomic alignment  
  **originating limitation/observation**: CellMSA当前仅处理scRNA-seq，未整合空间位置信息（作者未提spatial data）；Figure 1类比暗示MSA范式可扩展至多模态。  
  **core hypothesis**: 将空间邻域spot作为额外上下文行，与scRNA细胞共同构成MSA-like输入，使CellMSA-Module学习空间-基因共表达模式。  
  **delta from paper**: 输入矩阵扩展为[X<sub>scRNA</sub>; X<sub>spatial</sub>]，新增spatial relation embedding，并修改Outer-product Mean以处理异构模态。  
  **initial method**: 在Slide-seqV2数据上预训练，spot表达经log-normalization后与scRNA共享基因vocab；上下文构建包含同区域spot、跨区域同型spot、跨区域相关spot。  
  **validation**: 使用spatial reconstruction loss（预测spot表达）与alignment accuracy（spot-scRNA匹配F1）。  
  **failure modes**: 空间分辨率不匹配导致上下文噪声；模态间批次效应放大。  
  **innovation status**: unverified  

- **name**: Causal CellMSA with regulatory prior injection  
  **originating limitation/observation**: 作者明确承认“statistical associations rather than explicit causal regulatory relationships” [Paper] [Paper: PDF p. 10]。  
  **core hypothesis**: 将已知TF-target网络（如DoRothEA）作为硬约束注入CellMSA-Module，引导基因对表示学习因果方向性。  
  **delta from paper**: 在Outer-product Mean更新中，对p<sup>l+1</sup><sub>uv</sub>施加TF→target mask（若u为TF、v为target则保留，否则置零），并添加causal consistency loss。  
  **initial method**: 在CellMSA预训练中联合优化LMGM与causal loss（如minimize KL divergence between learned p<sub>uv</sub>与prior p<sub>uv</sub><sup>causal</sup>）。  
  **validation**: 使用perturbation数据（Replogle）评估TF knockdown后target预测准确性（vs. baseline）。  
  **failure modes**: prior网络覆盖不全导致信息丢失；TF-target关系存在细胞类型特异性。  
  **innovation status**: unverified  

- **name**: Self-supervised context retrieval for label-free CellMSA  
  **originating limitation/observation**: Label-free实验（App. B.1.1）中CellMSA仍优于Stack，但性能下降（0.748→0.688），暴露对注释依赖。  
  **core hypothesis**: 用CellMSA自身学习的基因对表示指导无监督上下文检索，形成闭环优化。  
  **delta from paper**: 移除人工定义的N<sup>cross type</sup><sub>i</sub>，改为：对目标细胞ci，计算其PL<sup>MSA</sup>与所有其他细胞cj的PL<sup>MSA</sup><sub>j</sub>的Frobenius距离，取最近K个作为上下文。  
  **initial method**: 预训练分两阶段——Stage 1用label-informed context训练初始CellMSA；Stage 2冻结CellMSA-Module，仅微调context retrieval policy。  
  **validation**: 在Bladder label-free setting中比较context quality（如NMI of retrieved context vs. ground-truth type）。  
  **failure modes**: 初始模型偏差导致检索循环强化错误；距离度量对噪声敏感。  
  **innovation status**: unverified