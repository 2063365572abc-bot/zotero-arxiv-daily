## OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning

**标题与发布时间**  
OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning（2026-08-24T04:15:39+00:00）

**作者和机构**  
Rabeya Tus Sadia, Qiang Ye, Qiang Cheng；University of Kentucky 计算机科学与数学系

**发表状态**  
arXiv 预印本

**研究背景**  
现有空间多组学聚类方法（如 SpatialGlue、MISO）只输出硬聚类标签，缺乏可靠性量化、可解释性与模态归因。单细胞领域虽有LLM应用，但未与空间聚类模型耦合。OmicSync首次将不确定性估计与MoE路由结合用于空间多组学。

**核心假设或问题**  
如何在无真实标注的临床FFPE数据上，同时输出聚类结果与可靠性信号，并用这些信号约束LLM生成可审计的逐点自然语言解释？能否用非可微推理质量反馈优化聚类隐空间？

**方法逻辑**  
输入：每个spot的RNA、ADT、H&E图像块和空间坐标。  
核心方法：用KAN-GCN和CrossModalTransformer融合多模态；SpatialPositionEncoder注入位置信息；UncertaintyMoE通过MC Dropout估计模态路由权重与不确定性；ClusteringHead输出软聚类与置信度；LLM仅基于模型内生的五类证据生成解释；OmicSync-R用REINFORCE将推理质量作为reward反向优化聚类分配。  
输出：共享隐表示、软聚类、三类可靠性信号（置信度、不确定性、模态权重）、结构化自然语言解释。

**主要结果**  
在四个10x CytAssist FFPE数据集（Human Tonsil等）上，OmicSync平均排名最优（如Tonsil为1.44），综合九项指标（ARI/NMI/FMI等）。Stepwise解释策略在GR/CA/SC三项忠实性指标上达1.00，但属特定设计，不意味全面最优。

**真正贡献**  
提出可靠性作为模型原生输出；构建证据约束的LLM解释框架；实现无需梯度传播的推理-聚类协同优化；建立面向FFPE数据的跨数据集鲁棒评估协议。

**与你研究方向的关系**  
连接空间转录组（替代BayesSpace/GraphST）、多组学融合（扩展SpatialGlue/MISO）、单细胞基础模型（适配UNI/KAN-GCN）、以及LLM在生物医学中的可信推理。

**局限性**  
基础版OmicSync为后验解释，不优化聚类；OmicSync-R训练开销大；LLM仅见采样域的证据，存在确认偏误风险；所有结果均基于伪标签，无真实细胞类型标注验证。

**是否值得精读**  
值得精读：首次系统整合可靠性建模、证据约束LLM与空间多组学聚类，且在多个FFPE基准上验证有效。

**原文 PDF**：https://arxiv.org/pdf/2608.22785v2