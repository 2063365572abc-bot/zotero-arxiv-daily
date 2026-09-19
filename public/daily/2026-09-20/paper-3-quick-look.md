## Dynamic Generalized Gromov-Wasserstein Optimal Transport

**标题与发布时间**  
Dynamic Generalized Gromov-Wasserstein Optimal Transport（2026-09-17T10:17:33+00:00）

**作者和机构**  
Junda Ying, Zhiwei Zeng, Peijie Zhou, Lei Zhang；Card未提供所属机构。

**发表状态**  
arXiv 预印本（arXiv ID：2609.20008v1）

**研究背景**  
静态GW-OT等方法已用于空间转录组结构对齐，但缺乏可计算、免仿真的动态形式来重建连续轨迹。此前工作或聚焦单细胞轨迹（如OT-CFM），或仅扩展静态结构对齐（如IGW-OT），未统一结构约束与动力学演化。

**核心假设或问题**  
能否构建一种动态最优传输理论，既涵盖OT、GW-OT、IGW-OT为特例，又支持可训练、可扩展、可解释的求解？关键缺口是：如何让空间结构约束（如距离）直接驱动动力学过程，而非只作用于起点和终点匹配。

**方法逻辑**  
输入：初始/终末空间转录组分布（含基因表达与空间坐标）。  
核心方法：提出TP-DATE框架——先用动态二次型OT（QOT）求解最优耦合，再通过“行进对”路径动作A(z,z′)定义细胞对协同运动的最小作用量，并用流匹配学习联合速度场。该动作显式惩罚相对位移变化，使结构约束自然嵌入动力学。  
输出：保持空间结构的连续细胞轨迹插值。

**主要结果**  
在合成旋转数据及Mouse Brain、ARTISTA、Tumor真实数据上，TP-DATE显著优于OT-CFM等基线：Spatial MSE低至0.02269（OT-CFM为0.11015）；SC-eMSE更低；所有实验均为hold-one-out设置，仅用两个端点预测中间状态。

**真正贡献**  
提出首个免仿真、可训练的动态GW类最优传输框架；将结构建模从“端点耦合+独立插值”转向“成对协同运动+联合优化”；证明其理论统一性（涵盖OT/GW-OT/IGW-OT），并给出可解析的路径动作设计。

**与你研究方向的关系**  
适用于空间转录组轨迹推断；其“行进对”思想与单细胞foundation models的cell-cell attention有方法论共鸣；velocity分解（bₜ + fₜ）呼应多组学中“细胞内在+微环境外在”建模范式；C-Q分解与GNN message passing存在形式相似性。

**局限性**  
作者承认：静态QOT求解复杂度高（O(M²N²)），需靠KNN图稀疏化缓解；理论层面QOTS仅是BB-action的上界，非严格相等；方法学习的是Markovian速度场，可能弱化路径记忆特性。

**是否值得精读**  
值得精读；因它在多个真实空间转录组数据集上定量验证了结构保真优势，且方法设计（行进对+路径动作+流匹配）与结论间有完整证据链支撑。

**原文 PDF**：https://arxiv.org/pdf/2609.20008v1