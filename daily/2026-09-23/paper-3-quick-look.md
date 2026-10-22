## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-22T04:00:00+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong；Card未提供所属机构。

**发表状态**  
arXiv 预印本（v1）

**研究背景**  
单细胞基础模型（如scGPT）在细胞类型注释中广泛使用，但已有研究发现其对疾病相关罕见亚群（如MS中的oligodendrocyte C、phagocyte）性能显著下降，且随机过采样等采样策略无法完全解决。CV领域常用的长尾损失函数（如focal loss、LDAM）尚未在单细胞语境下系统验证其跨架构鲁棒性及对生物特异性失效的适配性。

**核心假设或问题**  
高准确率掩盖了对罕见病理亚群的系统性失效；该失效是否源于预训练偏差？能否仅靠损失函数统一解决？若不能，其边界与机制是什么？长尾问题需按失效机制分层建模，而非同质化处理。

**方法逻辑**  
输入：固定划分的单细胞数据、3种主干模型（scGPT/scBERT/Geneformer）、6种长尾损失函数；核心方法：控制变量训练162次，结合统计指标（Macro-F1、rare-class recall）与嵌入几何诊断（NC1、最近邻混淆）分阶归因；输出：识别“可优化”（loss-sensitive）与“不可优化”（severely entangled）两类失效，并预警严重纠缠类。

**主要结果**  
class-balanced loss和LDAM在9种（架构×数据集）组合中综合表现最稳健；weighted CE在MS数据集上Macro-F1最高（0.721），LDAM在Pancreas上最高（0.819）；六类损失均无法挽救严重纠缠类（如phagocyte），其根本瓶颈在于样本稀缺导致的嵌入几何坍缩。

**真正贡献**  
提出长尾失效的结构性二分法；将神经坍缩指标（NC1）首次用于单细胞冻结嵌入的事前失效预警；建立“先几何诊断、再损失优化”的新干预范式。

**与你研究方向的关系**  
嵌入几何诊断（如oligodendrocyte C的高NC1）可能泛化至扰动响应状态空间，提示在cell state representation和perturbation prediction中需显式约束嵌入几何。

**局限性**  
作者明确限制：仅测试3种主干模型（未覆盖scFoundation/CellPLM）；线性探针发现当前损失+线性头存在表达力天花板。Card未提供对技术噪声（如ambient RNA）是否干扰几何诊断的验证。

**是否值得精读**  
值得精读——它用162次控制实验+几何诊断，实证揭示单细胞长尾问题的本质分层，且开源代码与完整评估链便于复现和延伸。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1