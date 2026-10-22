## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong；Card未提供所属机构。

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（如scGPT/scBERT/Geneformer）在整体准确率上表现高，但罕见细胞类型（如早期过渡态、病理亚群）分类失败已被多次记录。此前工作聚焦采样策略或专用模型设计，尚未系统评估损失函数在跨架构下的独立作用。

**核心假设或问题**  
当模型在标准benchmark上报告高准确率（如97.5%）时，其对罕见细胞类型的失败是否具有系统性、可诊断且可干预的机制？失败根源是预训练偏差、数据结构缺陷，还是损失函数失配？是否存在几何信号能提前区分“换损失就能救”和“换啥都白搭”的两类罕见类？

**方法逻辑**  
输入：固定采样分布与批次构成的单细胞数据；核心方法：控制变量法——在3种主干、3个数据集、6种长尾损失间做162组正交实验，辅以UMAP可视化、NC1指标、最近邻熵和线性探针进行多维诊断；输出：识别损失敏感型与严重纠缠型罕见类，并建立基于绝对样本数的干预决策规则。

**主要结果**  
所有架构下均存在准确率 > Macro-F1 > 罕见类召回率的三重差距（如scBERT/MS：0.858 > 0.639 > 0.596）。class-balanced和LDAM损失在损失敏感型类上最稳健；但对严重纠缠类（Figure 3中全黑行）完全无效。F1提升由绝对训练样本数（而非相对频率）预测，且logit调整增益伴随精度下降。

**真正贡献**  
提出“几何可诊断的双模态失败”框架，将损失选择升级为“嵌入几何预筛 + 损失匹配”流程；验证NC1与最近邻熵可提前标记损失无效区；证明绝对样本数比不平衡比更能预测损失有效性。

**与你研究方向的关系**  
其几何诊断思路（UMAP、NC1）可迁移到空间转录组的邻域吸收分析；线性探针验证了表示-分类器解耦框架在单细胞领域的适用性；但未涉及图神经网络或空间图建模。

**局限性**  
仅测试scGPT/scBERT/Geneformer三种主干，未覆盖scFoundation/CellPLM；线性探针显示部分纠缠类仍有分类器表达力瓶颈；NC1在极小样本类上可能因分母收缩而误判。

**是否值得精读**  
值得精读：它提供了首个跨架构、控变量、带几何诊断的长尾损失基准，且结论附带三层明确限定，避免过度解读。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1