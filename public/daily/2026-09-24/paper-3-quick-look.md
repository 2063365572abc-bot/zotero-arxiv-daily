## Dynamic Generalized Gromov-Wasserstein Optimal Transport

**标题与发布时间**  
Dynamic Generalized Gromov-Wasserstein Optimal Transport（2026-09-17T00:00:00+00:00）

**作者和机构**  
Junda Ying, Zhiwei Zeng, Peijie Zhou, Lei Zhang（Card未提供具体机构）

**发表状态**  
arXiv 预印本

**研究背景**  
该工作融合三条路径：最优传输从静态规划走向动态流（如Benamou–Brenier）；结构感知传输从GW-OT扩展到静态QOT统一框架；生成式求解从OT-CFM迁移到Schrödinger桥，但尚未覆盖QOT动态化。

**核心假设或问题**  
现有方法无法在连续时间/深度轴上重建空间转录组的生物学轨迹：静态GW-OT只做快照对齐，仿真类方法（如stVCR）计算低效。目标是构建一个数学严谨、无需仿真的动态QOT框架，能统一OT、GW-OT等特例，并支持结构敏感的连续插值。

**方法逻辑**  
输入是成对细胞的起止位置；核心方法用“旅行对”建模——把两个细胞的联合运动路径作为基本单元，将空间结构约束（如距离变化率）直接嵌入动力学Lagrangian，并通过flow matching学习其速度场；输出是单细胞层面的演化速度场v_t，用于轨迹估计。

**主要结果**  
在合成旋转、小鼠脑、肿瘤等空间转录组数据上，TP-DATE显著优于OT-CFM等基线：Spatial MSE低至0.02565（vs 0.10601），SC-eMSE更低，且避免显式仿真导致的OOM问题。优势来自动态融合Lagrangian与成对flow matching的组合。

**真正贡献**  
提出首个端到端可训练的动态QOT框架；定义并证明QOTS/QOTD/QOTBB三类等价形式；实现OT与GW-OT在动力学层面的光滑过渡；用成对路径替代单点位移，天然保结构。

**与你研究方向的关系**  
专为空间转录组设计，模态分离Lagrangian天然适配“空间坐标+表达谱”双模态；成对流π_t(x,y)可作细胞关系建模器，未来或为单细胞foundation model提供relation-aware embedding；稀疏KNN图与GNN邻域聚合逻辑相似。

**局限性**  
明确不支持质量不守恒过程（如细胞增殖/凋亡）；静态QOT与BB-form不等价，仅证得QOTS ≥ QOTBB；学习的v_t是Markovian投影，可能丢失路径高阶统计特性。

**是否值得精读**  
值得精读：它首次将结构感知传输从静态耦合推进到连续动力学建模，且所有结论均有hold-one-out实验与消融验证支撑。

**原文 PDF**：https://arxiv.org/pdf/2609.20008