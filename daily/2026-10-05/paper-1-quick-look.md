## CellMSA: Context Modeling for Single-Cell Representation Learning

**标题与发布时间**  
CellMSA: Context Modeling for Single-Cell Representation Learning（2026-09-30T03:55:27+00:00）

**作者和机构**  
Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
现有单细胞基础模型（如 Geneformer/scGPT）多独立编码单细胞，或仅建模同一批次内细胞，导致上下文信息贫乏、易混淆技术噪声与真实生物学变异。CellMSA 直接回应这一瓶颈，提出基因级对齐的跨批次/跨类型上下文建模新路径。

**核心假设或问题**  
若能像 AlphaFold 利用 MSA 聚合同源序列共进化信号一样，聚合相似细胞（跨批次、跨类型）的表达一致性与差异性，是否可稳定提取状态特异的基因共表达模式？关键在于设计可扩展、基因级对齐的上下文机制。

**方法逻辑**  
输入：目标细胞 + 40 个邻居（16 same-batch、16 cross-batch、8 cross-type），构成类 MSA 矩阵；核心方法：先用 Outer-product Mean 聚合跨细胞共变信号，再用 Pair-weighted Averaging 迭代精炼基因对表示；输出：上下文感知的基因对关系，作为 bias 注入目标细胞 Transformer 编码。

**主要结果**  
在 Tabula Sapiens（24 组织）上，CellMSA 总分 0.736，NMI 0.895，ARI 0.805，显著优于 scVI、scGPT、STATE 等；优势在 label-informed context 检索下最明显，label-free 下仍存在但缩小；GO 富集显示其捕捉到 CUBN、HAVCR1 等已知病理相关 marker 基因。

**真正贡献**  
首次将 MSA 的归纳偏置迁移至单细胞领域，实现基因级对齐、三类生物语义上下文（去噪/稳定性/功能对比）联合建模，并提供可导出、可解释的基因对表示。

**与你研究方向的关系**  
方法论直连 AlphaFold；与 spatial transcriptomics 模型（如 STAGATE）形式相似但上下文由生物语义（非空间距离）驱动；预训练任务（LMGM/LRec/LCCE）专为单细胞设计，不同于 multi-omics 多模态对齐。

**局限性**  
作者明确：结果为统计关联，非因果推断；性能依赖高质量 cell-type 注释；未验证 spatial transcriptomics、multi-omics 或稀有细胞类型；计算复杂度随细胞数增长较快。

**是否值得精读**  
值得精读：它在多个标准数据集上系统验证了 MSA 类比范式的有效性，并提供了可复现的基因对解释路径，且所有结论均有对应实验支撑。

**原文 PDF**：https://arxiv.org/pdf/2609.38908v1