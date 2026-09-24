## Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation

**标题与发布时间**  
Correlation-Guided Flow Matching with Annealed Masking for Spatial Transcriptomics Generation（2026-09-01T00:00:00+00:00）

**作者和机构**  
Yupei Zhang, Hao Chen, Li Pan, Chao Li, Xiaohan Xing

**发表状态**  
arXiv 预印本

**研究背景**  
该工作处于组织切片图像（H&E）生成空间转录组（ST）的演进转折点：从早期确定性回归，到生成式建模（如Stem、STFlow），但均默认各基因独立预测；本文首次将基因互作建模嵌入生成动力学核心，而非仅作为输入特征或后处理步骤。

**核心假设或问题**  
标准流匹配目标在数学上天然分解为每个基因独立优化，导致模型无需学习基因间协同；本文问题是如何重构训练信号与正则机制，使模型**必须**利用基因互作结构才能最小化损失。

**方法逻辑**  
输入是H&E图像和部分基因表达；核心方法分两步：先用时变掩码（masking ratio随时间线性增加）破坏基因维度一一对应，迫使模型基于未掩码基因联合推断被掩码基因；再叠加融合STRING与WGCNA的基因图正则，约束邻近基因预测一致、全局共表达模块平滑。输出是生物更合理的ST表达矩阵。

**主要结果**  
在HEST-1K的10个数据集上，CorrFlow比STFlow基线PCC提升0.013（0.613 vs 0.600），HPCC提升0.015（0.628 vs 0.613），均p<0.05；HPCC增益更大，说明对通路级生物学一致性有特异性增强。

**真正贡献**  
提出“annealed masking”打破基因独立优化陷阱，使联合建模成为必需；设计基因图双重正则（局部边一致性+全局模块平滑），将生物先验直接嵌入生成目标；二者协同提升数值准确性和生物学合理性。

**与你研究方向的关系**  
方法可迁移至单细胞基础模型（用scRNA图替代静态图）、空间转录组内插（以邻近spot为条件）、图神经网络设计（局部消息+全局谱滤波）等方向。

**局限性**  
作者承认：仅在内部数据集（HEST-1K、STImage-1K4M）验证，缺乏完全独立外部队列；STRING+WGCNA融合图未考虑疾病或细胞类型特异的动态互作；临床可用性仍不足。

**是否值得精读**  
值得精读——因其首次将基因互作从可选先验升级为生成过程不可绕过的约束，并通过严谨的消融与理论命题（Proposition 1–2）支撑该设计选择。

**原文 PDF**：https://arxiv.org/pdf/2609.22187