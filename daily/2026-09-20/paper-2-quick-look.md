## OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning

**标题与发布时间**  
OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning（2026-08-24T04:15:39+00:00）

**作者和机构**  
Rabeya Tus Sadia, Qiang Ye, Qiang Cheng

**发表状态**  
arXiv 预印本

**研究背景**  
现有空间多组学聚类方法能划分组织域，但不提供“划分是否可信”的内生评估；可解释AI在该领域缺位，LLM此前未与空间聚类模型耦合；不确定性建模与强化学习的组合尚未用于可靠性驱动的聚类优化。

**核心假设或问题**  
如何在不降低聚类性能前提下，同步生成可计算、可分解、可审计的spot级可靠性信号，并用结构化证据约束LLM生成自然语言解释，实现“解释驱动优化”？

**方法逻辑**  
输入：RNA/ADT/H&E多模态空间数据及坐标；核心方法：先用KAN-GCN+不确定性感知MoE提取三个可靠性信号（聚类置信度、路由不确定性、模态权重），再构建证据字典驱动Llama-3.3-70B生成五类策略性解释，最后用GR/CA/SC指标作为REINFORCE奖励反向优化聚类头；输出：带spot级可靠性评分的聚类结果 + 可追溯的自然语言理由。

**主要结果**  
在四个CytAssist FFPE数据集上平均聚类排名最优（Tonsil 1.44，Glioblastoma 1.78）；OmicSync-R在k=10时ARI提升+0.99，但k=6–9时ARI骤降至23.68–27.77；NMI下降，提示改进偏向匹配伪标签而非提升内在纯度。

**真正贡献**  
首次将不确定性感知MoE路由、REINFORCE引导的潜在空间优化、证据约束的LLM推理三者闭环整合；把LLM降级为外部裁判，仅用其输出质量生成可微策略梯度，规避幻觉与不可微瓶颈。

**与你研究方向的关系**  
UncertaintyMoE与scVI等单细胞贝叶斯模型共享不确定性估计原理，但聚焦模态路由；SpatialPositionEncoder实现模态特异性位置调制；CrossModalTransformer采用spot内token互注意，强化模态协同建模。

**局限性**  
作者承认Task C原为后验解释，不参与聚类优化；REINFORCE奖励仅基于GR/CA/SC三项指标，对聚类数k高度敏感；Card未提供计算开销、泛化到非FFPE数据或非H&E模态的表现。

**是否值得精读**  
值得精读。它系统提出“可靠性即信号”的操作定义，并给出可复现的证据构造—LLM调用—策略更新闭环，且所有结论均附带明确条件限制。

**原文 PDF**：https://arxiv.org/pdf/2608.22785v2