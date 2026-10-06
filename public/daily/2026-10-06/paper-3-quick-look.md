## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong（Card未提供所属机构）

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（如scGPT/scBERT/Geneformer）在细胞类型标注中总体准确率高，但罕见细胞类型（如疾病早期过渡态）性能常被聚合指标掩盖；现有缓解策略（采样、表示调整、损失函数）缺乏跨架构、跨数据集的系统性验证。

**核心假设或问题**  
模型在罕见类上的失败不是随机噪声，而是由两个正交因素驱动：一是训练样本绝对数量过少（如n=3），导致嵌入空间无法形成可区分簇；二是当前损失函数无法适配单细胞嵌入的几何特性（如类间边界模糊）。

**方法逻辑**  
输入：固定backbone（scGPT/scBERT/Geneformer）、固定数据集（MS/Zheng68K/Pancreas）、固定预处理；核心方法：在162组控制实验中横向比较6种长尾损失函数，结合Macro-F1、UMAP可视化、NC1几何度量、线性探针和跨架构混淆分析，诊断失败根源；输出：按“数据层瓶颈”与“优化层瓶颈”分类的可操作修复路径。

**主要结果**  
Class-balanced loss和LDAM在9个(backbone×dataset)组合中平均排名最高（2.4/2.6），但非处处最优；重加权收益与训练样本绝对数量强负相关（r=−0.77），仅适用于排除n=3后的“可恢复”类；n=3样本存在“邻域吸收”，此时调损失无效。

**真正贡献**  
将长尾问题从超参调优重构为三步决策流程：先用嵌入几何（NC1、混淆模式）诊断是否可修复；再用log(absolute count)预测ΔF1收益；最后选择并验证损失函数。

**与你研究方向的关系**  
其嵌入几何诊断法（NC1+最近邻）可用于评估空间转录组中病灶区稀有细胞是否被正常组织簇吸收；“绝对样本数决定可修复性”规律可迁移至多组学场景（如scATAC低覆盖度peak导致跨模态对齐失效）。

**局限性**  
仅测试scGPT/scBERT/Geneformer三种backbone；NC1在n=3时易受统计噪声干扰，可能误判几何质量；线性探针能恢复信号，说明当前损失未充分利用表征能力。

**是否值得精读**  
值得精读：它提供了首个统一框架，用几何诊断+控制实验揭示了长尾损失何时有效、为何无效、如何预判。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1