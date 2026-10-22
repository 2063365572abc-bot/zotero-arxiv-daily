## Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction

**标题与发布时间**  
Preserving DEG Rankings for Gene Discovery in Histology-Based Spatial Gene Expression Prediction（2026-09-27T21:15:02+00:00）

**作者和机构**  
Kaito Shiku, Kazuya Nishimura, Yasuhiro Kojima, Ryoma Bise

**发表状态**  
arXiv 预印本（cs.CV 类）

**研究背景**  
空间转录组（ST）成本高、通量低，而病理H&E图像广泛可得；因此从组织图像预测基因表达是扩展分子分析的关键路径。此前方法聚焦“每个基因在每个位置的表达值重建精度”，但未考虑下游关键任务——发现哪些基因最能区分不同组织区域或表型。

**核心假设或问题**  
现有模型优化目标与生物学发现逻辑脱节：最小化spot-wise预测误差，却未建模gene-wise的差异表达排序（DEG ranking）。能否设计一个无需真实生物学标注、可微分的训练目标，让模型仅看图像就学会识别“哪些基因最敏感响应形态学差异”？

**方法逻辑**  
输入是H&E图像块；用冻结的CONCH模型提取特征；通过MLP预测全基因表达向量。不直接拟合真实表达值，而是构建形态学代理对比组（如K-means聚类生成A/B组），计算每组间基因表达差异强度的可微U统计量，并对齐其基因排序与真实DEG排序的相关性。

**主要结果**  
在HEST-1K和Her2st数据集上，该方法在nDCGDEG@200、SCCDEG和通路Jaccard重叠率上均优于基线；明确显示为提升排序质量，主动牺牲了单基因预测精度（PCC下降），属有意设计。

**真正贡献**  
首次形式化“图像驱动的差异表达排序预测”（IDER）任务；提出无监督代理对比+可微U统计对齐的端到端框架；验证排序保真度可提升下游通路富集的生物学相关性。

**与你研究方向的关系**  
为图像到空间转录组预测提供新评估范式；其代理对比思想可迁移至单细胞基础模型；U统计流程可自然嵌入空间图神经网络；与SPARK-X等空间DEG工具存在方法论呼应。

**局限性**  
性能依赖CONCH特征质量；未评估极稀疏细胞类型（<10 spots/患者）；作者未分析U统计是否隐含空间平滑效应，可能混淆排序提升与空间一致性提升。

**是否值得精读**  
值得精读——它重新定义了histology-to-ST预测的目标：从信号保真转向生物学效用保真，并给出首个可微、无监督、排序导向的实现。

**原文 PDF**：https://arxiv.org/pdf/2609.33928v1