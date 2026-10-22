## Dynamic Generalized Gromov-Wasserstein Optimal Transport

**标题与发布时间**  
Dynamic Generalized Gromov-Wasserstein Optimal Transport（2026-09-24T00:00:00+00:00）

**作者和机构**  
Junda Ying, Zhiwei Zeng, Peijie Zhou, Lei Zhang

**发表状态**  
arXiv 预印本

**研究背景**  
OT动态形式（如Benamou–Brenier）用于单细胞轨迹推断，但忽略空间结构；静态QOT（如GW-OT、FGW-OT）能对齐结构，却无法建模连续演化。二者长期割裂，近期工作尚未给出通用动态QOT理论及高效算法。

**核心假设或问题**  
现有方法只能对离散快照做静态对齐，无法重建细胞群体在时间或空间上的连续演化轨迹。关键难点是如何把结构感知的传输成本，从端点匹配扩展为连续概率流的动态生成机制。

**方法逻辑**  
输入：两组空间点云（如不同时刻的细胞位置）；核心方法：提出TP-DATE框架，将结构演化建模为“行进对”在二粒子空间中的交互路径，用显式惩罚相对位移变化率的方式保持局部几何，并通过条件流匹配学习单粒子速度场；输出：可微、可扩展的动态对齐轨迹。

**主要结果**  
在Synthetic Rotation上，TP-DATE的Spatial MSE（0.02565）显著低于OT-CFM（0.10601），Pair distortion最低（0.17174）；在ARTISTA和Tumor数据集上，Expression W2和SC-eMSE优于stVCR，但Spatial W2不如stVCR。

**真正贡献**  
提出首个兼具数学严谨性与计算可行性的动态QOT理论框架；设计TP-DATE求解器，实现结构保持的马尔可夫近似；证明QOTS是QOTBB的可计算上界，并提供闭式路径解。

**与你研究方向的关系**  
适用于空间转录组动态建模；其“行进对”思想可类比图神经网络的消息传递；Lagrangian支持多组学模态分离建模；条件流匹配目标与单细胞基础模型的掩码预测任务形式相通。

**局限性**  
不支持细胞增殖/凋亡等非平衡动力学；理论限定在同一度量空间（Y=X），难以直接用于跨模态对齐；学习的速度场是马尔可夫近似，可能忽略生物过程中的历史依赖或全局上下文。

**是否值得精读**  
值得精读：论文提供了动态QOT的完整理论定义、路径构造与可训练实现，且实验覆盖合成与真实空间转录组数据，验证了结构保持优势与适用边界。

**原文 PDF**：https://arxiv.org/pdf/2609.20008