## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong；Card未提供所属机构。

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（如 scGPT、scBERT、Geneformer）在 cell-type annotation 中报告高 aggregate accuracy，但该指标被常见类主导，罕见细胞亚群（如多发性硬化中的 oligodendrocyte C）持续被低估。既有长尾方法中，损失重加权法因即插即用、不改 backbone，成为本文聚焦路径。

**核心假设或问题**  
主流假设“长尾损失函数能系统性缓解罕见类失败”是否成立？该效果是否依赖特定 backbone 或数据集？当损失优化失效时，瓶颈是数据稀缺、表示坍缩，还是分类器设计？能否用嵌入几何特征提前预判某类是否“不可救”？

**方法逻辑**  
输入：统一预处理的单细胞数据（MS/ Zheng68K/ hu）、固定 backbone 微调协议；核心方法：控制变量遍历 6 种长尾损失 × 3 种 backbone × 3 个数据集 × 3 次随机种子，辅以 per-class ∆F1 分析、NC1 几何诊断、frozen embedding 上的线性探针；输出：各损失在 aggregate accuracy、Macro-F1、罕见类召回等指标上的稳定排序与失效边界。

**主要结果**  
class-balanced loss 平均排名最高（2.4），但并非每组最优；logit adjustment 明确以精度换召回（MS 精度 0.650，召回 0.632）；极少数样本（n=3）导致嵌入严重纠缠，此时所有测试损失均无法提升 F1；绝对样本数与性能增益呈强负相关（r = −0.77）。

**真正贡献**  
提出罕见类失败的双重机制：可补救的 loss-sensitive 类（重加权有效）与结构性失败的 severely entangled 类（损失无效，需数据或表示层干预）；将“是否值得调损失函数”转化为可量化、可预测的决策问题。

**与你研究方向的关系**  
其损失函数 benchmark 协议和诊断工具（NC1、∆F1、线性探针）可直接用于评估 scGPT/scBERT 对罕见 perturbation 状态（如早期凋亡）的判别能力；证明“severely entangled”源于嵌入几何而非表示缺失，支持对 cell state representation 做 post-hoc 优化而非弃用 backbone。

**局限性**  
仅测试 scGPT/scBERT/Geneformer，未覆盖 scFoundation 和 CellPLM；分类器头为线性，可能表达力不足；仅考察 cell-type class imbalance，未涉及技术批次、扰动类型等其他不平衡维度。

**是否值得精读**  
值得精读；它提供了首个跨 backbone、跨数据集、含嵌入几何诊断的单细胞长尾损失 benchmark，且结论明确区分了“可调”与“不可调”的失败场景。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1