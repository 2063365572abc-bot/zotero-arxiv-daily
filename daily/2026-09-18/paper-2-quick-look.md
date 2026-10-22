## OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning

**标题与发布时间**  
OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning（2026-08-24T04:15:39+00:00）

**作者和机构**  
Rabeya Tus Sadia, Qiang Ye, Qiang Cheng

**发表状态**  
arXiv 预印本

**研究背景**  
空间多组学聚类已从单模态发展到多模态融合（如GROVER、SpatialGlue），但所有方法都只输出聚类结果，缺乏spot级可审计解释。现有解释工具（如SHAP、注意力图）无法回答“为何信任该spot的分配”这一临床关键问题。

**核心假设或问题**  
现有聚类结果不可靠，因无法判断：哪些spot分配可信？哪个模态主导决策？依据是什么？作者认为可靠性必须基于模型自身产生的spot级信号（置信度、不确定性、模态权重），而非全局指标或原始输入。

**方法逻辑**  
输入是RNA、ADT、组织图像三模态数据；核心方法先用KAN-GCN+空间位置编码提取特征，再经跨模态Transformer融合，通过UncertaintyMoE生成模态权重与不确定性信号，最后用ClusteringHead输出软聚类，并将这些信号构建成结构化证据字典，约束LLM生成自然语言报告；OmicSync-R进一步用报告忠实度（GR/CA/SC）作为REINFORCE奖励优化聚类头。

**主要结果**  
在4个CytAssist FFPE数据集上，OmicSync平均排名最优（Tonsil 1.44，Glioblastoma 1.78）；OmicSync-R使ARI提升+0.99；LLM报告在GR/CA/SC三项忠实度指标上达1.00/1.00/0.975，证明证据链可追溯。

**真正贡献**  
构建了首个从聚类输出到自然语言审计的可追溯证据链；首次将LLM忠实度作为非可微奖励，通过REINFORCE反向优化聚类表征；所有推理严格受限于模型自身中间信号，不引入外部知识。

**与你研究方向的关系**  
与空间转录组（STAGATE/GraphST）、多组学融合（GROVER/SpatialGlue）、单细胞基础模型（scGPT）存在方法论连接，尤其在空间编码、模态路由、policy gradient reward设计上有明确继承与拓展。

**局限性**  
基础版OmicSync是后验解释，不优化聚类；OmicSync-R计算开销大（训练需220次LLM调用）；SC指标仅衡量报告是否提及邻域组成，不验证其生物学意义；实验仅覆盖4个FFPE数据集。

**是否值得精读**  
值得精读 —— 因其完整展示了“信号→证据→推理→反馈”闭环的设计逻辑、实证链条与边界条件，且所有模块均开源可复现（Card未提供代码链接，但方法描述完整）。

**原文 PDF**：https://arxiv.org/pdf/2608.22785v2