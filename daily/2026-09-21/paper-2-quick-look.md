## OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning

**标题与发布时间**  
OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning（2026-08-24T04:15:39+00:00）

**作者和机构**  
Rabeya Tus Sadia, Qiang Ye, Qiang Cheng

**发表状态**  
arXiv 预印本（v2）

**研究背景**  
空间多组学已从单模态RNA发展为RNA+ADT+H&E融合分析，GROVER等方法用图神经网络建模空间邻近性，SpatialGlue等探索跨模态对齐。但所有现有方法只输出聚类结果，未同步建模可靠性或生成可验证解释。

**核心假设或问题**  
如何在完成空间域聚类的同时，为每个斑点回答：（1）该分配是否可靠？（2）是RNA、ADT还是图像主导决策？（3）为什么应信任它？目标是构建可验证、可归因、可信赖的端到端框架。

**方法逻辑**  
输入斑点的多模态数据与空间坐标；用KAN-GCN和CrossModalTransformer提取特征；UncertaintyMoE同步输出聚类置信度*cᵢ*、不确定性*uᵢ*和模态路由均值*ḡᵢ*；将这些信号结构化为证据字典，驱动Llama-3.3-70B生成五类解释；OmicSync-R进一步用解释质量（GR/CA/SC）作为奖励，通过REINFORCE微调聚类分布。

**主要结果**  
在Tonsil、Glioblastoma等4个数据集上平均排名最优（1.22–1.78），ARI全部第一；解释质量指标GR/CA/SC可量化验证；OmicSync-R带来+0.99 ARI提升，但需220次LLM调用。

**真正贡献**  
首次将空间多组学聚类、可靠性量化、证据结构化、LLM约束推理、推理-聚类闭环整合为统一可审计框架；解释不是后处理，而是参与优化的内在模型属性。

**与你研究方向的关系**  
KAN-GCN继承自GROVER，与图神经网络方法高度契合；UncertaintyMoE与不确定性感知GNN同源；REINFORCE闭环可迁用于扰动预测；五策略推理模板适配细胞状态“What-if”分析。

**局限性**  
基础版Task C解释不反向优化聚类；OmicSync-R计算开销大；GR指标仅计字符串匹配，未覆盖同义词或功能等价；*ḡᵢ*是模态主导性的代理指标，非因果归因。

**是否值得精读**  
值得精读——它提出首个将可靠性审计与LLM推理嵌入聚类主干的完整闭环设计，且所有模块均有明确输入输出与实证支撑。

**原文 PDF**：https://arxiv.org/pdf/2608.22785v2