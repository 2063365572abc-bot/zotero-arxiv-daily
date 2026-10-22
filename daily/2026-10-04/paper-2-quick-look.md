## CellMSA: Context Modeling for Single-Cell Representation Learning

**标题与发布时间**  
CellMSA: Context Modeling for Single-Cell Representation Learning（2026-09-30T03:55:27+00:00）

**作者和机构**  
Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
单细胞基础模型分两条路：一是把每个细胞当独立token（如Geneformer/scGPT），但难区分生物信号和噪声；二是把同批多个细胞当“句子”建模（如CellPLM/STATE），却压缩基因维度、且上下文只限同一批次同一种类，缺乏跨条件稳定性。

**核心假设或问题**  
现有方法无法稳定提取跨批次一致、跨类型对比凸显的基因共表达模式。作者假设：借鉴AlphaFold中MSA的思想——聚合跨样本的共变与保守性——可帮助模型解耦出状态特异的基因依赖关系。

**方法逻辑**  
输入是目标细胞及其三类邻居（同批同型、跨批同型、跨类型）；核心方法是CellMSA-Module，通过交替计算“基因对共变”和“基因级反馈”，生成一个保持全基因分辨率的上下文感知基因对表示P；输出是注入P作为注意力偏置的细胞表征，使模型显式建模基因间依赖。

**主要结果**  
在Tabula Sapiens上，CellMSA总分0.736，NMI 0.895，ARI 0.805，BRAS 1.000，iLISI 0.242，kBET 0.627，均优于scVI/scGPT/Geneformer等；消融显示移除CellMSA-Module使PT损伤预测准确率从0.958骤降至0.854。

**真正贡献**  
提出MSA-like上下文构造范式，首次将same/cross-batch/type三类细胞联合建模；设计CellMSA-Module与GenePairformer，全程保留基因维度，并产出可解释的基因对中间表示P。

**与你研究方向的关系**  
其跨类型上下文思想可迁移到空间转录组邻域构建；tripartite检索机制启发多组学整合（如用scRNA-seq细胞检索匹配的scATAC-seq细胞）；attention bias机制类似prompt tuning。

**局限性**  
作者承认：P反映统计关联而非因果调控；依赖高质量细胞类型标签构建上下文；跨类型聚类可能混入技术批次效应，非纯生物学相似性。

**是否值得精读**  
值得精读：因方法有明确因果链条（消融+可视化+多任务泛化），且上下文设计对单细胞建模范式具启发性。

**原文 PDF**：https://arxiv.org/pdf/2609.38908v1