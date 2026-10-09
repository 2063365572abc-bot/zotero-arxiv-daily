## CellMSA: Context Modeling for Single-Cell Representation Learning

**标题与发布时间**  
CellMSA: Context Modeling for Single-Cell Representation Learning（2026-09-30T03:55:27+00:00）

**作者和机构**  
Suyuan Zhao, Minghao Liu, Yizhen Luo, Zaiqing Nie

**发表状态**  
arXiv 预印本（NeurIPS 2026 投稿）

**研究背景**  
现有单细胞基础模型分两条路：一是把每个细胞当独立序列（如Geneformer、scGPT），难区分生物信号与技术噪声；二是只在同一批次内联合建模（如Stack、STATE），但会压缩基因细节，且无法跨批次/跨细胞类型泛化。CellMSA走第三条路：用类似蛋白质多序列比对（MSA）的方式，跨条件建模基因关系。

**核心假设或问题**  
单细胞中，多个相似细胞（同批、跨批、跨类型）的表达模式聚合后，能像蛋白质MSA识别共进化对一样，发现marker基因和细胞状态特异的基因依赖关系——而非仅靠单细胞独立编码或局部平均。

**方法逻辑**  
输入是1个目标细胞+40个上下文细胞（16同批+16跨批+8跨类型）构成的“伪MSA”矩阵；先在低维空间用迭代计算提炼基因对关系（捕捉跨细胞共变与差异），再将该关系作为注意力偏置，引导目标细胞的Transformer编码。不建图、不压缩基因维度，关系发现与主干编码解耦。

**主要结果**  
在Tabula Sapiens上，CellMSA总分0.736，高于Stack（0.663）和scVI（0.600）；NMI达0.895，iLISI为0.242，kBET为0.627。所有SOTA结果均基于标签辅助构建上下文；无标签版本性能明显下降。

**真正贡献**  
提出“跨条件、基因级、MSA式上下文建模”新范式；首次将Outer-product Mean与Pair-weighted Averaging引入单细胞，实现关系发现与表征编码分离；用relation-type embedding显式区分技术相似与功能相关信号。

**与你研究方向的关系**  
与空间转录组模型Stofm共享“多源上下文建模”思想，但Stofm处理空间邻域，CellMSA处理跨批次/跨类型细胞邻域；其pair-as-attention-bias机制与Uni-Mol等分子模型同源；上下文三元分组思路类似图神经网络的语义邻居采样。

**局限性**  
作者明确：基因对表示反映统计关联，非因果调控；性能依赖细胞类型标签构建上下文；预训练109M样本含重复观测，未验证规模扩展规律；same-batch上下文可能放大技术噪声。

**是否值得精读**  
值得精读——它系统重构了单细胞上下文定义，提供了可验证的关系建模新路径，且实验覆盖batch整合、cell-type注释、perturbation预测三大任务，但需注意结论的标签依赖前提。

**原文 PDF**：https://arxiv.org/pdf/2609.38908v1