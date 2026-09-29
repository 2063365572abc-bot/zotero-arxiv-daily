## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong（Card未提供所属机构）

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（scGPT/scBERT/Geneformer）在细胞注释中常用，但高总体准确率掩盖了对罕见细胞（如MS中的oligodendrocyte C、phagocyte）的系统性失效。此前工作关注采样或疾病亚组性能下降，但尚未系统检验损失函数这一核心干预手段。

**核心假设或问题**  
罕见细胞分类失效是否由损失函数设计导致？不同长尾损失在跨架构、跨数据集下是否表现稳健？失效能否通过嵌入几何特征（如神经坍塌、最近邻熵）区分可修复与不可修复类型？

**方法逻辑**  
输入：固定 backbone（scGPT/scBERT/Geneformer）、数据集、超参数，仅替换损失函数；核心方法：在162次受控训练中，用Macro-F1与Rare-class Recall评估聚合性能，用每类∆F1关联样本数定位可修复类，并通过NC1、UMAP可视化、线性探针分析嵌入几何；输出：双轨失效判据（损失敏感型 vs. 严重纠缠型）及对应干预建议。

**主要结果**  
标准交叉熵在所有数据集上均导致Accuracy > Macro-F1 > Rare-recall的指标断层；class-balanced loss和LDAM在所测6种损失中平均排名最高；重加权增益由罕见类绝对样本数决定（n越小增益越大）；而n=3的严重纠缠类在嵌入空间被邻近类吸收，换任何损失均无效，但线性探针证实信号仍存在于冻结嵌入中。

**真正贡献**  
提出“双轨失效”框架，首次将神经坍塌理论（NC1）和嵌入几何分析用于单细胞长尾诊断；实证揭示绝对样本数比相对频率更能预测重加权效果；建立从宏观性能→类级响应→微观几何归因的完整证据链。

**与你研究方向的关系**  
其几何诊断方法（UMAP/NC1/最近邻）可直接迁移至空间转录组嵌入分析；损失比较框架可扩展至多组学融合模型的模态不平衡处理；属弱连接/方法论连接。

**局限性**  
仅测试scGPT/scBERT/Geneformer三种backbone，scFoundation等未覆盖；结论限于细胞类型分类任务，不推广至cell state representation或cross-modal alignment；NC1低值可能源于生物学同质性而非数据稀缺，Card未排除该替代解释。

**是否值得精读**  
值得精读——它提供了首个控制变量下、跨架构、跨数据集的长尾损失系统基准，并给出可复现的几何诊断流程与双轨决策指南。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1