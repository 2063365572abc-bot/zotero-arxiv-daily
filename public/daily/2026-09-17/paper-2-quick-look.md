## OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning

**标题与发布时间**  
OmicSync: Reliability-Aware Spatial Multi-Omics Clustering with Evidence-Constrained LLM Reasoning（2026-08-24T04:15:39+00:00）

**作者和机构**  
Rabeya Tus Sadia, Qiang Ye, Qiang Cheng；University of Kentucky 计算机科学与数学系

**发表状态**  
arXiv 预印本；无正式期刊、会议或出版平台信息

**研究背景**  
现有空间多组学方法如 GROVER、SpatialGlue、COSMOS 只输出聚类分区，不提供 spot 级可靠性指示、模态贡献归因或可解释性。LLM 在单细胞中用于注释，但未与空间聚类模型耦合生成证据约束解释。

**核心假设或问题**  
如何在无真实标注的临床 FFPE 数据上，为每个 spot 生成可审计、证据约束的可靠性解释？如何分别衡量软分配置信度、模态路由权重、路由不确定性这三类信号？能否用 LLM 推理质量作为非可微反馈信号，闭环优化聚类结果？

**方法逻辑**  
输入 RNA、ADT、H&E 图像块和空间坐标；先用图神经网络建模空间邻接关系，再经跨模态 Transformer 融合；通过带随机失活的专家混合结构生成潜表示，并从中提取三类可靠性信号；将这些信号连同标记基因和邻域信息组成提示，驱动大语言模型执行五类结构化解释；最后用解释质量得分作为奖励，通过强化学习更新聚类分配。

**主要结果**  
在四个 10x CytAssist FFPE 数据集（Tonsil、Glioblastoma 等）上，OmicSync 平均聚类排名最优（如 Tonsil 1.44），调整兰德指数全面领先；所有评估基于 GROVER 生成的伪参考标签，非人工标注。

**真正贡献**  
提出同时使用三类正交可靠性信号的框架；实现仅依赖模型自身输出证据的大语言模型解释；首次将大语言模型推理质量作为强化学习奖励来优化聚类潜空间。

**与你研究方向的关系**  
延伸空间转录组方法至多组学（RNA+ADT+H&E），兼容 STAGATE/GraphST 思路；采用 GROVER 的图神经网络建模；未使用基础模型预训练，聚焦多头监督融合。

**局限性**  
基础版本 Task C 是后验解释，虽闭环优化的 OmicSync-R 其奖励对聚类数敏感，优势集中在十类情形；路由不确定性仅来自随机失活的方差，未对路由网络本身做不确定性校准；大语言模型调用开销大，训练不稳定。

**是否值得精读**  
值得精读：首次系统整合可靠性量化、证据约束大语言模型解释与强化学习闭环，在临床 FFPE 多组学场景提供可审计聚类新范式。

**原文 PDF**：https://arxiv.org/pdf/2608.22785v2