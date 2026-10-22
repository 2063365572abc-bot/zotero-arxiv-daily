## Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions

**标题与发布时间**  
Rethinking Class Imbalance for Single-Cell Foundation Models: A Systematic Benchmark Across Architectures and Long-Tail Loss Functions（2026-09-20T03:24:53+00:00）

**作者和机构**  
Zeyu Dong, Jiahui Zhong

**发表状态**  
arXiv 预印本

**研究背景**  
单细胞基础模型（如scGPT、scBERT、Geneformer）在细胞类型注释中广泛使用，但高总体准确率常掩盖对罕见细胞（如MS中的寡突胶质细胞C、吞噬细胞）的系统性漏检。此前工作聚焦采样策略或预训练偏差，尚未系统评估长尾损失函数在不同骨干架构下的效果。

**核心假设或问题**  
作者追问：长尾损失是否万能解药？具体包括——（1）损失效果是否依赖骨干架构？（2）罕见类失败是否可分“可修复”与“不可修复”两类？（3）决定可修复性的关键是相对频率还是绝对样本量？（4）不可修复类的失败根源是表征坍缩还是分类器缺陷？

**方法逻辑**  
输入：3个骨干模型（scGPT/scBERT/Geneformer）、3个数据集（MS/Zheng68K/Pancreas）、6种损失函数；核心方法：固定所有非损失变量，做162次控制实验；输出：按类分析∆F1、NC1指标、UMAP可视化嵌入吸收现象，并用线性探针定位瓶颈在分类器而非表示层。

**主要结果**  
Macro-F1等聚合指标持续高于Recall_R，说明罕见类性能被严重低估；MS中n≤3的两类在所有损失下F1=0，呈现嵌入空间“吸收”现象；microglial cell等“损失敏感型”类在class-balanced loss下F1从0提升至0.86–0.92；class-balanced loss和LDAM综合排名最优（均值2.4/2.6），但无单一损失在所有数据集上最优。

**真正贡献**  
提出诊断性框架：用NC1和UMAP区分“可修复”与“不可修复”罕见类；发现绝对样本量而非相对频率决定重加权收益；证明损失无效仅限于极低样本类，其余类可通过损失选择显著改善。

**与你研究方向的关系**  
UMAP揭示的嵌入空间吸收现象，与空间转录组中spot邻域关系存在方法论共鸣；线性探针发现冻结嵌入中残留判别信号，为扰动预测方向提供可迁移范式；几何诊断思路可拓展至多组学联合嵌入中识别对齐失败的罕见亚群。

**局限性**  
仅测试3种骨干模型，未覆盖scFoundation、CellPLM；MS中两类标签被作者注明“来源图谱定义模糊”，其F1=0可能源于标注歧义而非纯数据稀缺；线性探针显示当前分类头未充分利用嵌入信号。

**是否值得精读**  
值得精读。Card明确指出该文提供了条件化决策树：先诊断失败类型，再决定补数据或换损失，且所有结论均有NC1、UMAP、∆F1等多尺度证据支撑。

**原文 PDF**：https://arxiv.org/pdf/2609.23325v1